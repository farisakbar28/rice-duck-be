# R2 Parameter and Execution Registry

> **Purpose:** machine-implementation companion to `01_R2_MODEL_SSOT.md`.  
> A formula/parameter may exist in documentation without being executable.  
> Production code must check `execution_state` before using a numeric value.

## 1. Canonical Execution States

| State | Meaning |
|---|---|
| `ACTIVE` | Deterministic runtime formula/value may execute. |
| `ACTIVE_RANGE` | Runtime may calculate a range/reference but must preserve range semantics. |
| `ACTIVE_BASELINE` | Valid baseline calculation; does not claim a duck-induced saving/credit. |
| `CONDITIONAL` | Numeric result only when explicitly listed availability conditions are met. |
| `PENDING_LOOKUP` | Structural formula accepted; required sourced lookup is not yet populated. |
| `UNAVAILABLE` | No numeric runtime output allowed under current evidence. |
| `DESCRIPTIVE` | Qualitative/context output only. |
| `NON_EXECUTABLE_LEGACY` | Historical formula retained for audit; forbidden from runtime. |

## 2. Active Formula Registry

| ID | Component | Formula / rule | Status tag | Execution state | Provenance |
|---|---|---|---|---|---|
| `R2-NORM-01` | Area conversion | `A_m2 = 100*A_are` | `system-design` | `ACTIVE` | unit conversion |
| `R2-DEN-01` | Density | `d = J/A_are` | `system-design` | `ACTIVE` | deterministic |
| `R2-PRICE-01` | Duck buy effective price | manual if supplied else `26,500` | `mixed` | `ACTIVE` | local 25–28k + midpoint design |
| `R2-CAL-01` | Sertani harvest | `[100,110] HST` | `local-estimate` | `ACTIVE_RANGE` | local data collection |
| `R2-CAL-02` | Inpari harvest | `[90,100] HST` | `local-estimate` | `ACTIVE_RANGE` | local data collection |
| `R2-CAL-03` | Release | `[21,30] HST` | `local-estimate` | `ACTIVE_RANGE` | local data collection |
| `R2-CAL-04` | Pull/heading | `[56,60] HST` | `local-estimate` | `ACTIVE_RANGE` | local data collection |
| `R2-CAL-05` | Active duration reference | `32`, support `[28,40]` days | `local-estimate` | `ACTIVE_RANGE` | local data collection |
| `R2-AGE-01` | Age support | `<21 CAUTION; 21–30 SUPPORTED; >30 OUTSIDE_LOCAL_RANGE` | `mixed` | `ACTIVE` | local boundary + system labels |
| `R2-DEN-02` | Density support | Jarwo 2–4; Tegel 2–3; ~5–6 limited; ~>=8 high-risk | `mixed` | `ACTIVE` | local/expert boundary + system classification |
| `R2-SURV-01` | Safe survival ref | `lambda_safe_ref=0.90` | `local-estimate` | `CONDITIONAL` | expert safe-context estimate |
| `R2-SURV-02` | Survival availability | 0.90 only if age+density both supported; else unavailable | `mixed` | `ACTIVE` gate | confirmed R2 design |
| `R2-SURV-03` | Surviving ducks | `floor(J*lambda_eff)` | `system-design` | `CONDITIONAL` | deterministic once lambda available |
| `R2-YLD-01` | Yield structure | `Y_base(V_exact)*F_RD_lookup(d,release=30)` | `mixed` | `PENDING_LOOKUP` | accepted structure; lookups missing |
| `R2-YLD-02` | Total yield | `Yield_are*A_are` | `system-design` | `CONDITIONAL` | requires `R2-YLD-01` available |
| `R2-NUT-01` | N baseline | `1.1761*A_are` kg N | `literature-uncalibrated` | `ACTIVE_BASELINE` | Bali RDIS baseline reconstruction |
| `R2-NUT-02` | P2O5 baseline | `0.2745*A_are` kg | `literature-uncalibrated` | `ACTIVE_BASELINE` | same |
| `R2-NUT-03` | K2O baseline | `0.2745*A_are` kg | `literature-uncalibrated` | `ACTIVE_BASELINE` | same |
| `R2-NUT-04` | Manure-credit gate | `N_net=N_need; P2O5_net=P2O5_need; K2O_net=K2O_need` | `mixed` | `ACTIVE_BASELINE` | no supported manure temporal credit |
| `R2-FERT-01` | NPK quantity | `max(P2O5/0.10,K2O/0.12)` | `mixed` | `ACTIVE_BASELINE` | official current NPK composition + optimization design |
| `R2-FERT-02` | Urea quantity | `max(0,(N-0.15*Q_npk)/0.46)` | `mixed` | `ACTIVE_BASELINE` | official product composition |
| `R2-FERT-03` | Fertilizer cost | `1800*Q_urea+1840*Q_npk` | `mixed` | `ACTIVE_BASELINE` | official HET |
| `R2-COST-01` | Duck purchase | `J*p_duck_buy_eff` | `mixed` | `ACTIVE` | user/default price |
| `R2-INF-01` | Equivalent net length | `4*sqrt(100*A_are)` | `mixed` | `ACTIVE_RANGE` | system geometry + local unit cost |
| `R2-INF-02` | Net cycle min | `L*6000/3` | `mixed` | `ACTIVE_RANGE` | local range |
| `R2-INF-03` | Net cycle max | `L*6750/2` | `mixed` | `ACTIVE_RANGE` | local range |
| `R2-INF-04` | Net cycle ref | `L*6750/2.5` | `mixed` | `ACTIVE_RANGE` | conservative/ref design |
| `R2-CAGE-01` | Cage per-unit cycle range | 150k–200k; ref 175k | `local-estimate` | `ACTIVE_RANGE` | local cost/lifetime |
| `R2-WEED-01` | Weeding baseline | `A_are*[6000,38000]` | `local-estimate` | `ACTIVE_RANGE` | local cost range |
| `R2-GRAIN-01` | Paddy HPP benchmark | `6500 Rp/kg` | `regulatory-locked` | `ACTIVE` | Inpres 4/2026 |
| `R2-GRAIN-02` | Paddy revenue benchmark | `Yield_total*6500` | `mixed` | `CONDITIONAL` | requires yield |
| `R2-DUCKVAL-01` | Terminal duck value | `N_survive*45000`, sensitivity 30–60k | `local-estimate` | `CONDITIONAL` | local + expert price evidence |
| `R2-LEDGER-01` | Cash revenue | `Revenue_gabah` | `system-design` | `CONDITIONAL` | no automatic duck sale |
| `R2-LEDGER-02` | Gross economic value | `Revenue_gabah+V_duck_end` | `system-design` | `CONDITIONAL` | yield+survival needed |
| `R2-LEDGER-03` | Core direct cost | `C_duck_buy+C_net_cycle_ref` | `mixed` | `ACTIVE` | confirmed R2 definition |
| `R2-LEDGER-04` | Available cost total | sum only components with available numeric values | `mixed` | `ACTIVE` | availability-aware aggregation |
| `R2-LEDGER-05` | Margin core | `GrossEconomicValue-Cost_core_direct` | `mixed` | `CONDITIONAL` | yield+survival needed |
| `R2-LEDGER-06` | Full profit | `GrossEconomicValue-Cost_full_est` | `mixed` | `CONDITIONAL` | only if completeness COMPLETE |

## 3. Pending / Unavailable Registry

| ID | Component | Structural rule | Current state | Why numeric runtime is blocked |
|---|---|---|---|---|
| `R2-YLD-LKP-BASE` | Exact-cultivar baseline | `Y_base(V_exact)` | `PENDING_LOOKUP` | no approved exact-cultivar table configured |
| `R2-YLD-LKP-RD` | Rice-duck response | `F_RD_lookup(d, release)` | `PENDING_LOOKUP` | literature treatment table not yet encoded/approved |
| `R2-FEED-01` | Feed cost | `sum N_t*q_feed*p_feed` | `UNAVAILABLE` | valid quantity + price lookup incomplete |
| `R2-CAGE-02` | Total cage cost | `N_units*C_cage_unit_cycle` | `UNAVAILABLE` | cage capacity/unit-count rule absent |
| `R2-WEED-02` | Weeding savings | baseline-to-saving function | `UNAVAILABLE` | biological suppression != monetary saving |
| `R2-PEST-01` | Pest effect | context-specific | `DESCRIPTIVE` | evidence heterogeneous across pest guilds |
| `R2-PEST-02` | Pesticide saving | monetary conversion | `UNAVAILABLE` | no valid baseline/function |
| `R2-MANURE-01` | Manure nutrient credit | time/density-dependent credit | `UNAVAILABLE` | old linear temporal transform unsupported |
| `R2-KCL-01` | KCl price/product branch | price×quantity | `UNAVAILABLE` | exact valid official/Scopus price unresolved |
| `R2-PROFIT-01` | Full profit | full ledger | `UNAVAILABLE` until complete | feed/cage/etc. incomplete |

## 4. Legacy Non-Executable Formula Registry

These must remain documented for audit but must not be callable from production engine code.

| Legacy ID | Formula/value | Why invalid |
|---|---|---|
| `LEG-RAGE` | `R_age=0.35/0.15/0.05` | qualitative-to-numeric invention |
| `LEG-POVER` | `(d-Ksafe)/(8-Ksafe)` | unsupported linear penalty |
| `LEG-PUNDER` | `(2-d)/2` | unsupported under-density penalty |
| `LEG-LAMBDA-078125` | `0.78125*(1-.50R_age)*(1-.45P_over)` | recap-derived ceiling + invented multipliers |
| `LEG-SURV-FULL60` | `J if d<=8 else floor(.60J)` | current-master assumption, not R2 evidence |
| `LEG-Y0-478767507` | `47.8767507 kg/are` | historical recap calibration |
| `LEG-FDENSITY` | custom exponential/quadratic density curve | invented coefficients/form |
| `LEG-FAGE` | `1-.08R_age` | unsupported coefficient |
| `LEG-FSYS-1211` | Tegel `1.211` | clean-recap derived ratio |
| `LEG-FVAR-1` | universal variety multiplier 1 | unsupported equality assumption |
| `LEG-MANURE-T` | `max(0,.02*t-.6)` | unsupported linearization |
| `LEG-WEED-CURVE` | `.93*(1-exp(-.35d))` | exact curve not sourced |
| `LEG-PEST-CURVE` | `.80*(1-exp(-.35d))` | exact/universal effect unsupported |
| `LEG-FEED-4500` | `J*4500*(1+.75P_over+.50R_age)` | recap base + invented modifiers |
| `LEG-FEED-20000` | `J*20000` | current-master shortcut; insufficient standardization |
| `LEG-INFRA-289260` | `.5*289260*sqrt(A)` | recap regression |
| `LEG-CAGE-FLAT175` | flat total 175k/cycle | per-unit cost misused as total |
| `LEG-KCL-9500` | KCl price 9500/kg | exact price source unresolved |
| `LEG-GABAH-6000` | paddy price 6000/kg | replaced by official R2 benchmark 6500 |
| `LEG-DUCKSELL-35000` | duck cash revenue at 35k | sale state invalid + price issue |
| `LEG-DUCKSELL-52500` | duck potential cash revenue at 52.5k | current-master inference, not R2 |

## 5. Metadata Object Contract

For configurable parameters, backend should be able to expose/store metadata resembling:

```json
{
  "key": "p_duck_buy_default",
  "value": 26500,
  "unit": "Rp/duck",
  "status_tag": "mixed",
  "execution_state": "ACTIVE",
  "source_ids": ["I1"],
  "model_version": "R2",
  "effective_from": "2026-08-26",
  "note": "Midpoint of local 25k–28k range; used only when user value missing/null."
}
```

Do not store scientific status using current-master ad-hoc labels such as `local-validated`, `local-empirical-reference`, or `locked`.

## 6. Fail-Closed Rules

1. Missing `Y_base` -> yield null; never Y0 fallback.
2. Missing `F_RD_lookup` -> yield null.
3. Missing feed lookup -> feed cost null.
4. Missing cage capacity -> cage total null.
5. Missing KCl price -> exclude KCl branch from active product set; do not use 9500.
6. Out-of-domain survival -> lambda/N_survive null; do not use 60% penalty.
7. Incomplete cost ledger -> full profit null.
8. Unknown value in aggregation -> exclude only if metric is explicitly named `available`/partial; never coerce unknown to zero.

