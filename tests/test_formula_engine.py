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
    nutrients = compute_soil_nutrients(
        dung_total_per_duck_kg=2.56,
        density_ha=400,
        constants=DSS_CONSTANTS,
    )
    assert nutrients["status"] == "unavailable"
    assert nutrients["n_kg_per_ha"] is None
    assert nutrients["p2o5_kg_per_ha"] is None
    assert nutrients["k2o_kg_per_ha"] is None
    assert nutrients["missing_parameters"] == ["kappa_n", "kappa_p", "kappa_k"]


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
    assert ecology["pesticide_herbicide_saving_status"] == "estimation_only"
    assert ecology["status"] == "estimation_only"
    assert "v_eco2" in ecology["included_components"]
    assert ecology["missing_parameters"] == []
    # V_eco = V_eco1 + V_eco2 + V_gulma, all three > 0 for this scenario
    assert ecology["partial_ecological_value_rp"] > ecology["weeding_saving_rp"]


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
    assert environment["status"] == "disabled"
    assert environment["co2e_kg_per_ha_season"] is None
    assert environment["ghgi_kg_co2e_per_kg_yield"] is None
    assert environment["ch4_reduction_percent"] is None


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
    assert environment["status"] == "estimation_only"
    assert environment["co2e_kg_per_ha_season"] == 605
    assert environment["ghgi_kg_co2e_per_kg_yield"] == 0.1
    assert environment["ch4_reduction_percent"] == 50
