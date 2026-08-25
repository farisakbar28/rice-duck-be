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
      "yield_lookup_status": "PENDING_LOOKUP"
    },
    {
      "code": "inpari",
      "label": "Inpari",
      "harvest_hst_min": 90,
      "harvest_hst_max": 100,
      "calendar_status": "local-estimate",
      "yield_lookup_status": "PENDING_LOOKUP"
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
| `planting_date` | ISO date | yes | valid date |
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
    "availability": "UNAVAILABLE",
    "exact_cultivar_resolved": false,
    "baseline_kg_per_are": null,
    "rice_duck_response_factor": null,
    "yield_kg_per_are": null,
    "yield_total_kg": null,
    "reason_codes": ["Y_BASE_LOOKUP_MISSING", "F_RD_LOOKUP_MISSING"]
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
    "paddy_revenue_rp": null,
    "cash_revenue_rp": null,
    "gross_economic_value_rp": null,
    "margin_core_rp": null,
    "profit_full_est_rp": null,
    "profit_full_status": "UNAVAILABLE_INCOMPLETE_COST"
  },
  "reliability": {
    "yield_availability": "UNAVAILABLE",
    "survival_availability": "AVAILABLE",
    "feed_cost_availability": "UNAVAILABLE",
    "cost_completeness": "INCOMPLETE",
    "extrapolation": "IN_DOMAIN"
  },
  "warnings": [
    "Yield numeric output is unavailable until exact-cultivar and F_RD lookups are configured.",
    "Feed cost is unavailable; full profit is not computed."
  ],
  "trace": {
    "active_formula_ids": ["R2-A1", "R2-D1", "R2-CAL1", "R2-S1", "R2-FERT1", "R2-INF1", "R2-COST1"],
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

### Allowed visualization series

- density **support zones**; not a continuous biological yield multiplier;
- age **support zones**; not a vulnerability probability curve;
- calendar windows;
- infrastructure cost range vs area, because that formula is active;
- fertilizer baseline breakdown, because it is active;
- financial available-components waterfall that clearly marks unavailable nodes;
- yield curve **only after** `F_RD_lookup` is available and the plotted domain is explicitly the literature-supported domain.

### Forbidden visualization series

- `F_density_bio` custom curve;
- `R_age` curve;
- 0.78125 survival curve;
- 100%/60% survival step curve;
- fixed `47.8767507` yield line/benchmark;
- a waterfall that treats `V_duck_end` as realized revenue;
- a waterfall that calculates full profit while feed/cage/etc. are unavailable.

Suggested response:

```json
{
  "model_version": "R2",
  "density_zones": [...],
  "age_zones": [...],
  "calendar": {...},
  "available_cost_series": {...},
  "yield_series": {
    "availability": "UNAVAILABLE",
    "points": []
  },
  "financial_waterfall": {
    "availability": "PARTIAL",
    "nodes": [...],
    "excluded_unavailable_components": ["feed", "cage_total", "full_profit"]
  }
}
```

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

