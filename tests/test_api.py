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


def test_get_active_parameter_set() -> None:
    response = client.get("/api/v1/parameters/active")
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["id"] == "active"
    assert body["data"]["optimization"]["population_size"] == 40


def test_simulation_preview_context() -> None:
    response = client.post(
        "/api/v1/simulations/preview-context",
        json={
            "duck_count": 40,
            "land_area_are": 10,
            "rice_variety": "ciherang",
            "planting_system": "legowo",
            "planting_date": "2026-06-01",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["agronomic_context"]["safe_window_days"] == 60
    assert body["preview"]["duck_density_per_are"] == 4.0
    assert body["preview"]["max_duck_capacity"] == 38
    assert body["preview"]["risk_summary"]["level"] == "bahaya"


def test_simulation_invalid_lookup_returns_structured_error() -> None:
    response = client.post(
        "/api/v1/simulations/preview-context",
        json={
            "duck_count": 40,
            "land_area_are": 10,
            "rice_variety": "unknown-variety",
            "planting_system": "legowo",
            "planting_date": "2026-06-01",
        },
    )
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "invalid_reference"
    assert body["error"]["field"] == "rice_variety"


def test_simulation_validation_error_returns_issues() -> None:
    response = client.post(
        "/api/v1/simulations/preview-context",
        json={
            "duck_count": 40,
            "land_area_are": 0,
            "rice_variety": "ciherang",
            "planting_system": "legowo",
            "planting_date": "2026-06-01",
        },
    )
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["issues"]
    assert any(issue["field"] == "land_area_are" for issue in body["error"]["issues"])


def test_simulation_evaluate() -> None:
    response = client.post(
        "/api/v1/simulations/evaluate",
        json={
            "duck_count": 40,
            "land_area_are": 10,
            "rice_variety": "ciherang",
            "planting_system": "legowo",
            "planting_date": "2026-06-01",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["simulation_id"]
    assert body["reactive_result"]["duck_density_per_are"] == 4.0
    assert body["agronomic_context"]["k_max_per_are"] == 3.75
    assert body["reactive_result"]["risk_summary"]["level"] == "bahaya"
    assert body["optimization_meta"]["algorithm"] == "Differential Evolution"
    assert body["comparison"]["display_mode"] == "side_by_side"


def test_simulation_history_and_detail() -> None:
    evaluate_response = client.post(
        "/api/v1/simulations/evaluate",
        json={
            "duck_count": 32,
            "land_area_are": 8,
            "rice_variety": "ciherang",
            "planting_system": "legowo",
            "planting_date": "2026-06-05",
        },
    )
    assert evaluate_response.status_code == 200
    simulation_id = evaluate_response.json()["simulation_id"]

    list_response = client.get("/api/v1/simulations")
    assert list_response.status_code == 200
    list_body = list_response.json()
    assert any(item["simulation_id"] == simulation_id for item in list_body["data"])

    detail_response = client.get(f"/api/v1/simulations/{simulation_id}")
    assert detail_response.status_code == 200
    detail_body = detail_response.json()
    assert detail_body["simulation_id"] == simulation_id
    assert detail_body["input_summary"]["duck_count"] == 32
    assert "optimization_meta" in detail_body


def test_simulation_summary() -> None:
    evaluate_response = client.post(
        "/api/v1/simulations/evaluate",
        json={
            "duck_count": 28,
            "land_area_are": 8,
            "rice_variety": "ciherang",
            "planting_system": "legowo",
            "planting_date": "2026-06-07",
        },
    )
    assert evaluate_response.status_code == 200
    simulation_id = evaluate_response.json()["simulation_id"]

    summary_response = client.get(f"/api/v1/simulations/{simulation_id}/summary")
    assert summary_response.status_code == 200
    body = summary_response.json()
    assert body["header"]["simulation_id"] == simulation_id
    assert body["header"]["area_are"] == 8.0
    assert body["reactive_card"]["label"] == "reactive"
    assert body["reactive_card"]["duck_total"] == 28
    assert body["proactive_card"]["label"] == "proactive"
    assert body["recommendation"]["risk_transition"]


def test_simulation_detail_not_found_returns_structured_error() -> None:
    response = client.get("/api/v1/simulations/not-found-id")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "not_found"
    assert body["error"]["field"] == "simulation_id"


def test_simulation_summary_not_found_returns_structured_error() -> None:
    response = client.get("/api/v1/simulations/not-found-id/summary")
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "not_found"
    assert body["error"]["field"] == "simulation_id"
