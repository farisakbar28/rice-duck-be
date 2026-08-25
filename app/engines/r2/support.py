"""R2 support classifiers (registry R2-AGE-01, R2-DEN-02).

Age and density are support/applicability metadata ONLY. They must never
modify yield, survival coefficients, feed, fertilizer, or economics through
any numeric multiplier or penalty. The only numeric consequence of these
flags anywhere in R2 is the survival availability gate (survival engine).

Operational extrapolation flag: IN_DOMAIN exactly when both support flags
are SUPPORTED (survival-support domain). It does NOT describe yield
literature-domain status; yield stays fail-closed until real lookups exist.
"""

from __future__ import annotations

from decimal import Decimal

from app.domain.models import (
    AgeSupportFlag,
    DensitySupportFlag,
    ExtrapolationFlag,
    PlantingSystem,
)
from app.engines.r2.common import to_decimal
from app.engines.r2.config import R2EngineConfig


def classify_age(duck_age_days: int, config: R2EngineConfig) -> AgeSupportFlag:
    """CAUTION < 21; SUPPORTED 21..30 inclusive; OUTSIDE_LOCAL_RANGE > 30."""
    age = int(duck_age_days)
    if age < config.age_supported_min_days:
        return AgeSupportFlag.CAUTION
    if age <= config.age_supported_max_days:
        return AgeSupportFlag.SUPPORTED
    return AgeSupportFlag.OUTSIDE_LOCAL_RANGE


def classify_density(
    density_are: Decimal | float | int | str,
    system: PlantingSystem,
    config: R2EngineConfig,
) -> DensitySupportFlag:
    """Deterministic density-support classifier.

    Order is literal per SSOT section 4:
      1. d >= high-risk threshold          -> HIGH_RISK
      2. inside system supported range     -> SUPPORTED
      3. limited-test band [5, 6]          -> LIMITED_TEST
      4. otherwise                          -> EXTRAPOLATION
    """
    d = to_decimal(density_are)
    low, high = config.supported_density_by_system[system.code]

    if d >= config.density_high_risk_min_are:
        return DensitySupportFlag.HIGH_RISK
    if low <= d <= high:
        return DensitySupportFlag.SUPPORTED
    if (
        config.density_limited_test_min_are
        <= d
        <= config.density_limited_test_max_are
    ):
        return DensitySupportFlag.LIMITED_TEST
    return DensitySupportFlag.EXTRAPOLATION


def operational_extrapolation(
    age_flag: AgeSupportFlag,
    density_flag: DensitySupportFlag,
) -> ExtrapolationFlag:
    """IN_DOMAIN iff both support flags are SUPPORTED, else OUT_OF_DOMAIN."""
    if age_flag is AgeSupportFlag.SUPPORTED and density_flag is DensitySupportFlag.SUPPORTED:
        return ExtrapolationFlag.IN_DOMAIN
    return ExtrapolationFlag.OUT_OF_DOMAIN
