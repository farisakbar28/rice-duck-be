"""Phase 2: R2EngineConfig construction from the canonical registry.

The config factory must fail closed (single ValueError listing every
offender) on missing keys, wrong execution states, missing numeric values,
missing ranges, and non-integral integer fields. Derived references
(cage midpoint, lifetime midpoint) are computed, never hardcoded.
"""

import dataclasses
from decimal import Decimal

import pytest

from app.data.seed import PARAMETER_REGISTRY, PLANTING_SYSTEMS
from app.domain.models import ExecutionState
from app.engines.r2.config import R2EngineConfig, load_default_config


@pytest.fixture(scope="module")
def config() -> R2EngineConfig:
    return load_default_config()


class TestCanonicalValues:
    def test_area_factor_is_definitional_100(self, config: R2EngineConfig) -> None:
        assert config.area_m2_per_are == Decimal("100")

    def test_purchase_default(self, config: R2EngineConfig) -> None:
        assert config.p_duck_buy_default == Decimal("26500")

    def test_age_bounds_from_registry(self, config: R2EngineConfig) -> None:
        assert (config.age_supported_min_days, config.age_supported_max_days) == (21, 30)

    def test_density_metadata(self, config: R2EngineConfig) -> None:
        assert config.density_high_risk_min_are == Decimal("8")
        assert config.density_limited_test_min_are == Decimal("5")
        assert config.density_limited_test_max_are == Decimal("6")

    def test_density_map_covers_seed_systems(self, config: R2EngineConfig) -> None:
        codes = {s.code for s in PLANTING_SYSTEMS}
        assert set(config.supported_density_by_system) == codes
        assert config.supported_density_by_system["jajar_legowo"] == (
            Decimal("2"),
            Decimal("4"),
        )
        assert config.supported_density_by_system["tegel"] == (Decimal("2"), Decimal("3"))

    def test_calendar_windows(self, config: R2EngineConfig) -> None:
        assert config.release_hst_min == 21
        assert config.release_hst_max == 30
        assert config.pull_hst_min == 56
        assert config.pull_hst_max == 60
        assert config.active_duration_ref_days == 32
        assert config.active_duration_support_min_days == 28
        assert config.active_duration_support_max_days == 40

    def test_f_rd_release_reference_is_release_window_max(
        self, config: R2EngineConfig
    ) -> None:
        assert config.f_rd_release_ref_hst == config.release_hst_max == 30

    def test_survival_and_nutrients(self, config: R2EngineConfig) -> None:
        assert config.lambda_safe_ref == Decimal("0.90")
        assert config.n_need_kg_per_are == Decimal("1.1761")
        assert config.p2o5_need_kg_per_are == Decimal("0.2745")
        assert config.k2o_need_kg_per_are == Decimal("0.2745")

    def test_product_compositions_and_prices(self, config: R2EngineConfig) -> None:
        assert config.urea_n_fraction == Decimal("0.46")
        assert config.npk_n_fraction == Decimal("0.15")
        assert config.npk_p2o5_fraction == Decimal("0.10")
        assert config.npk_k2o_fraction == Decimal("0.12")
        assert config.het_urea_rp_per_kg == Decimal("1800")
        assert config.het_npk_rp_per_kg == Decimal("1840")

    def test_infrastructure_ranges_with_derived_midpoints(
        self, config: R2EngineConfig
    ) -> None:
        assert config.net_price_min_rp_per_m == Decimal("6000")
        assert config.net_price_max_rp_per_m == Decimal("6750")
        assert config.net_lifetime_min_cycles == Decimal("2")
        assert config.net_lifetime_max_cycles == Decimal("3")
        # Midpoint of the lifetime range, derived not stored.
        assert config.net_lifetime_mid_cycles == Decimal("2.5")
        assert config.cage_unit_min_rp_per_cycle == Decimal("150000")
        assert config.cage_unit_max_rp_per_cycle == Decimal("200000")
        # Reference midpoint derived from the registry range.
        assert config.cage_unit_ref_rp_per_cycle == Decimal("175000")

    def test_weeding_pest_economics_values(self, config: R2EngineConfig) -> None:
        assert config.weeding_baseline_min_rp_per_are == Decimal("6000")
        assert config.weeding_baseline_max_rp_per_are == Decimal("38000")
        assert config.pesticide_effect == "CONTEXT_SPECIFIC"
        assert config.p_gabah_ref_rp_per_kg == Decimal("6500")
        assert config.duck_terminal_min_rp_per_duck == Decimal("30000")
        assert config.duck_terminal_ref_rp_per_duck == Decimal("45000")
        assert config.duck_terminal_max_rp_per_duck == Decimal("60000")


class TestFailClosedConstruction:
    def _registry_without(self, key: str) -> dict:
        registry = dict(PARAMETER_REGISTRY)
        registry.pop(key)
        return registry

    def test_missing_parameter_raises_listing_key(self) -> None:
        with pytest.raises(ValueError) as excinfo:
            R2EngineConfig.from_registry(
                self._registry_without("lambda_safe_ref"), PLANTING_SYSTEMS
            )
        assert "lambda_safe_ref" in str(excinfo.value)

    def test_wrong_execution_state_raises(self) -> None:
        registry = dict(PARAMETER_REGISTRY)
        registry["p_duck_buy_default"] = dataclasses.replace(
            registry["p_duck_buy_default"],
            execution_state=ExecutionState.PENDING_LOOKUP,
            value=None,
        )
        with pytest.raises(ValueError) as excinfo:
            R2EngineConfig.from_registry(registry, PLANTING_SYSTEMS)
        message = str(excinfo.value)
        assert "p_duck_buy_default" in message
        assert "PENDING_LOOKUP" in message

    def test_missing_range_raises(self) -> None:
        registry = dict(PARAMETER_REGISTRY)
        registry["release_hst_window"] = dataclasses.replace(
            registry["release_hst_window"], minimum=None
        )
        with pytest.raises(ValueError) as excinfo:
            R2EngineConfig.from_registry(registry, PLANTING_SYSTEMS)
        assert "release_hst_window" in str(excinfo.value)

    def test_non_integral_integer_field_raises_not_zero(self) -> None:
        """Non-integral bounds must abort construction, never coerce to zero."""
        registry = dict(PARAMETER_REGISTRY)
        registry["release_hst_window"] = dataclasses.replace(
            registry["release_hst_window"], minimum=21.5
        )
        with pytest.raises(ValueError) as excinfo:
            R2EngineConfig.from_registry(registry, PLANTING_SYSTEMS)
        assert "integral" in str(excinfo.value)

    def test_empty_planting_systems_raises(self) -> None:
        with pytest.raises(ValueError):
            R2EngineConfig.from_registry(PARAMETER_REGISTRY, [])

    def test_inverted_density_range_raises(self) -> None:
        bad = dataclasses.replace(
            PLANTING_SYSTEMS[0],
            supported_density_min_are=4.0,
            supported_density_max_are=2.0,
        )
        with pytest.raises(ValueError):
            R2EngineConfig.from_registry(PARAMETER_REGISTRY, [bad])

    def test_all_errors_reported_together(self) -> None:
        registry = self._registry_without("pull_hst_window")
        registry["het_urea_rp_per_kg"] = dataclasses.replace(
            registry["het_urea_rp_per_kg"], value=None
        )
        with pytest.raises(ValueError) as excinfo:
            R2EngineConfig.from_registry(registry, PLANTING_SYSTEMS)
        message = str(excinfo.value)
        assert "pull_hst_window" in message
        assert "het_urea_rp_per_kg" in message


class TestImmutability:
    def test_config_is_frozen(self, config: R2EngineConfig) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            config.lambda_safe_ref = Decimal("1")  # type: ignore[misc]
