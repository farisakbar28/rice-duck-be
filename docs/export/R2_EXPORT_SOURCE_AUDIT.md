# R2 Export-Source Audit

> **Role:** `CURRENT_AUTHORITATIVE` cross-source audit.
> **Audit status:** `PASS`.
> **Scope:** the three Phase-6 export sources and their committed R2 evidence.

This audit checks that the mathematical-model source, validation-methodology
source, and IJoST fact package agree on identity, active parameters, corrected
metrics, terminology, and expert-final governance. It does not generate DOCX
files and does not rerun the comparator.

## 1. Sources audited

| Source | Role |
|---|---|
| `docs/export/R2_FINAL_MATHEMATICAL_MODEL_SOURCE.md` | Model/equation export source |
| `docs/export/R2_FINAL_VALIDATION_METHODOLOGY_SOURCE.md` | Validation-methodology export source |
| `docs/export/R2_IJOST_MANUSCRIPT_FACT_PACKAGE.md` | Publication-safe fact source |
| `docs/14_R2_FINAL_RELEASE_CLOSURE.md` | Release-level reference and source map |
| `docs/01_R2_MODEL_SSOT.md` | Current mathematical SSOT |
| `docs/04_R2_PARAMETER_EXECUTION_REGISTRY.md` | Current parameter/execution registry |
| `validation/results/20260826T202953Z_b10b0a1_phase6dr/` | Corrected Phase-6D-R evidence |
| `validation/results/20260826T202953Z_b10b0a1_phase6e/` | Independent Phase-6E audit/sign-off |
| `validation/results/20260826T202953Z_b10b0a1/` | Preserved original Phase-6D audit evidence |

## 2. Identity consistency — PASS

All three export sources and the release closure agree on:

| Item | Required value |
|---|---|
| `MODEL_VERSION` | `R2` |
| `PARAMETER_REGISTRY_VERSION` | `R2-2026-08-26.3` |
| `FREEZE_ID` | `R2-FREEZE-2026-08-26.5` |
| Scientific target SHA | `b10b0a1f83357c5db1d6cdfb9c41eaa84b6727a7` |
| Original official evidence commit | `eda6a8035b89174e225999dec3aac0ec98685510` |
| F-03 correction commit | `d2aa2f833bfa2c943b2d8266a05edf96fd5d78db` |
| Phase-6E sign-off/current closure commit | `186ebf9f4542cd056f69d6b7639f9870c5372959` |

No source presents `.2`, `.3`, or `.4` as the current freeze. `.2` is
historical Phase-5C; `.3` and `.4` are intermediate Phase-6 lineage; `.5` is
current. No `.6` identity appears as an active or proposed release identity.

## 3. Parameter consistency — PASS

The three export sources agree with the active seed/SSOT/registry on:

| Parameter | Required value |
|---|---|
| `Y_base(INPARI_GROUP)` | ref/low/high `53.5 / 20.0 / 78.4 kg/are` |
| `Y_base(SERTANI_GROUP)` | ref/low/high `44.5 / 22.3 / 66.7 kg/are` |
| `F_RD_ref` | `1.028` |
| Supported age | `21–30` days inclusive |
| Jajar Legowo density | `2–4` ducks/are inclusive |
| Tegel density | `2–3` ducks/are inclusive |
| Survival | `lambda_safe_ref=0.90`, conditional on supported age and density |
| Calendar | harvest Sertani `[100,110]`, Inpari `[90,100]`; release `[21,30]`; pull `[56,60]`; active reference `32`, support `[28,40]` HST/days |
| Purchase default | Rp`26,500`/duck; local range Rp`25,000–28,000` |
| Paddy HPP benchmark | Rp`6,500`/kg |
| Terminal duck value | Rp`45,000`/duck; sensitivity Rp`30,000–60,000`; asset, not cash |
| Nutrient/fertilizer | N/P2O5/K2O `1.1761/0.2745/0.2745` kg/are; Urea 46%; NPK 15-10-12; HET `1800/1840` |

No comparator metric is represented as a model parameter. All three sources
retain `LITERATURE_UNCALIBRATED` for external yield evidence.

## 4. Corrected yield numeric consistency — PASS

The exact primary metrics below appear consistently in all three export
sources and match `independent_metric_audit.json`:

| Metric | Required exact value |
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
| Envelope containment | `20/22 = 90.9090909090909%` |
| Mean envelope width | `47.60574545454545 kg/are` |
| Median envelope width | `45.6432 kg/are` |

The subgroup values also agree:

| Subgroup | Actual N | Predicted N | Coverage | MAE | RMSE | WAPE | Envelope coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| Strict supported domain | 17 | 17 | 100% | 9.855426004470589 | 14.436931455685956 | 23.478704172402782% | 88.23529411764706% |
| `INPARI_GROUP` | 5 | 3 | 60% | 8.309602693333334 | 10.467747785900904 | 17.60201414199902% | 100% |
| `SERTANI_GROUP` | 31 | 19 | 61.29032258064516% | 9.322029107157894 | 13.83058101193071 | 21.206653635894305% | 89.47368421052632% |
| Jajar Legowo | 32 | 20 | 62.5% | 8.8949165408 | 13.481510495508598 | 19.96657912338301% | 90% |
| Tegel | 4 | 2 | 50% | not reported | not reported | not reported | count-only |

## 5. Bootstrap consistency — PASS

All three export sources agree that these are cluster-bootstrap empirical
intervals around aggregate validation metrics:

| Metric | Required interval |
|---|---:|
| MAE | `[5.338547626190476, 14.255541432705883]` |
| RMSE | `[7.48075664347243, 19.285367878437786]` |
| MBE | `[-2.391187468095236, 8.891407133200001]` |
| WAPE | `[11.282456480039396, 36.907197894190645]` |
| Literature evidence-envelope coverage | `[0.75, 1.0]` |

Configuration is `farmer_cluster_id`, 2,000 resamples, seed `20260826`,
empirical percentiles `2.5 / 97.5%`. No source calls these prediction
intervals or parameter confidence intervals.

## 6. Calendar, purchase, and revenue consistency — PASS

| Item | Required exact result |
|---|---|
| Calendar | N=`12`; hits=`4`; coverage=`33.33333333333333%`; mean/median distance=`5` days; `HST_FROM_FIELD_TRANSPLANTING`; `VALIDATION_ASSUMPTION` |
| Purchase | `OBSERVED_VALUE=27`; `DERIVED_ACTUAL=2`; `EXPLICIT_ZERO=4`; `MISSING_UNKNOWN=3`; `LEGACY_IMPUTATION=0`; strict N=`27` |
| Current-HPP revenue | N actual=`36`, predicted=`22`; MAE=`311527.7986064933`; RMSE=`420128.394071854`; MedAE=`254786.2200136502`; MBE=`41782.65592655224`; WAPE=`16.576559236396317%` Rp/cycle |
| Price-neutral revenue | N actual=`36`, predicted=`22`; MAE=`297042.3196077955`; RMSE=`400883.6711827306`; MedAE=`241702.28101260017`; MBE=`30976.365834068216`; WAPE=`15.987950881921265%` Rp/cycle |

The calendar percentage is window coverage, not model accuracy. The revenue
figures are operational/value diagnostics, not realized-revenue or profit
accuracy.

## 7. Claim consistency — PASS

All three export sources:

- frame the yield result as moderate retrospective error with limited point
  precision;
- distinguish high containment from a broad literature envelope;
- disclose the strict-domain non-improvement, small Inpari N, Sertani warning,
  and Tegel count-only policy;
- state that full profit is unavailable;
- disclose F-03 as a source-semantic eligibility correction;
- prohibit 90% accuracy, calendar accuracy, validated profit, Bali calibration,
  expert-validated yield, and unsupported interval terminology.

## 8. Expert-pending consistency — PASS

Every export source states the same governance fact:

`EXPERT_FINAL_REVIEW=PENDING_NON_BLOCKING_EVIDENCE_STREAM`

The sources also state that final expert judgement was not performed, is not a
release blocker, and was not used for parameter selection, comparator
eligibility, or retrospective metric calculation. Earlier expert/development
evidence is retained only according to its documented parameter-specific
transferability.

## 9. Evidence and privacy consistency — PASS

The export sources point to the corrected Phase-6D-R evidence and Phase-6E
independent audit. They do not introduce new empirical results, a new freeze,
a literature search, or private source material. The committed privacy audit
reports no raw private workbook contents or direct PII; only approved source
filenames, fingerprints, anonymous row IDs, and anonymous farmer-cluster IDs
are retained.

## 10. Final audit disposition

| Audit dimension | Result |
|---|---|
| Identity consistency | `PASS` |
| Parameter consistency | `PASS` |
| Numeric consistency | `PASS` |
| Claim consistency | `PASS` |
| Expert-pending consistency | `PASS` |
| Privacy/source-role consistency | `PASS` |
| Overall export-source audit | `PASS` |

`R2_EXPORT_SOURCE_AUDIT=PASS`.
