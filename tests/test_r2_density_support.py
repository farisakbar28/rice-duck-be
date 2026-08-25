"""Phase 2: density support classifier -- full boundary matrix per system."""

from decimal import Decimal

import pytest

from app.data.seed import PLANTING_SYSTEMS
from app.domain.models import (
    AgeSupportFlag,
    DensitySupportFlag,
    ExtrapolationFlag,
)
from app.engines.r2.config import load_default_config
from app.engines.r2.support import classify_density, operational_extrapolation

JARWO = next(s for s in PLANTING_SYSTEMS if s.code == "jajar_legowo")
TEGEL = next(s for s in PLANTING_SYSTEMS if s.code == "tegel")


@pytest.fixture(scope="module")
def config():
    return load_default_config()


def d(value: str) -> Decimal:
    return Decimal(value)


class TestJarwoMatrix:
    @pytest.mark.parametrize(
        ("density", "expected"),
        [
            ("1.9", DensitySupportFlag.EXTRAPOLATION),
            ("2", DensitySupportFlag.SUPPORTED),
            ("4", DensitySupportFlag.SUPPORTED),
            ("4.1", DensitySupportFlag.EXTRAPOLATION),
            ("5", DensitySupportFlag.LIMITED_TEST),
            ("6", DensitySupportFlag.LIMITED_TEST),
            ("6.1", DensitySupportFlag.EXTRAPOLATION),
            ("7.9", DensitySupportFlag.EXTRAPOLATION),
            ("8", DensitySupportFlag.HIGH_RISK),
        ],
    )
    def test_boundaries(self, config, density: str, expected) -> None:
        assert classify_density(d(density), JARWO, config) is expected


class TestTegelMatrix:
    @pytest.mark.parametrize(
        ("density", "expected"),
        [
            ("1.9", DensitySupportFlag.EXTRAPOLATION),
            ("2", DensitySupportFlag.SUPPORTED),
            ("3", DensitySupportFlag.SUPPORTED),
            ("3.1", DensitySupportFlag.EXTRAPOLATION),
            ("5", DensitySupportFlag.LIMITED_TEST),
            ("6", DensitySupportFlag.LIMITED_TEST),
            ("8", DensitySupportFlag.HIGH_RISK),
        ],
    )
    def test_boundaries(self, config, density: str, expected) -> None:
        assert classify_density(d(density), TEGEL, config) is expected


class TestHighRiskThresholdInclusive:
    def test_exactly_8_is_high_risk_for_both_systems(self, config) -> None:
        assert classify_density(d("8"), JARWO, config) is DensitySupportFlag.HIGH_RISK
        assert classify_density(d("8"), TEGEL, config) is DensitySupportFlag.HIGH_RISK

    def test_just_below_8_is_not_high_risk(self, config) -> None:
        assert (
            classify_density(d("7.9999999"), JARWO, config)
            is DensitySupportFlag.EXTRAPOLATION
        )

    def test_just_above_8_is_high_risk(self, config) -> None:
        assert (
            classify_density(d("8.0000001"), JARWO, config)
            is DensitySupportFlag.HIGH_RISK
        )


class TestLimitedTestBandSystemIndependent:
    def test_band_applies_regardless_of_system(self, config) -> None:
        for system in (JARWO, TEGEL):
            assert (
                classify_density(d("5"), system, config)
                is DensitySupportFlag.LIMITED_TEST
            )
            assert (
                classify_density(d("5.5"), system, config)
                is DensitySupportFlag.LIMITED_TEST
            )
            assert (
                classify_density(d("6"), system, config)
                is DensitySupportFlag.LIMITED_TEST
            )


class TestMetadataOnly:
    def test_classifier_returns_bare_enum(self, config) -> None:
        result = classify_density(d("4"), JARWO, config)
        assert isinstance(result, DensitySupportFlag)


class TestOperationalExtrapolation:
    @pytest.mark.parametrize(
        ("age_flag", "density_flag", "expected"),
        [
            (AgeSupportFlag.SUPPORTED, DensitySupportFlag.SUPPORTED, ExtrapolationFlag.IN_DOMAIN),
            (AgeSupportFlag.SUPPORTED, DensitySupportFlag.LIMITED_TEST, ExtrapolationFlag.OUT_OF_DOMAIN),
            (AgeSupportFlag.CAUTION, DensitySupportFlag.SUPPORTED, ExtrapolationFlag.OUT_OF_DOMAIN),
            (AgeSupportFlag.OUTSIDE_LOCAL_RANGE, DensitySupportFlag.HIGH_RISK, ExtrapolationFlag.OUT_OF_DOMAIN),
        ],
    )
    def test_in_domain_only_when_both_supported(
        self, age_flag, density_flag, expected
    ) -> None:
        assert operational_extrapolation(age_flag, density_flag) is expected
