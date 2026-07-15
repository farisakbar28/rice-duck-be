import json
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4

from app.core.database import get_connection
from app.domain.models import SimulationHistory, SimulationHistoryLegacy


# SoT FINAL (docs/Model_Matematika_..._FINAL.docx): the response is split into
# Core Validated (Cost_duck_buy, Cost_total_cash) and Empirically Uncorrelated
# Isolated (Cost_*_isolated) groups. History rows persist the same split.
V2_INSERT_SQL = """
INSERT INTO dss_simulation_histories (
    id, user_id, schema_version, created_at,
    density_status, age_status, d_masuk_bebek, d_tarik_bebek, d_panen_gabah,
    n_survive,
    yield_are_predict, yield_total_predict,
    revenue_gabah, revenue_duck, total_revenue,
    cost_duck_buy, cost_feed_isolated,
    cost_weeding_isolated, cost_pesticide_isolated, cost_infra_isolated,
    cost_fertilizer_isolated, cost_infra_net_isolated, cost_infra_cage_isolated,
    cost_fert_urea_isolated, cost_fert_phonska_isolated, cost_fert_kcl_isolated,
    cost_total_cash,
    profit_net_cash,
    input_json, actual_scenario_json, recommended_scenario_json,
    comparison_json, risk_json, trace_json, notes_json,
    economics_json, ecology_json, environment_json, lookup_json,
    validation_json, data_readiness_json
) VALUES (
    ?, ?, 2, ?,
    ?, ?, ?, ?, ?,
    ?,
    ?, ?,
    ?, ?, ?,
    ?, ?,
    ?, ?, ?,
    ?, ?, ?,
    ?, ?, ?,
    ?,
    ?,
    ?, ?, ?, ?,
    ?, ?, ?, ?,
    ?, ?, ?, ?,
    ?, ?
)
"""


class HistoryRepository:
    # ------------------------------------------------------------------
    # v2 — explicit columns (SoT FINAL)
    # ------------------------------------------------------------------
    def create_v2(self, *, user_id: str, history: SimulationHistory) -> SimulationHistory:
        with get_connection() as connection:
            connection.execute(
                V2_INSERT_SQL,
                (
                    history.id,
                    history.user_id,
                    history.created_at.isoformat(),
                    history.density_status,
                    history.age_status,
                    history.d_masuk_bebek,
                    history.d_tarik_bebek,
                    history.d_panen_gabah,
                    history.n_survive,
                    history.yield_are_predict,
                    history.yield_total_predict,
                    history.revenue_gabah,
                    history.revenue_duck,
                    history.total_revenue,
                    history.cost_duck_buy,
                    history.cost_feed_isolated,
                    history.cost_weeding_isolated,
                    history.cost_pesticide_isolated,
                    history.cost_infra_isolated,
                    history.cost_fertilizer_isolated,
                    history.cost_infra_net_isolated,
                    history.cost_infra_cage_isolated,
                    history.cost_fert_urea_isolated,
                    history.cost_fert_phonska_isolated,
                    history.cost_fert_kcl_isolated,
                    history.cost_total_cash,
                    history.profit_net_cash,
                    json.dumps({}),     # input_json
                    json.dumps({}),     # actual_scenario_json
                    json.dumps({}),     # recommended_scenario_json
                    json.dumps({}),     # comparison_json
                    json.dumps({}),     # risk_json
                    json.dumps({}),     # trace_json
                    json.dumps([]),     # notes_json
                    json.dumps({}),     # economics_json
                    json.dumps({}),     # ecology_json
                    json.dumps({}),     # environment_json
                    json.dumps({}),     # lookup_json
                    json.dumps({}),     # validation_json
                    json.dumps({}),     # data_readiness_json
                ),
            )
        return history

    def new_id(self) -> str:
        return str(uuid4())

    def now(self) -> datetime:
        return datetime.now(timezone.utc)

    # ------------------------------------------------------------------
    # Reads — return v2 or legacy depending on schema_version.
    # ------------------------------------------------------------------
    def list_by_user(self, user_id: str) -> list[SimulationHistory | SimulationHistoryLegacy]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT * FROM dss_simulation_histories
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            ).fetchall()
        return [self._to_model(row) for row in rows]

    def get_by_id_and_user(
        self,
        history_id: str,
        user_id: str,
    ) -> SimulationHistory | SimulationHistoryLegacy | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT * FROM dss_simulation_histories
                WHERE id = ? AND user_id = ?
                """,
                (history_id, user_id),
            ).fetchone()
        return self._to_model(row) if row else None

    def delete_by_id_and_user(self, history_id: str, user_id: str) -> bool:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                DELETE FROM dss_simulation_histories
                WHERE id = ? AND user_id = ?
                """,
                (history_id, user_id),
            )
        return cursor.rowcount > 0

    def _to_model(self, row: sqlite3.Row) -> SimulationHistory | SimulationHistoryLegacy:
        version = row["schema_version"]
        if version >= 2:
            return SimulationHistory(
                id=row["id"],
                user_id=row["user_id"],
                schema_version=version,
                density_status=row["density_status"],
                age_status=row["age_status"],
                d_masuk_bebek=row["d_masuk_bebek"],
                d_tarik_bebek=row["d_tarik_bebek"],
                d_panen_gabah=row["d_panen_gabah"],
                n_survive=row["n_survive"],
                yield_are_predict=row["yield_are_predict"],
                yield_total_predict=row["yield_total_predict"],
                revenue_gabah=row["revenue_gabah"],
                revenue_duck=row["revenue_duck"],
                total_revenue=row["total_revenue"],
                cost_duck_buy=row["cost_duck_buy"],
                cost_feed_isolated=row["cost_feed_isolated"],
                cost_weeding_isolated=row["cost_weeding_isolated"],
                cost_pesticide_isolated=row["cost_pesticide_isolated"],
                cost_infra_isolated=row["cost_infra_isolated"],
                cost_fertilizer_isolated=row["cost_fertilizer_isolated"],
                cost_infra_net_isolated=row["cost_infra_net_isolated"],
                cost_infra_cage_isolated=row["cost_infra_cage_isolated"],
                cost_fert_urea_isolated=row["cost_fert_urea_isolated"],
                cost_fert_phonska_isolated=row["cost_fert_phonska_isolated"],
                cost_fert_kcl_isolated=row["cost_fert_kcl_isolated"],
                cost_total_cash=row["cost_total_cash"],
                profit_net_cash=row["profit_net_cash"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
        return SimulationHistoryLegacy(
            id=row["id"],
            user_id=row["user_id"],
            input_data=json.loads(row["input_json"]),
            actual_scenario=json.loads(row["actual_scenario_json"]),
            recommended_scenario=json.loads(row["recommended_scenario_json"]),
            comparison=json.loads(row["comparison_json"]),
            risk=json.loads(row["risk_json"]),
            trace=json.loads(row["trace_json"]),
            notes=json.loads(row["notes_json"]),
            economics=json.loads(row["economics_json"]),
            ecology=json.loads(row["ecology_json"]),
            environment=json.loads(row["environment_json"]),
            lookup=json.loads(row["lookup_json"]),
            validation=json.loads(row["validation_json"]),
            data_readiness=json.loads(row["data_readiness_json"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            schema_version=version,
        )


history_repository = HistoryRepository()
