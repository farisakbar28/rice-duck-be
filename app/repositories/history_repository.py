"""History persistence -- R2 schema v4 + isolated legacy read access.

Layout (docs/05_R2_PERSISTENCE_VERSIONING.md):

  * R2 operations write/read ONLY ``dss_simulation_histories_r2`` (v4).
    Every authenticated simulation persists exactly one row whose JSON
    snapshots are the canonical semantic record; the indexed columns exist
    for list/filter efficiency only. Unknown scientific outputs stay SQL
    NULL (never numeric zero).
  * Legacy operations are read/delete-only over ``dss_simulation_histories``
    (schema_version <= 3, pre-R2 semantics). They exist so historical rows
    remain visible/auditable and user-owned deletion keeps working; they
    NEVER convert legacy values into R2 values. There is deliberately no
    v3 writer anymore: production code must not create new legacy rows.
"""

import json
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4

from app.core.database import get_connection
from app.domain.models import R2HistorySnapshot, SimulationHistory, SimulationHistoryLegacy


R2_INSERT_SQL = """
INSERT INTO dss_simulation_histories_r2 (
    id, user_id, schema_version, model_version,
    parameter_registry_version, model_commit_sha, created_at,
    request_json, response_json, trace_json,
    land_area_are, duck_count, rice_variety, planting_system,
    duck_age_days, planting_date,
    p_duck_buy_manual, p_duck_buy_effective,
    density_are, age_support, density_support, extrapolation_status,
    yield_availability, survival_availability, cost_completeness,
    yield_total_kg, margin_core_rp, profit_full_est_rp
) VALUES (
    ?, ?, ?, ?,
    ?, ?, ?,
    ?, ?, ?,
    ?, ?, ?, ?,
    ?, ?,
    ?, ?,
    ?, ?, ?, ?,
    ?, ?, ?,
    ?, ?, ?
)
"""

R2_SELECT_COLUMNS = """
    id, user_id, schema_version, model_version,
    parameter_registry_version, model_commit_sha, created_at,
    request_json, response_json, trace_json,
    land_area_are, duck_count, rice_variety, planting_system,
    duck_age_days, planting_date,
    p_duck_buy_manual, p_duck_buy_effective,
    density_are, age_support, density_support, extrapolation_status,
    yield_availability, survival_availability, cost_completeness,
    yield_total_kg, margin_core_rp, profit_full_est_rp
"""


class HistoryRepository:
    # ------------------------------------------------------------------
    # R2 — schema v4 (canonical persistence for /dss/simulate)
    # ------------------------------------------------------------------
    def create_r2(self, snapshot: R2HistorySnapshot) -> R2HistorySnapshot:
        with get_connection() as connection:
            connection.execute(
                R2_INSERT_SQL,
                (
                    snapshot.id,
                    snapshot.user_id,
                    snapshot.schema_version,
                    snapshot.model_version,
                    snapshot.parameter_registry_version,
                    snapshot.model_commit_sha,
                    snapshot.created_at.isoformat(),
                    snapshot.request_json,
                    snapshot.response_json,
                    snapshot.trace_json,
                    snapshot.land_area_are,
                    snapshot.duck_count,
                    snapshot.rice_variety,
                    snapshot.planting_system,
                    snapshot.duck_age_days,
                    snapshot.planting_date,
                    snapshot.p_duck_buy_manual,
                    snapshot.p_duck_buy_effective,
                    snapshot.density_are,
                    snapshot.age_support,
                    snapshot.density_support,
                    snapshot.extrapolation_status,
                    snapshot.yield_availability,
                    snapshot.survival_availability,
                    snapshot.cost_completeness,
                    snapshot.yield_total_kg,
                    snapshot.margin_core_rp,
                    snapshot.profit_full_est_rp,
                ),
            )
        return snapshot

    def list_r2_by_user(self, user_id: str) -> list[R2HistorySnapshot]:
        with get_connection() as connection:
            rows = connection.execute(
                f"""
                SELECT {R2_SELECT_COLUMNS}
                FROM dss_simulation_histories_r2
                WHERE user_id = ?
                ORDER BY created_at DESC, id DESC
                """,
                (user_id,),
            ).fetchall()
        return [self._row_to_r2(row) for row in rows]

    def get_r2_by_id_and_user(
        self, history_id: str, user_id: str
    ) -> R2HistorySnapshot | None:
        with get_connection() as connection:
            row = connection.execute(
                f"""
                SELECT {R2_SELECT_COLUMNS}
                FROM dss_simulation_histories_r2
                WHERE id = ? AND user_id = ?
                """,
                (history_id, user_id),
            ).fetchone()
        return self._row_to_r2(row) if row else None

    def delete_r2_by_id_and_user(self, history_id: str, user_id: str) -> bool:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                DELETE FROM dss_simulation_histories_r2
                WHERE id = ? AND user_id = ?
                """,
                (history_id, user_id),
            )
        return cursor.rowcount > 0

    # ------------------------------------------------------------------
    # Legacy — v1/v2/v3 read-only compatibility (pre-R2 semantics).
    # Isolated on purpose: never called by the R2 simulate path.
    # ------------------------------------------------------------------
    def list_legacy_by_user(
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

    def get_legacy_by_id_and_user(
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

    def delete_legacy_by_id_and_user(self, history_id: str, user_id: str) -> bool:
        """User-owned deletion of an immutable pre-R2 record."""
        with get_connection() as connection:
            cursor = connection.execute(
                """
                DELETE FROM dss_simulation_histories
                WHERE id = ? AND user_id = ?
                """,
                (history_id, user_id),
            )
        return cursor.rowcount > 0

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def new_id(self) -> str:
        return str(uuid4())

    def now(self) -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _row_to_r2(row: sqlite3.Row) -> R2HistorySnapshot:
        return R2HistorySnapshot(
            id=row["id"],
            user_id=row["user_id"],
            schema_version=row["schema_version"],
            model_version=row["model_version"],
            parameter_registry_version=row["parameter_registry_version"],
            model_commit_sha=row["model_commit_sha"],
            created_at=datetime.fromisoformat(row["created_at"]),
            request_json=row["request_json"],
            response_json=row["response_json"],
            trace_json=row["trace_json"],
            land_area_are=row["land_area_are"],
            duck_count=row["duck_count"],
            rice_variety=row["rice_variety"],
            planting_system=row["planting_system"],
            duck_age_days=row["duck_age_days"],
            planting_date=row["planting_date"],
            p_duck_buy_manual=row["p_duck_buy_manual"],
            p_duck_buy_effective=row["p_duck_buy_effective"],
            density_are=row["density_are"],
            age_support=row["age_support"],
            density_support=row["density_support"],
            extrapolation_status=row["extrapolation_status"],
            yield_availability=row["yield_availability"],
            survival_availability=row["survival_availability"],
            cost_completeness=row["cost_completeness"],
            yield_total_kg=row["yield_total_kg"],
            margin_core_rp=row["margin_core_rp"],
            profit_full_est_rp=row["profit_full_est_rp"],
        )

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
