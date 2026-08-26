# Model Matematika Ekonomi R2 — Backend Source of Truth

> **Status:** CANONICAL IMPLEMENTATION SSOT  
> **Scope:** `/api/v1/dss/*` production DSS core only  
> **Model freeze target:** `R2`  
> **Historical recap role:** comparator only; never calibration  
> **Important:** `PENDING_LOOKUP`, `UNAVAILABLE`, and `INCOMPLETE` are valid runtime states. Do not fill them with legacy constants.

## 1. Runtime Inputs — Exactly Seven User Inputs

| API concept | Symbol | Rule |
|---|---|---|
| Active duck area | `A_are` | Required, `> 0` are. Active interaction area, not total farm area. |
| Initial duck count | `J` | Required integer, `> 0`. |
| Planting date | `D_tanam` | Required ISO date. For transplanted rice this means **field transplanting date**; HST is counted from transplanting. This is a `system-design` / validation assumption, not a newly observed field fact. |
| Planting system | `S` | Required; canonical codes `jajar_legowo` or `tegel`. |
| Rice variety | `V` | Required; the seven-input public API stays unchanged. Internally, only the approved local cultivar-group mapping below may be used for future yield lookup. |
| Duck age | `U_duck` | Required integer `> 0` days. |
| Duck purchase price | `p_duck_buy_manual` | **Optional**. Missing/null → internal default Rp26,500/duck. A supplied value must be `> 0`. Do not treat numeric `0` as a substitute for missing. |

### 1.1 Purchase-price resolution

```text
[system-design] A_m2 = 100 * A_are
[system-design] d = J / A_are
[mixed] p_duck_buy_eff = p_duck_buy_manual if supplied; otherwise 26_500
```

Default Rp26,500 is midpoint of local Rp25,000–28,000 range. The local range is `local-estimate`; midpoint selection is `system-design`; therefore effective default is `mixed`.

### 1.2 Evidence-bounded local cultivar groups

The historical labels support grouping for model lookup, not genetic identity.
Normalization is exact after trimming surrounding whitespace and comparing
case-insensitively; fuzzy matching and unlisted aliases are forbidden.

| Internal group | Approved source labels |
|---|---|
| `SERTANI_GROUP` | `Sertani`, `Sertani 13`, `Sertani a 13`, `Seratih` |
| `INPARI_GROUP` | `Inpari`, `Inpari 32` |

The public options remain `sertani` and `inpari`; both resolve deterministically
to their corresponding local group. An unlisted label resolves to no group and
must fail closed with `CULTIVAR_GROUP_UNRESOLVED`.

## 2. Calendar Engine

Calendar returns **windows**, not false-precision point estimates.

`D_tanam` is the field-transplanting date for transplanted rice. Every R2 HST
window below is counted from that date. Historical rows may enter calendar
validation only when both planting/transplanting date and harvest date are
observed. This semantic equivalence is a `system-design` / validation
assumption and does not change any numeric window.

```text
[local-estimate] HarvestHST(V):
  Sertani/Seratih -> [100, 110]
  Inpari          -> [90, 100]

[local-estimate] D_harvest_window =
  [D_tanam + HST_min(V), D_tanam + HST_max(V)]

[local-estimate] D_release_window =
  [D_tanam + 21, D_tanam + 30]

[local-estimate] D_pull_window =
  [D_tanam + 56, D_tanam + 60]

[local-estimate] t_active_ref = 32 days
support interval = [28, 40] days
```

Do not derive an exact release/pull pair from `t_active_ref`; these are independently documented local estimates.

### Forbidden calendar semantics

- fixed `HST_in=21`, `HST_out=65`, `t_active=44`.
- Inpari 109–116 or 134 HST.
- Sertani 114 HST.
- synthetic planting dates or historical default dates.

## 3. Age Support Engine

Age is a support/applicability classifier only.

```text
[mixed] AgeSupportFlag(U_duck) =
  CAUTION             if U_duck < 21
  SUPPORTED           if 21 <= U_duck <= 30
  OUTSIDE_LOCAL_RANGE if U_duck > 30
```

No numerical age multiplier may change yield, survival, feed, or other economics.

## 4. Density Support Engine

```text
[system-design] d = J / A_are
```

Canonical evidence-backed support:

```text
[mixed] Jarwo SUPPORTED: 2 <= d <= 4 duck/are
[mixed] Tegel SUPPORTED: 2 <= d <= 3 duck/are
[mixed] LIMITED_TEST: approximately 5–6 duck/are
[mixed] HIGH_RISK: approximately >= 8 duck/are
```

For continuous values outside explicitly supported ranges and not clearly in the limited-test/high-risk boundary, use `EXTRAPOLATION`.

Suggested deterministic classifier:

1. if `d >= 8` -> `HIGH_RISK`;
2. else if system-specific supported range -> `SUPPORTED`;
3. else if `5 <= d <= 6` -> `LIMITED_TEST`;
4. else -> `EXTRAPOLATION`.

This classifier is metadata/warning logic only. It does **not** create a penalty coefficient.

## 5. Survival Engine

### 5.1 Biological state is separate from sales state

`N_survive` must never be aliased to `N_sold`, `N_sold_DSS`, realized sale quantity, or duck revenue.

### 5.2 Conditional safe-domain estimate

```text
[local-estimate] lambda_safe_ref = 0.90

[mixed] lambda_eff = 0.90
  only if AgeSupportFlag == SUPPORTED
  and DensitySupportFlag == SUPPORTED;
  otherwise UNAVAILABLE

[system-design] N_survive = floor(J * lambda_eff)
  only when lambda_eff is available
```

The 0.90 value is a safe-context local working estimate, not a universal biological survival rate.

### Forbidden survival semantics

- `lambda_eff=0.78125` or any derivative.
- `(1-0.50*R_age)*(1-0.45*P_over)`.
- `N_survive=J` for `d<=8`.
- `N_survive=floor(0.60*J)` for `d>8`.
- using historical sold/initial ratios as survival calibration.

## 6. Yield Engine

R2 does **not** have a scientifically complete numeric yield runtime yet.

Canonical structural formula:

```text
[mixed] Yield_are_ref = Y_base(cultivar_group_code) * F_RD_lookup(system_scope, d, release=30)
[system-design] Yield_total = Yield_are_ref * A_are
```

Availability gate:

```text
[system-design] YieldAvailabilityFlag = AVAILABLE
  only if:
    1. an approved local cultivar_group_code is resolved;
    2. Y_base(group) has a traceable approved record;
    3. F_RD has a traceable approved record for the exact system/density/release node;
    4. the exact node is inside the record's supported domain;
    5. release timing semantics are equivalent to the R2 transplanting-based HST semantics.
otherwise UNAVAILABLE.
```

Until those lookups are explicitly populated and provenance-tested:

```text
Y_base = null
F_RD_lookup = null
Yield_are = null
Yield_total = null
YieldAvailabilityFlag = UNAVAILABLE
```

Current evidence closure is explicit: `LOCAL_CULTIVAR_GROUPING_READY` and
`LOOKUP_STRUCTURE_READY`, but `Y_BASE_NOT_READY`, `F_RD_NOT_READY`, and
`SYSTEM_UNRESOLVED_FAIL_CLOSED`. The verified density grid is descriptive
evidence only and is not executable without approved numeric records.

Future stores are discrete lookups only. Exact equality is required for
`cultivar_group_code`, `system_scope`, `density_are`, and `release_day`.
Interpolation, extrapolation, nearest-neighbour selection, range fallback,
and cross-system fallback are forbidden. The production store is empty.

### Forbidden yield fallbacks

Never fall back to:

- `47.8767507 kg/are`.
- any median from historical recap.
- `F_sys(Tegel)=1.211`.
- `F_var=1` as biological equality assumption.
- custom exponential density curve.
- age multiplier.
- extrapolation of literature effect outside its domain without explicit status.

## 7. Nutrient / Fertilizer Baseline Engine

Use one consistent nutrient basis: **N–P2O5–K2O**.

```text
[literature-uncalibrated] N_need_are    = 1.1761 kg N/are
[literature-uncalibrated] P2O5_need_are = 0.2745 kg P2O5/are
[literature-uncalibrated] K2O_need_are  = 0.2745 kg K2O/are

[mixed] N_need    = N_need_are * A_are
[mixed] P2O5_need = P2O5_need_are * A_are
[mixed] K2O_need  = K2O_need_are * A_are
```

Duck manure credit is not executable:

```text
[mixed] N_net    = N_need
[mixed] P2O5_net = P2O5_need
[mixed] K2O_net  = K2O_need
```

This is a **baseline-no-credit** state; it is not a claim that duck manure contributes zero nutrients.

### 7.1 Active product set

- Urea: 46% N.
- NPK Phonska: 15-10-12 N-P2O5-K2O.
- HET Urea: Rp1,800/kg.
- HET NPK: Rp1,840/kg.
- KCl is excluded until a valid exact price/source is configured.

```text
[mixed] min C_fert = 1_800*Q_urea + 1_840*Q_npk
subject to:
  0.46*Q_urea + 0.15*Q_npk >= N_net
  0.10*Q_npk >= P2O5_net
  0.12*Q_npk >= K2O_net
  Q_urea, Q_npk >= 0

[mixed] Q_npk* = max(P2O5_net/0.10, K2O_net/0.12)
[mixed] Q_urea* = max(0, (N_net - 0.15*Q_npk*)/0.46)
[mixed] C_fert_baseline = 1_800*Q_urea* + 1_840*Q_npk*
```

## 8. Duck Purchase Cost

```text
[mixed] C_duck_buy = J * p_duck_buy_eff
```

This is an active direct cost.

## 9. Feed Cost

Only the structural relationship is retained:

```text
[literature-uncalibrated]
C_feed = sum_t (N_t * q_feed(t,U,d) * p_feed(t))
```

Runtime state:

```text
[system-design] CostFeedAvailabilityFlag = UNAVAILABLE
```

until traceable `q_feed` and `p_feed` lookup data are configured. Do not use Rp4,500, Rp20,000, or an age/density modifier as a production shortcut.

## 10. Infrastructure Engine

### 10.1 Net/fence

Local evidence:

- price: Rp1.2–1.35 million per 200 m = Rp6,000–6,750/m;
- lifetime: 2–3 cycles.

Because polygon geometry is not one of the seven inputs, use an explicit square-equivalent design:

```text
[mixed] L_net_eq = 4 * sqrt(100 * A_are)
[local-estimate] p_net_m in [6_000, 6_750] Rp/m
[local-estimate] n_net_life in [2, 3] cycles

[mixed] C_net_cycle_min = L_net_eq * 6_000 / 3
[mixed] C_net_cycle_max = L_net_eq * 6_750 / 2
[mixed] C_net_cycle_ref = L_net_eq * 6_750 / 2.5
```

Return all three values and label them equivalent-area estimates.

### 10.2 Cage

```text
[local-estimate] C_cage_unit_cycle in [150_000, 200_000] Rp/unit/cycle
reference midpoint = 175_000
```

Total cage cost is `UNAVAILABLE` until a sourced capacity/unit-count rule exists.

## 11. Weed and Pest

### 11.1 Weed

```text
[literature-uncalibrated]
WeedSuppressionIndicator = evidence-based descriptor
```

No automatic conversion to cash saving.

```text
[local-estimate]
C_weeding_baseline_range = A_are * [6_000, 38_000]

[system-design]
C_weeding_saved = UNAVAILABLE
```

### 11.2 Pest

```text
[literature-uncalibrated] PestEffect = CONTEXT_SPECIFIC
[system-design] C_pesticide_saved = UNAVAILABLE
```

No universal pest-reduction scalar.

## 12. Paddy Benchmark and Duck Terminal Value

```text
[regulatory-locked] p_gabah_ref = 6_500 Rp/kg
[mixed] Revenue_gabah = Yield_total * p_gabah_ref
  only if YieldAvailabilityFlag == AVAILABLE
```

`p_gabah_ref` is an HPP regulatory benchmark, not a market-price forecast.

Duck terminal value:

```text
[local-estimate] p_duck_end_ref = 45_000 Rp/duck
sensitivity range = [30_000, 60_000]

[local-estimate] V_duck_end = N_survive * 45_000
range = [N_survive*30_000, N_survive*60_000]
```

`V_duck_end` is **not realized duck cash revenue**.

## 13. Economic Ledger

```text
[system-design] CashRevenue = Revenue_gabah
[system-design] GrossEconomicValue = Revenue_gabah + V_duck_end

[mixed] Cost_core_direct = C_duck_buy + C_net_cycle_ref
[mixed] Cost_total_available = sum(all cost components whose execution state is AVAILABLE)

[system-design] CostCompletenessFlag = COMPLETE
  only if every cost component required by the full configured ledger is AVAILABLE;
  otherwise INCOMPLETE.

[mixed] Margin_core = GrossEconomicValue - Cost_core_direct
  only if Yield and N_survive are available.

[mixed] Profit_full_est = GrossEconomicValue - Cost_full_est
  only if CostCompletenessFlag == COMPLETE.
```

Do not label `Margin_core` as net profit. Do not emit a numeric `Profit_full_est` while cost completeness is incomplete.

## 14. Canonical Reliability Flags

| Flag | Values |
|---|---|
| `age_support` | `CAUTION`, `SUPPORTED`, `OUTSIDE_LOCAL_RANGE` |
| `density_support` | `SUPPORTED`, `LIMITED_TEST`, `HIGH_RISK`, `EXTRAPOLATION` |
| `survival_availability` | `AVAILABLE`, `UNAVAILABLE` |
| `yield_availability` | `AVAILABLE`, `UNAVAILABLE` |
| `feed_cost_availability` | `AVAILABLE`, `UNAVAILABLE` |
| `cost_completeness` | `COMPLETE`, `INCOMPLETE` |
| `price_benchmark` | `REGULATORY_HPP` |
| `extrapolation` | `IN_DOMAIN`, `OUT_OF_DOMAIN` |

## 15. Status Tags

Only these scientific/provenance tags are canonical:

- `local-calibrated`
- `local-estimate`
- `literature-uncalibrated`
- `system-design`
- `regulatory-locked`
- `mixed`

Do not invent replacement tags such as `local-validated`, `local-empirical-reference`, `hardware-locked`, or `system-neutral-SoT` in R2 metadata.

## 16. Reference Codes

Internal sources:

- `I1` — `data_collection_padi_bebek_FINAL.xlsx`.
- `I2` — `Dokumentasi Expert DSS Padi-Bebek.docx`.
- `I3` — domain-wide model DOCX (format/provenance reference).
- `I4` — legacy economic model DOCX (audit target).
- `I5` — internal Scopus reference workbook; fallback only.

External/official sources to preserve in the implementation reference registry:

- `R1` Vipriyanti et al. 2021, Bali, IOP Conference Series: Earth and Environmental Science.
- `R2` Nallasamy et al. 2025, Organic Agriculture, India.
- `R3` Alfiansyah et al. 2025, Journal of Water and Land Development, South Sulawesi.
- `R4` Du et al. 2025, Field Crops Research.
- `R5` Qian et al. 2022, Biocontrol Science and Technology.
- `R6` Zhou et al. 2026, Agriculture.
- `R7` Xiong et al. 2014 — historical fallback only; non-executable unless a separately justified formula is approved.
- `O1` Inpres No.4/2026 — HPP GKP Rp6,500/kg.
- `O2` Kepmentan No.1117/2025 — HET Urea/NPK.
- `O3` official Urea specification 46% N.
- `O4` official NPK Phonska 15-10-12 registration/specification.
- `O5` official historical documentation of 15-15-15 Phonska used to reconstruct the 2021 baseline context.

## 17. Non-Executable Registry Requirement

Any formula marked unresolved in `04_R2_PARAMETER_EXECUTION_REGISTRY.md` must remain representable in documentation/metadata but **must not be imported by production engine code**.

Runtime code should fail closed:

- if a required lookup is missing -> return `UNAVAILABLE` with `null` numeric fields;
- never fall back to a historical constant merely to keep a chart or total populated.
