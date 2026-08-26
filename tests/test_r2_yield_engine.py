"""Phase 5C: local-group, discrete-node, fail-closed yield lookups."""

from decimal import Decimal

import pytest

from app.data.seed import PARAMETER_REGISTRY
from app.domain.models import (
    AvailabilityStatus,
    ExecutionState,
    LocalCultivarGroup,
    ProvenanceStatus,
    RiceVariety,
)
from app.engines.r2.config import load_default_config
from app.engines.r2.normalization import normalize_inputs
from app.engines.r2.yield_engine import (
    EMPTY_YIELD_LOOKUP_STORE,
    RELEASE_SEMANTICS_FIELD_TRANSPLANTING_HST,
    DiscreteYieldLookupStore,
    EmptyYieldLookupStore,
    FRDEntry,
    YieldBaselineEntry,
    compute_yield,
)
from app.repositories.lookup_repository import lookup_repository
from app.schemas.dss import ReasonCode


def baseline(group=LocalCultivarGroup.SERTANI_GROUP, system="jajar_legowo"):
    return YieldBaselineEntry(
        cultivar_group_code=group, kg_per_are=Decimal("50"),
        moisture_basis="dry", control_condition="rice-only control",
        site="synthetic", season="synthetic", system_scope=system,
        management_context="synthetic test only", source_id="SYNTHETIC",
        source_location="tests/test_r2_yield_engine.py",
        provenance_status=ProvenanceStatus.SYSTEM_DESIGN,
        version="synthetic-v1",
    )


def factor(
    *, group=LocalCultivarGroup.SERTANI_GROUP, system="jajar_legowo",
    density="4", release=30,
    semantics=RELEASE_SEMANTICS_FIELD_TRANSPLANTING_HST,
):
    return FRDEntry(
        cultivar_scope=group, system_scope=system,
        density_are=Decimal(density), release_day=release,
        release_semantics=semantics, factor=Decimal("1.08"),
        treatment_yield=Decimal("54"), control_yield=Decimal("50"),
        yield_unit="kg/are", season="synthetic",
        uncertainty="not applicable; synthetic test", source_id="SYNTHETIC",
        source_location="tests/test_r2_yield_engine.py",
        provenance_status=ProvenanceStatus.SYSTEM_DESIGN,
        supported_domain="exact node only", version="synthetic-v1",
    )


@pytest.fixture(scope="module")
def config():
    return load_default_config()


def normalized(*, density="4", config):
    area = Decimal("7")
    return normalize_inputs(
        land_area_are=area, duck_count=int(area * Decimal(density)),
        p_duck_buy_manual=None, config=config,
    )


def test_production_empty_store_is_fail_closed(config) -> None:
    result = compute_yield(
        variety=lookup_repository.get_rice_variety("sertani"),
        system_code="jajar_legowo",
        normalized_inputs=normalized(config=config), config=config,
    )
    assert isinstance(EMPTY_YIELD_LOOKUP_STORE, EmptyYieldLookupStore)
    assert result.availability is AvailabilityStatus.UNAVAILABLE
    assert result.cultivar_group_code is LocalCultivarGroup.SERTANI_GROUP
    assert result.cultivar_group_resolved is True
    assert result.reason_codes == (
        ReasonCode.Y_BASE_GROUP_LOOKUP_MISSING,
        ReasonCode.F_RD_NODE_MISSING,
    )
    assert result.yield_kg_per_are is result.yield_total_kg is None
    assert PARAMETER_REGISTRY["yield_base_by_cultivar_group"].value is None
    assert PARAMETER_REGISTRY["f_rd_lookup"].value is None


def test_exact_discrete_node_can_execute_only_with_complete_synthetic_records(config) -> None:
    store = DiscreteYieldLookupStore(
        baselines=(baseline(),), response_factors=(factor(),)
    )
    result = compute_yield(
        variety=lookup_repository.get_rice_variety("sertani"),
        system_code="jajar_legowo",
        normalized_inputs=normalized(config=config), config=config, store=store,
    )
    assert result.availability is AvailabilityStatus.AVAILABLE
    assert result.yield_kg_per_are == Decimal("54")
    assert result.yield_total_kg == Decimal("378")


def test_nearby_density_is_not_interpolated_or_selected(config) -> None:
    store = DiscreteYieldLookupStore(
        baselines=(baseline(),), response_factors=(factor(density="3"),)
    )
    result = compute_yield(
        variety=lookup_repository.get_rice_variety("sertani"),
        system_code="jajar_legowo",
        normalized_inputs=normalized(config=config), config=config, store=store,
    )
    assert result.availability is AvailabilityStatus.UNAVAILABLE
    assert result.reason_codes == (ReasonCode.F_RD_NODE_MISSING,)


def test_system_scope_and_release_have_specific_miss_codes(config) -> None:
    store = DiscreteYieldLookupStore(
        baselines=(baseline(),), response_factors=(factor(system="tegel"),)
    )
    result = compute_yield(
        variety=lookup_repository.get_rice_variety("sertani"),
        system_code="jajar_legowo",
        normalized_inputs=normalized(config=config), config=config, store=store,
    )
    assert ReasonCode.F_RD_SYSTEM_SCOPE_UNSUPPORTED in result.reason_codes

    release_store = DiscreteYieldLookupStore(
        baselines=(baseline(),), response_factors=(factor(release=29),)
    )
    result = compute_yield(
        variety=lookup_repository.get_rice_variety("sertani"),
        system_code="jajar_legowo",
        normalized_inputs=normalized(config=config), config=config,
        store=release_store,
    )
    assert result.reason_codes == (ReasonCode.RELEASE_NODE_UNSUPPORTED,)


def test_timing_semantics_and_group_scope_fail_closed(config) -> None:
    timing_store = DiscreteYieldLookupStore(
        baselines=(baseline(),),
        response_factors=(factor(semantics="DAYS_AFTER_DIRECT_SEEDING"),),
    )
    timing = compute_yield(
        variety=lookup_repository.get_rice_variety("sertani"),
        system_code="jajar_legowo",
        normalized_inputs=normalized(config=config), config=config,
        store=timing_store,
    )
    assert timing.reason_codes == (ReasonCode.TIMING_SEMANTICS_UNRESOLVED,)

    group_store = DiscreteYieldLookupStore(
        baselines=(baseline(),),
        response_factors=(factor(group=LocalCultivarGroup.INPARI_GROUP),),
    )
    group = compute_yield(
        variety=lookup_repository.get_rice_variety("sertani"),
        system_code="jajar_legowo",
        normalized_inputs=normalized(config=config), config=config,
        store=group_store,
    )
    assert group.reason_codes == (ReasonCode.F_RD_NODE_MISSING,)


def test_unresolved_group_has_specific_reason(config) -> None:
    unresolved = RiceVariety(
        code="unresolved", label="Unapproved label", harvest_hst_min=100,
        harvest_hst_max=110, calendar_status=ProvenanceStatus.LOCAL_ESTIMATE,
        yield_lookup_status=ExecutionState.PENDING_LOOKUP,
        cultivar_group_code=None,
    )
    result = compute_yield(
        variety=unresolved, system_code="jajar_legowo",
        normalized_inputs=normalized(config=config), config=config,
    )
    assert result.reason_codes[0] is ReasonCode.CULTIVAR_GROUP_UNRESOLVED


def test_none_variety_raises(config) -> None:
    with pytest.raises(ValueError):
        compute_yield(
            variety=None, system_code="jajar_legowo",
            normalized_inputs=normalized(config=config), config=config,
        )
