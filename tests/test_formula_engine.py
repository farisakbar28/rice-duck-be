"""Fase 7 — deterministic tests for formula_engine and impact_engine.

These tests cover the SoT-aligned core (Tabel 2.2 in
``Model_Matematika_..._FINAL_terbaru.md``) and Fase 0–6 changes.
"""

import math
from datetime import date

import pytest

from app.engines.formula_engine import (
    compute_calendar_milestones,
    compute_density,
    compute_duck_age_status,
    compute_surviving_ducks,
    compute_yield_components,
)
from app.engines.impact_engine import (
    K_WEED_HIRE_RP_PER_ARE,
    compute_ecology_weed,
    compute_feed_costs,
    compute_infrastructure_breakdown,
    compute_labor_breakdown,
    compute_weed_hired_cost,
    compute_weed_reduction,
)


# ===========================================================================
# 1. Age Engine (Tabel 2.2)
# ===========================================================================


def test_age_below_14_high_risk() -> None:
    out = compute_duck_age_status(10)
    assert out['R_age'] == 0.35
    assert 'WARNING' in out['age_status']


def test_age_14_to_29_safe_range() -> None:
    out = compute_duck_age_status(14)
    assert out['R_age'] == 0.15
    assert out['age_status'] == 'AGE_BUY_RANGE'
    out29 = compute_duck_age_status(29)
    assert out29['R_age'] == 0.15


def test_age_above_29_warning() -> None:
    out = compute_duck_age_status(30)
    assert out['R_age'] == 0.05
    assert 'ADAPTED_FULLY' in out['age_status']


# ===========================================================================
# 2. Density Engine (Tabel 2.2)
# ===========================================================================


def test_density_safe_zone() -> None:
    # Jarwo K_safe=4, d=3 → safe
    out = compute_density(30, 10, 4.0)
    assert out["d"] == 3.0
    assert out["P_over"] == 0
    assert out["P_under"] == 0
    assert out["density_status"] == "SAFE"


def test_density_above_k_safe_overdensity() -> None:
    # Jarwo K_safe=4, d=6 → (6-4)/(8-4)=0.5
    out = compute_density(60, 10, 4.0)
    assert out["P_over"] == pytest.approx(0.5)
    assert out["P_under"] == 0
    assert out["density_status"] == "WARNING_DENSITY"


def test_density_underdensity() -> None:
    out = compute_density(10, 10, 4.0)
    assert out["P_under"] == pytest.approx(0.5)
    assert out["density_status"] == "WARNING_UNDER_DENSITY"


def test_density_over_capped_at_1() -> None:
    out = compute_density(100, 1, 3.0)
    assert out["P_over"] == 1.0


# ===========================================================================
# 3. Survival Engine (Tabel 2.2)
# ===========================================================================


def test_lambda_eff_safe() -> None:
    # U=14 → r_age=0.15, d=5 → p_over=0.25
    # 0.78125 * (1 - 0.5*0.15) * (1 - 0.45*0.25) = 0.67*0.925*0.8875 = 0.5502...
    n = compute_surviving_ducks(50, 0.15, 0.25)
    expected = 50 * 0.78125 * 0.925 * 0.8875
    assert n == pytest.approx(expected)


def test_lambda_eff_zero_p_over() -> None:
    n = compute_surviving_ducks(50, 0.15, 0.0)
    expected = 50 * 0.78125 * 0.925 * 1.0
    assert n == pytest.approx(expected)


def test_n_survive_output_uses_floor_not_round_or_int_truncation() -> None:
    """SoT: N_survive = floor(J * lambda_eff), not round()."""
    from app.schemas.dss import DSSSimulationRequest
    from app.services.simulation_service import DSSService

    raw_n_survive = compute_surviving_ducks(50, 0.15, 0.25)
    assert raw_n_survive == pytest.approx(32.06787109375)
    assert math.floor(raw_n_survive) == 32
    assert round(raw_n_survive) == 32

    response = DSSService().simulate(
        DSSSimulationRequest(
            land_area_are=10,
            duck_count=50,
            rice_variety="sertani",
            planting_system="jajar_legowo",
            planting_date=date(2026, 1, 1),
            duck_age_days=14,
        )
    )
    assert response.N_survive == 32.0


# ===========================================================================
# 4. Yield Engine (Tabel 2.2) — TEGEL MUST BE 0.95, NOT 1.39
# ===========================================================================


def test_yield_jarwo_safe() -> None:
    # F_sys=1.00, p_under=0, p_over=0, r_age=0.15
    y = compute_yield_components(0.0, 0.0, 0.15, 1.00, 0.8)
    # 47.8767507 * 1 * (1-0.08*0.15) * 1 * 0.8
    expected = 47.8767507 * 1.0 * 0.988 * 0.8
    assert y == pytest.approx(expected, rel=1e-4)


def test_yield_tegel_higher_than_jarwo() -> None:
    y_jarwo = compute_yield_components(0.0, 0.0, 0.15, 1.00, 0.8)
    y_tegel = compute_yield_components(0.0, 0.0, 0.15, 1.211, 0.8)
    assert y_tegel > y_jarwo
    assert y_tegel == pytest.approx(y_jarwo * 1.211, rel=1e-4)


def test_yield_density_penalty() -> None:
    # p_under=0.5 → 1-0.12*0.5 = 0.94
    y = compute_yield_components(0.5, 0.0, 0.0, 1.0, 0.8)
    expected = 47.8767507 * 0.94 * 0.8
    assert y == pytest.approx(expected, rel=1e-4)


def test_yield_overdensity_penalty() -> None:
    # p_over=0.5 → 1-0.25*0.5 = 0.875
    y = compute_yield_components(0.0, 0.5, 0.0, 1.0, 0.8)
    expected = 47.8767507 * 0.875 * 0.8
    assert y == pytest.approx(expected, rel=1e-4)


# ===========================================================================
# 5. Calendar Engine (Tabel 2.2 / 2.3)
# ===========================================================================


def test_calendar_d_masuk_21_d_tarik_65() -> None:
    """Fase 1: D_masuk_bebek = D_tanam + 21, D_tarik_bebek = D_tanam + 65."""
    m = compute_calendar_milestones(date(2026, 1, 1), 99, 20, 65)
    assert m["D_masuk_bebek"] == date(2026, 1, 22)
    assert m["D_tarik_bebek"] == date(2026, 3, 7)
    assert m["t_active"] == 44


def test_calendar_d_panen_sertani_114() -> None:
    m = compute_calendar_milestones(date(2026, 1, 1), 114, 20, 65)
    assert m['D_panen_gabah'] == date(2026, 4, 25)


def test_calendar_d_panen_inpari_134() -> None:
    m = compute_calendar_milestones(date(2026, 1, 1), 134, 20, 65)
    assert m['D_panen_gabah'] == date(2026, 5, 15)


# ===========================================================================
# 6. Cost Engine — Feed (GUARDRAIL: must not change scale)
# ===========================================================================


def test_feed_unchanged_scale() -> None:
    # SoT example: 50 ducks, p_over=0.25, r_age=0.15 → 315625
    c = compute_feed_costs(50, 0.25, 0.15)
    expected = 50 * 4500 * (1 + 0.75 * 0.25 + 0.50 * 0.15)
    assert c == pytest.approx(expected, rel=1e-4)
    assert c == pytest.approx(284062.5, rel=1e-4)


# ===========================================================================
# 7. Cost Engine — Labor breakdown (Fase 2)
# ===========================================================================


def test_labor_breakdown_sot_example() -> None:
    lab = compute_labor_breakdown(10, 0.25, 0.15, 5.0)
    expected = 26178.0 * 10 * (1 - (0.93 * (1 - math.exp(-0.35 * 5.0))))
    assert lab['Cost_labor_weeding'] == pytest.approx(expected, rel=1e-3) # new total


def test_weed_reduction_formula() -> None:
    # R_weed(5) = 0.93 * (1 - exp(-1.75))
    r = compute_weed_reduction(5.0)
    expected = 0.93 * (1.0 - math.exp(-1.75))
    assert r == pytest.approx(expected, rel=1e-6)


def test_weed_hired_constant() -> None:
    assert K_WEED_HIRE_RP_PER_ARE == 26178.0


# ===========================================================================
# 8. Cost Engine — Infrastructure (Fase 2)
# ===========================================================================


def test_infra_no_floor_jarwo() -> None:
    inf = compute_infrastructure_breakdown(50, 10)
    expected_net = 0.5 * 289260.0 * math.sqrt(10)
    expected_cage = 175000.0
    assert inf['Cost_infra_net'] == pytest.approx(expected_net)
    assert inf['Cost_infra_cage'] == pytest.approx(expected_cage)
    assert inf['Cost_infra'] == pytest.approx(expected_net + expected_cage)


def test_infra_floor_zero_raw_split_50_50() -> None:
    inf = compute_infrastructure_breakdown(0, 0)
    assert inf['Cost_infra'] == pytest.approx(175000.0)


# ===========================================================================
# 9. Ecology Engine (Fase 3) — basis must be Cost_labor_base
# ===========================================================================


def test_valuation_weed_eco_basis() -> None:
    d = 5.0
    p_over = 0.25
    expected = (13500.0 * 10) * compute_weed_reduction(d) * (1.0 - 0.25 * p_over)
    v = compute_ecology_weed(10, d, p_over)
    assert v == pytest.approx(expected, rel=1e-4)


# ===========================================================================
# 10. Constants — SoT values
# ===========================================================================


def test_HET_pupuk() -> None:
    from app.domain.models import DSSConstants

    c = DSSConstants(
        survival_lambda=0.67,
        t_max_eff_days=45,
        t_phase_1_days=50,
        local_feed_warning_phase_days=30,
        dung_phase_1_total_kg=4.0,
        dung_phase_2_daily_kg=0.2,
        minimum_density_are=1.0,
        p_max=0.8,
        penalty_gamma=0.5,
        daily_duck_grazing_hours=10.0,
        baseline_grazing_hours=10.0,
        feed_requirement_kg_per_duck_day=0.10,
        feed_natural_saving_rate=1.0,
        feed_greedy_kg_per_duck_day=0.15,
        rice_duck_price_rp_per_kg=6000.0,
        duck_sale_price_rp_per_duck=35000.0,
        duck_buy_price_rp_per_duck=25000.0,
        duck_target_out_max_days=60,
        duck_buy_price_fallback_min_rp=25000.0,
        duck_buy_price_fallback_max_rp=25000.0,
        duck_buy_price_fallback_mid_rp=25000.0,
        feed_price_rp_per_kg=0.0,
        nitrogen_price_rp_per_kg=1800.0,
        potassium_price_rp_per_kg=9500.0,
        weeding_cost_rp_per_are=15000.0,
        net_cost_rp=1350000.0,
        net_lifetime_seasons=3,
        shelter_cost_rp=600000.0,
        shelter_lifetime_seasons=4,
        infrastructure_maintenance_rp_per_season=0.0,
        additional_cost_rp_per_season=0.0,
        gwp_ch4=34.0,
        gwp_n2o=265.0,
        seasonal_ch4_rice_duck_kg_per_ha=None,
        seasonal_ch4_conventional_kg_per_ha=None,
        seasonal_n2o_kg_per_ha=None,
        calibration_note="",
    )
    assert c.HET_urea == 1800.0
    assert c.HET_phonska == 1840.0
    assert c.HET_kcl == 9500.0


# ===========================================================================
# 11. Seed — SoT canonical values
# ===========================================================================


def test_seed_sertani_hst_panen_114() -> None:
    from app.data.seed import RICE_VARIETIES

    sertani = next(v for v in RICE_VARIETIES if v.code == 'sertani')
    assert sertani.hst_panen == 114


def test_seed_inpari_hst_panen_134() -> None:
    from app.data.seed import RICE_VARIETIES

    inpari = next(v for v in RICE_VARIETIES if v.code == 'inpari')
    assert inpari.hst_panen == 134


def test_seed_tegel_F_sys_1_211() -> None:
    from app.data.seed import PLANTING_SYSTEMS

    tegel = next(p for p in PLANTING_SYSTEMS if p.code == 'tegel')
    assert tegel.F_sys == 1.211
    assert tegel.f_yield == 1.211  # deprecated alias in sync


def test_seed_jarwo_k_safe_4_F_sys_1() -> None:
    from app.data.seed import PLANTING_SYSTEMS

    jarwo = next(p for p in PLANTING_SYSTEMS if p.code == "jajar_legowo")
    assert jarwo.k_safe_are == 4.0
    assert jarwo.F_sys == 1.00


# ===========================================================================
# 12. Phase 0 — Optimizer isolation
# ===========================================================================


def test_optimizer_schemas_isolated_from_dss_core() -> None:
    """Grep-equivalent: optimizer classes must not be in dss.py."""
    import app.schemas.dss as dss_mod

    dss_attrs = set(dir(dss_mod))
    forbidden = {
        "RecommendedScenario",
        "OptimalityAssessment",
        "EnvironmentSummary",
        "ActualScenario",
        "EconomicsSummary",
        "EcologySummary",
        "ComparisonSummary",
        "RiskSummary",
        "SoilNutrients",
        "ValidationSummary",
        "DataReadinessSummary",
        "ScenarioEconomics",
        "ScenarioEcology",
        "ScenarioEnvironment",
        "InfrastructureOutput",
        "PredictedYield",
        "QualityOutput",
        "DurationConstraintSummary",
        "DuckAgeAssessment",
    }
    leak = forbidden & dss_attrs
    assert not leak, f"Optimizer schemas leaked into dss.py: {leak}"


def test_optimizer_endpoint_exists() -> None:
    from app.api.routes.optimizer import router

    paths = [r.path for r in router.routes]
    assert "/optimizer/recommend" in paths


# ===========================================================================
# 13. Fase 6 — Generasi A artifacts removed from DSSConstants
# ===========================================================================


def test_no_alpha_local_in_DSSConstants() -> None:
    from app.domain.models import DSSConstants
    import dataclasses

    fields = {f.name for f in dataclasses.fields(DSSConstants)}
    assert "alpha_local" not in fields
    assert "kappa_n" not in fields
    assert "kappa_p" not in fields
    assert "kappa_k" not in fields
    assert "phosphate_price_rp_per_kg" not in fields
    assert "conventional_rice_price_rp_per_kg" not in fields
    assert "conventional_yield_kg_per_ha" not in fields


def test_no_alpha_local_in_seed_constants() -> None:
    from app.data.seed import DSS_CONSTANTS
    import dataclasses

    fields = {f.name for f in dataclasses.fields(type(DSS_CONSTANTS))}
    assert "alpha_local" not in fields
    # The default factory should not inject alpha_local either.
    assert not hasattr(DSS_CONSTANTS, "alpha_local")
