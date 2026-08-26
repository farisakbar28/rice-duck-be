# R2 IJoST Manuscript Fact Package

> **Role:** `CURRENT_AUTHORITATIVE` publication-safe factual source package.
> **This file is not the manuscript and is not a final DOCX.**
> **Release:** `R2_PHASE6_TECHNICAL_EMPIRICAL_RELEASE_CLOSED_WITH_LIMITATIONS`.

This package contains facts that may be used when regenerating a manuscript.
Interpretive claims must remain bounded by the evidence and terminology rules
below. Historical comparator evidence was not used to fit or recalibrate R2.

## A. Scientific identity

| Item | Fact |
|---|---|
| Model version | `R2` |
| Parameter registry | `R2-2026-08-26.3` |
| Freeze | `R2-FREEZE-2026-08-26.5` |
| Scientific target SHA | `b10b0a1f83357c5db1d6cdfb9c41eaa84b6727a7` |
| Original official evidence commit | `eda6a8035b89174e225999dec3aac0ec98685510` |
| F-03 correction commit | `d2aa2f833bfa2c943b2d8266a05edf96fd5d78db` |
| Phase-6E sign-off commit | `186ebf9f4542cd056f69d6b7639f9870c5372959` |
| Release status | `R2_PHASE6_TECHNICAL_EMPIRICAL_RELEASE_CLOSED_WITH_LIMITATIONS` |

The freeze denotes an immutable validation target. It does not denote universal
validation, high accuracy, completeness, or final expert validation.

## B. Model novelty/design facts

Publication-safe design facts are:

- R2 separates biological state, applicability support, provenance, and
  economic availability in a seven-input rice-duck DSS.
- The Phase-6 yield branch is range-aware and fail-closed: a pooled external
  rice-duck reference is applied only inside an explicitly supported age,
  density, and cultivar-group domain.
- The model exposes a literature evidence envelope and preserves its distinction
  from statistical uncertainty intervals.
- The economic ledger distinguishes paddy cash revenue, terminal duck asset
  value, available-cost subtotal, core margin, and unavailable full profit.
- These are model-design and software-governance facts; they are not claims of
  universal biological or geographic generalizability.

## C. Phase-6 external evidence basis

The active external evidence is literature-uncalibrated:

| Evidence item | Fact and limitation |
|---|---|
| `INPARI_GROUP` baseline | ref/low/high `53.5 / 20.0 / 78.4 kg/are`; external Indonesian field distribution, N=43; not Bali calibration |
| `SERTANI_GROUP` baseline | ref/low/high `44.5 / 22.3 / 66.7 kg/are`; two external locations; `LOW_EVIDENCE_TWO_LOCATION_EXTERNAL_RANGE` |
| `F_RD_ref` | `1.028`, pooled external rice-duck reference; not a density, system, release, or cultivar coefficient |
| Domain gate | Age `21–30` days; Jajar Legowo density `2–4` ducks/are; Tegel density `2–3` ducks/are; approved cultivar-group aliases only |

The evidence sources are non-comparator parameter sources. The historical clean
recap is not a calibration source.

## D. Methods facts

- The public request has seven user concepts: area, duck count, planting date,
  planting system, rice variety, duck age, and optional duck purchase price.
- Area is normalized as `A_m2 = 100*A_are`; density is `d = J/A_are`.
- Missing/null duck purchase price resolves to Rp26,500/duck; supplied positive
  values pass through.
- Age and density are support classifiers, not numerical yield multipliers.
- Conditional survival is `lambda_eff=0.90` only when age and density are both
  supported; then `N_survive=floor(J*lambda_eff)`.
- Yield reference, low, and high values are area-scaled from the approved
  cultivar-group records and `F_RD_ref`.
- The low/high values are named `LITERATURE_EVIDENCE_ENVELOPE`.
- All input and comparator values carry explicit provenance. Missing is not zero.
- Point metrics are computed only over numeric predicted rows; prediction
  coverage retains all eligible actuals in its denominator.
- Uncertainty around aggregate metrics uses cluster bootstrap by
  `farmer_cluster_id`, 2,000 resamples, seed `20260826`, empirical percentiles
  2.5/97.5.

## E. Validation cohort

The reconstructed source has 44 raw cycles, 36 clean cycles, and 8 excluded
stress cycles. The strict supported-domain cohort has 17 cycles. Calendar
validation has 12 cycles with both planting/transplanting and harvest dates
observed. The active yield comparator has 36 actual-eligible rows and 22
numeric predictions; 14 eligible rows are scientifically unavailable under the
frozen gate.

## F. Primary yield result

Among the 22 numerically predicted cycles:

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
| Envelope-contained outcomes | `20/22` |
| Literature evidence-envelope coverage | `90.9090909090909%` |
| Mean envelope width | `47.60574545454545 kg/are` |
| Median envelope width | `45.6432 kg/are` |

Publication interpretation: the result shows moderate retrospective point error
among numerically predicted cycles, slight mean overprediction, high containment
within a broad evidence envelope, and limited point precision. Negative R² is
diagnostic only; it indicates little explained cycle-to-cycle variation relative
to a constant-mean benchmark and does not mean negative accuracy.

## G. Subgroup result

| Subgroup | Actual N | Predicted N | Coverage | MAE | RMSE | WAPE | Envelope coverage | Qualification |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Strict supported domain | 17 | 17 | 100% | 9.855426004470589 | 14.436931455685956 | 23.478704172402782% | 88.23529411764706% | Restriction did not improve point performance |
| `INPARI_GROUP` | 5 | 3 | 60% | 8.309602693333334 | 10.467747785900904 | 17.60201414199902% | 100% | Very small numeric prediction N=3 |
| `SERTANI_GROUP` | 31 | 19 | 61.29032258064516% | 9.322029107157894 | 13.83058101193071 | 21.206653635894305% | 89.47368421052632% | `LOW_EVIDENCE_TWO_LOCATION_EXTERNAL_RANGE` |
| Jajar Legowo | 32 | 20 | 62.5% | 8.8949165408 | 13.481510495508598 | 19.96657912338301% | 90% | Secondary subgroup |
| Tegel | 4 | 2 | 50% | not reported | not reported | not reported | count-only | `COUNT_ONLY_SMALL_N` |

## H. Calendar result

The calendar result is N=`12`, hits=`4`, window coverage
`33.33333333333333%`, mean distance=`5` days, and median distance=`5` days.
Semantics are `HST_FROM_FIELD_TRANSPLANTING` with status
`VALIDATION_ASSUMPTION`. This is a calendar-window diagnostic, not model
accuracy.

## I. Revenue diagnostic

These are value diagnostics over 36 eligible actual rows and 22 numeric yield
predictions. The current-HPP diagnostic uses the Rp6,500/kg regulatory
benchmark. The price-neutral diagnostic uses observed historical paddy price as
comparator metadata only.

| Diagnostic | MAE Rp/cycle | RMSE Rp/cycle | MedAE Rp/cycle | MBE Rp/cycle | WAPE |
|---|---:|---:|---:|---:|---:|
| `CURRENT_HPP_OPERATIONAL_VALUE_DIAGNOSTIC` | 311527.7986064933 | 420128.394071854 | 254786.2200136502 | 41782.65592655224 | 16.576559236396317% |
| `PRICE_NEUTRAL_HISTORICAL_PRICE_DIAGNOSTIC` | 297042.3196077955 | 400883.6711827306 | 241702.28101260017 | 30976.365834068216 | 15.987950881921265% |

Neither diagnostic is historical realized-revenue accuracy or profit accuracy.

## J. Unavailable components

Publication-safe availability statements are:

- survival has `NO_COMPATIBLE_AGGREGATE_GROUND_TRUTH`;
- feed is `NOT_EVALUABLE`;
- total cage cost is `UNAVAILABLE`;
- infrastructure has `NO_METRIC`;
- weed has `NO_MONETARY_AGGREGATE`;
- pest has `SPARSE_CASE_DIAGNOSTICS_ONLY`;
- fertilizer is `DESCRIPTIVE_ONLY`;
- full profit is `UNAVAILABLE` because the configured cost ledger is incomplete;
- terminal duck value is an asset value, not realized cash revenue.

## K. F-03 methodological correction disclosure

Historical yield values were deterministic kg/are derivations from directly
recorded harvested-gabah quantity and direct program rice area. The validation
provenance layer initially treated formula cells as non-direct actuals. A
source-semantic audit established their admissibility before residual-based row
selection. The `DERIVED_ACTUAL` provenance label was retained, while semantic
admissibility was represented separately. The correction changed validation
eligibility only; it did not change the frozen model or parameters.

## L. Limitations

- The external yield evidence is not Bali calibration; Sertani evidence covers
  only two external locations.
- The broad evidence envelope should not be read as point precision or a
  statistical uncertainty interval.
- Prediction coverage is 22/36, not complete coverage of the clean cohort.
- The strict-domain subgroup does not improve point metrics.
- The Inpari subgroup has only three predictions and Tegel is count-only.
- Calendar timing uses a field-transplanting interpretation as a validation
  assumption.
- No compatible aggregate survival ground truth exists.
- Full profit remains unavailable because feed and cage-total evidence is
  incomplete.
- The evidence does not establish generalizability across Indonesia or Bali.

## M. Expert-final pending status

`EXPERT_FINAL_REVIEW=PENDING_NON_BLOCKING_EVIDENCE_STREAM`. Earlier expert and
development evidence is retained only according to documented
parameter-specific transferability. Final expert judgement of the frozen
Phase-6 configuration was not performed and was not used for parameter
selection, comparator eligibility, or retrospective metric calculation.

## N. Terminology blacklist

Do not use these claims or labels for the current release:

- “90.91% accuracy”;
- “model accuracy = 90.91%”;
- “33.33% accuracy” for calendar;
- “validated profit”;
- “full profit prediction”;
- “Bali-calibrated yield baseline”;
- “F_RD calibrated using Astungkara data”;
- “expert-validated Phase-6 yield”;
- “highly accurate”;
- “generalizable across Indonesia/Bali”;
- “prediction interval” for the literature evidence envelope;
- “95% confidence interval” for the cluster-bootstrap empirical intervals,
  unless a genuinely matching statistical construct is being discussed.

## O. Claims that are supported

Carefully bounded claims supported by the evidence include:

- the frozen Phase-6 model produced numeric yield estimates for 22 of 36 clean
  historical cycles under the supported-domain gate;
- point-estimate MAE was `9.183970959818181 kg/are` among predicted cycles;
- WAPE was `20.68403714256823%` among predicted cycles;
- mean bias was positive `2.606386759818184 kg/are`;
- the external literature evidence envelope contained 20/22 actual outcomes and
  had broad mean/median widths of `47.60574545454545`/`45.6432 kg/are`;
- calendar window coverage was 4/12 under the stated transplanting-date
  validation semantics;
- strict observed purchase-price comparator N was 27;
- full profit remained unavailable because the configured ledger was incomplete;
- no comparator outcome was used to recalibrate scientific parameters after
  freeze;
- final expert assessment remains pending and was not used in the retrospective
  empirical results.

## P. Claims that are not supported

The evidence does not support claims of 90% model accuracy, universal accuracy,
validated or complete profit, a prediction/confidence interval represented by
the literature envelope, final expert validation, Bali calibration of the
yield baseline or F_RD, causal monetary weed/pest savings, aggregate survival
accuracy, or generalizability across Indonesia/Bali.

## Q. Exact cross-source result ledger

This ledger is included so later manuscript regeneration cannot silently drift
from the mathematical-model and validation-methodology sources.

| Item | Exact result |
|---|---|
| Yield | actual N=`36`; predicted N=`22`; coverage=`61.111111111111114%`; MAE=`9.183970959818181`; RMSE=`13.421718631571618`; MedAE=`6.162351085000001`; MBE=`+2.606386759818184`; WAPE=`20.68403714256823%`; MAPE=`46.662702734492015%`; diagnostic R²=`-0.05747750232820392`; envelope=`20/22 = 90.9090909090909%` |
| Bootstrap | MAE `[5.338547626190476, 14.255541432705883]`; RMSE `[7.48075664347243, 19.285367878437786]`; MBE `[-2.391187468095236, 8.891407133200001]`; WAPE `[11.282456480039396, 36.907197894190645]`; envelope `[0.75, 1.0]`; cluster `farmer_cluster_id`; resamples `2000`; seed `20260826` |
| Calendar | N=`12`; hits=`4`; coverage=`33.33333333333333%`; mean/median distance=`5` days; `HST_FROM_FIELD_TRANSPLANTING`; `VALIDATION_ASSUMPTION` |
| Purchase | `OBSERVED_VALUE=27`; `DERIVED_ACTUAL=2`; `EXPLICIT_ZERO=4`; `MISSING_UNKNOWN=3`; `LEGACY_IMPUTATION=0`; strict N=`27` |
| Revenue | Current-HPP MAE/RMSE/MedAE/MBE/WAPE=`311527.7986064933`/`420128.394071854`/`254786.2200136502`/`41782.65592655224`/`16.576559236396317%`; price-neutral=`297042.3196077955`/`400883.6711827306`/`241702.28101260017`/`30976.365834068216`/`15.987950881921265%`; both N actual=`36`, predicted=`22` |
| Expert final | `EXPERT_FINAL_REVIEW=PENDING_NON_BLOCKING_EVIDENCE_STREAM` |
