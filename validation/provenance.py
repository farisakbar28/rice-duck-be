"""Freeze identity, Git state, and the official-execution gate (task §4/§36).

The runner derives every identity value from canonical sources at execution
time; nothing is hand-typed. ``backend_commit_sha`` is the ACTUAL clean HEAD
observed by this process, distinct from the deployment-injected
``settings.model_commit_sha``.
"""

from __future__ import annotations

import platform
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from validation._bootstrap import REPO_ROOT

EXPECTED_PARAMETER_REGISTRY_VERSION = "R2-2026-08-26.3"
PHASE4_BASELINE_COMMIT = "39fd69fbfa207862ce4da5be5d4f75e06eed6bdb"

RUN_MODE_OFFICIAL = "OFFICIAL_FROZEN_EXECUTION"
RUN_MODE_PRE_FREEZE = "NON_OFFICIAL_PRE_FREEZE"


@dataclass(frozen=True)
class FreezeIdentity:
    model_version: str
    parameter_registry_version: str
    freeze_id: str | None
    model_frozen: bool
    freeze_effective_from: str | None
    model_commit_sha_env: str | None
    app_version: str
    history_schema_version: int
    python_version: str
    execution_timestamp_utc: str


@dataclass(frozen=True)
class GateResult:
    official: bool
    run_mode: str
    failed_conditions: list[str] = field(default_factory=list)


def load_freeze_identity() -> FreezeIdentity:
    # Imported lazily AFTER _bootstrap configured the environment.
    from app.core.config import settings
    from app.data.seed import (
        FREEZE_EFFECTIVE_FROM,
        FREEZE_ID,
        MODEL_FROZEN,
        MODEL_VERSION,
        PARAMETER_REGISTRY_VERSION,
    )

    return FreezeIdentity(
        model_version=MODEL_VERSION,
        parameter_registry_version=PARAMETER_REGISTRY_VERSION,
        freeze_id=FREEZE_ID,
        model_frozen=MODEL_FROZEN,
        freeze_effective_from=FREEZE_EFFECTIVE_FROM,
        model_commit_sha_env=settings.model_commit_sha,
        app_version=settings.app_version,
        history_schema_version=4,
        python_version=platform.python_version(),
        execution_timestamp_utc=datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
    )


def git_head(root: Path = REPO_ROOT) -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def git_status_porcelain(root: Path = REPO_ROOT) -> str:
    try:
        out = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout
    except (OSError, subprocess.CalledProcessError):
        return "<git-unavailable>"


def is_tree_clean(root: Path = REPO_ROOT) -> bool:
    status = git_status_porcelain(root)
    return status == "" and status != "<git-unavailable>"


def evaluate_official_gate(
    identity: FreezeIdentity,
    *,
    head: str | None,
    tree_clean: bool,
    tests_passed: bool,
    source_discovery_executed: bool,
    source_fingerprints_valid: bool = False,
    cohort_reconstruction_successful: bool = False,
    source_version_mismatch: bool = False,
) -> GateResult:
    """Task §36: ALL conditions must hold for OFFICIAL artifacts."""
    failed: list[str] = []
    if not tree_clean:
        failed.append("OFFICIAL_VALIDATION_BLOCKED_DIRTY_TREE")
    if not head:
        failed.append("GIT_HEAD_UNRESOLVABLE")
    if not identity.model_frozen:
        failed.append("MODEL_FROZEN_IS_FALSE")
    if not identity.freeze_id:
        failed.append("FREEZE_ID_NOT_SET")
    if not tests_passed:
        failed.append("ACTIVE_TEST_SUITE_NOT_PASSING")
    if identity.parameter_registry_version != EXPECTED_PARAMETER_REGISTRY_VERSION:
        failed.append(
            f"REGISTRY_VERSION_MISMATCH expected="
            f"{EXPECTED_PARAMETER_REGISTRY_VERSION} "
            f"actual={identity.parameter_registry_version}"
        )
    if not source_discovery_executed:
        failed.append("SOURCE_DISCOVERY_NOT_EXECUTED")
    if not source_fingerprints_valid:
        failed.append("SOURCE_FINGERPRINTS_INVALID_OR_MISSING")
    if source_version_mismatch:
        failed.append("SOURCE_VERSION_MISMATCH")
    if not cohort_reconstruction_successful:
        failed.append("COHORT_RECONSTRUCTION_NOT_VERIFIED")
    official = not failed
    return GateResult(
        official=official,
        run_mode=RUN_MODE_OFFICIAL if official else RUN_MODE_PRE_FREEZE,
        failed_conditions=failed,
    )
