"""Phase-6D-R endpoint-specific provenance policy regressions."""

from types import SimpleNamespace

import pytest

from validation.comparators import build_purchase_comparator, build_yield_comparator
from validation.yield_adjudication import (
    DERIVED_ACTUAL_ADMISSIBLE,
    evaluate_yield_actual_eligibility,
    normalized_formula_pattern,
)


@pytest.mark.parametrize(
    ("provenance", "actual", "derived_admissibility", "expected"),
    [
        ("OBSERVED_VALUE", 40.0, None, True),
        ("DERIVED_ACTUAL", 40.0, True, True),
        ("DERIVED_ACTUAL", 40.0, False, False),
        ("LEGACY_IMPUTATION", 40.0, None, False),
        ("MISSING_UNKNOWN", None, None, False),
        ("EXPLICIT_ZERO", 0.0, None, False),
    ],
)
def test_yield_endpoint_policy_is_provenance_and_semantics_specific(
    provenance, actual, derived_admissibility, expected
):
    decision = evaluate_yield_actual_eligibility(
        provenance,
        actual,
        derived_actual_admissibility=derived_admissibility,
    )
    assert decision["eligible"] is expected


def test_verified_explicit_zero_is_not_silently_changed_to_missing():
    decision = evaluate_yield_actual_eligibility(
        "EXPLICIT_ZERO", 0.0, explicit_zero_semantics_verified=True
    )
    assert decision["eligible"] is True
    assert decision["reason"] == "EXPLICIT_ZERO_SEMANTICALLY_VERIFIED"


def test_formula_pattern_normalizes_absolute_and_relative_references():
    assert normalized_formula_pattern("=AA4/H4", 4) == "=AA{row}/H{row}"
    assert normalized_formula_pattern("=$AA$12/H12", 12) == "=$AA${row}/H{row}"


def _runtime_body():
    return {
        "model": {
            "model_version": "R2",
            "parameter_registry_version": "R2-2026-08-26.3",
            "freeze_id": "R2-FREEZE-2026-08-26.5",
            "model_commit_sha": None,
        },
        "operational": {
            "density_are": 2.0,
            "age_support": "SUPPORTED",
            "density_support": "SUPPORTED",
        },
        "yield": {
            "availability": "AVAILABLE",
            "reason_codes": [],
            "cultivar_group_code": "INPARI_GROUP",
            "yield_ref_kg_per_are": 42.0,
            "yield_low_kg_per_are": 30.0,
            "yield_high_kg_per_are": 50.0,
            "yield_total_ref_kg": 84.0,
            "yield_total_low_kg": 60.0,
            "yield_total_high_kg": 100.0,
        },
    }


class _Client:
    def post(self, *_args, **_kwargs):
        return SimpleNamespace(status_code=200, json=_runtime_body)


def _reconstruction(provenance="DERIVED_ACTUAL"):
    return SimpleNamespace(
        clean_records=[
            {
                "source_row": 4,
                "farmer_cluster_id": "F001",
                "input_fields": {
                    "land_area_are": {"value": 2.0, "provenance": "OBSERVED"},
                    "duck_count": {"value": 4, "provenance": "OBSERVED"},
                    "planting_date": {
                        "value": "2025-01-01",
                        "provenance": "VALIDATION_ASSUMPTION",
                    },
                    "planting_system": {
                        "value": "jajar_legowo",
                        "provenance": "OBSERVED",
                    },
                    "rice_variety": {"value": "inpari", "provenance": "OBSERVED"},
                    "p_duck_buy": {"value": 25000.0, "provenance": "OBSERVED"},
                },
                "actual_yield_kg_per_are": 40.0,
                "actual_provenance": {
                    "actual_yield_kg_per_are": provenance,
                },
            }
        ]
    )


def _adjudication(admissible):
    return {
        "records": [
            {
                "source_row": 4,
                "actual_numeric_value": 40.0,
                "actual_provenance": "DERIVED_ACTUAL",
                "derived_actual_admissibility": admissible,
                "admissibility": (
                    DERIVED_ACTUAL_ADMISSIBLE if admissible else "DERIVED_ACTUAL_NOT_ADMISSIBLE"
                ),
            }
        ]
    }


def test_admissible_derived_yield_enters_comparator_without_relabeling():
    result = build_yield_comparator(
        _reconstruction(),
        backend_commit_sha="frozen-runtime",
        client=_Client(),
        yield_adjudication=_adjudication(True),
    )
    row = result["rows"][0]
    assert row["actual"] == 40.0
    assert row["actual_yield_provenance"] == "DERIVED_ACTUAL"
    assert row["derived_actual_admissibility"] is True
    assert row["actual_comparator_eligible"] is True
    assert result["metrics"]["N_total_actual_eligible"] == 1


def test_non_admissible_derived_yield_is_excluded():
    result = build_yield_comparator(
        _reconstruction(),
        backend_commit_sha="frozen-runtime",
        client=_Client(),
        yield_adjudication=_adjudication(False),
    )
    row = result["rows"][0]
    assert row["actual"] is None
    assert row["actual_yield_provenance"] == "DERIVED_ACTUAL"
    assert row["derived_actual_admissibility"] is False
    assert row["actual_comparator_eligible"] is False
    assert result["metrics"]["N_total_actual_eligible"] == 0


def test_purchase_derived_actual_remains_excluded_from_strict_comparator():
    reconstruction = SimpleNamespace(
        clean_records=[
            {
                "source_row": 4,
                "duck_purchase_price": 25000.0,
                "duck_count": 4,
                "actual_provenance": {"duck_purchase_price": "DERIVED_ACTUAL"},
            }
        ]
    )
    result = build_purchase_comparator(reconstruction)
    assert result["effective_n"] == 0
    assert result["provenance_counts"]["DERIVED_ACTUAL"] == 1
