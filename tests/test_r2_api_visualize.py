"""Phase 4: R2 visualization is a truthful, side-effect-free simulation view."""

import pytest

from app.core.database import get_connection
from tests.r2_api_utils import (
    API,
    DEFAULT_SIMULATION_PAYLOAD,
    make_client,
    register_and_login,
)


def _visualize(client, overrides: dict | None = None, headers=None):
    payload = dict(DEFAULT_SIMULATION_PAYLOAD)
    payload.update(overrides or {})
    return client.post(f"{API}/dss/visualize", json=payload, headers=headers or {})


def test_visualization_contract_is_canonical_and_availability_aware() -> None:
    client = make_client()
    response = _visualize(client)
    assert response.status_code == 200, response.text
    body = response.json()

    assert set(body) == {
        "model",
        "selected_input",
        "density_zones",
        "age_zones",
        "calendar",
        "infrastructure",
        "fertilizer",
        "yield_series",
        "financial_waterfall",
        "warnings",
    }
    assert body["selected_input"]["density_are"] == 4.0
    assert sum(zone["selected_value_in_zone"] for zone in body["density_zones"]) == 1
    assert sum(zone["selected_value_in_zone"] for zone in body["age_zones"]) == 1
    assert next(z for z in body["density_zones"] if z["selected_value_in_zone"])["status"] == "SUPPORTED"
    assert next(z for z in body["age_zones"] if z["selected_value_in_zone"])["status"] == "SUPPORTED"

    simulation = client.post(f"{API}/dss/simulate", json=DEFAULT_SIMULATION_PAYLOAD).json()
    assert body["calendar"] == simulation["calendar"]
    assert body["warnings"] == simulation["warnings"]

    infra = body["infrastructure"]
    assert infra["series_semantics"] == "CALCULATED_REQUEST_RANGE"
    assert infra["cost_min_rp_per_cycle"] < infra["cost_ref_rp_per_cycle"] < infra["cost_max_rp_per_cycle"]

    fertilizer = body["fertilizer"]
    assert fertilizer["baseline_label"] == "BASELINE-NO-CREDIT"
    assert fertilizer["manure_credit_applied"] is False
    assert [item["key"] for item in fertilizer["components"]] == ["NPK_PHONSKA", "UREA"]

    assert body["yield_series"]["availability"] == "UNAVAILABLE"
    assert body["yield_series"]["points"] == []
    assert set(body["yield_series"]["reason_codes"]) == {
        "Y_BASE_LOOKUP_MISSING",
        "F_RD_LOOKUP_MISSING",
    }

    nodes = {node["key"]: node for node in body["financial_waterfall"]["nodes"]}
    assert nodes["terminal_duck_value_ref"]["kind"] == "ASSET_VALUE"
    assert nodes["terminal_duck_value_ref"]["affects_cash_total"] is False
    assert nodes["feed_cost"]["availability"] == "UNAVAILABLE"
    assert nodes["feed_cost"]["amount_rp"] is None
    assert nodes["cage_total_cost"]["amount_rp"] is None
    assert nodes["available_cost_subtotal"]["amount_rp"] > 0
    assert nodes["full_profit"]["availability"] == "UNAVAILABLE"
    assert nodes["full_profit"]["amount_rp"] is None

    serialized = response.text.lower()
    for prohibited in ("survival_curve", "yield_benchmark", "optimizer", "recommended_scenario"):
        assert prohibited not in serialized


@pytest.mark.parametrize(
    ("duck_count", "expected_status"),
    [(10, "EXTRAPOLATION"), (20, "SUPPORTED"), (40, "EXTRAPOLATION"),
     (50, "LIMITED_TEST"), (70, "EXTRAPOLATION"), (80, "HIGH_RISK")],
)
def test_tegel_density_partition_selects_exactly_one_zone(
    duck_count: int,
    expected_status: str,
) -> None:
    response = _visualize(
        make_client(),
        {"land_area_are": 10, "duck_count": duck_count, "planting_system": "tegel"},
    )
    assert response.status_code == 200, response.text
    selected = [z for z in response.json()["density_zones"] if z["selected_value_in_zone"]]
    assert len(selected) == 1
    assert selected[0]["status"] == expected_status


def test_visualization_never_persists_history_even_with_bearer_token() -> None:
    client = make_client()
    headers = register_and_login(client)
    with get_connection() as connection:
        before_r2 = connection.execute("SELECT COUNT(*) FROM dss_simulation_histories_r2").fetchone()[0]
        before_legacy = connection.execute("SELECT COUNT(*) FROM dss_simulation_histories").fetchone()[0]

    response = _visualize(client, headers=headers)
    assert response.status_code == 200, response.text

    with get_connection() as connection:
        after_r2 = connection.execute("SELECT COUNT(*) FROM dss_simulation_histories_r2").fetchone()[0]
        after_legacy = connection.execute("SELECT COUNT(*) FROM dss_simulation_histories").fetchone()[0]
    assert (after_r2, after_legacy) == (before_r2, before_legacy)


def test_visualization_validation_reference_and_openapi_contract() -> None:
    client = make_client()
    invalid = _visualize(client, {"duck_count": 0})
    assert invalid.status_code == 400
    assert invalid.json()["error"]["code"] == "validation_error"

    unknown = _visualize(client, {"planting_system": "unknown"})
    assert unknown.status_code == 422
    assert unknown.json()["error"]["code"] == "invalid_reference"

    operation = client.get("/openapi.json").json()["paths"][f"{API}/dss/visualize"]["post"]
    assert operation["responses"]["200"]
    assert operation["responses"]["400"]
    assert operation["responses"]["422"]

