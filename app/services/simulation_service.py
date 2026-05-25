from dataclasses import replace

from app.core.config import settings
from app.data.seed import ACTIVE_PARAMETER_SET, PLANTING_SYSTEMS, RICE_VARIETIES
from app.domain.enums import EmissionStatus, RiskLevel
from app.domain.models import MarketPrices, ParameterSet, PlantingSystem, RiceVariety
from app.engines.differential_evolution import DifferentialEvolutionOptimizer
from app.engines.formula_engine import (
    build_timeline,
    compute_delta_v_rice_rp,
    compute_duck_gross_value_rp,
    compute_dung_total_per_duck,
    compute_final_yield_ton_per_ha,
    compute_npk_contribution,
    compute_risk_level,
    compute_safe_window_days,
    compute_v_eco1_rp,
    compute_v_eco2_rp,
    to_hectare,
)
from app.schemas.lookups import PlantingSystemResponse, RiceVarietyResponse
from app.schemas.simulation import (
    AreaSummary,
    CalculationStatus,
    ComparisonSummary,
    InputSummary,
    ProactiveResult,
    ReactiveResult,
    SimulationRequest,
    SimulationResponse,
    SoilNutrientSummary,
    TimelineSummary,
)


class SimulationInputError(ValueError):
    """Raised when the request references an unknown lookup or invalid domain."""


class SimulationService:
    def __init__(self) -> None:
        self._optimizer = DifferentialEvolutionOptimizer(seed=settings.de_random_seed)

    def list_rice_varieties(self) -> list[RiceVarietyResponse]:
        return [
            RiceVarietyResponse(
                id=item.code,
                name=item.name,
                hst_entry=item.hst_entry,
                hst_heading=item.hst_heading,
                plant_height_category=item.plant_height_category,
                notes=item.notes,
            )
            for item in RICE_VARIETIES
        ]

    def list_planting_systems(self) -> list[PlantingSystemResponse]:
        return [
            PlantingSystemResponse(
                id=item.code,
                name=item.name,
                k_max_per_hectare=item.k_max_per_hectare,
                f_yield=item.f_yield,
                notes=item.notes,
            )
            for item in PLANTING_SYSTEMS
        ]

    def evaluate(self, payload: SimulationRequest) -> SimulationResponse:
        variety = self._find_variety(payload.rice_variety)
        planting_system = self._find_planting_system(payload.planting_system)
        parameter_set = self._resolve_parameter_set(payload.parameter_set_id)
        prices = self._merge_market_prices(parameter_set.market_prices, payload)

        area_hectare = to_hectare(payload.land_area, payload.land_area_unit)
        area_are = area_hectare * 100.0
        safe_window_days = compute_safe_window_days(variety, parameter_set.biological_constants)
        actual_density = payload.duck_count / area_hectare

        reactive_metrics = self._evaluate_candidate(
            duck_count=payload.duck_count,
            density_per_hectare=actual_density,
            duration_days=safe_window_days,
            area_hectare=area_hectare,
            variety=variety,
            planting_system=planting_system,
            prices=prices,
            parameter_set=parameter_set,
            planting_date=payload.planting_date,
        )

        bounds = [
            (0.0, planting_system.k_max_per_hectare),
            (1.0, float(safe_window_days)),
        ]
        optimization = self._optimizer.optimize(
            bounds=bounds,
            params=parameter_set.optimization,
            objective=lambda density, duration: self._evaluate_candidate(
                duck_count=max(0, round(density * area_hectare)),
                density_per_hectare=density,
                duration_days=duration,
                area_hectare=area_hectare,
                variety=variety,
                planting_system=planting_system,
                prices=prices,
                parameter_set=parameter_set,
                planting_date=payload.planting_date,
            )["total_benefit_rp"],
        )

        optimized_duration = min(optimization.duration_days, safe_window_days)
        recommended_duck_total = max(0, round(optimization.density_per_hectare * area_hectare))
        proactive_metrics = self._evaluate_candidate(
            duck_count=recommended_duck_total,
            density_per_hectare=optimization.density_per_hectare,
            duration_days=optimized_duration,
            area_hectare=area_hectare,
            variety=variety,
            planting_system=planting_system,
            prices=prices,
            parameter_set=parameter_set,
            planting_date=payload.planting_date,
        )

        reactive_result = ReactiveResult(
            duck_density_per_are=round(actual_density / 100.0, 3),
            duck_density_per_hectare=round(actual_density, 3),
            duration_days=reactive_metrics["duration_days"],
            risk_level=reactive_metrics["risk_level"].value,
            penalty_rate=round(reactive_metrics["penalty_rate"], 4),
            predicted_rice_yield_ton_per_ha=round(reactive_metrics["final_yield_ton_per_ha"], 4),
            total_benefit_rp=round(reactive_metrics["total_benefit_rp"], 2),
            delta_rice_value_rp=round(reactive_metrics["delta_rice_value_rp"], 2),
            duck_net_value_rp=round(reactive_metrics["duck_net_value_rp"], 2),
            ecological_value_rp=round(reactive_metrics["ecological_value_rp"], 2),
            penalty_yield_rp=round(reactive_metrics["penalty_yield_rp"], 2),
            penalty_feed_rp=round(reactive_metrics["penalty_feed_rp"], 2),
            soil_nutrients=SoilNutrientSummary(
                n_kg_per_ha=round(reactive_metrics["n_kg_per_ha"], 4),
                p2o5_kg_per_ha=round(reactive_metrics["p_kg_per_ha"], 4),
                k2o_kg_per_ha=round(reactive_metrics["k_kg_per_ha"], 4),
            ),
            timeline=TimelineSummary(
                duck_release_date=reactive_metrics["release_date"],
                duck_pull_date=reactive_metrics["pull_date"],
                safe_window_days=safe_window_days,
            ),
            warnings=reactive_metrics["warnings"],
        )

        proactive_result = ProactiveResult(
            recommended_duck_total=recommended_duck_total,
            recommended_duck_density_per_are=round(
                proactive_metrics["density_per_hectare"] / 100.0,
                3,
            ),
            recommended_duck_density_per_hectare=round(
                proactive_metrics["density_per_hectare"],
                3,
            ),
            recommended_duration_days=optimized_duration,
            predicted_optimal_yield_ton_per_ha=round(proactive_metrics["final_yield_ton_per_ha"], 4),
            projected_total_benefit_rp=round(proactive_metrics["total_benefit_rp"], 2),
            delta_profit_rp=round(
                proactive_metrics["total_benefit_rp"] - reactive_metrics["total_benefit_rp"],
                2,
            ),
            timeline=TimelineSummary(
                duck_release_date=proactive_metrics["release_date"],
                duck_pull_date=proactive_metrics["pull_date"],
                safe_window_days=safe_window_days,
            ),
            warnings=proactive_metrics["warnings"],
        )

        risk_transition = (
            f"{reactive_metrics['risk_level'].value} -> {proactive_metrics['risk_level'].value}"
        )
        comparison = ComparisonSummary(
            display_mode="side_by_side",
            yield_gain_ton_per_ha=round(
                proactive_metrics["final_yield_ton_per_ha"] - reactive_metrics["final_yield_ton_per_ha"],
                4,
            ),
            profit_gain_rp=round(
                proactive_metrics["total_benefit_rp"] - reactive_metrics["total_benefit_rp"],
                2,
            ),
            risk_transition=risk_transition,
            summary=self._build_summary(reactive_metrics, proactive_metrics),
        )

        calculation_status = CalculationStatus(
            economy="estimated",
            emission=(
                EmissionStatus.LIMITED.value
                if payload.include_emission
                else EmissionStatus.NOT_CALCULATED.value
            ),
            calibration=parameter_set.calibration_status.value,
        )

        assumptions = [
            "The implementation normalizes t as duration in days, not absolute HST, to keep units consistent in the yield function.",
            "Penalty rate is capped at 50 percent to match the design note in the variable workbook.",
            "The first backend setup uses a local gross duck-value model to avoid currency mismatch and double counting from the literature net polynomial.",
            "Seed market prices are illustrative and must be replaced by BPS, market survey, or field-validated values before publication use.",
            "Emission outputs stay limited until seasonal flux conversion and local baseline variables are available.",
        ]
        if payload.market_overrides is None:
            assumptions.append(
                "No request-level market override was supplied, so the seed parameter set was used for the financial projection."
            )

        return SimulationResponse(
            input_summary=InputSummary(
                duck_count=payload.duck_count,
                area=AreaSummary(
                    value_are=round(area_are, 4),
                    value_hectare=round(area_hectare, 4),
                ),
                rice_variety=variety.code,
                planting_system=planting_system.code,
                planting_date=payload.planting_date,
                parameter_set_id=parameter_set.id,
            ),
            reactive_result=reactive_result,
            proactive_result=proactive_result,
            comparison=comparison,
            calculation_status=calculation_status,
            assumptions=assumptions,
        )

    def _resolve_parameter_set(self, parameter_set_id: str) -> ParameterSet:
        if parameter_set_id != ACTIVE_PARAMETER_SET.id:
            raise SimulationInputError(
                f"Unknown parameter_set_id '{parameter_set_id}'. Only 'active' is available in the seed setup."
            )
        return ACTIVE_PARAMETER_SET

    def _find_variety(self, code: str) -> RiceVariety:
        normalized = code.strip().lower()
        for item in RICE_VARIETIES:
            if item.code == normalized:
                return item
        raise SimulationInputError(f"Unknown rice_variety '{code}'.")

    def _find_planting_system(self, code: str) -> PlantingSystem:
        normalized = code.strip().lower()
        for item in PLANTING_SYSTEMS:
            if item.code == normalized:
                return item
        raise SimulationInputError(f"Unknown planting_system '{code}'.")

    def _merge_market_prices(self, prices: MarketPrices, payload: SimulationRequest) -> MarketPrices:
        overrides = payload.market_overrides
        if overrides is None:
            return prices
        return replace(
            prices,
            rice_duck_price_rp_per_kg=overrides.rice_duck_price_rp_per_kg or prices.rice_duck_price_rp_per_kg,
            conventional_rice_price_rp_per_kg=(
                overrides.conventional_rice_price_rp_per_kg
                or prices.conventional_rice_price_rp_per_kg
            ),
            baseline_yield_ton_per_ha=(
                overrides.baseline_yield_ton_per_ha or prices.baseline_yield_ton_per_ha
            ),
            nitrogen_price_rp_per_kg=overrides.nitrogen_price_rp_per_kg or prices.nitrogen_price_rp_per_kg,
            phosphate_price_rp_per_kg=(
                overrides.phosphate_price_rp_per_kg or prices.phosphate_price_rp_per_kg
            ),
            potassium_price_rp_per_kg=(
                overrides.potassium_price_rp_per_kg or prices.potassium_price_rp_per_kg
            ),
            duck_price_rp_per_kg=overrides.duck_price_rp_per_kg or prices.duck_price_rp_per_kg,
            feed_price_rp_per_kg=overrides.feed_price_rp_per_kg or prices.feed_price_rp_per_kg,
        )

    def _evaluate_candidate(
        self,
        duck_count: int,
        density_per_hectare: float,
        duration_days: float,
        area_hectare: float,
        variety: RiceVariety,
        planting_system: PlantingSystem,
        prices: MarketPrices,
        parameter_set: ParameterSet,
        planting_date,
    ) -> dict:
        base_yield_kg, penalty_rate, final_yield_ton = compute_final_yield_ton_per_ha(
            density_per_hectare=density_per_hectare,
            duration_days=duration_days,
            planting_system=planting_system,
        )
        delta_rice_value = compute_delta_v_rice_rp(
            prices=prices,
            final_yield_ton_per_ha=final_yield_ton,
            area_hectare=area_hectare,
        )
        duck_net_value, feed_penalty = compute_duck_gross_value_rp(
            duck_count=duck_count,
            density_per_hectare=density_per_hectare,
            duration_days=duration_days,
            area_hectare=area_hectare,
            prices=prices,
            planting_system=planting_system,
            biology=parameter_set.biological_constants,
        )
        eco_1 = compute_v_eco1_rp(
            prices=prices,
            density_per_hectare=density_per_hectare,
            duration_days=duration_days,
            area_hectare=area_hectare,
            biology=parameter_set.biological_constants,
        )
        eco_2 = compute_v_eco2_rp(
            density_per_hectare=density_per_hectare,
            area_hectare=area_hectare,
        )
        ecological_value = eco_1 + eco_2
        penalty_yield = base_yield_kg * penalty_rate * area_hectare * prices.rice_duck_price_rp_per_kg
        risk_level = compute_risk_level(
            density_per_hectare=density_per_hectare,
            k_max_per_hectare=planting_system.k_max_per_hectare,
        )
        n_kg, p_kg, k_kg = compute_npk_contribution(
            density_per_hectare=density_per_hectare,
            duration_days=duration_days,
            biology=parameter_set.biological_constants,
        )
        release_date, pull_date = build_timeline(
            planting_date=planting_date,
            hst_entry=variety.hst_entry,
            duration_days=max(1, round(duration_days)),
        )
        total_benefit = delta_rice_value + duck_net_value + ecological_value

        warnings: list[str] = []
        if risk_level == RiskLevel.WASPADA:
            warnings.append("Duck density is above the carrying threshold and has entered the warning zone.")
        if risk_level == RiskLevel.BAHAYA:
            warnings.append("Duck density is in the danger zone and may damage rice stands.")
        if duration_days >= parameter_set.biological_constants.t_max_eff_days:
            warnings.append("Duck duration is at the efficiency ceiling and should not be extended without field validation.")
        if duck_count == 0:
            warnings.append("Duck count is zero, so the scenario behaves like a rice-only baseline.")

        return {
            "duck_count": duck_count,
            "density_per_hectare": density_per_hectare,
            "duration_days": max(1, round(duration_days)),
            "base_yield_kg_per_ha": base_yield_kg,
            "penalty_rate": penalty_rate,
            "final_yield_ton_per_ha": final_yield_ton,
            "delta_rice_value_rp": delta_rice_value,
            "duck_net_value_rp": duck_net_value,
            "ecological_value_rp": ecological_value,
            "penalty_yield_rp": penalty_yield,
            "penalty_feed_rp": feed_penalty,
            "total_benefit_rp": total_benefit,
            "risk_level": risk_level,
            "dung_total_per_duck_kg": compute_dung_total_per_duck(
                duration_days,
                parameter_set.biological_constants,
            ),
            "n_kg_per_ha": n_kg,
            "p_kg_per_ha": p_kg,
            "k_kg_per_ha": k_kg,
            "release_date": release_date,
            "pull_date": pull_date,
            "warnings": warnings,
        }

    def _build_summary(self, reactive_metrics: dict, proactive_metrics: dict) -> str:
        if proactive_metrics["total_benefit_rp"] > reactive_metrics["total_benefit_rp"]:
            return "The proactive recommendation improves projected benefit while staying inside the modeled safe window."
        return "The reactive scenario is already competitive under the current seed assumptions."


simulation_service = SimulationService()
