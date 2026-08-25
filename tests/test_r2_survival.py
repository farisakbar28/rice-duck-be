"""Phase 2: survival engine -- availability gate and floor semantics."""

import pytest

from app.domain.models import AgeSupportFlag, AvailabilityStatus, DensitySupportFlag
from app.engines.r2.config import load_default_config
from app.engines.r2.survival import compute_survival

SUPPORTED = AgeSupportFlag.SUPPORTED


@pytest.fixture(scope="module")
def config():
    return load_default_config()


def _unavailable_flags():
    return [
        AgeSupportFlag.CAUTION,
        AgeSupportFlag.OUTSIDE_LOCAL_RANGE,
    ], [
        DensitySupportFlag.LIMITED_TEST,
        DensitySupportFlag.HIGH_RISK,
        DensitySupportFlag.EXTRAPOLATION,
    ]


class TestGate:
    def test_supported_age_and_density_is_available(self, config) -> None:
        result = compute_survival(28, SUPPORTED, DensitySupportFlag.SUPPORTED, config)
        assert result.availability is AvailabilityStatus.AVAILABLE
        assert result.lambda_eff == __import__("decimal").Decimal("0.90")
        assert result.surviving_ducks == 25

    @pytest.mark.parametrize("age_flag", [AgeSupportFlag.CAUTION, AgeSupportFlag.OUTSIDE_LOCAL_RANGE])
    def test_unsupported_age_blocks_survival(self, config, age_flag) -> None:
        result = compute_survival(28, age_flag, DensitySupportFlag.SUPPORTED, config)
        assert result.availability is AvailabilityStatus.UNAVAILABLE
        assert result.lambda_eff is None
        assert result.surviving_ducks is None

    @pytest.mark.parametrize(
        "density_flag",
        [
            DensitySupportFlag.LIMITED_TEST,
            DensitySupportFlag.HIGH_RISK,
            DensitySupportFlag.EXTRAPOLATION,
        ],
    )
    def test_unsupported_density_blocks_survival(self, config, density_flag) -> None:
        result = compute_survival(28, SUPPORTED, density_flag, config)
        assert result.availability is AvailabilityStatus.UNAVAILABLE
        assert result.lambda_eff is None
        assert result.surviving_ducks is None

    def test_both_unsupported_blocks_survival(self, config) -> None:
        result = compute_survival(
            28, AgeSupportFlag.CAUTION, DensitySupportFlag.HIGH_RISK, config
        )
        assert result.availability is AvailabilityStatus.UNAVAILABLE
        assert result.lambda_eff is None
        assert result.surviving_ducks is None


class TestFloorSemantics:
    @pytest.mark.parametrize(
        ("duck_count", "expected"),
        [
            (28, 25),   # 25.2 -> 25
            (29, 26),   # 26.1 -> 26
            (30, 27),   # 27.0 -> 27
            (10, 9),
            (1, 0),
        ],
    )
    def test_floor_of_product(self, config, duck_count: int, expected: int) -> None:
        result = compute_survival(
            duck_count, SUPPORTED, DensitySupportFlag.SUPPORTED, config
        )
        assert result.surviving_ducks == expected


class TestNoDegradedEstimate:
    def test_out_of_domain_never_gets_a_rate(self, config) -> None:
        """No fallback rate of any kind outside the supported domain."""
        age_flags, density_flags = _unavailable_flags()
        for age in age_flags:
            for density in density_flags:
                result = compute_survival(50, age, density, config)
                assert result.lambda_eff is None
                assert result.surviving_ducks is None

    def test_result_type_has_no_sale_state(self, config) -> None:
        import dataclasses

        names = {f.name for f in dataclasses.fields(type(compute_survival(28, SUPPORTED, DensitySupportFlag.SUPPORTED, config)))}
        assert names == {"availability", "lambda_eff", "surviving_ducks"}
