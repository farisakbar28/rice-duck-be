"""Phase 2: yield engine -- fail-closed interface with synthetic test lookups.

Synthetic fixtures are clearly named (``synthetic_variety``, SYNTH_* values)
and exist ONLY in this test module; production keeps the empty store.
"""

from decimal import Decimal

import pytest

from app.data.seed import PARAMETER_REGISTRY
from app.domain.models import AvailabilityStatus, ProvenanceStatus, ExecutionState
from app.domain.models import RiceVariety
from app.engines.r2.config import load_default_config
from app.engines.r2.normalization import normalize_inputs
from app.engines.r2.yield_engine import (
    EMPTY_YIELD_LOOKUP_STORE,
    EmptyYieldLookupStore,
    FRDEntry,
    YieldBaselineEntry,
    compute_yield,
)
from app.repositories.lookup_repository import lookup_repository
from app.schemas.dss import ReasonCode

# --- clearly synthetic lookup data (never production) -----------------------
SYNTH_BASELINE_KG_PER_ARE = Decimal("50")
SYNTH_FACTOR = Decimal("1.08")
SYNTH_VERSION = "synthetic-test-v1"

SYNTH_VARIETY = RiceVariety(
    code="synthetic_variety",
    label="Synthetic Test Variety",
    harvest_hst_min=100,
    harvest_hst_max=110,
    calendar_status=ProvenanceStatus.LOCAL_ESTIMATE,
    yield_lookup_status=ExecutionState.PENDING_LOOKUP,
    exact_cultivar_code="synthetic_variety",
)


class SyntheticYieldLookupStore:
    """Test-only store with explicit supported domains."""

    def __init__(self, baselines=None, entries=None):
        self._baselines = (
            baselines
            if baselines is not None
            else {
                "synthetic_variety": YieldBaselineEntry(
                    exact_cultivar_code="synthetic_variety",
                    kg_per_are=SYNTH_BASELINE_KG_PER_ARE,
                    source_id="SYNTHETIC",
                    version=SYNTH_VERSION,
                )
            }
        )
        self._entries = (
            entries
            if entries is not None
            else [
                FRDEntry(
                    system_code="jajar_legowo",
                    d_min_are=Decimal("2"),
                    d_max_are=Decimal("4"),
                    factor=SYNTH_FACTOR,
                    source_id="SYNTHETIC",
                    version=SYNTH_VERSION,
                )
            ]
        )

    def find_baseline(self, exact_cultivar_code: str):
        return self._baselines.get(exact_cultivar_code)

    def find_response_factor(self, *, system_code, density_are, release_hst_ref):
        for entry in self._entries:
            if entry.system_code == system_code and entry.d_min_are <= density_are <= entry.d_max_are:
                return entry
        return None


@pytest.fixture(scope="module")
def config():
    return load_default_config()


def normalized(area="7", ducks=28, config=None):
    return normalize_inputs(
        land_area_are=area, duck_count=ducks, p_duck_buy_manual=None, config=config
    )


class TestProductionFailClosed:
    def test_empty_store_yields_unavailable_with_both_reasons(self, config) -> None:
        result = compute_yield(
            variety=lookup_repository.get_rice_variety("sertani"),
            system_code="jajar_legowo",
            normalized_inputs=normalized(config=config),
            config=config,
        )
        assert result.availability is AvailabilityStatus.UNAVAILABLE
        assert result.exact_cultivar_resolved is False
        assert result.baseline_kg_per_are is None
        assert result.rice_duck_response_factor is None
        assert result.yield_kg_per_are is None
        assert result.yield_total_kg is None
        assert result.reason_codes == (
            ReasonCode.Y_BASE_LOOKUP_MISSING,
            ReasonCode.F_RD_LOOKUP_MISSING,
        )

    def test_empty_store_is_the_production_default(self, config) -> None:
        assert isinstance(EMPTY_YIELD_LOOKUP_STORE, EmptyYieldLookupStore)
        assert EMPTY_YIELD_LOOKUP_STORE.find_baseline("anything") is None
        assert (
            EMPTY_YIELD_LOOKUP_STORE.find_response_factor(
                system_code="tegel",
                density_are=Decimal("3"),
                release_hst_ref=30,
            )
            is None
        )

    def test_registry_pending_lookups_stay_none(self) -> None:
        """No synthetic lookup may leak into production seed."""
        assert PARAMETER_REGISTRY["yield_base_by_variety"].value is None
        assert PARAMETER_REGISTRY["f_rd_lookup"].value is None

    def test_unresolved_variety_raises(self, config) -> None:
        with pytest.raises(ValueError):
            compute_yield(
                variety=None,
                system_code="jajar_legowo",
                normalized_inputs=normalized(config=config),
                config=config,
            )


class TestPartialLookupsFailClosed:
    def test_missing_baseline_only(self, config) -> None:
        store = SyntheticYieldLookupStore(baselines={})
        result = compute_yield(
            variety=SYNTH_VARIETY,
            system_code="jajar_legowo",
            normalized_inputs=normalized(config=config),
            config=config,
            store=store,
        )
        assert result.availability is AvailabilityStatus.UNAVAILABLE
        assert result.reason_codes == (ReasonCode.Y_BASE_LOOKUP_MISSING,)
        # The cultivar identity is structurally resolved even when its
        # baseline lookup row is absent; availability still fails closed.
        assert result.exact_cultivar_resolved is True
        assert result.yield_total_kg is None

    def test_missing_factor_only(self, config) -> None:
        store = SyntheticYieldLookupStore(entries=[])
        result = compute_yield(
            variety=SYNTH_VARIETY,
            system_code="jajar_legowo",
            normalized_inputs=normalized(config=config),
            config=config,
            store=store,
        )
        assert result.availability is AvailabilityStatus.UNAVAILABLE
        assert result.reason_codes == (ReasonCode.F_RD_LOOKUP_MISSING,)
        assert result.exact_cultivar_resolved is True


class TestSyntheticSuccessPath:
    def test_multiplication_and_domain_gate_internal(self, config) -> None:
        result = compute_yield(
            variety=SYNTH_VARIETY,
            system_code="jajar_legowo",
            normalized_inputs=normalized(config=config),
            config=config,
            store=SyntheticYieldLookupStore(),
        )
        assert result.availability is AvailabilityStatus.AVAILABLE
        assert result.exact_cultivar_resolved is True
        assert result.baseline_kg_per_are == SYNTH_BASELINE_KG_PER_ARE
        assert result.rice_duck_response_factor == SYNTH_FACTOR
        assert result.yield_kg_per_are == Decimal("54")  # 50 * 1.08
        assert result.yield_total_kg == Decimal("378")   # 54 * 7
        assert result.reason_codes == ()

    def test_out_of_lookup_domain_fails_closed(self, config) -> None:
        """Density 5.5 lies outside the synthetic 2-4 entry: unavailable."""
        result = compute_yield(
            variety=SYNTH_VARIETY,
            system_code="jajar_legowo",
            normalized_inputs=normalized(ducks=55, config=config),
            config=config,
            store=SyntheticYieldLookupStore(),
        )
        assert result.availability is AvailabilityStatus.UNAVAILABLE
        assert result.yield_kg_per_are is None
        assert result.yield_total_kg is None

    def test_unknown_cultivar_in_store_fails_closed(self, config) -> None:
        """Generic input options never masquerade as an exact cultivar."""
        result = compute_yield(
            variety=lookup_repository.get_rice_variety("inpari"),
            system_code="jajar_legowo",
            normalized_inputs=normalized(config=config),
            config=config,
            store=SyntheticYieldLookupStore(),
        )
        assert result.availability is AvailabilityStatus.UNAVAILABLE
        assert result.exact_cultivar_resolved is False
        assert ReasonCode.Y_BASE_LOOKUP_MISSING in result.reason_codes
