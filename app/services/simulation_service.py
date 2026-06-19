import math

from app.core.exceptions import InvalidReferenceError, ResourceNotFoundError
from app.domain.models import DSSConstants, PlantingSystem, RiceVariety
from app.engines.formula_engine import (
    compute_actual_duration_days,
    compute_density,
    compute_dung_total,
    compute_effective_duration,
    compute_final_yield_kg_per_ha,
    compute_pull_date_from_duration,
    compute_pull_date_from_hst,
    compute_release_date,
    compute_risk_status,
    compute_surviving_ducks,
    convert_are_to_ha,
    convert_yield_units,
    risk_rank,
)
from app.engines.impact_engine import (
    compute_ecology,
    compute_economics,
    compute_environment,
    compute_soil_nutrients,
)
from app.repositories.lookup_repository import lookup_repository
from app.repositories.history_repository import history_repository
from app.schemas.dss import (
    ActualScenario,
    ComparisonSummary,
    DeleteHistoryResponse,
    DSSInput,
    DSSOptionsResponse,
    DSSSimulationRequest,
    DSSSimulationResponse,
    DataReadinessSummary,
    EcologySummary,
    EconomicsSummary,
    EnvironmentSummary,
    HistoryListItem,
    HistoryListResponse,
    HistorySummary,
    InfrastructureOutput,
    PlantingSystemOption,
    PredictedYield,
    RecommendedScenario,
    RiceVarietyOption,
    RiskSummary,
    ScenarioEcology,
    ScenarioEconomics,
    ScenarioEnvironment,
    SoilNutrients,
    ValidationSummary,
)


class DSSService:
    def get_options(self) -> DSSOptionsResponse:
        return DSSOptionsResponse(
            rice_varieties=[
                RiceVarietyOption(
                    code=item.code,
                    label=item.label,
                    hst_masuk=item.hst_masuk,
                    hst_heading=item.hst_heading,
                    harvest_age_days=item.harvest_age_days,
                    risk_note=item.risk_note,
                    hst_masuk_range={
                        "min": item.hst_masuk_min,
                        "max": item.hst_masuk_max,
                    },
                    hst_heading_range={
                        "min": item.hst_heading_min,
                        "max": item.hst_heading_max,
                    },
                    status=item.status,
                )
                for item in lookup_repository.list_rice_varieties()
            ],
            planting_systems=[
                PlantingSystemOption(
                    code=item.code,
                    label=item.label,
                    k_max_are=item.k_max_are,
                    f_yield=item.f_yield,
                    note=item.note,
                    k_max_range_are={
                        "min": item.k_max_min_are,
                        "max": item.k_max_max_are,
                    },
                    limited_test_max_are=item.limited_test_max_are,
                    k_max_status=item.k_max_status,
                    f_yield_status=item.f_yield_status,
                )
                for item in lookup_repository.list_planting_systems()
            ],
        )

    def simulate(
        self,
        payload: DSSSimulationRequest,
        user_id: str | None = None,
    ) -> DSSSimulationResponse:
        variety = self._find_variety(payload.rice_variety)
        planting_system = self._find_planting_system(payload.planting_system)
        constants = lookup_repository.get_constants()

        actual = self._evaluate_scenario(
            duck_count=payload.duck_count,
            land_area_are=payload.land_area_are,
            planting_date=payload.planting_date,
            variety=variety,
            planting_system=planting_system,
            constants=constants,
            duration_days=compute_actual_duration_days(variety.hst_masuk, variety.hst_heading),
            use_heading_pull_date=True,
        )
        recommended = self._search_recommendation(
            actual=actual,
            land_area_are=payload.land_area_are,
            planting_date=payload.planting_date,
            variety=variety,
            planting_system=planting_system,
            constants=constants,
        )

        recommended["reasoning_summary"] = self._build_reasoning(
            actual=actual,
            recommended=recommended,
        )

        notes = [
            "Model ini adalah deterministic mathematical model, bukan machine learning dan bukan IoT.",
            constants.calibration_note,
            "land_area_are diasumsikan sebagai area aktif yang benar-benar dimasuki bebek, bukan total lahan jika keduanya berbeda.",
            "duck_age_days dicatat sebagai konteks biologis, tetapi belum mengubah yield karena koefisien umur bebek belum terkalibrasi.",
            "Profit tidak dihitung karena harga gabah padi-bebek, baseline yield konvensional, dan kuantitas pakan belum lengkap.",
            "Hara tanah tidak dihitung karena koefisien kappa belum tersedia atau tervalidasi lokal.",
            "Output ekologis berstatus estimation_only; V_eco2 dihitung dari formula sigmoid DOCX sebagai estimasi rendah.",
            "Modul environment disabled sampai tersedia flux CH4 dan N2O musiman dalam satuan kg/ha/musim.",
        ]
        if actual["duration_days"] > actual["modeled_duration_days"]:
            notes.append(
                "Durasi aktual melebihi t_max_eff sehingga trace mencatat dua angka: durasi kalender aktual dan durasi yang dipakai model yield."
            )

        lookup = self._build_lookup(
            variety=variety,
            planting_system=planting_system,
        )
        validation = self._build_validation(
            payload=payload,
            actual=actual,
            variety=variety,
            planting_system=planting_system,
            constants=constants,
        )
        data_readiness = DataReadinessSummary(
            agronomy_ready="ready",
            yield_ready="estimation_only",
            economics_ready="partial",
            ecology_ready="estimation_only",
            environment_ready="disabled",
            overall_status="partial",
        )

        trace = {
            "area_conversion": {
                "formula": "A_ha = A_are / 100",
                "A_are": payload.land_area_are,
                "A_ha": round(actual["land_area_ha"], 4),
            },
            "density_calculation": {
                "formula": "d_are = J / A_are; d_ha = d_are * 100",
                "J": payload.duck_count,
                "A_are": payload.land_area_are,
                "d_are": round(actual["density_are"], 4),
                "d_ha": round(actual["density_ha"], 4),
            },
            "lookup_used": {
                "rice_variety": {
                    "code": variety.code,
                    "label": variety.label,
                    "hst_masuk": variety.hst_masuk,
                    "hst_heading": variety.hst_heading,
                    "harvest_age_days": variety.harvest_age_days,
                },
                "planting_system": {
                    "code": planting_system.code,
                    "label": planting_system.label,
                    "k_max_are": planting_system.k_max_are,
                    "f_yield": planting_system.f_yield,
                },
                "constants": {
                    "lambda": constants.survival_lambda,
                    "t_max_eff_days": constants.t_max_eff_days,
                    "p_max": constants.p_max,
                    "penalty_gamma": constants.penalty_gamma,
                    "alpha_local": constants.alpha_local,
                    "daily_duck_grazing_hours": constants.daily_duck_grazing_hours,
                    "baseline_grazing_hours": constants.baseline_grazing_hours,
                    "gwp_ch4": constants.gwp_ch4,
                    "gwp_n2o": constants.gwp_n2o,
                },
                "economic_defaults": {
                    "p_gabah_rd_rp_per_kg": constants.rice_duck_price_rp_per_kg,
                    "p_gabah_konv_rp_per_kg": constants.conventional_rice_price_rp_per_kg,
                    "x0_kg_per_ha": constants.conventional_yield_kg_per_ha,
                    "p_duck_sale_rp_per_duck": constants.duck_sale_price_rp_per_duck,
                    "p_duck_buy_rp_per_duck": constants.duck_buy_price_rp_per_duck,
                    "p_feed_rp_per_kg": constants.feed_price_rp_per_kg,
                    "weeding_cost_rp_per_are": constants.weeding_cost_rp_per_are,
                },
                "nutrient_defaults": {
                    "kappa_n": constants.kappa_n,
                    "kappa_p": constants.kappa_p,
                    "kappa_k": constants.kappa_k,
                },
            },
            "duration_calculation": {
                "formula": "t_aktual = HST_heading - HST_masuk",
                "hst_masuk": variety.hst_masuk,
                "hst_heading": variety.hst_heading,
                "duration_days": actual["duration_days"],
                "duration_used_in_yield_model": actual["modeled_duration_days"],
                "t_effective_days": round(actual["effective_duration_days"], 4),
                "t_effective_formula": "t * daily_duck_grazing_hours / baseline_grazing_hours",
            },
            "timeline_calculation": {
                "release_date_formula": "release_date = planting_date + HST_masuk",
                "pull_date_formula_actual": "pull_date = planting_date + HST_heading",
                "pull_date_formula_recommended": "pull_date = planting_date + HST_masuk + recommended_duration_days",
                "planting_date": payload.planting_date.isoformat(),
                "actual_release_date": actual["release_date"].isoformat(),
                "actual_pull_date": actual["pull_date"].isoformat(),
                "recommended_pull_date": recommended["pull_date"].isoformat(),
            },
            "survival_calculation": {
                "formula": "N_d = J * lambda",
                "J": payload.duck_count,
                "lambda": constants.survival_lambda,
                "N_d": round(actual["surviving_ducks"], 4),
            },
            "dung_calculation": {
                "formula_per_duck": "Jika t <= 50: (t/50)*4; jika t > 50: 4 + (t-50)*0.2",
                "formula_per_ha": "Dung_ha = Dung_total * d_ha * lambda",
                "duration_days_used": actual["modeled_duration_days"],
                "dung_total_per_duck_kg": round(actual["dung_total_per_duck_kg"], 4),
                "dung_total_kg_per_ha": round(
                    actual["dung_total_per_duck_kg"]
                    * actual["density_ha"]
                    * constants.survival_lambda,
                    4,
                ),
                "status": "estimation_only",
                "note": "Kotoran bebek belum diukur secara lokal pada data collection.",
            },
            "yield_model": {
                "formula": "x(d,t) = (-0.0103*d_ha^2 + 2.6314*d_ha + 7569.4) * exp(-((t - 80)^2 / (2 * 80^2)))",
                "density_basis": "d_ha",
                "x_base": round(actual["x_base"], 4),
                "p_rate": round(actual["penalty_rate"], 4),
                "x_penalized": round(actual["x_penalized"], 4),
                "f_yield": planting_system.f_yield,
                "alpha_local": constants.alpha_local,
                "x_final": round(actual["kg_per_ha"], 4),
            },
            "recommendation_grid_search": {
                "method": "grid_search",
                "candidate_basis": "integer_duck_count",
                "duck_count_range": {
                    "start": recommended["candidate_duck_count_min"],
                    "end": recommended["candidate_duck_count_max"],
                    "step": 1,
                },
                "duration_range_days": {
                    "start": 1,
                    "end": recommended["duration_limit_days"],
                    "step": 1,
                },
                "constraints": [
                    "recommended_density_are <= K_max_are",
                    "recommended_duration_days <= t_max_eff",
                    "HST_masuk + recommended_duration_days <= HST_heading",
                ],
                "objective": "score = normalized_yield - risk_penalty",
                "objective_components_used": recommended[
                    "objective_components_used"
                ],
                "objective_components_skipped": [
                    component
                    for component, used in (
                        ("normalized_profit", recommended["economics_component_used"]),
                        ("normalized_ecology", recommended["ecology_component_used"]),
                    )
                    if not used
                ],
                "candidate_count": recommended["candidate_count"],
                "best_duck_count": recommended["duck_count"],
                "best_candidate_density_are": round(recommended["density_are"], 4),
                "best_candidate_density_ha": round(recommended["density_ha"], 4),
                "density_formula": "best_candidate_density_are = best_duck_count / A_are",
                "best_duration_days": recommended["duration_days"],
                "best_score": round(recommended["score"], 6),
                "best_score_components": {
                    "normalized_profit": self._round_optional(
                        recommended["normalized_profit"],
                        6,
                    ),
                    "normalized_ecology": self._round_optional(
                        recommended["normalized_ecology"],
                        6,
                    ),
                    "normalized_yield": round(recommended["normalized_yield"], 6),
                    "risk_penalty": round(recommended["risk_penalty"], 6),
                },
            },
            "economics_calculation": {
                "delta_v_rice_formula": "(p_RD*x_final_kg_ha - p0*x0_kg_ha) * A_ha",
                "v_duck_formula": "N_d*p_duck - J*p_duck_buy - C_feed - Penalty_feed",
                "net_profit_formula": "R_gabah_RD + V_duck + V_eco - C_infra - additional_cost",
                "actual_net_profit_rp": self._round_optional(
                    actual["economics"]["net_profit_rp"],
                    2,
                ),
                "recommended_net_profit_rp": self._round_optional(
                    recommended["economics"]["net_profit_rp"],
                    2,
                ),
            },
            "soil_nutrient_calculation": {
                "formula": "kappa * (Dung_total/10) * d_ha * lambda",
                "actual": self._round_mapping(actual["nutrients"], 6),
                "recommended": self._round_mapping(recommended["nutrients"], 6),
            },
            "environment_calculation": {
                "co2e_formula": "F_CH4*GWP_CH4 + F_N2O*GWP_N2O",
                "ghgi_formula": "CO2e / x_final_kg_ha",
                "ch4_reduction_formula": "(F_CH4_konv-F_CH4_RD)/F_CH4_konv*100",
                "status": actual["environment"]["status"],
            },
        }

        response = DSSSimulationResponse(
            history_id=None,
            input=DSSInput(**payload.model_dump()),
            lookup=lookup,
            actual_scenario=ActualScenario(
                duck_count=actual["duck_count"],
                land_area_are=round(actual["land_area_are"], 4),
                land_area_ha=round(actual["land_area_ha"], 4),
                density_are=round(actual["density_are"], 4),
                density_ha=round(actual["density_ha"], 4),
                duration_days=actual["duration_days"],
                release_date=actual["release_date"],
                pull_date=actual["pull_date"],
                surviving_ducks=round(actual["surviving_ducks"], 4),
                dung_total_per_duck_kg=round(
                    actual["dung_total_per_duck_kg"],
                    4,
                ),
                dung_status="estimation_only",
                effective_duration_days=round(
                    actual["effective_duration_days"],
                    4,
                ),
                x_base_kg_per_ha=round(actual["x_base"], 4),
                penalty_rate=round(actual["penalty_rate"], 6),
                x_penalized_kg_per_ha=round(actual["x_penalized"], 4),
                predicted_yield=PredictedYield(
                    kg_per_ha=round(actual["kg_per_ha"], 4),
                    kg_per_are=round(actual["kg_per_are"], 4),
                    ton_per_ha=round(actual["kg_per_ha"] / 1000.0, 4),
                    estimated_total_kg=round(actual["estimated_total_kg"], 4),
                ),
                risk_status=actual["risk_status"],
            ),
            recommended_scenario=RecommendedScenario(
                recommended_duck_count=recommended["duck_count"],
                recommended_density_are=round(recommended["density_are"], 4),
                recommended_density_ha=round(recommended["density_ha"], 4),
                recommended_duration_days=recommended["duration_days"],
                recommended_release_date=recommended["release_date"],
                recommended_pull_date=recommended["pull_date"],
                surviving_ducks=round(recommended["surviving_ducks"], 4),
                dung_total_per_duck_kg=round(
                    recommended["dung_total_per_duck_kg"],
                    4,
                ),
                dung_status="estimation_only",
                effective_duration_days=round(
                    recommended["effective_duration_days"],
                    4,
                ),
                x_base_kg_per_ha=round(recommended["x_base"], 4),
                penalty_rate=round(recommended["penalty_rate"], 6),
                x_penalized_kg_per_ha=round(
                    recommended["x_penalized"],
                    4,
                ),
                predicted_yield=PredictedYield(
                    kg_per_ha=round(recommended["kg_per_ha"], 4),
                    kg_per_are=round(recommended["kg_per_are"], 4),
                    ton_per_ha=round(recommended["kg_per_ha"] / 1000.0, 4),
                    estimated_total_kg=round(recommended["estimated_total_kg"], 4),
                ),
                risk_status=recommended["risk_status"],
                reasoning_summary=recommended["reasoning_summary"],
            ),
            comparison=ComparisonSummary(
                duck_count_difference=recommended["duck_count"] - actual["duck_count"],
                density_difference_are=round(recommended["density_are"] - actual["density_are"], 4),
                yield_difference_kg_per_ha=round(recommended["kg_per_ha"] - actual["kg_per_ha"], 4),
                yield_difference_total_kg=round(recommended["estimated_total_kg"] - actual["estimated_total_kg"], 4),
                risk_change=self._risk_change(actual["risk_status"], recommended["risk_status"]),
                profit_difference_rp=self._difference_optional(
                    recommended["economics"]["net_profit_rp"],
                    actual["economics"]["net_profit_rp"],
                    2,
                ),
            ),
            risk=RiskSummary(
                actual_status=actual["risk_status"],
                recommended_status=recommended["risk_status"],
                density_risk=actual["risk_status"],
                phase_risk=(
                    "SAFE"
                    if actual["duration_days"] <= actual["max_duration_days"]
                    else "HIGH"
                ),
                feed_warning=(
                    "WARNING"
                    if actual["duration_days"]
                    > constants.local_feed_warning_phase_days
                    or actual["density_are"] > planting_system.k_max_are
                    else "LOW"
                ),
                survival_data_warning="ESTIMATION_ONLY",
                thresholds={
                    "low_max_are": round(0.8 * planting_system.k_max_are, 4),
                    "safe_max_are": round(planting_system.k_max_are, 4),
                    "warning_max_are": round(1.25 * planting_system.k_max_are, 4),
                },
                notes=self._risk_notes(
                    actual_density_are=actual["density_are"],
                    actual_duration_days=actual["duration_days"],
                    max_duration_days=actual["max_duration_days"],
                    planting_system=planting_system,
                ),
            ),
            trace=trace,
            notes=notes,
            economics=self._to_economics_summary(actual, recommended),
            ecology=self._to_ecology_summary(actual, recommended),
            environment=self._to_environment_summary(actual, recommended),
            validation=validation,
            data_readiness=data_readiness,
        )
        if user_id is not None:
            history = history_repository.create(
                user_id=user_id,
                input_data=response.input.model_dump(mode="json"),
                actual_scenario=response.actual_scenario.model_dump(mode="json"),
                recommended_scenario=response.recommended_scenario.model_dump(mode="json"),
                comparison=response.comparison.model_dump(mode="json"),
                risk=response.risk.model_dump(mode="json"),
                trace=response.trace,
                notes=response.notes,
                economics=response.economics.model_dump(mode="json"),
                ecology=response.ecology.model_dump(mode="json"),
                environment=response.environment.model_dump(mode="json"),
                lookup=response.lookup,
                validation=response.validation.model_dump(mode="json"),
                data_readiness=response.data_readiness.model_dump(mode="json"),
            )
            response.history_id = history.id
        return response

    def list_histories(self, user_id: str) -> HistoryListResponse:
        items: list[HistoryListItem] = []
        for history in history_repository.list_by_user(user_id):
            variety = lookup_repository.get_rice_variety(history.input_data["rice_variety"])
            planting_system = lookup_repository.get_planting_system(
                history.input_data["planting_system"]
            )
            items.append(
                HistoryListItem(
                    id=history.id,
                    created_at=history.created_at,
                    summary=HistorySummary(
                        rice_variety=(
                            variety.label
                            if variety is not None
                            else history.input_data["rice_variety"]
                        ),
                        planting_system=(
                            planting_system.label
                            if planting_system is not None
                            else history.input_data["planting_system"]
                        ),
                        duck_count=history.input_data["duck_count"],
                        land_area_are=history.input_data["land_area_are"],
                        actual_density_are=history.actual_scenario["density_are"],
                        recommended_duck_count=history.recommended_scenario[
                            "recommended_duck_count"
                        ],
                        risk_status=history.actual_scenario["risk_status"],
                        estimated_total_yield_kg=history.actual_scenario[
                            "predicted_yield"
                        ]["estimated_total_kg"],
                    ),
                )
            )
        return HistoryListResponse(data=items)

    def get_history(self, history_id: str, user_id: str) -> DSSSimulationResponse:
        history = history_repository.get_by_id_and_user(history_id, user_id)
        if history is None:
            raise ResourceNotFoundError(
                message=f"History '{history_id}' was not found.",
                field="history_id",
            )
        if (
            not history.economics
            or not history.ecology
            or not history.environment
            or not history.lookup
            or not history.validation
            or not history.data_readiness
        ):
            rebuilt = self.simulate(
                DSSSimulationRequest.model_validate(history.input_data),
                user_id=None,
            )
            rebuilt.history_id = history.id
            return rebuilt
        return DSSSimulationResponse(
            history_id=history.id,
            input=history.input_data,
            lookup=history.lookup,
            actual_scenario=history.actual_scenario,
            recommended_scenario=history.recommended_scenario,
            comparison=history.comparison,
            risk=history.risk,
            trace=history.trace,
            notes=history.notes,
            economics=history.economics,
            ecology=history.ecology,
            environment=history.environment,
            validation=history.validation,
            data_readiness=history.data_readiness,
        )

    def delete_history(self, history_id: str, user_id: str) -> DeleteHistoryResponse:
        deleted = history_repository.delete_by_id_and_user(history_id, user_id)
        if not deleted:
            raise ResourceNotFoundError(
                message=f"History '{history_id}' was not found.",
                field="history_id",
            )
        return DeleteHistoryResponse(message="Simulation history deleted successfully")

    def _find_variety(self, code: str) -> RiceVariety:
        variety = lookup_repository.get_rice_variety(code)
        if variety is None:
            raise InvalidReferenceError(message=f"Unknown rice_variety '{code}'.", field="rice_variety")
        return variety

    def _find_planting_system(self, code: str) -> PlantingSystem:
        planting_system = lookup_repository.get_planting_system(code)
        if planting_system is None:
            raise InvalidReferenceError(message=f"Unknown planting_system '{code}'.", field="planting_system")
        return planting_system

    def _evaluate_scenario(
        self,
        *,
        duck_count: int,
        land_area_are: float,
        planting_date,
        variety: RiceVariety,
        planting_system: PlantingSystem,
        constants: DSSConstants,
        duration_days: int,
        use_heading_pull_date: bool,
    ) -> dict:
        land_area_ha = convert_are_to_ha(land_area_are)
        density_are, density_ha = compute_density(duck_count, land_area_are)
        max_duration_days = compute_actual_duration_days(variety.hst_masuk, variety.hst_heading)
        modeled_duration_days = min(duration_days, constants.t_max_eff_days)
        release_date = compute_release_date(planting_date, variety.hst_masuk)
        pull_date = (
            compute_pull_date_from_hst(planting_date, variety.hst_heading)
            if use_heading_pull_date
            else compute_pull_date_from_duration(planting_date, variety.hst_masuk, duration_days)
        )
        surviving_ducks = compute_surviving_ducks(duck_count, constants.survival_lambda)
        dung_total_per_duck_kg = compute_dung_total(modeled_duration_days, constants)
        effective_duration_days = compute_effective_duration(
            modeled_duration_days,
            constants,
        )
        x_base, penalty_rate, x_penalized, kg_per_ha = compute_final_yield_kg_per_ha(
            density_are=density_are,
            duration_days=modeled_duration_days,
            k_max_are=planting_system.k_max_are,
            f_yield=planting_system.f_yield,
            constants=constants,
        )
        kg_per_are, estimated_total_kg = convert_yield_units(
            final_yield_kg_per_ha=kg_per_ha,
            land_area_are=land_area_are,
        )
        risk_status = compute_risk_status(
            density_are=density_are,
            k_max_are=planting_system.k_max_are,
            duration_days=duration_days,
            max_duration_days=max_duration_days,
        )
        nutrients = compute_soil_nutrients(
            dung_total_per_duck_kg=dung_total_per_duck_kg,
            density_ha=density_ha,
            constants=constants,
        )
        ecology = compute_ecology(
            density_are=density_are,
            duration_days=modeled_duration_days,
            area_are=land_area_are,
            k_max_are=planting_system.k_max_are,
            constants=constants,
        )
        economics = compute_economics(
            duck_count=duck_count,
            surviving_ducks=surviving_ducks,
            density_are=density_are,
            duration_days=modeled_duration_days,
            effective_duration_days=effective_duration_days,
            area_are=land_area_are,
            final_yield_kg_per_ha=kg_per_ha,
            base_yield_kg_per_ha=x_base,
            penalty_rate=penalty_rate,
            k_max_are=planting_system.k_max_are,
            partial_ecological_value_rp=ecology["partial_ecological_value_rp"],
            constants=constants,
        )
        environment = compute_environment(
            final_yield_kg_per_ha=kg_per_ha,
            constants=constants,
        )
        return {
            "duck_count": duck_count,
            "land_area_are": land_area_are,
            "land_area_ha": land_area_ha,
            "density_are": density_are,
            "density_ha": density_ha,
            "duration_days": duration_days,
            "modeled_duration_days": modeled_duration_days,
            "max_duration_days": max_duration_days,
            "release_date": release_date,
            "pull_date": pull_date,
            "surviving_ducks": surviving_ducks,
            "dung_total_per_duck_kg": dung_total_per_duck_kg,
            "effective_duration_days": effective_duration_days,
            "x_base": x_base,
            "penalty_rate": penalty_rate,
            "x_penalized": x_penalized,
            "kg_per_ha": kg_per_ha,
            "kg_per_are": kg_per_are,
            "estimated_total_kg": estimated_total_kg,
            "risk_status": risk_status,
            "nutrients": nutrients,
            "ecology": ecology,
            "economics": economics,
            "environment": environment,
        }

    def _search_recommendation(
        self,
        *,
        actual: dict,
        land_area_are: float,
        planting_date,
        variety: RiceVariety,
        planting_system: PlantingSystem,
        constants: DSSConstants,
    ) -> dict:
        duration_limit = min(actual["max_duration_days"], constants.t_max_eff_days)
        candidates: list[dict] = []
        minimum_duck_count = max(
            1,
            math.ceil(constants.minimum_density_are * land_area_are),
        )
        maximum_duck_count = math.floor(
            planting_system.k_max_are * land_area_are
        )
        if maximum_duck_count < minimum_duck_count:
            minimum_duck_count = 0
            maximum_duck_count = 0

        for duck_count in range(minimum_duck_count, maximum_duck_count + 1):
            for duration_days in range(1, duration_limit + 1):
                candidates.append(
                    self._evaluate_scenario(
                        duck_count=duck_count,
                        land_area_are=land_area_are,
                        planting_date=planting_date,
                        variety=variety,
                        planting_system=planting_system,
                        constants=constants,
                        duration_days=duration_days,
                        use_heading_pull_date=False,
                    )
                )

        yield_values = [candidate["kg_per_ha"] for candidate in candidates]
        # Incomplete local economics and ecology data must not affect ranking.
        # No unsupported weighting constants are introduced.
        use_economics = False
        use_ecology = False
        for candidate in candidates:
            normalized_yield = self._normalize(
                candidate["kg_per_ha"],
                yield_values,
            )
            risk_penalty = (
                0.0 if candidate["risk_status"] in {"LOW", "SAFE"} else 1.0
            )
            candidate["normalized_profit"] = None
            candidate["normalized_ecology"] = None
            candidate["normalized_yield"] = normalized_yield
            candidate["risk_penalty"] = risk_penalty
            candidate["score"] = normalized_yield - risk_penalty
            candidate["objective_components_used"] = [
                "normalized_yield",
                "risk_penalty",
            ]

        best = max(
            candidates,
            key=lambda item: (
                item["score"],
                item["kg_per_ha"],
                -risk_rank(item["risk_status"]),
                -item["duck_count"],
            ),
        )
        best["candidate_count"] = len(candidates)
        best["candidate_duck_count_min"] = minimum_duck_count
        best["candidate_duck_count_max"] = maximum_duck_count
        best["duration_limit_days"] = duration_limit
        best["economics_component_used"] = use_economics
        best["ecology_component_used"] = use_ecology
        return best

    def _build_lookup(
        self,
        *,
        variety: RiceVariety,
        planting_system: PlantingSystem,
    ) -> dict:
        parameter_metadata = {
            key: {
                "value": metadata.value,
                "unit": metadata.unit,
                "source": metadata.source,
                "status": metadata.status,
                "note": metadata.note,
                "min": metadata.minimum,
                "max": metadata.maximum,
            }
            for key, metadata in lookup_repository.get_parameter_metadata().items()
        }
        parameter_metadata["k_max_are"] = {
            "value": planting_system.k_max_are,
            "unit": "duck/are",
            "source": "data_collection",
            "status": planting_system.k_max_status,
            "note": planting_system.note,
            "min": planting_system.k_max_min_are,
            "max": planting_system.k_max_max_are,
            "limited_test_max": planting_system.limited_test_max_are,
        }
        parameter_metadata["f_yield"] = {
            "value": planting_system.f_yield,
            "unit": "ratio",
            "source": "model",
            "status": planting_system.f_yield_status,
            "note": "Faktor model belum memiliki pengukuran numerik lokal yang kuat.",
            "min": None,
            "max": None,
        }
        return {
            "rice_variety": {
                "code": variety.code,
                "label": variety.label,
                "hst_masuk": variety.hst_masuk,
                "hst_heading": variety.hst_heading,
                "harvest_age_days": variety.harvest_age_days,
                "status": variety.status,
            },
            "planting_system": {
                "code": planting_system.code,
                "label": planting_system.label,
                "k_max_are": planting_system.k_max_are,
                "f_yield": planting_system.f_yield,
                "k_max_status": planting_system.k_max_status,
                "f_yield_status": planting_system.f_yield_status,
            },
            "parameters": parameter_metadata,
        }

    def _build_validation(
        self,
        *,
        payload: DSSSimulationRequest,
        actual: dict,
        variety: RiceVariety,
        planting_system: PlantingSystem,
        constants: DSSConstants,
    ) -> ValidationSummary:
        violations: list[str] = []
        warnings: list[str] = []
        if actual["density_are"] > planting_system.k_max_are:
            violations.append("actual_density_exceeds_conservative_k_max")
        if variety.hst_masuk + actual["duration_days"] > variety.hst_heading:
            violations.append("actual_duration_passes_heading")
        if actual["duration_days"] > constants.t_max_eff_days:
            violations.append("actual_duration_exceeds_t_max_eff")
        if not 14 <= payload.duck_age_days <= 21:
            warnings.append(
                "duck_age_days berada di luar rentang lokal 14-21 hari; "
                "nilai hanya menjadi konteks risiko dan tidak mengubah yield."
            )
        warnings.extend(
            [
                "Survival lambda 0.67 adalah estimasi batas atas lokal, bukan rata-rata final.",
                "Jumlah pakan kg/ekor/hari tidak tersedia; ekonomi bebek dan profit tidak lengkap.",
                "Maintenance infrastruktur memakai placeholder 0 karena data tidak tercatat.",
            ]
        )
        missing = sorted(
            set(
                actual["economics"]["missing_parameters"]
                + actual["ecology"]["missing_parameters"]
                + actual["nutrients"]["missing_parameters"]
                + actual["environment"]["missing_parameters"]
            )
        )
        return ValidationSummary(
            input_valid=True,
            constraint_violations=violations,
            warnings=warnings,
            missing_parameters=missing,
        )

    def _normalize(self, value: float, values: list[float]) -> float:
        minimum = min(values)
        maximum = max(values)
        if maximum == minimum:
            return 1.0
        return (value - minimum) / (maximum - minimum)

    def _round_mapping(self, values: dict, digits: int) -> dict:
        return {
            key: round(value, digits) if isinstance(value, float) else value
            for key, value in values.items()
        }

    def _to_economics_summary(
        self,
        actual: dict,
        recommended: dict,
    ) -> EconomicsSummary:
        delta_profit = self._difference_optional(
            recommended["economics"]["net_profit_rp"],
            actual["economics"]["net_profit_rp"],
            2,
        )
        return EconomicsSummary(
            status="partial",
            actual=self._to_scenario_economics(actual["economics"]),
            recommended=self._to_scenario_economics(recommended["economics"]),
            delta_profit_rp=delta_profit,
            assumptions=[
                "Perspektif harga adalah gabah; harga gabah padi-bebek final belum tersedia.",
                "Baseline yield konvensional belum memiliki angka final yang sebanding.",
                "Jumlah pakan kg/ekor/hari tidak tersedia sehingga C_feed, V_duck, Laba_bersih, dan DeltaProfit tidak dihitung.",
                "Biaya infrastruktur tetap dihitung dari data jaring dan kandang yang tersedia.",
            ],
        )

    def _to_scenario_economics(self, values: dict) -> ScenarioEconomics:
        infrastructure = values["infrastructure"]
        return ScenarioEconomics(
            status=values["status"],
            perspective=values["perspective"],
            rice_revenue_rp=self._round_optional(values["rice_revenue_rp"], 2),
            conventional_rice_revenue_rp=self._round_optional(
                values["conventional_rice_revenue_rp"],
                2,
            ),
            delta_rice_value_rp=self._round_optional(
                values["delta_rice_value_rp"],
                2,
            ),
            duck_revenue_rp=round(values["duck_revenue_rp"], 2),
            duck_purchase_cost_rp=round(values["duck_purchase_cost_rp"], 2),
            feed_cost_rp=self._round_optional(values["feed_cost_rp"], 2),
            feed_cost_status=values["feed_cost_status"],
            duck_net_value_rp=self._round_optional(
                values["duck_net_value_rp"],
                2,
            ),
            infrastructure=InfrastructureOutput(
                status=infrastructure["status"],
                net_cost_per_cycle_rp=round(
                    infrastructure["net_cost_per_cycle_rp"],
                    2,
                ),
                shelter_cost_per_cycle_rp=round(
                    infrastructure["shelter_cost_per_cycle_rp"],
                    2,
                ),
                maintenance_cost_rp=round(
                    infrastructure["maintenance_cost_rp"],
                    2,
                ),
                total_infrastructure_cost_rp=round(
                    infrastructure["total_infrastructure_cost_rp"],
                    2,
                ),
                note=infrastructure["note"],
            ),
            penalty_yield_rp=self._round_optional(
                values["penalty_yield_rp"],
                2,
            ),
            penalty_feed_rp=self._round_optional(
                values["penalty_feed_rp"],
                2,
            ),
            net_profit_rp=self._round_optional(values["net_profit_rp"], 2),
            net_profit_rp_per_are=self._round_optional(
                values["net_profit_rp_per_are"],
                2,
            ),
            missing_parameters=values["missing_parameters"],
        )

    def _to_ecology_summary(
        self,
        actual: dict,
        recommended: dict,
    ) -> EcologySummary:
        return EcologySummary(
            status="estimation_only",
            actual=self._to_scenario_ecology(actual),
            recommended=self._to_scenario_ecology(recommended),
            assumptions=[
                "V_eco1 memakai formula model dan harga pupuk batas bawah, sehingga berstatus estimation_only.",
                "V_eco2 memakai formula sigmoid DOCX §5.7 sebagai estimasi rendah; pengurangan pestisida/herbisida belum terukur kuantitatif secara lokal.",
                "V_gulma memakai biaya weeding batas bawah Rp6.000/are dan r_gulma desain model.",
                "Kappa hara lokal dan uji kotoran bebek belum tersedia; N/P/K tanah bernilai null.",
            ],
        )

    def _to_scenario_ecology(self, scenario: dict) -> ScenarioEcology:
        ecology = scenario["ecology"]
        nutrients = scenario["nutrients"]
        area_ha = scenario["land_area_ha"]
        return ScenarioEcology(
            status=ecology["status"],
            fertilizer_saving_rp=round(ecology["fertilizer_saving_rp"], 2),
            fertilizer_saving_status=ecology["fertilizer_saving_status"],
            pesticide_herbicide_saving_rp=self._round_optional(
                ecology["pesticide_herbicide_saving_rp"],
                2,
            ),
            pesticide_herbicide_saving_status=ecology[
                "pesticide_herbicide_saving_status"
            ],
            weed_reduction_rate=round(ecology["weed_reduction_rate"], 4),
            weeding_saving_rp=round(ecology["weeding_saving_rp"], 2),
            weeding_saving_status=ecology["weeding_saving_status"],
            partial_ecological_value_rp=round(
                ecology["partial_ecological_value_rp"],
                2,
            ),
            total_ecological_value_rp=round(
                ecology["partial_ecological_value_rp"],
                2,
            ),
            included_components=ecology["included_components"],
            missing_parameters=ecology["missing_parameters"],
            soil_nutrients=SoilNutrients(
                status=nutrients["status"],
                n_kg_per_ha=self._round_optional(
                    nutrients["n_kg_per_ha"],
                    6,
                ),
                p2o5_kg_per_ha=self._round_optional(
                    nutrients["p2o5_kg_per_ha"],
                    6,
                ),
                k2o_kg_per_ha=self._round_optional(
                    nutrients["k2o_kg_per_ha"],
                    6,
                ),
                n_total_kg=self._multiply_optional(
                    nutrients["n_kg_per_ha"],
                    area_ha,
                    6,
                ),
                p2o5_total_kg=self._multiply_optional(
                    nutrients["p2o5_kg_per_ha"],
                    area_ha,
                    6,
                ),
                k2o_total_kg=self._multiply_optional(
                    nutrients["k2o_kg_per_ha"],
                    area_ha,
                    6,
                ),
                missing_parameters=nutrients["missing_parameters"],
            ),
        )

    def _to_environment_summary(
        self,
        actual: dict,
        recommended: dict,
    ) -> EnvironmentSummary:
        status = actual["environment"]["status"]
        return EnvironmentSummary(
            status=status,
            actual=self._to_scenario_environment(actual["environment"]),
            recommended=self._to_scenario_environment(recommended["environment"]),
            assumptions=[
                "CO2e dan GHGI hanya dihitung jika F_CH4 dan F_N2O tersedia dalam kg/ha/musim.",
                "Reduksi_CH4 hanya dihitung jika baseline CH4 konvensional tersedia.",
                "Data CH4, N2O, dan DO tidak tersedia pada data collection; modul disabled.",
                "Nilai null berarti data belum layak dihitung, bukan emisi nol.",
            ],
        )

    def _to_scenario_environment(self, values: dict) -> ScenarioEnvironment:
        return ScenarioEnvironment(
            status=values["status"],
            co2e_kg_per_ha_season=self._round_optional(
                values["co2e_kg_per_ha_season"],
                6,
            ),
            ghgi_kg_co2e_per_kg_yield=self._round_optional(
                values["ghgi_kg_co2e_per_kg_yield"],
                8,
            ),
            ch4_reduction_percent=self._round_optional(
                values["ch4_reduction_percent"],
                4,
            ),
            missing_parameters=values["missing_parameters"],
        )

    def _round_optional(self, value: float | None, digits: int) -> float | None:
        return round(value, digits) if value is not None else None

    def _difference_optional(
        self,
        first: float | None,
        second: float | None,
        digits: int,
    ) -> float | None:
        if first is None or second is None:
            return None
        return round(first - second, digits)

    def _multiply_optional(
        self,
        value: float | None,
        multiplier: float,
        digits: int,
    ) -> float | None:
        return round(value * multiplier, digits) if value is not None else None

    def _build_reasoning(self, *, actual: dict, recommended: dict) -> str:
        if risk_rank(recommended["risk_status"]) < risk_rank(actual["risk_status"]):
            return (
                "Skenario rekomendasi dipilih karena menurunkan risiko kepadatan, "
                "memenuhi batas HST, dan memberi yield model terbaik dalam mode aman."
            )
        if recommended["kg_per_ha"] > actual["kg_per_ha"]:
            return (
                "Skenario rekomendasi dipilih karena memberi yield model lebih tinggi "
                "tanpa melewati K_max, t_max_eff, atau fase heading."
            )
        return (
            "Skenario rekomendasi dipilih dari kombinasi jumlah bebek integer dan durasi "
            "yang memberi skor yield-risk terbaik dalam seluruh constraint aman."
        )

    def _risk_change(self, actual_status: str, recommended_status: str) -> str:
        actual_rank = risk_rank(actual_status)
        recommended_rank = risk_rank(recommended_status)
        if recommended_rank < actual_rank:
            return "improved"
        if recommended_rank > actual_rank:
            return "worsened"
        return "same"

    def _risk_notes(
        self,
        *,
        actual_density_are: float,
        actual_duration_days: int,
        max_duration_days: int,
        planting_system: PlantingSystem,
    ) -> list[str]:
        notes = [
            "Kepadatan terlalu tinggi dapat menyebabkan injakan dan kerusakan tanaman padi.",
            "Bebek harus ditarik sebelum fase keluar malai untuk mengurangi risiko makan bulir.",
            "Durasi terlalu panjang dapat meningkatkan kebutuhan pakan tambahan dan menurunkan efisiensi.",
            "Profit tidak dihitung final karena harga padi-bebek, baseline yield, dan jumlah pakan belum lengkap.",
            "Environment disabled karena CH4, N2O, dan DO musiman tidak tersedia.",
        ]
        if actual_density_are > planting_system.k_max_are:
            notes.append("Skenario aktual sudah melewati K_max sehingga penalti kepadatan aktif di model.")
        if actual_duration_days > max_duration_days:
            notes.append("Durasi aktual melebihi jendela aman kalender varietas.")
        return notes


dss_service = DSSService()
