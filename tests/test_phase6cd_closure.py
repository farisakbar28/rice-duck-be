"""Synthetic-only Phase-6C/D closure regressions."""

from types import SimpleNamespace

import pytest

from app.data.seed import FREEZE_ID, MODEL_VERSION, PARAMETER_REGISTRY_VERSION
from validation.comparators import build_revenue_diagnostics, build_yield_comparator
from validation.metrics import is_strict_supported_domain_row, phase6_yield_subgroups
from validation.provenance import (
    FreezeIdentity,
    evaluate_pre_empirical_gate,
    evaluate_source_reconstruction_gate,
)
from validation.report import render_validation_report_md


def _identity() -> FreezeIdentity:
    return FreezeIdentity(
        model_version=MODEL_VERSION,
        parameter_registry_version=PARAMETER_REGISTRY_VERSION,
        freeze_id=FREEZE_ID,
        model_frozen=True,
        freeze_effective_from="2026-08-26",
        model_commit_sha_env=None,
        app_version="test",
        history_schema_version=4,
        python_version="test",
        execution_timestamp_utc="2026-08-26T00:00:00+00:00",
    )


def _row(**overrides):
    row = {
        "source_row": 4,
        "farmer_cluster_id": "F001",
        "actual": 40.0,
        "area_are": 2.0,
        "paddy_price": 6000.0,
        "paddy_price_provenance": "OBSERVED_VALUE",
        "pred_ref": 42.0,
        "pred_low": 30.0,
        "pred_high": 50.0,
        "pred_total_ref": 84.0,
        "pred_total_low": 60.0,
        "pred_total_high": 100.0,
        "age_support": "SUPPORTED",
        "density_support": "SUPPORTED",
        "planting_system_provenance": "OBSERVED",
        "cultivar_group": "INPARI_GROUP",
        "planting_system": "jajar_legowo",
    }
    row.update(overrides)
    return row


def test_strict_cohort_requires_observed_planting_system_provenance():
    assert not is_strict_supported_domain_row(
        _row(planting_system_provenance="LOCAL_DEFAULT")
    )
    assert is_strict_supported_domain_row(_row())


def test_subgroup_strict_n_is_recomputed_and_not_hardcoded():
    rows = [_row(source_row=4), _row(source_row=5, planting_system_provenance="LOCAL_DEFAULT")]
    groups = phase6_yield_subgroups(rows)
    assert groups["strict_supported_domain"]["N_predicted"] == 1


def test_stage_a_dirty_tree_blocks_before_stage_b():
    stage_a = evaluate_pre_empirical_gate(
        _identity(), head="clean-head", tree_clean=False, tests_passed=True,
        source_discovery_executed=True, source_fingerprints_valid=True,
    )
    assert not stage_a.official
    assert "OFFICIAL_VALIDATION_BLOCKED_DIRTY_TREE" in stage_a.failed_conditions
    stage_b = evaluate_source_reconstruction_gate(
        stage_a, cohort_reconstruction_successful=True,
    )
    assert not stage_b.official


def test_source_fingerprint_failure_is_stage_a_blocker():
    gate = evaluate_pre_empirical_gate(
        _identity(), head="clean-head", tree_clean=True, tests_passed=True,
        source_discovery_executed=True, source_fingerprints_valid=False,
    )
    assert gate.official is False
    assert "SOURCE_FINGERPRINTS_INVALID_OR_MISSING" in gate.failed_conditions


def test_yield_rows_record_harness_sha_and_both_http_statuses():
    body = {
        "model": {"model_version": "R2", "parameter_registry_version": PARAMETER_REGISTRY_VERSION,
                  "freeze_id": FREEZE_ID, "model_commit_sha": None},
        "operational": {"density_are": 2.0, "age_support": "SUPPORTED", "density_support": "SUPPORTED"},
        "yield": {"availability": "AVAILABLE", "reason_codes": [],
                   "cultivar_group_code": "INPARI_GROUP", "yield_ref_kg_per_are": 42.0,
                   "yield_low_kg_per_are": 30.0, "yield_high_kg_per_are": 50.0,
                   "yield_total_ref_kg": 84.0, "yield_total_low_kg": 60.0,
                   "yield_total_high_kg": 100.0},
    }

    class Client:
        def post(self, *_args, **_kwargs):
            return SimpleNamespace(status_code=200, json=lambda: body)

    reconstruction = SimpleNamespace(clean_records=[{
        "source_row": 4, "farmer_cluster_id": "F001", "input_fields": {
            "land_area_are": {"value": 2.0, "provenance": "OBSERVED"},
            "duck_count": {"value": 4, "provenance": "OBSERVED"},
            "planting_date": {"value": "2025-01-01", "provenance": "VALIDATION_ASSUMPTION"},
            "planting_system": {"value": "jajar_legowo", "provenance": "OBSERVED"},
            "rice_variety": {"value": "inpari", "provenance": "OBSERVED"},
            "p_duck_buy": {"value": 25000.0, "provenance": "OBSERVED"},
        },
        "actual_yield_kg_per_are": 40.0,
        "paddy_price": 6000.0,
        "actual_provenance": {"actual_yield_kg_per_are": "OBSERVED_VALUE", "paddy_price": "OBSERVED_VALUE"},
    }])
    result = build_yield_comparator(reconstruction, backend_commit_sha="clean-head", client=Client())
    assert result["rows"][0]["backend_commit_sha"] == "clean-head"
    assert result["rows"][0]["response_model_commit_sha"] is None
    assert result["rows"][0]["http_status_21"] == result["rows"][0]["http_status_30"] == 200


def test_http_replay_failure_is_not_scientific_unavailable():
    body = {"model": {}, "operational": {}, "yield": {
        "availability": "AVAILABLE", "reason_codes": [],
        "yield_ref_kg_per_are": 42.0, "yield_low_kg_per_are": 30.0,
        "yield_high_kg_per_are": 50.0, "yield_total_ref_kg": 84.0,
        "yield_total_low_kg": 60.0, "yield_total_high_kg": 100.0,
    }}

    class Client:
        def post(self, _url, json):
            if json["duck_age_days"] == 30:
                return SimpleNamespace(status_code=503, json=lambda: {})
            return SimpleNamespace(status_code=200, json=lambda: body)

    fields = {
        "land_area_are": {"value": 2.0, "provenance": "OBSERVED"},
        "duck_count": {"value": 4, "provenance": "OBSERVED"},
        "planting_date": {"value": "2025-01-01", "provenance": "VALIDATION_ASSUMPTION"},
        "planting_system": {"value": "jajar_legowo", "provenance": "OBSERVED"},
        "rice_variety": {"value": "inpari", "provenance": "OBSERVED"},
        "p_duck_buy": {"value": 25000.0, "provenance": "OBSERVED"},
    }
    reconstruction = SimpleNamespace(clean_records=[{
        "source_row": 4, "farmer_cluster_id": "F001", "input_fields": fields,
        "actual_yield_kg_per_are": 40.0,
        "actual_provenance": {"actual_yield_kg_per_are": "OBSERVED_VALUE"},
    }])
    result = build_yield_comparator(reconstruction, backend_commit_sha="clean-head", client=Client())
    row = result["rows"][0]
    assert row["prediction_status"] == "HTTP_EXECUTION_FAILURE"
    assert row["http_status_age_30"] == 503
    assert result["metrics"]["http_execution_failure_n"] == 1
    assert result["metrics"]["scientific_unavailable_n"] == 0


def test_renderer_uses_same_machine_values_and_calendar_not_stale():
    manifest = {
        "run_mode": "NON_OFFICIAL_PRECOMPARATOR_BLOCKED", "execution_timestamp_utc": "now",
        "python_version": "test", "backend_commit_sha": "clean-head",
        "parameter_registry_version": PARAMETER_REGISTRY_VERSION, "freeze_id": FREEZE_ID,
        "official_gate_failed_conditions": ["SOURCE_FINGERPRINTS_INVALID_OR_MISSING"],
        "model_version": "R2", "history_schema_version": 4, "app_version": "test",
        "model_frozen": True, "freeze_effective_from": "2026-08-26", "source_fingerprints": [],
    }
    fixture = {"empirical_source_status": "BLOCKED_SOURCE_FILES_MISSING", "cohort_metadata": {}}
    eligibility = {"components": {
        "calendar": {"status": "BLOCKED"},
        "infrastructure_net_cage": {"semantic_compatibility_established": False, "metric_allowed": False, "eligibility_reason": "n/a"},
        "profit_margin": {"cost_completeness": "INCOMPLETE"},
    }}
    yield_validation = {"status": "EVALUATED", "reason": None,
                        "metrics": {"N_total_actual_eligible": 3, "N_predicted": 2,
                                    "prediction_coverage_fraction": 2/3, "prediction_coverage_percent": 200/3,
                                    "MAE": 1.25, "RMSE": 2.5, "MedAE": 1.0, "MBE": .5,
                                    "WAPE": 3.0, "MAPE": 4.0, "R2": .9, "covered_N": 2,
                                    "LITERATURE_EVIDENCE_ENVELOPE_COVERAGE": .75,
                                    "LITERATURE_EVIDENCE_ENVELOPE_COVERAGE_PERCENT": 75,
                                    "mean_envelope_width": 10, "median_envelope_width": 9,
                                    "http_execution_failure_n": 0},
                        "age_assumption_invariance": True, "subgroups": {}}
    calendar = {"status": "EVALUATED", "timing_semantics": "HST_FROM_FIELD_TRANSPLANTING",
                "timing_semantics_status": "VALIDATION_ASSUMPTION",
                "metrics": {"N": 2, "hits": 1, "coverage": .5,
                            "mean_distance_to_window_days": 1, "median_distance_to_window_days": 1}}
    report = render_validation_report_md(
        manifest, fixture, eligibility, {}, [], {"pass": True, "differing_paths": []},
        {"all_pass": True, "items": []}, {"status": "BLOCKED"},
        calendar_validation=calendar, yield_validation=yield_validation,
    )
    assert "MAE kg/are=1.25" in report
    assert "N_predicted=2" in report
    assert "N=2; hits=1; coverage=0.5" in report
    assert "must be recomputed before any metric" not in report


def test_revenue_diagnostics_are_separate_and_price_is_metadata_only():
    result = build_revenue_diagnostics({"rows": [_row()]})
    operational = result["diagnostics"]["CURRENT_HPP_OPERATIONAL_VALUE_DIAGNOSTIC"]
    neutral = result["diagnostics"]["PRICE_NEUTRAL_HISTORICAL_PRICE_DIAGNOSTIC"]
    assert operational["metrics"]["N_predicted"] == 1
    assert neutral["metrics"]["N_predicted"] == 1
    assert operational["rows"][0]["price_source"] == "R2_REGULATORY_HPP"
    assert neutral["rows"][0]["price_source"] == "COMPARATOR_METADATA_ONLY"
    assert "runtime" not in neutral["rows"][0]["price_source"].lower()
