import sqlite3
from pathlib import Path

from app.core.config import settings


# Columns added by Fase 5 (explicit-column migration). The history table
# originally stored everything as JSON blobs; rows written before this
# migration keep ``schema_version=1`` and remain read-only legacy.
HISTORY_V2_COLUMNS = (
    # Agronomi & operasional
    "density_status TEXT NOT NULL DEFAULT ''",
    "age_status TEXT NOT NULL DEFAULT ''",
    "d_masuk_bebek TEXT NOT NULL DEFAULT ''",
    "d_tarik_bebek TEXT NOT NULL DEFAULT ''",
    "d_panen_gabah TEXT NOT NULL DEFAULT ''",
    "n_survive REAL NOT NULL DEFAULT 0",
    # Yield
    "yield_are_predict REAL NOT NULL DEFAULT 0",
    "yield_total_predict REAL NOT NULL DEFAULT 0",
    # Revenue
    "revenue_gabah REAL NOT NULL DEFAULT 0",
    "revenue_duck REAL NOT NULL DEFAULT 0",
    "total_revenue REAL NOT NULL DEFAULT 0",
    # Cost detail
    "cost_duck_buy REAL NOT NULL DEFAULT 0",
    "cost_feed REAL NOT NULL DEFAULT 0",
    "cost_labor_base REAL NOT NULL DEFAULT 0",
    "cost_labor_weed_hired REAL NOT NULL DEFAULT 0",
    # DEPRECATED (lihat FINAL_BANGET.md Catatan Finalisasi poin 12):
    # dihapus dari formula Cost Engine sejak 2026-07-07. Kolom dipertahankan
    # di DB untuk backward compatibility historical records, nilai selalu 0.0,
    # TIDAK di-expose di API response.
    "cost_labor_tending REAL NOT NULL DEFAULT 0",
    "cost_labor_total REAL NOT NULL DEFAULT 0",
    "cost_infra_net REAL NOT NULL DEFAULT 0",
    "cost_infra_cage REAL NOT NULL DEFAULT 0",
    "cost_infra_total REAL NOT NULL DEFAULT 0",
    "cost_fert_urea REAL NOT NULL DEFAULT 0",
    "cost_fert_phonska REAL NOT NULL DEFAULT 0",
    "cost_fert_kcl REAL NOT NULL DEFAULT 0",
    "cost_fertilizer_total REAL NOT NULL DEFAULT 0",
    "cost_pesticide REAL NOT NULL DEFAULT 0",
    "cost_total_cash REAL NOT NULL DEFAULT 0",
    # Profit
    "profit_net_cash REAL NOT NULL DEFAULT 0",
    "valuation_weed_eco REAL NOT NULL DEFAULT 0",
    "profit_net_full REAL NOT NULL DEFAULT 0",
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
                -- Legacy JSON blobs (kept for backward-compat with old rows).
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
                -- Fase 5: explicit columns + schema_version.
                -- 1 = legacy JSON-only row (backward-compat read).
                -- 2 = explicit-column row written by /dss/simulate.
                schema_version INTEGER NOT NULL DEFAULT 1,
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
        for column_def in (
            "economics_json",
            "ecology_json",
            "environment_json",
            "lookup_json",
            "validation_json",
            "data_readiness_json",
            "schema_version",
        ):
            if column_def not in existing_columns:
                if column_def == "schema_version":
                    connection.execute(
                        "ALTER TABLE dss_simulation_histories "
                        "ADD COLUMN schema_version INTEGER NOT NULL DEFAULT 1"
                    )
                else:
                    connection.execute(
                        f"ALTER TABLE dss_simulation_histories "
                        f"ADD COLUMN {column_def} TEXT NOT NULL DEFAULT '{{}}'"
                    )
        # Re-fetch after ALTER.
        existing_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(dss_simulation_histories)"
            ).fetchall()
        }
        for column_def in HISTORY_V2_COLUMNS:
            column_name = column_def.split()[0]
            if column_name not in existing_columns:
                connection.execute(
                    f"ALTER TABLE dss_simulation_histories ADD COLUMN {column_def}"
                )
