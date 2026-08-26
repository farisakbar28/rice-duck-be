"""Deterministic artifact generation: manifests, component statuses, report.

Everything derivable is DERIVED: formula groups come from
``app.engines.r2.FORMULA_IDS``, disabled legacy IDs and consumed parameter
keys come from the production service module, parameters are dumped from
``app.data.seed`` registries. Nothing scientific is hand-typed here.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from validation._bootstrap import REPO_ROOT
from validation.expert_transfer import EXPERT_TRANSFER_MATRIX, GLOBAL_NOTES
from validation.metrics import (
    YIELD_REASON_R2_UNAVAILABLE,
    YIELD_STATUS_NOT_EVALUABLE,
)
from validation.provenance import FreezeIdentity, GateResult
from validation.source_loader import (
    EMPIRICAL_SOURCE_STATUS_BLOCKED,
    ROLE_CLEAN_COHORT,
    ROLE_LEGACY_SIMULATION,
    SourceFile,
    empirical_source_status,
)

CANONICAL_ARTIFACTS = [
    "app/data/seed.py",
    "app/domain/models.py",
    "app/schemas/dss.py",
    "app/engines/r2/__init__.py",
    "app/engines/r2/config.py",
    "app/engines/r2/normalization.py",
    "app/engines/r2/support.py",
    "app/engines/r2/calendar.py",
    "app/engines/r2/survival.py",
    "app/engines/r2/yield_engine.py",
    "app/engines/r2/fertilizer.py",
    "app/engines/r2/infrastructure.py",
    "app/engines/r2/availability.py",
    "app/engines/r2/economics.py",
    "app/services/simulation_service.py",
    "app/services/visualization_service.py",
    "docs/01_R2_MODEL_SSOT.md",
    "docs/03_R2_API_CONTRACT.md",
    "docs/04_R2_PARAMETER_EXECUTION_REGISTRY.md",
    "docs/07_R2_LEGACY_INVALIDATION_REGISTER.md",
    "docs/10_R2_REFERENCE_PROVENANCE.md",
    "docs/11_R2_FREEZE_MANIFEST.md",
]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_artifact_hashes() -> dict[str, str]:
    hashes = {}
    for rel in CANONICAL_ARTIFACTS:
        path = REPO_ROOT / rel
        if path.is_file():
            hashes[rel] = sha256_file(path)
    return hashes


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parameter_dump() -> list[dict]:
    from app.data.seed import PARAMETER_REGISTRY

    dump = []
    for key, p in PARAMETER_REGISTRY.items():
        dump.append(
            {
                "key": key,
                "value": p.value,
                "minimum": p.minimum,
                "maximum": p.maximum,
                "unit": p.unit,
                "status_tag": p.status_tag.value,
                "execution_state": p.execution_state.value,
                "source_ids": list(p.source_ids),
                "model_version": p.model_version,
                "effective_from": p.effective_from,
            }
        )
    return dump


def _formula_registry_dump() -> dict:
    from app.engines.r2 import FORMULA_IDS
    from app.services.simulation_service import (
        _ALWAYS_ACTIVE_TRACE_GROUPS,
        _DISABLED_LEGACY_FORMULA_IDS,
    )

    return {
        "formula_ids_by_engine_group": {k: list(v) for k, v in FORMULA_IDS.items()},
        "always_active_trace_groups": list(_ALWAYS_ACTIVE_TRACE_GROUPS),
        "disabled_legacy_formula_ids": list(_DISABLED_LEGACY_FORMULA_IDS),
        "note": (
            "Per-request execution truth lives in each response trace "
            "(active/conditional lists); pending/unavailable branches never "
            "advertise execution."
        ),
    }


def build_freeze_manifest(
    identity: FreezeIdentity,
    gate: GateResult,
    backend_commit_sha: str | None,
    sources: dict[str, SourceFile],
    test_summary: dict,
) -> dict:
    from app.data.seed import PLANTING_SYSTEMS, RICE_VARIETIES

    manifest = {
        "freeze_id": identity.freeze_id,
        "model_version": identity.model_version,
        "parameter_registry_version": identity.parameter_registry_version,
        "backend_commit_sha": backend_commit_sha,
        "model_commit_sha_env_injected": identity.model_commit_sha_env,
        "app_version": identity.app_version,
        "history_schema_version": identity.history_schema_version,
        "execution_timestamp_utc": identity.execution_timestamp_utc,
        "python_version": identity.python_version,
        "model_frozen": identity.model_frozen,
        "freeze_effective_from": identity.freeze_effective_from,
        "frozen_semantics": (
            "immutable validation target; NOT empirical accuracy certification"
        ),
        "run_mode": gate.run_mode,
        "official_gate_failed_conditions": gate.failed_conditions,
        "formula_registry": _formula_registry_dump(),
        "parameters": _parameter_dump(),
        "rice_varieties": [
            {
                "code": v.code,
                "harvest_hst_min": v.harvest_hst_min,
                "harvest_hst_max": v.harvest_hst_max,
                "calendar_status": v.calendar_status.value,
                "yield_lookup_status": v.yield_lookup_status.value,
                "exact_cultivar_code": v.exact_cultivar_code,
            }
            for v in RICE_VARIETIES
        ],
        "planting_systems": [
            {
                "code": s.code,
                "supported_density_min_are": s.supported_density_min_are,
                "supported_density_max_are": s.supported_density_max_are,
            }
            for s in PLANTING_SYSTEMS
        ],
        "pending_unavailable_parameters": [
            p["key"]
            for p in _parameter_dump()
            if p["execution_state"] in ("PENDING_LOOKUP", "UNAVAILABLE")
        ],
        "yield_lookup_state": "PENDING_LOOKUP (Y_base + F_RD unpopulated)",
        "feed_lookup_state": "UNAVAILABLE",
        "cage_capacity_state": "UNAVAILABLE (total cost null)",
        "canonical_artifact_sha256": canonical_artifact_hashes(),
        "test_summary": test_summary,
        "source_fingerprints": [s.to_dict() for s in sources.values()],
        "no_secrets_note": "This manifest contains no secrets and no raw workbook contents.",
    }
    return manifest


# ---------------------------------------------------------------------------
# Component-level validation statuses
# ---------------------------------------------------------------------------


def build_component_eligibility(
    sources: dict[str, SourceFile], probe: dict
) -> dict:
    clean_present = sources[ROLE_CLEAN_COHORT].present
    source_status = empirical_source_status(sources)

    def comparator(n_key: str) -> dict:
        prior = {
            "yield_actual": "36/36",
            "paddy_price": "36/36",
            "positive_purchase_price": "29/36",
            "positive_feed_cost": "23/36",
            "positive_duck_sale_revenue": "16/36",
            "positive_net_infrastructure_proxy": "17/36",
            "positive_cage": "9/36",
            "positive_pesticide": "4/36",
            "positive_fertilizer": "1/36",
            "positive_weeding_cash": "0/36",
            "actual_duck_age": "0/36",
            "actual_active_duration": "0/36",
        }
        return {
            "prior_audit_coverage": prior[n_key],
            "recomputed_from_source": False,
            "source_status": source_status,
        }

    infra_compatible = False  # construct compatibility NOT established -> NO METRIC
    components = {
        "calendar": {
            "eligible_when_source_available": True,
            "status": "BLOCKED_SOURCE_FILES_MISSING" if not clean_present else "PENDING_EXECUTION",
            "metric_allowed": clean_present,
            "comparator": comparator("actual_active_duration"),
        },
        "yield": {
            "prediction_availability": probe["yield_availability"],
            "reason_codes": probe["yield_reason_codes"],
            "status": YIELD_STATUS_NOT_EVALUABLE,
            "reason": YIELD_REASON_R2_UNAVAILABLE,
            "metric_allowed": False,
            "comparator": comparator("yield_actual"),
        },
        "paddy_revenue_operational": {
            "status": YIELD_STATUS_NOT_EVALUABLE,
            "reason": YIELD_REASON_R2_UNAVAILABLE,
            "metric_allowed": False,
        },
        "paddy_revenue_price_neutral_diagnostic": {
            "status": YIELD_STATUS_NOT_EVALUABLE,
            "reason": YIELD_REASON_R2_UNAVAILABLE,
            "metric_allowed": False,
            "note": "historical prices may load as dataset metadata only, never runtime inputs",
        },
        "duck_purchase_cost_identity": {
            "status": "VERIFIED_BY_V1_TESTS",
            "metric_allowed": True,
            "note": "deterministic accounting identity; observed-price rows are plausibility context only",
            "comparator": comparator("positive_purchase_price"),
        },
        "survival_aggregate": {
            "ground_truth_status": "NO_COMPATIBLE_AGGREGATE",
            "metric_allowed": False,
        },
        "terminal_duck_value": {
            "comparison_against_duck_sales": "FORBIDDEN",
            "allowed": ["price plausibility", "min/ref/max sensitivity", "expert mapping"],
            "metric_allowed": False,
        },
        "feed_accuracy": {
            "runtime_availability": probe["feed_availability"],
            "status": YIELD_STATUS_NOT_EVALUABLE.replace(
                "NOT_EVALUABLE", "NOT_EVALUABLE_FEED_LOOKUP_MISSING"
            ),
            "metric_allowed": False,
            "comparator": comparator("positive_feed_cost"),
            "note": "positive historical feed values are future eligibility metadata only",
        },
        "weeding_cash": {"metric_allowed": False,
                         "comparator": comparator("positive_weeding_cash")},
        "pesticide": {"mode": "sparse case diagnostics only",
                      "metric_allowed": False,
                      "comparator": comparator("positive_pesticide")},
        "fertilizer": {"mode": "descriptive only",
                       "metric_allowed": False,
                       "comparator": comparator("positive_fertilizer")},
        "infrastructure_net_cage": {
            "semantic_compatibility_established": infra_compatible,
            "eligibility_reason": (
                "historical 'infra' proxies are ambiguous; square-equivalent net "
                "amortization and per-cycle cage totals cannot be assumed to match "
                "historical constructs" if not infra_compatible else "compatible"
            ),
            "metric_allowed": infra_compatible,
            "comparator": comparator("positive_net_infrastructure_proxy"),
        },
        "profit_margin": {
            "cost_completeness": probe["cost_completeness"],
            "profit_full_status": probe["profit_full_status"],
            "legacy_farmer_profit_comparison": "FORBIDDEN",
            "margin_core_vs_legacy_profit": "FORBIDDEN",
            "metric_allowed": False,
        },
    }
    legacy_role_guard = {
        "workbook": sources[ROLE_LEGACY_SIMULATION].filename,
        "present": sources[ROLE_LEGACY_SIMULATION].present,
        "never_used_as": [
            "R2 prediction source",
            "R2 input default",
            "parameter registry entry",
            "calibration coefficient",
        ],
    }
    return {
        "source_status": source_status,
        "components": components,
        "legacy_simulation_role_guard": legacy_role_guard,
    }


def build_yield_status_block(probe: dict, sources: dict[str, SourceFile]) -> dict:
    """Yield metrics derive from PRODUCTION AVAILABILITY STATE (task §23)."""
    unavailable = probe["yield_availability"] == "UNAVAILABLE"
    if not unavailable:  # defensive: harness refuses to exist in that world silently
        raise RuntimeError(
            "Production yield reported AVAILABLE; this harness version has no "
            "approved quantitative yield-validation protocol. Stop and run a "
            "new pre-freeze review before extending validation."
        )
    clean_present = sources[ROLE_CLEAN_COHORT].present
    return {
        "status": YIELD_STATUS_NOT_EVALUABLE,
        "reason": YIELD_REASON_R2_UNAVAILABLE,
        "actual_coverage": "36/36" if clean_present else "unverified_source_missing",
        "prediction_coverage": "0/36",
        "quantitative_metrics": None,
        "metrics_not_computed": ["MAE", "RMSE", "MedAE", "MBE", "WAPE", "MAPE",
                                 "R2", "release_scenario_envelope_coverage"],
        "derived_from_runtime_response_field": "yield.availability",
    }


def build_stress_block(sources: dict[str, SourceFile]) -> dict:
    clean_present = sources[ROLE_CLEAN_COHORT].present
    if not clean_present:
        return {
            "status": "BLOCKED_SOURCE_FILES_MISSING",
            "reason": "the 8 excluded/stress cycles are identifiable only from "
                      "the clean comparator workbook; they are never guessed",
            "assertions_when_executed": [
                "no crash", "no NaN", "no Infinity", "support/extrapolation "
                "semantics intact", "warnings emitted", "no hidden fallback",
            ],
            "merged_into_headline_metrics": False,
        }
    return {"status": "PENDING_MODE_B_EXECUTION"}


def render_validation_report_md(
    manifest: dict,
    fixture_manifest: dict,
    eligibility: dict,
    yield_block: dict,
    synthetic_records: list[dict],
    age_invariance: dict,
    v1: dict,
    stress_block: dict,
) -> str:
    ts = manifest["execution_timestamp_utc"]
    passed = sum(1 for r in synthetic_records if r["pass"])
    lines: list[str] = []
    add = lines.append
    add(f"# R2 Phase-5 Validation Report ({manifest['run_mode']})")
    add("")
    add(f"> Execution: {ts} | Python {manifest['python_version']} | "
        f"backend commit `{manifest['backend_commit_sha']}` | "
        f"registry `{manifest['parameter_registry_version']}` | "
        f"freeze_id `{manifest['freeze_id']}`")
    add("")
    if manifest["run_mode"] != "OFFICIAL_FROZEN_EXECUTION":
        add("**WATERMARK: NON_OFFICIAL / PRE_FREEZE — not an official frozen result.**")
        add(f"Failed official-gate conditions: {manifest['official_gate_failed_conditions']}")
        add("")
    add("## 1. Freeze identity")
    add(f"- model_version={manifest['model_version']} (unchanged)")
    add(f"- parameter_registry_version={manifest['parameter_registry_version']} (unchanged)")
    add(f"- history schema={manifest['history_schema_version']}; app_version={manifest['app_version']}")
    add(f"- MODEL_FROZEN={manifest['model_frozen']}, FREEZE_ID={manifest['freeze_id']}, "
        f"FREEZE_EFFECTIVE_FROM={manifest['freeze_effective_from']}")
    add("- frozen means *immutable validation target*; it does NOT mean empirically "
        "validated, accurate, or complete.")
    add("")
    add("## 2. Source fingerprints")
    for src in manifest["source_fingerprints"]:
        add(f"- {src['role']}: {src['filename']} — {src['status']}"
            + (f", sha256={src['sha256']}" if src["sha256"] else ""))
    add("")
    add("## 3. Dataset/cohort status")
    add(f"- empirical_source_status = {fixture_manifest['empirical_source_status']}")
    cohorts = fixture_manifest["cohort_metadata"]
    for name, state in cohorts.items():
        add(f"- {name}: expected(prior audit)={state['expected_from_prior_audit']}, "
            f"verified={state['verified_from_source']}, status={state['status']}")
    add("")
    add("## 4. V1 computational verification")
    add(f"- all_pass = {v1['all_pass']}; items = {len(v1['items'])} "
        f"(docs/06 §19 matrix mapped to active tests)")
    add("")
    add("## 5. Synthetic runtime evidence (B01–B18)")
    add(f"- passed {passed}/{len(synthetic_records)} via canonical HTTP path; "
        f"raw responses archived in synthetic_cases.json")
    add(f"- supported-age invariance (21 vs 30): pass={age_invariance['pass']} "
        f"differing_paths={age_invariance['differing_paths']}")
    add("- Synthetic cases are contract evidence, NOT field observations.")
    add("")
    add("## 6. Calendar comparator")
    cal = eligibility["components"]["calendar"]
    add(f"- status={cal['status']}; eligible rows require OBSERVED planting AND harvest dates")
    add("- Prior-audit expectation N=12 must be recomputed from source before any metric.")
    add("")
    yb = yield_block
    add("## 7. Yield status")
    add(f"- status={yb['status']}; reason={yb['reason']}; "
        f"actual_coverage={yb['actual_coverage']}; prediction_coverage={yb['prediction_coverage']}; "
        f"quantitative_metrics=None")
    add("")
    add("## 8. Revenue status")
    add("- operational paddy revenue = NOT_EVALUABLE (yield unavailable); "
        "price-neutral diagnostic = NOT_EVALUABLE. No zero-residual substitution.")
    add("")
    add("## 9. Survival status")
    add("- ground_truth_status=NO_COMPATIBLE_AGGREGATE; no MAE/RMSE; sold ducks are "
        "never survival actuals. V1 gate + expert transfer only.")
    add("")
    add("## 10. Purchase-cost status")
    add("- deterministic identity verified by V1 tests; observed historical prices are "
        "plausibility/comparator context; default-price rows excluded from observed comparators.")
    add("")
    add("## 11. Feed status")
    add("- runtime UNAVAILABLE -> no accuracy metric; positive historical feed counts "
        "reported as coverage metadata only.")
    add("")
    add("## 12. Infrastructure status")
    inf = eligibility["components"]["infrastructure_net_cage"]
    add(f"- semantic_compatibility_established={inf['semantic_compatibility_established']} "
        f"-> metric_allowed={inf['metric_allowed']}; reason: {inf['eligibility_reason']}")
    add("")
    add("## 13. Weed/pest/fertilizer status")
    add("- weeding: no monetary accuracy metric; pesticide: sparse case diagnostics; "
        "fertilizer: descriptive only. Small N never promoted to aggregate validation.")
    add("")
    add("## 14. Profit/margin status")
    add("- no comparison of historical farmer profit with Margin_core/Profit_full_est; "
        f"cost_completeness={eligibility['components']['profit_margin']['cost_completeness']} -> "
        "Profit_full_est null by design.")
    add("")
    add("## 15. Stress-test status")
    add(f"- {stress_block['status']}" + (
        f"; reason: {stress_block.get('reason','')}" if "reason" in stress_block else ""))
    add("")
    add("## 16. Expert-transfer summary")
    counts: dict[str, int] = {}
    for item in EXPERT_TRANSFER_MATRIX:
        counts[item["transfer"]] = counts.get(item["transfer"], 0) + 1
    add(f"- labels: {counts} over {len(EXPERT_TRANSFER_MATRIX)} items "
        "(see expert_transfer.json); global notes: " + " ".join(GLOBAL_NOTES))
    add("")
    add("## 17. Limitations")
    add("- yield/feed/cage-total/full-profit unavailable by design; comparator workbooks "
        "partially missing; strict-domain N=17 and calendar N=12 remain unverified hypotheses.")
    add("")
    add("## 18. No-recalibration declaration")
    add("- no fitting/optimization/calibration workflow exists in this package "
        "(statically guarded by tests/test_validation_isolation.py); no seed/engine/"
        "SSOT coefficient was modified during validation; discrepancies are reported, "
        "never tuned away.")
    add("")
    add("## 19. Component-specific conclusions")
    add("- Computational implementation: VERIFIED (V1 100%)" if v1["all_pass"]
        else "- Computational implementation: FAILED INVESTIGATION REQUIRED")
    add("- Calendar: quantitatively evaluable only after source verification (blocked).")
    add("- Yield: NOT EVALUABLE — lookup unavailable (hard gate).")
    add("- Survival: no aggregate ground truth; deterministic + expert evidence only.")
    add("- Feed: not evaluable. Infrastructure: limited/conditional. Full profit: not evaluable.")
    add("- No universal accuracy score exists in this report.")
    return "\n".join(lines) + "\n"


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def new_run_id(head: str | None) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}_{(head or 'nohead')[:7]}"


__all__ = [
    "build_component_eligibility",
    "build_fixture_manifest_ref",
    "build_freeze_manifest",
    "build_stress_block",
    "build_yield_status_block",
    "new_run_id",
    "render_validation_report_md",
    "write_json",
]


def build_fixture_manifest_ref(fixture_manifest: dict) -> dict:  # re-export shim
    return fixture_manifest
