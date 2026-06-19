import sqlite3
from pathlib import Path

from app.core.config import settings


def get_connection() -> sqlite3.Connection:
    database_path = Path(settings.database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS dss_simulation_histories (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                input_json TEXT NOT NULL,
                actual_scenario_json TEXT NOT NULL,
                recommended_scenario_json TEXT NOT NULL,
                comparison_json TEXT NOT NULL,
                risk_json TEXT NOT NULL,
                trace_json TEXT NOT NULL,
                notes_json TEXT NOT NULL,
                economics_json TEXT NOT NULL DEFAULT '{}',
                ecology_json TEXT NOT NULL DEFAULT '{}',
                environment_json TEXT NOT NULL DEFAULT '{}',
                lookup_json TEXT NOT NULL DEFAULT '{}',
                validation_json TEXT NOT NULL DEFAULT '{}',
                data_readiness_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_dss_histories_user_created
            ON dss_simulation_histories(user_id, created_at DESC);
            """
        )
        existing_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(dss_simulation_histories)"
            ).fetchall()
        }
        for column_name in (
            "economics_json",
            "ecology_json",
            "environment_json",
            "lookup_json",
            "validation_json",
            "data_readiness_json",
        ):
            if column_name not in existing_columns:
                connection.execute(
                    f"ALTER TABLE dss_simulation_histories "
                    f"ADD COLUMN {column_name} TEXT NOT NULL DEFAULT '{{}}'"
                )
