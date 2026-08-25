import sqlite3
from pathlib import Path

from app.core.config import settings


# legacy-compat-region: v3 columns (do not scan numerics) -- START
# v3 explicit columns — pre-R2 SoT FINAL (INVALIDATED for R2; docs/07).
# schema_version=3 rows are immutable historical records that stay readable.
# R2 simulations NEVER write here: they go to ``dss_simulation_histories_r2``.
# The legacy default values below (65 / 44 / 0 ...) belong to the invalidated
# pre-R2 point-calendar model and are retained ONLY so old rows/columns keep
# working; they are not R2 values.
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
# legacy-compat-region: v3 columns -- END

# R2 persistence v4 (docs/05_R2_PERSISTENCE_VERSIONING.md).
# Scientific/economic unknowns are SQL NULL -- never NOT NULL DEFAULT 0.
HISTORY_R2_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS dss_simulation_histories_r2 (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    schema_version INTEGER NOT NULL DEFAULT 4,
    model_version TEXT NOT NULL,
    parameter_registry_version TEXT NOT NULL,
    model_commit_sha TEXT,
    created_at TEXT NOT NULL,

    request_json TEXT NOT NULL,
    response_json TEXT NOT NULL,
    trace_json TEXT NOT NULL,

    land_area_are REAL NOT NULL,
    duck_count INTEGER NOT NULL,
    rice_variety TEXT NOT NULL,
    planting_system TEXT NOT NULL,
    duck_age_days INTEGER NOT NULL,
    planting_date TEXT NOT NULL,
    p_duck_buy_manual REAL,
    p_duck_buy_effective REAL NOT NULL,

    density_are REAL NOT NULL,
    age_support TEXT NOT NULL,
    density_support TEXT NOT NULL,
    extrapolation_status TEXT NOT NULL,
    yield_availability TEXT NOT NULL,
    survival_availability TEXT NOT NULL,
    cost_completeness TEXT NOT NULL,

    yield_total_kg REAL,
    margin_core_rp REAL,
    profit_full_est_rp REAL,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

HISTORY_R2_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_dss_r2_user_created
ON dss_simulation_histories_r2(user_id, created_at DESC);
"""


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

        # R2 persistence v4 -- independent, idempotent creation. The legacy
        # table above is never destructively altered and old rows are never
        # rewritten; the new table simply coexists (docs/05 section 8).
        connection.executescript(HISTORY_R2_TABLE_SQL)
        connection.executescript(HISTORY_R2_INDEX_SQL)
