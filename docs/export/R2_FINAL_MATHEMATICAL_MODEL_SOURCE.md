# R2 Final Mathematical Model Source

> **Role:** `CURRENT_AUTHORITATIVE` export source for later mathematical-model
> DOCX generation.
> **This file is not the final DOCX.**
> **Release:** `R2_PHASE6_TECHNICAL_EMPIRICAL_RELEASE_CLOSED_WITH_LIMITATIONS`.

## 1. Purpose and scope

This source defines the frozen R2 mathematical and economic semantics used by
the production DSS core under `/api/v1/dss/*`. It is a source package for a
later document-generation step. It does not alter runtime code and it keeps
model parameters separate from retrospective validation diagnostics.

R2 uses exactly seven user concepts. It is availability-aware: a valid request
may return null scientific/economic numerics with an explicit availability or
status value. Historical recap workbooks are comparator evidence only and are
never used to fit, tune, or recalibrate R2.

## 2. Input definitions

| API field | Symbol | Unit/type | Definition and rule |
|---|---|---|---|
| `land_area_are` | `A_are` | are, finite `>0` | Active rice-duck interaction/program area, not total farm area |
| `duck_count` | `J` | ducks, integer `>0` | Initial duck count |
| `planting_date` | `D_tanam` | ISO date | Field-transplanting date for transplanted rice; HST is counted from this date |
| `planting_system` | `S` | code | `jajar_legowo` or `tegel` |
| `rice_variety` | `V` | code | `sertani` or `inpari`; resolves only through approved exact aliases |
| `duck_age_days` | `U_duck` | days, integer `>0` | Duck age at release/input time |
| `p_duck_buy` | `p_duck_buy_manual` | Rp/duck, optional finite `>0` | User price; omitted/null resolves to the registered default |

Approved local cultivar-group normalization is exact after trimming surrounding
whitespace and case-folding. It allows `Sertani`, `Sertani 13`, `Sertani a 13`,
`Seratih`, `Inpari`, and `Inpari 32`. Fuzzy matching, substrings, and unlisted
aliases fail closed.

## 3. Symbols, units, and precision

| Symbol | Meaning | Unit |
|---|---|---|
| `A_m2` | Active area converted to square metres | m² |
| `d` | Duck density | ducks/are |
| `p_duck_buy_eff` | Resolved duck purchase price | Rp/duck |
| `lambda_eff` | Conditional safe-domain survival reference | ratio |
| `N_survive` | Biological surviving-duck estimate | ducks |
| `Y_base_ref/low/high` | Cultivar-group baseline reference/evidence bounds | kg/are |
| `F_RD_ref` | Pooled external rice-duck reference factor | dimensionless |
| `Yield_are_ref/low/high` | Per-area yield reference/evidence envelope | kg/are |
| `Yield_total_ref/low/high` | Area-scaled yield reference/evidence envelope | kg |
| `p_gabah_ref` | Regulatory paddy HPP benchmark | Rp/kg |
| `V_duck_end` | Terminal duck asset value | Rp |
| `Margin_core` | Gross economic value less core direct cost | Rp/cycle |

Calculations use the project’s high-precision decimal path and do not round in
the middle of a calculation. Serialization precision is separate from the
mathematical definition.

## 4. Normalization

The deterministic normalization equations are:

```text
[system-design] A_m2 = 100 * A_are
[system-design] d = J / A_are
[mixed] p_duck_buy_eff = p_duck_buy_manual if supplied; otherwise 26_500
```

The default Rp26,500/duck is the midpoint of the local-estimate range
Rp25,000–28,000/duck. The default is `mixed`: local evidence supplies the
range and system design selects the midpoint.

## 5. Calendar equations

All HST values are measured from `D_tanam`, whose transplanted-rice meaning is
the explicit validation/system-design assumption
`HST_FROM_FIELD_TRANSPLANTING`.

```text
[local-estimate] HarvestHST(Sertani/Seratih) = [100, 110]
[local-estimate] HarvestHST(Inpari)          = [90, 100]
[local-estimate] D_harvest_window = D_tanam + HarvestHST(V)
[local-estimate] D_release_window = [D_tanam + 21, D_tanam + 30]
[local-estimate] D_pull_window    = [D_tanam + 56, D_tanam + 60]
[local-estimate] t_active_ref     = 32 days
support interval                  = [28, 40] days
```

Release and pull are independently documented windows; neither is derived as
an exact pair from the active-duration reference. Fixed 21-to-65 calendars,
Inpari 109–116/134, and Sertani 114 HST are not R2 semantics.

## 6. Density classifications

```text
[system-design] d = J / A_are
[mixed] Jarwo SUPPORTED: 2 <= d <= 4
[mixed] Tegel SUPPORTED: 2 <= d <= 3
[mixed] LIMITED_TEST: 5 <= d <= 6 (approximate band)
[mixed] HIGH_RISK: d >= 8 (approximate threshold)
```

For a continuous value outside a system-specific supported interval and not in
the limited/high-risk bands, classify as `EXTRAPOLATION`. The classifier is
metadata and warning logic only. It does not create a density penalty or yield
multiplier.

## 7. Age classifications

```text
[mixed] AgeSupportFlag(U_duck) =
  CAUTION             if U_duck < 21
  SUPPORTED           if 21 <= U_duck <= 30
  OUTSIDE_LOCAL_RANGE if U_duck > 30
```

Age is an applicability classifier. It has no numerical multiplier for yield,
survival, feed, or economics.

## 8. Survival equation and gates

Biological survival state is separate from sales state. `N_survive` is never
aliased to `N_sold`, `N_sold_DSS`, realized sale quantity, or duck revenue.

```text
[local-estimate] lambda_safe_ref = 0.90

[mixed] lambda_eff = 0.90 only if
  AgeSupportFlag == SUPPORTED
  and DensitySupportFlag == SUPPORTED
otherwise lambda_eff = UNAVAILABLE

[system-design] N_survive = floor(J * lambda_eff)
only when lambda_eff is available
```

The 0.90 value is a safe-context local working estimate, not a universal
biological survival rate. Outside the joint gate, survival numerics are null.

## 9. Yield formulation

The active Phase-6 yield configuration is a supported-domain, pooled-global
reference. It is literature-uncalibrated and not a Bali calibration.

### 9.1 Baseline records

| Cultivar group | Reference | Low | High | Evidence status |
|---|---:|---:|---:|---|
| `INPARI_GROUP` | 53.5 kg/are | 20.0 kg/are | 78.4 kg/are | `LITERATURE_UNCALIBRATED`; external field distribution N=43 |
| `SERTANI_GROUP` | 44.5 kg/are | 22.3 kg/are | 66.7 kg/are | `LITERATURE_UNCALIBRATED`; `LOW_EVIDENCE_TWO_LOCATION_EXTERNAL_RANGE` |

### 9.2 Reference factor and equations

`F_RD_ref = 1.028`, source ID `FRD-FENG-2024`, is a pooled external reference.
It is not a system, density, release-time, or cultivar-specific coefficient.

```text
[literature-uncalibrated]
Yield_are_ref  = Y_base_ref(V_group)  * F_RD_ref
Yield_are_low  = Y_base_low(V_group)  * F_RD_ref
Yield_are_high = Y_base_high(V_group) * F_RD_ref

[system-design]
Yield_total_ref  = Yield_are_ref  * A_are
Yield_total_low  = Yield_are_low  * A_are
Yield_total_high = Yield_are_high * A_are
```

Numeric yield is available only when the cultivar group resolves, the approved
baseline record exists, age is `SUPPORTED`, density is system-specifically
`SUPPORTED`, and the F_RD record and required inputs are valid. This is
`SUPPORTED_DOMAIN_GLOBAL_F_RD`.

`Yield_are_low/high` form the `LITERATURE_EVIDENCE_ENVELOPE`. They are
literature-derived sensitivity bounds, not a confidence interval, prediction
interval, credible interval, or formal probabilistic uncertainty interval.
There is no interpolation, extrapolation, nearest-node selection,
cross-system fallback, or new moderator coefficient.

## 10. Fertilizer equations

The single nutrient basis is N–P2O5–K2O.

```text
[literature-uncalibrated] N_need_are    = 1.1761 kg N/are
[literature-uncalibrated] P2O5_need_are = 0.2745 kg P2O5/are
[literature-uncalibrated] K2O_need_are  = 0.2745 kg K2O/are

N_need    = N_need_are    * A_are
P2O5_need = P2O5_need_are * A_are
K2O_need  = K2O_need_are  * A_are
```

Manure credit is unavailable, so the active state is baseline-no-credit:

```text
N_net    = N_need
P2O5_net = P2O5_need
K2O_net  = K2O_need
```

This is not a claim that duck manure contributes zero nutrients.

Active products are Urea (46% N) and NPK Phonska (15-10-12 N-P2O5-K2O).
HET prices are Rp1,800/kg for Urea and Rp1,840/kg for NPK. KCl is excluded
until an exact valid price/source is configured.

```text
min C_fert = 1_800*Q_urea + 1_840*Q_npk

subject to:
  0.46*Q_urea + 0.15*Q_npk >= N_net
  0.10*Q_npk >= P2O5_net
  0.12*Q_npk >= K2O_net
  Q_urea, Q_npk >= 0

Q_npk* = max(P2O5_net/0.10, K2O_net/0.12)
Q_urea* = max(0, (N_net - 0.15*Q_npk*)/0.46)
C_fert_baseline = 1_800*Q_urea* + 1_840*Q_npk*
```

## 11. Infrastructure equations

Because polygon geometry is not an input, R2 uses an explicit square-equivalent
design:

```text
[mixed] L_net_eq = 4 * sqrt(100 * A_are)
[local-estimate] p_net_m in [6_000, 6_750] Rp/m
[local-estimate] n_net_life in [2, 3] cycles

C_net_cycle_min = L_net_eq * 6_000 / 3
C_net_cycle_ref = L_net_eq * 6_750 / 2.5
C_net_cycle_max = L_net_eq * 6_750 / 2
```

These are equivalent-area estimates. Cage cost is available only per unit:

```text
[local-estimate] C_cage_unit_cycle in [150_000, 200_000] Rp/unit/cycle
reference midpoint = 175_000 Rp/unit/cycle
```

Total cage cost is unavailable because no sourced capacity/unit-count rule
exists.

## 12. Other cost equations and availability

Duck purchase is an active direct cost:

```text
[mixed] C_duck_buy = J * p_duck_buy_eff
```

Feed retains only its structural relationship and is unavailable at runtime:

```text
[literature-uncalibrated]
C_feed = sum_t (N_t * q_feed(t,U,d) * p_feed(t))
[system-design] CostFeedAvailabilityFlag = UNAVAILABLE
```

No Rp4,500 or Rp20,000 shortcut is allowed. Weeding returns a baseline range
`A_are * [6,000, 38,000]` Rp; monetary saving is unavailable. Pest effect is
`CONTEXT_SPECIFIC`; monetary pesticide saving is unavailable. No universal pest
or weed cash coefficient is executable.

## 13. Paddy revenue and terminal duck asset

The paddy benchmark is a regulatory HPP, not a market-price forecast:

```text
[regulatory-locked] p_gabah_ref = 6_500 Rp/kg

Revenue_gabah_ref  = Yield_total_ref  * p_gabah_ref
Revenue_gabah_low  = Yield_total_low  * p_gabah_ref
Revenue_gabah_high = Yield_total_high * p_gabah_ref
```

These values exist only when yield is available. Terminal duck value is an
asset value, not realized duck cash revenue:

```text
[local-estimate] p_duck_end_ref = 45_000 Rp/duck
sensitivity range = [30_000, 60_000] Rp/duck

V_duck_end_ref = N_survive * 45_000
V_duck_end_min = N_survive * 30_000
V_duck_end_max = N_survive * 60_000
terminal_value_is_cash_revenue = false
```

## 14. Gross economic value, core margin, and full profit

```text
CashRevenue_ref/low/high = Revenue_gabah_ref/low/high

GrossEconomicValue_ref = Revenue_gabah_ref + V_duck_end_ref
GrossEconomicValue_low = Revenue_gabah_low + V_duck_end_ref
GrossEconomicValue_high = Revenue_gabah_high + V_duck_end_ref

Cost_core_direct = C_duck_buy + C_net_cycle_ref
Cost_total_available = sum(numerically available cost components only)

Margin_core_ref = GrossEconomicValue_ref - Cost_core_direct
Margin_core_low = GrossEconomicValue_low - Cost_core_direct
Margin_core_high = GrossEconomicValue_high - Cost_core_direct
```

Gross value and core margin require both available yield and survival. They are
not called net profit. `Cost_total_available` is a partial subtotal and never
coerces unknown amounts to zero.

```text
CostCompletenessFlag = COMPLETE only when every configured full-ledger cost
component is available; otherwise INCOMPLETE.

Profit_full_est = GrossEconomicValue - Cost_full_est
only when CostCompletenessFlag == COMPLETE
```

The current full ledger is incomplete because feed amount and total cage cost
are unavailable; `Profit_full_est` is therefore null with an unavailable status.

## 15. Component availability contract

| Component | Current state |
|---|---|
| Calendar | Active windows |
| Age/density | Active applicability classifiers |
| Survival | Conditional; supported age and density only |
| Yield | Active range/reference inside full evidence gate |
| Fertilizer | Active baseline-no-credit |
| Duck purchase | Active direct cost |
| Net infrastructure | Active equivalent-area range |
| Cage per-unit | Active range; total unavailable |
| Feed | Unavailable |
| Weed saving | Unavailable; baseline range only |
| Pest effect | Descriptive; monetary saving unavailable |
| Manure credit | Unavailable |
| Paddy revenue | Conditional on yield |
| Terminal duck value | Conditional on survival; asset value |
| Core margin | Conditional on yield and survival |
| Full profit | Unavailable while ledger incomplete |

## 16. Fail-closed rules

1. Unresolved cultivar group or missing baseline returns null yield.
2. Missing F_RD reference returns null yield.
3. Unsupported age or density returns null yield and null envelope values.
4. Unsupported age or density returns null survival; there is no 60% fallback.
5. Missing feed lookup returns null feed cost.
6. Missing cage capacity returns null total cage cost.
7. Missing KCl price excludes the KCl branch; Rp9,500 is not used.
8. Incomplete ledger returns null full profit.
9. Unknown values are never coerced to zero in an explicitly named full total.
10. No interpolation, extrapolation, nearest-node, cross-system, historical-
    median, or legacy-constant fallback is permitted.

Canonical yield reason codes are `CULTIVAR_GROUP_UNRESOLVED`,
`Y_BASE_GROUP_LOOKUP_MISSING`, `AGE_OUTSIDE_SUPPORTED_DOMAIN`,
`DENSITY_OUTSIDE_SUPPORTED_DOMAIN`, `FRD_REFERENCE_MISSING`, and
`EVIDENCE_DOMAIN_UNSUPPORTED`.

## 17. Parameter provenance

| Parameter family | Provenance/status | Source or limitation |
|---|---|---|
| Calendar, age, density boundaries | `local-estimate` / `mixed` | Internal local data and documented boundary evidence |
| Safe survival reference | `local-estimate` | Expert safe-context evidence; conditional only |
| Cultivar-group yield ranges | `literature-uncalibrated` | `YB-INPARI-SULAEMAN-2024`; `YB-SERTANI-SULAEMAN-2022` |
| Rice-duck factor | `literature-uncalibrated` | `FRD-FENG-2024`; pooled external reference |
| Nutrient baseline | `literature-uncalibrated` | Bali RDIS baseline reconstruction and official product sources |
| Fertilizer composition/HET | `regulatory-locked` | Official product/regulatory sources |
| Paddy price benchmark | `regulatory-locked` | Inpres 4/2026 HPP benchmark |
| Duck purchase and terminal price | `mixed` / `local-estimate` | Local range and terminal-value evidence |
| Net, cage, and weeding ranges | `local-estimate` | Local cost evidence; geometry/capacity limitations remain explicit |
| Feed, KCl, manure credit, monetary savings | `UNAVAILABLE` or descriptive | Required source/semantic rule is incomplete |

The canonical provenance vocabulary is `local-calibrated`, `local-estimate`,
`literature-uncalibrated`, `system-design`, `regulatory-locked`, and `mixed`.
Execution state is separate from provenance.

## 18. Limitations

- External yield ranges are not local Bali calibration and the Sertani evidence
  is limited to two external locations.
- Supported-domain gating leaves some historical cycles without numeric yield.
- A literature evidence envelope is broad sensitivity evidence, not statistical
  uncertainty or precision.
- The transplanting-date interpretation is a validation assumption.
- No compatible aggregate survival ground truth exists.
- Feed quantity/price and cage capacity are missing; full profit is unavailable.
- Weed/pest monetary conversion and manure credit are unsupported.
- Historical comparator values are not model parameters.
- Final expert judgement is pending but non-blocking for this release.

## 19. Version and freeze identity

| Item | Value |
|---|---|
| Model version | `R2` |
| Parameter registry | `R2-2026-08-26.3` |
| Freeze | `R2-FREEZE-2026-08-26.5` |
| Scientific target SHA | `b10b0a1f83357c5db1d6cdfb9c41eaa84b6727a7` |
| Original official evidence commit | `eda6a8035b89174e225999dec3aac0ec98685510` |
| F-03 correction commit | `d2aa2f833bfa2c943b2d8266a05edf96fd5d78db` |
| Phase-6E sign-off commit | `186ebf9f4542cd056f69d6b7639f9870c5372959` |
| Freeze effective date | `2026-08-26` |
| History schema for new simulations | `4` |
| Release closure status | `R2_PHASE6_TECHNICAL_EMPIRICAL_RELEASE_CLOSED_WITH_LIMITATIONS` |

No `.6` freeze is created. The freeze means immutable validation target, not
universal empirical validation or final expert validation.

## 20. Separate validation status summary

The following is evidence status, not a parameter definition. Exact values are
copied from the Phase-6D-R corrected evidence and the Phase-6E independent
metric audit so this export source agrees with the validation-methodology and
fact-package sources.

### Primary yield

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
| Envelope coverage | `20/22 = 90.9090909090909%` |
| Mean envelope width | `47.60574545454545 kg/are` |
| Median envelope width | `45.6432 kg/are` |

### Subgroups

| Subgroup | Actual N | Predicted N | Coverage | MAE | RMSE | WAPE | Envelope coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| Strict supported domain | 17 | 17 | 100% | 9.855426004470589 | 14.436931455685956 | 23.478704172402782% | 88.23529411764706% |
| `INPARI_GROUP` | 5 | 3 | 60% | 8.309602693333334 | 10.467747785900904 | 17.60201414199902% | 100% |
| `SERTANI_GROUP` | 31 | 19 | 61.29032258064516% | 9.322029107157894 | 13.83058101193071 | 21.206653635894305% | 89.47368421052632% |
| Jajar Legowo | 32 | 20 | 62.5% | 8.8949165408 | 13.481510495508598 | 19.96657912338301% | 90% |
| Tegel | 4 | 2 | 50% | not reported | not reported | not reported | count-only |

The strict cohort does not improve point performance. `INPARI_GROUP` has only
three numeric predictions. `SERTANI_GROUP` requires
`LOW_EVIDENCE_TWO_LOCATION_EXTERNAL_RANGE`. Tegel is
`COUNT_ONLY_SMALL_N`.

### Bootstrap, calendar, purchase, and revenue

| Item | Exact result |
|---|---|
| Bootstrap | cluster unit `farmer_cluster_id`; 2,000 resamples; seed `20260826`; empirical percentiles `2.5 / 97.5%` |
| MAE bootstrap interval | `[5.338547626190476, 14.255541432705883]` |
| RMSE bootstrap interval | `[7.48075664347243, 19.285367878437786]` |
| MBE bootstrap interval | `[-2.391187468095236, 8.891407133200001]` |
| WAPE bootstrap interval | `[11.282456480039396, 36.907197894190645]` |
| Envelope coverage bootstrap interval | `[0.75, 1.0]` |
| Calendar | N=`12`; hits=`4`; coverage=`33.33333333333333%`; mean/median distance=`5` days; `HST_FROM_FIELD_TRANSPLANTING`; `VALIDATION_ASSUMPTION` |
| Purchase | `OBSERVED_VALUE=27`; `DERIVED_ACTUAL=2`; `EXPLICIT_ZERO=4`; `MISSING_UNKNOWN=3`; strict N=`27` |
| `CURRENT_HPP_OPERATIONAL_VALUE_DIAGNOSTIC` | N actual=`36`, predicted=`22`; MAE=`311527.7986064933`; RMSE=`420128.394071854`; MedAE=`254786.2200136502`; MBE=`41782.65592655224`; WAPE=`16.576559236396317%` Rp/cycle |
| `PRICE_NEUTRAL_HISTORICAL_PRICE_DIAGNOSTIC` | N actual=`36`, predicted=`22`; MAE=`297042.3196077955`; RMSE=`400883.6711827306`; MedAE=`241702.28101260017`; MBE=`30976.365834068216`; WAPE=`15.987950881921265%` Rp/cycle |
| Expert final | `EXPERT_FINAL_REVIEW=PENDING_NON_BLOCKING_EVIDENCE_STREAM` |

These intervals are cluster-bootstrap empirical intervals around aggregate
validation metrics, not prediction intervals or parameter confidence intervals.
The revenue diagnostics are not realized-revenue or profit accuracy.
