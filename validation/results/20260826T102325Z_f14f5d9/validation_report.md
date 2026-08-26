# R2 Phase-5 Validation Report (OFFICIAL_FROZEN_EXECUTION)

> Execution: 2026-08-26T10:22:51+00:00 | Python 3.14.2 | backend commit `f14f5d97b09d8afb29e4d0d840e41fe2b00886f5` | registry `R2-2026-08-26.2` | freeze_id `R2-FREEZE-2026-08-26.2`

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

## 6. Calendar comparator
- status=EVALUATED; eligible rows require OBSERVED planting AND harvest dates
- Prior-audit expectation N=12 must be recomputed from source before any metric.

## 7. Yield status
- status=NOT_EVALUABLE; reason=R2_YIELD_EVIDENCE_INSUFFICIENT; actual_coverage=36/36; prediction_coverage=0/36; quantitative_metrics=None

## 8. Revenue status
- operational paddy revenue = NOT_EVALUABLE (yield unavailable); price-neutral diagnostic = NOT_EVALUABLE. No zero-residual substitution.

## 9. Survival status
- ground_truth_status=NO_COMPATIBLE_AGGREGATE; no MAE/RMSE; sold ducks are never survival actuals. V1 gate + expert transfer only.

## 10. Purchase-cost status
- deterministic identity verified by V1 tests; observed historical prices are plausibility/comparator context; default-price rows excluded from observed comparators.

## 11. Feed status
- runtime UNAVAILABLE -> no accuracy metric; positive historical feed counts reported as coverage metadata only.

## 12. Infrastructure status
- semantic_compatibility_established=False -> metric_allowed=False; reason: historical 'infra' proxies are ambiguous; square-equivalent net amortization and per-cycle cage totals cannot be assumed to match historical constructs

## 13. Weed/pest/fertilizer status
- weeding: no monetary accuracy metric; pesticide: sparse case diagnostics; fertilizer: descriptive only. Small N never promoted to aggregate validation.

## 14. Profit/margin status
- no comparison of historical farmer profit with Margin_core/Profit_full_est; cost_completeness=INCOMPLETE -> Profit_full_est null by design.

## 15. Stress-test status
- EVALUATED_SEPARATELY

## 16. Expert-transfer summary
- labels: {'DIRECT': 3, 'PARTIAL': 6, 'NONE': 3} over 12 items (see expert_transfer.json); global notes: Expert ~80% working confidence is not a statistical pass/fail threshold. No aggregate 'expert accuracy' score is defined anywhere in this harness.

## 17. Limitations
- yield/feed/cage-total/full-profit remain unavailable by design; cohort counts and comparator eligibility are source-version gated.

## 18. No-recalibration declaration
- no fitting/optimization/calibration workflow exists in this package (statically guarded by tests/test_validation_isolation.py); no seed/engine/SSOT coefficient was modified during validation; discrepancies are reported, never tuned away.

## 19. Component-specific conclusions
- Computational implementation: VERIFIED (V1 100%)
- Calendar: quantitatively evaluable only after source verification (blocked).
- Yield: NOT EVALUABLE — lookup unavailable (hard gate).
- Survival: no aggregate ground truth; deterministic + expert evidence only.
- Feed: not evaluable. Infrastructure: limited/conditional. Full profit: not evaluable.
- No universal accuracy score exists in this report.
