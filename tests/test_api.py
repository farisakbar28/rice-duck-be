from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_rice_variety_lookup() -> None:
    response = client.get("/api/v1/lookups/rice-varieties")
    assert response.status_code == 200
    body = response.json()
    assert body["data"]
    assert any(item["id"] == "ciherang" for item in body["data"])


def test_simulation_evaluate() -> None:
    response = client.post(
        "/api/v1/simulations/evaluate",
        json={
            "duck_count": 40,
            "land_area": 10,
            "land_area_unit": "are",
            "rice_variety": "ciherang",
            "planting_system": "legowo",
            "planting_date": "2026-06-01",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["reactive_result"]["duck_density_per_hectare"] == 400.0
    assert body["comparison"]["display_mode"] == "side_by_side"

