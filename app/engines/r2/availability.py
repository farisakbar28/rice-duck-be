"""R2 feed / weeding / pest availability engine.

Feed (R2-FEED-01, unavailable): no numeric value may be produced until a
traceable quantity AND price lookup are configured. Missing is not zero.

Weeding (R2-WEED-01): only the local baseline cost range per are is returned
(A * [6,000, 38,000]). Biological suppression is never converted into a
monetary saving -- no reduction percentage is monetized here.

Pest (R2-PEST-01/02): descriptive context only. No universal scalar and no
monetary saving.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.domain.models import AvailabilityStatus, ComponentAvailability
from app.engines.r2.common import to_decimal
from app.engines.r2.config import R2EngineConfig
from app.schemas.dss import ReasonCode

FEED_REASON_CODES: tuple[ReasonCode, ...] = (
    ReasonCode.FEED_QUANTITY_LOOKUP_MISSING,
    ReasonCode.FEED_PRICE_LOOKUP_MISSING,
)


@dataclass(frozen=True)
class FeedResult:
    availability: AvailabilityStatus
    amount_rp: Decimal | None
    reason_codes: tuple[ReasonCode, ...]


@dataclass(frozen=True)
class WeedingResult:
    availability: ComponentAvailability
    baseline_min_rp: Decimal
    baseline_max_rp: Decimal
    saving_rp: Decimal | None


@dataclass(frozen=True)
class PestResult:
    effect: str
    saving_rp: Decimal | None


def compute_feed_cost(config: R2EngineConfig) -> FeedResult:
    """Feed stays fail-closed while quantity/price lookups are unconfigured."""
    return FeedResult(
        availability=AvailabilityStatus.UNAVAILABLE,
        amount_rp=None,
        reason_codes=FEED_REASON_CODES,
    )


def compute_weeding_baseline(
    land_area_are: Decimal | float | int | str,
    config: R2EngineConfig,
) -> WeedingResult:
    a = to_decimal(land_area_are)
    return WeedingResult(
        availability=ComponentAvailability.BASELINE_RANGE_ONLY,
        baseline_min_rp=a * config.weeding_baseline_min_rp_per_are,
        baseline_max_rp=a * config.weeding_baseline_max_rp_per_are,
        saving_rp=None,
    )


def compute_pest_effect(config: R2EngineConfig) -> PestResult:
    return PestResult(
        effect=config.pesticide_effect,
        saving_rp=None,
    )
