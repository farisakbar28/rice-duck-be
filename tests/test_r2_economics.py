from app.services.simulation_service import dss_service
from app.schemas.dss import DSSSimulationRequest

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
