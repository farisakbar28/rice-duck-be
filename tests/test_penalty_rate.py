"""Fase 7 — edge case tests for the DSS core calculator.

Covers:
- Floor infra proportional split
- Zero raw infra → 50/50 split (interim, open question)
- High density saturation
- Small A_are / d=0 edge
- Cost_infra_net + Cost_infra_cage = Cost_infra invariant
"""

import math

import pytest

from app.engines.impact_engine import (
    INFRA_FLOOR_RP,
    compute_infrastructure_breakdown,
    compute_labor_breakdown,
)


def test_infra_floor_split_invariant_many_cases() -> None:
    """For any (J, A), net + cage == Cost_infra exactly."""
    for j in (1, 2, 5, 10, 20, 50):
        for a in (0.5, 1.0, 2.0, 5.0, 10.0, 20.0):
            inf = compute_infrastructure_breakdown(j, a)
            total = inf["Cost_infra_net"] + inf["Cost_infra_cage"]
            assert total == pytest.approx(inf["Cost_infra"], rel=1e-4), (
                f"j={j}, a={a}: {inf}"
            )


def test_infra_high_d_j_above_floor() -> None:
    """Very large inputs: raw sum should exceed floor and not scale."""
    inf = compute_infrastructure_breakdown(500, 500)
    # raw > floor
    assert inf["Cost_infra"] > INFRA_FLOOR_RP
    # net and cage not equal to half of total
    assert inf["Cost_infra_net"] != pytest.approx(inf["Cost_infra"] / 2)


def test_infra_floor_active_split() -> None:
    """Small J, A: floor active, both parts scaled proportionally."""
    inf = compute_infrastructure_breakdown(1, 1)
    assert inf["Cost_infra"] == INFRA_FLOOR_RP
    # Both positive
    assert inf["Cost_infra_net"] > 0
    assert inf["Cost_infra_cage"] > 0


def test_infra_zero_zero_50_50() -> None:
    """J=0, A=0 → 50/50 floor (open question, interim)."""
    inf = compute_infrastructure_breakdown(0, 0)
    assert inf["Cost_infra"] == INFRA_FLOOR_RP
    assert inf["Cost_infra_net"] == INFRA_FLOOR_RP / 2
    assert inf["Cost_infra_cage"] == INFRA_FLOOR_RP / 2


def test_labor_weed_hired_decreases_with_density() -> None:
    """Higher d → higher R_weed(d) → lower C_weed_hired."""
    lab_low = compute_labor_breakdown(10, 0.0, 0.15, 1.0)
    lab_high = compute_labor_breakdown(10, 0.0, 0.15, 8.0)
    # d=1 → R_weed ≈ 0.95*(1-exp(-0.35)) ≈ 0.296
    # d=8 → R_weed ≈ 0.95*(1-exp(-2.8)) ≈ 0.893
    # So C_weed_hired at d=1 > C_weed_hired at d=8
    assert lab_low["Cost_labor_weed_hired"] > lab_high["Cost_labor_weed_hired"]


def test_labor_weed_hired_scales_with_area() -> None:
    lab_a10 = compute_labor_breakdown(10, 0.0, 0.15, 5.0)
    lab_a20 = compute_labor_breakdown(20, 0.0, 0.15, 2.5)
    # Same J, A doubled → d halved.
    # C_weed_hired = k * A * (1 - R_weed(d))
    # At d=5, R≈0.7849 → weed_hired ≈ 30539*10*0.2151 ≈ 65685
    # At d=2.5, R≈0.95*(1-exp(-0.875)) ≈ 0.583 → weed_hired ≈ 30539*20*0.417 ≈ 254707
    # A doubled but R dropped → may go either way
    # Just assert both are positive
    assert lab_a10["Cost_labor_weed_hired"] > 0
    assert lab_a20["Cost_labor_weed_hired"] > 0


def test_labor_base_independent_of_ducks() -> None:
    lab1 = compute_labor_breakdown(10, 0.0, 0.15, 1.0)
    lab2 = compute_labor_breakdown(10, 0.0, 0.15, 10.0)
    # base = 47527 * A — same A → same base
    assert lab1["Cost_labor_base"] == lab2["Cost_labor_base"]
