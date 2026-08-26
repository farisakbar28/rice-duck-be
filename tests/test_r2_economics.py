from app.services.simulation_service import dss_service
from app.schemas.dss import DSSSimulationRequest
import pytest


def _body(variety="inpari", age=21, count=20, area=10):
    return _response(variety, age, count, area).model_dump(mode="json", by_alias=True)

def _response(variety="inpari", age=21, count=20, area=10):
    return dss_service.simulate(DSSSimulationRequest(land_area_are=area, duck_count=count, planting_date="2026-01-01", planting_system="jajar_legowo", rice_variety=variety, duck_age_days=age))

def test_phase6_yield_economics_are_range_aware_and_partial():
    r = _response()
    e = r.economics
    assert e.paddy_revenue_low_rp < e.paddy_revenue_ref_rp < e.paddy_revenue_high_rp
    assert e.cash_revenue_ref_rp == e.paddy_revenue_ref_rp
    assert e.gross_economic_value_low_rp < e.gross_economic_value_ref_rp < e.gross_economic_value_high_rp
    assert e.margin_core_low_rp < e.margin_core_ref_rp < e.margin_core_high_rp
    assert e.profit_full_est_rp is None and r.costs.cost_completeness.value == "INCOMPLETE"
    assert r.duck.terminal_value_is_cash_revenue is False

def test_phase6_unavailable_yield_propagates_null_economics():
    r = _response(age=20)
    assert r.crop_yield.yield_ref_kg_per_are is None
    assert r.economics.paddy_revenue_ref_rp is None
    assert r.economics.cash_revenue_ref_rp is None


def test_purchase_identity_uses_default_price():
    body = _body()
    assert body["costs"]["duck_purchase"]["amount_rp"] == 20 * 26500


def test_paddy_revenue_equals_reference_yield_times_hpp():
    body = _body()
    assert body["economics"]["paddy_revenue_ref_rp"] == body["yield"]["yield_total_ref_kg"] * 6500


def test_cash_revenue_is_paddy_only_not_terminal_asset():
    body = _body()
    econ, duck = body["economics"], body["duck"]
    assert econ["cash_revenue_ref_rp"] == econ["paddy_revenue_ref_rp"]
    assert econ["gross_economic_value_ref_rp"] == econ["cash_revenue_ref_rp"] + duck["terminal_value_ref_rp"]


@pytest.mark.parametrize("suffix", ["low", "ref", "high"])
def test_economic_range_fields_propagate_each_yield_branch(suffix):
    body = _body()
    econ = body["economics"]
    assert econ[f"paddy_revenue_{suffix}_rp"] is not None
    assert econ[f"cash_revenue_{suffix}_rp"] == econ[f"paddy_revenue_{suffix}_rp"]
    assert econ[f"gross_economic_value_{suffix}_rp"] is not None
    assert econ[f"margin_core_{suffix}_rp"] is not None


def test_economic_range_order_is_monotonic():
    econ = _body()["economics"]
    for prefix in ("paddy_revenue", "cash_revenue", "gross_economic_value", "margin_core"):
        assert econ[f"{prefix}_low_rp"] < econ[f"{prefix}_ref_rp"] < econ[f"{prefix}_high_rp"]


def test_available_cost_subtotal_excludes_unknown_feed_and_cage():
    costs = _body()["costs"]
    assert costs["feed"]["amount_rp"] is None
    assert costs["cage"]["total_amount_rp"] is None
    assert costs["cost_total_available_rp"] > costs["cost_core_direct_rp"] > 0


def test_full_profit_stays_null_for_incomplete_ledger():
    econ = _body()["economics"]
    assert econ["profit_full_est_rp"] is None
    assert econ["profit_full_status"] == "UNAVAILABLE_INCOMPLETE_COST"


@pytest.mark.parametrize("age", [20, 31])
def test_unsupported_yield_nulls_all_yield_dependent_economics(age):
    econ = _body(age=age)["economics"]
    for key in ("paddy_revenue_rp", "paddy_revenue_ref_rp", "cash_revenue_rp", "gross_economic_value_rp", "margin_core_rp"):
        assert econ[key] is None
