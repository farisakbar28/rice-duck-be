# R2 Test and Validation Protocol

> **Rule:** implementation tests and empirical model validation are different activities.  
> **Historical recap is comparator only. It must never fit/tune R2.**

## 1. Validation Layers

| Layer | Purpose | Recap use |
|---|---|---|
| V1 Computational verification | prove code implements R2 formulas/contracts exactly | no |
| V2 Retrospective comparator | compare compatible R2 outputs with actual observations | yes, comparator only |
| V3 Domain/robustness | test normal, boundary, extrapolation and excluded cycles | yes, context/stress only |
| V4 Expert evidence binding | connect expert judgement to exact parameter/formula | context, not fitting |

## 2. Model Freeze Before Empirical Metrics

Before calculating MAE/RMSE/WAPE:

```text
model_version
parameter_registry_version
Git commit SHA
active formula list
pending/unavailable formula list
lookup versions
regulatory price versions
```

must be frozen.

After error is observed, no coefficient may be changed and then re-evaluated on the same comparator while calling that result blind validation.

## 3. Comparator Datasets

- Raw source: 44 cycles.
- Clean comparator: 36 cycles.
- Excluded/stress: 8 cycles.

Roles:

- raw recap: provenance/zero-vs-missing verification;
- clean 36: primary comparator cohort;
- old simulation workbook: legacy audit only; never R2 prediction source;
- 8 excluded: abnormal/out-of-distribution stress set.

## 4. Provenance Flags for Validation Inputs

Every fixture value must carry one of:

- `OBSERVED`
- `LOCAL_DEFAULT`
- `VALIDATION_ASSUMPTION`
- `UNAVAILABLE`

Every comparator value must carry:

- `OBSERVED_VALUE`
- `EXPLICIT_ZERO`
- `MISSING_UNKNOWN`
- `DERIVED_ACTUAL`
- `LEGACY_IMPUTATION`

Rules:

```text
NULL != 0
UNRECORDED != 0
LEGACY_IMPUTATION != GROUND_TRUTH
```

## 5. Primary Cohorts

### 5.1 All-clean cohort

`N=36` for outputs with actual coverage across all 36, especially yield once R2 yield is executable.

### 5.2 Strict supported-domain cohort

Previously audited strict cohort:

- observed planting system;
- Jarwo density within 2–4 or Tegel within 2–3;
- `N=17`.

Report quantitative yield metrics at minimum for:

```text
all clean: N=36
strict supported-domain: N=17
```

Do not delete extreme residuals from the 36 after seeing results.

## 6. Yield Validation Gate

**Current R2 state:** yield runtime is `PENDING_LOOKUP/UNAVAILABLE` until approved local-cultivar-group baseline and exact-node F_RD records are configured. Grouping and schema readiness are not numeric evidence.

Therefore:

```text
if YieldAvailabilityFlag != AVAILABLE:
    DO NOT calculate/publish R2 yield MAE/RMSE.
```

Do not use legacy fixed `47.8767507` just to make validation runnable.

When yield becomes available and model is frozen, use:

```text
e_i = pred_i - actual_i
MAE   = mean(abs(e_i))
RMSE  = sqrt(mean(e_i^2))
MedAE = median(abs(e_i))
MBE   = mean(e_i)
WAPE  = sum(abs(e_i)) / sum(actual_i) * 100%
```

Headline metric: **MAE kg/are**.

MAPE may be supplementary only because very low-yield observations make percentage error unstable. `R^2` is diagnostic only, not a substitute for absolute error.

## 7. Release-Time Scenario Envelope

Actual release dates are unavailable historically. Never pretend legacy imputed release is observed.

Once `F_RD_lookup` exists, evaluate the supported local release window:

```text
release HST in [21,30]
```

For scenario `i`:

```text
Y_ref_i = Y(d_i, release=30)
Y_min_i = min(Y(d_i,r) for r in supported release window)
Y_max_i = max(Y(d_i,r) for r in supported release window)
```

Then report:

```text
scenario-envelope coverage =
  count(actual_i in [Y_min_i,Y_max_i]) / N
```

Call this a **scenario envelope**, not a 95% confidence interval.

## 8. Calendar Validation

Audited coverage:

- planting date available: 12/36;
- harvest date available: 15/36;
- both together: 12/36.

Harvest-window validation uses the mechanically reconstructed `N=12` only.
For this comparator, an observed historical planting date is interpreted as
the field-transplanting date. This is an explicit validation assumption; if
that equivalence cannot be maintained, use `TIMING_SEMANTICS_UNRESOLVED` and
exclude the row rather than changing the calendar window.

```text
Hit_i = 1 if actual harvest date in predicted window else 0
Coverage = sum(Hit_i)/N
```

Distance-to-window error:

```text
0 if inside window
min(abs(actual-min), abs(actual-max)) if outside
```

Release date, pull date, and active duration have no historical actual comparator and do not receive fake accuracy metrics.

## 9. Survival Validation

No aggregate compatible `N_survive_actual` exists.

Therefore:

- no survival MAE;
- no comparison against `N_sold_actual`;
- no inversion of duck sales revenue into survival;
- use deterministic formula tests, expert boundary evidence, literature consistency, and documented individual case diagnostics only.

## 10. Duck Terminal Value

Do not compare:

```text
V_duck_end
```

with historical realized duck sales revenue as if they were the same variable.

Validation is price plausibility/sensitivity only.

## 11. Paddy Revenue

When yield becomes available, report two diagnostics:

### Operational R2

```text
Revenue_pred_operational = Yield_pred_total * 6500
```

This uses current regulatory HPP benchmark.

### Price-neutral diagnostic

```text
Revenue_pred_yield_only = Yield_pred_total * historical_price
```

Historical price is used only inside the validation harness to isolate yield error; it is not a runtime user input or R2 calibration parameter.

## 12. Component Coverage

Previously audited clean-set coverage:

| Component | Comparator availability |
|---|---:|
| Yield | 36/36 |
| Paddy price | 36/36 |
| Positive duck purchase price | 29/36 |
| Positive feed cost | 23/36 |
| Positive duck sale revenue | 16/36 |
| Positive net/infrastructure proxy | 17/36 |
| Positive cage | 9/36 |
| Positive pesticide | 4/36 |
| Positive fertilizer | 1/36 |
| Positive weeding cash | 0/36 |
| Actual duck age | 0/36 |
| Actual active duration | 0/36 |

Every metric must report its own effective `N`.

## 13. Duck Purchase Cost

This is deterministic accounting:

```text
C_duck_buy = J*p_duck_buy_eff
```

V1 tests must prove exact identity.

Historical purchase prices are plausibility/comparator context only; they do not recalibrate the Rp26,500 default.

For missing historical price, a replay may use R2 default only with provenance `LOCAL_DEFAULT`; it cannot be treated as an observed historical purchase cost.

## 14. Feed Cost

Current R2 feed cost is `UNAVAILABLE`; therefore no feed accuracy metric may be produced yet.

If a future approved feed lookup activates it, compare only against eligible documented-positive observations (`N=23` in the audited data) and report MAE/MedAE/WAPE with missingness caveats.

## 15. Weeding, Pesticide, Fertilizer, Infrastructure

### Weeding

No historical cash ground truth: no monetary accuracy metric.

### Pesticide

Only sparse 4 positive records and heterogeneous mechanism: case diagnostics only.

### Fertilizer

Only 1 positive record: descriptive only, not statistical accuracy.

### Infrastructure

Net records (`N=17`) and cage records (`N=9`) may support secondary comparison of compatible cost constructs, but unrecorded zero must not be assumed actual zero.

## 16. Profit/Margin

Never compare old farmer-profit columns directly to R2 `Margin_core` or `Profit_full_est` because ledger definitions differ.

If `CostCompletenessFlag=INCOMPLETE`, `Profit_full_est` must remain null and cannot have an accuracy metric.

## 17. Repeated Farmers and Uncertainty

Clean set includes repeated farmers. If reporting uncertainty around aggregate metrics, use **cluster bootstrap by farmer**, not independent row bootstrap.

Suggested procedure:

1. sample farmers with replacement;
2. include all cycles belonging to each sampled farmer;
3. compute metric;
4. repeat e.g. 2,000 times;
5. report percentile 95% empirical bootstrap interval.

Do not call it a universal population guarantee.

## 18. Expert Evidence Transfer

Each R2 parameter/formula gets one label:

- `DIRECT` — exact concept/parameter was judged.
- `PARTIAL` — concept same, mathematical form changed or only boundary was judged.
- `NONE` — new R2 formula was not evaluated by expert.

Important examples:

- `N_survive != N_sold` -> DIRECT.
- supported density boundary -> DIRECT.
- safe survival 0.90 -> PARTIAL.
- new yield lookup formula -> NONE until specifically reviewed.
- old 45.84 kg/are plausibility -> historical snapshot only; not validation of R2 yield.

The expert's earlier ~80% working confidence is **not** a statistical pass/fail threshold.

## 19. V1 Computational Tests Required

At minimum:

1. `A_m2=100*A_are`.
2. `d=J/A_are`.
3. missing/null purchase price -> 26,500.
4. provided positive purchase price passes through.
5. `0`, NaN, Infinity purchase price rejected.
6. age support boundaries 20/21/30/31.
7. Jarwo density boundaries 2/4.
8. Tegel density boundaries 2/3.
9. limited/high-risk/extrapolation classifications.
10. survival numeric only if both support flags `SUPPORTED`.
11. out-of-domain survival returns null/unavailable, not 60%.
12. calendar windows exact.
13. Inpari window is 90–100, not 109–116.
14. nutrient basis remains N-P2O5-K2O.
15. fertilizer solver constraints are satisfied.
16. KCl branch not used.
17. net min/ref/max range is monotonic.
18. feed numeric value remains null while lookup unavailable.
19. yield numeric value remains null while lookup unavailable.
20. `V_duck_end` never appears as cash duck sale revenue.
21. `Profit_full_est` is null while cost completeness incomplete.
22. disabled legacy formulas are not imported/called by production path.

## 20. V2/V3 Evidence Record

Every validation row should store:

```text
model_version
parameter_registry_version
backend_commit
source_workbook
source_row
farmer_cycle_id
input_value
input_provenance
actual_value
actual_provenance
prediction
availability_status
residual_if_compatible
supported_domain_flag
expert_transfer_label
notes
```

## 21. Acceptance Criteria

R2 can be considered implemented correctly even if empirical error is large, provided:

- active formulas match frozen R2 exactly;
- unresolved formulas do not execute;
- historical recap was not used for parameter fitting;
- all comparator provenance is traceable;
- missing values were not converted to zero;
- unavailable outputs remain unavailable;
- all implementation invariant/contract tests pass;
- empirical discrepancies are reported rather than tuned away.

A large error is a research result, not permission to recalibrate from the comparator set.

## 22. Phase-6 Pre-registered Yield Validation (execute only after R2.3 freeze)

This amendment supersedes the former exact-node/release scenario-envelope
proposal. Do not access any yield comparator outcome until the Phase-6 code,
tests, registry `R2-2026-08-26.3`, and matching committed freeze are complete
on a clean tree.

Primary yield cohort: every eligible clean record for which the frozen runtime
returns numeric `yield_ref_kg_per_are`. Report total clean N, prediction
coverage N and percent, strict supported-domain N, cultivar subgroup N
(`INPARI_GROUP` and `SERTANI_GROUP` separately), and planting-system subgroup
N where sufficiently large. Never present one pooled headline without the
cultivar subgroup disclosure; Sertani reports its low-evidence warning.

For each compatible row, calculate reference-value `MAE`, `RMSE`, `MedAE`,
`MBE`, and `WAPE`; `R²` is optional diagnostic and MAPE is supplementary only
where denominators are valid. Report metric units and effective N.

For every predicted row pre-register:

```text
actual_inside_envelope = yield_actual between [yield_pred_low, yield_pred_high]
```

Report `N`, covered N, coverage percent, mean envelope width, median envelope
width, and optionally normalized width. The name is **LITERATURE
EVIDENCE-ENVELOPE COVERAGE**, never confidence coverage or prediction-interval
coverage. Reference residuals and coverage use the frozen, independently
literature-derived parameters unchanged.

After the freeze is committed, no `Y_base` reference/range, `F_RD`, support
boundary, or envelope may be changed after inspecting comparator results. A
correction requires a new registry version and a new freeze before another
comparison. The validation harness may then add yield replay, row-level
reference predictions, residuals, envelope coverage, and subgroup metrics; it
must not import comparator outcomes into production modules.

## 23. Phase-6 Stress Amendment

Stress and boundary tests must prove age 20/31, non-supported density, unknown
cultivar group, missing baseline/factor, and all CAUTION/LIMITED_TEST/
HIGH_RISK/EXTRAPOLATION states return unavailable yield with null ref/low/high;
no nearest-value fallback, interpolation, extrapolation, NaN, or Infinity;
correct reason/warning codes; and downstream economic null propagation.
