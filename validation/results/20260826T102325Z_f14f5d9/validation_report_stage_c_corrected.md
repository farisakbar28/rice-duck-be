# R2 Phase-5 Validation Report — POST-STAGE-C CORRECTED PUBLICATION-FACING REPORT

> Correction layer: `POST_STAGE_C_EVIDENCE_CORRECTION` (findings F-01 P2, F-02 P3) |
> Corrected: 2026-08-26 | Evidence commit `4ffa65b0ecaa1e880194802bd3786cb7f27a90b7`

**Status of this document.**

- This corrected report is based on the official frozen run
  `20260826T102325Z_f14f5d9` (OFFICIAL_FROZEN_EXECUTION, executed 2026-08-26T10:22:51+00:00).
- The scientific target remains `f14f5d97b09d8afb29e4d0d840e41fe2b00886f5`
  (MODEL_VERSION R2, PARAMETER_REGISTRY_VERSION R2-2026-08-26.2,
  FREEZE_ID R2-FREEZE-2026-08-26.2 — unchanged; no `.3` bump).
- **This is not a new model run.** No model, parameter, lookup, calendar window,
  survival logic, economics, or API change is introduced; nothing was recalibrated.
- The original official artifacts of the run — including `validation_report.md`,
  `purchase_validation.json`, and `freeze_manifest.json` — are retained unchanged
  for audit reproducibility.
- Corrections address Stage-C findings F-01 (purchase provenance) and F-02 (stale
  calendar prose) only. All scientifically valid Stage-B results below are carried
  over from the machine-readable evidence of that same run.

## 1. Freeze identity

- model_version=R2 (unchanged)
- parameter_registry_version=R2-2026-08-26.2 (unchanged)
- history schema=4; app_version=0.1.0
- MODEL_FROZEN=True, FREEZE_ID=R2-FREEZE-2026-08-26.2, FREEZE_EFFECTIVE_FROM=2026-08-26
- frozen means *immutable validation target*; it does NOT mean empirically validated, accurate, or complete.

## 2. Source fingerprints

- raw_recap: Recap Data CRS Bebek.xlsx — PRESENT, sha256=6b73b34a418d36cddbdf61679944eeaaf7fda312f1ee88c64476670bc0da82d1
- clean_cohort: DSS_Padi_Bebek_Rekap_Bersih_v10.xlsx — PRESENT, sha256=98fff237d24b6191d0d21a9e04048d54d4efd83082a61dae0da37c584405c2bd
- legacy_simulation: Dataset Bersih Rekap Include Hasil Simulasi Baru.xlsx — PRESENT, sha256=f5e88945196c2300d57c36b16fc5c175c24ecfbd903468cc1c553771e1e94a46

Fingerprints re-verified against the workbooks at correction time: MATCH.

## 3. Dataset/cohort status

- empirical_source_status = OK
- all_clean: expected(prior audit)=36, verified=True, status=VERIFIED
- excluded_stress: expected(prior audit)=8, verified=True, status=VERIFIED
- strict_supported_domain: expected(prior audit)=17, verified=True, status=VERIFIED
- calendar_eligible_both_observed_dates: expected(prior audit)=12, verified=True, status=VERIFIED

## 4. V1 computational verification

- all_pass = True; items = 22 (docs/06 §19 matrix mapped to active tests)

## 5. Synthetic runtime evidence (B01–B18)

- passed 18/18 via canonical HTTP path; raw responses archived in synthetic_cases.json
- supported-age invariance (21 vs 30): pass=True differing_paths=[]
- Synthetic cases are contract evidence, NOT field observations.

## 6. Calendar comparator (CORRECTED — closes F-02)

The original `validation_report.md` contained two stale pre-empirical placeholder
prose lines inherited from the frozen Stage-A renderer. They conflicted with the
machine-readable evidence of the same run; the machine artifacts were always
authoritative and were never affected. The authoritative corrected result:

- status = EVALUATED
- eligible N = 12 (rows require OBSERVED planting AND harvest dates)
- window hits = 4 (rows 38, 43, 51, 53)
- window coverage = 33.33% (4/12)
- mean distance-to-window = 5.0 days
- median distance-to-window = 5.0 days
- timing semantics = VALIDATION_ASSUMPTION (`HST_FROM_FIELD_TRANSPLANTING`)

Per-row distances (days): 28→7, 34→5, 36→16, 37→1, 38→0, 39→5, 41→9, 43→0,
44→12, 51→0, 53→0, 55→5. Full row-level evidence (predicted min/max dates,
observed harvest dates) in `calendar_validation.json`.

Methodological qualification: coverage is a **window-hit rate under the stated
timing assumption**, not a model accuracy metric. The complementary 8/12 rows are
misses of a ±10-day window under an assumed transplanting-date semantics; they are
not a "67% failure rate" of the model. No universal accuracy percentage is defined
or claimed anywhere in this report.

## 7. Yield status

- status=NOT_EVALUABLE; reason=R2_YIELD_EVIDENCE_INSUFFICIENT; actual_coverage=36/36; prediction_coverage=0/36; quantitative_metrics=None

## 8. Revenue status

- operational paddy revenue = NOT_EVALUABLE (yield unavailable); price-neutral diagnostic = NOT_EVALUABLE. No zero-residual substitution.

## 9. Survival status

- ground_truth_status=NO_COMPATIBLE_AGGREGATE; no MAE/RMSE; sold ducks are never survival actuals. V1 gate + expert transfer only.

## 10. Purchase-cost status (CORRECTED — closes F-01)

Source-recomputed provenance of all 36 clean duck-purchase-price records
(`purchase_validation_stage_c_corrected.json`; independently re-derived from both
fingerprint-verified workbooks with formulas preserved):

- 27 rows contained positive directly observed duck unit prices (provenance OBSERVED_VALUE);
- 2 additional positive unit-price values were derived from recorded totals and
  duck counts via spreadsheet formulas (source row 14 `=200000/9`, source row 18
  `=200000/AM18`) and were treated separately as DERIVED_ACTUAL;
- 7 rows contained explicit zero or missing price values (4 EXPLICIT_ZERO:
  rows 37, 38, 43, 44; 3 MISSING_UNKNOWN: rows 20, 24, 41) and therefore used the
  R2 runtime local default Rp26,500 when replayed;
- only the 27 OBSERVED_VALUE rows belong to the strict observed-price comparator.

Strict directly observed unit-price statistics:

| Metric | Value |
| --- | --- |
| Strict observed N | 27 |
| Minimum observed price | Rp5,000 per duck |
| Maximum observed price | Rp32,000 per duck |
| Mean observed price | Rp18,818.11 per duck |
| Median observed price | Rp25,000 per duck |

- The former N=29 ("effective_n" in the preserved original artifact) must NOT be
  cited as the strict observed N: it included the two formula-derived values.
- The DERIVED_ACTUAL rows remain valid derived contextual evidence (accounting
  identity/diagnostics) but are excluded from strict observed-price statistics.
- The runtime default is a model input-resolution rule, not observed evidence;
  default-price rows are excluded from observed comparators.
- Deterministic identity `C_duck_buy = J × p_duck_buy` verified per row across all
  29 positive records; historical prices are plausibility/comparator context only.

## 11. Feed status

- runtime UNAVAILABLE -> no accuracy metric; positive historical feed counts reported as coverage metadata only.

## 12. Infrastructure status

- semantic_compatibility_established=False -> metric_allowed=False; reason: historical 'infra' proxies are ambiguous; square-equivalent net amortization and per-cycle cage totals cannot be assumed to match historical constructs

## 13. Weed/pest/fertilizer status

- weeding: no monetary accuracy metric; pesticide: sparse case diagnostics; fertilizer: descriptive only. Small N never promoted to aggregate validation.

## 14. Profit/margin status

- no comparison of historical farmer profit with Margin_core/Profit_full_est; cost_completeness=INCOMPLETE -> Profit_full_est null by design.

## 15. Stress-test status

- EVALUATED_SEPARATELY (N=8, executed_n=5, input_unavailable_n=3; stress rows never merged into clean headline statistics).

## 16. Expert-transfer summary

- labels: {'DIRECT': 3, 'PARTIAL': 6, 'NONE': 3} over 12 items (see expert_transfer.json); global notes: Expert ~80% working confidence is not a statistical pass/fail threshold. No aggregate 'expert accuracy' score is defined anywhere in this harness. Expert final validation remains PENDING.

## 17. Limitations

- yield/feed/cage-total/full-profit remain unavailable by design; cohort counts and comparator eligibility are source-version gated.

## 18. No-recalibration declaration

- no fitting/optimization/calibration workflow exists in this package (statically guarded by tests/test_validation_isolation.py); no seed/engine/SSOT coefficient was modified during validation or during this post-review correction; discrepancies are reported, never tuned away.

## 19. Component-specific conclusions (corrected)

- Computational implementation: VERIFIED (V1 100%)
- Calendar: EVALUATED — N=12, hits=4, coverage 33.33% (window-hit rate under the
  VALIDATION_ASSUMPTION timing semantics), mean/median distance-to-window 5.0 days.
- Yield: NOT EVALUABLE — lookup unavailable (hard gate).
- Survival: no aggregate ground truth; deterministic + expert evidence only.
- Feed: not evaluable. Infrastructure: limited/conditional. Full profit: not evaluable.
- No universal accuracy score exists in this report.

## 20. Correction traceability

| Item | Value |
| --- | --- |
| Original official report (preserved) | `validation_report.md` |
| Corrected purchase artifact | `purchase_validation_stage_c_corrected.json` |
| Correction manifest | `stage_c_corrections.json` |
| Finding F-01 | CLOSED — provenance recomputed from source; strict comparator N=27; derived rows separated |
| Finding F-02 | CLOSED — calendar section restated from machine-readable evidence; stale prose superseded |

Publication-facing evidence status after corrections:
`READY_AFTER_STAGE_C_CORRECTIONS`. Expert final validation: PENDING.
