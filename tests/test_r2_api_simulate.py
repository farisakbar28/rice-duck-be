"""Phase 3: POST /api/v1/dss/simulate -- R2 orchestration semantics over HTTP.

Contract oracle: docs/03_R2_API_CONTRACT.md (structural semantics; numeric
spot checks derive from SSOT arithmetic only -- density 28/7=4,
floor(28*0.90)=25, terminal 25*45_000, fertilizer baseline solver).
"""

import json
import math

from tests.r2_api_utils import (
    API,
    DEFAULT_SIMULATION_PAYLOAD,
    make_client,
    register_and_login,
)


def _simulate(client, payload_overrides: dict | None = None):
    payload = dict(DEFAULT_SIMULATION_PAYLOAD)
    payload.update(payload_overrides or {})
    return client.post(f"{API}/dss/simulate", json=payload)


def _simulate_as(client, headers, payload_overrides: dict | None = None):
    payload = dict(DEFAULT_SIMULATION_PAYLOAD)
    payload.update(payload_overrides or {})
    return client.post(f"{API}/dss/simulate", json=payload, headers=headers)


# ---------------------------------------------------------------------------
# Supported in-domain case (price omitted -> registry default)
# ---------------------------------------------------------------------------


def test_supported_domain_default_price_semantics() -> None:
    client = make_client()
    response = _simulate(client)
    assert response.status_code == 200
    body = response.json()

    # Model metadata
    model = body["model"]
    assert model["model_version"] == "R2"
    assert model["history_schema_version"] == 4
    assert model["parameter_registry_version"] == "R2-2026-08-26.3"
    assert model["frozen"] is True  # sourced from app.data.seed.MODEL_FROZEN (docs/11)
    assert model["freeze_id"] == "R2-FREEZE-2026-08-26.5"
    assert model["generated_at"]

    # Input echo: omitted price resolves to registry default.
    inp = body["input"]
    assert inp["land_area_are"] == 7
    assert inp["duck_count"] == 28
    assert inp["p_duck_buy_manual"] is None
    assert inp["p_duck_buy_effective"] == 26500.0
    assert inp["p_duck_buy_source"] == "LOCAL_DEFAULT_MIDPOINT"

    # Operational profile
    op = body["operational"]
    assert op["area_m2"] == 700.0
    assert op["density_are"] == 4.0
    assert op["age_support"] == "SUPPORTED"
    assert op["density_support"] == "SUPPORTED"
    assert op["extrapolation"] == "IN_DOMAIN"

    # Calendar windows (no point-calendar legacy fields).
    cal = body["calendar"]
    assert (cal["release_hst_min"], cal["release_hst_max"]) == (21, 30)
    assert (cal["pull_hst_min"], cal["pull_hst_max"]) == (56, 60)
    assert (cal["harvest_hst_min"], cal["harvest_hst_max"]) == (100, 110)
    assert cal["active_duration_ref_days"] == 32
    assert (cal["active_duration_support_min_days"], cal["active_duration_support_max_days"]) == (28, 40)
    assert cal["release_date_min"] == "2026-06-22"
    for legacy_key in ("HST_in", "HST_out", "D_in", "D_out", "t_active"):
        assert legacy_key not in body

    # Duck outputs: gated survival + terminal asset value, never sale state.
    duck = body["duck"]
    assert duck["survival_availability"] == "AVAILABLE"
    assert duck["lambda_eff"] == 0.9
    assert duck["surviving_ducks"] == 25
    assert duck["sale_quantity"] is None
    assert duck["sale_quantity_status"] == "UNAVAILABLE"
    assert duck["terminal_value_ref_rp"] == 25 * 45000
    assert duck["terminal_value_min_rp"] == 25 * 30000
    assert duck["terminal_value_max_rp"] == 25 * 60000
    assert duck["terminal_value_is_cash_revenue"] is False

    # Phase-6 literature evidence envelope.
    yld = body["yield"]
    assert yld["availability"] == "AVAILABLE"
    assert yld["cultivar_group_code"] == "SERTANI_GROUP"
    assert yld["cultivar_group_resolved"] is True
    assert yld["baseline_kg_per_are"] == 44.5
    assert yld["rice_duck_response_factor"] == 1.028
    assert yld["yield_kg_per_are"] == yld["yield_ref_kg_per_are"] == 45.746
    assert yld["yield_total_kg"] == yld["yield_total_ref_kg"] == 320.222
    assert yld["yield_range_type"] == "LITERATURE_EVIDENCE_ENVELOPE"
    assert yld["yield_evidence_warning"] == "LOW_EVIDENCE_TWO_LOCATION_EXTERNAL_RANGE"
    assert yld["yield_baseline_source_id"] == "YB-SERTANI-SULAEMAN-2022"
    assert yld["yield_frd_source_id"] == "FRD-FENG-2024"
    assert yld["reason_codes"] == []

    # Fertilizer baseline available.
    fert = body["fertilizer_baseline"]
    assert fert["availability"] == "AVAILABLE"
    assert fert["nutrient_basis"] == "N-P2O5-K2O"
    assert fert["manure_credit_applied"] is False
    assert math.isclose(fert["n_need_kg"], 8.2327, rel_tol=1e-12)
    assert math.isclose(fert["q_npk_kg"], 19.215, rel_tol=1e-12)

    # Costs: mixed availability, no zero-filling.
    costs = body["costs"]
    assert costs["duck_purchase"]["availability"] == "AVAILABLE"
    assert costs["duck_purchase"]["amount_rp"] == 28 * 26500
    assert costs["feed"]["availability"] == "UNAVAILABLE"
    assert costs["feed"]["amount_rp"] is None
    assert set(costs["feed"]["reason_codes"]) == {
        "FEED_QUANTITY_LOOKUP_MISSING",
        "FEED_PRICE_LOOKUP_MISSING",
    }
    net = costs["net_infrastructure"]
    assert net["availability"] == "AVAILABLE_RANGE"
    assert net["geometry_assumption"] == "SQUARE_EQUIVALENT"
    assert 0 < net["cost_min_rp_per_cycle"] < net["cost_ref_rp_per_cycle"] < net["cost_max_rp_per_cycle"]
    cage = costs["cage"]
    assert cage["availability"] == "PARTIAL_RANGE_ONLY"
    assert cage["total_amount_rp"] is None
    assert cage["cost_per_unit_ref_rp_per_cycle"] == 175000
    assert "CAGE_CAPACITY_RULE_MISSING" in cage["reason_codes"]
    weed = costs["weeding"]
    assert weed["availability"] == "BASELINE_RANGE_ONLY"
    assert (weed["baseline_min_rp"], weed["baseline_max_rp"]) == (7 * 6000, 7 * 38000)
    assert weed["saving_rp"] is None
    assert costs["pesticide"]["effect"] == "CONTEXT_SPECIFIC"
    assert costs["pesticide"]["saving_rp"] is None

    # Totals come from the economics engine.
    assert costs["cost_completeness"] == "INCOMPLETE"

    # Economics: range-aware paddy revenue; terminal value remains non-cash.
    econ = body["economics"]
    assert econ["paddy_price_benchmark_rp_per_kg"] == 6500.0
    assert econ["paddy_price_semantics"] == "REGULATORY_HPP"
    assert econ["paddy_revenue_low_rp"] < econ["paddy_revenue_rp"] < econ["paddy_revenue_high_rp"]
    assert econ["cash_revenue_rp"] == econ["paddy_revenue_rp"]
    assert econ["gross_economic_value_low_rp"] < econ["gross_economic_value_rp"] < econ["gross_economic_value_high_rp"]
    assert econ["margin_core_low_rp"] < econ["margin_core_rp"] < econ["margin_core_high_rp"]
    assert econ["profit_full_est_rp"] is None
    assert econ["profit_full_status"] == "UNAVAILABLE_INCOMPLETE_COST"

    # Reliability mirrors execution flags.
    rel = body["reliability"]
    assert rel == {
        "yield_availability": "AVAILABLE",
        "survival_availability": "AVAILABLE",
        "feed_cost_availability": "UNAVAILABLE",
        "cost_completeness": "INCOMPLETE",
        "extrapolation": "IN_DOMAIN",
    }

    # Warnings communicate current unavailability states.
    warnings_text = "\n".join(body["warnings"])
    for category in (
        "FEED_COST_UNAVAILABLE",
        "CAGE_TOTAL_UNAVAILABLE",
        "FULL_PROFIT_UNAVAILABLE",
    ):
        assert category in warnings_text
    assert "60%" not in warnings_text
    assert "YIELD_EVIDENCE_WARNING" in warnings_text
    assert "prediction still calculated" not in warnings_text.lower()

    # Trace: truthful formula ids + defaulted price record + reasons.
    trace = body["trace"]
    assert "R2-NORM-01" in trace["active_formula_ids"]
    assert "R2-SURV-01" in trace["conditional_formula_ids"]
    assert "R2-CAL-01" in trace["active_formula_ids"]
    assert "R2-CAL-02" not in trace["active_formula_ids"]
    assert "R2-YLD-01" not in trace["active_formula_ids"]
    assert "R2-YLD-01" in trace["conditional_formula_ids"]
    assert "R2-LEDGER-06" not in trace["conditional_formula_ids"]
    assert trace["disabled_legacy_formula_ids"][:2] == ["LEG-RAGE", "LEG-POVER"]
    assert trace["defaulted_inputs"] == [
        {"field": "p_duck_buy", "resolved_value": 26500.0, "source": "I1", "status_tag": "mixed"}
    ]
    assert "yield" not in trace["availability_reasons"]
    assert trace["lookup_versions"]["parameter_registry"] == "R2-2026-08-26.3"
    assert trace["lookup_versions"]["yield_base_by_cultivar_group"] == "ACTIVE_RANGE"
    assert trace["lookup_versions"]["f_rd_lookup"] == "ACTIVE"
    assert trace["parameter_sources"]["yield_base_by_cultivar_group"] == ["YB-INPARI-SULAEMAN-2024", "YB-SERTANI-SULAEMAN-2022"]
    assert trace["parameter_sources"]["f_rd_lookup"] == ["FRD-FENG-2024"]


def test_response_top_level_yield_alias_and_no_flat_legacy_fields() -> None:
    client = make_client()
    raw = _simulate(client).text
    body_keys = set(client.app.openapi()["components"]["schemas"])
    assert "DSSSimulationResponse" in body_keys

    import json

    parsed = json.loads(raw)
    assert "yield" in parsed  # alias preserved at top level
    banned_flat_fields = [
        "Net_Cash_Contribution_DSS",
        "Total_Revenue_DSS",
        "Revenue_duck_potential",
        "Revenue_gabah",
        "N_survive",
        "Yield_total_pred",
        "sandbox",
        "age_flag",
        "density_status",
    ]
    for field in banned_flat_fields:
        assert field not in parsed


# ---------------------------------------------------------------------------
# Price resolution variants
# ---------------------------------------------------------------------------


def test_explicit_null_price_equals_omitted_price() -> None:
    client = make_client()
    without_field = _simulate(client).json()
    with_null = _simulate(client, {"p_duck_buy": None}).json()

    for section in ("input", "operational", "duck", "yield", "fertilizer_baseline", "costs", "economics", "reliability"):
        assert with_null[section] == without_field[section]
    assert with_null["trace"]["defaulted_inputs"] == without_field["trace"]["defaulted_inputs"]


def test_manual_price_separation_and_ledger_use() -> None:
    client = make_client()
    body = _simulate(client, {"p_duck_buy": 30000}).json()

    inp = body["input"]
    assert inp["p_duck_buy_manual"] == 30000.0
    assert inp["p_duck_buy_effective"] == 30000.0
    assert inp["p_duck_buy_source"] == "USER_INPUT"
    assert body["trace"]["defaulted_inputs"] == []
    assert body["costs"]["duck_purchase"]["amount_rp"] == 28 * 30000


def test_zero_price_rejected_as_validation_error() -> None:
    client = make_client()
    response = _simulate(client, {"p_duck_buy": 0})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "validation_error"


def test_non_finite_price_rejected() -> None:
    client = make_client()
    # Raw JSON NaN/Infinity tokens (parsers may accept them; the schema must
    # reject them as measurements).
    for token in ("NaN", "Infinity", "-Infinity"):
        payload = dict(DEFAULT_SIMULATION_PAYLOAD)
        body_parts = [f'"{k}": {json.dumps(v)}' for k, v in payload.items()]
        body_parts.append(f'"p_duck_buy": {token}')
        raw = "{" + ", ".join(body_parts) + "}"
        response = client.post(
            f"{API}/dss/simulate",
            content=raw.encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 400, f"token={token}: {response.text}"
        assert response.json()["error"]["code"] == "validation_error"


# ---------------------------------------------------------------------------
# Categorical references
# ---------------------------------------------------------------------------


def test_unknown_variety_is_422() -> None:
    client = make_client()
    response = _simulate(client, {"rice_variety": "ciherang"})
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "invalid_reference"
    assert error["field"] == "rice_variety"


def test_unknown_planting_system_is_422() -> None:
    client = make_client()
    response = _simulate(client, {"planting_system": "hidroponik"})
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "invalid_reference"
    assert error["field"] == "planting_system"


# ---------------------------------------------------------------------------
# Unsupported scientific domains stay HTTP 200 with nulls (no penalties)
# ---------------------------------------------------------------------------


def test_age_outside_support_nulls_survival_chain() -> None:
    client = make_client()
    for age, expected_flag in ((20, "CAUTION"), (31, "OUTSIDE_LOCAL_RANGE")):
        body = _simulate(client, {"duck_age_days": age}).json()
        assert body["operational"]["age_support"] == expected_flag
        assert body["operational"]["extrapolation"] == "OUT_OF_DOMAIN"
        assert body["duck"]["survival_availability"] == "UNAVAILABLE"
        assert body["duck"]["lambda_eff"] is None
        assert body["duck"]["surviving_ducks"] is None
        assert body["duck"]["terminal_value_ref_rp"] is None
        assert body["reliability"]["survival_availability"] == "UNAVAILABLE"
        assert any(w.startswith("SURVIVAL_UNAVAILABLE") or w.startswith("AGE_") for w in body["warnings"])


def test_density_outside_support_nulls_survival_chain() -> None:
    client = make_client()
    cases = [
        # Tegel d=40/10=4 -> EXTRAPOLATION (above supported 3, below high-risk 8).
        ({"planting_system": "tegel", "land_area_are": 10, "duck_count": 40}, "EXTRAPOLATION"),
        # Jarwo d=55/10=5.5 -> LIMITED_TEST band.
        ({"land_area_are": 10, "duck_count": 55}, "LIMITED_TEST"),
        # d=80/10=8 -> HIGH_RISK threshold.
        ({"land_area_are": 10, "duck_count": 80}, "HIGH_RISK"),
    ]
    for overrides, expected_flag in cases:
        body = _simulate(client, overrides).json()
        assert body["operational"]["density_support"] == expected_flag
        assert body["duck"]["surviving_ducks"] is None
        assert body["duck"]["terminal_value_ref_rp"] is None
        assert body["economics"]["gross_economic_value_rp"] is None
        assert any(w.startswith("DENSITY_OUTSIDE_SUPPORTED_DOMAIN") for w in body["warnings"])


def test_boundary_densities_still_supported() -> None:
    client = make_client()
    jarwo_edge = _simulate(client, {"land_area_are": 10, "duck_count": 40}).json()
    assert jarwo_edge["operational"]["density_support"] == "SUPPORTED"
    assert jarwo_edge["duck"]["surviving_ducks"] == int(40 * 0.90)

    tegel_edge = _simulate(
        client, {"planting_system": "tegel", "land_area_are": 10, "duck_count": 30}
    ).json()
    assert tegel_edge["operational"]["density_support"] == "SUPPORTED"
    assert tegel_edge["duck"]["surviving_ducks"] == 27


# ---------------------------------------------------------------------------
# Persistence gating by authentication
# ---------------------------------------------------------------------------


def test_unauthenticated_simulate_persists_nothing_but_matches_authenticated_numbers() -> None:
    from app.repositories.history_repository import history_repository
    from app.core.database import get_connection

    client = make_client()
    anon_body = _simulate(client).json()

    headers = register_and_login(client)
    auth_body = _simulate_as(client, headers).json()

    # Authentication never changes numeric results (ignore time/version meta).
    for key in ("input", "operational", "calendar", "duck", "yield", "fertilizer_baseline", "costs", "economics", "reliability", "warnings", "trace"):
        assert auth_body[key] == anon_body[key], f"difference in {key}"

    # Exactly one v4 row for the authenticated user; none overall before it.
    with get_connection() as connection:
        count = connection.execute("SELECT COUNT(*) AS c FROM dss_simulation_histories_r2").fetchone()["c"]
    assert count == 1
    items = client.get(f"{API}/dss/histories", headers=headers).json()["data"]
    assert len(items) == 1
    assert items[0]["model_version"] == "R2"
    assert items[0]["schema_version"] == 4
