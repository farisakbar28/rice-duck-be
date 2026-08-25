"""R2 survival engine (registry R2-SURV-01 .. R2-SURV-03).

Conditional safe-domain estimate:
    lambda_eff = 0.90 ONLY IF age SUPPORTED AND density SUPPORTED;
    otherwise survival is UNAVAILABLE with no numeric estimate.

When available:
    N_survive = floor(J * lambda_eff)

The surviving-duck count is a biological state. It is never a sale quantity
and never converted into duck cash revenue anywhere in this package.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_FLOOR, Decimal

from app.domain.models import AgeSupportFlag, AvailabilityStatus, DensitySupportFlag
from app.engines.r2.common import to_decimal
from app.engines.r2.config import R2EngineConfig


@dataclass(frozen=True)
class SurvivalResult:
    availability: AvailabilityStatus
    lambda_eff: Decimal | None
    surviving_ducks: int | None


def compute_survival(
    duck_count: int,
    age_flag: AgeSupportFlag,
    density_flag: DensitySupportFlag,
    config: R2EngineConfig,
) -> SurvivalResult:
    if (
        age_flag is not AgeSupportFlag.SUPPORTED
        or density_flag is not DensitySupportFlag.SUPPORTED
    ):
        return SurvivalResult(
            availability=AvailabilityStatus.UNAVAILABLE,
            lambda_eff=None,
            surviving_ducks=None,
        )

    lam = config.lambda_safe_ref
    product = to_decimal(int(duck_count)) * lam
    surviving = int(product.to_integral_value(rounding=ROUND_FLOOR))
    return SurvivalResult(
        availability=AvailabilityStatus.AVAILABLE,
        lambda_eff=lam,
        surviving_ducks=surviving,
    )
