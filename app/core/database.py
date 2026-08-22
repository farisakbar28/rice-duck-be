import sqlite3
from pathlib import Path

from app.core.config import settings


# v3 explicit columns — SoT FINAL
# schema_version=3 rows written by /dss/simulate (authenticated)
# schema_version<=2 legacy rows remain readable via SimulationHistoryLegacy
HISTORY_V3_COLUMNS = (
    # Input snapshot
    "land_area_are REAL NOT NULL DEFAULT 0",
    "duck_count INTEGER NOT NULL DEFAULT 0",
    "rice_variety TEXT NOT NULL DEFAULT ''",
    "planting_system TEXT NOT NULL DEFAULT ''",
    "duck_age_days INTEGER NOT NULL DEFAULT 0",
    "planting_date TEXT NOT NULL DEFAULT ''",
    "p_duck_buy REAL NOT NULL DEFAULT 0",
    # Age Engine (SoT §4)
    "age_flag TEXT NOT NULL DEFAULT ''",
    # Density Engine (SoT §5)
    "density_are REAL NOT NULL DEFAULT 0",
    "density_ha REAL NOT NULL DEFAULT 0",
    "density_status TEXT NOT NULL DEFAULT ''",
    # Calendar Engine (SoT §6)
    "hst_in INTEGER NOT NULL DEFAULT 21",
    "hst_out INTEGER NOT NULL DEFAULT 65",
    "t_active INTEGER NOT NULL DEFAULT 44",
    "d_in TEXT NOT NULL DEFAULT ''",
    "d_out TEXT NOT NULL DEFAULT ''",
    "harvest_hst_min INTEGER NOT NULL DEFAULT 0",
    "harvest_hst_max INTEGER NOT NULL DEFAULT 0",
    "d_panen_min TEXT NOT NULL DEFAULT ''",
    "d_panen_max TEXT NOT NULL DEFAULT ''",
    # Survival Engine (SoT §7)
    "n_survive INTEGER NOT NULL DEFAULT 0",
    # Yield Engine (SoT §8)
    "yield_are_pred REAL NOT NULL DEFAULT 0",
    "yield_total_pred REAL NOT NULL DEFAULT 0",
    # Core Economics (SoT §9)
    "revenue_gabah REAL NOT NULL DEFAULT 0",
    "revenue_duck_potential REAL NOT NULL DEFAULT 0",
    "cost_duck_buy REAL NOT NULL DEFAULT 0",
    "cost_feed REAL NOT NULL DEFAULT 0",
    "core_cash_cost REAL NOT NULL DEFAULT 0",
    "total_revenue_dss REAL NOT NULL DEFAULT 0",
    "net_cash_contribution_dss REAL NOT NULL DEFAULT 0",
    # Warnings
    "warnings_json TEXT NOT NULL DEFAULT '[]'",
)


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
                -- Legacy JSON blobs (kept for backward-compat with v1/v2 rows).
                input_json TEXT NOT NULL DEFAULT '{}',
                actual_scenario_json TEXT NOT NULL DEFAULT '{}',
                recommended_scenario_json TEXT NOT NULL DEFAULT '{}',
                comparison_json TEXT NOT NULL DEFAULT '{}',
                risk_json TEXT NOT NULL DEFAULT '{}',
                trace_json TEXT NOT NULL DEFAULT '{}',
                notes_json TEXT NOT NULL DEFAULT '[]',
                economics_json TEXT NOT NULL DEFAULT '{}',
                ecology_json TEXT NOT NULL DEFAULT '{}',
                environment_json TEXT NOT NULL DEFAULT '{}',
                lookup_json TEXT NOT NULL DEFAULT '{}',
                validation_json TEXT NOT NULL DEFAULT '{}',
                data_readiness_json TEXT NOT NULL DEFAULT '{}',
                -- schema_version: 1/2=legacy JSON, 3=v3 explicit columns (SoT FINAL)
                schema_version INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_dss_histories_user_created
            ON dss_simulation_histories(user_id, created_at DESC);
            """
        )
        # Add missing legacy JSON columns
        existing_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(dss_simulation_histories)"
            ).fetchall()
        }
        for col_name, col_def in [
            ("economics_json", "TEXT NOT NULL DEFAULT '{}'"),
            ("ecology_json", "TEXT NOT NULL DEFAULT '{}'"),
            ("environment_json", "TEXT NOT NULL DEFAULT '{}'"),
            ("lookup_json", "TEXT NOT NULL DEFAULT '{}'"),
            ("validation_json", "TEXT NOT NULL DEFAULT '{}'"),
            ("data_readiness_json", "TEXT NOT NULL DEFAULT '{}'"),
            ("schema_version", "INTEGER NOT NULL DEFAULT 1"),
        ]:
            if col_name not in existing_columns:
                connection.execute(
                    f"ALTER TABLE dss_simulation_histories ADD COLUMN {col_name} {col_def}"
                )

        # Re-fetch after potential ALTER
        existing_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(dss_simulation_histories)"
            ).fetchall()
        }

        # Add v3 columns
        for column_def in HISTORY_V3_COLUMNS:
            column_name = column_def.split()[0]
            if column_name not in existing_columns:
                connection.execute(
                    f"ALTER TABLE dss_simulation_histories ADD COLUMN {column_def}"
                )
