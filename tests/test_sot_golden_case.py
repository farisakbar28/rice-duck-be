import pytest
from fastapi.testclient import TestClient
from app.main import create_app

RP1 = 1.0

@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())

GOLDEN_PAYLOAD = {
    'land_area_are': 10,
    'duck_count': 50,
    'rice_variety': 'sertani',
    'planting_system': 'jajar_legowo',
    'planting_date': '2026-01-01',
    'duck_age_days': 14
}

def test_golden_full_response_matches_sot_tabel_2_3(client: TestClient) -> None:
    r = client.post('/api/v1/dss/simulate', json=GOLDEN_PAYLOAD)
    assert r.status_code == 200, r.text
    body = r.json()
    expected = {
        'density_status': 'WARNING_DENSITY',
        'age_status': 'AGE_BUY_RANGE',
        'D_masuk_bebek': '2026-01-22',
        'D_tarik_bebek': '2026-03-07',
        'D_panen_gabah': '2026-04-25',
        'N_survive': 32.0,
        'Yield_are_predict': 52.36,
        'Yield_total_predict': 523.6,
        'Revenue_gabah': 3141883.01,
        'Revenue_duck': 1120000.0,
        'Total_Revenue': 4261883.01,
        'Cost_duck_buy': 1250000.0,
        'Cost_feed_isolated': 284062.5,
        'Cost_weeding_isolated': 60630.8,
        'Cost_pesticide_isolated': 7238.06,
        'Cost_infra_isolated': 632360.22,
        'Cost_fertilizer_isolated': 104554.64,
        'Cost_infra_net_isolated': 457360.22,
        'Cost_infra_cage_isolated': 175000.0,
        'Cost_fert_urea_isolated': 16074.77,
        'Cost_fert_phonska_isolated': 88479.87,
        'Cost_fert_kcl_isolated': 0.0,
        'Cost_total_cash': 1250000.0,
        'Profit_net_cash': 3011883.01,
        'F_sys': 1.0
    }
    assert body == expected

def test_golden_response_excludes_cost_labor_tending(client: TestClient) -> None:
    r = client.post('/api/v1/dss/simulate', json=GOLDEN_PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    assert 'Cost_labor_tending' not in body

def test_golden_invariants_hold(client: TestClient) -> None:
    r = client.post('/api/v1/dss/simulate', json=GOLDEN_PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    assert body['Cost_infra_net_isolated'] + body['Cost_infra_cage_isolated'] == pytest.approx(body['Cost_infra_isolated'], abs=RP1)
    assert body['Cost_fert_urea_isolated'] + body['Cost_fert_phonska_isolated'] + body['Cost_fert_kcl_isolated'] == pytest.approx(body['Cost_fertilizer_isolated'], abs=RP1)
    assert body['Revenue_gabah'] + body['Revenue_duck'] == pytest.approx(body['Total_Revenue'], abs=RP1)
    assert body['Total_Revenue'] - body['Cost_total_cash'] == pytest.approx(body['Profit_net_cash'], abs=RP1)
