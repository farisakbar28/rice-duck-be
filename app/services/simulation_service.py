import math

from app.core.exceptions import InvalidReferenceError, ResourceNotFoundError
from app.domain.models import DSSConstants, PlantingSystem, RiceVariety
from app.engines.formula_engine import (
    compute_actual_duration_days,
    compute_density,
    compute_dung_total,
    compute_duck_age_status,
    compute_effective_duration,
    compute_final_yield_kg_per_ha,
    compute_p_duck_buy_age,
    compute_pull_date_from_duration,
    compute_pull_date_from_hst,
    compute_quality_output,
    compute_release_date,
    compute_rey,
    compute_risk_status,
    compute_surviving_ducks,
    compute_t_age_max,
    compute_t_maks_rekomendasi,
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
    DuckAgeAssessment,
    DurationConstraintSummary,
    EcologySummary,
    EconomicsSummary,
    EnvironmentSummary,
    HistoryListItem,
    HistoryListResponse,
    HistorySummary,
    InfrastructureOutput,
    OptimalityAssessment,
    PlantingSystemOption,
    PredictedYield,
    QualityOutput,
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

        duck_age = compute_duck_age_status(payload.duck_age_days)
        duck_buy_price = compute_p_duck_buy_age(
            payload.duck_age_days,
            payload.duck_buy_price_rp_per_duck,
            constants,
        )
        hst_phase_limit_days = compute_actual_duration_days(variety.hst_masuk, variety.hst_heading)
        t_age_max = compute_t_age_max(
            payload.duck_age_days,
            hst_phase_limit_days,
            constants.duck_target_out_max_days,
        )
        t_maks_rekomendasi = compute_t_maks_rekomendasi(
            constants.t_max_eff_days,
            variety.hst_masuk,
            variety.hst_heading,
            t_age_max,
        )
        quality_raw = compute_quality_output(
            c_area=1.0 if payload.land_area_are > 0 else 0.0,
            c_calendar=1.0 if t_maks_rekomendasi > 0 else 0.4,
            c_age=duck_age["c_age"],
            c_price=(1.0 if payload.duck_buy_price_rp_per_duck is not None else (0.8 if not duck_buy_price["requires_actual_price"] else 0.4)),
            c_baseline=1.0 if constants.conventional_yield_kg_per_ha is not None else 0.6,
        )

        actual = self._evaluate_scenario(
            duck_count=payload.duck_count,
            land_area_are=payload.land_area_are,
            planting_date=payload.planting_date,
            variety=variety,
            planting_system=planting_system,
            constants=constants,
            duration_days=t_maks_rekomendasi,
            modeled_duration_days_override=min(
                constants.t_max_eff_days,
                hst_phase_limit_days,
            ),
            use_heading_pull_date=False,
            duck_age_days=payload.duck_age_days,
            duck_buy_price=duck_buy_price,
            t_age_max=t_age_max,
            t_maks_rekomendasi=t_maks_rekomendasi,
        )
        recommended = self._search_recommendation(
            actual=actual,
            land_area_are=payload.land_area_are,
            planting_date=payload.planting_date,
            variety=variety,
            planting_system=planting_system,
            constants=constants,
            duck_age_days=payload.duck_age_days,
            duck_buy_price=duck_buy_price,
            t_age_max=t_age_max,
            t_maks_rekomendasi=t_maks_rekomendasi,
        )

        recommended["reasoning_summary"] = self._build_reasoning(
            actual=actual,
            recommended=recommended,
        )

        notes = [
            "Model ini adalah deterministic mathematical model, bukan machine learning dan bukan IoT.",
            constants.calibration_note,
            "land_area_are diasumsikan sebagai area aktif yang benar-benar dimasuki bebek, bukan total lahan jika keduanya berbeda.",
            "Catatan: duck_age_days aktif untuk U_status, p_duck_buy_age, t_age_max, t_maks_rekomendasi, tanggal_tarik, dan quality output; tidak langsung mengubah yield, q_feed, survival, dung, N/P/K, V_eco, bobot jual, atau emisi.",
            "Catatan: Laba_bersih dan DeltaProfit hanya menerima pengaruh umur bebek melalui p_duck_buy_age di dalam C_duck_buy. Umur bebek tidak mengubah C_feed, yield, survival lambda, Dung_total, N/P/K, V_eco, bobot jual, atau emisi.",
            (
                "Rev 1: Laba_bersih dihitung menggunakan fallback referensi jika q_feed lokal tidak tersedia; "
                "status sumber data tersedia di economics.actual.sumber_data dan optimality_assessment.profit_data_purity. "
                "Jika Laba_bersih masih null, berarti feed_price_rp_per_kg dan/atau rice_duck_price_rp_per_kg belum tersedia."
            ),
            "Hara tanah dihitung sebagai estimation-only berbasis koefisien referensi kappa_N=0.049, kappa_P=0.072, kappa_K=0.032 yang belum dikalibrasi lokal Astungkara Way.",
            "Output ekologis V_eco1/V_eco2 berstatus literature-uncalibrated; V_gulma berstatus local-estimate.",
            "Modul emisi tetap limitation penelitian; tidak menjadi output numerik aktif dan tidak masuk objective.",
            "R-01: land_area_are diasumsikan area aktif bebek (A_active_duck_are). Jika berbeda dari total lahan, kepadatan dapat bias (warning bias area aktif).",
            (
                "REY (Rice Equivalent Yield) dihitung jika p_gabah_rd tersedia; "
                "5 variasi notasi di literatur — semua konsep setara (A17, A08, A19, A18, B5A06)."
            ),
        ]
        if actual["duration_days"] > actual["modeled_duration_days"]:
            notes.append(
                "Durasi aktual melebihi t_max_eff sehingga trace mencatat dua angka: durasi kalender aktual dan durasi yang dipakai model yield."
            )

        optimality = self._compute_optimality(
            actual=actual,
            recommended=recommended,
            planting_system=planting_system,
            variety=variety,
        )

        # Bagian B (aturan inti): gating rekomendasi hanya berdasarkan is_optimal.
        # Requirement baru: recommended_scenario/comparison hanya null jika aktual benar-benar best.
        show_recommendation = not optimality.is_optimal
        # Jangan memengaruhi rekomendasi berdasarkan safety_status/density tolerances.
        # recommended_scenario/comparison hanya null jika benar-benar best (optimality.is_optimal=True).
        if not show_recommendation:
            notes.append(
                "Kondisi aktual sudah identik dengan skenario terbaik menurut optimizer model, sehingga tidak ada rekomendasi alternatif."
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
            environment_ready="limitation",
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
                "formula": "t_rekomendasi <= min(t_max_eff, HST_heading - HST_masuk, t_age_max)",
                "hst_masuk": variety.hst_masuk,
                "hst_heading": variety.hst_heading,
                "hst_phase_limit_days": hst_phase_limit_days,
                "t_max_eff_days": constants.t_max_eff_days,
                "t_age_max_days": t_age_max,
                "t_maks_rekomendasi_days": t_maks_rekomendasi,
                "duration_days": actual["duration_days"],
                "duration_used_in_yield_model": actual["modeled_duration_days"],
                "t_effective_days": round(actual["effective_duration_days"], 4),
                "t_effective_formula": "t * daily_duck_grazing_hours / baseline_grazing_hours",
            },
            "timeline_calculation": {
                "release_date_formula": "release_date = planting_date + HST_masuk",
                "pull_date_formula_actual": "pull_date = planting_date + HST_masuk + actual_duration_days",
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
                    "recommended_duration_days <= t_maks_rekomendasi",
                    "HST_masuk + recommended_duration_days <= HST_heading",
                ],
                "objective": "score = normalized_yield + normalized_ecology + normalized_profit_if_ready - risk_penalty",
                "objective_components_used": recommended["objective_components_used"],

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
                "delta_v_rice_formula": "R_gabah_RD = x_final_kg_are * A_are * p_gabah_RD (Rev 2)",
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
                "formula": "kappa * (Dung_total/10) * d_aktual_are * lambda (Rev 2 basis are)",
                "actual": self._round_mapping(actual["nutrients"], 6),
                "recommended": self._round_mapping(recommended["nutrients"], 6),
            },
            "environment_calculation": {
                "co2e_formula": "CO2e_are = F_CH4_are*GWP_CH4 + F_N2O_are*GWP_N2O (Rev 2 basis are)",
                "ghgi_formula": "GHGI = CO2e_are / x_final_kg_are",
                "ch4_reduction_formula": "(F_CH4_konv_are - F_CH4_RD_are) / F_CH4_konv_are * 100%",
                "status": actual["environment"]["status"],
            },
        }

        response = DSSSimulationResponse(
            history_id=None,
            input=DSSInput(**payload.model_dump()),
            lookup=lookup,
            duck_age_assessment=DuckAgeAssessment(
                duck_age_days=payload.duck_age_days,
                u_status=duck_age["u_status"],
                c_age=duck_age["c_age"],
                p_duck_buy_age_rp=self._round_optional(duck_buy_price["price_rp"], 2),
                p_duck_buy_age_source=duck_buy_price["source"],
                p_duck_buy_age_status=duck_buy_price["status"],
                requires_actual_duck_buy_price=duck_buy_price["requires_actual_price"],
                note=duck_age["note"],
            ),
            duration_constraints=DurationConstraintSummary(
                t_max_eff_days=constants.t_max_eff_days,
                hst_phase_limit_days=hst_phase_limit_days,
                t_age_max_days=t_age_max,
                t_maks_rekomendasi_days=t_maks_rekomendasi,
                u_target_out_max_days=constants.duck_target_out_max_days,
            ),
            quality_output=QualityOutput(
                q_output=quality_raw["q_output"],
                score=round(quality_raw["score"], 4),
                components={key: round(val, 4) for key, val in quality_raw["components"].items()},
                notes=[
                    duck_buy_price["note"],
                    "Q_output hanya quality gate, bukan objective function.",
                ],
            ),
            actual_scenario=ActualScenario(
                duck_count=actual["duck_count"],
                land_area_are=round(actual["land_area_are"], 4),
                land_area_ha=round(actual["land_area_ha"], 4),
                land_area_ha_note=round(actual["land_area_ha"], 4),  # Rev 2: A_ha_note alias
                density_are=round(actual["density_are"], 4),
                density_ha=round(actual["density_ha"], 4),
                density_lit_ha=round(actual["density_ha"], 4),  # Rev 2: d_lit_ha = d_are * 100
                duration_days=actual["duration_days"],
                release_date=actual["release_date"],
                pull_date=actual["pull_date"],
                t_age_max_days=actual.get("t_age_max_days"),
                t_maks_rekomendasi_days=actual.get("t_maks_rekomendasi_days"),
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
                x_base_kg_are=round(actual["x_base"] / 100.0, 6),  # Rev 2
                penalty_rate=round(actual["penalty_rate"], 6),
                x_penalized_kg_per_ha=round(actual["x_penalized"], 4),
                x_penalized_kg_are=round(actual["x_penalized"] / 100.0, 6),  # Rev 2
                predicted_yield=PredictedYield(
                    kg_per_ha=round(actual["kg_per_ha"], 4),
                    kg_per_are=round(actual["kg_per_are"], 4),
                    ton_per_ha=round(actual["kg_per_ha"] / 1000.0, 4),
                    estimated_total_kg=round(actual["estimated_total_kg"], 4),
                ),
                risk_status=actual["risk_status"],
                # Rev 1 R-4: REY
                rey=self._round_optional(actual.get("rey"), 4),
                rey_status=actual.get("rey_status", "missing_params"),
                rey_notes=actual.get("rey_notes", ""),
            ),
            optimality_assessment=optimality,
            recommended_scenario=(
                RecommendedScenario(
                    recommended_duck_count=recommended["duck_count"],
                    recommended_density_are=round(recommended["density_are"], 4),
                    recommended_density_ha=round(recommended["density_ha"], 4),
                    recommended_density_lit_ha=round(recommended["density_ha"], 4),  # Rev 2
                    recommended_duration_days=recommended["duration_days"],
                    recommended_release_date=recommended["release_date"],
                    recommended_pull_date=recommended["pull_date"],
                    t_age_max_days=recommended.get("t_age_max_days"),
                    t_maks_rekomendasi_days=recommended.get("t_maks_rekomendasi_days"),
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
                    x_base_kg_are=round(recommended["x_base"] / 100.0, 6),  # Rev 2
                    penalty_rate=round(recommended["penalty_rate"], 6),
                    x_penalized_kg_per_ha=round(
                        recommended["x_penalized"],
                        4,
                    ),
                    x_penalized_kg_are=round(recommended["x_penalized"] / 100.0, 6),  # Rev 2
                    predicted_yield=PredictedYield(
                        kg_per_ha=round(recommended["kg_per_ha"], 4),
                        kg_per_are=round(recommended["kg_per_are"], 4),
                        ton_per_ha=round(recommended["kg_per_ha"] / 1000.0, 4),
                        estimated_total_kg=round(recommended["estimated_total_kg"], 4),
                    ),
                    risk_status=recommended["risk_status"],
                    reasoning_summary=recommended["reasoning_summary"],
                    # Rev 1 R-4: REY
                    rey=self._round_optional(recommended.get("rey"), 4),
                    rey_status=recommended.get("rey_status", "missing_params"),
                    rey_notes=recommended.get("rey_notes", ""),
                )
                if show_recommendation
                else None
            ),
            comparison=(
                ComparisonSummary(
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
                )
                if show_recommendation
                else None
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
                recommended_scenario=(
                    response.recommended_scenario.model_dump(mode="json")
                    if response.recommended_scenario is not None
                    else None
                ),
                comparison=(
                    response.comparison.model_dump(mode="json")
                    if response.comparison is not None
                    else None
                ),
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

            recommended_scenario = history.recommended_scenario or None
            recommended_duck_count = (
                recommended_scenario.get("recommended_duck_count")
                if isinstance(recommended_scenario, dict)
                else None
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
                        recommended_duck_count=recommended_duck_count
                        if recommended_duck_count is not None
                        else history.input_data["duck_count"],
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
        # Selalu re-simulate dari stored input agar optimality_assessment dan
        # field baru lainnya selalu dihitung ulang (tidak tersimpan di DB lama).
        rebuilt = self.simulate(
            DSSSimulationRequest.model_validate(history.input_data),
            user_id=None,
        )
        rebuilt.history_id = history.id
        return rebuilt

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
        modeled_duration_days_override: int | None = None,
        use_heading_pull_date: bool,
        duck_age_days: int,
        duck_buy_price: dict,
        t_age_max: int,
        t_maks_rekomendasi: int,
    ) -> dict:
        land_area_ha = convert_are_to_ha(land_area_are)
        density_are, density_ha = compute_density(duck_count, land_area_are)
        max_duration_days = t_maks_rekomendasi
        calendar_duration_days = duration_days
        modeled_duration_days = (
            modeled_duration_days_override
            if modeled_duration_days_override is not None
            else min(duration_days, t_maks_rekomendasi)
        )
        release_date = compute_release_date(planting_date, variety.hst_masuk)
        pull_date = (
            compute_pull_date_from_hst(planting_date, variety.hst_masuk + calendar_duration_days)
            if use_heading_pull_date
            else compute_pull_date_from_duration(planting_date, variety.hst_masuk, calendar_duration_days)
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
            duration_days=calendar_duration_days,
            max_duration_days=max_duration_days,
        )
        nutrients = compute_soil_nutrients(
            dung_total_per_duck_kg=dung_total_per_duck_kg,
            density_are=density_are,
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
            x_final_kg_are=kg_per_are,
            base_yield_kg_per_ha=x_base,
            penalty_rate=penalty_rate,
            k_max_are=planting_system.k_max_are,
            partial_ecological_value_rp=ecology["partial_ecological_value_rp"],
            duck_buy_price_rp_per_duck=duck_buy_price["price_rp"],
            duck_buy_price_source=duck_buy_price["source"],
            duck_buy_price_status=duck_buy_price["status"],
            duck_buy_price_requires_actual=duck_buy_price["requires_actual_price"],
            constants=constants,
        )
        environment = compute_environment(
            final_yield_kg_per_ha=kg_per_ha,
            x_final_kg_are=kg_per_are,   # Rev 2 primary
            constants=constants,
        )
        # R-4: REY = Σ(Y_i * P_i) / P_rice  (Rev1_Doc)
        rey_result = compute_rey(
            rice_yield_kg=estimated_total_kg if constants.rice_duck_price_rp_per_kg is not None else None,
            rice_price_rp_per_kg=constants.rice_duck_price_rp_per_kg,
            duck_revenue_rp=economics["duck_revenue_rp"],
            rice_reference_price_rp_per_kg=constants.conventional_rice_price_rp_per_kg,
        )
        return {
            "duck_count": duck_count,
            "land_area_are": land_area_are,
            "land_area_ha": land_area_ha,
            "density_are": density_are,
            "density_ha": density_ha,
            "duration_days": calendar_duration_days,
            "modeled_duration_days": modeled_duration_days,
            "max_duration_days": max_duration_days,
            "t_age_max_days": t_age_max,
            "t_maks_rekomendasi_days": t_maks_rekomendasi,
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
            "rey": rey_result["rey"],
            "rey_status": rey_result["rey_status"],
            "rey_notes": rey_result["rey_notes"],
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
        duck_age_days: int,
        duck_buy_price: dict,
        t_age_max: int,
        t_maks_rekomendasi: int,
    ) -> dict:
        duration_limit = t_maks_rekomendasi
        candidates: list[dict] = []
        minimum_duck_count = max(
            1,
            math.ceil(planting_system.recommended_density_min_are * land_area_are),
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
                        modeled_duration_days_override=None,
                        use_heading_pull_date=False,
                        duck_age_days=duck_age_days,
                        duck_buy_price=duck_buy_price,
                        t_age_max=t_age_max,
                        t_maks_rekomendasi=t_maks_rekomendasi,
                    )
                )

        scoring_population = candidates + [actual]
        yield_values = [candidate["kg_per_ha"] for candidate in scoring_population]

        # Rev 2 sesuai dokumentasi:
        #   score = normalized_yield - risk_penalty
        #   Ekonomi & ekologi hanya masuk jika data numeriknya tersedia.
        # Karena dokumen tidak memberi bobot eksplisit, komponen ekonomi/ekologi
        # dimasukkan sebagai tambahan langsung dalam skala normalized (konsisten
        # dengan normalisasi yield).
        profit_values = [
            c.get("economics", {}).get("net_profit_rp") for c in scoring_population
            if c.get("economics", {}).get("net_profit_rp") is not None
        ]
        ecology_values = [
            c.get("ecology", {}).get("partial_ecological_value_rp") for c in scoring_population
            if c.get("ecology", {}).get("partial_ecological_value_rp") is not None
        ]

        include_ecology_component = any(
            c.get("ecology", {}).get("partial_ecological_value_rp") is not None
            for c in scoring_population
        )

        for candidate in candidates:
            normalized_yield = self._normalize(
                candidate["kg_per_ha"],
                yield_values,
            )
            risk_penalty = (
                0.0 if candidate["risk_status"] in {"LOW", "SAFE"} else 1.0
            )

            profit_val = candidate.get("economics", {}).get("net_profit_rp")
            eco_val = candidate.get("ecology", {}).get(
                "partial_ecological_value_rp"
            )


            normalized_profit = (
                self._normalize(profit_val, profit_values)
                if profit_val is not None and len(profit_values) > 0
                else None
            )
            normalized_ecology = (
                self._normalize(eco_val, ecology_values)
                if eco_val is not None and len(ecology_values) > 0
                else None
            )

            candidate["normalized_profit"] = normalized_profit
            candidate["normalized_ecology"] = normalized_ecology
            candidate["normalized_yield"] = normalized_yield
            candidate["risk_penalty"] = risk_penalty

            score = normalized_yield - risk_penalty
            objective_components = ["normalized_yield", "risk_penalty"]

            if normalized_profit is not None:
                score += normalized_profit
                objective_components.append("normalized_profit")

            if normalized_ecology is not None and include_ecology_component:
                score += normalized_ecology
                objective_components.append("normalized_ecology")


            candidate["score"] = score
            candidate["objective_components_used"] = objective_components

        actual["normalized_yield"] = self._normalize(actual["kg_per_ha"], yield_values)
        actual_profit = actual.get("economics", {}).get("net_profit_rp")
        actual_ecology = actual.get("ecology", {}).get("partial_ecological_value_rp")
        actual["normalized_profit"] = (
            self._normalize(actual_profit, profit_values)
            if actual_profit is not None and len(profit_values) > 0
            else None
        )
        actual["normalized_ecology"] = (
            self._normalize(actual_ecology, ecology_values)
            if actual_ecology is not None and len(ecology_values) > 0
            else None
        )
        actual["risk_penalty"] = 0.0 if actual["risk_status"] in {"LOW", "SAFE"} else 1.0
        actual_score = actual["normalized_yield"] - actual["risk_penalty"]
        actual_components = ["normalized_yield", "risk_penalty"]
        if actual["normalized_profit"] is not None:
            actual_score += actual["normalized_profit"]
            actual_components.append("normalized_profit")
        if actual["normalized_ecology"] is not None and include_ecology_component:
            actual_score += actual["normalized_ecology"]
            actual_components.append("normalized_ecology")
        actual["score"] = actual_score
        actual["objective_components_used"] = actual_components

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
        best["economics_component_used"] = any(
            "normalized_profit" in c.get("objective_components_used", [])
            for c in candidates
        )
        best["ecology_component_used"] = any(
            "normalized_ecology" in c.get("objective_components_used", [])
            for c in candidates
        )

        # Simpan best_score agar evaluasi optimalitas bisa membandingkan actual vs best
        # secara exact (tanpa threshold heuristik).
        best["score"] = best["score"]

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
        if payload.duck_age_days < 14 or payload.duck_age_days > 30:
            warnings.append(
                "duck_age_days berada di luar rentang lokal 14-30 hari; meminta harga beli aktual dan memberi quality output lebih rendah."
            )
        warnings.extend(
            [
                "Survival lambda 0.67 adalah estimasi batas atas lokal, bukan rata-rata final.",
                "Jumlah pakan kg/ekor/hari tidak tersedia lokal; sistem menggunakan fallback referensi 0.10 kg/ekor/hari (literature-uncalibrated) dan nilai ini tidak berubah oleh umur bebek.",
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
                "Jumlah pakan kg/ekor/hari tidak tersedia lokal; sistem menggunakan fallback referensi q_feed=0.10 (literature-uncalibrated). net_profit_rp null jika harga gabah padi-bebek, harga pakan, atau harga beli bebek aktual yang wajib belum tersedia.",
                "Biaya infrastruktur tetap dihitung dari data jaring dan kandang yang tersedia.",
            ],
        )

    def _to_scenario_economics(self, values: dict) -> ScenarioEconomics:
        infrastructure = values["infrastructure"]
        return ScenarioEconomics(
            status=values["status"],
            status_data=values.get("status_data"),
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
            duck_purchase_cost_rp=self._round_optional(values["duck_purchase_cost_rp"], 2),
            duck_purchase_price_rp_per_duck=self._round_optional(values.get("duck_purchase_price_rp_per_duck"), 2),
            duck_purchase_price_source=values.get("duck_purchase_price_source"),
            duck_purchase_price_status=values.get("duck_purchase_price_status"),
            duck_purchase_price_requires_actual=values.get("duck_purchase_price_requires_actual", False),
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
            # Rev 1 field baru
            sumber_data=values.get("sumber_data", "literature-uncalibrated"),
            data_readiness=values.get("data_readiness"),
            formula_available=values.get("formula_available", True),
            numeric_ready=values.get("numeric_ready"),
            q_feed_source=values.get("q_feed_source"),
            q_feed_status=values.get("q_feed_status"),
            q_feed_assumption_note=values.get("q_feed_assumption_note"),
            v_duck_xiong_reference=self._round_optional(values.get("v_duck_xiong_reference"), 2),
            v_duck_xiong_model_value=self._round_optional(values.get("v_duck_xiong_model_value"), 2),
            v_duck_xiong_status=values.get("v_duck_xiong_status", "literature-uncalibrated"),
            additional_cost=round(values.get("additional_cost_rp", 0.0), 2),
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
        area_are = scenario["land_area_are"]
        area_ha = scenario["land_area_ha"]
        return ScenarioEcology(
            status=ecology["status"],
            fertilizer_saving_rp=round(ecology["fertilizer_saving_rp"], 2),
            fertilizer_saving_raw_rp=round(ecology["fertilizer_saving_raw_rp"], 2),
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
                # Rev 2 primary: kg/are
                n_kg_per_are=self._round_optional(nutrients.get("n_kg_per_are"), 6),
                p2o5_kg_per_are=self._round_optional(nutrients.get("p2o5_kg_per_are"), 6),
                k2o_kg_per_are=self._round_optional(nutrients.get("k2o_kg_per_are"), 6),
                # Backward compat: kg/ha (note)
                n_kg_per_ha=self._round_optional(nutrients.get("n_kg_per_ha"), 6),
                p2o5_kg_per_ha=self._round_optional(nutrients.get("p2o5_kg_per_ha"), 6),
                k2o_kg_per_ha=self._round_optional(nutrients.get("k2o_kg_per_ha"), 6),
                n_total_kg=self._multiply_optional(
                    nutrients.get("n_kg_per_are"),
                    area_are,
                    6,
                ),
                p2o5_total_kg=self._multiply_optional(
                    nutrients.get("p2o5_kg_per_are"),
                    area_are,
                    6,
                ),
                k2o_total_kg=self._multiply_optional(
                    nutrients.get("k2o_kg_per_are"),
                    area_are,
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
        # Rev 4: modul emisi tetap ada sebagai limitation-only.
        status = actual["environment"]["status"]
        return EnvironmentSummary(
            status=status,
            actual=self._to_scenario_environment(actual["environment"]),
            recommended=self._to_scenario_environment(recommended["environment"]),
            assumptions=[
                "Catatan: environment/emission menjadi limitation penelitian, bukan output numerik aktif.",
                "CO2e, GHGI, Reduksi_CH4, dan DO-to-CH4 tidak masuk objective function.",
                "Nilai null berarti modul sengaja tidak diaktifkan pada runtime, bukan emisi nol.",
            ],
        )

    def _to_scenario_environment(self, values: dict) -> ScenarioEnvironment:
        return ScenarioEnvironment(
            status=values["status"],
            calibration_note=values["calibration_note"],
            co2e_kg_per_ha_season=self._round_optional(
                values.get("co2e_kg_per_ha_season"),
                6,
            ),
            ghgi_kg_co2e_per_kg_yield=self._round_optional(
                values.get("ghgi_kg_co2e_per_kg_yield"),
                8,
            ),
            ch4_reduction_percent=self._round_optional(
                values.get("ch4_reduction_percent"),
                4,
            ),
            y_ch4_do_model=values.get("y_ch4_do_model"),
            missing_parameters=values["missing_parameters"],
            sumber_data=values.get("sumber_data", "literature-uncalibrated"),
            status_data=values.get("status_data"),
            catatan_kalibrasi=values.get("catatan_kalibrasi", values["calibration_note"]),
            data_readiness=values.get("data_readiness"),
            formula_available=values.get("formula_available", True),
            numeric_ready=values.get("numeric_ready"),
            # Rev 2 primary fields (are)
            co2e_are=self._round_optional(values.get("co2e_are"), 6),
            f_ch4_are=self._round_optional(values.get("f_ch4_are"), 6),
            f_n2o_are=self._round_optional(values.get("f_n2o_are"), 6),
            ghgi=self._round_optional(values.get("ghgi"), 8),
            ch4_reduction_pct=self._round_optional(values.get("ch4_reduction_pct"), 4),
            co2e_ha_note=self._round_optional(values.get("co2e_ha_note"), 6),
            f_ch4_ha_note=self._round_optional(values.get("f_ch4_ha_note"), 6),
            f_n2o_ha_note=self._round_optional(values.get("f_n2o_ha_note"), 6),
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
            "net_profit_rp null karena harga gabah padi-bebek dan/atau harga jual bebek belum tersedia lokal; komponen lain tetap dihitung.",
            "Modul emisi tetap limitation penelitian; belum diaktifkan sebagai output numerik backend.",
        ]
        if actual_density_are > planting_system.k_max_are:
            notes.append("Skenario aktual sudah melewati K_max sehingga penalti kepadatan aktif di model.")
        if actual_duration_days > max_duration_days:
            notes.append("Durasi aktual melebihi jendela aman kalender varietas.")
        return notes

    def _compute_optimality(
        self,
        *,
        actual: dict,
        recommended: dict,
        planting_system: PlantingSystem,
        variety: "RiceVariety",
    ) -> OptimalityAssessment:
        """Hitung optimalitas hanya berdasarkan perbandingan actual vs best_scenario dari optimizer.

        Rule final sesuai requirement:
        - recommended_scenario dan comparison hanya null jika actual identik dengan best_scenario.
        - is_optimal=true hanya jika actual == best_scenario (duck_count, density_are, duration_days dan score).

        floating_epsilon kecil dipakai untuk menghindari error floating.
        """
        floating_epsilon = 1e-6

        # ---- Safety flag tetap dihitung sebagai info, bukan dasar gating rekomendasi ----
        safety_hst = variety.hst_masuk + actual["duration_days"] <= variety.hst_heading
        safety_density = actual["density_are"] <= planting_system.k_max_are
        score_safety = safety_hst and safety_density and actual["land_area_are"] > 0

        # ---- Best scenario dari optimizer berada di parameter `recommended` ----
        actual_density_are = actual["density_are"]

        best_density_are = recommended["density_are"]

        actual_duration_days = actual["duration_days"]
        best_duration_days = recommended["duration_days"]

        actual_duck_count = actual["duck_count"]
        best_duck_count = recommended["duck_count"]

        # Requirement baru: hanya is_optimal jika actual benar-benar sama dengan best_scenario hasil optimizer.
        # Karena `recommended` di sini adalah best_scenario, maka bandingkan parameter diskret dan score exact
        # dengan floating_epsilon untuk guard error float.
        best_score = recommended.get("score")
        actual_score = actual.get("score")

        same_density = abs(actual_density_are - best_density_are) <= floating_epsilon
        same_duration = actual_duration_days == best_duration_days
        same_duck_count = actual_duck_count == best_duck_count
        same_score = (
            best_score is not None
            and abs((actual_score or 0.0) - best_score) <= floating_epsilon
        )

        is_optimal = same_duck_count and same_density and same_duration and same_score


        # Field-field threshold tetap diisi untuk struktur response (informasi tambahan),
        # tetapi tidak dipakai untuk menyembunyikan rekomendasi.
        density_gap_ratio = (
            (abs(actual_density_are - best_density_are) / best_density_are)
            if best_density_are not in (None, 0)
            else None
        )

        # Dev note: jangan gunakan heuristic thresholds untuk gating rekomendasi.


        delta_yield_pct = None
        if actual.get("kg_per_ha", 0) not in (None, 0):
            delta_yield_pct = (
                (recommended.get("kg_per_ha", 0) - actual.get("kg_per_ha", 0))
                / actual.get("kg_per_ha", 0)
            ) * 100.0

        # Profit ratio opsional; tetap dihitung jika data tersedia
        profit_ratio = None
        profit_component_included = False
        actual_profit = actual["economics"].get("net_profit_rp")
        rec_profit = recommended.get("economics", {}).get("net_profit_rp")
        if actual_profit is not None and rec_profit is not None and actual_profit != 0:
            profit_ratio = (rec_profit - actual_profit) / abs(actual_profit)
            profit_component_included = True

        econ_sumber = actual["economics"].get("sumber_data", "literature-uncalibrated")
        profit_data_purity = (
            "literature-uncalibrated"
            if actual["economics"].get("net_profit_rp") is None
            else econ_sumber
        )

        note = (
            "Kondisi aktual identik dengan skenario terbaik menurut optimizer model. "
            "Rekomendasi disembunyikan karena tidak ada skenario dengan objective score lebih baik."
            if is_optimal
            else "Kondisi aktual belum identik dengan skenario terbaik menurut optimizer model. "
            "Rekomendasi ditampilkan karena masih ada kombinasi dengan objective score lebih baik."
        )

        return OptimalityAssessment(

            is_optimal=is_optimal,

            score_safety=score_safety,
            density_gap_ratio=round(density_gap_ratio, 4) if density_gap_ratio is not None else None,
            density_gap_within_threshold=None,
            delta_yield_pct=round(delta_yield_pct, 4) if delta_yield_pct is not None else None,
            delta_yield_within_threshold=None,
            delta_profit_ratio=round(profit_ratio, 4) if profit_ratio is not None else None,
            delta_profit_within_threshold=None,
            profit_component_included=profit_component_included,
            optimality_basis=("best_scenario_match" if is_optimal else "best_scenario_mismatch"),
            catatan_kalibrasi=note,
            thresholds={},
            threshold_status="system-design-uncalibrated",
            sumber_data=profit_data_purity,
            profit_data_purity=profit_data_purity,
        )



dss_service = DSSService()
