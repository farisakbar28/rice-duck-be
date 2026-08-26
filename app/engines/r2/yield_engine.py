"""R2 yield engine -- fail-closed lookup interface (registry R2-YLD-01/02).

Structural formula:
    Yield_are_ref = Y_base(V_exact) * F_RD_lookup(d, release_ref)
    Yield_total   = Yield_are_ref * A_are

Availability gate (SSOT section 6): numeric yield is AVAILABLE only when
  1. the exact cultivar is resolved,
  2. a traceable Y_base entry exists for it,
  3. a traceable F_RD entry exists for the requested point, and
  4. the requested point is inside the F_RD supported domain.

Production default is ``EMPTY_YIELD_LOOKUP_STORE``: every query misses, so
the engine returns UNAVAILABLE with explicit reason codes and null numerics.
There is no fallback constant of any kind. Synthetic stores exist ONLY in
tests; none may ship in production seed or production wiring.

Reason-code mapping note: a point outside every supplied F_RD domain has no
valid literature entry for that point and therefore fails closed with
F_RD_LOOKUP_MISSING (documented mapping; a dedicated out-of-domain reason
code would require a docs-first contract update).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from app.domain.models import AvailabilityStatus, RiceVariety
from app.engines.r2.common import high_precision, to_decimal
from app.engines.r2.config import R2EngineConfig
from app.engines.r2.normalization import NormalizedInputs
from app.schemas.dss import ReasonCode


@dataclass(frozen=True)
class YieldBaselineEntry:
    """Exact-cultivar baseline lookup row (kg per are)."""

    exact_cultivar_code: str
    kg_per_are: Decimal
    source_id: str
    version: str


@dataclass(frozen=True)
class FRDEntry:
    """Rice-duck response-factor lookup row over an explicit density domain."""

    system_code: str
    d_min_are: Decimal
    d_max_are: Decimal
    factor: Decimal
    source_id: str
    version: str


class YieldLookupStore(Protocol):
    """Read interface for sourced yield lookups (injected; never global)."""

    def find_baseline(self, exact_cultivar_code: str) -> YieldBaselineEntry | None: ...

    def find_response_factor(
        self,
        *,
        system_code: str,
        density_are: Decimal,
        release_hst_ref: int,
    ) -> FRDEntry | None: ...


class EmptyYieldLookupStore:
    """Production default store: PENDING_LOOKUP for every query."""

    def find_baseline(self, exact_cultivar_code: str) -> YieldBaselineEntry | None:
        return None

    def find_response_factor(
        self,
        *,
        system_code: str,
        density_are: Decimal,
        release_hst_ref: int,
    ) -> FRDEntry | None:
        return None


EMPTY_YIELD_LOOKUP_STORE = EmptyYieldLookupStore()


@dataclass(frozen=True)
class YieldResult:
    availability: AvailabilityStatus
    exact_cultivar_resolved: bool
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
            "Rice variety lookup unresolved; exact-cultivar yield cannot be "
            "evaluated without a resolved cultivar code."
        )

    # Generic API options (for example ``inpari``) do not prove exact
    # cultivar identity. Baseline presence must never flip this flag by
    # coincidence; an explicit exact-cultivar code is required first.
    exact_cultivar_code = variety.exact_cultivar_code
    baseline = (
        store.find_baseline(exact_cultivar_code)
        if exact_cultivar_code is not None
        else None
    )
    factor_entry = store.find_response_factor(
        system_code=system_code,
        density_are=normalized_inputs.density_are,
        release_hst_ref=config.f_rd_release_ref_hst,
    )

    missing: list[ReasonCode] = []
    if baseline is None:
        missing.append(ReasonCode.Y_BASE_LOOKUP_MISSING)
    if factor_entry is None:
        missing.append(ReasonCode.F_RD_LOOKUP_MISSING)

    if missing:
        # Fail closed: no numeric output while any required piece is absent.
        return YieldResult(
            availability=AvailabilityStatus.UNAVAILABLE,
            exact_cultivar_resolved=exact_cultivar_code is not None,
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
        exact_cultivar_resolved=True,
        baseline_kg_per_are=baseline.kg_per_are,
        rice_duck_response_factor=factor_entry.factor,
        yield_kg_per_are=yield_are,
        yield_total_kg=yield_total,
        reason_codes=(),
    )
