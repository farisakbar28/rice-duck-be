# R2 Final Validation Methodology Source

> **Role:** `CURRENT_AUTHORITATIVE` export source for later validation-
> methodology DOCX generation.
> **This file is not the final DOCX.**
> **Release:** `R2_PHASE6_TECHNICAL_EMPIRICAL_RELEASE_CLOSED_WITH_LIMITATIONS`.

## 1. Validation philosophy and scope

R2 validation separates computational implementation verification,
retrospective comparison, domain/robustness checks, and expert evidence
transfer. A comparator discrepancy is reported as a scientific result; it is
not permission to change a frozen coefficient. Historical recap data are
comparator evidence only.

This methodology applies to the frozen target:

| Item | Value |
|---|---|
| Model version | `R2` |
| Parameter registry | `R2-2026-08-26.3` |
| Freeze | `R2-FREEZE-2026-08-26.5` |
| Scientific target SHA | `b10b0a1f83357c5db1d6cdfb9c41eaa84b6727a7` |
| Original official evidence commit | `eda6a8035b89174e225999dec3aac0ec98685510` |
| F-03 correction commit | `d2aa2f833bfa2c943b2d8266a05edf96fd5d78db` |
| Phase-6E sign-off commit | `186ebf9f4542cd056f69d6b7639f9870c5372959` |

## 2. Freeze-before-comparator rule

Before accessing comparator outcomes, the following were fixed and recorded:

- model version and parameter registry version;
- frozen target and actual backend commit;
- active formula and pending/unavailable formula lists;
- lookup and regulatory-price versions;
- source-workbook fingerprints and cohort reconstruction;
- the no-recalibration/production-isolation guard.

The frozen Phase-6 target was executed before the corrected provenance review.
The F-03 correction admitted semantically eligible actual cells and reused the
original frozen runtime predictions. It did not rerun the model, select rows
from residuals, change coefficients, create a new freeze, or perform a new
real comparator run.

## 3. Source roles

| Source role | Treatment |
|---|---|
| Raw recap, 44 cycles | Provenance and zero-versus-missing reconstruction |
| Clean comparator, 36 cycles | Primary retrospective comparator cohort |
| Excluded/stress, 8 cycles | Separate robustness/context set; never headline metrics |
| Legacy simulation workbook | Audit-only; never parameter, prediction, or comparator source |
| Local data collection and approved external literature | R2 parameter/evidence provenance, not comparator outcomes |

The workbooks are not used for fitting, median baselines, multiplier selection,
LOFO calibration, or post-hoc tuning.

## 4. Cohort reconstruction

The source reconstruction is 44 raw / 36 clean / 8 excluded. The strict
supported-domain yield cohort is 17. Calendar eligibility is 12 because both
planting/transplanting and harvest dates must be observed. Repeated farmers are
represented through anonymous `farmer_cluster_id` values for uncertainty
resampling.

The clean yield cohort has 36 actual-eligible outcomes after the F-03
source-semantic admissibility decision. Only 22 receive numeric predictions
under the frozen supported-domain gate, so coverage is computed as
`N_predicted / N_total_actual_eligible`, while point metrics use the 22
predicted rows.

## 5. Provenance vocabulary

### 5.1 Input provenance

Each replay input is labelled `OBSERVED`, `LOCAL_DEFAULT`,
`VALIDATION_ASSUMPTION`, or `UNAVAILABLE`. Missing is not zero.

### 5.2 Comparator provenance

Each actual/comparator value is labelled `OBSERVED_VALUE`, `EXPLICIT_ZERO`,
`MISSING_UNKNOWN`, `DERIVED_ACTUAL`, or `LEGACY_IMPUTATION`.

`NULL != 0`, `UNRECORDED != 0`, and `LEGACY_IMPUTATION != GROUND_TRUTH`.
Admissibility is a separate semantic boolean; a provenance label is not
silently rewritten when a value is admitted.

## 6. Input and model provenance

The active scientific identity and parameters are sourced from the R2 seed,
SSOT, registry, and provenance documents. The yield values are
`LITERATURE_UNCALIBRATED`: `Y_base` is 53.5/20.0/78.4 kg/are for
`INPARI_GROUP` and 44.5/22.3/66.7 kg/are for `SERTANI_GROUP`; the pooled
`F_RD_ref` is 1.028. Age and density are applicability gates, not fitted
moderators. The supported age is 21–30 days; supported densities are 2–4
ducks/are for Jajar Legowo and 2–3 ducks/are for Tegel.

## 7. F-01, F-02, and F-03 correction protocol

### F-01 — purchase provenance

Strict purchase comparison accepts positive directly observed unit prices only.
The final provenance counts are `OBSERVED_VALUE=27`, `DERIVED_ACTUAL=2`,
`EXPLICIT_ZERO=4`, `MISSING_UNKNOWN=3`, `LEGACY_IMPUTATION=0`. The strict
observed comparator is N=27. The two derived positive values remain contextual
accounting evidence and are excluded from strict N.

### F-02 — calendar/report semantics

Stale report prose was corrected to match the machine-readable calendar
evidence. The final calendar result is N=12, four window hits, coverage
`33.33333333333333%`, mean distance 5 days, and median distance 5 days under
`HST_FROM_FIELD_TRANSPLANTING` with status `VALIDATION_ASSUMPTION`.

### F-03 — yield actual admissibility

Historical yield values were deterministic kg/are derivations from directly
recorded harvested-gabah quantity divided by directly recorded program rice
area. The validation provenance layer initially treated every formula cell as a
non-direct actual. A source-semantic audit established admissibility before
residual-based row selection: all 36 rows have direct numeric precedents, no
model prediction, imputation, sale quantity, total-land substitution, or
unknown precedent. The `DERIVED_ACTUAL` label is retained; semantic
admissibility is separate. The correction changed validation eligibility only;
it did not change the frozen model or parameters.

This is a methodological provenance note, not a dramatic software-bug claim.

## 8. Yield actual admissibility and prediction coverage

The yield comparator accepts an actual only when it is an observed value or a
semantically verified deterministic derived value in kg/are. A derived yield is
eligible when direct harvested quantity in kg is divided by direct active
cultivated/program rice area in are. Legacy imputation, unverified zeros,
missing values, and non-admissible derivations are excluded.

For every eligible actual, the frozen runtime is replayed with the registered
seven-input semantics. Unsupported age/density/cultivar/F_RD conditions remain
scientifically unavailable. Unavailable predictions remain in the 36-row
coverage denominator but not in point-error numerators.

## 9. Yield metrics

For each compatible predicted row, with `e_i = pred_i - actual_i`:

```text
MAE   = mean(abs(e_i))
RMSE  = sqrt(mean(e_i^2))
MedAE = median(abs(e_i))
MBE   = mean(e_i)
WAPE  = sum(abs(e_i)) / sum(actual_i) * 100%
```

MAPE is supplementary only because low-yield denominators can make percentage
error unstable. R² is diagnostic only and is not substituted for absolute
error. The literature evidence envelope is evaluated separately:

```text
actual_inside_envelope = actual_i between [pred_low_i, pred_high_i]
```

Envelope containment is called `LITERATURE_EVIDENCE_ENVELOPE_COVERAGE`. It is
not accuracy, confidence-interval coverage, prediction-interval coverage, or a
formal uncertainty interval.

## 10. Cluster bootstrap

Uncertainty around aggregate validation metrics uses cluster resampling by
`farmer_cluster_id`, keeping all cycles in a sampled farmer cluster together.
The pre-registered configuration is 2,000 resamples, seed `20260826`, and
empirical percentiles 2.5/97.5. These are cluster-bootstrap empirical
intervals around aggregate validation metrics, not prediction intervals or
parameter confidence intervals.

## 11. Subgroups

Subgroup results are reported with their effective actual and predicted N.
Strict restriction is not interpreted as an improvement unless point metrics
actually improve. `INPARI_GROUP` requires a small-N qualifier when only three
predictions are available. `SERTANI_GROUP` always carries
`LOW_EVIDENCE_TWO_LOCATION_EXTERNAL_RANGE`. Tegel with two predictions is
`COUNT_ONLY_SMALL_N` and receives no aggregate error metrics.

## 12. Calendar method

Calendar validation uses only rows with both planting/transplanting and harvest
dates observed. `planting_date` is interpreted as field-transplanting date for
HST calculation, explicitly labelled `VALIDATION_ASSUMPTION`.

```text
Hit_i = 1 when actual harvest date is inside predicted window
Coverage = sum(Hit_i) / N
distance = 0 inside; otherwise distance to nearest window edge
```

Release, pull, and active-duration windows have no historical actual comparator
and receive no fabricated accuracy metric. Calendar coverage is a window-hit
diagnostic, not model accuracy.

## 13. Purchase validation

`C_duck_buy = J * p_duck_buy_eff` is deterministic accounting. The runtime
default Rp26,500 is a local/default input-resolution rule, not observed
historical purchase evidence. The strict observed-positive comparator N is 27;
the two `DERIVED_ACTUAL` purchase values are context only.

## 14. Revenue diagnostics

When yield is numerically available, two diagnostics are kept separate:

```text
CURRENT_HPP_OPERATIONAL_VALUE_DIAGNOSTIC
  predicted yield total * current regulatory HPP Rp6,500/kg

PRICE_NEUTRAL_HISTORICAL_PRICE_DIAGNOSTIC
  predicted yield total * observed historical paddy price
```

Historical price is comparator metadata only. These diagnostics are not
historical realized-revenue accuracy and do not evaluate profit.

## 15. Other component validation

- Survival: no compatible aggregate ground truth; do not use `N_sold` or duck
  sale revenue as survival actuals.
- Feed: runtime unavailable; no accuracy metric.
- Cage total: unavailable without capacity/unit-count rule.
- Infrastructure: no aggregate metric because historical constructs are not
  semantically compatible with the square-equivalent/per-unit runtime output.
- Weed: no monetary aggregate.
- Pest: sparse case diagnostics only.
- Fertilizer: descriptive baseline only.
- Full profit: unavailable while the cost ledger is incomplete.
- Terminal duck value: asset-value plausibility/sensitivity only, not cash-sale
  comparison.

## 16. Stress validation

The eight excluded cycles are executed separately when their seven required
inputs permit it. The final status is N=8, executed=5, input unavailable=3; all
executed outputs are finite, with no NaN or infinity. Stress outcomes are not
merged into clean-cohort headline metrics.

## 17. Computational V1 verification

V1 verifies implementation invariants and contracts, not predictive accuracy.
The Phase-6 evidence records 22/22 required checks passed, including
normalization, support boundaries, survival gates, calendar windows, nutrient
basis, fertilizer constraints, unavailable feed/cage/full-profit behavior,
range-aware yield arithmetic, source traceability, terminal-value separation,
and legacy import isolation.

## 18. Synthetic cases

Synthetic cases B01–B18 passed 18/18 through the canonical HTTP runtime path.
They verify supported and unsupported boundaries, exact reference/low/high
arithmetic, area scaling, source metadata, unavailable propagation, and
visualization/history semantics. Synthetic cases are contract evidence, not
field observations and not comparator outcomes.

## 19. Privacy and provenance governance

Committed artifacts may retain approved source filenames, SHA-256 fingerprints,
anonymous source-row identifiers, and anonymous farmer-cluster identifiers.
They must not contain raw workbook contents, farmer names, private mappings, or
the private `penelitian/` tree. The Phase-6 privacy audit passes under that
policy.

## 20. Anti-recalibration and expert evidence

The validation harness contains no fitting or optimization path, does not
rebind seed/registry identifiers, and does not import comparator outcomes into
production modules. No residual, MAPE, envelope miss, or subgroup result was
used to change a parameter. Any future scientific change requires a new model
or registry identity, a new freeze, and a new validation generation.

Earlier expert/development evidence is retained only according to its
parameter-specific transfer labels (`DIRECT`, `PARTIAL`, `NONE`). Final expert
assessment of the frozen Phase-6 configuration remains
`EXPERT_FINAL_REVIEW=PENDING_NON_BLOCKING_EVIDENCE_STREAM`; it was not used in parameter
selection, comparator eligibility, or retrospective metric calculation.

## 21. Canonical exact result ledger

This section is evidence status, not a model-parameter definition. It must
agree with `R2_FINAL_MATHEMATICAL_MODEL_SOURCE.md` and
`R2_IJOST_MANUSCRIPT_FACT_PACKAGE.md`.

### 21.1 Primary yield result

| Metric | Exact result |
|---|---:|
| Actual eligible N | `36` |
| Predicted N | `22` |
| Prediction coverage | `61.111111111111114%` |
| MAE | `9.183970959818181 kg/are` |
| RMSE | `13.421718631571618 kg/are` |
| MedAE | `6.162351085000001 kg/are` |
| MBE | `+2.606386759818184 kg/are` |
| WAPE | `20.68403714256823%` |
| Supplementary MAPE | `46.662702734492015%` |
| Diagnostic R² | `-0.05747750232820392` |
| Envelope-covered outcomes | `20/22` |
| Literature evidence-envelope coverage | `90.9090909090909%` |
| Mean envelope width | `47.60574545454545 kg/are` |
| Median envelope width | `45.6432 kg/are` |

### 21.2 Subgroups

| Subgroup | Actual N | Predicted N | Coverage | MAE | RMSE | WAPE | Envelope coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| Strict supported domain | 17 | 17 | 100% | 9.855426004470589 | 14.436931455685956 | 23.478704172402782% | 88.23529411764706% |
| `INPARI_GROUP` | 5 | 3 | 60% | 8.309602693333334 | 10.467747785900904 | 17.60201414199902% | 100% |
| `SERTANI_GROUP` | 31 | 19 | 61.29032258064516% | 9.322029107157894 | 13.83058101193071 | 21.206653635894305% | 89.47368421052632% |
| Jajar Legowo | 32 | 20 | 62.5% | 8.8949165408 | 13.481510495508598 | 19.96657912338301% | 90% |
| Tegel | 4 | 2 | 50% | not reported | not reported | not reported | count-only |

### 21.3 Bootstrap

| Metric | Exact interval |
|---|---:|
| MAE | `[5.338547626190476, 14.255541432705883]` |
| RMSE | `[7.48075664347243, 19.285367878437786]` |
| MBE | `[-2.391187468095236, 8.891407133200001]` |
| WAPE | `[11.282456480039396, 36.907197894190645]` |
| Literature evidence-envelope coverage | `[0.75, 1.0]` |

Configuration: cluster `farmer_cluster_id`; resamples `2000`; seed `20260826`;
empirical percentiles `2.5 / 97.5%`.

### 21.4 Calendar, purchase, and revenue

| Item | Exact result |
|---|---|
| Calendar | N=`12`; hits=`4`; coverage=`33.33333333333333%`; mean/median distance=`5` days; `HST_FROM_FIELD_TRANSPLANTING`; `VALIDATION_ASSUMPTION` |
| Purchase | `OBSERVED_VALUE=27`; `DERIVED_ACTUAL=2`; `EXPLICIT_ZERO=4`; `MISSING_UNKNOWN=3`; `LEGACY_IMPUTATION=0`; strict N=`27` |
| Current-HPP revenue diagnostic | N actual=`36`, predicted=`22`; MAE=`311527.7986064933`; RMSE=`420128.394071854`; MedAE=`254786.2200136502`; MBE=`41782.65592655224`; WAPE=`16.576559236396317%` Rp/cycle |
| Price-neutral revenue diagnostic | N actual=`36`, predicted=`22`; MAE=`297042.3196077955`; RMSE=`400883.6711827306`; MedAE=`241702.28101260017`; MBE=`30976.365834068216`; WAPE=`15.987950881921265%` Rp/cycle |
| Expert final | `EXPERT_FINAL_REVIEW=PENDING_NON_BLOCKING_EVIDENCE_STREAM` |

## 22. Methodological disposition

Phase 6E verdict: `APPROVE_PHASE6_TECHNICAL_EMPIRICAL_VALIDATION_WITH_LIMITATIONS`.
The current release is technically and retrospectively closed with explicit
limitations. It is not fully validated, universally validated, or final
expert-validated. No new comparator run, no literature search, no recalibration,
and no DOCX generation belongs to this source-closure task.
