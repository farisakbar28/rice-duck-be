"""R2 DSS API contracts.

Request/response semantics follow docs/03_R2_API_CONTRACT.md; canonical
values and flags come from docs/01_R2_MODEL_SSOT.md; execution/provenance
dimensions come from docs/04_R2_PARAMETER_EXECUTION_REGISTRY.md.

Design rules:
  * Exactly seven user concepts; ``p_duck_buy`` is optional/nullable.
    Missing or ``null`` means "use the registry default" (resolution happens
    in Phase-2 normalization, not here). A supplied value must be finite
    and > 0 -- numeric 0 is NOT a substitute for missing.
  * Unknown scientific values are ``None`` plus explicit availability /
    reason metadata. No unknown field may require numeric 0.
  * Terminal duck value is never realized sale revenue; full profit is only
    representable when cost completeness is COMPLETE (otherwise null).
  * This module describes API semantics only -- it performs no scientific
    calculation. Numeric population belongs to Phase-2+ engines/services.
  * Pre-R2 flat canonical fields (duck potential-sale revenue, pre-R2 total
    revenue/net-contribution aggregates, fixed-yield predictions, point
    release/pull calendar fields, mandatory numeric feed cost) are
    intentionally absent and must not be re-aliased. The full blacklist is
    docs/07_R2_LEGACY_INVALIDATION_REGISTER.md sections 1-2; the static
    anti-regression test enforces it for this module.
"""

from datetime import date, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.models import (
    AgeSupportFlag,
    AvailabilityStatus,
    ComponentAvailability,
    CostCompletenessFlag,
    DensitySupportFlag,
    ExecutionState,
    ExtrapolationFlag,
    PriceBenchmarkType,
    ProvenanceStatus,
    PurchasePriceSource,
)


# ---------------------------------------------------------------------------
# Shared vocabularies
# ---------------------------------------------------------------------------


class ReasonCode(str, Enum):
    """Explicit machine-readable causes for unavailable numeric outputs.

    Members are limited to causes documented in docs/03_R2_API_CONTRACT.md
    section 4; new codes require a documentation update first.
    """

    Y_BASE_LOOKUP_MISSING = "Y_BASE_LOOKUP_MISSING"
    F_RD_LOOKUP_MISSING = "F_RD_LOOKUP_MISSING"
    FEED_QUANTITY_LOOKUP_MISSING = "FEED_QUANTITY_LOOKUP_MISSING"
    FEED_PRICE_LOOKUP_MISSING = "FEED_PRICE_LOOKUP_MISSING"
    CAGE_CAPACITY_RULE_MISSING = "CAGE_CAPACITY_RULE_MISSING"


NutrientBasis = Literal["N-P2O5-K2O"]
GeometryAssumption = Literal["SQUARE_EQUIVALENT"]
ProfitFullStatus = Literal["UNAVAILABLE_INCOMPLETE_COST"]


# ---------------------------------------------------------------------------
# GET /dss/options
# ---------------------------------------------------------------------------


class RiceVarietyOption(BaseModel):
    """Variety choice + operational metadata (no yield multipliers exposed)."""

    code: str
    label: str
    harvest_hst_min: int
    harvest_hst_max: int
    calendar_status: ProvenanceStatus
    yield_lookup_status: ExecutionState


class PlantingSystemOption(BaseModel):
    code: str
    label: str
    supported_density_min_are: float
    supported_density_max_are: float
    status: ProvenanceStatus


class PurchasePriceOption(BaseModel):
    """Purchase-price input metadata (contract section 2)."""

    optional: bool = True
    default_rp_per_duck: float
    local_range_rp_per_duck: list[float]
    status: ProvenanceStatus


class DSSOptionsResponse(BaseModel):
    model_version: str = "R2"
    rice_varieties: list[RiceVarietyOption]
    planting_systems: list[PlantingSystemOption]
    purchase_price: PurchasePriceOption


# ---------------------------------------------------------------------------
# POST /dss/simulate -- request
# ---------------------------------------------------------------------------


class DSSSimulationRequest(BaseModel):
    """Seven user concepts (contract section 3.1).

    ``p_duck_buy``: omitted/null -> registry default applies later in Phase-2
    normalization; supplied -> must be finite and > 0. Zero is rejected:
    it does not mean "no purchase this cycle".
    """

    model_config = ConfigDict(
        # JSON permits non-finite numeric tokens in some parsers; they do not
        # represent valid production measurements.
        allow_inf_nan=False,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "land_area_are": 7,
                "duck_count": 28,
                "planting_date": "2026-06-01",
                "planting_system": "jajar_legowo",
                "rice_variety": "sertani",
                "duck_age_days": 30,
                "p_duck_buy": None,
            }
        },
    )

    land_area_are: float = Field(gt=0, description="Active duck interaction area in are (> 0).")
    duck_count: int = Field(gt=0, description="Initial duck count (> 0).")
    planting_date: date = Field(description="Planting date (ISO). Required; no fallback.")
    planting_system: str = Field(min_length=1, description="Lookup value ('jajar_legowo' | 'tegel').")
    rice_variety: str = Field(min_length=1, description="Lookup value ('sertani' | 'inpari').")
    duck_age_days: int = Field(gt=0, description="Duck age at release in days (> 0).")
    p_duck_buy: float | None = Field(
        default=None,
        gt=0,
        allow_inf_nan=False,
        description=(
            "Manual duck purchase price (Rp/duck). Optional; missing/null uses "
            "the registry default. Supplied values must be > 0."
        ),
    )


# ---------------------------------------------------------------------------
# POST /dss/simulate -- response semantic groups
# ---------------------------------------------------------------------------


class ModelMeta(BaseModel):
    """Runtime model identity. Distinct concepts kept separate:

    - model_version:      runtime scientific model generation ("R2")
    - history_schema_version: persistence schema of new simulations (4)
    - parameter_registry_version: immutable registry identifier
    - model_commit_sha:   git commit that produced the response (if available)
    """

    model_version: str = "R2"
    history_schema_version: int = 4
    parameter_registry_version: str | None = None
    model_commit_sha: str | None = None
    # Phase 3 runtime is NOT the final model freeze (docs/08 places freeze in
    # the final phase); responses must not claim validation/freeze occurred.
    frozen: bool = False
    generated_at: datetime | None = None


class SimulationInputEcho(BaseModel):
    """Effective input snapshot: manual price, effective price, source are distinct."""

    land_area_are: float
    duck_count: int
    planting_date: date
    planting_system: str
    rice_variety: str
    duck_age_days: int
    p_duck_buy_manual: float | None = None
    p_duck_buy_effective: float | None = None
    p_duck_buy_source: PurchasePriceSource | None = None


class OperationalProfile(BaseModel):
    area_m2: float | None = None
    density_are: float | None = None
    age_support: AgeSupportFlag | None = None
    density_support: DensitySupportFlag | None = None
    extrapolation: ExtrapolationFlag | None = None


class CalendarWindow(BaseModel):
    """Calendar as windows; no false-precision release/pull points."""

    release_hst_min: int | None = None
    release_hst_max: int | None = None
    release_date_min: date | None = None
    release_date_max: date | None = None
    pull_hst_min: int | None = None
    pull_hst_max: int | None = None
    pull_date_min: date | None = None
    pull_date_max: date | None = None
    active_duration_ref_days: int | None = None
    active_duration_support_min_days: int | None = None
    active_duration_support_max_days: int | None = None
    harvest_hst_min: int | None = None
    harvest_hst_max: int | None = None
    harvest_date_min: date | None = None
    harvest_date_max: date | None = None


class DuckOutputs(BaseModel):
    """Biological state separated from sales state (SSOT section 5.1).

    ``sale_quantity`` is a distinct concept from ``surviving_ducks`` and has
    no automatic numeric value. Terminal value is livestock asset value --
    ``terminal_value_is_cash_revenue`` is False by design invariant.
    """

    survival_availability: AvailabilityStatus | None = None
    lambda_eff: float | None = None
    surviving_ducks: int | None = None
    sale_quantity: int | None = None
    sale_quantity_status: AvailabilityStatus | None = None
    terminal_value_ref_rp: float | None = None
    terminal_value_min_rp: float | None = None
    terminal_value_max_rp: float | None = None
    terminal_value_is_cash_revenue: bool = False


class YieldOutputs(BaseModel):
    """Fail-closed yield group (SSOT section 6): null until lookups exist."""

    availability: AvailabilityStatus | None = None
    exact_cultivar_resolved: bool | None = None
    baseline_kg_per_are: float | None = None
    rice_duck_response_factor: float | None = None
    yield_kg_per_are: float | None = None
    yield_total_kg: float | None = None
    reason_codes: list[ReasonCode] = Field(default_factory=list)


class FertilizerBaseline(BaseModel):
    """Baseline-no-credit fertilizer group (SSOT section 7)."""

    availability: AvailabilityStatus | None = None
    nutrient_basis: NutrientBasis | None = None
    manure_credit_applied: bool | None = None
    n_need_kg: float | None = None
    p2o5_need_kg: float | None = None
    k2o_need_kg: float | None = None
    q_npk_kg: float | None = None
    q_urea_kg: float | None = None
    cost_npk_rp: float | None = None
    cost_urea_rp: float | None = None
    cost_total_rp: float | None = None


class DuckPurchaseCost(BaseModel):
    availability: AvailabilityStatus | None = None
    amount_rp: float | None = None


class FeedCost(BaseModel):
    availability: AvailabilityStatus | None = None
    amount_rp: float | None = None
    reason_codes: list[ReasonCode] = Field(default_factory=list)


class NetInfrastructureCost(BaseModel):
    availability: ComponentAvailability | None = None
    equivalent_perimeter_m: float | None = None
    cost_min_rp_per_cycle: float | None = None
    cost_ref_rp_per_cycle: float | None = None
    cost_max_rp_per_cycle: float | None = None
    geometry_assumption: GeometryAssumption | None = None


class CageCost(BaseModel):
    availability: ComponentAvailability | None = None
    cost_per_unit_min_rp_per_cycle: float | None = None
    cost_per_unit_ref_rp_per_cycle: float | None = None
    cost_per_unit_max_rp_per_cycle: float | None = None
    total_amount_rp: float | None = None
    reason_codes: list[ReasonCode] = Field(default_factory=list)


class WeedingCost(BaseModel):
    availability: ComponentAvailability | None = None
    baseline_min_rp: float | None = None
    baseline_max_rp: float | None = None
    saving_rp: float | None = None


class PesticideCost(BaseModel):
    effect: str | None = None
    saving_rp: float | None = None


class CostLedger(BaseModel):
    duck_purchase: DuckPurchaseCost = Field(default_factory=DuckPurchaseCost)
    feed: FeedCost = Field(default_factory=FeedCost)
    net_infrastructure: NetInfrastructureCost = Field(default_factory=NetInfrastructureCost)
    cage: CageCost = Field(default_factory=CageCost)
    weeding: WeedingCost = Field(default_factory=WeedingCost)
    pesticide: PesticideCost = Field(default_factory=PesticideCost)
    cost_core_direct_rp: float | None = None
    cost_total_available_rp: float | None = None
    cost_completeness: CostCompletenessFlag | None = None


class EconomicsOutputs(BaseModel):
    """Conditional economics (SSOT sections 12-13).

    ``profit_full_est_rp`` stays null unless every ledger component required
    by the configured full ledger is available (cost_completeness=COMPLETE).
    """

    paddy_price_benchmark_rp_per_kg: float | None = None
    paddy_price_semantics: PriceBenchmarkType | None = None
    paddy_revenue_rp: float | None = None
    cash_revenue_rp: float | None = None
    gross_economic_value_rp: float | None = None
    margin_core_rp: float | None = None
    profit_full_est_rp: float | None = None
    profit_full_status: ProfitFullStatus | None = None


class ReliabilitySummary(BaseModel):
    """Canonical reliability flags (SSOT section 14); mirrors key groups."""

    yield_availability: AvailabilityStatus | None = None
    survival_availability: AvailabilityStatus | None = None
    feed_cost_availability: AvailabilityStatus | None = None
    cost_completeness: CostCompletenessFlag | None = None
    extrapolation: ExtrapolationFlag | None = None


class DefaultedInputRecord(BaseModel):
    """Record of an input silently resolved to a default (persistence doc section 5)."""

    field: str
    resolved_value: float | int | str | None = None
    source: str | None = None
    status_tag: ProvenanceStatus | None = None


class TraceMeta(BaseModel):
    """Formula/source trace (contract section 4, persistence doc section 5).

    ``availability_reasons`` maps response group paths to the explicit machine
    reason codes that explain a null/unavailable numeric output. It carries
    only codes actually emitted by engines -- never fabricated entries.
    """

    active_formula_ids: list[str] = Field(default_factory=list)
    conditional_formula_ids: list[str] = Field(default_factory=list)
    disabled_legacy_formula_ids: list[str] = Field(default_factory=list)
    parameter_sources: dict[str, object] = Field(default_factory=dict)
    lookup_versions: dict[str, object] = Field(default_factory=dict)
    regulation_versions: dict[str, object] = Field(default_factory=dict)
    defaulted_inputs: list[DefaultedInputRecord] = Field(default_factory=list)
    availability_reasons: dict[str, list[str]] = Field(default_factory=dict)


class DSSSimulationResponse(BaseModel):
    """Canonical R2 simulation response (contract section 4).

    Every scientific/economic subgroup is present but individually nullable;
    all groups can serialize with unavailable numerics as JSON null.
    The yield group is serialized under the JSON key ``yield`` (Python
    attribute ``crop_yield`` because ``yield`` is a reserved keyword).
    """

    model_config = ConfigDict(populate_by_name=True)

    model: ModelMeta = Field(default_factory=ModelMeta)
    input: SimulationInputEcho
    operational: OperationalProfile = Field(default_factory=OperationalProfile)
    calendar: CalendarWindow = Field(default_factory=CalendarWindow)
    duck: DuckOutputs = Field(default_factory=DuckOutputs)
    crop_yield: YieldOutputs = Field(default_factory=YieldOutputs, alias="yield")
    fertilizer_baseline: FertilizerBaseline = Field(default_factory=FertilizerBaseline)
    costs: CostLedger = Field(default_factory=CostLedger)
    economics: EconomicsOutputs = Field(default_factory=EconomicsOutputs)
    reliability: ReliabilitySummary = Field(default_factory=ReliabilitySummary)
    warnings: list[str] = Field(default_factory=list)
    trace: TraceMeta = Field(default_factory=TraceMeta)


# ---------------------------------------------------------------------------
# History (persistence v4) -- list/delete contracts (docs/05 sections 3/7)
# ---------------------------------------------------------------------------


class R2HistorySummary(BaseModel):
    """Indexed summary fields of a stored schema-v4 simulation snapshot.

    Mirrors the ``dss_simulation_histories_r2`` index columns; the semantic
    truth of every simulation remains its stored response snapshot.
    Unknown scientific outputs stay null here as well.
    """

    land_area_are: float
    duck_count: int
    rice_variety: str
    planting_system: str
    duck_age_days: int
    planting_date: date
    p_duck_buy_effective: float
    density_are: float
    age_support: AgeSupportFlag
    density_support: DensitySupportFlag
    extrapolation_status: ExtrapolationFlag
    yield_availability: AvailabilityStatus
    survival_availability: AvailabilityStatus
    cost_completeness: CostCompletenessFlag
    yield_total_kg: float | None = None
    margin_core_rp: float | None = None
    profit_full_est_rp: float | None = None


class HistoryListItem(BaseModel):
    """One history row in the merged list.

    ``model_version`` distinguishes canonical R2 rows ("R2") from immutable
    pre-R2 records ("LEGACY", schema_version <= 3). Legacy items expose only
    identity/version/timestamp metadata -- no scientific values are
    synthesized or re-labeled for them (docs/05 section 7).
    """

    id: str
    model_version: str
    schema_version: int
    created_at: datetime
    r2_summary: R2HistorySummary | None = None


class HistoryListResponse(BaseModel):
    data: list[HistoryListItem]


class DeleteHistoryResponse(BaseModel):
    message: str


__all__ = [
    "AgeSupportFlag",
    "AvailabilityStatus",
    "CageCost",
    "CalendarWindow",
    "ComponentAvailability",
    "CostCompletenessFlag",
    "CostLedger",
    "DeleteHistoryResponse",
    "DSSOptionsResponse",
    "DSSSimulationRequest",
    "DSSSimulationResponse",
    "DefaultedInputRecord",
    "DensitySupportFlag",
    "DuckOutputs",
    "DuckPurchaseCost",
    "EconomicsOutputs",
    "ExtrapolationFlag",
    "FeedCost",
    "FertilizerBaseline",
    "HistoryListItem",
    "HistoryListResponse",
    "ModelMeta",
    "NetInfrastructureCost",
    "OperationalProfile",
    "PesticideCost",
    "PlantingSystemOption",
    "PriceBenchmarkType",
    "ProvenanceStatus",
    "PurchasePriceOption",
    "PurchasePriceSource",
    "R2HistorySummary",
    "ReasonCode",
    "ReliabilitySummary",
    "RiceVarietyOption",
    "SimulationInputEcho",
    "TraceMeta",
    "WeedingCost",
    "YieldOutputs",
]
