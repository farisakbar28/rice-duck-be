"""Fixture construction policies + fixture manifest (task §13–§19, §32).

Mode A reality: only the raw recap workbook is locally available; the clean
comparator workbook (36 keep + 8 excluded) is NOT. Cohort fixtures therefore
MUST NOT be fabricated. This module emits an honest fixture manifest that:

  * records fingerprints/roles of whatever sources exist;
  * marks cohort construction BLOCKED_SOURCE_FILES_MISSING when the clean
    workbook is absent (no reconstruction from docs/memory -- task §10);
  * fixes, BEFORE any residual inspection, the deterministic validation
    anchor planting date and the supported-age replay assumptions;
  * documents field-level input provenance and comparator provenance rules.
"""

from __future__ import annotations

from validation.source_loader import (
    EMPIRICAL_SOURCE_STATUS_BLOCKED,
    ROLE_CLEAN_COHORT,
    ROLE_RULES,
    SourceFile,
    empirical_source_status,
)

# Fixed BEFORE residual inspection (task §17). Used ONLY to satisfy the
# mandatory planting-date API field for non-calendar replay outputs; its
# generated calendar dates are never calendar-validation evidence.
VALIDATION_ANCHOR_PLANTING_DATE = "2025-01-01"

# Supported-age replay assumptions (task §16): historical duck age was never
# observed; both values are SUPPORTED by R2, so numeric outputs must be
# invariant between them. Neither is observed ground truth.
SUPPORTED_AGE_ASSUMPTIONS_DAYS = (21, 30)

INPUT_PROVENANCE_VOCAB = (
    "OBSERVED",
    "LOCAL_DEFAULT",
    "VALIDATION_ASSUMPTION",
    "UNAVAILABLE",
)
COMPARATOR_PROVENANCE_VOCAB = (
    "OBSERVED_VALUE",
    "EXPLICIT_ZERO",
    "MISSING_UNKNOWN",
    "DERIVED_ACTUAL",
    "LEGACY_IMPUTATION",
)
SEVEN_INPUT_FIELDS = (
    "land_area_are",
    "duck_count",
    "planting_date",
    "planting_system",
    "rice_variety",
    "duck_age_days",
    "p_duck_buy",
)

PRIOR_AUDIT_COUNTS = {
    # Previously audited numbers (docs/06 section 3/5.2); hypotheses to
    # RE-VERIFY from source, never assumptions to reuse blindly.
    "raw_total": 44,
    "clean_keep": 36,
    "excluded_stress": 8,
    "strict_supported_domain": 17,
    "calendar_eligible_both_dates": 12,
}


def build_fixture_manifest(sources: dict[str, SourceFile]) -> dict:
    clean_present = sources[ROLE_CLEAN_COHORT].present
    status = empirical_source_status(sources)
    blocked = status == EMPIRICAL_SOURCE_STATUS_BLOCKED or not clean_present

    def cohort_state(expected_key: str) -> dict:
        return {
            "expected_from_prior_audit": PRIOR_AUDIT_COUNTS[expected_key],
            "verified_from_source": False,
            "status": (
                "BLOCKED_SOURCE_FILES_MISSING" if blocked else "PENDING_VERIFICATION"
            ),
            "note": (
                "Counts are NEVER assumed into existence; they must be "
                "recomputed from the clean comparator workbook."
            ),
        }

    return {
        "empirical_source_status": status,
        "sources": {role: src.to_dict() for role, src in sources.items()},
        "cohort_metadata": {
            "all_clean": cohort_state("clean_keep"),
            "excluded_stress": cohort_state("excluded_stress"),
            "strict_supported_domain": cohort_state("strict_supported_domain"),
            "calendar_eligible_both_observed_dates": cohort_state(
                "calendar_eligible_both_dates"
            ),
        },
        "input_policy": {
            "fields": list(SEVEN_INPUT_FIELDS),
            "provenance_vocab": list(INPUT_PROVENANCE_VOCAB),
            "rules": [
                "Never store a bare numeric value without its provenance tuple.",
                "OBSERVED is never inferred from a cleaned/defaulted cell.",
                "Missing/ambiguous/non-positive historical p_duck_buy -> request "
                "null (runtime default Rp26,500), provenance LOCAL_DEFAULT; such "
                "rows are excluded from observed purchase-price comparators.",
                "Historical zero price is never reinterpreted as a valid R2 "
                "zero-price input (task §19).",
                f"Supported-age replay uses {list(SUPPORTED_AGE_ASSUMPTIONS_DAYS)} "
                "days, each marked VALIDATION_ASSUMPTION; numeric invariance "
                "between them is asserted at runtime.",
                f"Rows lacking an observed planting date use anchor "
                f"{VALIDATION_ANCHOR_PLANTING_DATE} "
                "(VALIDATION_ASSUMPTION) solely to execute non-calendar outputs; "
                "anchor-generated calendar dates never enter calendar metrics.",
                "Strict supported-domain cohort requires OBSERVED system AND "
                "Jarwo d in [2,4] / Tegel d in [2,3]; defaulted-system rows are "
                "excluded from strict-domain N (task §18).",
            ],
        },
        "comparator_policy": {
            "provenance_vocab": list(COMPARATOR_PROVENANCE_VOCAB),
            "rules": [
                "NULL != 0; UNRECORDED != 0; LEGACY_IMPUTATION != GROUND_TRUTH.",
                "Ambiguous clean-workbook zeros stay MISSING_UNKNOWN unless the "
                "raw recap proves an explicit recorded zero (EXPLICIT_ZERO).",
                "Residuals are computed ONLY where a semantic-compatibility "
                "eligibility mask is true.",
            ],
        },
        "privacy": {
            "farmer_cluster_ids": "F001..Fnnn deterministic pseudonyms",
            "private_mapping_location": "validation/local/ (gitignored)",
            "forbidden_in_committed_artifacts": [
                "full farmer name",
                "phone number",
                "email address",
                "postal address",
            ],
        },
        "roles_enforcement": {
            role: {"allowed_use": rule["allowed_use"],
                   "forbidden_use": rule["forbidden_use"]}
            for role, rule in ROLE_RULES.items()
        },
    }
