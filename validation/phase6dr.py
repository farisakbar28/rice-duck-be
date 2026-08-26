"""Phase-6D-R provenance correction and corrected evidence runner.

The runner first writes and reloads the row-level semantic adjudication.  Only
then does it apply the endpoint-specific yield policy to the already-frozen
Phase-6 runtime evidence.  It never changes production science and never
rewrites the original official run directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Any

from validation._bootstrap import REPO_ROOT, configure_runtime_env

configure_runtime_env()

from validation.comparators import (  # noqa: E402
    build_purchase_comparator,
    build_revenue_diagnostics,
)
from validation.metrics import (  # noqa: E402
    cluster_bootstrap_metric_intervals,
    phase6_yield_metrics,
    phase6_yield_subgroups,
    revenue_metrics,
)
from validation.provenance import git_head  # noqa: E402
from validation.source_loader import (  # noqa: E402
    ROLE_CLEAN_COHORT,
    ROLE_RAW_RECAP,
    discover_sources,
)
from validation.workbook_parser import reconstruct_cohorts  # noqa: E402
from validation.yield_adjudication import (  # noqa: E402
    adjudication_index,
    build_yield_actual_adjudication,
    evaluate_yield_actual_eligibility,
)


SCIENTIFIC_TARGET_SHA = "b10b0a1f83357c5db1d6cdfb9c41eaa84b6727a7"
ORIGINAL_OFFICIAL_RUN_ID = "20260826T202953Z_b10b0a1"
ORIGINAL_HARNESS_SHA = "0eafa61e8ee5e6c62f41a12e86a1a8dadb035c21"
PROTOCOL_SOURCE_SHA = "7c329403e8b6325760513b7f2f50e93c1d3259f9"
CORRECTION_DIR_NAME = f"{ORIGINAL_OFFICIAL_RUN_ID}_phase6dr"

SCIENTIFIC_DIFF_PATHS = (
    "app",
    "docs/01_R2_MODEL_SSOT.md",
    "docs/02_R2_ENGINE_SPEC.md",
    "docs/04_R2_PARAMETER_EXECUTION_REGISTRY.md",
    "docs/10_R2_REFERENCE_PROVENANCE.md",
)
HARNESS_IDENTITY_PATHS = (
    "validation/comparators.py",
    "validation/yield_adjudication.py",
    "validation/phase6dr.py",
    "tests/test_phase6dr_adjudication.py",
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _directory_sha256_manifest(path: Path) -> dict[str, str]:
    return {
        item.relative_to(path).as_posix(): _sha256_file(item)
        for item in sorted(path.rglob("*"))
        if item.is_file()
    }


def _git_name_only(root: Path, target: str, paths: tuple[str, ...]) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", target, "--", *paths],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _git_blob_sha(root: Path, target: str, path: str) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", f"{target}:{path}"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _scientific_diff_audit(root: Path = REPO_ROOT) -> dict[str, Any]:
    changed_paths = _git_name_only(root, SCIENTIFIC_TARGET_SHA, SCIENTIFIC_DIFF_PATHS)
    current_hashes: dict[str, str | None] = {}
    target_hashes: dict[str, str | None] = {}
    for path_text in SCIENTIFIC_DIFF_PATHS:
        path = root / path_text
        if path.is_file():
            current_hashes[path_text] = _sha256_file(path)
        elif path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file() and "__pycache__" not in child.parts and child.suffix in {
                    ".py",
                    ".md",
                }:
                    relative = child.relative_to(root).as_posix()
                    current_hashes[relative] = _sha256_file(child)
        target_blob = _git_blob_sha(root, SCIENTIFIC_TARGET_SHA, path_text)
        if target_blob is not None:
            target_hashes[path_text] = target_blob
    return {
        "scientific_target_sha": SCIENTIFIC_TARGET_SHA,
        "guard_paths": list(SCIENTIFIC_DIFF_PATHS),
        "changed_paths": changed_paths,
        "scientific_parameter_or_equation_change": bool(changed_paths),
        "current_file_sha256": current_hashes,
        "target_blob_sha": target_hashes,
        "pass": not changed_paths,
        "interpretation": (
            "No app or locked scientific SSOT/engine/registry/provenance file "
            "diff is attributable to the validation correction."
            if not changed_paths
            else "Scientific diff guard failed; corrected metrics must not execute."
        ),
    }


def _working_harness_sha(root: Path = REPO_ROOT) -> str:
    digest = hashlib.sha256()
    for relative in HARNESS_IDENTITY_PATHS:
        path = root / relative
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _run_qa_command(root: Path, arguments: list[str]) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, *arguments],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    output = "\n".join(
        part for part in (result.stdout.strip(), result.stderr.strip()) if part
    )
    return {
        "command": [sys.executable, *arguments],
        "exit_code": result.returncode,
        "passed": result.returncode == 0,
        "output_tail": "\n".join(output.splitlines()[-40:]),
    }


def _run_required_qa(root: Path = REPO_ROOT) -> dict[str, Any]:
    commands = [
        _run_qa_command(root, ["-m", "pytest", "--collect-only", "-q"]),
        _run_qa_command(root, ["-m", "pytest", "-q"]),
        _run_qa_command(root, ["-m", "compileall", "app", "validation"]),
    ]
    return {
        "commands": commands,
        "all_passed": all(command["passed"] for command in commands),
    }


def _apply_adjudication_to_frozen_rows(
    original_rows: list[dict[str, Any]],
    clean_records: tuple[dict[str, Any], ...],
    adjudication: dict[str, Any],
) -> list[dict[str, Any]]:
    clean_by_row = {int(row["source_row"]): row for row in clean_records}
    adjudicated_by_row = adjudication_index(adjudication)
    corrected_rows: list[dict[str, Any]] = []
    for original in original_rows:
        source_row = int(original["source_row"])
        clean_record = clean_by_row.get(source_row)
        if clean_record is None:
            raise ValueError(f"clean source row missing from reconstruction: {source_row}")
        provenance = original.get("actual_yield_provenance")
        adjudication_record = adjudicated_by_row.get(source_row)
        actual = clean_record.get("actual_yield_kg_per_are")
        if adjudication_record is not None and adjudication_record.get("actual_numeric_value") is not None:
            actual = adjudication_record["actual_numeric_value"]
        decision = evaluate_yield_actual_eligibility(
            provenance,
            actual,
            derived_actual_admissibility=(
                adjudication_record.get("derived_actual_admissibility")
                if adjudication_record is not None
                else None
            ),
        )
        row = dict(original)
        row.update(
            {
                "actual_before_correction": original.get("actual"),
                "actual_source_value": actual,
                "actual": actual if decision["eligible"] else None,
                "actual_yield": actual if decision["eligible"] else None,
                "actual_provenance": provenance,
                "derived_actual_admissibility": decision[
                    "derived_actual_admissibility"
                ],
                "actual_comparator_eligible": decision["eligible"],
                "actual_adjudication_reason": decision["reason"],
                "adjudication_artifact_record_present": adjudication_record is not None,
                "scientific_target_sha": SCIENTIFIC_TARGET_SHA,
            }
        )
        corrected_rows.append(row)
    return corrected_rows


def build_corrected_yield_validation(
    original_validation: dict[str, Any],
    clean_records: tuple[dict[str, Any], ...],
    adjudication: dict[str, Any],
) -> dict[str, Any]:
    """Apply the frozen run's predictions to the frozen semantic decisions."""
    corrected_rows = _apply_adjudication_to_frozen_rows(
        list(original_validation.get("rows", [])), clean_records, adjudication
    )
    metrics = phase6_yield_metrics(corrected_rows)
    metrics["http_execution_failure_n"] = sum(
        bool(row.get("http_execution_failure")) for row in corrected_rows
    )
    metrics["scientific_unavailable_n"] = sum(
        row.get("prediction_status") == "SCIENTIFIC_UNAVAILABLE"
        for row in corrected_rows
    )
    return {
        **original_validation,
        "status": "EVALUATED" if metrics["N_predicted"] else "NOT_EVALUABLE",
        "reason": None if metrics["N_predicted"] else "NO_ELIGIBLE_PREDICTED_ROWS",
        "correction_layer": "PHASE_6D_R_YIELD_PROVENANCE_ADJUDICATION",
        "runtime_science_reused_from_original_run": True,
        "model_rerun": False,
        "rows": corrected_rows,
        "metrics": metrics,
        "subgroups": phase6_yield_subgroups(corrected_rows),
        "cluster_bootstrap": cluster_bootstrap_metric_intervals(corrected_rows),
        "adjudication_artifact": {
            "path": "yield_actual_provenance_adjudication.json",
            "scientific_target_sha": SCIENTIFIC_TARGET_SHA,
            "admissible_derived_actual_n": adjudication[
                "admissible_derived_actual_n"
            ],
        },
    }


def _direct_yield_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    actual_eligible = [row for row in rows if row.get("actual") is not None]
    eligible = [
        row
        for row in actual_eligible
        if all(row.get(key) is not None for key in ("pred_ref", "pred_low", "pred_high"))
    ]
    coverage = len(eligible) / len(actual_eligible) if actual_eligible else None
    base = {
        "N_total_actual_eligible": len(actual_eligible),
        "N_actual_eligible": len(actual_eligible),
        "N_predicted": len(eligible),
        "prediction_coverage_fraction": coverage,
        "prediction_coverage_percent": coverage * 100 if coverage is not None else None,
        "prediction_coverage": coverage,
        "http_execution_failure_n": sum(
            bool(row.get("http_execution_failure")) for row in rows
        ),
        "scientific_unavailable_n": sum(
            row.get("prediction_status") == "SCIENTIFIC_UNAVAILABLE"
            for row in rows
        ),
    }
    if not eligible:
        return {
            **base,
            "N": 0,
            "MAE": None,
            "RMSE": None,
            "MedAE": None,
            "MBE": None,
            "WAPE": None,
            "MAPE": None,
            "R2": None,
            "covered_N": 0,
            "LITERATURE_EVIDENCE_ENVELOPE_COVERAGE": None,
            "LITERATURE_EVIDENCE_ENVELOPE_COVERAGE_PERCENT": None,
            "mean_envelope_width": None,
            "median_envelope_width": None,
        }
    errors = [float(row["pred_ref"]) - float(row["actual"]) for row in eligible]
    absolute = [abs(error) for error in errors]
    actuals = [float(row["actual"]) for row in eligible]
    widths = [float(row["pred_high"]) - float(row["pred_low"]) for row in eligible]
    covered = sum(
        row["pred_low"] <= row["actual"] <= row["pred_high"] for row in eligible
    )
    actual_sum = sum(abs(value) for value in actuals)
    mean_actual = statistics.fmean(actuals)
    ss_total = sum((value - mean_actual) ** 2 for value in actuals)
    mape_values = [
        abs(error / actual) * 100
        for error, actual in zip(errors, actuals)
        if actual
    ]
    envelope_coverage = covered / len(eligible)
    return {
        **base,
        "N": len(eligible),
        "MAE": statistics.fmean(absolute),
        "RMSE": statistics.fmean(error * error for error in errors) ** 0.5,
        "MedAE": float(statistics.median(absolute)),
        "MBE": statistics.fmean(errors),
        "WAPE": sum(absolute) / actual_sum * 100 if actual_sum else None,
        "MAPE": statistics.fmean(mape_values) if mape_values else None,
        "R2": 1 - sum(error * error for error in errors) / ss_total if ss_total else None,
        "covered_N": covered,
        "LITERATURE_EVIDENCE_ENVELOPE_COVERAGE": envelope_coverage,
        "LITERATURE_EVIDENCE_ENVELOPE_COVERAGE_PERCENT": envelope_coverage * 100,
        "mean_envelope_width": statistics.fmean(widths),
        "median_envelope_width": float(statistics.median(widths)),
    }


def _direct_revenue_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    actual_eligible = [row for row in rows if row.get("actual_revenue") is not None]
    eligible = [
        row
        for row in actual_eligible
        if row.get("pred_ref") is not None
    ]
    coverage = len(eligible) / len(actual_eligible) if actual_eligible else None
    base = {
        "N_total_actual_eligible": len(actual_eligible),
        "N_actual_eligible": len(actual_eligible),
        "N_predicted": len(eligible),
        "prediction_coverage_fraction": coverage,
        "prediction_coverage_percent": coverage * 100 if coverage is not None else None,
        "prediction_coverage": coverage,
    }
    if not eligible:
        result = {
            **base,
            "N": 0,
            "MAE": None,
            "RMSE": None,
            "MedAE": None,
            "MBE": None,
            "WAPE": None,
            "covered_N": 0,
            "LITERATURE_EVIDENCE_ENVELOPE_COVERAGE": None,
            "LITERATURE_EVIDENCE_ENVELOPE_COVERAGE_PERCENT": None,
            "mean_envelope_width": None,
            "median_envelope_width": None,
        }
        result.update(
            {
                "MAE_RP_PER_CYCLE": result["MAE"],
                "RMSE_RP_PER_CYCLE": result["RMSE"],
                "MedAE_RP_PER_CYCLE": result["MedAE"],
                "MBE_RP_PER_CYCLE": result["MBE"],
                "WAPE_PERCENT": result["WAPE"],
            }
        )
        return result
    errors = [float(row["pred_ref"]) - float(row["actual_revenue"]) for row in eligible]
    absolute = [abs(error) for error in errors]
    actual_sum = sum(abs(float(row["actual_revenue"])) for row in eligible)
    envelope_rows = [
        row
        for row in eligible
        if row.get("pred_low") is not None and row.get("pred_high") is not None
    ]
    widths = [float(row["pred_high"]) - float(row["pred_low"]) for row in envelope_rows]
    covered = sum(
        row["pred_low"] <= row["actual_revenue"] <= row["pred_high"]
        for row in envelope_rows
    )
    result = {
        **base,
        "N": len(eligible),
        "MAE": statistics.fmean(absolute),
        "RMSE": statistics.fmean(error * error for error in errors) ** 0.5,
        "MedAE": float(statistics.median(absolute)),
        "MBE": statistics.fmean(errors),
        "WAPE": sum(absolute) / actual_sum * 100 if actual_sum else None,
        "covered_N": covered,
        "LITERATURE_EVIDENCE_ENVELOPE_COVERAGE": (
            covered / len(envelope_rows) if envelope_rows else None
        ),
        "LITERATURE_EVIDENCE_ENVELOPE_COVERAGE_PERCENT": (
            covered / len(envelope_rows) * 100 if envelope_rows else None
        ),
        "mean_envelope_width": statistics.fmean(widths) if widths else None,
        "median_envelope_width": float(statistics.median(widths)) if widths else None,
    }
    result.update(
        {
            "MAE_RP_PER_CYCLE": result["MAE"],
            "RMSE_RP_PER_CYCLE": result["RMSE"],
            "MedAE_RP_PER_CYCLE": result["MedAE"],
            "MBE_RP_PER_CYCLE": result["MBE"],
            "WAPE_PERCENT": result["WAPE"],
        }
    )
    return result


def _numeric_equal(left: Any, right: Any) -> bool:
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        if isinstance(left, bool) or isinstance(right, bool):
            return left == right
        return math.isclose(float(left), float(right), rel_tol=1e-12, abs_tol=1e-8)
    return left == right


def _differences(expected: Any, observed: Any, prefix: str = "") -> list[str]:
    if isinstance(expected, dict) and isinstance(observed, dict):
        differences: list[str] = []
        for key in sorted(set(expected) | set(observed)):
            path = f"{prefix}.{key}" if prefix else str(key)
            if key not in expected or key not in observed:
                differences.append(path)
            else:
                differences.extend(_differences(expected[key], observed[key], path))
        return differences
    if not _numeric_equal(expected, observed):
        return [prefix]
    return []


def independently_reproduce_metrics(
    corrected_yield: dict[str, Any],
    revenue_validation: dict[str, Any],
) -> dict[str, Any]:
    yield_expected = corrected_yield["metrics"]
    yield_observed = _direct_yield_metrics(corrected_yield["rows"])
    checks: dict[str, Any] = {
        "yield": {
            "harness_metrics": yield_expected,
            "independently_recomputed_metrics": yield_observed,
            "mismatches": _differences(yield_expected, yield_observed),
        }
    }
    for name, diagnostic in revenue_validation.get("diagnostics", {}).items():
        expected = diagnostic["metrics"]
        observed_rows = diagnostic.get("rows", [])
        observed = _direct_revenue_metrics(observed_rows)
        checks["revenue:" + name] = {
            "harness_metrics": expected,
            "independently_recomputed_metrics": observed,
            "mismatches": _differences(expected, observed),
        }
    mismatches = {
        key: value["mismatches"]
        for key, value in checks.items()
        if value["mismatches"]
    }
    return {
        "status": "PASS" if not mismatches else "FAIL",
        "tolerance": {"relative": 1e-12, "absolute": 1e-8},
        "checks": checks,
        "mismatches": mismatches,
        "zero_meaningful_mismatch": not mismatches,
    }


def _format_metric(value: Any) -> str:
    return "None" if value is None else str(value)


def _render_corrected_report(
    *,
    output_dir: Path,
    head: str,
    adjudication: dict[str, Any],
    corrected_yield: dict[str, Any],
    revenue_validation: dict[str, Any],
    purchase_validation: dict[str, Any],
    scientific_diff: dict[str, Any],
    independent: dict[str, Any],
    original_before: dict[str, str],
    original_after: dict[str, str],
    corrections_manifest: dict[str, Any],
) -> str:
    metrics = corrected_yield["metrics"]
    lines = [
        "# Phase 6D-R Corrected Publication-Facing Validation Report",
        "",
        "> Status: `PHASE_6DR_CORRECTED_EMPIRICAL_VALIDATION_COMPLETE`",
        "> This report separates a validation-harness provenance correction from the frozen R2 scientific model.",
        "",
        "## Identity and immutability",
        "",
        f"- Current repository HEAD: `{head}`",
        f"- Scientific target SHA: `{SCIENTIFIC_TARGET_SHA}`",
        f"- Original official Phase-6D run: `{ORIGINAL_OFFICIAL_RUN_ID}`",
        f"- Original comparator harness blob SHA: `{ORIGINAL_HARNESS_SHA}`",
        f"- Corrected validation harness working target: `{corrections_manifest['validation_harness_sha']}`",
        f"- Protocol source blob SHA at the scientific target: `{PROTOCOL_SOURCE_SHA}`",
        "- MODEL_VERSION=`R2`; registry=`R2-2026-08-26.3`; scientific freeze=`R2-FREEZE-2026-08-26.5`.",
        "- No `.6` freeze, `.4` registry, coefficient revision, recalibration, or model rerun was performed.",
        "- Corrected metrics reuse the original frozen Phase-6 runtime predictions.",
        "",
        "## Original-run root cause",
        "",
        "- `validation/workbook_parser.py::_actual_provenance` assigns `DERIVED_ACTUAL` whenever the raw comparator cell content is a formula (`raw_formula` starts with `=`); `reconstruct_cohorts` applies that result to `actual_yield_kg_per_are`.",
        "- In the original `validation/comparators.py::build_yield_comparator`, the actual value was retained only when `actual_provenance == OBSERVED_VALUE`; every derived actual was replaced with `None` before metric calculation.",
        "- Result: the official source reconstruction was valid, but the yield/revenue comparator became non-evaluable at N=0 due to endpoint provenance-admissibility logic.",
        "",
        "## Pre-existing protocol finding",
        "",
        "- At the target protocol, clean cohort N=36 is stated in §§3 and 5.1; the component table in §12 states yield comparator availability 36/36; §6 and §22 prescribe yield comparison when executable.",
        "- §4 explicitly includes `DERIVED_ACTUAL` in the comparator provenance vocabulary.",
        "- Finding: the pre-existing protocol did not state that `DERIVED_ACTUAL` yield must be rejected. The original harness exclusion was not a protocol requirement.",
        "",
        "## Raw yield formula and precedent audit",
        "",
        f"- Audited all {adjudication['row_count']} clean rows before calculating residuals; `metric_calculation_performed`={adjudication['metric_calculation_performed']}; `residuals_used_for_adjudication`={adjudication['residuals_used_for_adjudication']}.",
        "- Formula patterns:",
    ]
    for group in adjudication["formula_pattern_inventory"]:
        lines.append(
            f"  - `{group['formula_pattern']}`: N={group['n_rows']}; class={group['formula_class']}; numerator={group['numerator_semantic']}; denominator={group['denominator_semantic']}; unit={group['unit_transformation']}; constant={group['constant_used']}; pure deterministic measurement derivation={group['pure_deterministic_measurement_derivation']}."
        )
    lines.extend(
        [
            "- Precedents for every row are recorded in `yield_actual_provenance_adjudication.json`; all formula precedents are direct numeric raw cells: `AA` actual gabah quantity and `H` program rice area. No formula-derived precedent, imputation, legacy model result, prediction, default, or unknown precedent was used.",
            "- Area semantic: `H` is `Rice field in program (Are)`, mapped by the clean workbook to `A_are (Luas Program)` and compatible with R2 active cultivated/program rice interaction area. It is not total land and is not a separate unverified harvested-area construct.",
            "- Harvest quantity semantic: `AA` is directly recorded `Actual gabah yield (kg)`, with separate sale-price and gabah-revenue fields. It is treated as actual harvested gabah quantity, not a sales quantity or legacy prediction.",
            "- Basis limitation: the workbooks say gabah but do not identify GKP, GKG, or moisture percentage; the heterogeneity/unknown basis is disclosed and not silently harmonized.",
            "",
            "## Yield admissibility decision",
            "",
            "- A `DERIVED_ACTUAL` yield is eligible only when its formula deterministically transforms semantically compatible direct actual observations into kg/are: actual harvested quantity (kg) divided by active cultivated/program rice area (are), with no forbidden model/imputation/fallback semantics.",
            f"- Admissible derived-yield N={adjudication['admissible_derived_actual_n']}; non-admissible N={adjudication['not_admissible_derived_actual_n']}.",
            f"- Non-admissible yield reason counts: `{adjudication['not_admissible_reason_counts']}`.",
            f"- Yield provenance distribution: `{adjudication['yield_provenance_distribution']}`. Provenance remains `DERIVED_ACTUAL`; admissibility is a separate boolean dimension.",
            "- No row was excluded for residual size, envelope miss, MAPE, or model performance. Row inclusion was fully determined before metric calculation by source semantics and provenance.",
            "",
            "## Endpoint-specific policy",
            "",
            "- Purchase price strict comparator remains `OBSERVED_VALUE` and positive only; `DERIVED_ACTUAL` purchase price remains excluded.",
            "- Yield comparator accepts `OBSERVED_VALUE` plus semantically verified/admissible `DERIVED_ACTUAL`; non-admissible derived, legacy imputation, missing/unknown, and unverified explicit zero are excluded.",
            "- Paddy price follows the existing approved diagnostic rule: observed positive historical price is metadata for the price-neutral diagnostic only.",
            "",
            "## Corrected yield comparator",
            "",
            f"- N_total_actual_eligible={_format_metric(metrics.get('N_total_actual_eligible'))}; N_predicted={_format_metric(metrics.get('N_predicted'))}; prediction coverage={_format_metric(metrics.get('prediction_coverage_percent'))}% ({_format_metric(metrics.get('prediction_coverage_fraction'))}).",
            f"- MAE={_format_metric(metrics.get('MAE'))} kg/are; RMSE={_format_metric(metrics.get('RMSE'))} kg/are; MedAE={_format_metric(metrics.get('MedAE'))} kg/are; MBE={_format_metric(metrics.get('MBE'))} kg/are; WAPE={_format_metric(metrics.get('WAPE'))}%; supplementary MAPE={_format_metric(metrics.get('MAPE'))}%; diagnostic R²={_format_metric(metrics.get('R2'))}.",
            f"- Evidence envelope: covered N={_format_metric(metrics.get('covered_N'))}; LITERATURE_EVIDENCE_ENVELOPE_COVERAGE={_format_metric(metrics.get('LITERATURE_EVIDENCE_ENVELOPE_COVERAGE'))} ({_format_metric(metrics.get('LITERATURE_EVIDENCE_ENVELOPE_COVERAGE_PERCENT'))}%); mean width={_format_metric(metrics.get('mean_envelope_width'))} kg/are; median width={_format_metric(metrics.get('median_envelope_width'))} kg/are.",
            f"- Prediction status counts: scientific unavailable N={metrics.get('scientific_unavailable_n')}; HTTP execution failure N={metrics.get('http_execution_failure_n')}.",
            f"- Cluster bootstrap: `{corrected_yield['cluster_bootstrap']}` (farmer_cluster_id, 2,000 resamples, seed 20260826, 2.5/97.5 percentile).",
            "",
            "### Subgroups",
            "",
        ]
    )
    for name, subgroup in corrected_yield.get("subgroups", {}).items():
        subgroup_metrics = subgroup.get("metrics") or {}
        lines.append(
            f"- {name}: N_actual_eligible={subgroup.get('N_actual_eligible')}; N_predicted={subgroup.get('N_predicted')}; coverage={subgroup.get('prediction_coverage')}; policy={subgroup.get('policy')}; MAE={subgroup_metrics.get('MAE')}; RMSE={subgroup_metrics.get('RMSE')}; WAPE={subgroup_metrics.get('WAPE')}; R²={subgroup_metrics.get('R2')}" + (
                f"; note={subgroup.get('evidence_note')}" if subgroup.get("evidence_note") else ""
            )
        )
    lines.extend(
        [
            "",
            "## Revenue diagnostics",
            "",
        ]
    )
    for name, diagnostic in revenue_validation.get("diagnostics", {}).items():
        rm = diagnostic["metrics"]
        lines.append(
            f"- {name}: status={diagnostic['status']}; N_total_actual_eligible={rm.get('N_total_actual_eligible')}; N_predicted={rm.get('N_predicted')}; coverage={rm.get('prediction_coverage_percent')}%; MAE={rm.get('MAE')} Rp/cycle; RMSE={rm.get('RMSE')} Rp/cycle; MedAE={rm.get('MedAE')} Rp/cycle; MBE={rm.get('MBE')} Rp/cycle; WAPE={rm.get('WAPE')}%; envelope coverage={rm.get('LITERATURE_EVIDENCE_ENVELOPE_COVERAGE')}."
        )
    lines.extend(
        [
            "- Current-HPP diagnostic uses the current regulatory HPP benchmark; price-neutral diagnostic uses observed historical paddy price as comparator metadata only. No profit metric is produced.",
            "",
            "## Scientific diff and independent reproduction",
            "",
            f"- Scientific diff guard pass={scientific_diff['pass']}; changed paths={scientific_diff['changed_paths']}; scientific parameter/equation change={scientific_diff['scientific_parameter_or_equation_change']}.",
            f"- Independent yield/envelope/revenue reproduction: `{independent['status']}`; zero meaningful mismatch={independent['zero_meaningful_mismatch']}; tolerance={independent['tolerance']}. Full check is in `independent_metric_reproduction.json`.",
            "",
            "## Original-run preservation and QA",
            "",
            f"- Original run before/after file manifests identical={original_before == original_after}; original artifacts remain byte-for-byte preserved.",
            f"- Purchase policy result: strict_N={purchase_validation.get('strict_n')}; derived_actual_context_N={purchase_validation.get('derived_actual_context_n')}; no derived purchase price entered the strict comparator.",
            "- No PII is present in correction artifacts; row identity is source row plus anonymous farmer cluster ID only.",
            "- Required tests and compileall results are recorded in `qa_results.json`.",
            "",
            "## Correction conclusion",
            "",
            "- The original Phase-6D execution was official and targeted the correct frozen science, but its yield/revenue result was rendered non-evaluable by a validation-harness endpoint provenance-admissibility defect. It is not evidence that the model empirically failed at N=0.",
            "- This correction changes validation semantics only; production science remains R2 / registry .3 / freeze .5.",
            "",
            "`PHASE_6DR_CORRECTED_EMPIRICAL_VALIDATION_COMPLETE`",
        ]
    )
    return "\n".join(lines) + "\n"


def run_correction(
    *,
    source_dir: Path,
    output_dir: Path,
    root: Path = REPO_ROOT,
) -> dict[str, Any]:
    original_dir = root / "validation" / "results" / ORIGINAL_OFFICIAL_RUN_ID
    if not original_dir.is_dir():
        raise FileNotFoundError(f"original official run missing: {original_dir}")
    original_before = _directory_sha256_manifest(original_dir)

    head = git_head(root)
    harness_sha = _working_harness_sha(root)
    validation_harness_sha = f"{head}+WORKTREE:{harness_sha}"
    scientific_diff = _scientific_diff_audit(root)
    if not scientific_diff["pass"]:
        raise RuntimeError("scientific diff guard failed; corrected metrics not executed")

    sources = discover_sources(source_dir)
    reconstruction = reconstruct_cohorts(sources, private_map_path=None)
    if reconstruction.status != "RECONSTRUCTION_OK":
        raise RuntimeError(
            f"source reconstruction failed: {reconstruction.status} {reconstruction.mismatches}"
        )

    adjudication = build_yield_actual_adjudication(
        sources,
        reconstruction,
        scientific_target_sha=SCIENTIFIC_TARGET_SHA,
        original_official_run_id=ORIGINAL_OFFICIAL_RUN_ID,
        validation_harness_sha=validation_harness_sha,
        protocol_source_sha=PROTOCOL_SOURCE_SHA,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    adjudication_path = output_dir / "yield_actual_provenance_adjudication.json"
    _write_json(adjudication_path, adjudication)
    adjudication_sha = _sha256_file(adjudication_path)
    frozen_adjudication = _read_json(adjudication_path)
    if frozen_adjudication != adjudication:
        raise RuntimeError("adjudication artifact changed during local freeze/reload")

    if frozen_adjudication["admissible_derived_actual_n"] == 0:
        status = "PHASE_6DR_YIELD_ACTUAL_NOT_ADMISSIBLE"
        corrections_manifest = {
            "finding_id": "F-03_YIELD_DERIVED_ACTUAL_ADMISSIBILITY",
            "status": status,
            "original_official_run_id": ORIGINAL_OFFICIAL_RUN_ID,
            "scientific_target_sha": SCIENTIFIC_TARGET_SHA,
            "validation_harness_sha": validation_harness_sha,
            "protocol_source_sha": PROTOCOL_SOURCE_SHA,
            "adjudication_artifact_sha256": adjudication_sha,
            "admissible_derived_actual_n": 0,
            "scientific_coefficients_changed": False,
            "model_rerun_or_recalibration": False,
            "post_hoc_row_selection": False,
        }
        _write_json(output_dir / "corrections_manifest.json", corrections_manifest)
        return {"status": status, "output_dir": str(output_dir)}

    original_validation = _read_json(original_dir / "yield_validation.json")
    corrected_yield = build_corrected_yield_validation(
        original_validation,
        reconstruction.clean_records,
        frozen_adjudication,
    )
    revenue_validation = build_revenue_diagnostics(corrected_yield)
    purchase_validation = build_purchase_comparator(reconstruction)
    independent = independently_reproduce_metrics(corrected_yield, revenue_validation)

    original_after = _directory_sha256_manifest(original_dir)
    if original_before != original_after:
        raise RuntimeError("original official run changed during correction")

    required_qa = _run_required_qa(root)
    if not required_qa["all_passed"]:
        raise RuntimeError("required Phase-6D-R QA command failed")
    qa_results = {
        "scientific_diff_guard": scientific_diff,
        "adjudication_artifact_frozen": True,
        "original_run_byte_for_byte_preserved": original_before == original_after,
        "independent_metric_reproduction": independent,
        "required_commands": required_qa,
        "python_version": platform.python_version(),
    }
    corrections_manifest = {
        "finding_id": "F-03_YIELD_DERIVED_ACTUAL_ADMISSIBILITY",
        "status": "PHASE_6DR_CORRECTED_EMPIRICAL_VALIDATION_COMPLETE",
        "original_official_run_id": ORIGINAL_OFFICIAL_RUN_ID,
        "scientific_target_sha": SCIENTIFIC_TARGET_SHA,
        "original_validation_harness_sha": ORIGINAL_HARNESS_SHA,
        "validation_harness_sha": validation_harness_sha,
        "protocol_source_sha": PROTOCOL_SOURCE_SHA,
        "original_harness_behavior": {
            "yield_actual_eligible_condition": "actual_provenance == OBSERVED_VALUE",
            "derived_actual_yield_excluded": True,
            "resulting_n_total_actual_eligible": 0,
            "resulting_revenue_metrics": "NOT_EVALUABLE_DOWNSTREAM",
        },
        "pre_existing_protocol_evidence": {
            "clean_cohort_n": 36,
            "actual_yield_coverage": "36/36",
            "derived_actual_in_provenance_vocab": True,
            "derived_actual_yield_explicitly_forbidden": False,
            "source": "docs/06_R2_TEST_VALIDATION_PROTOCOL.md at scientific target",
        },
        "source_semantic_reproduction": {
            "formula_patterns": frozen_adjudication["formula_pattern_inventory"],
            "all_clean_rows_audited": frozen_adjudication["row_count"],
            "admissible_derived_actual_n": frozen_adjudication[
                "admissible_derived_actual_n"
            ],
            "not_admissible_derived_actual_n": frozen_adjudication[
                "not_admissible_derived_actual_n"
            ],
        },
        "correction": {
            "yield_rule": "OBSERVED_VALUE OR DERIVED_ACTUAL with true semantic admissibility",
            "purchase_rule": "OBSERVED_VALUE positive only",
            "paddy_price_rule": "existing approved observed-positive metadata diagnostic",
            "adjudication_artifact": "yield_actual_provenance_adjudication.json",
            "adjudication_artifact_sha256": adjudication_sha,
            "runtime_science_reused": True,
        },
        "adjudication_artifact_sha256": adjudication_sha,
        "scientific_coefficients_changed": False,
        "model_rerun_or_recalibration": False,
        "post_hoc_row_selection": False,
        "no_new_freeze": True,
        "required_qa_all_passed": required_qa["all_passed"],
        "original_run_sha256_before": original_before,
        "original_run_sha256_after": original_after,
        "original_run_byte_for_byte_preserved": original_before == original_after,
    }
    _write_json(output_dir / "corrected_yield_validation.json", corrected_yield)
    _write_json(output_dir / "revenue_validation_corrected.json", revenue_validation)
    _write_json(output_dir / "purchase_validation_context.json", purchase_validation)
    _write_json(output_dir / "scientific_diff_audit.json", scientific_diff)
    _write_json(output_dir / "independent_metric_reproduction.json", independent)
    _write_json(output_dir / "qa_results.json", qa_results)
    _write_json(output_dir / "corrections_manifest.json", corrections_manifest)
    report = _render_corrected_report(
        output_dir=output_dir,
        head=head or "UNRESOLVED",
        adjudication=frozen_adjudication,
        corrected_yield=corrected_yield,
        revenue_validation=revenue_validation,
        purchase_validation=purchase_validation,
        scientific_diff=scientific_diff,
        independent=independent,
        original_before=original_before,
        original_after=original_after,
        corrections_manifest=corrections_manifest,
    )
    (output_dir / "validation_report_phase6dr_corrected.md").write_text(
        report, encoding="utf-8"
    )
    return {
        "status": corrections_manifest["status"],
        "output_dir": str(output_dir),
        "adjudication_sha256": adjudication_sha,
        "corrected_yield": corrected_yield,
        "revenue_validation": revenue_validation,
        "purchase_validation": purchase_validation,
        "scientific_diff": scientific_diff,
        "independent": independent,
        "corrections_manifest": corrections_manifest,
        "original_run_sha256_before": original_before,
        "original_run_sha256_after": original_after,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m validation.phase6dr",
        description="Run the Phase-6D-R yield provenance correction layer.",
    )
    parser.add_argument(
        "--source-dir",
        default=str(REPO_ROOT / "penelitian" / "R2_validation_sources"),
    )
    parser.add_argument(
        "--output-dir",
        default=str(REPO_ROOT / "validation" / "results" / CORRECTION_DIR_NAME),
    )
    args = parser.parse_args(argv)
    result = run_correction(
        source_dir=Path(args.source_dir).resolve(),
        output_dir=Path(args.output_dir).resolve(),
    )
    print(f"[phase6dr] status       : {result['status']}")
    print(f"[phase6dr] output dir   : {result['output_dir']}")
    if result["status"] == "PHASE_6DR_CORRECTED_EMPIRICAL_VALIDATION_COMPLETE":
        metrics = result["corrected_yield"]["metrics"]
        print(
            f"[phase6dr] yield N      : actual={metrics['N_total_actual_eligible']} "
            f"predicted={metrics['N_predicted']} "
            f"coverage={metrics['prediction_coverage_percent']}%"
        )
        print(f"[phase6dr] reproduction : {result['independent']['status']}")
    return 0 if result["status"] != "PHASE_6DR_CORRECTION_BLOCKED" else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "CORRECTION_DIR_NAME",
    "ORIGINAL_OFFICIAL_RUN_ID",
    "PROTOCOL_SOURCE_SHA",
    "SCIENTIFIC_TARGET_SHA",
    "build_corrected_yield_validation",
    "independently_reproduce_metrics",
    "run_correction",
]
