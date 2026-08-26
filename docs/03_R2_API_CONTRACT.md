# R2 API Contract

> **Scope:** production DSS endpoints under `/api/v1/dss`  
> **Contract generation:** R2  
> **Breaking semantic change:** yes. Do not preserve wrong fields solely for backward compatibility.

## 1. Design Principles

1. Exactly seven user concepts; purchase price is optional.
2. Unknown scientific values are represented as `null` plus an explicit availability/status field.
3. Missing is not zero.
4. Terminal duck value is not realized sale revenue.
5. Full profit is not emitted numerically while cost completeness is incomplete.
6. Every response contains enough model metadata to identify the R2 semantics used.
7. Historical persistence version and runtime model version are distinct concepts.

## 2. `GET /api/v1/dss/options`

### Purpose

Return valid categorical choices and their **operational metadata**, not unsupported yield multipliers.

### Proposed response

```json
{
  "model_version": "R2",
  "rice_varieties": [
    {
      "code": "sertani",
      "label": "Sertani / Seratih",
      "harvest_hst_min": 100,
      "harvest_hst_max": 110,
      "calendar_status": "local-estimate",
      "yield_lookup_status": "ACTIVE_RANGE"
    },
    {
      "code": "inpari",
      "label": "Inpari",
      "harvest_hst_min": 90,
      "harvest_hst_max": 100,
      "calendar_status": "local-estimate",
      "yield_lookup_status": "ACTIVE_RANGE"
    }
  ],
  "planting_systems": [
    {
      "code": "jajar_legowo",
      "label": "Jajar Legowo",
      "supported_density_min_are": 2.0,
      "supported_density_max_are": 4.0,
      "status": "local-estimate"
    },
    {
      "code": "tegel",
      "label": "Tegel",
      "supported_density_min_are": 2.0,
      "supported_density_max_are": 3.0,
      "status": "local-estimate"
    }
  ],
  "purchase_price": {
    "optional": true,
    "default_rp_per_duck": 26500,
    "local_range_rp_per_duck": [25000, 28000],
    "status": "mixed"
  }
}
```

Do not expose `F_sys`, `Y_base=47.8767507`, `p_duck_sell=52500`, feed=20000, KCl price 9500, or legacy calendar fields from this endpoint.

## 3. `POST /api/v1/dss/simulate`

### 3.1 Request schema

Canonical field names should follow current `master` where semantically compatible to reduce frontend churn:

```json
{
  "land_area_are": 7,
  "duck_count": 28,
  "planting_date": "2026-06-01",
  "planting_system": "jajar_legowo",
  "rice_variety": "sertani",
  "duck_age_days": 30,
  "p_duck_buy": null
}
```

Rules:

| Field | Type | Required | Validation |
|---|---|---:|---|
| `land_area_are` | finite float | yes | `>0` |
| `duck_count` | integer | yes | `>0` |
| `planting_date` | ISO date | yes | valid field-transplanting date for transplanted rice; HST is counted from transplanting (`system-design` / validation assumption) |
| `planting_system` | string | yes | lookup value |
| `rice_variety` | string | yes | lookup value |
| `duck_age_days` | integer | yes | `>0` |
| `p_duck_buy` | finite float/null | **no** | if supplied, `>0`; missing/null means use Rp26,500 default |

### 3.2 Purchase price semantics

The following are equivalent:

```json
{}
```

for the optional field and:

```json
{"p_duck_buy": null}
```

Both resolve to:

```text
p_duck_buy_eff = 26,500
purchase_price_source = "LOCAL_DEFAULT_MIDPOINT"
```

A numeric `0` must **not** mean “no purchase this cycle.” That meaning was introduced by the wrong current-master model and is not part of R2.

Recommended validation:

```text
p_duck_buy: float | None = Field(default=None, gt=0, allow_inf_nan=False)
```

## 4. Canonical Simulation Response

Use nested semantic groups. Do not repeat old flat naming solely to satisfy legacy frontend code.

Yield reason codes are specific and fail-closed: `CULTIVAR_GROUP_UNRESOLVED`,
`Y_BASE_GROUP_LOOKUP_MISSING`, `FRD_REFERENCE_MISSING`,
`AGE_OUTSIDE_SUPPORTED_DOMAIN`, `DENSITY_OUTSIDE_SUPPORTED_DOMAIN`, and
`EVIDENCE_DOMAIN_UNSUPPORTED`. Generic availability semantics remain
`availability=UNAVAILABLE` plus null numeric outputs. No code authorizes
interpolation, extrapolation, nearest-neighbour selection, or a numeric fallback.

```json
{
  "model": {
    "model_version": "R2",
    "history_schema_version": 4,
    "frozen": true,
    "generated_at": "..."
  },
  "input": {
    "land_area_are": 7.0,
    "duck_count": 28,
    "planting_date": "2026-06-01",
    "planting_system": "jajar_legowo",
    "rice_variety": "sertani",
    "duck_age_days": 30,
    "p_duck_buy_manual": null,
    "p_duck_buy_effective": 26500.0,
    "p_duck_buy_source": "LOCAL_DEFAULT_MIDPOINT"
  },
  "operational": {
    "area_m2": 700.0,
    "density_are": 4.0,
    "age_support": "SUPPORTED",
    "density_support": "SUPPORTED",
    "extrapolation": "IN_DOMAIN"
  },
  "calendar": {
    "hst_origin_semantics": "FIELD_TRANSPLANTING_DATE",
    "release_hst_min": 21,
    "release_hst_max": 30,
    "release_date_min": "2026-06-22",
    "release_date_max": "2026-07-01",
    "pull_hst_min": 56,
    "pull_hst_max": 60,
    "pull_date_min": "2026-07-27",
    "pull_date_max": "2026-07-31",
    "active_duration_ref_days": 32,
    "active_duration_support_min_days": 28,
    "active_duration_support_max_days": 40,
    "harvest_hst_min": 100,
    "harvest_hst_max": 110,
    "harvest_date_min": "2026-09-09",
    "harvest_date_max": "2026-09-19"
  },
  "duck": {
    "survival_availability": "AVAILABLE",
    "lambda_eff": 0.9,
    "surviving_ducks": 25,
    "sale_quantity": null,
    "sale_quantity_status": "UNAVAILABLE",
    "terminal_value_ref_rp": 1125000.0,
    "terminal_value_min_rp": 750000.0,
    "terminal_value_max_rp": 1500000.0,
    "terminal_value_is_cash_revenue": false
  },
  "yield": {
    "availability": "AVAILABLE",
    "cultivar_group_code": "SERTANI_GROUP",
    "cultivar_group_resolved": true,
    "baseline_kg_per_are": 44.5,
    "rice_duck_response_factor": 1.028,
    "yield_kg_per_are": 45.746,
    "yield_total_kg": 320.222,
    "yield_baseline_source_id": "YB-SERTANI-SULAEMAN-2022",
    "yield_frd_source_id": "FRD-FENG-2024",
    "reason_codes": []
  },
  "fertilizer_baseline": {
    "availability": "AVAILABLE",
    "nutrient_basis": "N-P2O5-K2O",
    "manure_credit_applied": false,
    "n_need_kg": 8.2327,
    "p2o5_need_kg": 1.9215,
    "k2o_need_kg": 1.9215,
    "q_npk_kg": 19.215,
    "q_urea_kg": 11.631413,
    "cost_npk_rp": 35355.6,
    "cost_urea_rp": 20936.54,
    "cost_total_rp": 56292.14
  },
  "costs": {
    "duck_purchase": {
      "availability": "AVAILABLE",
      "amount_rp": 742000.0
    },
    "feed": {
      "availability": "UNAVAILABLE",
      "amount_rp": null,
      "reason_codes": ["FEED_QUANTITY_LOOKUP_MISSING", "FEED_PRICE_LOOKUP_MISSING"]
    },
    "net_infrastructure": {
      "availability": "AVAILABLE_RANGE",
      "equivalent_perimeter_m": 105.830052,
      "cost_min_rp_per_cycle": 211660.10,
      "cost_ref_rp_per_cycle": 285741.14,
      "cost_max_rp_per_cycle": 357176.43,
      "geometry_assumption": "SQUARE_EQUIVALENT"
    },
    "cage": {
      "availability": "PARTIAL_RANGE_ONLY",
      "cost_per_unit_min_rp_per_cycle": 150000.0,
      "cost_per_unit_ref_rp_per_cycle": 175000.0,
      "cost_per_unit_max_rp_per_cycle": 200000.0,
      "total_amount_rp": null,
      "reason_codes": ["CAGE_CAPACITY_RULE_MISSING"]
    },
    "weeding": {
      "availability": "BASELINE_RANGE_ONLY",
      "baseline_min_rp": 42000.0,
      "baseline_max_rp": 266000.0,
      "saving_rp": null
    },
    "pesticide": {
      "effect": "CONTEXT_SPECIFIC",
      "saving_rp": null
    },
    "cost_core_direct_rp": 1027741.14,
    "cost_total_available_rp": 1084033.28,
    "cost_completeness": "INCOMPLETE"
  },
  "economics": {
    "paddy_price_benchmark_rp_per_kg": 6500.0,
    "paddy_price_semantics": "REGULATORY_HPP",
    "paddy_revenue_rp": 2081443.0,
    "cash_revenue_rp": 2081443.0,
    "gross_economic_value_rp": 3206443.0,
    "margin_core_rp": 2178701.86,
    "profit_full_est_rp": null,
    "profit_full_status": "UNAVAILABLE_INCOMPLETE_COST"
  },
  "reliability": {
    "yield_availability": "AVAILABLE",
    "survival_availability": "AVAILABLE",
    "feed_cost_availability": "UNAVAILABLE",
    "cost_completeness": "INCOMPLETE",
    "extrapolation": "IN_DOMAIN"
  },
  "warnings": [
    "YIELD_EVIDENCE_WARNING: LOW_EVIDENCE_TWO_LOCATION_EXTERNAL_RANGE",
    "Feed cost is unavailable; full profit is not computed."
  ],
  "trace": {
    "active_formula_ids": ["R2-NORM-01", "R2-DEN-01", "R2-AGE-01", "R2-CAL-01", "R2-CAL-03", "R2-SURV-02", "R2-NUT-01", "R2-INF-01", "R2-COST-01"],
    "conditional_formula_ids": ["R2-SURV-01", "R2-SURV-03", "R2-DUCKVAL-01"],
    "disabled_legacy_formula_ids": ["LEG-RAGE", "LEG-LAMBDA-078125", "LEG-Y0-478767507"]
  }
}
```

The numeric values above are **contract-shape examples** for deterministic active formulas; they are not a golden prediction of full R2 yield/profit.

## 5. HTTP Error Semantics

Continue current envelope:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed.",
    "field": null,
    "issues": []
  }
}
```

Recommended status use:

- `400` — malformed/invalid numeric/date input.
- `401` — auth failure.
- `404` — history not found.
- `409` — registration conflict.
- `422` — categorical reference not found.

**Scientific unavailability is normally HTTP 200**, because the simulation may still validly return partial outputs and explicit availability flags.

## 6. `POST /api/v1/dss/visualize`

The endpoint may remain POST because financial/contextual series depend on the simulation request.

The endpoint is a presentation-only view over
`simulate(request, user_id=None)`: it performs no separate scientific or
economic calculation and never persists history, even when the HTTP request
includes a bearer token.

### Required visualization series

- a complete positive-input density partition for the selected planting system,
  including supported, limited-test, high-risk, and extrapolation intervals;
- a complete age partition with caution, supported, and outside-local-range
  intervals;
- exactly one interval marked `selected_value_in_zone=true` in each partition;
- the exact calendar object returned by the canonical simulation;
- one request-area infrastructure range labeled
  `CALCULATED_REQUEST_RANGE`;
- NPK and urea fertilizer components labeled `BASELINE-NO-CREDIT`;
- a yield series whose `points` stay empty while yield is unavailable and whose
  availability/reason codes match the simulation;
- a partial financial waterfall that keeps terminal duck value as a non-cash
  asset node, keeps unavailable amounts null, labels the available-cost
  subtotal as partial, and leaves full profit unavailable while the ledger is
  incomplete.

### Forbidden visualization series

- `F_density_bio` custom curve;
- `R_age` curve;
- 0.78125 survival curve;
- 100%/60% survival step curve;
- fixed `47.8767507` yield line/benchmark;
- a waterfall that treats `V_duck_end` as realized revenue;
- a waterfall that calculates full profit while feed/cage/etc. are unavailable.

Canonical top-level response:

```json
{
  "model": {"model_version": "R2"},
  "selected_input": {"density_are": 4.0},
  "density_zones": [...],
  "age_zones": [...],
  "calendar": {...},
  "infrastructure": {
    "availability": "AVAILABLE_RANGE",
    "series_semantics": "CALCULATED_REQUEST_RANGE"
  },
  "fertilizer": {
    "availability": "AVAILABLE",
    "baseline_label": "BASELINE-NO-CREDIT",
    "components": [...]
  },
  "yield_series": {
    "availability": "AVAILABLE",
    "points": [],
    "reason_codes": [],
    "yield_ref_kg_per_are": 45.746,
    "yield_low_kg_per_are": 22.9244,
    "yield_high_kg_per_are": 68.5676,
    "yield_range_type": "LITERATURE_EVIDENCE_ENVELOPE"
  },
  "financial_waterfall": {
    "availability": "PARTIAL",
    "cost_completeness": "INCOMPLETE",
    "nodes": [...]
  },
  "warnings": [...]
}
```

Support interval endpoints include explicit `min_inclusive` and
`max_inclusive` flags; an omitted bound is serialized as null. Financial nodes
use the kinds `CASH_REVENUE`, `ASSET_VALUE`, `COST`,
`AVAILABLE_COST_SUBTOTAL`, and `FULL_PROFIT`, each with an availability flag,
nullable `amount_rp`, and `affects_cash_total` semantics.

Trace semantics are actual-execution semantics: `active_formula_ids` contains
rules evaluated for this request (including only the selected variety calendar
branch), while `conditional_formula_ids` contains only conditional branches
that produced their governed value. Pending or unavailable yield/revenue/full-
profit branches are not advertised as executed.

## 7. History Endpoints

Keep routes:

- `GET /api/v1/dss/histories`
- `GET /api/v1/dss/histories/{id}`
- `DELETE /api/v1/dss/histories/{id}`

New authenticated simulations persist as schema v4. History detail must return the semantic snapshot saved at simulation time, not recompute it with future parameter versions.

## 8. Compatibility Policy

Do not put R2 values into old field names when their semantics differ.

Examples that should be removed from the R2 canonical response:

- `Net_Cash_Contribution_DSS`
- `Profit_net_cash`
- `Revenue_duck_potential`
- `Revenue_duck`
- `Cost_feed` if it implies a numeric fixed-cost estimate
- `HST_in/HST_out` point semantics
- `D_in/D_out` point semantics
- `Yield_are_pred=47.8767507`

If frontend migration needs temporary aliases, place them behind an explicitly temporary compatibility adapter and never persist them as v4 canonical semantics.

## 9. Current Phase-6 Yield Contract

The seven-input request is unchanged. The active runtime uses registry
`R2-2026-08-26.3` and final corrected freeze `R2-FREEZE-2026-08-26.5`.

For a request that passes the full Phase-6 supported-domain gate, `yield` must
contain the following exact semantic representation:

```json
{
  "availability": "AVAILABLE",
  "cultivar_group_code": "INPARI_GROUP",
  "baseline_ref_kg_per_are": 53.5,
  "baseline_low_kg_per_are": 20.0,
  "baseline_high_kg_per_are": 78.4,
  "rice_duck_response_factor": 1.028,
  "yield_ref_kg_per_are": 54.998,
  "yield_low_kg_per_are": 20.56,
  "yield_high_kg_per_are": 80.5952,
  "yield_total_ref_kg": 384.986,
  "yield_total_low_kg": 143.92,
  "yield_total_high_kg": 564.1664,
  "yield_range_type": "LITERATURE_EVIDENCE_ENVELOPE",
  "yield_evidence_status": "LITERATURE_UNCALIBRATED",
  "yield_evidence_strength": "EXTERNAL_FIELD_DISTRIBUTION_N43",
  "yield_evidence_warning": null,
  "yield_baseline_source_id": "YB-INPARI-SULAEMAN-2024",
  "yield_frd_source_id": "FRD-FENG-2024",
  "yield_kg_per_are": 54.998,
  "yield_total_kg": 384.986,
  "reason_codes": []
}
```

The unsuffixed `yield_kg_per_are` and `yield_total_kg` fields are retained as
backward-compatible aliases of `*_ref`, not standalone exact claims. New
clients must consume the explicit reference, low/high, range-type, and evidence
metadata together. For `SERTANI_GROUP`, set
`yield_evidence_strength="LOW_EVIDENCE_TWO_LOCATION_EXTERNAL_RANGE"` and
return that same value in `yield_evidence_warning`.

`yield_range_type` must never be serialized or described as a confidence,
prediction, credible, or probabilistic uncertainty interval. No client input
is added. Availability and execution state are separate: the registry uses
`ACTIVE_RANGE` for range-aware execution, whereas the response uses
`availability=AVAILABLE` only after the full gate succeeds.

For an unsupported request, all ref/low/high and alias numerics are `null`,
`availability=UNAVAILABLE`, and reason codes report the first applicable
canonical cause(s): `CULTIVAR_GROUP_UNRESOLVED`,
`Y_BASE_GROUP_LOOKUP_MISSING`, `AGE_OUTSIDE_SUPPORTED_DOMAIN`,
`DENSITY_OUTSIDE_SUPPORTED_DOMAIN`, `FRD_REFERENCE_MISSING`, or
`EVIDENCE_DOMAIN_UNSUPPORTED`. `LIMITED_TEST`, `HIGH_RISK`,
`EXTRAPOLATION`, `CAUTION`, and `OUTSIDE_LOCAL_RANGE` never receive a range.

### 9.1 Economics and visualization propagation

When yield is available, return `paddy_revenue_ref_rp`,
`paddy_revenue_low_rp`, `paddy_revenue_high_rp`; the corresponding
`cash_revenue_*`, `gross_economic_value_*`, and `margin_core_*` fields; and
their existing unsuffixed fields as `*_ref` aliases. A low/high yield envelope
must not collapse silently into a single economic figure. `cost_total_available`
is active as a partial subtotal; `profit_full_est_rp` remains null with
`UNAVAILABLE_INCOMPLETE_COST` because feed and total cage cost remain unknown.
Terminal duck value remains an asset, not cash revenue.

Visualization is a projection of the canonical simulation response. Its yield
series must expose the selected request's reference and envelope (or an empty
unavailable series) and preserve the same metadata/reason codes. It must not
plot interpolated density/release curves or call the envelope an interval of
statistical confidence.
