from fastapi.testclient import TestClient

from app.main import create_app


def test_visualization_contract_uses_final_sot_semantics() -> None:
    client = TestClient(create_app())
    response = client.post("/api/v1/dss/visualize", json={"duck_count": 20, "land_area_are": 10, "rice_variety": "sertani", "planting_system": "jajar_legowo", "duck_age_days": 21, "planting_date": "2026-01-01", "p_duck_buy": 15000})
    assert response.status_code == 200, response.text
    body = response.json()
    assert len(body["density_zones"]) == 100 and len(body["age_zones"]) == 45
    assert next(point for point in body["density_zones"] if point["density"] == 4.0)["density_status"] == "RECOMMENDED"
    assert next(point for point in body["density_zones"] if point["density"] == 8.1)["survival_rate"] == 0.6
    assert body["age_zones"][19]["age_flag"] == "TOO_YOUNG" and body["age_zones"][20]["age_flag"] == "RECOMMENDED"
    assert body["reference_benchmarks"]["yield_baseline_kg_per_are"] == 47.8767507
    assert [node["name"] for node in body["financial_waterfall"]] == ["Revenue Gabah", "Revenue Potensial Bebek", "Biaya Beli Bebek", "Biaya Pakan", "Net_Cash_Contribution_DSS"]
    assert "F_density_bio" not in str(body)
