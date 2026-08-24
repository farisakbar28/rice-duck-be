"""Model C contract, persistence, and scientific-boundary regression tests."""

import math

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
BASE = {
    "land_area_are": 10,
    "duck_count": 20,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "duck_age_days": 21,
}
FORBIDDEN_FIELDS = {
    "N_survive", "survival_rate", "Yield_are_pred", "Yield_total_pred",
    "Revenue_duck_potential", "Cost_feed", "Core_Cash_Cost",
    "Total_Revenue_DSS", "Net_Cash_Contribution_DSS", "HST_out",
    "t_active", "yield_status",
}


def post(**changes):
    return client.post("/api/v1/dss/simulate", json=BASE | changes)


def test_c0_golden_default_economics_and_fallback_provenance():
    response = post()
    assert response.status_code == 200
    body = response.json()
    assert body["model_variant"] == "C_FARMER_GROUPED_LOCAL"
    assert body["model_validation_status"] == "LOCAL_CALIBRATED_WITH_LIMITED_HOLDOUT_PERFORMANCE"
    assert body["yield_are_kg"] == 50
    assert body["yield_total_kg"] == 500
    assert body["revenue_gabah"] == 3_000_000
    assert body["revenue_duck_all_sold_scenario"] == 900_000
    assert body["cost_duck_buy"] == 500_000
    assert body["cash_contribution_before_optional"] == 3_400_000
    assert body["cost_feed_scenario"] is None
    assert body["cost_infra_cycle"] is None
    assert body["cash_contribution_after_optional"] is None
    prices = body["provenance"]["prices"]
    assert prices["p_gabah"]["status"] == "local-calibrated"
    assert prices["p_duck_buy"]["status"] == "local-calibrated"
    assert prices["p_duck_sell"]["status"] == "local-estimate"


@pytest.mark.parametrize(
    ("duck_count", "expected"),
    [(19, "UNDER"), (20, "RECOMMENDED"), (40, "RECOMMENDED"),
     (41, "WARNING_ABOVE_RECOMMENDED"), (80, "WARNING_ABOVE_RECOMMENDED"),
     (81, "HIGH_RISK")],
)
def test_jarwo_density_boundaries(duck_count, expected):
    body = post(duck_count=duck_count).json()
    assert body["density_status"] == expected
    assert body["yield_are_kg"] == 50


@pytest.mark.parametrize(
    ("duck_count", "expected"),
    [(20, "RECOMMENDED"), (30, "RECOMMENDED"), (31, "WARNING_ABOVE_RECOMMENDED")],
)
def test_tegel_density_boundaries(duck_count, expected):
    body = post(duck_count=duck_count, planting_system="tegel").json()
    assert body["density_status"] == expected
    assert body["yield_are_kg"] == 50


@pytest.mark.parametrize(
    ("age", "expected"),
    [(20, "NOT_RECOMMENDED"), (21, "LOCAL_READY"),
     (30, "LOCAL_READY"), (31, "OLDER_CONSERVATIVE")],
)
def test_age_boundaries(age, expected):
    assert post(duck_age_days=age).json()["age_status"] == expected


def test_production_yield_is_invariant_to_all_non_area_inputs():
    variants = [
        {"duck_count": 0}, {"duck_count": 81},
        {"planting_system": "tegel", "rice_variety": "inpari"},
        {"duck_age_days": 20}, {"duck_age_days": 31},
    ]
    for change in variants:
        body = post(**change).json()
        assert body["yield_are_kg"] == 50
        assert body["yield_total_kg"] == 500


def test_high_risk_only_marks_risk_and_disables_all_sold_scenario():
    body = post(duck_count=81).json()
    assert body["survival_risk"] == "HIGH"
    assert body["revenue_duck_all_sold_scenario"] is None
    assert body["cash_contribution_before_optional"] is None
    assert body["cash_contribution_after_optional"] is None
    assert body["yield_are_kg"] == 50


def test_zero_ducks_is_accepted_without_fabricated_survival():
    body = post(duck_count=0).json()
    assert body["density_are"] == 0
    assert body["density_status"] == "UNDER"
    assert body["survival_risk"] is None
    assert body["revenue_duck_all_sold_scenario"] == 0
    assert body["cost_duck_buy"] == 0
    assert body["yield_are_kg"] == 50


def test_optional_costs_are_explicit_and_amortized_only_when_selected():
    body = post(
        c_feed_scenario=100,
        c_jaring_purchase=1_000,
        n_jaring_cycles=10,
        c_kandang_purchase=500,
        n_kandang_cycles=5,
    ).json()
    assert body["cost_feed_scenario"] == 100
    assert body["cost_infra_cycle"] == 200
    assert body["cash_contribution_after_optional"] == 3_399_700
    assert post(c_jaring_purchase=1).status_code == 400
    assert post(c_kandang_purchase=1).status_code == 400
    assert post(c_jaring_purchase=1, n_jaring_cycles=0).status_code == 400
    assert post(c_kandang_purchase=1, n_kandang_cycles=0).status_code == 400


def test_calendar_range_with_and_without_anchor():
    unanchored = post().json()
    assert [unanchored[key] for key in (
        "release_hst_min", "release_hst_max", "withdraw_hst_min", "withdraw_hst_max"
    )] == [21, 30, 56, 60]
    assert all(unanchored[key] is None for key in (
        "release_date_min", "release_date_max", "withdraw_date_min", "withdraw_date_max"
    ))
    anchored = post(planting_date="2026-01-01").json()
    assert [anchored[key] for key in (
        "release_date_min", "release_date_max", "withdraw_date_min", "withdraw_date_max"
    )] == ["2026-01-22", "2026-01-31", "2026-02-26", "2026-03-02"]


def test_pre_specified_holdout_replay_uses_frozen_c0_and_documented_metrics():
    # H01-H11 are fixed pre-specified holdout rows. The holdout is now opened,
    # so these numbers must never become a source for runtime fitting.
    holdout = [
        ("H01", 8, 3.60, 13, "sertani", "jajar_legowo", 45.83, 6_000, 25_000, None),
        ("H02", 9, 5.10, 5, "sertani", "jajar_legowo", 48.04, 6_000, 25_000, None),
        ("H03", 11, 10.00, 65, "sertani", "jajar_legowo", 60.50, 6_000, 7_539, None),
        ("H04", 14, 7.26, 9, "sertani", "jajar_legowo", 59.37, 7_500, 22_222.22222, None),
        ("H05", 23, 5.10, 10, "inpari", "jajar_legowo", 21.02, 7_500, 5_000, None),
        ("H06", 25, 14.41, 30, "sertani", "jajar_legowo", 52.43, 7_500, 10_000, None),
        ("H07", 38, 10.00, 32, "sertani", "jajar_legowo", 53.40, 6_300, 0, "2024-04-22"),
        ("H08", 43, 3.60, 15, "sertani", "jajar_legowo", 40.42, 6_000, 0, "2024-10-01"),
        ("H09", 44, 10.00, 29, "inpari", "tegel", 38.65, 6_000, 0, "2024-09-28"),
        ("H10", 47, 3.00, 6, "sertani", "jajar_legowo", 13.50, 6_000, 25_000, None),
        ("H11", 62, 3.77, 8, "sertani", "jajar_legowo", 36.47, 6_000, 25_000, None),
    ]
    errors = []
    for _, _, area, ducks, variety, system, actual, rice_price, duck_buy_price, planting_date in holdout:
        payload = {
            "land_area_are": area,
            "duck_count": ducks,
            "rice_variety": variety,
            "planting_system": system,
            "p_gabah": rice_price,
            "p_duck_buy": duck_buy_price,
            "p_duck_sell": 45_000,
        }
        if planting_date is not None:
            payload["planting_date"] = planting_date
        response = post(
            **payload,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["yield_are_kg"] == 50
        assert body["yield_total_kg"] == pytest.approx(50 * area)
        assert body["density_are"] == pytest.approx(ducks / area)
        assert body["revenue_gabah"] == pytest.approx(50 * area * rice_price)
        assert body["cost_duck_buy"] == pytest.approx(ducks * duck_buy_price, abs=0.01)
        assert body["provenance"]["prices"]["p_duck_buy"]["source"] == "runtime"
        assert body["provenance"]["prices"]["p_duck_buy"]["status"] == "runtime"
        if planting_date is None:
            assert all(body[key] is None for key in (
                "release_date_min", "release_date_max", "withdraw_date_min", "withdraw_date_max"
            ))
        else:
            assert body["release_date_min"] is not None
            assert body["withdraw_date_max"] is not None
        errors.append(body["yield_are_kg"] - actual)
    absolute_errors = sorted(abs(error) for error in errors)
    assert sum(abs(error) for error in errors) / len(errors) == pytest.approx(11.979, abs=0.001)
    assert (sum(error * error for error in errors) / len(errors)) ** 0.5 == pytest.approx(15.990, abs=0.001)
    # Public scenario rows show yield with two decimal places, while the SoT's
    # frozen MedAE uses the higher-precision source values.
    assert absolute_errors[len(absolute_errors) // 2] == pytest.approx(9.583, abs=0.005)
    assert sum(errors) / len(errors) == pytest.approx(7.307, abs=0.001)


def test_zero_runtime_duck_purchase_price_is_not_a_fallback():
    body = post(p_duck_buy=0).json()
    assert body["cost_duck_buy"] == 0
    assert body["provenance"]["prices"]["p_duck_buy"] == {
        "value": 0.0,
        "source": "runtime",
        "status": "runtime",
    }


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("land_area_are", "10"), ("land_area_are", True),
        ("p_gabah", "6000"), ("p_duck_buy", "25000"),
        ("p_duck_sell", "45000"), ("c_feed_scenario", "10"),
        ("c_jaring_purchase", "10"), ("n_jaring_cycles", "2"),
        ("c_kandang_purchase", "10"), ("n_kandang_cycles", "2"),
        ("duck_count", "20"), ("duck_count", 20.0),
        ("duck_age_days", "21"), ("duck_age_days", 21.0),
    ],
)
def test_strict_json_number_wire_contract(field, value):
    assert post(**{field: value}).status_code == 400


def test_nonfinite_json_numbers_are_rejected():
    from app.schemas.dss import DSSSimulationRequest
    from pydantic import ValidationError

    for field, value in [("land_area_are", math.nan), ("land_area_are", math.inf),
                         ("p_gabah", math.nan), ("p_gabah", math.inf)]:
        with pytest.raises(ValidationError):
            DSSSimulationRequest.model_validate(BASE | {field: value})
    for token in ("NaN", "Infinity"):
        response = client.post(
            "/api/v1/dss/simulate",
            content=(
                '{"land_area_are":' + token
                + ',"duck_count":20,"rice_variety":"sertani",'
                '"planting_system":"jajar_legowo","duck_age_days":21}'
            ).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 400


@pytest.mark.parametrize(
    ("field", "value"),
    [("rice_variety", "SERTANI"), ("rice_variety", " sertani "),
     ("planting_system", "JAJAR_LEGOWO"), ("planting_system", " tegel ")],
)
def test_reference_codes_are_exact_and_never_normalized(field, value):
    assert post(**{field: value}).status_code == 422


def test_runtime_prices_override_fallbacks_and_metadata_is_frozen():
    body = post(p_gabah=7_000, p_duck_buy=26_000, p_duck_sell=46_000).json()
    assert body["revenue_gabah"] == 3_500_000
    assert body["cost_duck_buy"] == 520_000
    assert body["revenue_duck_all_sold_scenario"] == 920_000
    assert all(item["status"] == "runtime" for item in body["provenance"]["prices"].values())
    assert body["parameter_uncertainty_y0_95pct"] == [42.81, 55.78]
    assert body["provenance"]["validation"] == {
        "untouched_holdout_cycles": 11,
        "untouched_holdout_farmers": 6,
        "MAE": 11.979,
        "RMSE": 15.990,
        "MedAE": 9.583,
        "Bias": 7.307,
        "limitation": "limited holdout performance",
    }


def test_current_response_has_no_candidate_xiong_or_legacy_semantics():
    response = post()
    body = response.json()
    assert not FORBIDDEN_FIELDS.intersection(body)
    serialized = response.text.lower()
    for forbidden in ("xiong", "alpha", "f_tegel", "f_inpari", "c1", "c3", "c4"):
        assert forbidden not in serialized
    assert post(literature_duration_days=50).status_code == 400


def test_visualization_is_model_c_gates_not_numerical_survival():
    response = client.post("/api/v1/dss/visualize", json=BASE)
    assert response.status_code == 200
    body = response.json()
    assert body["reference_benchmarks"]["yield_baseline_kg_per_are"] == 50
    assert "survival_rate" not in response.text
    assert body["financial_waterfall"][1]["amount"] == 900_000
    risky = client.post("/api/v1/dss/visualize", json=BASE | {"duck_count": 81}).json()
    assert risky["financial_waterfall"][1]["amount"] is None


def test_openapi_documents_complete_model_c_contract():
    schema = app.openapi()["components"]["schemas"]
    request = schema["DSSSimulationRequest"]
    assert request["required"] == [
        "land_area_are", "duck_count", "rice_variety", "planting_system", "duck_age_days"
    ]
    for field in (
        "planting_date", "p_gabah", "p_duck_buy", "p_duck_sell", "c_feed_scenario",
        "c_jaring_purchase", "n_jaring_cycles", "c_kandang_purchase", "n_kandang_cycles",
    ):
        assert request["properties"][field]["description"]
    assert "literature_duration_days" not in request["properties"]
    assert request["properties"]["rice_variety"]["enum"] == ["sertani", "inpari"]
    assert request["properties"]["planting_system"]["enum"] == ["jajar_legowo", "tegel"]
    response = schema["DSSSimulationResponse"]
    assert response["example"]["model_variant"] == "C_FARMER_GROUPED_LOCAL"
    assert set(FORBIDDEN_FIELDS).isdisjoint(response["properties"])
    assert all(field.get("description") for field in response["properties"].values())
    assert not any(path.startswith("/api/v1/optimizer") for path in app.openapi()["paths"])
    assert client.post("/api/v1/optimizer/recommend", json={}).status_code == 404


def test_runtime_validator_covers_live_legacy_history_and_postman_has_assertions():
    from pathlib import Path
    import json

    runtime_source = Path("scripts/validate_model_c_runtime.py").read_text(encoding="utf-8")
    assert "verify_legacy_history_over_http" in runtime_source
    assert "legacy-runtime-v{version}" in runtime_source
    assert "cal_unanchored" in runtime_source
    assert "release_date_max" in runtime_source
    assert "withdraw_date_min" in runtime_source
    collection = json.loads(Path("postman/Rice_Duck_DSS.postman_collection.json").read_text(encoding="utf-8"))
    environment = json.loads(Path("postman/Rice_Duck_DSS.postman_environment.json").read_text(encoding="utf-8"))
    requests = [
        item
        for folder in collection["item"]
        for item in folder.get("item", [])
        if "request" in item
    ]
    names = {item["name"] for item in requests}
    assert {
        "S-C01 Jarwo d=2 recommended",
        "S-C02 Jarwo d=4 recommended",
        "S-C03 Jarwo d=4.1 warning",
        "S-C04 Jarwo d=8 warning",
        "S-C05 Jarwo d>8 high risk",
        "S-C06 Tegel d=3 recommended",
        "S-C07 Tegel d=3.1 warning",
        "S-C08 age 20 lower boundary",
        "S-C08 age 21 recommended boundary",
        "S-C08 age 30 recommended boundary",
        "S-C08 age 31 upper boundary",
        "S-C09 golden default prices",
        "Runtime duck-buy override",
        "Runtime duck-buy zero",
        "S-C10 optional costs omitted",
        "S-C11 zero ducks",
        "S-C12 invalid area",
        "Calendar with planting date",
        "Optional feed and infrastructure",
        "Invalid infrastructure denominator pairing",
        "Persist v4 simulation",
        "List v4 histories",
        "Detail v4 history preserves original payload",
        "Delete v4 history",
        "Deleted v4 history is 404",
    }.issubset(names)
    assert all(
        any(event["listen"] == "test" for event in item.get("event", []))
        for item in requests
    )
    scripts = "\n".join(
        "\n".join(event["script"]["exec"])
        for item in requests
        for event in item.get("event", [])
        if event["listen"] == "test"
    )
    assert "C_FARMER_GROUPED_LOCAL" in scripts
    assert "yield_are_kg" in scripts
    assert "N_survive" in scripts
    assert "density_status" in scripts
    assert "p_duck_buy.source" in scripts
    sc05 = next(item for item in requests if item["name"] == "S-C05 Jarwo d>8 high risk")
    sc05_script = "\n".join(
        "\n".join(event["script"]["exec"])
        for event in sc05["event"]
        if event["listen"] == "test"
    )
    assert "survival_risk" in sc05_script
    assert "'HIGH'" in sc05_script
    environment_keys = {item["key"] for item in environment["values"]}
    assert environment_keys == {"base_url"}
    assert not environment_keys.intersection({"email", "password", "token", "history_id", "original_simulation"})


def _auth_headers(email: str) -> tuple[dict[str, str], str]:
    password = "password123"
    assert client.post("/api/v1/auth/register", json={
        "name": "Model C", "email": email, "password": password,
    }).status_code == 201
    token = client.post("/api/v1/auth/login", json={
        "email": email, "password": password,
    }).json()["access_token"]
    user_id = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}).json()["id"]
    return {"Authorization": f"Bearer {token}"}, user_id


def test_authenticated_v4_history_round_trip():
    headers, _ = _auth_headers("model-c-history@example.com")
    original = client.post("/api/v1/dss/simulate", json=BASE, headers=headers).json()
    listing = client.get("/api/v1/dss/histories", headers=headers).json()
    assert listing["data"][0]["schema_version"] == 4
    history_id = listing["data"][0]["id"]
    assert client.get(f"/api/v1/dss/histories/{history_id}", headers=headers).json() == original
    assert client.delete(f"/api/v1/dss/histories/{history_id}", headers=headers).status_code == 200
    assert client.get(f"/api/v1/dss/histories/{history_id}", headers=headers).status_code == 404


@pytest.mark.parametrize("schema_version", [1, 2, 3])
def test_legacy_rows_are_preserved_hidden_and_not_deletable(schema_version):
    from app.core.database import get_connection

    headers, user_id = _auth_headers(f"legacy-v{schema_version}@example.com")
    history_id = f"legacy-v{schema_version}"
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO dss_simulation_histories "
            "(id,user_id,schema_version,created_at,input_json,actual_scenario_json,"
            "recommended_scenario_json,comparison_json,risk_json,trace_json,notes_json,"
            "economics_json,ecology_json,environment_json,lookup_json,validation_json,"
            "data_readiness_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (history_id, user_id, schema_version, "2026-01-01T00:00:00+00:00", "{}", "{}", "{}",
             "{}", "{}", "{}", "[]", "{}", "{}", "{}", "{}", "{}", "{}"),
        )
    assert client.get("/api/v1/dss/histories", headers=headers).json()["data"] == []
    assert client.get(f"/api/v1/dss/histories/{history_id}", headers=headers).status_code == 404
    assert client.delete(f"/api/v1/dss/histories/{history_id}", headers=headers).status_code == 404
    with get_connection() as connection:
        assert connection.execute(
            "SELECT 1 FROM dss_simulation_histories WHERE id = ?", (history_id,)
        ).fetchone() is not None
