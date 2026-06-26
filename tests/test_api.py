from fastapi.testclient import TestClient

from app.core.database import get_connection
from app.main import app

client = TestClient(app)

SIMULATION_PAYLOAD = {
    "duck_count": 28,
    "land_area_are": 7,
    "planting_date": "2026-06-01",
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "duck_age_days": 30,
}


def register_and_login(
    *,
    name: str = "Faris",
    email: str = "faris@example.com",
    password: str = "password123",
) -> tuple[dict, dict[str, str]]:
    register_response = client.post(
        "/api/v1/auth/register",
        json={"name": name, "email": email, "password": password},
    )
    assert register_response.status_code == 201
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    login_body = login_response.json()
    return login_body["user"], {
        "Authorization": f"Bearer {login_body['access_token']}"
    }


def test_openapi_exposes_only_requested_endpoints() -> None:
    assert set(app.openapi()["paths"]) == {
        "/health",
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/auth/me",
        "/api/v1/dss/options",
        "/api/v1/dss/simulate",
        "/api/v1/dss/histories",
        "/api/v1/dss/histories/{history_id}",
    }


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "rice-duck-dss-backend"}


def test_cors_allows_any_origin() -> None:
    response = client.get(
        "/api/v1/dss/options",
        headers={"Origin": "http://frontend.example"},
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "*"


def test_cors_preflight_allows_authorization_header() -> None:
    response = client.options(
        "/api/v1/dss/simulate",
        headers={
            "Origin": "http://frontend.example",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "*"
    assert "authorization" in response.headers["access-control-allow-headers"].lower()
    assert "content-type" in response.headers["access-control-allow-headers"].lower()


def test_dss_options_are_public() -> None:
    response = client.get("/api/v1/dss/options")
    assert response.status_code == 200
    body = response.json()
    assert any(item["code"] == "sertani" for item in body["rice_varieties"])
    assert any(item["code"] == "jajar_legowo" for item in body["planting_systems"])
    tegel = next(
        item for item in body["planting_systems"] if item["code"] == "tegel"
    )
    assert tegel["k_max_are"] == 2.5
    assert tegel["k_max_range_are"] == {"min": 2, "max": 3}


def test_register_user() -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Faris",
            "email": "faris@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 201
    assert response.json()["message"] == "User registered successfully"
    assert response.json()["user"]["email"] == "faris@example.com"
    with get_connection() as connection:
        row = connection.execute(
            "SELECT password_hash FROM users WHERE email = ?",
            ("faris@example.com",),
        ).fetchone()
    assert row is not None
    assert row["password_hash"] != "password123"
    assert row["password_hash"].startswith("pbkdf2_sha256$")


def test_duplicate_email_is_rejected() -> None:
    register_and_login()
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Another Faris",
            "email": "FARIS@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 409
    assert response.json()["error"]["field"] == "email"


def test_login_and_get_current_user() -> None:
    user, headers = register_and_login()
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json() == user
    assert response.json()["email"] == "faris@example.com"


def test_invalid_login_is_rejected() -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Faris",
            "email": "faris@example.com",
            "password": "password123",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "faris@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


def test_protected_endpoints_require_access_token() -> None:
    assert client.get("/api/v1/auth/me").status_code == 401
    assert client.get("/api/v1/dss/histories").status_code == 401


def test_public_simulation_does_not_save_history() -> None:
    response = client.post("/api/v1/dss/simulate", json=SIMULATION_PAYLOAD)
    assert response.status_code == 200
    assert response.json()["history_id"] is None
    assert response.json()["actual_scenario"]["density_are"] == 4.0
    body = response.json()
    assert body["economics"]["status"] == "partial"
    assert body["economics"]["actual"]["net_profit_rp"] is None
    # Kappa values are now available (0.049, 0.072, 0.032) so status is estimation_only
    assert body["ecology"]["actual"]["soil_nutrients"]["status"] == "estimation_only"
    assert body["ecology"]["actual"]["pesticide_herbicide_saving_status"] == "literature-uncalibrated"
    assert body["ecology"]["actual"]["pesticide_herbicide_saving_rp"] is not None
    assert body["environment"]["status"] == "literature-uncalibrated"
    assert body["environment"]["actual"]["co2e_kg_per_ha_season"] is None
    assert body["data_readiness"] == {
        "agronomy_ready": "ready",
        "yield_ready": "estimation_only",
        "economics_ready": "partial",
        "ecology_ready": "estimation_only",
        "environment_ready": "literature-uncalibrated",
        "overall_status": "partial",
    }
    assert body["lookup"]["parameters"]["survival_lambda"]["source"] == "data_collection"
    assert body["lookup"]["parameters"]["survival_lambda"]["status"] == "local-estimate"
    assert body["validation"]["input_valid"] is True
    assert any(
        "14-21" in warning for warning in body["validation"]["warnings"]
    )
    
    dung_calc = body["trace"]["dung_calculation"]
    assert dung_calc["dung_total_kg_per_ha"] == 686.08

    trace = body["trace"]["recommendation_grid_search"]
    recommended = body["recommended_scenario"]
    assert trace["candidate_basis"] == "integer_duck_count"
    assert recommended is None
    assert body["optimality_assessment"]["is_optimal"] is True

    assert trace["best_duration_days"] <= 80
    assert 28 + trace["best_duration_days"] <= 60
    assert trace["objective_components_used"] == [
        "normalized_yield",
        "risk_penalty",
    ]


def test_public_simulation_rejects_invalid_optional_token() -> None:
    response = client.post(
        "/api/v1/dss/simulate",
        json=SIMULATION_PAYLOAD,
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


def test_simulation_is_saved_as_user_history() -> None:
    _, headers = register_and_login()
    response = client.post(
        "/api/v1/dss/simulate",
        json=SIMULATION_PAYLOAD,
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["history_id"]
    assert body["actual_scenario"]["density_are"] == 4.0
    assert body["actual_scenario"]["duration_days"] == 32
    assert body["actual_scenario"]["surviving_ducks"] == 18.76
    assert body["actual_scenario"]["predicted_yield"]["kg_per_ha"] == 6116.3981
    assert body["actual_scenario"]["predicted_yield"]["estimated_total_kg"] == 428.1479
    assert body["actual_scenario"]["risk_status"] == "SAFE"
    assert body["trace"]["yield_model"]["density_basis"] == "d_ha"

    list_response = client.get("/api/v1/dss/histories", headers=headers)
    assert list_response.status_code == 200
    histories = list_response.json()["data"]
    assert len(histories) == 1
    assert histories[0]["id"] == body["history_id"]
    assert "trace" not in histories[0]
    assert histories[0]["summary"]["rice_variety"] == "Sertani / Seratih"



def test_history_detail_and_delete() -> None:
    _, headers = register_and_login()
    simulate_response = client.post(
        "/api/v1/dss/simulate",
        json=SIMULATION_PAYLOAD,
        headers=headers,
    )
    history_id = simulate_response.json()["history_id"]

    detail_response = client.get(
        f"/api/v1/dss/histories/{history_id}",
        headers=headers,
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["history_id"] == history_id
    assert detail_response.json()["trace"]["yield_model"]["x_final"] == 6116.3981
    assert detail_response.json()["economics"]["actual"]["net_profit_rp"] is None
    # Kappa values are now available, so nutrients are calculated (not None)
    assert detail_response.json()["ecology"]["actual"]["soil_nutrients"]["n_kg_per_ha"] is not None
    assert detail_response.json()["environment"]["status"] == "literature-uncalibrated"

    delete_response = client.delete(
        f"/api/v1/dss/histories/{history_id}",
        headers=headers,
    )
    assert delete_response.status_code == 200
    assert client.get(
        f"/api/v1/dss/histories/{history_id}",
        headers=headers,
    ).status_code == 404


def test_user_cannot_access_another_users_history() -> None:
    _, first_headers = register_and_login(
        name="First User",
        email="first@example.com",
    )
    simulate_response = client.post(
        "/api/v1/dss/simulate",
        json=SIMULATION_PAYLOAD,
        headers=first_headers,
    )
    history_id = simulate_response.json()["history_id"]

    _, second_headers = register_and_login(
        name="Second User",
        email="second@example.com",
    )
    assert client.get(
        f"/api/v1/dss/histories/{history_id}",
        headers=second_headers,
    ).status_code == 404
    assert client.delete(
        f"/api/v1/dss/histories/{history_id}",
        headers=second_headers,
    ).status_code == 404
    assert client.get("/api/v1/dss/histories", headers=second_headers).json() == {
        "data": []
    }


def test_simulation_invalid_lookup_returns_structured_error() -> None:
    _, headers = register_and_login()
    payload = dict(SIMULATION_PAYLOAD)
    payload["rice_variety"] = "unknown"
    response = client.post(
        "/api/v1/dss/simulate",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 422
    assert response.json()["error"]["field"] == "rice_variety"


def test_simulation_invalid_planting_system_returns_structured_error() -> None:
    _, headers = register_and_login()
    payload = dict(SIMULATION_PAYLOAD)
    payload["planting_system"] = "unknown"
    response = client.post(
        "/api/v1/dss/simulate",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 422
    assert response.json()["error"]["field"] == "planting_system"


def test_simulation_validation_error() -> None:
    _, headers = register_and_login()
    payload = dict(SIMULATION_PAYLOAD)
    payload["land_area_are"] = 0
    response = client.post(
        "/api/v1/dss/simulate",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 422
    assert any(
        issue["field"] == "land_area_are"
        for issue in response.json()["error"]["issues"]
    )
