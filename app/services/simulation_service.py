from app.core.config import settings
from app.core.exceptions import InvalidReferenceError, ResourceNotFoundError
from app.domain.enums import EmissionStatus, RiskLevel
from app.domain.models import MarketPrices, ParameterSet, PlantingSystem, RiceVariety
from app.engines.differential_evolution import DifferentialEvolutionOptimizer
from app.engines.formula_engine import (
    build_timeline,
    compute_delta_v_rice_rp,
    compute_duck_gross_value_rp,
    compute_dung_total_per_duck,
    compute_final_yield_kg_per_are,
    compute_npk_contribution,
    compute_safe_window_days,
    compute_v_eco1_rp,
    compute_v_eco2_rp,
)
from app.repositories.lookup_repository import lookup_repository
from app.repositories.parameter_repository import parameter_repository
from app.repositories.simulation_repository import simulation_repository
from app.schemas.lookups import PlantingSystemResponse, RiceVarietyResponse
from app.schemas.simulation import (
    AgronomicContext,
    AreaSummary,
    CalculationStatus,
    ComparisonSummary,
    InputSummary,
    OptimizationBounds,
    OptimizationMeta,
    RecommendationSummary,
    ProactiveResult,
    ReactiveResult,
    RiskSummary,
    ScenarioSummaryCard,
    SimulationDashboardSummaryResponse,
    SimulationListItem,
    SimulationPreviewRequest,
    SimulationPreviewResponse,
    SimulationRequest,
    SimulationResponse,
    SimulationSummaryHeader,
    SoilNutrientSummary,
    TimelineSummary,
    PreviewSummary,
)

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
            for item in lookup_repository.list_rice_varieties()
        ]

    def list_planting_systems(self) -> list[PlantingSystemResponse]:
        return [
            PlantingSystemResponse(
                id=item.code,
                name=item.name,
                k_max_per_are=item.k_max_per_are,
                f_yield=item.f_yield,
                notes=item.notes,
            )
            for item in lookup_repository.list_planting_systems()
        ]

    def preview_context(self, payload: SimulationPreviewRequest) -> SimulationPreviewResponse:
        variety = self._find_variety(payload.rice_variety)
        planting_system = self._find_planting_system(payload.planting_system)
        parameter_set = self._resolve_parameter_set(payload.parameter_set_id)

        area_are = payload.land_area_are
        safe_window_days = compute_safe_window_days(variety, parameter_set.biological_constants)
        actual_density = payload.duck_count / area_are
        preview_metrics = self._evaluate_candidate(
            duck_count=payload.duck_count,
            density_per_are=actual_density,
            duration_days=safe_window_days,
            area_are=area_are,
            variety=variety,
            planting_system=planting_system,
            prices=parameter_set.market_prices,
            parameter_set=parameter_set,
            planting_date=payload.planting_date,
        )
        agronomic_context = self._build_agronomic_context(
            variety=variety,
            planting_system=planting_system,
            safe_window_days=safe_window_days,
            baseline_yield_kg_per_are=parameter_set.market_prices.baseline_yield_kg_per_are,
        )
        return SimulationPreviewResponse(
            input_summary=InputSummary(
                duck_count=payload.duck_count,
                area=AreaSummary(value_are=round(area_are, 4)),
                rice_variety=variety.code,
                planting_system=planting_system.code,
                planting_date=payload.planting_date,
                parameter_set_id=parameter_set.id,
            ),
            agronomic_context=agronomic_context,
            preview=PreviewSummary(
                duck_count=payload.duck_count,
                land_area_are=round(area_are, 4),
                duck_density_per_are=round(actual_density, 3),
                duration_days=safe_window_days,
                max_duck_capacity=max(0, round(planting_system.k_max_per_are * area_are)),
                recommended_duck_upper_bound=max(
                    0,
                    round(planting_system.k_max_per_are * area_are),
                ),
                estimated_rice_yield_kg_per_are=round(preview_metrics["final_yield_kg_per_are"], 3),
                estimated_rice_yield_total_kg=round(preview_metrics["total_rice_yield_kg"], 3),
                timeline=TimelineSummary(
                    duck_release_date=preview_metrics["release_date"],
                    duck_pull_date=preview_metrics["pull_date"],
                    safe_window_days=safe_window_days,
                ),
                risk_summary=self._build_risk_summary(
                    density_per_are=actual_density,
                    k_max_per_are=planting_system.k_max_per_are,
                    risk_level=preview_metrics["risk_level"],
                ),
                warnings=preview_metrics["warnings"],
            ),
            calculation_status=CalculationStatus(
                economy="preview",
                emission=EmissionStatus.NOT_CALCULATED.value,
                calibration=parameter_set.calibration_status.value,
            ),
            assumptions=[
                "Preview context does not run Differential Evolution; it only derives the current agronomic baseline from the input scenario.",
                "The preview yield estimate uses the same static parameter set as the full simulation unless a later evaluate call overrides market prices.",
            ],
        )

    def evaluate(self, payload: SimulationRequest) -> SimulationResponse:
        variety = self._find_variety(payload.rice_variety)
        planting_system = self._find_planting_system(payload.planting_system)
        parameter_set = self._resolve_parameter_set(payload.parameter_set_id)
        prices = self._merge_market_prices(parameter_set.market_prices, payload)

        area_are = payload.land_area_are
        safe_window_days = compute_safe_window_days(variety, parameter_set.biological_constants)
        actual_density = payload.duck_count / area_are

        reactive_metrics = self._evaluate_candidate(
            duck_count=payload.duck_count,
            density_per_are=actual_density,
            duration_days=safe_window_days,
            area_are=area_are,
            variety=variety,
            planting_system=planting_system,
            prices=prices,
            parameter_set=parameter_set,
            planting_date=payload.planting_date,
        )

        bounds = [
            (0.0, planting_system.k_max_per_are),
            (1.0, float(safe_window_days)),
        ]
        optimization = self._optimizer.optimize(
            bounds=bounds,
            params=parameter_set.optimization,
            objective=lambda density, duration: self._evaluate_candidate(
                duck_count=max(0, round(density * area_are)),
                density_per_are=density,
                duration_days=duration,
                area_are=area_are,
                variety=variety,
                planting_system=planting_system,
                prices=prices,
                parameter_set=parameter_set,
                planting_date=payload.planting_date,
            )["total_benefit_rp"],
        )

        optimized_duration = min(optimization.duration_days, safe_window_days)
        recommended_duck_total = max(0, round(optimization.density_per_are * area_are))
        proactive_metrics = self._evaluate_candidate(
            duck_count=recommended_duck_total,
            density_per_are=optimization.density_per_are,
            duration_days=optimized_duration,
            area_are=area_are,
            variety=variety,
            planting_system=planting_system,
            prices=prices,
            parameter_set=parameter_set,
            planting_date=payload.planting_date,
        )

        risk_transition = (
            f"{reactive_metrics['risk_level'].value} -> {proactive_metrics['risk_level'].value}"
        )
        comparison = ComparisonSummary(
            display_mode="side_by_side",
            yield_gain_kg_per_are=round(
                proactive_metrics["final_yield_kg_per_are"] - reactive_metrics["final_yield_kg_per_are"],
                3,
            ),
            yield_gain_total_kg=round(
                proactive_metrics["total_rice_yield_kg"] - reactive_metrics["total_rice_yield_kg"],
                3,
            ),
            profit_gain_rp=round(
                proactive_metrics["total_benefit_rp"] - reactive_metrics["total_benefit_rp"],
                2,
            ),
            risk_transition=risk_transition,
            summary=self._build_summary(reactive_metrics, proactive_metrics),
        )
        agronomic_context = self._build_agronomic_context(
            variety=variety,
            planting_system=planting_system,
            safe_window_days=safe_window_days,
            baseline_yield_kg_per_are=prices.baseline_yield_kg_per_are,
        )
        optimization_meta = OptimizationMeta(
            algorithm="Differential Evolution",
            objective_name="total_benefit_rp",
            population_size=parameter_set.optimization.population_size,
            mutation_factor=parameter_set.optimization.mutation_factor,
            crossover_rate=parameter_set.optimization.crossover_rate,
            max_generations=parameter_set.optimization.max_generations,
            executed_generations=optimization.generations,
            converged=optimization.converged,
            best_objective_value_rp=round(optimization.objective_value, 2),
            bounds=OptimizationBounds(
                density_min_per_are=0.0,
                density_max_per_are=round(planting_system.k_max_per_are, 3),
                duration_min_days=1,
                duration_max_days=safe_window_days,
            ),
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

        staged_record = simulation_repository.create(
            request_payload=payload.model_dump(mode="json"),
            response_payload={},
        )

        response = SimulationResponse(
            simulation_id=staged_record.id,
            created_at=staged_record.created_at,
            input_summary=InputSummary(
                duck_count=payload.duck_count,
                area=AreaSummary(
                    value_are=round(area_are, 4),
                ),
                rice_variety=variety.code,
                planting_system=planting_system.code,
                planting_date=payload.planting_date,
                parameter_set_id=parameter_set.id,
            ),
            agronomic_context=agronomic_context,
            reactive_result=self._to_reactive_result(reactive_metrics, safe_window_days),
            proactive_result=self._to_proactive_result(
                proactive_metrics=proactive_metrics,
                safe_window_days=safe_window_days,
                reactive_total_benefit_rp=reactive_metrics["total_benefit_rp"],
                recommended_duck_total=recommended_duck_total,
                recommended_duration_days=optimized_duration,
            ),
            comparison=comparison,
            optimization_meta=optimization_meta,
            calculation_status=calculation_status,
            assumptions=assumptions,
        )
        simulation_repository.update_response_payload(
            simulation_id=staged_record.id,
            response_payload=response.model_dump(mode="json"),
        )
        return response

    def list_simulations(self) -> list[SimulationListItem]:
        items: list[SimulationListItem] = []
        for record in simulation_repository.list_all():
            if not record.response_payload:
                continue
            response = SimulationResponse.model_validate(record.response_payload)
            items.append(
                SimulationListItem(
                    simulation_id=response.simulation_id,
                    created_at=response.created_at,
                    rice_variety=response.input_summary.rice_variety,
                    planting_system=response.input_summary.planting_system,
                    planting_date=response.input_summary.planting_date,
                    duck_count=response.input_summary.duck_count,
                    area_are=response.input_summary.area.value_are,
                    reactive_risk_level=response.reactive_result.risk_level,
                    reactive_total_benefit_rp=response.reactive_result.total_benefit_rp,
                    proactive_total_benefit_rp=response.proactive_result.projected_total_benefit_rp,
                    recommended_duck_total=response.proactive_result.recommended_duck_total,
                    calibration_status=response.calculation_status.calibration,
                )
            )
        return items

    def get_simulation_detail(self, simulation_id: str) -> SimulationResponse:
        record = simulation_repository.get_by_id(simulation_id)
        if record is None or not record.response_payload:
            raise ResourceNotFoundError(
                message=f"Simulation '{simulation_id}' was not found.",
                field="simulation_id",
            )
        return SimulationResponse.model_validate(record.response_payload)

    def get_simulation_summary(self, simulation_id: str) -> SimulationDashboardSummaryResponse:
        response = self.get_simulation_detail(simulation_id)
        return SimulationDashboardSummaryResponse(
            header=SimulationSummaryHeader(
                simulation_id=response.simulation_id,
                created_at=response.created_at,
                rice_variety=response.input_summary.rice_variety,
                planting_system=response.input_summary.planting_system,
                planting_date=response.input_summary.planting_date,
                duck_count=response.input_summary.duck_count,
                area_are=response.input_summary.area.value_are,
            ),
            reactive_card=self._to_summary_card(response, scenario="reactive"),
            proactive_card=self._to_summary_card(response, scenario="proactive"),
            recommendation=RecommendationSummary(
                profit_gain_rp=response.comparison.profit_gain_rp,
                yield_gain_kg_per_are=response.comparison.yield_gain_kg_per_are,
                yield_gain_total_kg=response.comparison.yield_gain_total_kg,
                risk_transition=response.comparison.risk_transition,
                recommended_action=response.comparison.summary,
            ),
            calculation_status=response.calculation_status,
        )

    def _resolve_parameter_set(self, parameter_set_id: str) -> ParameterSet:
        parameter_set = parameter_repository.get_by_id(parameter_set_id)
        if parameter_set is None:
            raise InvalidReferenceError(
                message=f"Unknown parameter_set_id '{parameter_set_id}'. Only seeded parameter sets are available.",
                field="parameter_set_id",
            )
        return parameter_set

    def _find_variety(self, code: str) -> RiceVariety:
        variety = lookup_repository.get_rice_variety(code)
        if variety is None:
            raise InvalidReferenceError(
                message=f"Unknown rice_variety '{code}'.",
                field="rice_variety",
            )
        return variety

    def _find_planting_system(self, code: str) -> PlantingSystem:
        planting_system = lookup_repository.get_planting_system(code)
        if planting_system is None:
            raise InvalidReferenceError(
                message=f"Unknown planting_system '{code}'.",
                field="planting_system",
            )
        return planting_system

    def _merge_market_prices(self, prices: MarketPrices, payload: SimulationRequest) -> MarketPrices:
        overrides = payload.market_overrides
        if overrides is None:
            return prices
        return MarketPrices(
            rice_duck_price_rp_per_kg=(
                overrides.rice_duck_price_rp_per_kg or prices.rice_duck_price_rp_per_kg
            ),
            conventional_rice_price_rp_per_kg=(
                overrides.conventional_rice_price_rp_per_kg
                or prices.conventional_rice_price_rp_per_kg
            ),
            baseline_yield_kg_per_are=(
                overrides.baseline_yield_kg_per_are or prices.baseline_yield_kg_per_are
            ),
            nitrogen_price_rp_per_kg=(
                overrides.nitrogen_price_rp_per_kg or prices.nitrogen_price_rp_per_kg
            ),
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
        density_per_are: float,
        duration_days: float,
        area_are: float,
        variety: RiceVariety,
        planting_system: PlantingSystem,
        prices: MarketPrices,
        parameter_set: ParameterSet,
        planting_date,
    ) -> dict:
        base_yield_kg_per_are, penalty_rate, final_yield_kg_per_are = compute_final_yield_kg_per_are(
            density_per_are=density_per_are,
            duration_days=duration_days,
            planting_system=planting_system,
        )
        total_rice_yield_kg = final_yield_kg_per_are * area_are
        delta_rice_value = compute_delta_v_rice_rp(
            prices=prices,
            final_yield_kg_per_are=final_yield_kg_per_are,
            area_are=area_are,
        )
        duck_net_value, feed_penalty = compute_duck_gross_value_rp(
            duck_count=duck_count,
            density_per_are=density_per_are,
            duration_days=duration_days,
            area_are=area_are,
            prices=prices,
            planting_system=planting_system,
            biology=parameter_set.biological_constants,
        )
        eco_1 = compute_v_eco1_rp(
            prices=prices,
            density_per_are=density_per_are,
            duration_days=duration_days,
            area_are=area_are,
            biology=parameter_set.biological_constants,
        )
        eco_2 = compute_v_eco2_rp(
            density_per_are=density_per_are,
            area_are=area_are,
        )
        ecological_value = eco_1 + eco_2
        penalty_yield = (
            base_yield_kg_per_are * penalty_rate * area_are * prices.rice_duck_price_rp_per_kg
        )
        risk_level = compute_risk_level(
            density_per_are=density_per_are,
            k_max_per_are=planting_system.k_max_per_are,
        )
        n_per_are, p_per_are, k_per_are = compute_npk_contribution(
            density_per_are=density_per_are,
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
            warnings.append(
                "Duck duration is at the efficiency ceiling and should not be extended without field validation."
            )
        if duck_count == 0:
            warnings.append("Duck count is zero, so the scenario behaves like a rice-only baseline.")

        return {
            "duck_count": duck_count,
            "density_per_are": density_per_are,
            "duration_days": max(1, round(duration_days)),
            "base_yield_kg_per_are": base_yield_kg_per_are,
            "penalty_rate": penalty_rate,
            "final_yield_kg_per_are": final_yield_kg_per_are,
            "total_rice_yield_kg": total_rice_yield_kg,
            "delta_rice_value_rp": delta_rice_value,
            "duck_net_value_rp": duck_net_value,
            "ecological_value_rp": ecological_value,
            "penalty_yield_rp": penalty_yield,
            "penalty_feed_rp": feed_penalty,
            "total_benefit_rp": total_benefit,
            "risk_level": risk_level,
            "k_max_per_are": planting_system.k_max_per_are,
            "dung_total_per_duck_kg": compute_dung_total_per_duck(
                duration_days,
                parameter_set.biological_constants,
            ),
            "n_kg_per_are": n_per_are,
            "p_kg_per_are": p_per_are,
            "k_kg_per_are": k_per_are,
            "n_total_kg": n_per_are * area_are,
            "p_total_kg": p_per_are * area_are,
            "k_total_kg": k_per_are * area_are,
            "release_date": release_date,
            "pull_date": pull_date,
            "warnings": warnings,
        }

    def _to_reactive_result(self, metrics: dict, safe_window_days: int) -> ReactiveResult:
        return ReactiveResult(
            duck_density_per_are=round(metrics["density_per_are"], 3),
            duration_days=metrics["duration_days"],
            risk_level=metrics["risk_level"].value,
            risk_summary=self._build_risk_summary(
                density_per_are=metrics["density_per_are"],
                k_max_per_are=metrics["k_max_per_are"],
                risk_level=metrics["risk_level"],
            ),
            penalty_rate=round(metrics["penalty_rate"], 4),
            predicted_rice_yield_kg_per_are=round(metrics["final_yield_kg_per_are"], 3),
            predicted_rice_yield_total_kg=round(metrics["total_rice_yield_kg"], 3),
            total_benefit_rp=round(metrics["total_benefit_rp"], 2),
            delta_rice_value_rp=round(metrics["delta_rice_value_rp"], 2),
            duck_net_value_rp=round(metrics["duck_net_value_rp"], 2),
            ecological_value_rp=round(metrics["ecological_value_rp"], 2),
            penalty_yield_rp=round(metrics["penalty_yield_rp"], 2),
            penalty_feed_rp=round(metrics["penalty_feed_rp"], 2),
            soil_nutrients=SoilNutrientSummary(
                n_kg_per_are=round(metrics["n_kg_per_are"], 4),
                p2o5_kg_per_are=round(metrics["p_kg_per_are"], 4),
                k2o_kg_per_are=round(metrics["k_kg_per_are"], 4),
                n_total_kg=round(metrics["n_total_kg"], 4),
                p2o5_total_kg=round(metrics["p_total_kg"], 4),
                k2o_total_kg=round(metrics["k_total_kg"], 4),
            ),
            timeline=TimelineSummary(
                duck_release_date=metrics["release_date"],
                duck_pull_date=metrics["pull_date"],
                safe_window_days=safe_window_days,
            ),
            warnings=metrics["warnings"],
        )

    def _to_proactive_result(
        self,
        proactive_metrics: dict,
        safe_window_days: int,
        reactive_total_benefit_rp: float,
        recommended_duck_total: int,
        recommended_duration_days: int,
    ) -> ProactiveResult:
        return ProactiveResult(
            recommended_duck_total=recommended_duck_total,
            recommended_duck_density_per_are=round(
                proactive_metrics["density_per_are"],
                3,
            ),
            recommended_duration_days=recommended_duration_days,
            risk_summary=self._build_risk_summary(
                density_per_are=proactive_metrics["density_per_are"],
                k_max_per_are=proactive_metrics["k_max_per_are"],
                risk_level=proactive_metrics["risk_level"],
            ),
            predicted_optimal_yield_kg_per_are=round(
                proactive_metrics["final_yield_kg_per_are"],
                3,
            ),
            predicted_optimal_yield_total_kg=round(proactive_metrics["total_rice_yield_kg"], 3),
            projected_total_benefit_rp=round(proactive_metrics["total_benefit_rp"], 2),
            delta_profit_rp=round(
                proactive_metrics["total_benefit_rp"] - reactive_total_benefit_rp,
                2,
            ),
            timeline=TimelineSummary(
                duck_release_date=proactive_metrics["release_date"],
                duck_pull_date=proactive_metrics["pull_date"],
                safe_window_days=safe_window_days,
            ),
            warnings=proactive_metrics["warnings"],
        )

    def _build_summary(self, reactive_metrics: dict, proactive_metrics: dict) -> str:
        if proactive_metrics["total_benefit_rp"] > reactive_metrics["total_benefit_rp"]:
            return "The proactive recommendation improves projected benefit while staying inside the modeled safe window."
        return "The reactive scenario is already competitive under the current seed assumptions."

    def _to_summary_card(
        self,
        response: SimulationResponse,
        scenario: str,
    ) -> ScenarioSummaryCard:
        if scenario == "reactive":
            return ScenarioSummaryCard(
                label="reactive",
                duck_total=response.input_summary.duck_count,
                duck_density_per_are=response.reactive_result.duck_density_per_are,
                duration_days=response.reactive_result.duration_days,
                predicted_rice_yield_kg_per_are=response.reactive_result.predicted_rice_yield_kg_per_are,
                predicted_rice_yield_total_kg=response.reactive_result.predicted_rice_yield_total_kg,
                total_benefit_rp=response.reactive_result.total_benefit_rp,
                risk_level=response.reactive_result.risk_level,
                warning_count=len(response.reactive_result.warnings),
                duck_release_date=response.reactive_result.timeline.duck_release_date,
                duck_pull_date=response.reactive_result.timeline.duck_pull_date,
            )
        return ScenarioSummaryCard(
            label="proactive",
            duck_total=response.proactive_result.recommended_duck_total,
            duck_density_per_are=response.proactive_result.recommended_duck_density_per_are,
            duration_days=response.proactive_result.recommended_duration_days,
            predicted_rice_yield_kg_per_are=response.proactive_result.predicted_optimal_yield_kg_per_are,
            predicted_rice_yield_total_kg=response.proactive_result.predicted_optimal_yield_total_kg,
            total_benefit_rp=response.proactive_result.projected_total_benefit_rp,
            risk_level=response.proactive_result.risk_summary.level,
            warning_count=len(response.proactive_result.warnings),
            duck_release_date=response.proactive_result.timeline.duck_release_date,
            duck_pull_date=response.proactive_result.timeline.duck_pull_date,
        )

    def _build_risk_summary(
        self,
        density_per_are: float,
        k_max_per_are: float,
        risk_level: RiskLevel,
    ) -> RiskSummary:
        exceeded_density = max(0.0, density_per_are - k_max_per_are)
        exceeded_ratio_pct = 0.0
        if k_max_per_are > 0:
            exceeded_ratio_pct = (exceeded_density / k_max_per_are) * 100.0
        return RiskSummary(
            level=risk_level.value,
            current_density_per_are=round(density_per_are, 3),
            k_max_per_are=round(k_max_per_are, 3),
            warning_limit_per_are=round(k_max_per_are * 1.3, 3),
            exceeded_density_per_are=round(exceeded_density, 3),
            exceeded_ratio_pct=round(exceeded_ratio_pct, 3),
        )

    def _build_agronomic_context(
        self,
        variety: RiceVariety,
        planting_system: PlantingSystem,
        safe_window_days: int,
        baseline_yield_kg_per_are: float,
    ) -> AgronomicContext:
        return AgronomicContext(
            rice_variety_code=variety.code,
            rice_variety_name=variety.name,
            planting_system_code=planting_system.code,
            planting_system_name=planting_system.name,
            hst_entry=variety.hst_entry,
            hst_heading=variety.hst_heading,
            safe_window_days=safe_window_days,
            k_max_per_are=round(planting_system.k_max_per_are, 3),
            warning_limit_per_are=round(planting_system.k_max_per_are * 1.3, 3),
            f_yield=planting_system.f_yield,
            baseline_yield_kg_per_are=baseline_yield_kg_per_are,
        )


simulation_service = SimulationService()
