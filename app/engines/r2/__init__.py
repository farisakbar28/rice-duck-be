"""R2 pure engines (Phase 2).

This package implements the canonical R2 scientific/economic engines as
pure, deterministic functions over Decimal values:

    normalization  -> area/density/price resolution
    support        -> age + density support classifiers, operational extrapolation
    calendar       -> release/pull/harvest windows and active duration
    survival       -> gated lambda=0.90 estimate and surviving ducks
    yield_engine   -> fail-closed lookup interface (empty production store)
    fertilizer     -> N-P2O5-K2O baseline-no-credit + urea/NPK optimum
    infrastructure -> square-equivalent net range + cage partial range
    availability   -> feed/weeding/pest availability semantics
    economics      -> conditional economic ledger

Boundary rules:
  * Engines import ONLY stdlib, ``app.domain.models``, ``app.data.seed``
    (config factory), and the canonical reason-code vocabulary from
    ``app.schemas.dss``. The static suite enforces this whitelist.
  * No engine imports or reimplements the invalidated legacy engine modules.
  * All constants come from ``R2EngineConfig`` built from the canonical R2
    registry; no scientific magic numbers live in engine bodies.
"""

from __future__ import annotations

# Canonical formula-ID trace map (docs/04 section 2), consumed by Phase-3
# orchestration to populate response trace metadata.
FORMULA_IDS: dict[str, tuple[str, ...]] = {
    "normalization": ("R2-NORM-01", "R2-DEN-01", "R2-PRICE-01"),
    "age_support": ("R2-AGE-01",),
    "density_support": ("R2-DEN-02",),
    "calendar": ("R2-CAL-01", "R2-CAL-02", "R2-CAL-03", "R2-CAL-04", "R2-CAL-05"),
    "survival": ("R2-SURV-01", "R2-SURV-02", "R2-SURV-03"),
    "yield": ("R2-YLD-01", "R2-YLD-02"),
    "fertilizer": (
        "R2-NUT-01",
        "R2-NUT-02",
        "R2-NUT-03",
        "R2-NUT-04",
        "R2-FERT-01",
        "R2-FERT-02",
        "R2-FERT-03",
    ),
    "infrastructure_net": ("R2-INF-01", "R2-INF-02", "R2-INF-03", "R2-INF-04"),
    "infrastructure_cage": ("R2-CAGE-01",),
    "feed": (),
    "weeding": ("R2-WEED-01",),
    "pest": ("R2-PEST-01",),
    "economics": (
        "R2-COST-01",
        "R2-GRAIN-01",
        "R2-GRAIN-02",
        "R2-DUCKVAL-01",
        "R2-LEDGER-01",
        "R2-LEDGER-02",
        "R2-LEDGER-03",
        "R2-LEDGER-04",
        "R2-LEDGER-05",
        "R2-LEDGER-06",
    ),
}

from app.engines.r2.availability import (  # noqa: E402
    FeedResult,
    PestResult,
    WeedingResult,
    compute_feed_cost,
    compute_pest_effect,
    compute_weeding_baseline,
)
from app.engines.r2.calendar import CalendarWindows, compute_calendar_windows  # noqa: E402
from app.engines.r2.config import R2EngineConfig, load_default_config  # noqa: E402
from app.engines.r2.economics import (  # noqa: E402
    EconomicLedgerResult,
    PROFIT_FULL_STATUS_INCOMPLETE,
    compute_economic_ledger,
)
from app.engines.r2.fertilizer import FertilizerResult, compute_fertilizer_baseline  # noqa: E402
from app.engines.r2.infrastructure import (  # noqa: E402
    CageInfrastructureResult,
    InfrastructureResult,
    NetInfrastructureResult,
    compute_infrastructure,
)
from app.engines.r2.normalization import (  # noqa: E402
    NormalizedInputs,
    normalize_cultivar_group_label,
    normalize_inputs,
)
from app.engines.r2.support import (  # noqa: E402
    SupportInterval,
    age_support_intervals,
    classify_age,
    classify_density,
    density_support_intervals,
    operational_extrapolation,
)
from app.engines.r2.survival import SurvivalResult, compute_survival  # noqa: E402
from app.engines.r2.yield_engine import (  # noqa: E402
    EMPTY_YIELD_LOOKUP_STORE,
    DiscreteYieldLookupStore,
    EmptyYieldLookupStore,
    FRDEntry,
    YieldBaselineEntry,
    YieldLookupStore,
    YieldResult,
    RELEASE_SEMANTICS_FIELD_TRANSPLANTING_HST,
    compute_yield,
)

__all__ = [
    "EMPTY_YIELD_LOOKUP_STORE",
    "FORMULA_IDS",
    "PROFIT_FULL_STATUS_INCOMPLETE",
    "CalendarWindows",
    "CageInfrastructureResult",
    "EconomicLedgerResult",
    "EmptyYieldLookupStore",
    "DiscreteYieldLookupStore",
    "FRDEntry",
    "FeedResult",
    "FertilizerResult",
    "InfrastructureResult",
    "NetInfrastructureResult",
    "NormalizedInputs",
    "PestResult",
    "R2EngineConfig",
    "SurvivalResult",
    "SupportInterval",
    "WeedingResult",
    "YieldBaselineEntry",
    "YieldLookupStore",
    "YieldResult",
    "RELEASE_SEMANTICS_FIELD_TRANSPLANTING_HST",
    "age_support_intervals",
    "classify_age",
    "classify_density",
    "density_support_intervals",
    "compute_calendar_windows",
    "compute_economic_ledger",
    "compute_feed_cost",
    "compute_fertilizer_baseline",
    "compute_infrastructure",
    "normalize_cultivar_group_label",
    "compute_pest_effect",
    "compute_survival",
    "compute_weeding_baseline",
    "compute_yield",
    "load_default_config",
    "normalize_inputs",
    "operational_extrapolation",
]
