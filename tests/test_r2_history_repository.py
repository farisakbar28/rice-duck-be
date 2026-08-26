"""Phase 3: R2 history repository -- v4 storage semantics at the data layer."""

from datetime import datetime, timezone
from uuid import uuid4

from app.core.database import get_connection
from app.domain.models import R2HistorySnapshot
from app.repositories.history_repository import history_repository


def _ensure_user(user_id: str) -> None:
    with get_connection() as connection:
        connection.execute(
            "INSERT OR IGNORE INTO users (id, name, email, password_hash, created_at, updated_at) "
            "VALUES (?, 'Repo Test', ?, 'x', '2026-08-26', '2026-08-26')",
            (user_id, f"{user_id}@example.com"),
        )


def _snapshot(**overrides) -> R2HistorySnapshot:
    base = dict(
        id=str(uuid4()),
        user_id="user-r2-repo",
        schema_version=4,
        model_version="R2",
        parameter_registry_version="R2-2026-08-26.2",
        model_commit_sha=None,
        created_at=datetime(2026, 8, 26, 12, 0, 0, tzinfo=timezone.utc),
        request_json='{"land_area_are":7.0}',
        response_json='{"model":{"frozen":false},"yield":{"availability":"UNAVAILABLE"}}',
        trace_json='{"active_formula_ids":[]}',
        land_area_are=7.0,
        duck_count=28,
        rice_variety="sertani",
        planting_system="jajar_legowo",
        duck_age_days=30,
        planting_date="2026-06-01",
        p_duck_buy_manual=None,
        p_duck_buy_effective=26500.0,
        density_are=4.0,
        age_support="SUPPORTED",
        density_support="SUPPORTED",
        extrapolation_status="IN_DOMAIN",
        yield_availability="UNAVAILABLE",
        survival_availability="AVAILABLE",
        cost_completeness="INCOMPLETE",
        yield_total_kg=None,
        margin_core_rp=None,
        profit_full_est_rp=None,
    )
    base.update(overrides)
    return R2HistorySnapshot(**base)


def test_v4_table_and_index_exist() -> None:
    with get_connection() as connection:
        tables = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        indexes = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='index'"
            ).fetchall()
        }
    assert "dss_simulation_histories_r2" in tables
    assert "idx_dss_r2_user_created" in indexes


def test_scientific_columns_nullable_without_zero_defaults() -> None:
    with get_connection() as connection:
        columns = connection.execute(
            "PRAGMA table_info(dss_simulation_histories_r2)"
        ).fetchall()
    by_name = {col["name"]: col for col in columns}

    for column in ("yield_total_kg", "margin_core_rp", "profit_full_est_rp", "p_duck_buy_manual", "model_commit_sha"):
        assert by_name[column]["notnull"] == 0, f"{column} must stay nullable"
        assert by_name[column]["dflt_value"] is None, f"{column} must have no DEFAULT (esp. not 0)"


def test_create_get_round_trip_preserves_nulls() -> None:
    _ensure_user("user-r2-repo")
    snapshot = _snapshot()
    history_repository.create_r2(snapshot)

    loaded = history_repository.get_r2_by_id_and_user(snapshot.id, snapshot.user_id)
    assert loaded == snapshot
    assert loaded.yield_total_kg is None
    assert loaded.margin_core_rp is None
    assert loaded.profit_full_est_rp is None
    assert loaded.p_duck_buy_manual is None


def test_list_orders_desc_and_filters_by_user() -> None:
    _ensure_user("user-r2-repo")
    _ensure_user("someone-else")
    first = _snapshot(created_at=datetime(2026, 8, 1, tzinfo=timezone.utc))
    second = _snapshot(created_at=datetime(2026, 8, 2, tzinfo=timezone.utc))
    other_user = _snapshot(user_id="someone-else")
    for item in (first, second, other_user):
        history_repository.create_r2(item)

    rows = history_repository.list_r2_by_user(first.user_id)
    assert [r.id for r in rows] == [second.id, first.id]
    assert all(r.user_id == first.user_id for r in rows)
    assert history_repository.list_r2_by_user("missing-user") == []


def test_delete_scoped_by_user() -> None:
    _ensure_user("user-r2-repo")
    snapshot = _snapshot()
    history_repository.create_r2(snapshot)

    assert history_repository.delete_r2_by_id_and_user(snapshot.id, "wrong-user") is False
    assert history_repository.get_r2_by_id_and_user(snapshot.id, snapshot.user_id) is not None
    assert history_repository.delete_r2_by_id_and_user(snapshot.id, snapshot.user_id) is True
    assert history_repository.get_r2_by_id_and_user(snapshot.id, snapshot.user_id) is None


def test_foreign_key_cascades_on_user_delete() -> None:
    user_id = str(uuid4())
    _ensure_user(user_id)
    snapshot = _snapshot(user_id=user_id)
    history_repository.create_r2(snapshot)

    with get_connection() as connection:
        connection.execute("DELETE FROM users WHERE id = ?", (user_id,))
        remaining = connection.execute(
            "SELECT COUNT(*) AS c FROM dss_simulation_histories_r2 WHERE user_id = ?",
            (user_id,),
        ).fetchone()["c"]
    assert remaining == 0
