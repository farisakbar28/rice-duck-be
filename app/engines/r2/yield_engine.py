"""R2 yield engine -- fail-closed lookup interface (registry R2-YLD-01/02).

Structural formula:
    Yield_are_ref = Y_base(local_group) * F_RD_exact_node(system,d,release_ref)
    Yield_total   = Yield_are_ref * A_are

Availability gate (SSOT section 6): numeric yield is AVAILABLE only when
  1. the approved local cultivar group is resolved,
  2. a traceable Y_base entry exists for that group/system scope,
  3. a traceable F_RD entry exists for the requested point, and
  4. the requested point is inside the F_RD supported domain.

Production default is ``EMPTY_YIELD_LOOKUP_STORE``: every query misses, so
the engine returns UNAVAILABLE with explicit reason codes and null numerics.
There is no fallback constant of any kind. Synthetic stores exist ONLY in
tests; none may ship in production seed or production wiring.

All lookups are exact-node and discrete. There is no interpolation,
extrapolation, nearest-neighbour, density-band, release, or system fallback.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from app.domain.models import AvailabilityStatus, LocalCultivarGroup, ProvenanceStatus, RiceVariety
from app.engines.r2.common import high_precision, to_decimal
from app.engines.r2.config import R2EngineConfig
from app.engines.r2.normalization import NormalizedInputs
from app.schemas.dss import ReasonCode


@dataclass(frozen=True)
class YieldBaselineEntry:
    """Future-ready local cultivar-group baseline row (kg per are)."""

    cultivar_group_code: LocalCultivarGroup
    kg_per_are: Decimal
    moisture_basis: str
    control_condition: str
    site: str
    season: str
    system_scope: str
    management_context: str
    source_id: str
    source_location: str
    provenance_status: ProvenanceStatus
    version: str

    def __post_init__(self) -> None:
        if self.kg_per_are <= 0:
            raise ValueError("Baseline kg_per_are must be positive")
        for field_name in (
            "moisture_basis", "control_condition", "site", "season",
            "system_scope", "management_context", "source_id",
            "source_location", "version",
        ):
            if not getattr(self, field_name).strip():
                raise ValueError(f"Baseline {field_name} must be non-empty")


@dataclass(frozen=True)
class FRDEntry:
    """Future-ready response row for one explicit discrete treatment node."""

    cultivar_scope: LocalCultivarGroup
    system_scope: str
    density_are: Decimal
    release_day: int
    release_semantics: str
    factor: Decimal
    treatment_yield: Decimal
    control_yield: Decimal
    yield_unit: str
    season: str
    uncertainty: str
    source_id: str
    source_location: str
    provenance_status: ProvenanceStatus
    supported_domain: str
    version: str

    def __post_init__(self) -> None:
        if self.density_are <= 0 or self.release_day < 0:
            raise ValueError("F_RD density must be positive and release non-negative")
        if self.factor <= 0 or self.control_yield <= 0 or self.treatment_yield <= 0:
            raise ValueError("F_RD factor and yields must be positive")
        if self.factor != self.treatment_yield / self.control_yield:
            raise ValueError("F_RD factor must equal treatment_yield/control_yield")
        for field_name in (
            "system_scope", "release_semantics", "yield_unit", "season",
            "uncertainty", "source_id", "source_location",
            "supported_domain", "version",
        ):
            if not getattr(self, field_name).strip():
                raise ValueError(f"F_RD {field_name} must be non-empty")


RELEASE_SEMANTICS_FIELD_TRANSPLANTING_HST = "HST_FROM_FIELD_TRANSPLANTING"


class YieldLookupStore(Protocol):
    """Read interface for sourced yield lookups (injected; never global)."""

    def find_baseline(
        self, cultivar_group_code: LocalCultivarGroup, system_scope: str
    ) -> YieldBaselineEntry | None: ...

    def find_response_factor(
        self,
        *,
        system_code: str,
        cultivar_group_code: LocalCultivarGroup | None,
        density_are: Decimal,
        release_hst_ref: int,
    ) -> FRDEntry | None: ...

    def diagnose_response_miss(
        self, *, system_code: str, release_hst_ref: int
    ) -> ReasonCode: ...


class EmptyYieldLookupStore:
    """Production default store: PENDING_LOOKUP for every query."""

    def find_baseline(
        self, cultivar_group_code: LocalCultivarGroup, system_scope: str
    ) -> YieldBaselineEntry | None:
        return None

    def find_response_factor(
        self,
        *,
        system_code: str,
        cultivar_group_code: LocalCultivarGroup | None,
        density_are: Decimal,
        release_hst_ref: int,
    ) -> FRDEntry | None:
        return None

    def diagnose_response_miss(
        self, *, system_code: str, release_hst_ref: int
    ) -> ReasonCode:
        return ReasonCode.F_RD_NODE_MISSING


class DiscreteYieldLookupStore:
    """Validation/test store implementing exact equality and no fallback."""

    def __init__(
        self,
        *,
        baselines: tuple[YieldBaselineEntry, ...] = (),
        response_factors: tuple[FRDEntry, ...] = (),
    ) -> None:
        self._baselines = baselines
        self._response_factors = response_factors

    def find_baseline(
        self, cultivar_group_code: LocalCultivarGroup, system_scope: str
    ) -> YieldBaselineEntry | None:
        matches = [
            row for row in self._baselines
            if row.cultivar_group_code is cultivar_group_code
            and row.system_scope == system_scope
        ]
        if len(matches) > 1:
            raise ValueError("Duplicate exact baseline lookup node")
        return matches[0] if matches else None

    def find_response_factor(
        self,
        *,
        system_code: str,
        cultivar_group_code: LocalCultivarGroup | None,
        density_are: Decimal,
        release_hst_ref: int,
    ) -> FRDEntry | None:
        matches = [
            row for row in self._response_factors
            if row.system_scope == system_code
            and row.cultivar_scope is cultivar_group_code
            and row.density_are == density_are
            and row.release_day == release_hst_ref
        ]
        if len(matches) > 1:
            raise ValueError("Duplicate exact F_RD lookup node")
        return matches[0] if matches else None

    def diagnose_response_miss(
        self, *, system_code: str, release_hst_ref: int
    ) -> ReasonCode:
        system_rows = [
            row for row in self._response_factors
            if row.system_scope == system_code
        ]
        if self._response_factors and not system_rows:
            return ReasonCode.F_RD_SYSTEM_SCOPE_UNSUPPORTED
        if system_rows and not any(
            row.release_day == release_hst_ref for row in system_rows
        ):
            return ReasonCode.RELEASE_NODE_UNSUPPORTED
        return ReasonCode.F_RD_NODE_MISSING


EMPTY_YIELD_LOOKUP_STORE = EmptyYieldLookupStore()


@dataclass(frozen=True)
class YieldResult:
    availability: AvailabilityStatus
    cultivar_group_code: LocalCultivarGroup | None
    cultivar_group_resolved: bool
    baseline_kg_per_are: Decimal | None
    rice_duck_response_factor: Decimal | None
    yield_kg_per_are: Decimal | None
    yield_total_kg: Decimal | None
    reason_codes: tuple[ReasonCode, ...] = ()


def compute_yield(
    *,
    variety: RiceVariety | None,
    system_code: str,
    normalized_inputs: NormalizedInputs,
    config: R2EngineConfig,
    store: YieldLookupStore = EMPTY_YIELD_LOOKUP_STORE,
) -> YieldResult:
    if variety is None:
        raise ValueError(
            "Rice variety lookup unresolved; local-group yield cannot be "
            "evaluated without a resolved public variety."
        )

    cultivar_group_code = variety.cultivar_group_code
    baseline = (
        store.find_baseline(cultivar_group_code, system_code)
        if cultivar_group_code is not None
        else None
    )
    factor_entry = store.find_response_factor(
        system_code=system_code,
        cultivar_group_code=cultivar_group_code,
        density_are=normalized_inputs.density_are,
        release_hst_ref=config.f_rd_release_ref_hst,
    )

    missing: list[ReasonCode] = []
    if cultivar_group_code is None:
        missing.append(ReasonCode.CULTIVAR_GROUP_UNRESOLVED)
    if baseline is None:
        missing.append(ReasonCode.Y_BASE_GROUP_LOOKUP_MISSING)
    if factor_entry is None:
        missing.append(store.diagnose_response_miss(
            system_code=system_code,
            release_hst_ref=config.f_rd_release_ref_hst,
        ))
    elif factor_entry.release_semantics != RELEASE_SEMANTICS_FIELD_TRANSPLANTING_HST:
        missing.append(ReasonCode.TIMING_SEMANTICS_UNRESOLVED)

    if missing:
        # Fail closed: no numeric output while any required piece is absent.
        return YieldResult(
            availability=AvailabilityStatus.UNAVAILABLE,
            cultivar_group_code=cultivar_group_code,
            cultivar_group_resolved=cultivar_group_code is not None,
            baseline_kg_per_are=None,
            rice_duck_response_factor=None,
            yield_kg_per_are=None,
            yield_total_kg=None,
            reason_codes=tuple(missing),
        )

    assert baseline is not None and factor_entry is not None  # narrowed above
    with high_precision():
        yield_are = baseline.kg_per_are * factor_entry.factor
        yield_total = yield_are * to_decimal(normalized_inputs.land_area_are)

    return YieldResult(
        availability=AvailabilityStatus.AVAILABLE,
        cultivar_group_code=cultivar_group_code,
        cultivar_group_resolved=True,
        baseline_kg_per_are=baseline.kg_per_are,
        rice_duck_response_factor=factor_entry.factor,
        yield_kg_per_are=yield_are,
        yield_total_kg=yield_total,
        reason_codes=(),
    )
