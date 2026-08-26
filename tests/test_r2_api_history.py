"""Phase 3: history endpoints -- v4 snapshot persistence semantics.

Mandates (docs/05 sections 3/7/10): round-trip equality, NULL survival of
unknown outputs, manual/effective price separation, version retention,
snapshot-not-recomputed, ownership isolation, delete, and the documented
legacy policy (list=merged with explicit LEGACY label; detail=409
legacy_history_semantics; never recalculated).
"""

from dataclasses import replace

from app.core.database import get_connection
from app.data.seed import PARAMETER_REGISTRY, PARAMETER_REGISTRY_VERSION
from tests.r2_api_utils import (
    API,
    DEFAULT_SIMULATION_PAYLOAD,
    login_headers,
    make_client,
    register_and_login,
    register_user,
)


def _simulate(client, headers=None, overrides: dict | None = None):
    payload = dict(DEFAULT_SIMULATION_PAYLOAD)
    payload.update(overrides or {})
    kwargs = {"json": payload}
    if headers is not None:
        kwargs["headers"] = headers
    return client.post(f"{API}/dss/simulate", **kwargs)


def _seed_legacy_row(user_id: str) -> str:
    """Insert one immutable schema_version=3 row directly (pre-R2 fixture)."""
    import uuid

    legacy_id = str(uuid.uuid4())
    created_at = "2025-01-01T00:00:00+00:00"
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO dss_simulation_histories (
                id, user_id, schema_version, created_at,
                input_json, actual_scenario_json, recommended_scenario_json,
                comparison_json, risk_json, trace_json, notes_json,
                economics_json, ecology_json, environment_json, lookup_json,
                validation_json, data_readiness_json,
                rice_variety, planting_system, duck_count, land_area_are,
                duck_age_days, planting_date, p_duck_buy, age_flag,
                density_are, density_ha, density_status,
                hst_in, hst_out, t_active, d_in, d_out,
                harvest_hst_min, harvest_hst_max, d_panen_min, d_panen_max,
                n_survive, yield_are_pred, yield_total_pred,
                revenue_gabah, revenue_duck_potential, cost_duck_buy,
                cost_feed, core_cash_cost, total_revenue_dss,
                net_cash_contribution_dss, warnings_json
            ) VALUES (?, ?, 3, ?,
                      '{}', '{}', '{}', '{}', '{}', '{}', '[]',
                      '{}', '{}', '{}', '{}', '{}', '{}',
                      'sertani', 'jajar_legowo', 20, 5.0, 25,
                      '2025-05-01', 26500, 'RECOMMENDED', 4.0, 0.04,
                      'RECOMMENDED', 21, 65, 44, '2025-05-22',
                      '2025-07-06', 100, 110, '2025-08-09', '2025-08-19',
                      20, 47.8767507, 239.3837535, 1556009.39775, 1050000.0,
                      530000.0, 400000.0, 930000.0, 2606009.39775,
                      2126009.39775, '[]')
            """,
            (legacy_id, user_id, created_at),
        )
    return legacy_id


# ---------------------------------------------------------------------------
# Round trip + column semantics
# ---------------------------------------------------------------------------


def test_v4_round_trip_returns_stored_semantic_snapshot() -> None:
    client = make_client()
    headers = register_and_login(client)

    original = _simulate(client, headers).json()
    items = client.get(f"{API}/dss/histories", headers=headers).json()["data"]
    assert len(items) == 1
    history_id = items[0]["id"]

    detail = client.get(f"{API}/dss/histories/{history_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json() == original


def test_phase6_snapshot_preserves_yield_envelope_and_source_trace() -> None:
    client = make_client()
    headers = register_and_login(client, email="phase6-history@example.com")
    original = _simulate(client, headers).json()
    history_id = client.get(f"{API}/dss/histories", headers=headers).json()["data"][0]["id"]
    stored = client.get(f"{API}/dss/histories/{history_id}", headers=headers).json()
    for key in ("yield_ref_kg_per_are", "yield_low_kg_per_are", "yield_high_kg_per_are",
                "yield_range_type", "yield_baseline_source_id", "yield_frd_source_id",
                "yield_evidence_strength", "yield_evidence_warning"):
        assert stored["yield"][key] == original["yield"][key]
    assert stored["model"]["parameter_registry_version"] == "R2-2026-08-26.3"
    assert stored["model"]["freeze_id"] == "R2-FREEZE-2026-08-26.4"


def test_unknown_scientific_outputs_persist_as_null() -> None:
    client = make_client()
    headers = register_and_login(client)
    _simulate(client, headers)

    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM dss_simulation_histories_r2"
        ).fetchone()

    assert row["yield_total_kg"] is not None
    assert row["margin_core_rp"] is not None
    assert row["profit_full_est_rp"] is None
    assert row["schema_version"] == 4
    assert row["model_version"] == "R2"
    assert row["parameter_registry_version"] == PARAMETER_REGISTRY_VERSION


def test_price_manual_effective_separation_persisted() -> None:
    client = make_client()
    headers = register_and_login(client)
    _simulate(client, headers)  # omitted price
    _simulate(client, headers, {"p_duck_buy": 30000})  # manual price

    with get_connection() as connection:
        rows = connection.execute(
            "SELECT p_duck_buy_manual, p_duck_buy_effective "
            "FROM dss_simulation_histories_r2 ORDER BY created_at ASC"
        ).fetchall()

    assert rows[0]["p_duck_buy_manual"] is None
    assert rows[0]["p_duck_buy_effective"] == 26500
    assert rows[1]["p_duck_buy_manual"] == 30000
    assert rows[1]["p_duck_buy_effective"] == 30000


# ---------------------------------------------------------------------------
# Snapshot immutability under registry mutation (mandatory test)
# ---------------------------------------------------------------------------


def test_stored_snapshot_not_recomputed_after_registry_change(monkeypatch) -> None:
    client = make_client()
    headers = register_and_login(client)

    original = _simulate(client, headers).json()
    items = client.get(f"{API}/dss/histories", headers=headers).json()["data"]
    history_id = items[0]["id"]

    # Mutate the runtime registry: lambda 0.90 -> 0.80 would change a fresh run.
    entry = PARAMETER_REGISTRY["lambda_safe_ref"]
    mutated = replace(entry, value=0.80)
    monkeypatch.setitem(PARAMETER_REGISTRY, "lambda_safe_ref", mutated)
    try:
        fresh = _simulate(client, headers).json()
        assert fresh["duck"]["surviving_ducks"] == int(28 * 0.80)

        stored = client.get(f"{API}/dss/histories/{history_id}", headers=headers)
        assert stored.status_code == 200
        # The saved response is untouched by the registry change.
        assert stored.json() == original
    finally:
        monkeypatch.undo()


# ---------------------------------------------------------------------------
# Ownership isolation
# ---------------------------------------------------------------------------


def test_ownership_isolation_across_users_and_stores() -> None:
    client = make_client()
    owner_headers = register_and_login(client, email="owner@example.com")
    other_headers = register_and_login(client, email="other@example.com")

    _simulate(client, owner_headers)
    owner_items = client.get(f"{API}/dss/histories", headers=owner_headers).json()["data"]
    r2_id = owner_items[0]["id"]

    # R2 detail/delete by another user -> 404, no existence disclosure.
    assert client.get(f"{API}/dss/histories/{r2_id}", headers=other_headers).status_code == 404
    assert client.delete(f"{API}/dss/histories/{r2_id}", headers=other_headers).status_code == 404
    other_list_ids = {i["id"] for i in client.get(f"{API}/dss/histories", headers=other_headers).json()["data"]}
    assert r2_id not in other_list_ids


# ---------------------------------------------------------------------------
# Delete + list policies
# ---------------------------------------------------------------------------


def test_delete_r2_history_then_detail_is_404() -> None:
    client = make_client()
    headers = register_and_login(client)
    _simulate(client, headers)
    history_id = client.get(f"{API}/dss/histories", headers=headers).json()["data"][0]["id"]

    deleted = client.delete(f"{API}/dss/histories/{history_id}", headers=headers)
    assert deleted.status_code == 200
    assert "deleted" in deleted.json()["message"].lower()
    assert client.get(f"{API}/dss/histories/{history_id}", headers=headers).status_code == 404
    assert client.delete(f"{API}/dss/histories/{history_id}", headers=headers).status_code == 404


def test_histories_require_authentication() -> None:
    client = make_client()
    assert client.get(f"{API}/dss/histories").status_code == 401
    assert client.delete(f"{API}/dss/histories/some-id").status_code == 401
    assert client.get(f"{API}/dss/histories/some-id").status_code == 401


# ---------------------------------------------------------------------------
# Legacy policy (docs/05 section 7)
# ---------------------------------------------------------------------------


def test_legacy_row_listed_as_legacy_never_as_r2() -> None:
    client = make_client()
    email = "legacy-owner@example.com"
    user_id = register_user(client, email=email)
    legacy_id = _seed_legacy_row(user_id)
    headers = login_headers(client, email=email)

    items = client.get(f"{API}/dss/histories", headers=headers).json()["data"]
    legacy_items = [i for i in items if i["id"] == legacy_id]
    assert len(legacy_items) == 1
    legacy_item = legacy_items[0]
    assert legacy_item["model_version"] == "LEGACY"
    assert legacy_item["schema_version"] == 3
    assert legacy_item["r2_summary"] is None


def test_legacy_detail_returns_409_not_recalculated_r2() -> None:
    client = make_client()
    email = "legacy-detail@example.com"
    user_id = register_user(client, email=email)
    legacy_id = _seed_legacy_row(user_id)
    headers = login_headers(client, email=email)

    detail = client.get(f"{API}/dss/histories/{legacy_id}", headers=headers)
    assert detail.status_code == 409
    assert detail.json()["error"]["code"] == "legacy_history_semantics"

    # Another user gets 404 (no existence disclosure) for the same row.
    other_headers = register_and_login(client, email="legacy-detail-other@example.com")
    assert client.get(f"{API}/dss/histories/{legacy_id}", headers=other_headers).status_code == 404


def test_legacy_operations_never_write_v4_and_legacy_delete_works() -> None:
    client = make_client()
    email = "legacy-delete@example.com"
    user_id = register_user(client, email=email)
    legacy_id = _seed_legacy_row(user_id)
    headers = login_headers(client, email=email)

    with get_connection() as connection:
        before = connection.execute(
            "SELECT COUNT(*) AS c FROM dss_simulation_histories_r2"
        ).fetchone()["c"]

    deleted = client.delete(f"{API}/dss/histories/{legacy_id}", headers=headers)
    assert deleted.status_code == 200
    assert client.get(f"{API}/dss/histories/{legacy_id}", headers=headers).status_code == 404

    with get_connection() as connection:
        after = connection.execute(
            "SELECT COUNT(*) AS c FROM dss_simulation_histories_r2"
        ).fetchone()["c"]

    # Legacy reads/deletes never create or touch v4 rows.
    assert after == before
