"""R2 infrastructure engine (registry R2-INF-01..04, R2-CAGE-01).

Equivalent square geometry (polygon shape is not one of the seven inputs):
    L_net_eq = 4 * sqrt(100 * A_are)

Net/fence per cycle:
    min = L * price_min / lifetime_max      (6,000 / 3)
    ref = L * price_max / lifetime_midpoint (6,750 / 2.5)
    max = L * price_max / lifetime_min      (6,750 / 2)

Cage: only the per-unit/cycle range is available (150k-200k; reference
midpoint 175k derived from the registry range). The TOTAL cage amount stays
unavailable because no sourced capacity/unit-count rule exists; no unit
count is ever inferred here.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.domain.models import ComponentAvailability
from app.engines.r2.common import high_precision, to_decimal
from app.engines.r2.config import R2EngineConfig
from app.schemas.dss import ReasonCode

GEOMETRY_ASSUMPTION = "SQUARE_EQUIVALENT"


@dataclass(frozen=True)
class NetInfrastructureResult:
    equivalent_perimeter_m: Decimal
    cost_min_rp_per_cycle: Decimal
    cost_ref_rp_per_cycle: Decimal
    cost_max_rp_per_cycle: Decimal
    geometry_assumption: str


@dataclass(frozen=True)
class CageInfrastructureResult:
    availability: ComponentAvailability
    cost_per_unit_min_rp_per_cycle: Decimal
    cost_per_unit_ref_rp_per_cycle: Decimal
    cost_per_unit_max_rp_per_cycle: Decimal
    total_amount_rp: Decimal | None
    reason_codes: tuple[ReasonCode, ...]


@dataclass(frozen=True)
class InfrastructureResult:
    net: NetInfrastructureResult
    cage: CageInfrastructureResult


def compute_infrastructure(
    land_area_are: Decimal | float | int | str,
    config: R2EngineConfig,
) -> InfrastructureResult:
    a = to_decimal(land_area_are)

    with high_precision():
        inner_side = (config.area_m2_per_are * a).sqrt()
        perimeter = to_decimal(4) * inner_side

        cost_min = perimeter * config.net_price_min_rp_per_m / config.net_lifetime_max_cycles
        cost_max = perimeter * config.net_price_max_rp_per_m / config.net_lifetime_min_cycles
        cost_ref = perimeter * config.net_price_max_rp_per_m / config.net_lifetime_mid_cycles

    return InfrastructureResult(
        net=NetInfrastructureResult(
            equivalent_perimeter_m=perimeter,
            cost_min_rp_per_cycle=cost_min,
            cost_ref_rp_per_cycle=cost_ref,
            cost_max_rp_per_cycle=cost_max,
            geometry_assumption=GEOMETRY_ASSUMPTION,
        ),
        cage=CageInfrastructureResult(
            availability=ComponentAvailability.PARTIAL_RANGE_ONLY,
            cost_per_unit_min_rp_per_cycle=config.cage_unit_min_rp_per_cycle,
            cost_per_unit_ref_rp_per_cycle=config.cage_unit_ref_rp_per_cycle,
            cost_per_unit_max_rp_per_cycle=config.cage_unit_max_rp_per_cycle,
            total_amount_rp=None,
            reason_codes=(ReasonCode.CAGE_CAPACITY_RULE_MISSING,),
        ),
    )
