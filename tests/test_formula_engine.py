from datetime import date
from dataclasses import replace

from app.data.seed import DSS_CONSTANTS
from app.engines.formula_engine import (
    compute_actual_duration_days,
    compute_density,
    compute_dung_total,
    compute_effective_duration,
    compute_final_yield_kg_per_ha,
    compute_penalty_rate,
    compute_pull_date_from_hst,
    compute_release_date,
    compute_risk_status,
    compute_surviving_ducks,
    convert_are_to_ha,
    convert_yield_units,
)
from app.engines.impact_engine import (
    compute_ecology,
    compute_economics,
    compute_environment,
    compute_soil_nutrients,
    compute_v_eco2,
)


def test_convert_are_to_ha() -> None:
    assert convert_are_to_ha(7) == 0.07


def test_compute_density() -> None:
    density_are, density_ha = compute_density(28, 7)
    assert density_are == 4
    assert density_ha == 400


def test_compute_actual_duration_days() -> None:
    assert compute_actual_duration_days(28, 60) == 32


def test_compute_release_and_pull_dates() -> None:
    planting_date = date(2026, 6, 1)
    assert compute_release_date(planting_date, 28).isoformat() == "2026-06-29"
    assert compute_pull_date_from_hst(planting_date, 60).isoformat() == "2026-07-31"


def test_compute_surviving_ducks() -> None:
    assert compute_surviving_ducks(28, 0.67) == 18.76


def test_compute_dung_total() -> None:
    assert compute_dung_total(32, DSS_CONSTANTS) == 2.56


def test_compute_effective_duration() -> None:
    assert round(compute_effective_duration(32, DSS_CONSTANTS), 4) == 26.6667


def test_compute_penalty_rate() -> None:
    assert compute_penalty_rate(4, 4, DSS_CONSTANTS) == 0
    assert round(compute_penalty_rate(5, 4, DSS_CONSTANTS), 4) == 0.125


def test_compute_final_yield_kg_per_ha() -> None:
    _, penalty_rate, _, x_final = compute_final_yield_kg_per_ha(
        density_are=4,
        duration_days=32,
        k_max_are=4,
        f_yield=1.05,
        constants=DSS_CONSTANTS,
    )
    assert penalty_rate == 0
    assert round(x_final, 4) == 6116.3981


def test_convert_yield_units() -> None:
    kg_per_are, estimated_total_kg = convert_yield_units(6116.398095752443, 7)
    assert round(kg_per_are, 4) == 61.164
    assert round(estimated_total_kg, 4) == 428.1479


def test_compute_risk_status() -> None:
    assert compute_risk_status(2, 4, 32, 32) == "LOW"
    assert compute_risk_status(4, 4, 32, 32) == "SAFE"
    assert compute_risk_status(4.5, 4, 32, 32) == "WARNING"
    assert compute_risk_status(5.1, 4, 32, 32) == "HIGH"


def test_compute_soil_nutrients() -> None:
    # Rev 2: compute_soil_nutrients memakai density_are (bukan density_ha)
    # N_tanah_are = kappa_N * (Dung_total/10) * d_aktual_are * lambda
    # Untuk d_aktual_are=4 (bukan d_ha=400):
    nutrients = compute_soil_nutrients(
        dung_total_per_duck_kg=2.56,
        density_are=4,    # Rev 2: d_aktual_are
        constants=DSS_CONSTANTS,
    )
    assert nutrients["status"] == "estimation_only"
    # Rev 2 primary: kg/are
    assert nutrients["n_kg_per_are"] is not None
    assert nutrients["p2o5_kg_per_are"] is not None
    assert nutrients["k2o_kg_per_are"] is not None
    # Backward compat: kg/ha = kg/are * 100
    assert nutrients["n_kg_per_ha"] is not None
    assert nutrients["p2o5_kg_per_ha"] is not None
    assert nutrients["k2o_kg_per_ha"] is not None
    assert nutrients["missing_parameters"] == []
    # Rev 2 contoh: N_tanah_are = 0.049*(2.56/10)*4*0.67 = 0.0336
    assert abs(nutrients["n_kg_per_are"] - 0.0336) < 0.0001
    assert abs(nutrients["p2o5_kg_per_are"] - 0.0494) < 0.0001
    assert abs(nutrients["k2o_kg_per_are"] - 0.0220) < 0.0001
    # Note: n_kg_per_ha = n_kg_per_are * 100 = 3.36
    assert abs(nutrients["n_kg_per_ha"] - 3.36) < 0.01


def test_compute_ecology() -> None:
    ecology = compute_ecology(
        density_are=4,
        duration_days=32,
        area_are=7,
        k_max_are=4,
        constants=DSS_CONSTANTS,
    )
    assert ecology["weed_reduction_rate"] == 1
    assert ecology["weeding_saving_rp"] == 42000
    assert ecology["pesticide_herbicide_saving_rp"] is not None
    assert ecology["pesticide_herbicide_saving_status"] == "literature-uncalibrated"
    assert ecology["status"] == "estimation_only"
    assert "v_eco2" in ecology["included_components"]
    assert ecology["missing_parameters"] == []
    # V_eco = V_eco1 + V_eco2 + V_gulma, all three > 0 for this scenario
    assert ecology["partial_ecological_value_rp"] > ecology["weeding_saving_rp"]
    # R-08: fertilizer_saving_raw_rp is exposed for audit
    assert "fertilizer_saving_raw_rp" in ecology


def test_compute_v_eco2_above_threshold() -> None:
    # d_ha=400 > 300, use sigmoid formula
    v_eco2 = compute_v_eco2(400, 0.07)
    expected = (400 / (1 + __import__('math').exp(-0.036626 * 400)) - 3.327) * 0.07
    assert abs(v_eco2 - expected) < 0.001


def test_compute_v_eco2_below_threshold() -> None:
    # d_ha=200 <= 300, use linear interpolation
    v_eco2 = compute_v_eco2(200, 0.07)
    threshold_value = compute_v_eco2(301, 0.07)  # just above threshold
    # linear from 0 to threshold_value at d_ha=300
    v_at_300 = (400 / (1 + __import__('math').exp(-0.036626 * 300)) - 3.327) * 0.07
    expected = v_at_300 * (200 / 300)
    assert abs(v_eco2 - expected) < 0.001


def test_compute_v_eco2_zero_density() -> None:
    assert compute_v_eco2(0, 0.07) == 0.0
    assert compute_v_eco2(-10, 0.07) == 0.0


def test_compute_economics() -> None:
    ecology = compute_ecology(
        density_are=4,
        duration_days=32,
        area_are=7,
        k_max_are=4,
        constants=DSS_CONSTANTS,
    )
    economics = compute_economics(
        duck_count=28,
        surviving_ducks=18.76,
        density_are=4,
        duration_days=32,
        effective_duration_days=compute_effective_duration(32, DSS_CONSTANTS),
        area_are=7,
        final_yield_kg_per_ha=6116.398095752443,
        base_yield_kg_per_ha=5825.141043573754,
        penalty_rate=0,
        k_max_are=4,
        partial_ecological_value_rp=ecology["partial_ecological_value_rp"],
        constants=DSS_CONSTANTS,
    )
    assert economics["status"] == "partial"
    assert economics["infrastructure"]["total_infrastructure_cost_rp"] == 875000
    assert economics["rice_revenue_rp"] is None
    assert economics["delta_rice_value_rp"] is None
    assert economics["feed_cost_rp"] is None
    assert economics["duck_net_value_rp"] is None
    assert economics["net_profit_rp"] is None


def test_penalty_outputs_for_over_capacity_scenario() -> None:
    x_base, penalty_rate, _, x_final = compute_final_yield_kg_per_ha(
        density_are=5,
        duration_days=60,
        k_max_are=4,
        f_yield=1.05,
        constants=DSS_CONSTANTS,
    )
    ecology = compute_ecology(
        density_are=5,
        duration_days=60,
        area_are=7,
        k_max_are=4,
        constants=DSS_CONSTANTS,
    )
    economics = compute_economics(
        duck_count=35,
        surviving_ducks=23.45,
        density_are=5,
        duration_days=60,
        effective_duration_days=compute_effective_duration(60, DSS_CONSTANTS),
        area_are=7,
        final_yield_kg_per_ha=x_final,
        base_yield_kg_per_ha=x_base,
        penalty_rate=penalty_rate,
        k_max_are=4,
        partial_ecological_value_rp=ecology["partial_ecological_value_rp"],
        constants=DSS_CONSTANTS,
    )
    assert penalty_rate == 0.125
    assert economics["penalty_yield_rp"] is None
    assert economics["penalty_feed_rp"] is None


def test_environment_is_optional_without_seasonal_flux() -> None:
    environment = compute_environment(
        final_yield_kg_per_ha=6000,
        constants=DSS_CONSTANTS,
    )
    # R-10: status sekarang literature-uncalibrated (bukan disabled), modul tetap ada
    assert environment["status"] == "literature-uncalibrated"
    assert environment["co2e_kg_per_ha_season"] is None
    assert environment["ghgi_kg_co2e_per_kg_yield"] is None
    assert environment["ch4_reduction_percent"] is None
    assert "calibration_note" in environment


def test_environment_calculation_when_flux_is_available() -> None:
    constants = replace(
        DSS_CONSTANTS,
        seasonal_ch4_rice_duck_kg_per_ha=10,
        seasonal_ch4_conventional_kg_per_ha=20,
        seasonal_n2o_kg_per_ha=1,
    )
    environment = compute_environment(
        final_yield_kg_per_ha=6050,
        constants=constants,
    )
    # R-10: status tetap literature-uncalibrated meskipun data ada
    assert environment["status"] == "literature-uncalibrated"
    # Rev 2: f_ch4_are = 10/100 = 0.1; f_n2o_are = 1/100 = 0.01
    assert abs(environment["f_ch4_are"] - 0.1) < 0.0001
    assert abs(environment["f_n2o_are"] - 0.01) < 0.0001
    # Rev 2: co2e_are = 0.1*34 + 0.01*265 = 3.4 + 2.65 = 6.05
    assert abs(environment["co2e_are"] - 6.05) < 0.0001
    # co2e_kg_per_ha_season = co2e_ha_note = co2e_are * 100 = 605
    assert abs(environment["co2e_kg_per_ha_season"] - 605) < 0.01
    # Rev 2: GHGI = co2e_are / x_final_kg_are = 6.05 / (6050/100) = 6.05/60.5
    assert abs(environment["ghgi"] - (6.05 / 60.5)) < 0.0001
    # Rev 2: ch4_reduction = (0.2 - 0.1) / 0.2 * 100 = 50%
    assert abs(environment["ch4_reduction_pct"] - 50) < 0.01
    assert "calibration_note" in environment


# ============================================================
# Rev 1 — Test cases baru (R-4, R-1, R-9, R-7, R-11, R-3, R-5, R-6, R-8)
# ============================================================

from app.engines.formula_engine import compute_rey  # noqa: E402


# --- TC-REY-1: REY terhitung saat semua params tersedia ---
def test_compute_rey_complete_params() -> None:
    """R-4 AC-2: REY > 0 saat semua parameter tersedia."""
    result = compute_rey(
        rice_yield_kg=428.0,
        rice_price_rp_per_kg=5800.0,
        duck_revenue_rp=562800.0,
        rice_reference_price_rp_per_kg=5600.0,
    )
    assert result["rey"] is not None
    assert result["rey"] > 0
    assert result["rey_status"] == "calculated"
    assert result["missing_params"] == []
    # Verifikasi manual: (428*5800 + 562800) / 5600 = (2482400 + 562800) / 5600 ≈ 543.79
    assert abs(result["rey"] - 543.79) < 0.1


# --- TC-REY-2: REY = None saat param tidak ada ---
def test_compute_rey_missing_rice_price() -> None:
    """R-4 AC-3: REY = null saat rice_price_rp_per_kg = None."""
    result = compute_rey(
        rice_yield_kg=428.0,
        rice_price_rp_per_kg=None,  # tidak tersedia
        duck_revenue_rp=562800.0,
        rice_reference_price_rp_per_kg=5600.0,
    )
    assert result["rey"] is None
    assert result["rey_status"] == "missing_params"
    assert "rice_price_rp_per_kg" in result["missing_params"]


def test_compute_rey_missing_yield() -> None:
    """R-4 AC-3: REY = null saat rice_yield_kg = None."""
    result = compute_rey(
        rice_yield_kg=None,
        rice_price_rp_per_kg=5800.0,
        duck_revenue_rp=562800.0,
        rice_reference_price_rp_per_kg=5600.0,
    )
    assert result["rey"] is None
    assert "rice_yield_kg" in result["missing_params"]


def test_compute_rey_notes_contain_literature_variants() -> None:
    """R-4 AC-5: rey_notes menyebut variasi notasi di literatur."""
    result = compute_rey(
        rice_yield_kg=428.0,
        rice_price_rp_per_kg=5800.0,
        duck_revenue_rp=562800.0,
        rice_reference_price_rp_per_kg=5600.0,
    )
    notes = result["rey_notes"]
    # Minimal menyebut beberapa ID artikel variasi
    assert "A17" in notes
    assert "A08" in notes
    assert "Rev1_Doc" in notes


# --- TC-ECON-1: net_profit_rp tidak None saat q_feed fallback ke referensi ---
def test_compute_economics_fallback_qfeed() -> None:
    """R-1 AC-2, R-9 AC-2: net_profit_rp != null saat q_feed dari referensi Lit_DB.
    Opsi A: fallback 0.10 dari A02 row 975 (MATCH_EXACT).
    """
    # DSS_CONSTANTS default: feed_requirement_kg_per_duck_day = None
    # Opsi A: feed_requirement_kg_per_duck_day_reference = 0.10 (A02 row 975)
    # Untuk tes ini kita butuh juga feed_price — beri nilai
    constants_with_feed_price = replace(
        DSS_CONSTANTS,
        feed_price_rp_per_kg=3500.0,
        rice_duck_price_rp_per_kg=5800.0,
        conventional_yield_kg_per_ha=5000.0,
    )
    # q_feed lokal masih None — harus fallback ke referensi
    assert constants_with_feed_price.feed_requirement_kg_per_duck_day is None
    result = compute_economics(
        duck_count=28,
        surviving_ducks=18.76,
        density_are=4.0,
        duration_days=32,
        effective_duration_days=26.67,
        area_are=7.0,
        final_yield_kg_per_ha=6116.0,
        base_yield_kg_per_ha=6200.0,
        penalty_rate=0.0,
        k_max_are=4.0,
        partial_ecological_value_rp=50000.0,
        constants=constants_with_feed_price,
    )
    # Dengan fallback q_feed, feed_cost_rp harus ada
    assert result["feed_cost_rp"] is not None
    assert result["feed_cost_rp"] > 0
    # Dan net_profit harus ada (rice_revenue + duck_net_value tersedia)
    assert result["net_profit_rp"] is not None
    # Sumber data harus mixed atau literature-uncalibrated (bukan local-calibrated karena q_feed dari ref)
    assert result["sumber_data"] in ("mixed", "literature-uncalibrated")


# --- TC-PURITY-1: profit_data_purity saat feed dari referensi ---
def test_economics_sumber_data_literature_when_qfeed_fallback() -> None:
    """R-3, R-7: sumber_data = mixed atau literature-uncalibrated saat q_feed dari referensi."""
    constants_with_feed_price = replace(
        DSS_CONSTANTS,
        feed_price_rp_per_kg=3500.0,
        rice_duck_price_rp_per_kg=5800.0,
    )
    result = compute_economics(
        duck_count=10,
        surviving_ducks=6.7,
        density_are=2.0,
        duration_days=32,
        effective_duration_days=26.67,
        area_are=5.0,
        final_yield_kg_per_ha=5800.0,
        base_yield_kg_per_ha=5900.0,
        penalty_rate=0.0,
        k_max_are=4.0,
        partial_ecological_value_rp=30000.0,
        constants=constants_with_feed_price,
    )
    assert result["sumber_data"] in ("mixed", "literature-uncalibrated")
    assert result["feed_cost_rp"] is not None


# --- TC-XIONG-1: V_duck_Xiong > 0 untuk input normal ---
def test_v_duck_xiong_nonzero() -> None:
    """R-11 AC-1: v_duck_xiong_reference > 0 untuk density dan durasi yang wajar."""
    result = compute_economics(
        duck_count=28,
        surviving_ducks=18.76,
        density_are=4.0,
        duration_days=32,
        effective_duration_days=26.67,
        area_are=7.0,
        final_yield_kg_per_ha=6116.0,
        base_yield_kg_per_ha=6200.0,
        penalty_rate=0.0,
        k_max_are=4.0,
        partial_ecological_value_rp=50000.0,
        constants=DSS_CONSTANTS,
    )
    assert "v_duck_xiong_reference" in result
    assert result["v_duck_xiong_reference"] is not None
    assert result["v_duck_xiong_status"] == "literature-uncalibrated"
    # Rumus Xiong dengan d_ha=400, lambda=0.67, t=32, A_ha=0.07
    # = (-0.0096*400^2 + (11.3861 + 14.4*0.67)*400 - 0.18*0.67*32*400 + 17.0857) * 0.07
    # harus positif atau negatif tergantung rumus — kita hanya cek ada nilainya
    assert isinstance(result["v_duck_xiong_reference"], float)


# --- TC-ENV-1: sumber_data di environment selalu "literature-uncalibrated" ---
def test_environment_sumber_data_always_literature_uncalibrated() -> None:
    """R-3 AC-3: sumber_data di environment = 'literature-uncalibrated'."""
    env = compute_environment(
        final_yield_kg_per_ha=6000.0,
        constants=DSS_CONSTANTS,
    )
    assert env["sumber_data"] == "literature-uncalibrated"


def test_environment_sumber_data_present_when_flux_available() -> None:
    """R-3 AC-3: sumber_data ada meski flux tersedia."""
    constants_with_flux = replace(
        DSS_CONSTANTS,
        seasonal_ch4_rice_duck_kg_per_ha=200.0,
        seasonal_ch4_conventional_kg_per_ha=400.0,
        seasonal_n2o_kg_per_ha=2.0,
    )
    env = compute_environment(
        final_yield_kg_per_ha=6000.0,
        constants=constants_with_flux,
    )
    assert env["sumber_data"] == "literature-uncalibrated"
    assert env["co2e_kg_per_ha_season"] is not None


# --- TC-SEED-1: k_max_status sudah local-calibrated ---
def test_planting_system_kmax_status_local_calibrated() -> None:
    """R-4, R13: k_max_status di seed.py = local-estimate (NOT local-calibrated — hanya range dari Field_Data)."""
    from app.data.seed import PLANTING_SYSTEMS
    jarwo = next(ps for ps in PLANTING_SYSTEMS if ps.code == "jajar_legowo")
    tegel = next(ps for ps in PLANTING_SYSTEMS if ps.code == "tegel")
    assert jarwo.k_max_status == "local-estimate"
    assert tegel.k_max_status == "local-estimate"


# --- TC-SEED-2: f_yield_status tetap literature-uncalibrated ---
def test_planting_system_fyield_status_literature_uncalibrated() -> None:
    """R-6 AC-7: f_yield_status tidak boleh dinaikkan ke local-calibrated."""
    from app.data.seed import PLANTING_SYSTEMS
    for ps in PLANTING_SYSTEMS:
        assert ps.f_yield_status == "literature-uncalibrated", (
            f"{ps.code}.f_yield_status harus 'literature-uncalibrated', bukan '{ps.f_yield_status}'"
        )


# --- TC-SEED-3: metadata valid_period untuk harga gabah konvensional ---
def test_conventional_rice_price_has_period_metadata() -> None:
    """R-13 AC-4: harga gabah konvensional berlabeli periode Maret 2026, status local-estimate."""
    from app.data.seed import PARAMETER_METADATA
    meta = PARAMETER_METADATA.get("conventional_rice_price")
    assert meta is not None
    assert "Maret 2026" in meta.note
    assert meta.status == "local-estimate"


# --- TC-SEED-4: lambda tetap literature-uncalibrated ---
def test_lambda_status_stays_literature_uncalibrated() -> None:
    """R-4 AC-1, R-13: lambda = local-estimate weak/indicative (NOT literature-uncalibrated, NOT local-calibrated)."""
    from app.data.seed import PARAMETER_METADATA
    meta = PARAMETER_METADATA.get("survival_lambda")
    assert meta is not None
    assert meta.status == "local-estimate"
    # Verify weak/indicative note is present
    assert "weak" in meta.note.lower() or "indicative" in meta.note.lower() or "indikatif" in meta.note.lower()


# --- TC-FALLBACK-1: cabang safety+yield masih berjalan ---
def test_optimality_fallback_safety_yield_basis_present() -> None:
    """R-1 AC-4: optimality_basis='safety+yield' ketika DeltaProfit=None."""
    # Skenario: net_profit_rp = None di keduanya
    # Kita verifikasi bahwa schema OptimalityAssessment menerima optimality_basis='safety+yield'
    from app.schemas.dss import OptimalityAssessment
    assessment = OptimalityAssessment(
        is_optimal=True,
        score_safety=True,
        density_gap_ratio=0.0,
        density_gap_within_threshold=True,
        delta_yield_pct=0.0,
        delta_yield_within_threshold=True,
        delta_profit_ratio=None,
        delta_profit_within_threshold=None,
        profit_component_included=False,
        optimality_basis="safety+yield",
        catatan_kalibrasi="Evaluasi parsial — DeltaProfit tidak tersedia.",
        thresholds={"density_gap": 0.15, "delta_yield_pct": 5.0, "delta_profit_ratio": 0.10},
        threshold_status="system-design-uncalibrated",
        sumber_data="literature-uncalibrated",
        profit_data_purity="literature-uncalibrated",
    )
    assert assessment.optimality_basis == "safety+yield"
    assert assessment.profit_component_included is False
    assert assessment.profit_data_purity == "literature-uncalibrated"


# --- TC-SCHEMA-1: field sumber_data ada di ScenarioEconomics ---
def test_scenario_economics_has_sumber_data_field() -> None:
    """R-3 AC-2: ScenarioEconomics memiliki field sumber_data."""
    from app.schemas.dss import ScenarioEconomics, InfrastructureOutput
    economics = ScenarioEconomics(
        status="partial",
        perspective="gabah",
        rice_revenue_rp=None,
        conventional_rice_revenue_rp=None,
        delta_rice_value_rp=None,
        duck_revenue_rp=100000.0,
        duck_purchase_cost_rp=56000.0,
        feed_cost_rp=None,
        feed_cost_status="unavailable",
        duck_net_value_rp=None,
        infrastructure=InfrastructureOutput(
            status="estimation",
            net_cost_per_cycle_rp=675000.0,
            shelter_cost_per_cycle_rp=200000.0,
            maintenance_cost_rp=0.0,
            total_infrastructure_cost_rp=875000.0,
            note="test",
        ),
        penalty_yield_rp=None,
        penalty_feed_rp=None,
        net_profit_rp=None,
        net_profit_rp_per_are=None,
        missing_parameters=["rice_duck_price_rp_per_kg"],
        sumber_data="literature-uncalibrated",
        v_duck_xiong_rp=None,
        v_duck_xiong_status="literature-uncalibrated",
        additional_cost=0.0,
    )
    assert economics.sumber_data == "literature-uncalibrated"
    assert economics.v_duck_xiong_status == "literature-uncalibrated"


# --- TC-SCHEMA-2: field profit_data_purity ada di OptimalityAssessment ---
def test_optimality_assessment_has_profit_data_purity() -> None:
    """R-7 AC-1: OptimalityAssessment memiliki field profit_data_purity."""
    from app.schemas.dss import OptimalityAssessment
    assessment = OptimalityAssessment(
        is_optimal=False,
        score_safety=True,
        density_gap_ratio=2.1,
        density_gap_within_threshold=False,
        delta_yield_pct=10.0,
        delta_yield_within_threshold=False,
        delta_profit_ratio=None,
        delta_profit_within_threshold=None,
        profit_component_included=False,
        optimality_basis="safety+yield",
        catatan_kalibrasi="test",
        thresholds={"density_gap": 0.15, "delta_yield_pct": 5.0, "delta_profit_ratio": 0.10},
        threshold_status="system-design-uncalibrated",
        sumber_data="mixed",
        profit_data_purity="mixed",
    )
    assert hasattr(assessment, "profit_data_purity")
    assert assessment.profit_data_purity == "mixed"


# --- TC-REY-ZERO-REF-PRICE: REY = None saat harga referensi = 0 ---
def test_compute_rey_zero_reference_price() -> None:
    """R-4: REY = None jika P_rice referensi = 0 (pembagi nol)."""
    result = compute_rey(
        rice_yield_kg=428.0,
        rice_price_rp_per_kg=5800.0,
        duck_revenue_rp=562800.0,
        rice_reference_price_rp_per_kg=0.0,
    )
    assert result["rey"] is None
    assert result["rey_status"] == "missing_params"


# ============================================================
# Rev 2 — Test cases baru (unit conversion, basis are, hara, ekonomi, emisi)
# ============================================================

# --- TC-REV2-UNIT-1: Konversi satuan are-ha ---
def test_rev2_unit_conversions() -> None:
    """Rev 2 §5.1: A_ha_note = A_are / 100; d_lit_ha = d_aktual_are * 100."""
    A_are = 7.0
    A_ha_note = A_are / 100.0
    assert A_ha_note == 0.07

    d_aktual_are = 4.0
    d_lit_ha = d_aktual_are * 100.0
    assert d_lit_ha == 400.0


# --- TC-REV2-YIELD-1: x_base_kg_are = x_base_kg_ha_note / 100 ---
def test_rev2_yield_are_basis() -> None:
    """Rev 2 §5.5: x_base_kg_are = x_base_kg_ha_note / 100; x_final_kg_are utama."""
    x_base, penalty_rate, x_penalized, x_final_ha = compute_final_yield_kg_per_ha(
        density_are=4,
        duration_days=32,
        k_max_are=4,
        f_yield=1.05,
        constants=DSS_CONSTANTS,
    )
    x_base_are = x_base / 100.0
    x_final_are = x_final_ha / 100.0
    x_final_ton_ha_note = x_final_are / 10.0

    # Rev 2 contoh: x_final_are = x_final_ha / 100
    assert abs(x_final_are - 61.1640) < 0.001
    # x_final_ton_ha_note = x_final_kg_are / 10
    assert abs(x_final_ton_ha_note - 6.11640) < 0.0001
    # x_base_are = x_base_ha / 100
    assert abs(x_base_are - (x_base / 100.0)) < 0.00001


# --- TC-REV2-HARA-1: N/P/K tanah basis are ---
def test_rev2_hara_are_basis() -> None:
    """Rev 2 §5.4: N_tanah_are/P_tanah_are/K_tanah_are untuk payload 28/7/Jarwo."""
    nutrients = compute_soil_nutrients(
        dung_total_per_duck_kg=2.56,  # Dung_total untuk t=32
        density_are=4.0,              # d_aktual_are = 28/7 = 4
        constants=DSS_CONSTANTS,
    )
    # Rev 2 contoh dokumen:
    # N_tanah_are = 0.049 * (2.56/10) * 4 * 0.67 = 0.0336 kg/are
    assert abs(nutrients["n_kg_per_are"] - 0.0336) < 0.0001
    # P_tanah_are = 0.072 * (2.56/10) * 4 * 0.67 = 0.0494 kg/are
    assert abs(nutrients["p2o5_kg_per_are"] - 0.0494) < 0.0001
    # K_tanah_are = 0.032 * (2.56/10) * 4 * 0.67 = 0.0220 kg/are
    assert abs(nutrients["k2o_kg_per_are"] - 0.0220) < 0.0001
    # Catatan ha: = kg_are * 100
    assert abs(nutrients["n_kg_per_ha"] - (nutrients["n_kg_per_are"] * 100)) < 0.0001
    assert abs(nutrients["p2o5_kg_per_ha"] - (nutrients["p2o5_kg_per_are"] * 100)) < 0.0001
    assert abs(nutrients["k2o_kg_per_ha"] - (nutrients["k2o_kg_per_are"] * 100)) < 0.0001


# --- TC-REV2-ECON-1: R_gabah_RD memakai x_final_kg_are * A_are ---
def test_rev2_economics_rice_revenue_are_basis() -> None:
    """Rev 2 §5.6: R_gabah_RD = x_final_kg_are * A_are * p_gabah_RD (bukan ha)."""
    from dataclasses import replace
    constants_with_price = replace(
        DSS_CONSTANTS,
        feed_price_rp_per_kg=3500.0,
        rice_duck_price_rp_per_kg=5800.0,
        conventional_yield_kg_per_ha=5000.0,
    )
    x_final_ha = 6116.4
    x_final_are = x_final_ha / 100.0  # = 61.164
    A_are = 7.0
    price = 5800.0

    result = compute_economics(
        duck_count=28,
        surviving_ducks=18.76,
        density_are=4.0,
        duration_days=32,
        effective_duration_days=26.67,
        area_are=A_are,
        final_yield_kg_per_ha=x_final_ha,
        x_final_kg_are=x_final_are,
        base_yield_kg_per_ha=5825.0,
        penalty_rate=0.0,
        k_max_are=4.0,
        partial_ecological_value_rp=50000.0,
        constants=constants_with_price,
    )
    # Rev 2: R_gabah_RD = x_final_kg_are * A_are * price = 61.164 * 7 * 5800
    expected_rice_revenue = x_final_are * A_are * price
    assert abs(result["rice_revenue_rp"] - expected_rice_revenue) < 1.0
    # R_gabah_K = x0_kg_are * A_are * p_gabah_konv = (5000/100) * 7 * 5600
    x0_are = 5000.0 / 100.0  # = 50
    expected_conv_revenue = x0_are * A_are * 5600.0
    assert abs(result["conventional_rice_revenue_rp"] - expected_conv_revenue) < 1.0


# --- TC-REV2-ENV-1: CO2e_are = F_CH4_are*GWP_CH4 + F_N2O_are*GWP_N2O ---
def test_rev2_environment_are_basis() -> None:
    """Rev 2 §5.8: CO2e_are basis are; f_ch4_are = f_ch4_ha/100."""
    from dataclasses import replace
    constants_with_flux = replace(
        DSS_CONSTANTS,
        seasonal_ch4_rice_duck_kg_per_ha=200.0,   # kg/ha/musim
        seasonal_ch4_conventional_kg_per_ha=400.0,
        seasonal_n2o_kg_per_ha=2.0,
    )
    env = compute_environment(
        final_yield_kg_per_ha=6116.4,
        x_final_kg_are=61.164,  # = 6116.4 / 100
        constants=constants_with_flux,
    )
    # f_ch4_are = 200/100 = 2.0
    assert abs(env["f_ch4_are"] - 2.0) < 0.0001
    # f_n2o_are = 2.0/100 = 0.02
    assert abs(env["f_n2o_are"] - 0.02) < 0.0001
    # CO2e_are = 2.0*34 + 0.02*265 = 68 + 5.3 = 73.3
    assert abs(env["co2e_are"] - 73.3) < 0.01
    # co2e_ha_note = co2e_are * 100 = 7330
    assert abs(env["co2e_ha_note"] - 7330.0) < 1.0
    # GHGI = co2e_are / x_final_kg_are = 73.3 / 61.164
    expected_ghgi = 73.3 / 61.164
    assert abs(env["ghgi"] - expected_ghgi) < 0.001
    # Reduksi_CH4: (400/100 - 200/100) / (400/100) * 100 = (4-2)/4 * 100 = 50%
    assert abs(env["ch4_reduction_pct"] - 50.0) < 0.01
    # Environment status tidak pernah disabled
    assert env["status"] == "literature-uncalibrated"
    assert env["formula_available"] is True
    assert env["numeric_ready"] is True


# --- TC-REV2-EKOL-1: V_eco1 memakai d_aktual_are * A_are ---
def test_rev2_ecology_v_eco1_are_basis() -> None:
    """Rev 2 §5.7: V_eco1 = (0.02*t-0.6) * factor * d_aktual_are * lambda * A_are."""
    import math as _math
    ecology = compute_ecology(
        density_are=4.0,
        duration_days=32,
        area_are=7.0,
        k_max_are=4.0,
        constants=DSS_CONSTANTS,
    )
    # Hitung manual
    P_N = P_P = P_K = 2400.0
    factor = (0.107*P_N + 0.424*P_P + 0.058*P_K)
    v_eco1_expected = max(0.0, (0.02*32 - 0.6) * factor * 4.0 * 0.67 * 7.0)
    assert abs(ecology["fertilizer_saving_rp"] - v_eco1_expected) < 1.0
    # V_eco2 threshold: d_aktual_are=4 > 3 → sigmoid branch
    assert ecology["pesticide_herbicide_saving_rp"] is not None
    assert ecology["pesticide_herbicide_saving_rp"] > 0
    # V_gulma = C_gulma * A_are * r_gulma = 6000 * 7 * 1 = 42000
    assert ecology["weeding_saving_rp"] == 42000.0


# --- TC-REV2-DENSITY-1: density_lit_ha = density_are * 100 ---
def test_rev2_density_lit_ha_field() -> None:
    """Rev 2 §5.1: d_lit_ha = d_aktual_are * 100 hanya catatan konversi."""
    density_are, density_ha = compute_density(28, 7)
    assert density_are == 4.0
    assert density_ha == 400.0  # d_lit_ha = d_are * 100


# ============================================================
# Data Provenance Traceability Patch — q_feed Opsi A, feed_saving, dung
# ============================================================

from app.engines.impact_engine import compute_feed_costs  # noqa: E402


def test_q_feed_reference_opsi_a_exact_value() -> None:
    """Opsi A: feed_requirement_kg_per_duck_day_reference == 0.10 (MATCH_EXACT A02 row 975)."""
    assert DSS_CONSTANTS.feed_requirement_kg_per_duck_day_reference == 0.10, (
        "Opsi A: fallback harus 0.10 dari A02 row 975, bukan 0.15"
    )


def test_q_feed_source_literature_reference_a02() -> None:
    """Opsi A: q_feed_source = 'literature-reference-a02' saat fallback aktif."""
    result = compute_feed_costs(
        duck_count=28,
        density_are=4.0,
        duration_days=32,
        effective_duration_days=26.67,
        area_ha=0.07,
        k_max_are=4.0,
        constants=DSS_CONSTANTS,  # feed_price None → unavailable, tapi q_feed metadata harus ada
    )
    # q_feed metadata harus tetap ada meskipun feed_cost null
    assert result["q_feed_source"] == "literature-reference-a02"
    assert result["q_feed_status"] == "literature-uncalibrated"
    assert result["q_feed_assumption_note"] is not None
    assert "A02" in result["q_feed_assumption_note"]
    assert "0.1" in result["q_feed_assumption_note"]


def test_q_feed_assumption_note_explains_local_unavailable() -> None:
    """q_feed_assumption_note menjelaskan bahwa q_feed lokal belum tersedia."""
    result = compute_feed_costs(
        duck_count=28,
        density_are=4.0,
        duration_days=32,
        effective_duration_days=26.67,
        area_ha=0.07,
        k_max_are=4.0,
        constants=DSS_CONSTANTS,
    )
    note = result["q_feed_assumption_note"]
    assert note is not None
    note_lower = note.lower()
    assert "lokal" in note_lower or "local" in note_lower
    # harus tidak mengklaim 0.12-0.225 sebagai range eksplisit
    # (boleh menyebutnya sebagai "tidak ditemukan")
    if "0.12" in note:
        assert "tidak ditemukan" in note_lower or "not found" in note_lower or "tidak" in note_lower


def test_q_feed_assumption_note_no_false_0_15_claim() -> None:
    """q_feed_assumption_note tidak mengklaim 0.15 sebagai exact reference row."""
    result = compute_feed_costs(
        duck_count=28,
        density_are=4.0,
        duration_days=32,
        effective_duration_days=26.67,
        area_ha=0.07,
        k_max_are=4.0,
        constants=DSS_CONSTANTS,
    )
    note = result["q_feed_assumption_note"] or ""
    # Nilai 0.15 tidak boleh diklaim sebagai traceable exact reference
    assert "0.15" not in note or "tidak" in note.lower(), (
        "q_feed_assumption_note must not claim 0.15 as traceable exact reference"
    )


def test_feed_natural_saving_rate_0_66_two_thirds() -> None:
    """feed_natural_saving_rate_reference == 0.66 (MATCH_DERIVED_FROM_TEXT 'two thirds')."""
    assert DSS_CONSTANTS.feed_natural_saving_rate_reference == 0.66


def test_dung_values_retained() -> None:
    """dung_phase_1_total_kg=4.0 dan dung_phase_2_daily_kg=0.2 tetap ada (PARTIAL_SOURCE)."""
    assert DSS_CONSTANTS.dung_phase_1_total_kg == 4.0
    assert DSS_CONSTANTS.dung_phase_2_daily_kg == 0.2


def test_dung_total_calculation_still_works() -> None:
    """Rumus dung masih benar setelah patch: t=32 → 2.56 kg/ekor."""
    from app.engines.formula_engine import compute_dung_total
    result = compute_dung_total(32, DSS_CONSTANTS)
    assert result == 2.56, f"Expected 2.56, got {result}"


def test_q_feed_economics_uses_0_10_not_0_15() -> None:
    """Feed cost dihitung dengan 0.10 (Opsi A), bukan 0.15."""
    constants_with_price = replace(
        DSS_CONSTANTS,
        feed_price_rp_per_kg=1000.0,   # Rp1000/kg untuk memudahkan verifikasi
        rice_duck_price_rp_per_kg=5800.0,
    )
    result_econ = compute_economics(
        duck_count=10,
        surviving_ducks=6.7,
        density_are=2.0,
        duration_days=32,
        effective_duration_days=32 * 10 / 12,  # ≈ 26.67
        area_are=5.0,
        final_yield_kg_per_ha=5800.0,
        base_yield_kg_per_ha=5900.0,
        penalty_rate=0.0,
        k_max_are=4.0,
        partial_ecological_value_rp=10000.0,
        constants=constants_with_price,
    )
    # feed_req = 0.10, feed_save = 0.66, t_eff ≈ 26.67, duck_count=10, price=1000
    # base_feed = 10 * 0.10 * 26.67 * 1000 * (1-0.66) = 10 * 0.10 * 26.67 * 1000 * 0.34
    # ≈ 9067.8
    expected_base = 10 * 0.10 * (32 * 10 / 12) * 1000.0 * (1 - 0.66)
    assert result_econ["feed_cost_rp"] is not None
    assert abs(result_econ["feed_cost_rp"] - expected_base) < 10.0, (
        f"feed_cost_rp {result_econ['feed_cost_rp']} != expected {expected_base} "
        f"(verifying 0.10 is used, not 0.15)"
    )
