from fastapi.testclient import TestClient

from app.main import create_app


def test_v3_history_round_trip_and_delete() -> None:
    client = TestClient(create_app())
    register = client.post("/api/v1/auth/register", json={"name": "History User", "email": "history@example.com", "password": "password123"})
    assert register.status_code == 201
    token = client.post("/api/v1/auth/login", json={"email": "history@example.com", "password": "password123"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"land_area_are": 10, "duck_count": 20, "rice_variety": "sertani", "planting_system": "jajar_legowo", "duck_age_days": 21, "planting_date": "2026-01-01", "p_duck_buy": 15000}

    simulated = client.post("/api/v1/dss/simulate", json=payload, headers=headers)
    assert simulated.status_code == 200, simulated.text
    histories = client.get("/api/v1/dss/histories", headers=headers)
    assert histories.status_code == 200
    history_id = histories.json()["data"][0]["id"]

    detail = client.get(f"/api/v1/dss/histories/{history_id}", headers=headers)
    assert detail.status_code == 200, detail.text
    assert detail.json() == simulated.json()

    assert client.delete(f"/api/v1/dss/histories/{history_id}", headers=headers).status_code == 200
    assert client.get(f"/api/v1/dss/histories/{history_id}", headers=headers).status_code == 404
