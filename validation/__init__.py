"""Rice-Duck R2 Phase-6 research-only validation harness.

ISOLATION CONTRACT (task §7, docs/11):
  * This package is research tooling ONLY. No module under ``app/`` may import
    it (guarded by tests/test_validation_isolation.py).
  * It reads canonical registries through the public ``app.data.seed`` surface
    and executes predictions exclusively through the real FastAPI application
    (TestClient). It never reimplements scientific formulas and never writes
    model parameters.
  * Empirical comparator workbooks are loaded only from the explicitly
    configured source directory (R2_VALIDATION_SOURCE_DIR / --source-dir).
"""

__all__ = [
    "_bootstrap",
    "cli",
    "expert_transfer",
    "fixture_builder",
    "metrics",
    "provenance",
    "report",
    "runtime_runner",
    "source_loader",
]
