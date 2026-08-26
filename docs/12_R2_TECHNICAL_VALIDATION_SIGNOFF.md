# R2 Technical Validation Sign-Off — Phase 5C Stage B (Official Frozen Execution)

Status: **TECHNICAL EMPIRICAL CLOSURE — EVIDENCE/SIGN-OFF DOCUMENT**

This document records the official frozen empirical execution of the R2
rice-duck backend. It is an evidence artifact only: it does not alter any
scientific model definition, parameter, lookup, calendar window, survival or
economic constant, and it does not constitute final expert validation.

---

## 1. Scientific target identity

| Item | Value |
| --- | --- |
| Repository | farisakbar28/rice-duck-be |
| Branch | master |
| Scientific target commit SHA | `f14f5d97b09d8afb29e4d0d840e41fe2b00886f5` |
| MODEL_VERSION | R2 |
| PARAMETER_REGISTRY_VERSION | R2-2026-08-26.2 |
| FREEZE_ID | R2-FREEZE-2026-08-26.2 |
| MODEL_FROZEN | true |
| FREEZE_EFFECTIVE_FROM | 2026-08-26 |

## 2. Execution record

| Item | Value |
| --- | --- |
| Official run ID | `20260826T102325Z_f14f5d9` |
| Official execution timestamp (UTC) | 2026-08-26T10:22:51+00:00 |
| Python version | 3.14.2 |
| Working tree at gate evaluation | CLEAN (`git status --porcelain` empty) |
| Evidence source root | `penelitian/R2_validation_sources` (uncommitted, gitignored) |

The official run was started from the clean committed scientific HEAD above.
Generated artifacts made the tree dirty only AFTER the official gate had been
evaluated, per the evidence-commit model (scientific freeze commit → clean
official execution → generated evidence artifacts → separate evidence-only
commit). The later evidence commit is NOT the scientific target SHA.

## 3. CI result

| Item | Value |
| --- | --- |
| Workflow | CI (.github/workflows/ci.yml) |
| Run ID | 32956669853 |
| Head SHA | `f14f5d97b09d8afb29e4d0d840e41fe2b00886f5` |
| Status / conclusion | completed / **success** |

Local verification is independent of CI and was executed locally in this run.

## 4. Local active-test result

| Metric | Value |
| --- | --- |
| Collected | 380 |
| Passed | 380 |
| Failed / Errors | 0 / 0 |
| Skipped / xfailed / xpassed | 0 / 0 / 0 |
| `tests/legacy_invalid` collected | false (excluded via pytest.ini `norecursedirs`) |
| `python -m compileall app validation` | OK |

## 5. Source fingerprints (SHA-256)

| Role | File | SHA-256 | Fingerprint |
| --- | --- | --- | --- |
| raw_recap | Recap Data CRS Bebek.xlsx | `6b73b34a418d36cddbdf61679944eeaaf7fda312f1ee88c64476670bc0da82d1` | VALID |
| clean_cohort | DSS_Padi_Bebek_Rekap_Bersih_v10.xlsx | `98fff237d24b6191d0d21a9e04048d54d4efd83082a61dae0da37c584405c2bd` | VALID |
| legacy_simulation (AUDIT_ONLY) | Dataset Bersih Rekap Include Hasil Simulasi Baru.xlsx | `f5e88945196c2300d57c36b16fc5c175c24ecfbd903468cc1c553771e1e94a46` | VALID |

Internal evidence package also inventoried for provenance:
`data_collection_padi_bebek_FINAL.xlsx`, `Dokumentasi Expert DSS Padi-Bebek.docx`,
`Model Matematika Data Collection DSS Padi Bebek.docx`,
`Kumpulan_Variabel_Rumus_Data_Artikel_Referensi_Scopus_FINAL.docx`,
`literature/` (Alfiansyah 2025; Nallasamy 2025 + supplementary; Vipriyanti 2021).
Only the raw and clean workbooks are empirical official-gate sources.

## 6. Cohort reconstruction (recomputed from source, not supplied)

| Cohort | N | Source rows |
| --- | --- | --- |
| raw eligible cohort | 44 | 4–64 per `cohort_reconstruction.json` (`raw` list) |
| clean KEEP | 36 | see `clean` list |
| excluded/stress | 8 | 16, 22, 29, 32, 48, 57, 59, 64 |
| strict supported-domain | 17 | 19, 21, 25, 28, 34, 36, 38, 39, 44, 46, 47, 51, 53, 55, 60, 61, 62 |
| calendar eligible (both dates OBSERVED) | 12 | 28, 34, 36, 37, 38, 39, 41, 43, 44, 51, 53, 55 |

Regression expectations 44/36/8/17/12 reproduced exactly from the fingerprint-verified
source workbooks. Strict-domain rule: planting system provenance = OBSERVED,
Jarwo 2 ≤ d ≤ 4, Tegel 2 ≤ d ≤ 3 (defaulted-system rows excluded).

### Raw-to-clean traceability

Every clean/stress row carries: raw source row ID, clean row ID, KEEP/EXCLUDED
role, anonymous farmer cluster (`F001..F026`), and — for excluded rows — the
workbook exclusion reason (see §14 stress table). No real farmer names appear in
any committed artifact (§16 privacy audit).

## 7. Timing semantics (VALIDATION_ASSUMPTION)

`planting_date` represents the FIELD TRANSPLANTING DATE for HST calculation.
Label: `HST_FROM_FIELD_TRANSPLANTING` with status **VALIDATION_ASSUMPTION**
(`timing_semantics_status` in `calendar_validation.json`). It is not asserted as
observed for every historical record. Calendar windows were not modified based
on comparator outcomes.

## 8. V1 computational verification (docs/06 §19 matrix)

**all_pass = true**, item count = **22/22** (V1-01 … V1-22).
Computational implementation verification only — not empirical predictive accuracy.
Evidence: `v1_computational.json`.

## 9. Synthetic B01–B18 (canonical HTTP/runtime path)

**18/18 pass** through `POST /api/v1/dss/simulate` (FastAPI TestClient on the
frozen production app). Fresh raw request/response JSON stored verbatim per case
in `synthetic_cases.json` (no reuse of earlier `.1` runs).

## 10. Age-invariance evidence

Supported-age scenarios 21 days vs 30 days, both **VALIDATION_ASSUMPTION**:
numeric payloads invariant (`numeric_payloads_invariant=true`,
`differing_paths=[]`, excluded paths limited to wall-clock metadata and the age
echo itself). Age was not selected based on historical fit. Evidence:
`synthetic_cases.json → age_invariance`.

## 11. Calendar empirical comparator (quantitative)

Units: **days**. Eligibility: observed planting AND observed harvest date.
No calendar parameter altered post-hoc.

| Metric | Value |
| --- | --- |
| N | 12 |
| Window hits | 4 (rows 38, 43, 51, 53) |
| Overall window coverage | 0.3333 (4/12) |
| Mean distance-to-window | 5.0 days |
| Median distance-to-window | 5.0 days |

Per-row distances (days): 28→7, 34→5, 36→16, 37→1, 38→0, 39→5, 41→9, 43→0,
44→12, 51→0, 53→0, 55→5. Full row-level evidence (predicted min/max dates,
observed harvest dates) in `calendar_validation.json`.

### Independent metric reproduction

Calendar metrics were independently recomputed once from row-level evidence by a
standalone script reading the clean workbook directly (plain arithmetic against
the seed harvest windows, no harness computation path): N=12, hits=4,
coverage=0.3333333333333333, mean=5.0, median=5.0, all row values identical.
Result: **MATCH — no CALENDAR_METRIC_REPRODUCTION_FAILURE**.

## 12. Purchase-cost comparator

**Post-review correction (Stage-C finding F-01, P2): CLOSED.** The original run
artifact `purchase_validation.json` labeled source rows 14 and 18 as
OBSERVED_VALUE even though their raw unit-price cells are formula-derived
(`=200000/9` and `=200000/AM18`); under the canonical provenance taxonomy they are
DERIVED_ACTUAL. The publication-facing corrected evidence is
`validation/results/20260826T102325Z_f14f5d9/purchase_validation_stage_c_corrected.json`;
the original artifact is preserved unchanged for audit.

Source-recomputed provenance of all 36 clean records:
OBSERVED_VALUE = 27, DERIVED_ACTUAL = 2 (rows 14, 18), EXPLICIT_ZERO = 4
(rows 37, 38, 43, 44), MISSING_UNKNOWN = 3 (rows 20, 24, 41); total = 36.

| Item | Value |
| --- | --- |
| Strict eligible N (price positive AND provenance OBSERVED_VALUE only) | **27** |
| DERIVED_ACTUAL positive contextual rows (excluded from strict statistics) | 2 — source rows 14 (`=200000/9`, Rp22,222.22222 × 9 ducks) and 18 (`=200000/AM18`, Rp6,666.666667 × 30 ducks) |
| Defaulted rows excluded (runtime default Rp26,500) | 7 — blank-price rows 20, 24, 41 plus zero-price rows 37, 38, 43, 44 (zeros/blanks are not R2 positive-price inputs; provenance LOCAL_DEFAULT) |
| Observed price range observed in data (strict cohort) | Rp5,000 – Rp32,000 per duck |
| Mean / median strictly observed price | **Rp18,818.11 / Rp25,000 per duck** |
| Identity check | `C_duck_buy = J × p_duck_buy` re-verified per row for all 27 OBSERVED_VALUE + 2 DERIVED_ACTUAL records in `purchase_validation_stage_c_corrected.json`; runtime identity covered by V1 items + synthetic B12 |

Rows using the runtime default are explicitly NOT treated as observed-price
accuracy observations; the default is a model input-resolution rule, not observed
evidence. The former N=29 / mean Rp18,516.48 figures from the preserved original
artifact must not be cited as strict directly observed comparator results.

## 13. Yield final status

| Item | Value |
| --- | --- |
| status | **NOT_EVALUABLE** |
| reason | **R2_YIELD_EVIDENCE_INSUFFICIENT** (approved canonical equivalent of the frozen methodology) |
| prediction_coverage | 0 (0/36) |
| metrics | null |

Not computed: MAE, RMSE, MedAE, MBE, WAPE, MAPE, R². Unavailable predictions
were not replaced by zero; this is NOT "zero accuracy". No numeric lookup was
derived after seeing comparator data. Production `Y_base(V_group)` and `F_RD`
remain intentionally empty (evidence boundary CLOSED).

## 14. Component statuses and stress set

| Component | Official status | Coverage metadata |
| --- | --- | --- |
| Survival | NO_COMPATIBLE_AGGREGATE_GROUND_TRUTH; `N_sold` never used as survival ground truth; no aggregate MAE/RMSE | — |
| Terminal duck value | livestock asset value ≠ realized sale revenue; no sale-revenue accuracy vs `V_duck_end` | — |
| Feed | NOT_EVALUABLE (runtime lookup unavailable); positive history is coverage metadata only | 23/36 positive |
| Infrastructure | NO_METRIC (semantic compatibility NOT established; ambiguous historical constructs) | net 17/36, cage 9/36 positive |
| Weeding | NO_MONETARY_AGGREGATE (descriptive only) | 0/36 positive cash |
| Pesticide | SPARSE_CASE_DIAGNOSTICS_ONLY (no headline aggregate) | 4/36 positive |
| Fertilizer | DESCRIPTIVE_ONLY (parameters untouched) | 1/36 positive |
| Profit/Margin | Profit_full_est = UNAVAILABLE (ledger incomplete); Margin_core is NOT labeled profit; legacy farmer profit comparison FORBIDDEN | — |

### Zero-vs-missing provenance audit

Provenance vocabulary preserved end-to-end: EXPLICIT_ZERO / MISSING_UNKNOWN /
OBSERVED_VALUE / DERIVED_ACTUAL / LEGACY_IMPUTATION. Independent re-audit of
duck purchase price, feed, weeding, fertilizer, pesticide, net, cage:

* Purchase price zeros in clean rows trace to raw-recorded explicit zeros
  (rows 37, 38, 43, 44) or true blanks (rows 20, 24, 41) — no promotion.
* Raw-recap fertilizer/pesticide/weeding/feed zeros produced by legacy
  spreadsheet formulas (e.g. `=EC28+EG28+EK28+EN28`) are classified
  DERIVED_ACTUAL by the frozen parser — never promoted to OBSERVED_VALUE /
  EXPLICIT_ZERO.
* Positive-coverage counts independently recomputed and matched the artifacts
  exactly: feed 23, weeding 0, pesticide 4, fertilizer 1, net 17, cage 9.

### Stress-8 official run (excluded cohort, executed separately)

| Row | Cluster | Exclusion reason (from workbook) | Result |
| --- | --- | --- | --- |
| 16 | F011 | explicit field note: borrowed ducks | EXECUTED, HTTP 200, finite, density EXTRAPOLATION |
| 22 | F005 | cycle without ducks (J≤0 / duck data empty) | NOT_EXECUTABLE_INPUT_UNAVAILABLE (`duck_count`) |
| 29 | F013 | explicit field note: pest/outbreak | EXECUTED, HTTP 200, finite, SUPPORTED |
| 32 | F014 | explicit field note: pest/outbreak | NOT_EXECUTABLE_INPUT_UNAVAILABLE (`rice_variety`) |
| 48 | F017 | extreme micro-area (A < 2.5 are) | EXECUTED, HTTP 200, finite, SUPPORTED |
| 57 | F021 | extreme micro-area; experimental plot | EXECUTED, HTTP 200, finite, SUPPORTED |
| 59 | F022 | extreme micro-area (A < 2.5 are) | EXECUTED, HTTP 200, finite, EXTRAPOLATION |
| 64 | F026 | ceremony ducks / non-reconcilable density basis | NOT_EXECUTABLE_INPUT_UNAVAILABLE (`planting_system`) |

N=8, executed_n=5, input_unavailable_n=3, HTTP rejected=0,
all_executed_rows_finite=true, warnings propagated, null propagation intact.
Stress rows are NOT merged into clean headline statistics.

### Legacy simulation audit

Legacy workbook role = AUDIT_ONLY; structure-only parse
(`values_exposed_to_r2=false`). No legacy yield prediction, NetCash, profit,
feed, or other formula imported into R2 comparator prediction. Evidence:
`legacy_simulation_audit.json`.

## 15. Privacy audit

All generated artifacts scanned: real farmer names (all 26 entries of the
private mapping), email patterns, phone patterns, address keywords.
Result: **ZERO PII leakage**. Only anonymous IDs F001–F026 appear. One regex
hit was a false positive (digits inside a SHA-256 hex string). The private
name mapping resides in gitignored `validation/local/farmer_id_map.json`.

## 16. Comparator-leakage audit

Confirmed via git: after the official run, the ONLY changes are the mirrored
`validation/freeze_manifest.json` and the new untracked results directory. No
change to `app/data/seed.py`, `app/engines/r2/**`, registry constants, lookup
records, support boundaries, calendar windows, or economic parameters. This run
is evaluation-only; no calibration occurred (statically guarded by
`tests/test_validation_isolation.py`). No scientific file was modified after
official execution began.

## 17. No-recalibration declaration

No fitting, optimization, calibration, or comparator-derived parameter change
was performed anywhere in this stage. Discrepancies are reported, never tuned
away.

## 18. Expert status

**EXPERT_FINAL_REVIEW = PENDING.** Existing expert-transfer evidence remains
labeled DIRECT (3) / PARTIAL (6) / NONE (3) over 12 items
(`expert_transfer.json`); these are transfer-mapping labels, not final expert
validation. Technical empirical closure does not depend on the pending final
expert judgement.

## 19. Reporting correction record (Stage-C findings F-01/F-02 — CLOSED)

Stage C (post-review) approved technical validation with two publication-facing
evidence corrections, both now closed through an explicit POST-REVIEW CORRECTION
LAYER. The original official report `validation_report.md` of run
`20260826T102325Z_f14f5d9` is **preserved unchanged for audit reproducibility**
(it was NOT regenerated during the official run and has not been edited since);
it contains two stale pre-empirical placeholder prose lines in sections 6 and 19
inherited from the frozen Stage-A renderer ("Prior-audit expectation N=12 …",
"…(blocked)"). The machine-readable Stage-B results were never affected:
`calendar_validation.json` always reported status=EVALUATED with full metrics.

A corrected publication-facing report now exists at
`validation/results/20260826T102325Z_f14f5d9/validation_report_stage_c_corrected.md`,
restating the authoritative calendar result (EVALUATED; N=12; hits=4;
coverage 33.33%; mean/median distance-to-window 5.0 days) and the source-recomputed
purchase provenance (strict observed N=27; DERIVED_ACTUAL rows 14/18 disclosed
separately). Correction traceability: `stage_c_corrections.json`.
Scientific model unchanged; no new freeze; no new official empirical execution.

- **F-01 status = CLOSED** (corrected artifact:
  `purchase_validation_stage_c_corrected.json`)
- **F-02 status = CLOSED** (corrected report:
  `validation_report_stage_c_corrected.md`)

## 20. Conclusion

All Phase-5C Stage-B official gates passed: correct HEAD, OFFICIAL_FROZEN_EXECUTION
mode, 380/380 local tests, CI success on target, valid source fingerprints,
exact 44/36/8/17/12 source reconstruction, V1 22/22, B01–B18 18/18, age
invariance, independently reproduced calendar metrics, purchase identity,
correctly closed yield/feed/survival boundaries, complete stress set, privacy
and leakage audits clean. No universal model accuracy percentage exists or is
claimed anywhere in this package.

Post-review (Stage C): APPROVE TECHNICAL VALIDATION COMPLETE with evidence
corrections F-01/F-02 applied via the POST-REVIEW CORRECTION LAYER above; the
scientific target `f14f5d97b09d8afb29e4d0d840e41fe2b00886f5`, freeze identity
R2-FREEZE-2026-08-26.2, and the original official run artifacts remain unchanged.

**PHASE_5C_OFFICIAL_EXECUTION_COMPLETE_READY_FOR_EVIDENCE_COMMIT**

**POST-REVIEW EVIDENCE CORRECTIONS COMPLETE — PUBLICATION EVIDENCE:
READY_AFTER_STAGE_C_CORRECTIONS**
