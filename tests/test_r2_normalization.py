"""Phase 2: normalization engine -- area, density, purchase-price resolution."""

import dataclasses
from decimal import Decimal

import pytest

from app.data.seed import PARAMETER_REGISTRY, PLANTING_SYSTEMS
from app.domain.models import PurchasePriceSource
from app.engines.r2.config import R2EngineConfig, load_default_config
from app.engines.r2.normalization import NormalizedInputs, normalize_inputs


@pytest.fixture(scope="module")
def config():
    return load_default_config()


class TestAreaConversion:
    @pytest.mark.parametrize(
        ("area_are", "expected_m2"),
        [
            (7, Decimal("700")),
            (0.5, Decimal("50")),
            (1, Decimal("100")),
            (12.25, Decimal("1225")),
        ],
    )
    def test_a_m2_is_100_times_area(
        self, config, area_are: float, expected_m2: Decimal
    ) -> None:
        result = normalize_inputs(
            land_area_are=area_are,
            duck_count=10,
            p_duck_buy_manual=None,
            config=config,
        )
        assert result.area_m2 == expected_m2

    def test_float_input_uses_string_conversion(self, config) -> None:
        """Decimal(str(0.1)) path: exact decimal, no binary-float noise."""
        result = normalize_inputs(
            land_area_are=0.1, duck_count=1, p_duck_buy_manual=None, config=config
        )
        assert result.area_m2 == Decimal("10")
        assert result.land_area_are == Decimal("0.1")


class TestDensity:
    def test_density_exact(self, config) -> None:
        result = normalize_inputs(
            land_area_are=7, duck_count=28, p_duck_buy_manual=None, config=config
        )
        assert result.density_are == Decimal("4")

    def test_density_repeating_decimal_keeps_precision(self, config) -> None:
        result = normalize_inputs(
            land_area_are=3, duck_count=20, p_duck_buy_manual=None, config=config
        )
        # 20/3 = 6.666...; high precision context must keep ~50 digits.
        assert abs(result.density_are - Decimal("6.6666666666666666666666666666666666666666666666667")) < Decimal(
            "1e-45"
        )


class TestPurchasePriceResolution:
    def test_missing_price_uses_registry_default(self, config) -> None:
        result = normalize_inputs(
            land_area_are=7, duck_count=28, p_duck_buy_manual=None, config=config
        )
        assert result.purchase_price_effective == Decimal("26500")
        assert result.purchase_price_source is PurchasePriceSource.LOCAL_DEFAULT_MIDPOINT
        assert result.purchase_price_manual is None

    def test_explicit_null_price_uses_registry_default(self, config) -> None:
        result = normalize_inputs(
            land_area_are=7, duck_count=28, p_duck_buy_manual=None, config=config
        )
        assert result.purchase_price_source is PurchasePriceSource.LOCAL_DEFAULT_MIDPOINT

    @pytest.mark.parametrize("manual", [30000, 27500.5, "31000", Decimal("29999.99")])
    def test_supplied_price_passes_through_with_user_input_source(
        self, config, manual
    ) -> None:
        result = normalize_inputs(
            land_area_are=7, duck_count=28, p_duck_buy_manual=manual, config=config
        )
        assert result.purchase_price_effective == Decimal(str(manual))
        assert result.purchase_price_source is PurchasePriceSource.USER_INPUT
        assert result.purchase_price_manual == Decimal(str(manual))

    def test_default_value_tracks_registry_not_hardcode(self) -> None:
        """A modified registry default flows through; proves the engine does
        not carry its own 26,500 constant."""
        registry = dict(PARAMETER_REGISTRY)
        registry["p_duck_buy_default"] = dataclasses.replace(
            registry["p_duck_buy_default"], value=27000
        )
        custom = R2EngineConfig.from_registry(registry, PLANTING_SYSTEMS)
        result = normalize_inputs(
            land_area_are=7, duck_count=28, p_duck_buy_manual=None, config=custom
        )
        assert result.purchase_price_effective == Decimal("27000")


class TestResultShape:
    def test_normalized_inputs_fields(self) -> None:
        names = {f.name for f in dataclasses.fields(NormalizedInputs)}
        assert names == {
            "land_area_are",
            "duck_count",
            "area_m2",
            "density_are",
            "purchase_price_manual",
            "purchase_price_effective",
            "purchase_price_source",
        }

    def test_result_is_frozen(self, config) -> None:
        result = normalize_inputs(
            land_area_are=7, duck_count=28, p_duck_buy_manual=None, config=config
        )
        with pytest.raises(Exception):
            result.area_m2 = Decimal("1")  # type: ignore[misc]
