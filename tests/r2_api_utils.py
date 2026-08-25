"""Shared helpers for Phase-3 R2 API tests."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.main import app

API = "/api/v1"

DEFAULT_SIMULATION_PAYLOAD: dict = {
    "land_area_are": 7,
    "duck_count": 28,
    "planting_date": "2026-06-01",
    "planting_system": "jajar_legowo",
    "rice_variety": "sertani",
    "duck_age_days": 30,
    # p_duck_buy omitted on purpose (registry default applies).
}


def make_client() -> TestClient:
    return TestClient(app)


def register_and_login(
    client: TestClient,
    *,
    email: str | None = None,
    password: str = "password123",
    name: str = "R2 Tester",
) -> dict[str, str]:
    """Create a fresh user and return Authorization headers."""
    email = email or f"{uuid.uuid4().hex[:10]}@example.com"
    response = client.post(
        f"{API}/auth/register",
        json={"name": name, "email": email, "password": password},
    )
    assert response.status_code == 201, response.text
    return login_headers(client, email=email, password=password)


def login_headers(
    client: TestClient,
    *,
    email: str,
    password: str = "password123",
) -> dict[str, str]:
    """Login an existing user and return Authorization headers."""
    response = client.post(
        f"{API}/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def register_user(
    client: TestClient,
    *,
    email: str,
    password: str = "password123",
    name: str = "R2 Tester",
) -> str:
    """Register a user; returns the new user id."""
    response = client.post(
        f"{API}/auth/register",
        json={"name": name, "email": email, "password": password},
    )
    assert response.status_code == 201, response.text
    return response.json()["user"]["id"]
