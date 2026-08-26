# R2 Final Release Closure

> **Role:** `CURRENT_AUTHORITATIVE` release-level documentation.
> **Release status:** `R2_PHASE6_TECHNICAL_EMPIRICAL_RELEASE_CLOSED_WITH_LIMITATIONS`.
> **Prepared from:** branch `master`, HEAD
> `186ebf9f4542cd056f69d6b7639f9870c5372959`.

This document closes the current R2 documentation package. It is the release
map for the frozen scientific model, the corrected retrospective evidence, and
the publication-source files. It does not change the model, parameters,
support boundaries, freeze identity, comparator rows, or validation results.

## 1. Release decision

Phase 6E approved the technical-empirical validation with limitations:
`APPROVE_PHASE6_TECHNICAL_EMPIRICAL_VALIDATION_WITH_LIMITATIONS`. The
Phase-6D-R corrected evidence is the authoritative retrospective yield and
revenue result; the original Phase-6D N=0 result is retained only as historical
audit evidence of F-03.

The final expert assessment is explicitly
`EXPERT_FINAL_REVIEW=PENDING_NON_BLOCKING_EVIDENCE_STREAM`. It has not been
performed, is not a release blocker, and was not used to select parameters,
determine comparator eligibility, or calculate retrospective results. Earlier
expert/development evidence is retained only through its documented
parameter-specific transfer labels.

This closure therefore does not claim `FULLY_VALIDATED`, universal validity,
final expert validation, 90% model accuracy, validated profit, or generality
across Bali/Indonesia.

## 2. Scientific identity and evidence chain

| Identity item | Final value | Role |
|---|---|---|
| `MODEL_VERSION` | `R2` | Scientific model generation |
| `PARAMETER_REGISTRY_VERSION` | `R2-2026-08-26.3` | Immutable parameter registry |
| `FREEZE_ID` | `R2-FREEZE-2026-08-26.5` | Immutable validation-target identity |
| `FREEZE_EFFECTIVE_FROM` | `2026-08-26` | Effective date |
| `MODEL_FROZEN` | `true` | Frozen validation target, not an accuracy claim |
| Scientific target SHA | `b10b0a1f83357c5db1d6cdfb9c41eaa84b6727a7` | Frozen R2 runtime/science |
| Original official evidence commit | `eda6a8035b89174e225999dec3aac0ec98685510` | Phase-6D evidence |
| F-03 correction commit | `d2aa2f833bfa2c943b2d8266a05edf96fd5d78db` | Validation provenance correction |
| Phase-6E sign-off commit | `186ebf9f4542cd056f69d6b7639f9870c5372959` | Independent approval and current HEAD |

The commit/evidence chain is:

1. `b10b0a1f83357c5db1d6cdfb9c41eaa84b6727a7` — final Phase-6C/D
   pre-comparator scientific target;
2. `eda6a8035b89174e225999dec3aac0ec98685510` — official frozen Phase-6D
   evidence, including the original run;
3. `d2aa2f833bfa2c943b2d8266a05edf96fd5d78db` — F-03 semantic provenance
   correction, with no scientific rerun or recalibration;
4. `186ebf9f4542cd056f69d6b7639f9870c5372959` — Phase-6E independent
   technical-empirical sign-off.

The original official run directory
`validation/results/20260826T202953Z_b10b0a1/` is immutable historical audit
evidence. The corrected result is in
`validation/results/20260826T202953Z_b10b0a1_phase6dr/`, and the independent
review is in
`validation/results/20260826T202953Z_b10b0a1_phase6e/`.

## 3. Documentation inventory and role matrix

All existing tracked Markdown documents and the new release-package Markdown
files were inventoried. Historical documents and evidence directories are not
rewritten to make their old result state appear current.

| Document | Role | Current interpretation |
|---|---|---|
| `README.md` | `SUPPORTING_REFERENCE` | Current user-facing repository overview and release links |
| `CHANGELOG.md` | `SUPPORTING_REFERENCE` | Current release notes plus explicitly historical version entries |
| `docs/00_R2_BACKEND_DOCUMENTATION_INDEX.md` | `CURRENT_AUTHORITATIVE` | Precedence, package map, and current Phase-6 entry point |
| `docs/01_R2_MODEL_SSOT.md` | `CURRENT_AUTHORITATIVE` | Mathematical and economic R2 source of truth |
| `docs/02_R2_BACKEND_MIGRATION_PLAN.md` | `IMPLEMENTATION_HISTORY` | Migration plan and pre-R2 audit; not a status dashboard |
| `docs/03_R2_API_CONTRACT.md` | `CURRENT_AUTHORITATIVE` | Production endpoint and response semantics |
| `docs/04_R2_PARAMETER_EXECUTION_REGISTRY.md` | `CURRENT_AUTHORITATIVE` | Active registry, availability states, and legacy invalidation |
| `docs/05_R2_PERSISTENCE_VERSIONING.md` | `CURRENT_AUTHORITATIVE` | Schema-v4 snapshot and Phase-6 persistence semantics |
| `docs/06_R2_TEST_VALIDATION_PROTOCOL.md` | `CURRENT_AUTHORITATIVE` | Validation rules and completed Phase-6 status |
| `docs/07_R2_LEGACY_INVALIDATION_REGISTER.md` | `CURRENT_AUTHORITATIVE` | Banned formula, field, and provenance register |
| `docs/08_R2_IMPLEMENTATION_CHECKLIST.md` | `IMPLEMENTATION_HISTORY` | Original migration checklist; current completion is in this document |
| `docs/09_R2_REPO_AUDIT_MANIFEST.md` | `HISTORICAL_AUDIT` | Pre-R2 repository audit snapshot at commit `2a4824d...` |
| `docs/10_R2_REFERENCE_PROVENANCE.md` | `CURRENT_AUTHORITATIVE` | Source and provenance registry for active R2 values |
| `docs/11_R2_FREEZE_MANIFEST.md` | `CURRENT_AUTHORITATIVE` | Final freeze lineage, execution gate, and anti-calibration rules |
| `docs/12_R2_TECHNICAL_VALIDATION_SIGNOFF.md` | `HISTORICAL_AUDIT` | Preserved Phase-5C `.2` sign-off |
| `docs/13_R2_PHASE6_TECHNICAL_EMPIRICAL_SIGNOFF.md` | `CURRENT_AUTHORITATIVE` | Phase-6E approval and corrected-evidence disposition |
| `docs/14_R2_FINAL_RELEASE_CLOSURE.md` | `CURRENT_AUTHORITATIVE` | Current release closure and publication-source map |
| `docs/export/R2_FINAL_MATHEMATICAL_MODEL_SOURCE.md` | `CURRENT_AUTHORITATIVE` | Mathematical-model source for later DOCX generation; not a DOCX |
| `docs/export/R2_FINAL_VALIDATION_METHODOLOGY_SOURCE.md` | `CURRENT_AUTHORITATIVE` | Validation-methodology source for later DOCX generation; not a DOCX |
| `docs/export/R2_IJOST_MANUSCRIPT_FACT_PACKAGE.md` | `CURRENT_AUTHORITATIVE` | Publication-safe factual source package; not a manuscript |
| `docs/export/R2_EXPORT_SOURCE_AUDIT.md` | `CURRENT_AUTHORITATIVE` | Cross-source identity, numeric, claim, and expert-status audit |
| `docs/tes_skenario_R2.md` | `SUPPORTING_REFERENCE` | Scenario, provenance, and runtime-evidence guidance |
| `tests/legacy_invalid/README.md` | `LEGACY_INVALIDATED` | Quarantined pre-R2 test semantics; never an active oracle |
| `validation/results/20260826T074343Z_39fd69f/validation_report.md` | `HISTORICAL_AUDIT` | Non-official Phase-5 pre-freeze report |
| `validation/results/20260826T102325Z_f14f5d9/validation_report.md` | `HISTORICAL_AUDIT` | Original official Phase-5C `.2` report |
| `validation/results/20260826T102325Z_f14f5d9/validation_report_stage_c_corrected.md` | `HISTORICAL_AUDIT` | Preserved F-01/F-02 correction report for `.2` |
| `validation/results/20260826T193654Z_88a1ebf/validation_report.md` | `HISTORICAL_AUDIT` | Non-official Phase-6 `.4` pre-freeze report |
| `validation/results/20260826T202953Z_b10b0a1/validation_report.md` | `HISTORICAL_AUDIT` | Original Phase-6D `.5` report; superseded yield/revenue conclusion |
| `validation/results/20260826T202953Z_b10b0a1_phase6dr/validation_report_phase6dr_corrected.md` | `CURRENT_AUTHORITATIVE` | Corrected Phase-6D-R retrospective evidence |
| `validation/results/20260826T202953Z_b10b0a1_phase6e/phase6e_validation_signoff.md` | `CURRENT_AUTHORITATIVE` | Independent Phase-6E approval evidence |

There is no tracked `docs/02_R2_ENGINE_SPEC.md`. Engine semantics are sourced
from the existing SSOT, API contract, registry, and implementation evidence.

## 4. Stale-claim audit

| Claim family | Resolution in current release |
|---|---|
| Yield always unavailable, coverage 0, or yield metrics pending | Resolved in current README, API/SSOT status text, protocol, and export sources. Such values remain only in clearly labelled historical reports. |
| Exact-node `F_RD` required | Resolved: current active configuration uses pooled `F_RD_ref=1.028` with supported-domain gates. The former exact-node design is labelled historical/superseded in the registry and protocol. |
| R2.3 only a candidate/not active | Resolved: registry `.3` and freeze `.5` are current; candidate wording remains only in implementation history or freeze lineage. |
| Freeze `.2`, `.3`, or `.4` presented as current | Resolved: `.2` is historical Phase-5C; `.3`/`.4` are intermediate lineage; `.5` is current. |
| Phase-6 comparator pending | Resolved: Phase-6D-R is corrected and Phase 6E approved with limitations. |
| Revenue diagnostic unavailable because yield is unavailable | Resolved: current-HPP and price-neutral diagnostics are reported separately below; historical pre-correction reports retain their original state. |
| Expert review required before release | Resolved: final expert review is `PENDING_NON_BLOCKING_EVIDENCE_STREAM`, not a release gate. |
| 90% accuracy or 33.33% calendar accuracy | Forbidden. Current text uses literature-envelope containment and calendar-window coverage, respectively. |
| Validated profit/full profit available | Resolved: full profit remains unavailable because the configured ledger is incomplete. |
| Old paddy price 6000, terminal duck price 52500, fixed yield 47.8767507, old profit formula, or `N_sold` survival proxy | Retained only as explicit legacy/audit material; prohibited as current R2 semantics. |

## 5. Final parameter consistency audit

The following values were cross-checked against `app/data/seed.py`, the active
SSOT/registry/provenance documents, the Phase-6D-R evidence, and the Phase-6E
independent audit. Result: **PASS — no model or parameter change**.

| Parameter or rule | Final value |
|---|---|
| `Y_base(INPARI_GROUP)` | ref `53.5`, low `20.0`, high `78.4` kg/are |
| `Y_base(SERTANI_GROUP)` | ref `44.5`, low `22.3`, high `66.7` kg/are |
| `F_RD_ref` | `1.028` |
| Supported duck age | `21–30` days inclusive |
| Jajar Legowo density | `2–4` ducks/are inclusive |
| Tegel density | `2–3` ducks/are inclusive |
| Conditional survival reference | `lambda_safe_ref=0.90`; only supported age and density |
| Release window | `21–30` HST |
| Pull/heading window | `56–60` HST |
| Active duration | reference `32` days; support `[28,40]` days |
| Duck purchase default/range | Rp`26,500`; local range Rp`25,000–28,000` |
| Paddy benchmark | Rp`6,500`/kg, regulatory HPP |
| Terminal duck value | Rp`45,000`/duck; sensitivity Rp`30,000–60,000`; asset, not cash |
| Nutrient baseline | N `1.1761`, P2O5 `0.2745`, K2O `0.2745` kg/are |
| Fertilizer products | Urea 46% N; NPK 15-10-12; HET Rp`1,800`/Rp`1,840` per kg |
| Net/fence | equivalent perimeter; price Rp`6,000–6,750`/m; life `2–3` cycles |
| Cage | Rp`150,000–200,000`/unit/cycle; total unavailable without capacity rule |
| Feed, manure credit, KCl, monetary weed/pest saving | unavailable or descriptive; no legacy fallback |

No comparator-derived value is present in the parameter registry. `Y_base` and
`F_RD_ref` are external literature evidence, explicitly
`LITERATURE_UNCALIBRATED`, not Bali calibration.

## 6. Final evidence-status matrix

| Component | Runtime execution state | Empirical comparator status | Evidence source | Effective N | Validation result type | Main limitation | Expert-final dependency | Release blocker? |
|---|---|---|---|---:|---|---|---|---|
| Yield | `ACTIVE_RANGE`; available only inside gate | `EVALUATED_CORRECTED` | Phase-6D-R corrected yield JSON/report; Phase-6E audit | actual 36 / predicted 22 | Retrospective point metrics plus literature-envelope containment | 14 rows unavailable; external envelope broad; limited precision | No | No |
| Calendar | `ACTIVE_RANGE` | `EVALUATED` | Original frozen `calendar_validation.json`; F-02 corrected report | 12 | Window-hit coverage and distance | `HST_FROM_FIELD_TRANSPLANTING` is `VALIDATION_ASSUMPTION` | No | No |
| Survival | `CONDITIONAL` | `NO_COMPATIBLE_AGGREGATE_GROUND_TRUTH` | Phase-6E sign-off; SSOT | No aggregate N | Deterministic gate/formula verification | Sales state cannot stand in for survival | No | No |
| Feed | `UNAVAILABLE` | `NOT_EVALUABLE` | Phase-6E sign-off; SSOT/registry | positive history N=23 context only | Availability status | Quantity and price lookups incomplete | No | No |
| Cage total | `UNAVAILABLE` | `NOT_EVALUABLE` | Phase-6E sign-off; SSOT/registry | No metric N | Fail-closed availability | Capacity/unit-count rule absent | No | No |
| Infrastructure | `ACTIVE_RANGE` | `NO_METRIC` | Phase-6E sign-off; SSOT/registry | Historical net 17 / cage 9 context only | Runtime range, no aggregate comparator | Historical constructs not semantically compatible | No | No |
| Weed | baseline `ACTIVE_RANGE`; saving unavailable | `NO_MONETARY_AGGREGATE` | Phase-6E sign-off; SSOT | 0 monetary aggregate | Descriptive/baseline only | Biological suppression is not a cash saving | No | No |
| Pest | `DESCRIPTIVE` | `SPARSE_CASE_DIAGNOSTICS_ONLY` | Phase-6E sign-off; SSOT | 4 positive cases context | Case diagnostics | Heterogeneous mechanisms and sparse evidence | No | No |
| Fertilizer | `ACTIVE_BASELINE` | `DESCRIPTIVE_ONLY` | Phase-6E sign-off; SSOT/registry | 1 positive case context | Baseline calculation, not inferential validation | Sparse comparator and no manure credit | No | No |
| Duck purchase | `ACTIVE` | Strict observed-positive comparator | F-01 corrected purchase evidence | 27 strict; 2 derived context | Provenance/accounting validation | Derived values excluded from strict observed N | No | No |
| Paddy revenue | `CONDITIONAL` | `EVALUATED` diagnostics | Phase-6D-R corrected revenue JSON/report | actual 36 / predicted 22 | HPP operational and price-neutral value diagnostics | Not realized-revenue or profit accuracy | No | No |
| Full profit | `UNAVAILABLE` | `NOT_EVALUABLE` | Phase-6E sign-off; incomplete ledger | No metric N | Fail-closed availability | Feed and cage total unavailable | No | No |
| Stress set | Separate execution path | Not merged into headline | Original Phase-6D stress results; Phase 6E | N=8; executed 5; unavailable 3 | Finite-output robustness check | Not a clean-cohort metric | No | No |
| Expert final | Not performed | Not performed | Phase-6E governance statement | N/A | Pending evidence stream | Final judgement absent | N/A | **No** |

## 7. Authoritative yield result

The corrected Phase-6D-R result is the current empirical conclusion. It uses
all 36 semantically admissible actual yield cells, which remain provenance
`DERIVED_ACTUAL` because each is a deterministic kg/are derivation from direct
harvested-gabah quantity divided by direct program rice area. Eligibility was
decided from source semantics before residuals were calculated.

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
| `LITERATURE_EVIDENCE_ENVELOPE_COVERAGE` | `90.9090909090909%` |
| Mean envelope width | `47.60574545454545 kg/are` |
| Median envelope width | `45.6432 kg/are` |

Interpretation: moderate retrospective point error among numeric predictions,
slight mean overprediction, high containment in a broad external evidence
envelope, and limited point precision. The appropriate framing is
**HIGH CONTAINMENT / BROAD ENVELOPE / LIMITED PRECISION**. The negative R² is
diagnostic only: it indicates that the frozen reference explains little
cycle-to-cycle variation relative to a constant-mean benchmark; it does not
mean negative accuracy.

## 8. Final subgroup metrics

| Subgroup | Actual N | Predicted N | Coverage | MAE kg/are | RMSE kg/are | WAPE | Envelope coverage | Publication status |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Strict supported domain | 17 | 17 | 100% | 9.855426004470589 | 14.436931455685956 | 23.478704172402782% | 88.23529411764706% | Quantitative; does not improve overall point performance |
| `INPARI_GROUP` | 5 | 3 | 60% | 8.309602693333334 | 10.467747785900904 | 17.60201414199902% | 100% | Quantitative with very small N=3 predictions |
| `SERTANI_GROUP` | 31 | 19 | 61.29032258064516% | 9.322029107157894 | 13.83058101193071 | 21.206653635894305% | 89.47368421052632% | Quantitative with `LOW_EVIDENCE_TWO_LOCATION_EXTERNAL_RANGE` |
| Jajar Legowo | 32 | 20 | 62.5% | 8.8949165408 | 13.481510495508598 | 19.96657912338301% | 90% | Quantitative subgroup |
| Tegel | 4 | 2 | 50% | — | — | — | — | `COUNT_ONLY_SMALL_N`; do not publish aggregate error metrics |

## 9. Cluster-bootstrap metrics

These are cluster-bootstrap empirical intervals around aggregate validation
metrics, not prediction intervals or parameter confidence intervals.

| Quantity | Exact empirical percentile interval |
|---|---:|
| MAE | `[5.338547626190476, 14.255541432705883]` kg/are |
| RMSE | `[7.48075664347243, 19.285367878437786]` kg/are |
| MBE | `[-2.391187468095236, 8.891407133200001]` kg/are |
| WAPE | `[11.282456480039396, 36.907197894190645]` |
| Literature evidence-envelope coverage | `[0.75, 1.0]` |

Bootstrap unit: `farmer_cluster_id`; resamples: `2000`; seed: `20260826`;
percentiles: `2.5 / 97.5%`.

## 10. Calendar result

| Quantity | Result |
|---|---:|
| Eligible N | `12` |
| Window hits | `4` |
| Calendar window coverage | `33.33333333333333%` |
| Mean distance to window | `5` days |
| Median distance to window | `5` days |
| Timing semantics | `HST_FROM_FIELD_TRANSPLANTING` |
| Timing status | `VALIDATION_ASSUMPTION` |

This is a calendar-window diagnostic, not model accuracy.

## 11. Purchase result

The F-01 correction establishes the final purchase provenance counts:

| Provenance | Count | Treatment |
|---|---:|---|
| `OBSERVED_VALUE` | 27 | Strict observed-positive comparator |
| `DERIVED_ACTUAL` | 2 | Context only; excluded from strict N |
| `EXPLICIT_ZERO` | 4 | Runtime default when replayed; not observed-positive comparator |
| `MISSING_UNKNOWN` | 3 | Runtime default when replayed; not observed-positive comparator |
| `LEGACY_IMPUTATION` | 0 | None |

Strict comparator N is `27`. Purchase DERIVED_ACTUAL is not silently promoted
to observed ground truth.

## 12. Revenue diagnostics

These diagnostics use the 22 numeric yield predictions over 36 eligible actual
rows. The current-HPP diagnostic uses Rp6,500/kg. The price-neutral diagnostic
uses historical paddy price only as comparator metadata. Neither is historical
realized-revenue accuracy or profit accuracy.

| Diagnostic | N actual | N predicted | MAE Rp/cycle | RMSE Rp/cycle | MedAE Rp/cycle | MBE Rp/cycle | WAPE |
|---|---:|---:|---:|---:|---:|---:|---:|
| `CURRENT_HPP_OPERATIONAL_VALUE_DIAGNOSTIC` | 36 | 22 | 311527.7986064933 | 420128.394071854 | 254786.2200136502 | 41782.65592655224 | 16.576559236396317% |
| `PRICE_NEUTRAL_HISTORICAL_PRICE_DIAGNOSTIC` | 36 | 22 | 297042.3196077955 | 400883.6711827306 | 241702.28101260017 | 30976.365834068216 | 15.987950881921265% |

## 13. Other component statuses

| Component | Final status |
|---|---|
| Survival | `NO_COMPATIBLE_AGGREGATE_GROUND_TRUTH` |
| Feed | `NOT_EVALUABLE` |
| Cage total | `UNAVAILABLE` |
| Infrastructure | `NO_METRIC` |
| Weed | `NO_MONETARY_AGGREGATE` |
| Pest | `SPARSE_CASE_DIAGNOSTICS_ONLY` |
| Fertilizer | `DESCRIPTIVE_ONLY` |
| Full profit | `UNAVAILABLE` |
| Expert final | `PENDING_NON_BLOCKING` |

Stress status is `N=8`, executed `5`, input unavailable `3`; all executed outputs
were finite, with no NaN or infinity, and stress rows were not merged into
headline metrics.

## 14. F-01/F-02/F-03 correction register

| Finding | Closure |
|---|---|
| F-01 | Purchase-price provenance corrected. Strict observed-positive comparator N=`27`; two `DERIVED_ACTUAL` purchase values remain context and are excluded from strict N. |
| F-02 | Stale calendar/report prose corrected in the evidence layer. Machine-readable and report semantics now align: N=`12`, hits=`4`, window coverage=`33.33333333333333%`, mean/median distance=`5` days. |
| F-03 | Yield `DERIVED_ACTUAL` admissibility corrected. All 36 values are deterministic kg/are derivations from direct harvested-gabah quantity / direct program rice area. The derived provenance label is retained; semantic admissibility is separate. Eligibility changed, not the frozen model or parameters. |

F-03 was a source-semantic validation correction, not a model-bug narrative.
The original Phase-6D run is preserved; no residual-based row selection,
recalibration, or new empirical comparator run occurred.

## 15. No-change and governance declarations

- No model change.
- No parameter change.
- No new freeze; specifically, no `R2-FREEZE-2026-08-26.6`.
- No recalibration.
- No new real comparator run.
- No source-literature search.
- No DOCX generation.
- No private workbook, raw workbook rows, farmer names, or private mapping was
  added to the tracked release package.

If final expert judgement occurs later, it is an additive evidence extension.
It may confirm, reject, or qualify interpretations and may produce
expert-specific artifacts. It must not retroactively alter the current
empirical metrics, original comparator rows, or scientific target identity. If
expert feedback changes the scientific model, a new parameter registry, new
freeze, and new validation generation are required.

## 16. Publication-artifact source map

| Artifact | Role | Source authority |
|---|---|---|
| `docs/export/R2_FINAL_MATHEMATICAL_MODEL_SOURCE.md` | Mathematical-model DOCX source; not final DOCX | `docs/01_R2_MODEL_SSOT.md`, `docs/04_R2_PARAMETER_EXECUTION_REGISTRY.md`, `app/engines/r2/` |
| `docs/export/R2_FINAL_VALIDATION_METHODOLOGY_SOURCE.md` | Validation-methodology DOCX source; not final DOCX | `docs/06_R2_TEST_VALIDATION_PROTOCOL.md`, Phase-6D-R and Phase-6E evidence |
| `docs/export/R2_IJOST_MANUSCRIPT_FACT_PACKAGE.md` | Publication-safe factual package; not manuscript | Frozen identity, SSOT/registry, corrected evidence, Phase-6E limits |
| `docs/export/R2_EXPORT_SOURCE_AUDIT.md` | Cross-source audit | The three export sources plus authoritative repository evidence |

Final DOCX generation is intentionally deferred to a separate task.

## 17. QA and closure gate

The Phase-6E committed QA evidence records 425 collected and passed tests,
successful `python -m compileall app validation`, independent metric
reproduction, original-run byte preservation, and privacy pass. This
documentation closure requires those gates to remain true after the
documentation-only changes; the final command results are reported with the
release handoff.

The release is ready only with the limitations recorded here:

`PHASE_6F_FINAL_DOCUMENTATION_RELEASE_CLOSURE_READY`
