# R2 Phase 6 Technical-Empirical Signoff

Status: `APPROVE_PHASE6_TECHNICAL_EMPIRICAL_VALIDATION_WITH_LIMITATIONS`

This document records the independent Phase-6E audit of the frozen R2 comparator validation and the Phase-6D provenance correction. It is evidence-only. It does not change the model, parameters, freeze, or calibration state.

## 1. Identity and scope

| Item | Value |
|---|---|
| Model version | `R2` |
| Parameter registry | `R2-2026-08-26.3` |
| Freeze ID | `R2-FREEZE-2026-08-26.5` |
| Scientific target | `b10b0a1f83357c5db1d6cdfb9c41eaa84b6727a7` |
| Original official evidence commit | `eda6a8035b89174e225999dec3aac0ec98685510` |
| Correction/review HEAD | `d2aa2f833bfa2c943b2d8266a05edf96fd5d78db` |
| Original run | `20260826T202953Z_b10b0a1` |
| Corrected evidence run | `20260826T202953Z_b10b0a1_phase6dr` |

The target-to-official commit is an evidence/freeze-manifest transition. The official-to-correction commit changes validation/test implementation and adds corrected evidence artifacts only. No application code or scientific documents changed across the target-to-review comparison.

The named `docs/02_R2_ENGINE_SPEC.md` path is absent at both target and review HEAD. The repository contains `docs/02_R2_BACKEND_MIGRATION_PLAN.md`; therefore, content-level audit claims for the named engine-spec path are unavailable and are retained as a documentation/guard limitation.

## 2. Correction integrity

The correction is a post-exposure semantic provenance adjudication. All 36 clean-cohort yield actuals are admitted as `DERIVED_ACTUAL` because the raw workbooks provide direct harvested gabah quantity divided by direct program rice area. The formula inventory is 35 relative `=AArow/Hrow` formulas and one absolute-reference variant `=$AA$12/H12`; the latter is mathematically and semantically identical for its row.

The source workbook audit found 36/36 row matches, direct numeric precedents for all numerator/denominator cells, positive denominators, no sales-quantity substitution, no total-land substitution, and a maximum raw-to-clean arithmetic difference of `4.803155206900556e-09 kg/are`. The source basis is described as gabah; no unsupported GKP/GKG or moisture harmonization is asserted.

Adjudication used no residuals, no MAE/RMSE/MAPE/WAPE or envelope threshold, no model-performance ranking, and no manually favorable row list. It performed no metric calculation for row selection, reran no model, changed no scientific coefficient, and created no new freeze. The five required correction files are byte-identical to the review HEAD; the binding status is `CORRECTION_WORKTREE_BOUND_TO_COMMIT`.

The original 15-file official run is byte-for-byte preserved. Its historical `NOT_EVALUABLE` revenue/yield conclusions remain historical evidence only; they are not used as the corrected conclusion.

## 3. Corrected yield evidence

The corrected yield diagnostic has 36 actual-eligible rows and 22 predicted rows, giving prediction coverage of `61.111111111111114%`. The 22 covered rows produce:

| Metric | Result |
|---|---:|
| MAE | `9.183970959818181 kg/are` |
| RMSE | `13.421718631571618 kg/are` |
| MedAE | `6.162351085000001 kg/are` |
| MBE | `2.606386759818184 kg/are` |
| WAPE | `20.68403714256823%` |
| Supplementary MAPE | `46.662702734492015%` |
| Diagnostic R2 | `-0.05747750232820392` |
| Literature-evidence envelope coverage | `20/22 = 90.9090909090909%` |
| Mean envelope width | `47.60574545454545 kg/are` |

Fourteen rows are scientifically unavailable under the frozen supported-domain/density policy, with zero HTTP execution failures. The strict supported-domain subgroup is 17 actual and 17 predicted rows; its MAE `9.855426004470589`, RMSE `14.436931455685956`, and WAPE `23.478704172402782%` do not improve on the overall covered diagnostic. No strict-cohort improvement claim is allowed.

Subgroup policy is explicit. `INPARI_GROUP` is quantitative but has only three predicted rows. `SERTANI_GROUP` is quantitative only with the required qualifier `LOW_EVIDENCE_TWO_LOCATION_EXTERNAL_RANGE`; it has 19 predicted rows and 89.47368421052632% envelope coverage. `Tegel` is count-only because it has two predicted rows. No subgroup result is treated as a universal pass/fail claim.

The independent recomputation reproduced yield, subgroup, and bootstrap metrics with zero meaningful mismatches. The cluster bootstrap used 2,000 resamples and seed `20260826`; the 95% intervals are MAE `[5.338547626190476, 14.255541432705883]`, RMSE `[7.48075664347243, 19.285367878437786]`, MBE `[-2.391187468095236, 8.891407133200001]`, WAPE `[11.282456480039396, 36.907197894190645]`, and envelope coverage `[0.75, 1.0]`.

The five required Phase-6 yield classifications remain separate:

- Computational implementation: verified by the committed implementation and 425 passing tests.
- Empirical point performance: corrected comparator diagnostic only; no universal pass/fail threshold.
- Supported-domain coverage: `22/36 = 61.111111111111114%`; 14 rows are scientifically unavailable.
- Literature-evidence envelope containment: `20/22 = 90.9090909090909%`; this is neither accuracy nor confidence-interval coverage.
- External-evidence transfer limitation: `LOW_EVIDENCE_TWO_LOCATION_EXTERNAL_RANGE`; no local Bali calibration claim is made.

## 4. Calendar, purchase, and revenue

Calendar validation has 12 eligible cases, four window hits, and `33.33333333333333%` window coverage, with mean and median distance of five days. Its timing status is `VALIDATION_ASSUMPTION`; it is a calendar-window coverage diagnostic, not model accuracy.

Purchase validation is `ELIGIBLE_OBSERVED_POSITIVE_ONLY`, with `N=27`. The two derived purchase values remain context and are excluded; nine rows are excluded from the strict positive-observed metric.

Revenue is reported as two separate diagnostics at current HPP `Rp6,500/kg`:

- `CURRENT_HPP_OPERATIONAL_VALUE_DIAGNOSTIC`: MAE `Rp311527.7986064933/cycle`, RMSE `Rp420128.394071854/cycle`, WAPE `16.576559236396317%`.
- `PRICE_NEUTRAL_HISTORICAL_PRICE_DIAGNOSTIC`: MAE `Rp297042.3196077955/cycle`, RMSE `Rp400883.6711827306/cycle`, WAPE `15.987950881921265%`.

The current HPP is an operational value diagnostic. Historical paddy prices are comparator metadata only. Neither diagnostic is historical realized-revenue accuracy, and the price-neutral metric is not a runtime price input.

## 5. Stress and component-wise status

Stress cases are evaluated separately: `N=8`, executed `5`, input-unavailable `3`, all executed outputs finite, and not merged into the headline.

| Surface | Status |
|---|---|
| Survival | `NO_COMPATIBLE_AGGREGATE_GROUND_TRUTH` |
| Feed | `NOT_EVALUABLE` |
| Cage total | `UNAVAILABLE` |
| Infrastructure | `NO_METRIC` |
| Weed | `NO_MONETARY_AGGREGATE` |
| Pest | `SPARSE_CASE_DIAGNOSTICS_ONLY` |
| Fertilizer | `DESCRIPTIVE_ONLY` |
| Full profit | `UNAVAILABLE` |
| Expert final | `PENDING` |

These statuses are not collapsed into a single accuracy score. The evidence supports technical validation of the executed comparator and correction, while empirical claims remain bounded by coverage, provenance, external-range evidence, and missing compatible ground truth.

## 6. QA, privacy, and disposition

The full test suite collected and passed 425 tests. `python -m compileall app validation` passed. The independent metric audit and original-run immutability audit passed. No tracked Phase-6 artifact contains raw private workbook contents or direct PII; only approved filenames, hashes, anonymous row identifiers, and anonymous cluster IDs are retained. Local farmer-ID mapping and the private `penelitian/` tree are ignored and untracked.

`CI_STATUS_NOT_RECORDED_FOR_CORRECTION_COMMIT`: no CI workflow/configuration is present locally, so no successful CI status is asserted.

Final disposition: approve Phase-6 technical-empirical validation with limitations. Expert final signoff remains pending. The corrected comparator evidence must not be described as universal production accuracy or used to justify post-hoc recalibration.

NO MODEL CHANGE.
NO PARAMETER CHANGE.
NO NEW FREEZE.
NO RECALIBRATION.
