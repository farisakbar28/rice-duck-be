# Phase 6E Independent Technical-Empirical Signoff

Status: `APPROVE_PHASE6_TECHNICAL_EMPIRICAL_VALIDATION_WITH_LIMITATIONS`

This file is an evidence-only signoff for the frozen R2 comparator validation. It does not authorize a model change, parameter change, new freeze, or recalibration.

## Identity and binding

- Model: `R2`
- Parameter registry: `R2-2026-08-26.3`
- Freeze: `R2-FREEZE-2026-08-26.5`
- Scientific target: `b10b0a1f83357c5db1d6cdfb9c41eaa84b6727a7`
- Original official evidence commit: `eda6a8035b89174e225999dec3aac0ec98685510`
- Correction/review HEAD: `d2aa2f833bfa2c943b2d8266a05edf96fd5d78db`
- Correction binding: `CORRECTION_WORKTREE_BOUND_TO_COMMIT`

The correction is a semantic provenance adjudication. It admits 36 semantically verified `DERIVED_ACTUAL` yield rows. It calculated no metrics during row selection, used no residuals or performance values, reran no model, changed no scientific coefficients, and created no new freeze.

## Reproducibility and QA

An independent basic-Python implementation reproduced corrected yield, subgroup, bootstrap, and revenue diagnostics with zero meaningful mismatches. The original 15-file official run remains byte-for-byte identical. The full test suite collected 425 tests and passed 425; `compileall` passed for `app` and `validation`.

`CI_STATUS_NOT_RECORDED_FOR_CORRECTION_COMMIT`: no CI workflow/configuration is present locally, so no successful CI status is asserted.

## Corrected yield diagnostic

The corrected comparator has 36 actual-eligible rows and 22 predicted rows: coverage `61.111111111111114%`. On the 22 covered rows:

- MAE: `9.183970959818181 kg/are`
- RMSE: `13.421718631571618 kg/are`
- MedAE: `6.162351085000001 kg/are`
- MBE: `2.606386759818184 kg/are`
- WAPE: `20.68403714256823%`
- Supplementary MAPE: `46.662702734492015%`
- Diagnostic R2: `-0.05747750232820392`
- Literature-evidence envelope coverage: `20/22 = 90.9090909090909%`
- Mean envelope width: `47.60574545454545 kg/are`

Fourteen rows are scientifically unavailable because the frozen supported-domain/density policy does not produce a prediction; `http_execution_failure_n=0`. The strict supported-domain cohort is 17 actual and 17 predicted rows, but it does not improve point metrics: MAE, RMSE, WAPE, and positive bias are higher than the overall covered diagnostic. No improvement claim is permitted.

The `SERTANI_GROUP` result requires the qualifier `LOW_EVIDENCE_TWO_LOCATION_EXTERNAL_RANGE`. The `Tegel` subgroup is count-only because only two predictions are available. The `INPARI_GROUP` quantitative result is explicitly small (`N=3` predictions).

These are comparator diagnostics, not universal production accuracy and not a universal statistical pass/fail threshold.

The required Phase-6 yield classifications are kept separate: computational implementation is verified by the committed implementation and passing tests; empirical point performance is a corrected comparator diagnostic; supported-domain coverage is 22/36; literature-evidence envelope containment is 20/22 and is not accuracy or confidence-interval coverage; external-evidence transfer is limited by `LOW_EVIDENCE_TWO_LOCATION_EXTERNAL_RANGE` and does not establish a local Bali calibration claim.

## Other validation surfaces

- Calendar: 12 eligible, 4 window hits, coverage `33.33333333333333%`; this is a `VALIDATION_ASSUMPTION` calendar-window diagnostic, not model accuracy.
- Purchase: positive observed-only metric, `N=27`; two derived purchase values remain context and are excluded.
- Revenue: operational current-HPP diagnostic MAE `Rp311527.7986064933/cycle`, WAPE `16.576559236396317%`; price-neutral historical-price diagnostic MAE `Rp297042.3196077955/cycle`, WAPE `15.987950881921265%`. Historical prices are comparator metadata only; these are not realized-revenue accuracy claims.
- Stress: evaluated separately, `N=8`, executed `5`, input-unavailable `3`, all executed outputs finite, not merged into the headline.
- Components: survival `NO_COMPATIBLE_AGGREGATE_GROUND_TRUTH`; feed `NOT_EVALUABLE`; cage total `UNAVAILABLE`; infrastructure `NO_METRIC`; weed `NO_MONETARY_AGGREGATE`; pest `SPARSE_CASE_DIAGNOSTICS_ONLY`; fertilizer `DESCRIPTIVE_ONLY`; full profit `UNAVAILABLE`; expert final `PENDING`.

## Limitations and disposition

The requested `docs/02_R2_ENGINE_SPEC.md` path is absent at both the scientific target and review HEAD; the repository contains `docs/02_R2_BACKEND_MIGRATION_PLAN.md` instead. This is recorded as a documentation/guard limitation. The available SSOT, parameter registry, provenance document, validation protocol, application code, and correction implementation were audited as unchanged or bound to the review commit.

The signoff therefore approves the Phase-6 technical-empirical validation with explicit limitations. It does not elevate comparator evidence into universal accuracy, and expert final signoff remains pending until compatible aggregate ground truth is available.

NO MODEL CHANGE.
NO PARAMETER CHANGE.
NO NEW FREEZE.
NO RECALIBRATION.
