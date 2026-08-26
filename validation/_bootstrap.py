"""Runtime-environment bootstrap for the research harness.

MUST be imported before anything under ``app/`` so the isolated validation
environment (ephemeral secret, dedicated SQLite file, relaxed test hashing)
is in place before ``app.core.config.Settings`` instantiates. The production
database under ``data/`` is never touched: validation uses its own DB file in
the gitignored ``validation/local/`` directory.
"""

from __future__ import annotations

import os
import secrets
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LOCAL_DIR = REPO_ROOT / "validation" / "local"
VALIDATION_DB_PATH = LOCAL_DIR / "rice_duck_validation.db"


def configure_runtime_env() -> Path:
    """Prepare an isolated runtime env; return the local scratch directory."""
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("APP_ENV", "test")
    # Ephemeral per-process secret; never written to disk or artifacts.
    os.environ.setdefault("JWT_SECRET_KEY", secrets.token_hex(32))
    os.environ.setdefault("PASSWORD_HASH_ITERATIONS", "1000")
    os.environ["DATABASE_PATH"] = str(VALIDATION_DB_PATH)
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    return LOCAL_DIR
