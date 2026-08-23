"""HTTP contract tests for the final DSS SoT."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def payload(**overrides: object) -> dict:
    value = {
        "land_area_are": 10,
        "duck_count": 20,
        "rice_variety": "sertani",
        "planting_system": "jajar_legowo",
        "duck_age_days": 21,
        "planting_date": "2026-01-01",
        "p_duck_buy": 15000,
    }
    value.update(overrides)
    return value


def test_simulate_returns_canonical_sot_output(client: TestClient) -> None:
    response = client.post("/api/v1/dss/simulate", json=payload())
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["age_flag"] == "RECOMMENDED"
    assert body["density_are"] == 2.0
    assert body["density_ha"] == 200.0
    assert body["density_status"] == "RECOMMENDED"
    assert body["HST_in"] == 21 and body["HST_out"] == 65 and body["t_active"] == 44
    assert body["D_in"] == "2026-01-22" and body["D_out"] == "2026-03-07"
    assert body["harvest_hst_min"] == 100 and body["harvest_hst_max"] == 110
    assert body["D_panen_min"] == "2026-04-11" and body["D_panen_max"] == "2026-04-21"
    assert body["N_survive"] == 20
    assert body["Yield_are_pred"] == pytest.approx(47.8767507)
    assert body["Yield_total_pred"] == pytest.approx(478.7675)
    assert body["Revenue_gabah"] == pytest.approx(2872605.04)
    assert body["Revenue_duck_potential"] == 1050000.0
    assert body["Cost_duck_buy"] == 300000.0 and body["Cost_feed"] == 400000.0
    assert body["Core_Cash_Cost"] == 700000.0
    assert body["Total_Revenue_DSS"] == pytest.approx(3922605.04)
    assert body["Net_Cash_Contribution_DSS"] == pytest.approx(3222605.04)
    assert set(body["sandbox"]["infrastructure"]) == {"note"}


@pytest.mark.parametrize(("duck_age_days", "expected"), [(20, "TOO_YOUNG"), (30, "RECOMMENDED"), (31, "ABOVE_RECOMMENDED_AGE")])
def test_age_boundaries(client: TestClient, duck_age_days: int, expected: str) -> None:
    body = client.post("/api/v1/dss/simulate", json=payload(duck_age_days=duck_age_days)).json()
    assert body["age_flag"] == expected
    assert body["Yield_are_pred"] == pytest.approx(47.8767507)
    assert body["N_survive"] == 20


@pytest.mark.parametrize(
    ("planting_system", "duck_count", "expected_status", "expected_survivors"),
    [
        ("jajar_legowo", 10, "UNDER_DENSITY", 10), ("jajar_legowo", 20, "RECOMMENDED", 20),
        ("jajar_legowo", 40, "RECOMMENDED", 40), ("jajar_legowo", 50, "ABOVE_RECOMMENDED", 50),
        ("jajar_legowo", 81, "OVERLOAD_HIGH_RISK", 48), ("tegel", 20, "RECOMMENDED", 20),
        ("tegel", 30, "RECOMMENDED", 30), ("tegel", 40, "ABOVE_RECOMMENDED", 40),
    ],
)
def test_density_and_survival_boundaries(client: TestClient, planting_system: str, duck_count: int, expected_status: str, expected_survivors: int) -> None:
    body = client.post("/api/v1/dss/simulate", json=payload(planting_system=planting_system, duck_count=duck_count)).json()
    assert body["density_status"] == expected_status
    assert body["N_survive"] == expected_survivors
    assert body["Yield_are_pred"] == pytest.approx(47.8767507)


def test_purchase_price_zero_and_passthrough(client: TestClient) -> None:
    zero = client.post("/api/v1/dss/simulate", json=payload(p_duck_buy=0)).json()
    paid = client.post("/api/v1/dss/simulate", json=payload(p_duck_buy=30000)).json()
    assert zero["Cost_duck_buy"] == 0
    assert paid["Cost_duck_buy"] == 600000


def test_inpari_uses_local_empirical_harvest_window(client: TestClient) -> None:
    body = client.post("/api/v1/dss/simulate", json=payload(rice_variety="inpari")).json()
    assert (body["harvest_hst_min"], body["harvest_hst_max"]) == (109, 116)
    assert (body["D_panen_min"], body["D_panen_max"]) == ("2026-04-20", "2026-04-27")
    assert not any("generic" in warning.lower() for warning in body["warnings"])


def test_options_expose_only_sot_domains(client: TestClient) -> None:
    body = client.get("/api/v1/dss/options").json()
    assert {item["code"] for item in body["rice_varieties"]} == {"sertani", "inpari"}
    assert {item["code"] for item in body["planting_systems"]} == {"jajar_legowo", "tegel"}
    assert all("F_sys" not in item for item in body["planting_systems"])
    assert next(item for item in body["planting_systems"] if item["code"] == "jajar_legowo")["label"] == "Jajar Legowo 2:1"
    inpari = next(item for item in body["rice_varieties"] if item["code"] == "inpari")
    assert (inpari["hst_panen_min"], inpari["hst_panen_max"]) == (109, 116)
    assert inpari["status"] == "local-empirical-reference"


@pytest.mark.parametrize("missing", ["planting_date", "duck_age_days", "p_duck_buy"])
def test_required_input_rejected(client: TestClient, missing: str) -> None:
    request = payload()
    request.pop(missing)
    response = client.post("/api/v1/dss/simulate", json=request)
    assert response.status_code == 400
    assert any(issue["field"] == missing for issue in response.json()["error"]["issues"])


@pytest.mark.parametrize("field", ["land_area_are", "duck_count"])
def test_positive_area_and_duck_count_required(client: TestClient, field: str) -> None:
    response = client.post("/api/v1/dss/simulate", json=payload(**{field: 0}))
    assert response.status_code == 400
    assert any(issue["field"] == field for issue in response.json()["error"]["issues"])


@pytest.mark.parametrize(
    ("field", "raw_value"),
    [
        ("land_area_are", "NaN"),
        ("land_area_are", "Infinity"),
        ("p_duck_buy", "NaN"),
        ("p_duck_buy", "Infinity"),
    ],
)
def test_non_finite_numeric_inputs_are_rejected(
    client: TestClient, field: str, raw_value: str
) -> None:
    """Non-finite JSON numbers must not reach Decimal-based Core engines."""
    import json

    request_body = json.dumps(payload()).replace(
        f'"{field}": {json.dumps(payload()[field])}',
        f'"{field}": {raw_value}',
        1,
    )
    response = client.post(
        "/api/v1/dss/simulate",
        content=request_body,
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 400
    assert any(issue["field"] == field for issue in response.json()["error"]["issues"])


def test_non_jarwo_2_1_category_is_rejected(client: TestClient) -> None:
    response = client.post("/api/v1/dss/simulate", json=payload(planting_system="jajar_legowo_4_1"))
    assert response.status_code == 422
    assert response.json()["error"]["field"] == "planting_system"


def test_zero_age_is_classified_by_age_engine(client: TestClient) -> None:
    response = client.post("/api/v1/dss/simulate", json=payload(duck_age_days=0))
    assert response.status_code == 200
    assert response.json()["age_flag"] == "TOO_YOUNG"


def test_small_area_has_validation_domain_warning(client: TestClient) -> None:
    body = client.post("/api/v1/dss/simulate", json=payload(land_area_are=1)).json()
    assert any("di bawah 2,5 are" in warning for warning in body["warnings"])


def test_optimizer_remains_isolated(client: TestClient) -> None:
    request = {key: value for key, value in payload().items() if key != "p_duck_buy"}
    response = client.post("/api/v1/optimizer/recommend", json=request)
    assert response.status_code == 200
    assert "scope_notice" in response.json()
