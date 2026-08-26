"""Semantically eligible Phase-5C comparators and excluded-row stress runs."""

from __future__ import annotations

import math
import statistics
from datetime import date
from typing import Any

from validation._bootstrap import configure_runtime_env
from validation.metrics import calendar_metrics
from validation.workbook_parser import Reconstruction

configure_runtime_env()

from app.data.seed import (  # noqa: E402
    PARAMETER_REGISTRY,
    PLANTING_SYSTEMS,
    RICE_VARIETIES,
)
from app.engines.r2.calendar import compute_calendar_windows  # noqa: E402
from app.engines.r2.config import R2EngineConfig  # noqa: E402
from validation.runtime_runner import API, make_client  # noqa: E402


def _variety(code: str):
    return next((item for item in RICE_VARIETIES if item.code == code), None)


def build_calendar_comparator(reconstruction: Reconstruction) -> dict[str, Any]:
    config = R2EngineConfig.from_registry(PARAMETER_REGISTRY, PLANTING_SYSTEMS)
    metric_rows: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for row in reconstruction.clean_records:
        planting = row["planting_date_observed"]
        harvest = row["harvest_date_observed"]
        variety = _variety(row["rice_variety"])
        if planting is None or harvest is None:
            excluded.append({
                "source_row": row["source_row"],
                "reason": "BOTH_OBSERVED_DATES_REQUIRED",
            })
            continue
        if variety is None:
            excluded.append({
                "source_row": row["source_row"],
                "reason": "CULTIVAR_GROUP_UNRESOLVED",
            })
            continue
        windows = compute_calendar_windows(planting, variety, config)
        metric_rows.append({
            "source_row": row["source_row"],
            "farmer_cluster_id": row["farmer_cluster_id"],
            "predicted_min": windows.harvest_date_min,
            "predicted_max": windows.harvest_date_max,
            "actual_harvest": harvest,
        })
    metrics = calendar_metrics(metric_rows)
    return {
        "status": "EVALUATED" if metric_rows else "NOT_EVALUABLE",
        "timing_semantics": "HST_FROM_FIELD_TRANSPLANTING",
        "timing_semantics_status": "VALIDATION_ASSUMPTION",
        "eligibility_rule": "observed transplanting/planting date AND observed harvest date",
        "metrics": metrics,
        "excluded_rows": excluded,
    }


def build_purchase_comparator(reconstruction: Reconstruction) -> dict[str, Any]:
    rows = []
    for row in reconstruction.clean_records:
        price = row["duck_purchase_price"]
        provenance = row["input_fields"]["p_duck_buy"]["provenance"]
        if provenance != "OBSERVED" or not isinstance(price, (int, float)) or price <= 0:
            continue
        rows.append({
            "source_row": row["source_row"],
            "farmer_cluster_id": row["farmer_cluster_id"],
            "observed_price_rp_per_duck": float(price),
            "duck_count": row["duck_count"],
            "observed_purchase_cost_rp": float(price) * row["duck_count"],
            "provenance": "OBSERVED_VALUE",
        })
    prices = [row["observed_price_rp_per_duck"] for row in rows]
    return {
        "status": "ELIGIBLE_OBSERVED_POSITIVE_ONLY",
        "effective_n": len(rows),
        "defaulted_rows_excluded": len(reconstruction.clean_records) - len(rows),
        "mean_observed_price_rp_per_duck": statistics.fmean(prices) if prices else None,
        "median_observed_price_rp_per_duck": (
            float(statistics.median(prices)) if prices else None
        ),
        "rows": rows,
    }


def _positive_observed_count(
    reconstruction: Reconstruction, field: str
) -> int:
    return sum(
        1 for row in reconstruction.clean_records
        if isinstance(row[field], (int, float))
        and row[field] > 0
        and row["actual_provenance"].get(field) in {
            "OBSERVED_VALUE", "DERIVED_ACTUAL"
        }
    )


def build_component_comparators(reconstruction: Reconstruction) -> dict[str, Any]:
    return {
        "feed": {
            "status": "NOT_EVALUABLE",
            "runtime_reason": "FEED_LOOKUP_UNAVAILABLE",
            "historical_positive_coverage_n": _positive_observed_count(
                reconstruction, "feed_cost"
            ),
            "metrics": None,
        },
        "survival": {
            "status": "NO_COMPATIBLE_AGGREGATE_GROUND_TRUTH",
            "n_sold_used_as_survival": False,
            "metrics": None,
        },
        "terminal_duck_value": {
            "realized_sale_metric": None,
            "reason": "ASSET_VALUE_IS_NOT_REALIZED_SALE_REVENUE",
        },
        "infrastructure": {
            "semantic_eligibility": "AMBIGUOUS_HISTORICAL_CONSTRUCT",
            "status": "NO_METRIC",
            "net_positive_coverage_n": _positive_observed_count(
                reconstruction, "net_cost"
            ),
            "cage_positive_coverage_n": _positive_observed_count(
                reconstruction, "cage_cost"
            ),
        },
        "weeding": {
            "status": "NO_MONETARY_AGGREGATE",
            "positive_coverage_n": _positive_observed_count(
                reconstruction, "weeding_cost"
            ),
            "metrics": None,
        },
        "pesticide": {
            "status": "SPARSE_CASE_DIAGNOSTICS_ONLY",
            "positive_coverage_n": _positive_observed_count(
                reconstruction, "pesticide_cost"
            ),
            "metrics": None,
        },
        "fertilizer": {
            "status": "DESCRIPTIVE_ONLY",
            "positive_coverage_n": _positive_observed_count(
                reconstruction, "fertilizer_cost"
            ),
            "metrics": None,
        },
        "profit": {
            "legacy_accuracy_metric": None,
            "profit_full": "UNAVAILABLE_INCOMPLETE_COST",
            "margin_core_is_profit": False,
        },
    }


def _finite_tree(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(_finite_tree(item) for item in value.values())
    if isinstance(value, list):
        return all(_finite_tree(item) for item in value)
    return True


def run_stress_rows(reconstruction: Reconstruction) -> dict[str, Any]:
    client = make_client()
    results: list[dict[str, Any]] = []
    for row in reconstruction.stress_records:
        missing = [
            name for name in ("area_are", "duck_count", "planting_system", "rice_variety")
            if row.get(name) is None
        ]
        if missing:
            results.append({
                "source_row": row["source_row"],
                "farmer_cluster_id": row["farmer_cluster_id"],
                "status": "NOT_EXECUTABLE_INPUT_UNAVAILABLE",
                "missing_inputs": missing,
                "merged_into_headline_metrics": False,
            })
            continue
        payload = {
            "land_area_are": row["area_are"],
            "duck_count": row["duck_count"],
            "planting_date": date(2025, 1, 1).isoformat(),
            "planting_system": row["planting_system"],
            "rice_variety": row["rice_variety"],
            "duck_age_days": 21,
            "p_duck_buy": (
                float(row["duck_purchase_price"])
                if isinstance(row["duck_purchase_price"], (int, float))
                and row["duck_purchase_price"] > 0 else None
            ),
        }
        response = client.post(f"{API}/dss/simulate", json=payload)
        body = response.json()
        results.append({
            "source_row": row["source_row"],
            "farmer_cluster_id": row["farmer_cluster_id"],
            "status": "EXECUTED" if response.status_code == 200 else "HTTP_REJECTED",
            "http_status": response.status_code,
            "no_nan_or_infinity": _finite_tree(body),
            "density_support": body.get("operational", {}).get("density_support"),
            "yield_availability": body.get("yield", {}).get("availability"),
            "survival_availability": body.get("duck", {}).get("survival_availability"),
            "warnings": body.get("warnings", []),
            "merged_into_headline_metrics": False,
        })
    return {
        "status": "EVALUATED_SEPARATELY",
        "N": len(results),
        "executed_n": sum(row["status"] == "EXECUTED" for row in results),
        "input_unavailable_n": sum(
            row["status"] == "NOT_EXECUTABLE_INPUT_UNAVAILABLE" for row in results
        ),
        "all_executed_rows_finite": all(
            row.get("no_nan_or_infinity", True) for row in results
        ),
        "merged_into_headline_metrics": False,
        "rows": results,
    }
