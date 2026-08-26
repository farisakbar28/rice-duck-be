"""Synthetic-only tests for the Phase-6 comparator harness."""

import pytest

from validation.metrics import (
    cluster_bootstrap_percentile_interval,
    phase6_yield_metrics,
    phase6_yield_subgroups,
)


def _rows():
    return [
        {"actual": 10.0, "pred_ref": 12.0, "pred_low": 8.0, "pred_high": 14.0,
         "cultivar_group": "INPARI_GROUP", "planting_system": "jajar_legowo", "age_support": "SUPPORTED", "density_support": "SUPPORTED"},
        {"actual": 20.0, "pred_ref": 18.0, "pred_low": 16.0, "pred_high": 22.0,
         "cultivar_group": "INPARI_GROUP", "planting_system": "jajar_legowo", "age_support": "SUPPORTED", "density_support": "SUPPORTED"},
        {"actual": 30.0, "pred_ref": None, "pred_low": None, "pred_high": None,
         "cultivar_group": "SERTANI_GROUP", "planting_system": "tegel", "age_support": "SUPPORTED", "density_support": "EXTRAPOLATION"},
    ]


def test_prediction_coverage_uses_all_actual_eligible_rows():
    metrics = phase6_yield_metrics(_rows())
    assert (metrics["N_total_actual_eligible"], metrics["N_predicted"]) == (3, 2)
    assert metrics["prediction_coverage_fraction"] == pytest.approx(2 / 3)
    assert metrics["prediction_coverage_percent"] == pytest.approx(200 / 3)


def test_reference_error_metrics_are_computed_only_for_predictions():
    metrics = phase6_yield_metrics(_rows())
    assert metrics["MAE"] == metrics["RMSE"] == metrics["MedAE"] == 2.0
    assert metrics["MBE"] == 0.0
    assert metrics["WAPE"] == pytest.approx(100 * 4 / 30)


def test_evidence_envelope_metrics_are_not_statistical_intervals():
    metrics = phase6_yield_metrics(_rows())
    assert metrics["covered_N"] == 2
    assert metrics["LITERATURE_EVIDENCE_ENVELOPE_COVERAGE"] == 1.0
    assert metrics["mean_envelope_width"] == metrics["median_envelope_width"] == 6.0


def test_no_prediction_does_not_become_zero_prediction():
    metrics = phase6_yield_metrics([{"actual": 4.0, "pred_ref": None, "pred_low": None, "pred_high": None}])
    assert metrics["N_predicted"] == 0
    assert metrics["prediction_coverage_fraction"] == 0.0
    assert metrics["MAE"] is None


def test_subgroup_policy_is_count_only_below_three_predictions():
    groups = phase6_yield_subgroups(_rows())
    assert groups["INPARI_GROUP"]["N"] == 2
    assert groups["INPARI_GROUP"]["policy"] == "COUNT_ONLY_SMALL_N"
    assert groups["SERTANI_GROUP"]["N"] == 0


def test_subgroup_policy_reports_quantitative_metrics_at_three():
    groups = phase6_yield_subgroups(_rows()[:2] + [{"actual": 40.0, "pred_ref": 40.0, "pred_low": 38.0, "pred_high": 42.0, "cultivar_group": "INPARI_GROUP", "planting_system": "jajar_legowo", "age_support": "SUPPORTED", "density_support": "SUPPORTED"}])
    assert groups["INPARI_GROUP"]["policy"] == "QUANTITATIVE"
    assert groups["INPARI_GROUP"]["metrics"]["N_predicted"] == 3


def test_cluster_bootstrap_groups_repeated_farmer_rows():
    interval = cluster_bootstrap_percentile_interval({"F001": [1.0, 2.0], "F002": [10.0]}, lambda values: sum(values) / len(values), resamples=10, seed=1)
    assert interval["cluster_unit"] == "farmer"
    assert interval["resamples"] == 10


def test_cluster_bootstrap_refuses_single_cluster():
    assert cluster_bootstrap_percentile_interval({"F001": [1.0]}, max, resamples=10) is None
