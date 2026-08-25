# R2 Legacy Invalidation Register

> **Purpose:** anti-regression blacklist.  
> Presence in historical docs/comments is allowed only when explicitly labeled legacy/non-executable.  
> Presence in production calculation path is a release blocker.

## 1. Invalidated from `78f46e...`

| Signature | Legacy meaning | R2 disposition |
|---|---|---|
| `R_age` | age risk ratio 0.35/0.15/0.05 | forbidden runtime |
| `P_over` | linear over-density penalty | forbidden runtime |
| `P_under` | linear under-density penalty | forbidden runtime |
| `0.78125` | survival ceiling from recap sold/initial | forbidden runtime |
| `0.50 * R_age` | survival penalty | forbidden runtime |
| `0.45 * P_over` | survival penalty | forbidden runtime |
| `F_density_bio` | custom yield response | forbidden runtime |
| `alpha_bio = 0.15` | custom yield coefficient | forbidden runtime |
| `beta_tramp = 0.25` | custom yield coefficient | forbidden runtime |
| `F_age` / `0.08` age yield penalty | invented age-yield multiplier | forbidden runtime |
| `F_sys=1.211` | Tegel yield multiplier from clean recap | forbidden runtime |
| `Y0=47.8767507` | recap-calibrated yield baseline | forbidden runtime |
| `max(0,0.02*t-0.6)` | manure time credit | forbidden runtime |
| `0.93*(1-exp(-0.35*d))` | weed curve | forbidden runtime |
| `0.80*(1-exp(-0.35*d))` | pest curve | forbidden runtime |
| `J*4500*(1+0.75*P_over+0.50*R_age)` | feed cost | forbidden runtime |
| `0.5*289260*sqrt(A)` | net cost regression | forbidden runtime |
| flat total cage `175000` | total cage cost | forbidden as total; per-unit reference only |
| `p_gabah=6000` | old paddy price | replaced by regulatory benchmark 6500 |
| `p_duck_sell=35000` | automatic duck revenue | forbidden sale assumption |
| `Profit_net_cash` | incomplete ledger overclaim | forbidden canonical R2 output |

## 2. Invalidated from Current Master

Current master removed several older formulas but introduced another invalid model. The following are also banned:

| Signature | Current-master meaning | R2 disposition |
|---|---|---|
| `HST_IN = 21` as exact release point | fixed duck entry | replace by release window 21–30 |
| `HST_OUT = 65` | fixed pull point | replace by 56–60 window |
| `T_ACTIVE = 44` | fixed duration | replace by ref 32, support 28–40 |
| Inpari `109,116` | harvest window | replace by 90–100 |
| `Y_BASE = 47.8767507` | fixed yield | forbidden fallback |
| `N_survive=J` if `d<=8` | 100% survival | forbidden |
| `floor(0.60*J)` if `d>8` | overload survival | forbidden |
| `P_GABAH_RP_PER_KG=6000` | paddy price | replace 6500 official benchmark |
| `P_DUCK_SELL_RP_PER_DUCK=52500` | duck sale/potential revenue | forbidden automatic sale semantics |
| `C_FEED_RP_PER_DUCK_CYCLE=20000` | fixed feed cost | unavailable until sourced lookup |
| `Revenue_duck_potential` | survivor monetized as sale | forbidden |
| `Total_Revenue_DSS` | paddy + duck potential | forbidden canonical R2 aggregate |
| `Net_Cash_Contribution_DSS` | current-master main output | forbidden canonical R2 aggregate |
| `Pesticide_reduction_upper_bound=0.80` as runtime field | universal pest effect | descriptive context only, not scalar output |
| weeding `21000*(1-0.77)` | monetary saving | forbidden until monetary conversion supported |
| `HET_kcl=9500` | treated as regulatory locked | unresolved; KCl excluded |
| manure function in sandbox | still executable despite “sandbox” | forbidden: unresolved formula must not execute even in sandbox |

## 3. Invalid Status/Provenance Labels

Do not use these as R2 canonical status tags:

- `local-validated`
- `local-calculated`
- `local-empirical-reference`
- `locked`
- `hardware-locked`
- `system-neutral-SoT`
- `estimation`
- `partial`

Use only:

- `local-calibrated`
- `local-estimate`
- `literature-uncalibrated`
- `system-design`
- `regulatory-locked`
- `mixed`

Execution state is separate from provenance status.

## 4. Invalid Historical Validation Practices

The following are forbidden in R2 validation:

1. calculating Y baseline from the 36 clean recap;
2. LOFO-CV that recomputes median yield from recap and calls that R2 validation;
3. choosing system-neutral vs system-specific formula by whichever has lower error on the comparator and then treating it as independent validation;
4. treating `duck_age_days=21` imputation as observed ground truth;
5. treating `N_sold` or duck sale revenue as survival ground truth;
6. treating missing/blank cost as actual zero;
7. comparing old farmer profit directly to R2 full profit;
8. post-hoc coefficient tuning on the same 36-cycle comparator;
9. preserving historical MAE as a test constant for R2.

## 5. Grep/Static Anti-Regression Checks

Agent should add a test or CI script that searches **production paths** (`app/`) for banned scientific constants/identifiers.

Suggested checks:

```text
R_age
P_over
P_under
F_density_bio
alpha_bio
beta_tramp
0.78125
289260
Revenue_duck_potential
Net_Cash_Contribution_DSS
```

Constants such as `47.8767507`, `52500`, `20000`, `109`, `116`, `65`, `44`, `9500` require context-aware review because an isolated number can occur legitimately elsewhere. Prefer named-constant/static-AST checks over naive raw-text grep for common numbers.

Historical/archive docs are excluded from the production-code static rule only if they are clearly marked legacy.

## 6. Import Boundary Rule

Production modules must not import legacy formula implementations.

Recommended layout:

```text
app/engines/r2/
  normalization.py
  support.py
  calendar.py
  survival.py
  yield_engine.py
  fertilizer.py
  infrastructure.py
  economics.py

app/legacy/   # optional audit-only package; never imported by app/api or app/services/r2
```

If legacy code remains in repository for history, add an import-boundary test proving no module reachable from `/dss/simulate` imports it.

## 7. Release Blocker Definition

A release is blocked if any of the following is true:

- banned formula influences a production response;
- a `PENDING_LOOKUP` value silently falls back to legacy constant;
- unknown output is serialized as numeric zero without explicit observed-zero evidence;
- R2 history writes into v3 semantic schema;
- visualization displays a fabricated continuous biological curve;
- full profit is numeric while cost completeness is incomplete;
- historical replay data is used to modify an R2 parameter.

