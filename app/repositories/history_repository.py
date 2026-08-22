import json
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4

from app.core.database import get_connection
from app.domain.models import SimulationHistory, SimulationHistoryLegacy


V3_INSERT_SQL = """
INSERT INTO dss_simulation_histories (
    id, user_id, schema_version, created_at,
    input_json, actual_scenario_json, recommended_scenario_json,
    comparison_json, risk_json, trace_json, notes_json,
    economics_json, ecology_json, environment_json, lookup_json,
    validation_json, data_readiness_json,
    land_area_are, duck_count, rice_variety, planting_system,
    duck_age_days, planting_date, p_duck_buy,
    age_flag,
    density_are, density_ha, density_status,
    hst_in, hst_out, t_active,
    d_in, d_out,
    harvest_hst_min, harvest_hst_max,
    d_panen_min, d_panen_max,
    n_survive,
    yield_are_pred, yield_total_pred,
    revenue_gabah, revenue_duck_potential,
    cost_duck_buy, cost_feed, core_cash_cost,
    total_revenue_dss, net_cash_contribution_dss,
    warnings_json
) VALUES (
    ?, ?, 3, ?,
    '{}', '{}', '{}', '{}', '{}', '{}', '[]',
    '{}', '{}', '{}', '{}', '{}', '{}',
    ?, ?, ?, ?,
    ?, ?, ?,
    ?,
    ?, ?, ?,
    ?, ?, ?,
    ?, ?,
    ?, ?,
    ?, ?,
    ?,
    ?, ?,
    ?, ?,
    ?, ?, ?,
    ?, ?,
    ?
)
"""


class HistoryRepository:
    # ------------------------------------------------------------------
    # v3 — SoT FINAL explicit columns
    # ------------------------------------------------------------------
    def create_v3(
        self, *, user_id: str, history: SimulationHistory
    ) -> SimulationHistory:
        with get_connection() as connection:
            connection.execute(
                V3_INSERT_SQL,
                (
                    history.id,
                    history.user_id,
                    history.created_at.isoformat(),
                    # v3 explicit fields
                    history.land_area_are,
                    history.duck_count,
                    history.rice_variety,
                    history.planting_system,
                    history.duck_age_days,
                    history.planting_date,
                    history.p_duck_buy,
                    history.age_flag,
                    history.density_are,
                    history.density_ha,
                    history.density_status,
                    history.hst_in,
                    history.hst_out,
                    history.t_active,
                    history.d_in,
                    history.d_out,
                    history.harvest_hst_min,
                    history.harvest_hst_max,
                    history.d_panen_min,
                    history.d_panen_max,
                    history.n_survive,
                    history.yield_are_pred,
                    history.yield_total_pred,
                    history.revenue_gabah,
                    history.revenue_duck_potential,
                    history.cost_duck_buy,
                    history.cost_feed,
                    history.core_cash_cost,
                    history.total_revenue_dss,
                    history.net_cash_contribution_dss,
                    history.warnings_json,
                ),
            )
        return history

    def new_id(self) -> str:
        return str(uuid4())

    def now(self) -> datetime:
        return datetime.now(timezone.utc)

    # ------------------------------------------------------------------
    # Reads — dispatch on schema_version
    # ------------------------------------------------------------------
    def list_by_user(
        self, user_id: str
    ) -> list[SimulationHistory | SimulationHistoryLegacy]:
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

    def _to_model(
        self, row: sqlite3.Row
    ) -> SimulationHistory | SimulationHistoryLegacy:
        version = row["schema_version"]
        if version >= 3:
            return SimulationHistory(
                id=row["id"],
                user_id=row["user_id"],
                schema_version=version,
                land_area_are=row["land_area_are"],
                duck_count=row["duck_count"],
                rice_variety=row["rice_variety"],
                planting_system=row["planting_system"],
                duck_age_days=row["duck_age_days"],
                planting_date=row["planting_date"],
                p_duck_buy=row["p_duck_buy"],
                age_flag=row["age_flag"],
                density_are=row["density_are"],
                density_ha=row["density_ha"],
                density_status=row["density_status"],
                hst_in=row["hst_in"],
                hst_out=row["hst_out"],
                t_active=row["t_active"],
                d_in=row["d_in"],
                d_out=row["d_out"],
                harvest_hst_min=row["harvest_hst_min"],
                harvest_hst_max=row["harvest_hst_max"],
                d_panen_min=row["d_panen_min"],
                d_panen_max=row["d_panen_max"],
                n_survive=row["n_survive"],
                yield_are_pred=row["yield_are_pred"],
                yield_total_pred=row["yield_total_pred"],
                revenue_gabah=row["revenue_gabah"],
                revenue_duck_potential=row["revenue_duck_potential"],
                cost_duck_buy=row["cost_duck_buy"],
                cost_feed=row["cost_feed"],
                core_cash_cost=row["core_cash_cost"],
                total_revenue_dss=row["total_revenue_dss"],
                net_cash_contribution_dss=row["net_cash_contribution_dss"],
                warnings_json=row["warnings_json"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
        # v1/v2 legacy — read-only
        return SimulationHistoryLegacy(
            id=row["id"],
            user_id=row["user_id"],
            input_data=self._safe_json(row, "input_json", {}),
            actual_scenario=self._safe_json(row, "actual_scenario_json", {}),
            recommended_scenario=self._safe_json(row, "recommended_scenario_json", {}),
            comparison=self._safe_json(row, "comparison_json", {}),
            risk=self._safe_json(row, "risk_json", {}),
            trace=self._safe_json(row, "trace_json", {}),
            notes=self._safe_json(row, "notes_json", []),
            economics=self._safe_json(row, "economics_json", {}),
            ecology=self._safe_json(row, "ecology_json", {}),
            environment=self._safe_json(row, "environment_json", {}),
            lookup=self._safe_json(row, "lookup_json", {}),
            validation=self._safe_json(row, "validation_json", {}),
            data_readiness=self._safe_json(row, "data_readiness_json", {}),
            created_at=datetime.fromisoformat(row["created_at"]),
            schema_version=version,
        )

    @staticmethod
    def _safe_json(row: sqlite3.Row, key: str, default):
        try:
            val = row[key]
            if val is None:
                return default
            return json.loads(val)
        except (KeyError, json.JSONDecodeError):
            return default


history_repository = HistoryRepository()
