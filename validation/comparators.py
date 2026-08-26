"""Phase-6 pre-comparator builders and excluded-row stress runs.

Comparator functions are called only after the CLI's source-reconstruction
gate. They consume synthetic/runtime responses and never calibrate R2.
"""

from __future__ import annotations

import math
import statistics
from datetime import date
from typing import Any

from validation._bootstrap import configure_runtime_env
from validation.metrics import (
    calendar_metrics,
    cluster_bootstrap_metric_intervals,
    phase6_yield_metrics,
    phase6_yield_subgroups,
    revenue_metrics,
)
from validation.provenance import git_head
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
    provenance_counts = {
        "OBSERVED_VALUE": 0,
        "DERIVED_ACTUAL": 0,
        "EXPLICIT_ZERO": 0,
        "MISSING_UNKNOWN": 0,
        "LEGACY_IMPUTATION": 0,
    }
    for row in reconstruction.clean_records:
        provenance = row.get("actual_provenance", {}).get("duck_purchase_price")
        if provenance in provenance_counts:
            provenance_counts[provenance] += 1
    rows = []
    for row in reconstruction.clean_records:
        price = row["duck_purchase_price"]
        provenance = row["actual_provenance"].get("duck_purchase_price")
        if provenance != "OBSERVED_VALUE" or not isinstance(price, (int, float)) or price <= 0:
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
        "strict_n": len(rows),
        "strict_excluded_n": len(reconstruction.clean_records) - len(rows),
        "provenance_counts": provenance_counts,
        "derived_actual_context_n": provenance_counts["DERIVED_ACTUAL"],
        "mean_observed_price_rp_per_duck": statistics.fmean(prices) if prices else None,
        "median_observed_price_rp_per_duck": (
            float(statistics.median(prices)) if prices else None
        ),
        "rows": rows,
    }


def _revenue_diagnostic(rows: list[dict[str, Any]], *, price_field: str, price: float | None, name: str) -> dict[str, Any]:
    diagnostic_rows: list[dict[str, Any]] = []
    for row in rows:
        actual_yield = row.get("actual")
        area = row.get("area_are")
        if not isinstance(actual_yield, (int, float)) or not isinstance(area, (int, float)) or area <= 0:
            continue
        unit_price = price if price_field == "current_hpp" else row.get("paddy_price")
        if not isinstance(unit_price, (int, float)) or unit_price <= 0:
            continue
        actual_total_yield = float(actual_yield) * float(area)
        diagnostic_rows.append({
            "source_row": row.get("source_row"),
            "farmer_cluster_id": row.get("farmer_cluster_id"),
            "area_are": float(area),
            "actual_yield_kg_per_are": float(actual_yield),
            "actual_total_yield_kg": actual_total_yield,
            "price_rp_per_kg": float(unit_price),
            "price_source": "R2_REGULATORY_HPP" if price_field == "current_hpp" else "COMPARATOR_METADATA_ONLY",
            "pred_ref": (
                float(row["pred_total_ref"]) * float(unit_price)
                if row.get("pred_total_ref") is not None else None
            ),
            "pred_low": (
                float(row["pred_total_low"]) * float(unit_price)
                if row.get("pred_total_low") is not None else None
            ),
            "pred_high": (
                float(row["pred_total_high"]) * float(unit_price)
                if row.get("pred_total_high") is not None else None
            ),
            "actual_revenue": actual_total_yield * float(unit_price),
        })
    metrics = revenue_metrics(diagnostic_rows)
    metrics["MAE_RP_PER_CYCLE"] = metrics["MAE"]
    metrics["RMSE_RP_PER_CYCLE"] = metrics["RMSE"]
    metrics["MedAE_RP_PER_CYCLE"] = metrics["MedAE"]
    metrics["MBE_RP_PER_CYCLE"] = metrics["MBE"]
    metrics["WAPE_PERCENT"] = metrics["WAPE"]
    return {
        "name": name,
        "status": "EVALUATED" if metrics["N_predicted"] else "NOT_EVALUABLE",
        "reason": None if metrics["N_predicted"] else "NO_ELIGIBLE_PREDICTED_ROWS",
        "metrics": metrics,
        "rows": diagnostic_rows,
    }


def build_revenue_diagnostics(yield_validation: dict[str, Any]) -> dict[str, Any]:
    """Pre-register the two allowed paddy-revenue translations.

    Historical prices are used only in the price-neutral comparator and are
    never passed into the runtime simulation request.
    """
    rows = yield_validation.get("rows", [])
    config = R2EngineConfig.from_registry(PARAMETER_REGISTRY, PLANTING_SYSTEMS)
    hpp = float(config.p_gabah_ref_rp_per_kg)
    operational = _revenue_diagnostic(
        rows,
        price_field="current_hpp",
        price=hpp,
        name="CURRENT_HPP_OPERATIONAL_VALUE_DIAGNOSTIC",
    )
    price_neutral_rows = [
        row for row in rows
        if row.get("paddy_price_provenance") == "OBSERVED_VALUE"
        and isinstance(row.get("paddy_price"), (int, float))
        and row["paddy_price"] > 0
    ]
    neutral = _revenue_diagnostic(
        price_neutral_rows,
        price_field="historical",
        price=None,
        name="PRICE_NEUTRAL_HISTORICAL_PRICE_DIAGNOSTIC",
    )
    if not neutral["metrics"]["N_total_actual_eligible"]:
        neutral["reason"] = "HISTORICAL_PADDY_PRICE_UNAVAILABLE"
    return {
        "status": "EVALUATED" if operational["status"] == "EVALUATED" else "NOT_EVALUABLE",
        "current_hpp_rp_per_kg": hpp,
        "diagnostics": {
            "CURRENT_HPP_OPERATIONAL_VALUE_DIAGNOSTIC": operational,
            "PRICE_NEUTRAL_HISTORICAL_PRICE_DIAGNOSTIC": neutral,
        },
    }


# Explicit alias for callers using the report terminology.
build_revenue_validation = build_revenue_diagnostics


def build_yield_comparator(
    reconstruction: Reconstruction,
    *,
    backend_commit_sha: str | None = None,
    client=None,
) -> dict[str, Any]:
    """Replay clean rows through the canonical HTTP runtime, without formulas.

    This function is deliberately dormant unless source reconstruction has
    succeeded.  It never opens a workbook itself and records the two
    pre-registered supported-age assumptions for every executed row.
    """
    client = client or make_client()
    backend_commit_sha = backend_commit_sha or git_head()
    records: list[dict[str, Any]] = []
    for row in reconstruction.clean_records:
        fields = row["input_fields"]
        base_payload = {name: fields[name]["value"] for name in (
            "land_area_are", "duck_count", "planting_date", "planting_system",
            "rice_variety", "p_duck_buy",
        )}
        responses: dict[int, dict[str, Any]] = {}
        response_statuses: dict[int, int] = {}
        for age in (21, 30):
            payload = {**base_payload, "duck_age_days": age}
            response = client.post(f"{API}/dss/simulate", json=payload)
            response_statuses[age] = response.status_code
            responses[age] = response.json() if response.status_code == 200 else {}
        y21, y30 = responses[21].get("yield", {}), responses[30].get("yield", {})
        invariant_keys = (
            "availability", "yield_ref_kg_per_are", "yield_low_kg_per_are",
            "yield_high_kg_per_are", "reason_codes",
        )
        http_execution_failure = any(
            response_statuses[age] != 200 for age in (21, 30)
        )
        invariant = (
            None if http_execution_failure
            else all(y21.get(key) == y30.get(key) for key in invariant_keys)
        )
        if invariant is False:
            raise RuntimeError(f"AGE_ASSUMPTION_YIELD_INVARIANCE_FAILED source_row={row['source_row']}")
        numeric_21 = y21.get("yield_ref_kg_per_are") is not None
        actual = row.get("actual_yield_kg_per_are")
        actual_provenance = row.get("actual_provenance", {}).get("actual_yield_kg_per_are")
        if actual_provenance != "OBSERVED_VALUE":
            actual = None
        records.append({
            "source_row": row["source_row"], "farmer_cluster_id": row["farmer_cluster_id"],
            "model_version": responses[21].get("model", {}).get("model_version"),
            "registry_version": responses[21].get("model", {}).get("parameter_registry_version"),
            "freeze_id": responses[21].get("model", {}).get("freeze_id"),
            "backend_commit_sha": backend_commit_sha,
            "response_model_commit_sha": responses[21].get("model", {}).get("model_commit_sha"),
            "land_area_are": fields["land_area_are"]["value"], "land_area_are_provenance": fields["land_area_are"]["provenance"],
            "duck_count": fields["duck_count"]["value"], "duck_count_provenance": fields["duck_count"]["provenance"],
            "planting_system": fields["planting_system"]["value"], "planting_system_provenance": fields["planting_system"]["provenance"],
            "rice_variety": fields["rice_variety"]["value"], "rice_variety_provenance": fields["rice_variety"]["provenance"],
            "duck_age_days": 21, "duck_age_days_provenance": "VALIDATION_ASSUMPTION",
            "replay_age_21_days": 21,
            "replay_age_30_days": 30,
            "replay_age_21_provenance": "VALIDATION_ASSUMPTION",
            "replay_age_30_provenance": "VALIDATION_ASSUMPTION",
            "planting_date": fields["planting_date"]["value"], "planting_date_provenance": fields["planting_date"]["provenance"],
            "density": responses[21].get("operational", {}).get("density_are"),
            "age_support": responses[21].get("operational", {}).get("age_support"),
            "density_support": responses[21].get("operational", {}).get("density_support"),
            "cultivar_group": y21.get("cultivar_group_code"),
            "actual": actual, "actual_yield": actual, "actual_yield_provenance": actual_provenance,
            "area_are": fields["land_area_are"]["value"],
            "paddy_price": row.get("paddy_price"),
            "paddy_price_provenance": row.get("actual_provenance", {}).get("paddy_price"),
            "yield_availability": y21.get("availability"), "reason_codes": y21.get("reason_codes", []),
            "yield_availability_age_21": y21.get("availability"),
            "yield_availability_age_30": y30.get("availability"),
            "yield_ref_age_21": y21.get("yield_ref_kg_per_are"),
            "yield_ref_age_30": y30.get("yield_ref_kg_per_are"),
            "yield_low_age_21": y21.get("yield_low_kg_per_are"),
            "yield_low_age_30": y30.get("yield_low_kg_per_are"),
            "yield_high_age_21": y21.get("yield_high_kg_per_are"),
            "yield_high_age_30": y30.get("yield_high_kg_per_are"),
            "reason_codes_age_21": y21.get("reason_codes", []),
            "reason_codes_age_30": y30.get("reason_codes", []),
            "pred_ref": y21.get("yield_ref_kg_per_are"), "pred_low": y21.get("yield_low_kg_per_are"), "pred_high": y21.get("yield_high_kg_per_are"),
            "pred_total_ref": y21.get("yield_total_ref_kg"),
            "pred_total_low": y21.get("yield_total_low_kg"),
            "pred_total_high": y21.get("yield_total_high_kg"),
            "baseline_source_id": y21.get("yield_baseline_source_id"), "frd_source_id": y21.get("yield_frd_source_id"),
            "evidence_strength": y21.get("yield_evidence_strength"), "evidence_warning": y21.get("yield_evidence_warning"),
            "actual_inside_evidence_envelope": (y21.get("yield_low_kg_per_are") <= actual <= y21.get("yield_high_kg_per_are")) if numeric_21 and actual is not None else None,
            "age_assumption_invariant": invariant,
            "http_status_21": response_statuses[21],
            "http_status_30": response_statuses[30],
            "http_status_age_21": response_statuses[21],
            "http_status_age_30": response_statuses[30],
            "http_execution_failure": http_execution_failure,
            "prediction_status": (
                "HTTP_EXECUTION_FAILURE"
                if any(response_statuses[age] != 200 for age in (21, 30))
                else "SCIENTIFIC_UNAVAILABLE"
                if y21.get("yield_ref_kg_per_are") is None
                else "PREDICTED"
            ),
        })
    metrics = phase6_yield_metrics(records)
    metrics["http_execution_failure_n"] = sum(row["http_execution_failure"] for row in records)
    metrics["scientific_unavailable_n"] = sum(
        row["prediction_status"] == "SCIENTIFIC_UNAVAILABLE" for row in records
    )
    bootstrap = cluster_bootstrap_metric_intervals(records)
    return {
        "status": "EVALUATED" if metrics["N_predicted"] else "NOT_EVALUABLE",
        "age_assumptions_days": [21, 30], "age_assumption_provenance": "VALIDATION_ASSUMPTION",
        "primary_replay_age_days": 21, "sensitivity_replay_age_days": 30,
        "age_assumption_invariance": all(row["age_assumption_invariant"] for row in records),
        "metrics": metrics, "subgroups": phase6_yield_subgroups(records),
        "cluster_bootstrap": bootstrap, "rows": records,
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
