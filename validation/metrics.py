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
