"""Metric primitives for eligible comparators ONLY (task §23/§24/§34).

The harness computes errors exclusively where a semantic-compatibility mask
is true. There is deliberately NO yield/revenue/survival/feed accuracy
function in this module: with the production yield engine fail-closed, such
a metric cannot exist, and this file must stay structurally incapable of
producing one.
"""

from __future__ import annotations

import random
import statistics
from datetime import date

YIELD_STATUS_NOT_EVALUABLE = "NOT_EVALUABLE"
YIELD_REASON_R2_UNAVAILABLE = "R2_YIELD_EVIDENCE_INSUFFICIENT"

def phase6_yield_metrics(rows: list[dict]) -> dict:
    """Calculate metrics with all actual-eligible rows as coverage denominator.

    Unavailable runtime predictions stay unavailable; they are never coerced
    to zero. The yield range is a literature evidence envelope, not a
    statistical interval.
    """
    actual_eligible = [r for r in rows if r.get("actual") is not None]
    eligible = [r for r in actual_eligible if all(r.get(k) is not None for k in ("pred_ref", "pred_low", "pred_high"))]
    coverage = len(eligible) / len(actual_eligible) if actual_eligible else None
    base = {
        "N_total_actual_eligible": len(actual_eligible),
        "N_predicted": len(eligible),
        "prediction_coverage_fraction": coverage,
        "prediction_coverage_percent": coverage * 100 if coverage is not None else None,
        "prediction_coverage": coverage,
    }
    if not eligible:
        return {**base, "N": 0, "MAE": None, "RMSE": None, "MedAE": None,
                "MBE": None, "WAPE": None, "MAPE": None, "R2": None,
                "covered_N": 0, "LITERATURE_EVIDENCE_ENVELOPE_COVERAGE": None,
                "LITERATURE_EVIDENCE_ENVELOPE_COVERAGE_PERCENT": None,
                "mean_envelope_width": None, "median_envelope_width": None}
    errors = [float(r["pred_ref"] - r["actual"]) for r in eligible]
    absolute = [abs(x) for x in errors]
    widths = [float(r["pred_high"] - r["pred_low"]) for r in eligible]
    covered = sum(r["pred_low"] <= r["actual"] <= r["pred_high"] for r in eligible)
    actual_sum = sum(abs(float(r["actual"])) for r in eligible)
    actuals = [float(r["actual"]) for r in eligible]
    mean_actual = statistics.fmean(actuals)
    ss_total = sum((value - mean_actual) ** 2 for value in actuals)
    mape_values = [abs(error / actual) * 100 for error, actual in zip(errors, actuals) if actual]
    envelope_coverage = covered / len(eligible)
    return {**base, "N": len(eligible), "MAE": statistics.fmean(absolute),
            "RMSE": (statistics.fmean(x*x for x in errors)) ** .5,
            "MedAE": float(statistics.median(absolute)), "MBE": statistics.fmean(errors),
            "WAPE": sum(absolute) / actual_sum * 100 if actual_sum else None,
            "MAPE": statistics.fmean(mape_values) if mape_values else None,
            "R2": 1 - sum(x*x for x in errors) / ss_total if ss_total else None,
            "covered_N": covered,
            "LITERATURE_EVIDENCE_ENVELOPE_COVERAGE": envelope_coverage,
            "LITERATURE_EVIDENCE_ENVELOPE_COVERAGE_PERCENT": envelope_coverage * 100,
            "mean_envelope_width": statistics.fmean(widths),
            "median_envelope_width": float(statistics.median(widths))}


def phase6_yield_subgroups(rows: list[dict], *, minimum_n: int = 3) -> dict:
    """Pre-registered descriptive subgroups; N<3 is count-only."""
    selectors = {
        "overall_numeric_prediction_cohort": lambda row: True,
        "strict_supported_domain": lambda row: row.get("age_support") == "SUPPORTED" and row.get("density_support") == "SUPPORTED",
        "INPARI_GROUP": lambda row: row.get("cultivar_group") == "INPARI_GROUP",
        "SERTANI_GROUP": lambda row: row.get("cultivar_group") == "SERTANI_GROUP",
        "Jajar Legowo": lambda row: row.get("planting_system") == "jajar_legowo",
        "Tegel": lambda row: row.get("planting_system") == "tegel",
    }
    result = {}
    for name, selector in selectors.items():
        subset = [row for row in rows if selector(row)]
        predicted_n = sum(row.get("actual") is not None and row.get("pred_ref") is not None for row in subset)
        result[name] = {
            "N": predicted_n,
            "policy": "QUANTITATIVE" if predicted_n >= minimum_n else "COUNT_ONLY_SMALL_N",
            "metrics": phase6_yield_metrics(subset) if predicted_n >= minimum_n else None,
        }
    return result


def distance_to_window_days(actual: date, window_min: date, window_max: date) -> int:
    """0 when inside the window; otherwise days to the nearest edge."""
    if window_min <= actual <= window_max:
        return 0
    return min(abs((actual - window_min).days), abs((actual - window_max).days))


def calendar_metrics(
    rows: list[dict],
) -> dict:
    """rows: [{farmer_cluster_id, predicted_min, predicted_max, actual_harvest}]

    Eligibility (observed planting + observed harvest) is applied by the
    fixture layer; this function computes over the eligible set only.
    """
    if not rows:
        return {
            "N": 0,
            "hits": 0,
            "coverage": None,
            "mean_distance_to_window_days": None,
            "median_distance_to_window_days": None,
        }
    distances = [
        distance_to_window_days(
            row["actual_harvest"], row["predicted_min"], row["predicted_max"]
        )
        for row in rows
    ]
    hits = sum(1 for d in distances if d == 0)
    n = len(rows)
    row_results = []
    for row, distance in zip(rows, distances):
        row_results.append({
            "source_row": row.get("source_row"),
            "farmer_cluster_id": row.get("farmer_cluster_id"),
            "predicted_min": row["predicted_min"].isoformat(),
            "predicted_max": row["predicted_max"].isoformat(),
            "actual_harvest": row["actual_harvest"].isoformat(),
            "window_hit": distance == 0,
            "distance_to_window_days": distance,
        })
    return {
        "N": n,
        "hits": hits,
        "coverage": hits / n,
        "mean_distance_to_window_days": statistics.fmean(distances),
        "median_distance_to_window_days": float(statistics.median(distances)),
        "rows": row_results,
    }


def cluster_bootstrap_percentile_interval(
    values_by_farmer: dict[str, list[float]],
    metric,
    *,
    resamples: int = 2_000,
    seed: int = 20260826,
    lower_q: float = 0.025,
    upper_q: float = 0.975,
) -> dict | None:
    """Cluster bootstrap by farmer (task §34): sample FARMERS with replacement,
    keep every cycle of each sampled farmer, recompute, take percentiles.

    Returns None when there is nothing eligible to bootstrap -- never an
    interval manufactured from ineligible data.
    """
    farmers = [f for f, vals in values_by_farmer.items() if vals]
    if len(farmers) < 2:
        return None
    rng = random.Random(seed)
    stats: list[float] = []
    for _ in range(resamples):
        sample: list[float] = []
        for farmer in rng.choices(farmers, k=len(farmers)):
            sample.extend(values_by_farmer[farmer])
        stats.append(metric(sample))
    stats.sort()

    def quantile(q: float) -> float:
        idx = min(len(stats) - 1, max(0, int(q * (len(stats) - 1))))
        return stats[idx]

    return {
        "resamples": resamples,
        "seed": seed,
        "cluster_unit": "farmer",
        "lower": quantile(lower_q),
        "upper": quantile(upper_q),
    }
