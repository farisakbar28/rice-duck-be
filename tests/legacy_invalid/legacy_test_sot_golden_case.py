import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


GOLDEN_PAYLOAD = {"land_area_are": 10, "duck_count": 20, "rice_variety": "sertani", "planting_system": "jajar_legowo", "duck_age_days": 21, "planting_date": "2026-01-01", "p_duck_buy": 15000}


def test_golden_core_response_matches_final_sot(client: TestClient) -> None:
    response = client.post("/api/v1/dss/simulate", json=GOLDEN_PAYLOAD)
    assert response.status_code == 200, response.text
    body = response.json()
    expected = {"density_status": "RECOMMENDED", "age_flag": "RECOMMENDED", "D_in": "2026-01-22", "D_out": "2026-03-07", "D_panen_min": "2026-04-11", "D_panen_max": "2026-04-21", "N_survive": 20, "Yield_are_pred": 47.8767507, "Yield_total_pred": 478.7675, "Revenue_gabah": 2872605.04, "Revenue_duck_potential": 1050000.0, "Cost_duck_buy": 300000.0, "Cost_feed": 400000.0, "Core_Cash_Cost": 700000.0, "Total_Revenue_DSS": 3922605.04, "Net_Cash_Contribution_DSS": 3222605.04}
    assert {key: body[key] for key in expected} == expected


def test_golden_response_excludes_legacy_contract(client: TestClient) -> None:
    body = client.post("/api/v1/dss/simulate", json=GOLDEN_PAYLOAD).json()
    forbidden = {"Profit_net_cash", "Cost_feed_isolated", "Cost_total_cash", "F_sys", "Yield_are_predict", "Revenue_duck", "D_masuk_bebek", "D_tarik_bebek", "D_panen_gabah", "age_status"}
    assert not (forbidden & body.keys())


def test_core_economic_invariant(client: TestClient) -> None:
    body = client.post("/api/v1/dss/simulate", json=GOLDEN_PAYLOAD).json()
    assert body["Core_Cash_Cost"] == pytest.approx(body["Cost_duck_buy"] + body["Cost_feed"])
    assert body["Total_Revenue_DSS"] == pytest.approx(body["Revenue_gabah"] + body["Revenue_duck_potential"])
    assert body["Net_Cash_Contribution_DSS"] == pytest.approx(body["Total_Revenue_DSS"] - body["Core_Cash_Cost"])
