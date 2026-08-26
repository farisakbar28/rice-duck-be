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

from dataclasses import dataclass
from decimal import Decimal

from app.domain.models import (
    AgeSupportFlag,
    DensitySupportFlag,
    ExtrapolationFlag,
    PlantingSystem,
)
from app.engines.r2.common import to_decimal
from app.engines.r2.config import R2EngineConfig


@dataclass(frozen=True)
class SupportInterval:
    """Canonical finite/unbounded support interval used by classifiers and views."""

    key: str
    label: str
    minimum: Decimal | None
    maximum: Decimal | None
    min_inclusive: bool
    max_inclusive: bool
    status: AgeSupportFlag | DensitySupportFlag

    def contains(self, value: Decimal | int) -> bool:
        candidate = to_decimal(value)
        if self.minimum is not None:
            if candidate < self.minimum or (
                candidate == self.minimum and not self.min_inclusive
            ):
                return False
        if self.maximum is not None:
            if candidate > self.maximum or (
                candidate == self.maximum and not self.max_inclusive
            ):
                return False
        return True


def age_support_intervals(config: R2EngineConfig) -> tuple[SupportInterval, ...]:
    """Complete positive-input age partition for R2 presentation/classification."""
    lower = to_decimal(config.age_supported_min_days)
    upper = to_decimal(config.age_supported_max_days)
    return (
        SupportInterval(
            key="age_caution",
            label="Below locally supported age",
            minimum=Decimal("0"),
            maximum=lower,
            min_inclusive=False,
            max_inclusive=False,
            status=AgeSupportFlag.CAUTION,
        ),
        SupportInterval(
            key="age_supported",
            label="Locally supported age",
            minimum=lower,
            maximum=upper,
            min_inclusive=True,
            max_inclusive=True,
            status=AgeSupportFlag.SUPPORTED,
        ),
        SupportInterval(
            key="age_outside_local_range",
            label="Above locally supported age",
            minimum=upper,
            maximum=None,
            min_inclusive=False,
            max_inclusive=False,
            status=AgeSupportFlag.OUTSIDE_LOCAL_RANGE,
        ),
    )


def density_support_intervals(
    system: PlantingSystem,
    config: R2EngineConfig,
) -> tuple[SupportInterval, ...]:
    """Complete positive-input density partition for one planting system."""
    supported_min, supported_max = config.supported_density_by_system[system.code]
    limited_min = config.density_limited_test_min_are
    limited_max = config.density_limited_test_max_are
    high_risk = config.density_high_risk_min_are
    return (
        SupportInterval(
            key="density_extrapolation_below_supported",
            label="Below supported density",
            minimum=Decimal("0"),
            maximum=supported_min,
            min_inclusive=False,
            max_inclusive=False,
            status=DensitySupportFlag.EXTRAPOLATION,
        ),
        SupportInterval(
            key="density_supported",
            label="Supported density",
            minimum=supported_min,
            maximum=supported_max,
            min_inclusive=True,
            max_inclusive=True,
            status=DensitySupportFlag.SUPPORTED,
        ),
        SupportInterval(
            key="density_extrapolation_before_limited_test",
            label="Extrapolation between supported and limited-test ranges",
            minimum=supported_max,
            maximum=limited_min,
            min_inclusive=False,
            max_inclusive=False,
            status=DensitySupportFlag.EXTRAPOLATION,
        ),
        SupportInterval(
            key="density_limited_test",
            label="Limited-test density",
            minimum=limited_min,
            maximum=limited_max,
            min_inclusive=True,
            max_inclusive=True,
            status=DensitySupportFlag.LIMITED_TEST,
        ),
        SupportInterval(
            key="density_extrapolation_before_high_risk",
            label="Extrapolation between limited-test and high-risk ranges",
            minimum=limited_max,
            maximum=high_risk,
            min_inclusive=False,
            max_inclusive=False,
            status=DensitySupportFlag.EXTRAPOLATION,
        ),
        SupportInterval(
            key="density_high_risk",
            label="High-risk density",
            minimum=high_risk,
            maximum=None,
            min_inclusive=True,
            max_inclusive=False,
            status=DensitySupportFlag.HIGH_RISK,
        ),
    )


def classify_age(duck_age_days: int, config: R2EngineConfig) -> AgeSupportFlag:
    """CAUTION < 21; SUPPORTED 21..30 inclusive; OUTSIDE_LOCAL_RANGE > 30."""
    age = int(duck_age_days)
    for interval in age_support_intervals(config):
        if interval.contains(age):
            return interval.status  # type: ignore[return-value]
    raise ValueError("Duck age must be greater than zero.")


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
    for interval in density_support_intervals(system, config):
        if interval.contains(d):
            return interval.status  # type: ignore[return-value]
    raise ValueError("Duck density must be greater than zero.")


def operational_extrapolation(
    age_flag: AgeSupportFlag,
    density_flag: DensitySupportFlag,
) -> ExtrapolationFlag:
    """IN_DOMAIN iff both support flags are SUPPORTED, else OUT_OF_DOMAIN."""
    if age_flag is AgeSupportFlag.SUPPORTED and density_flag is DensitySupportFlag.SUPPORTED:
        return ExtrapolationFlag.IN_DOMAIN
    return ExtrapolationFlag.OUT_OF_DOMAIN
