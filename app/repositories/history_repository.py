import json
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4

from app.core.database import get_connection
from app.domain.models import SimulationHistory


class HistoryRepository:
    def create(
        self,
        *,
        user_id: str,
        input_data: dict,
        actual_scenario: dict,
        recommended_scenario: dict,
        comparison: dict,
        risk: dict,
        trace: dict,
        notes: list[str],
        economics: dict,
        ecology: dict,
        environment: dict,
        lookup: dict,
        validation: dict,
        data_readiness: dict,
    ) -> SimulationHistory:
        history = SimulationHistory(
            id=str(uuid4()),
            user_id=user_id,
            input_data=input_data,
            actual_scenario=actual_scenario,
            recommended_scenario=recommended_scenario,
            comparison=comparison,
            risk=risk,
            trace=trace,
            notes=notes,
            economics=economics,
            ecology=ecology,
            environment=environment,
            lookup=lookup,
            validation=validation,
            data_readiness=data_readiness,
            created_at=datetime.now(timezone.utc),
        )
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO dss_simulation_histories (
                    id, user_id, input_json, actual_scenario_json,
                    recommended_scenario_json, comparison_json, risk_json,
                    trace_json, notes_json, economics_json, ecology_json,
                    environment_json, lookup_json, validation_json,
                    data_readiness_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    history.id,
                    history.user_id,
                    json.dumps(history.input_data),
                    json.dumps(history.actual_scenario),
                    json.dumps(history.recommended_scenario),
                    json.dumps(history.comparison),
                    json.dumps(history.risk),
                    json.dumps(history.trace),
                    json.dumps(history.notes),
                    json.dumps(history.economics),
                    json.dumps(history.ecology),
                    json.dumps(history.environment),
                    json.dumps(history.lookup),
                    json.dumps(history.validation),
                    json.dumps(history.data_readiness),
                    history.created_at.isoformat(),
                ),
            )
        return history

    def list_by_user(self, user_id: str) -> list[SimulationHistory]:
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
    ) -> SimulationHistory | None:
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

    def _to_model(self, row: sqlite3.Row) -> SimulationHistory:
        return SimulationHistory(
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
        )


history_repository = HistoryRepository()
