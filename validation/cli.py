"""CLI orchestrator for the Phase-5 validation harness.

Usage (research-only):
    python -m validation [--source-dir PATH]

Artifacts are written to validation/results/<run_id>/ and the latest freeze
manifest is mirrored to validation/freeze_manifest.json. Official mode fires
only when every task-§36 gate condition holds on a CLEAN tree.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from validation._bootstrap import REPO_ROOT, configure_runtime_env

configure_runtime_env()

from validation import report as report_mod  # noqa: E402
from validation.expert_transfer import EXPERT_TRANSFER_MATRIX  # noqa: E402
from validation.fixture_builder import build_fixture_manifest  # noqa: E402
from validation.comparators import (  # noqa: E402
    build_calendar_comparator,
    build_component_comparators,
    build_purchase_comparator,
    run_stress_rows,
)
from validation.provenance import (  # noqa: E402
    evaluate_official_gate,
    git_head,
    git_status_porcelain,
    is_tree_clean,
    load_freeze_identity,
)
from validation.runtime_runner import (  # noqa: E402
    run_age_invariance,
    run_full_active_suite,
    run_synthetic_cases,
    run_v1_matrix,
    probe_production_availability,
)
from validation.source_loader import (  # noqa: E402
    ROLE_LEGACY_SIMULATION,
    ROLE_RAW_RECAP,
    ROLE_CLEAN_COHORT,
    discover_sources,
)
from validation.workbook_parser import (  # noqa: E402
    RECONSTRUCTION_OK,
    SOURCE_VERSION_MISMATCH,
    parse_legacy_simulation,
    reconstruct_cohorts,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m validation",
        description="Rice-Duck R2 Phase-5 research validation harness "
        "(never imported by production code).",
    )
    parser.add_argument(
        "--source-dir",
        default=os.environ.get("R2_VALIDATION_SOURCE_DIR"),
        help="Directory containing the expected research workbooks "
        "(R2_VALIDATION_SOURCE_DIR). Only this directory is searched.",
    )
    args = parser.parse_args(argv)

    source_dir = Path(args.source_dir).resolve() if args.source_dir else None
    print(f"[validation] repo root          : {REPO_ROOT}")
    print(f"[validation] source dir         : {source_dir or '<unset>'}")

    identity = load_freeze_identity()
    head = git_head()
    clean = is_tree_clean()
    porcelain = git_status_porcelain()
    print(f"[validation] HEAD               : {head}")
    print(f"[validation] tree clean         : {clean}")
    if not clean:
        entries = [ln for ln in porcelain.splitlines() if ln.strip()]
        print(f"[validation] dirty entries ({len(entries)}):")
        for line in entries[:50]:
            print(f"    {line}")

    print("[validation] running full active suite ...")
    test_summary = run_full_active_suite()
    print(
        f"[validation] tests              : collected={test_summary['collected']} "
        f"passed={test_summary['passed']} failed={test_summary['failed']} "
        f"skipped={test_summary['skipped']} xfailed={test_summary['xfailed']} "
        f"xpassed={test_summary['xpassed']} legacy_collected="
        f"{test_summary['legacy_invalid_collected']}"
    )

    sources = discover_sources(source_dir)
    for role, src in sources.items():
        print(f"[validation] source {role:<18}: {src.status}")

    print("[validation] probing canonical runtime availability state ...")
    probe = probe_production_availability()
    yield_unavailable = probe["yield_availability"] == "UNAVAILABLE"

    print("[validation] executing synthetic B01-B18 via canonical HTTP path ...")
    synthetic_records = run_synthetic_cases()
    age_invariance = run_age_invariance()
    print("[validation] executing docs/06 section-19 V1 matrix via pytest ...")
    v1 = run_v1_matrix()

    reconstruction = reconstruct_cohorts(
        sources,
        private_map_path=REPO_ROOT / "validation" / "local" / "farmer_id_map.json",
    )
    fixture_manifest = build_fixture_manifest(sources, reconstruction)
    eligibility = report_mod.build_component_eligibility(sources, probe)
    yield_block = report_mod.build_yield_status_block(probe, sources)
    calendar_block = (
        build_calendar_comparator(reconstruction)
        if reconstruction.status == RECONSTRUCTION_OK else {
            "status": reconstruction.status, "metrics": None
        }
    )
    purchase_block = (
        build_purchase_comparator(reconstruction)
        if reconstruction.status == RECONSTRUCTION_OK else {
            "status": reconstruction.status, "effective_n": 0, "rows": []
        }
    )
    component_block = (
        build_component_comparators(reconstruction)
        if reconstruction.status == RECONSTRUCTION_OK else {
            "status": reconstruction.status
        }
    )
    stress_block = (
        run_stress_rows(reconstruction)
        if reconstruction.status == RECONSTRUCTION_OK else {
            "status": reconstruction.status,
            "rows": [],
            "merged_into_headline_metrics": False,
        }
    )
    eligibility["components"]["calendar"]["status"] = calendar_block["status"]
    eligibility["components"]["calendar"]["metrics"] = calendar_block.get("metrics")
    eligibility["components"]["duck_purchase_cost_identity"][
        "observed_positive_comparator"
    ] = {
        "status": purchase_block["status"],
        "effective_n": purchase_block["effective_n"],
    }

    gate = evaluate_official_gate(
        identity,
        head=head,
        tree_clean=clean,
        tests_passed=bool(test_summary["all_passed"]),
        source_discovery_executed=True,
        source_fingerprints_valid=(
            sources[ROLE_RAW_RECAP].fingerprint_valid
            and sources[ROLE_CLEAN_COHORT].fingerprint_valid
        ),
        cohort_reconstruction_successful=(
            reconstruction.status == RECONSTRUCTION_OK
        ),
        source_version_mismatch=(
            reconstruction.status == SOURCE_VERSION_MISMATCH
        ),
    )
    manifest = report_mod.build_freeze_manifest(
        identity, gate, head, sources, test_summary
    )

    run_dir = REPO_ROOT / "validation" / "results" / report_mod.new_run_id(head)
    report_mod.write_json(run_dir / "freeze_manifest.json", manifest)
    report_mod.write_json(run_dir / "v1_computational.json", v1)
    report_mod.write_json(
        run_dir / "synthetic_cases.json",
        {
            "run_mode": gate.run_mode,
            "backend_commit_sha": head,
            "cases": synthetic_records,
            "age_invariance": age_invariance,
        },
    )
    report_mod.write_json(run_dir / "fixture_manifest.json", fixture_manifest)
    report_mod.write_json(
        run_dir / "cohort_reconstruction.json", reconstruction.manifest()
    )
    report_mod.write_json(run_dir / "component_eligibility.json", eligibility)
    report_mod.write_json(
        run_dir / "calendar_validation.json",
        calendar_block,
    )
    report_mod.write_json(run_dir / "purchase_validation.json", purchase_block)
    report_mod.write_json(run_dir / "component_comparators.json", component_block)
    report_mod.write_json(run_dir / "stress_results.json", stress_block)
    legacy_source = sources[ROLE_LEGACY_SIMULATION]
    legacy_audit = (
        parse_legacy_simulation(Path(legacy_source.path or "")).audit
        if legacy_source.present else {
            "role": "AUDIT_ONLY", "status": legacy_source.status
        }
    )
    report_mod.write_json(run_dir / "legacy_simulation_audit.json", legacy_audit)
    report_mod.write_json(
        run_dir / "expert_transfer.json",
        {"items": EXPERT_TRANSFER_MATRIX,
         "global_notes": [
             "Expert ~80% working confidence is not a statistical pass/fail threshold.",
             "No aggregate 'expert accuracy' score exists.",
         ]},
    )
    md = report_mod.render_validation_report_md(
        manifest, fixture_manifest, eligibility, yield_block,
        synthetic_records, age_invariance, v1, stress_block,
    )
    (run_dir / "validation_report.md").write_text(md, encoding="utf-8")
    # Mirror latest manifest at the documented top-level location.
    report_mod.write_json(REPO_ROOT / "validation" / "freeze_manifest.json", manifest)

    synth_passed = sum(1 for r in synthetic_records if r["pass"])
    print(f"[validation] synthetic cases    : {synth_passed}/{len(synthetic_records)} passed")
    print(f"[validation] V1 matrix all_pass : {v1['all_pass']}")
    print(f"[validation] age invariance     : pass={age_invariance['pass']}")
    print(f"[validation] empirical sources  : {fixture_manifest['empirical_source_status']}")
    print(f"[validation] yield status       : {yield_block['status']} ({yield_block['reason']})")
    print(f"[validation] run_mode           : {gate.run_mode}")
    if gate.failed_conditions:
        print(f"[validation] gate failures      : {gate.failed_conditions}")
    print(f"[validation] artifacts dir      : {run_dir}")

    # Mode A/B status line (task §42/§43).
    if not gate.official:
        print("STATUS: PHASE5_PREPARE_RUN_COMPLETE_NON_OFFICIAL")
    elif not fixture_manifest["empirical_source_status"] == "OK":
        print("STATUS: PHASE 5 EMPIRICAL SOURCE BLOCKED (official identity recorded)")
    else:
        print("STATUS: OFFICIAL RUN COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
