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
    CULTIVAR_GROUP_UNRESOLVED = "CULTIVAR_GROUP_UNRESOLVED"
    Y_BASE_GROUP_LOOKUP_MISSING = "Y_BASE_GROUP_LOOKUP_MISSING"
    F_RD_NODE_MISSING = "F_RD_NODE_MISSING"
    RELEASE_NODE_UNSUPPORTED = "RELEASE_NODE_UNSUPPORTED"
    F_RD_SYSTEM_SCOPE_UNSUPPORTED = "F_RD_SYSTEM_SCOPE_UNSUPPORTED"
    TIMING_SEMANTICS_UNRESOLVED = "TIMING_SEMANTICS_UNRESOLVED"
    AGE_OUTSIDE_SUPPORTED_DOMAIN = "AGE_OUTSIDE_SUPPORTED_DOMAIN"
    DENSITY_OUTSIDE_SUPPORTED_DOMAIN = "DENSITY_OUTSIDE_SUPPORTED_DOMAIN"
    FRD_REFERENCE_MISSING = "FRD_REFERENCE_MISSING"
    EVIDENCE_DOMAIN_UNSUPPORTED = "EVIDENCE_DOMAIN_UNSUPPORTED"
    FEED_QUANTITY_LOOKUP_MISSING = "FEED_QUANTITY_LOOKUP_MISSING"
    FEED_PRICE_LOOKUP_MISSING = "FEED_PRICE_LOOKUP_MISSING"
    CAGE_CAPACITY_RULE_MISSING = "CAGE_CAPACITY_RULE_MISSING"


NutrientBasis = Literal["N-P2O5-K2O"]
GeometryAssumption = Literal["SQUARE_EQUIVALENT"]
ProfitFullStatus = Literal["UNAVAILABLE_INCOMPLETE_COST"]
HSTOriginSemantics = Literal["FIELD_TRANSPLANTING_DATE"]


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
    planting_date: date = Field(
        description=(
            "Field-transplanting date (ISO) for transplanted rice. All HST "
            "windows are counted from this date; required, no fallback."
        )
    )
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
    - freeze_id:          governance freeze identifier (R2-FREEZE-YYYY-MM-DD.N)

    ``frozen=true`` means "immutable validation target" (docs/11). It does NOT
    mean empirically validated, accurate, or complete; unavailable scientific
    outputs stay unavailable after the freeze.
    """

    model_version: str = "R2"
    history_schema_version: int = 4
    parameter_registry_version: str | None = None
    model_commit_sha: str | None = None
    freeze_id: str | None = None
    # Schema-level default stays conservative (False); the production service
    # always sources this field from app.data.seed.MODEL_FROZEN.
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

    hst_origin_semantics: HSTOriginSemantics = "FIELD_TRANSPLANTING_DATE"
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
    """Range-aware, fail-closed Phase-6 yield group (SSOT section 6)."""

    availability: AvailabilityStatus | None = None
    cultivar_group_code: str | None = None
    cultivar_group_resolved: bool | None = None
    baseline_kg_per_are: float | None = None
    baseline_ref_kg_per_are: float | None = None
    baseline_low_kg_per_are: float | None = None
    baseline_high_kg_per_are: float | None = None
    rice_duck_response_factor: float | None = None
    yield_kg_per_are: float | None = None
    yield_total_kg: float | None = None
    yield_ref_kg_per_are: float | None = None
    yield_low_kg_per_are: float | None = None
    yield_high_kg_per_are: float | None = None
    yield_total_ref_kg: float | None = None
    yield_total_low_kg: float | None = None
    yield_total_high_kg: float | None = None
    yield_range_type: str | None = None
    yield_evidence_status: ProvenanceStatus | None = None
    yield_evidence_strength: str | None = None
    yield_evidence_warning: str | None = None
    yield_source_id: str | None = None
    yield_baseline_source_id: str | None = None
    yield_frd_source_id: str | None = None
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
    paddy_revenue_ref_rp: float | None = None
    paddy_revenue_low_rp: float | None = None
    paddy_revenue_high_rp: float | None = None
    cash_revenue_rp: float | None = None
    cash_revenue_ref_rp: float | None = None
    cash_revenue_low_rp: float | None = None
    cash_revenue_high_rp: float | None = None
    gross_economic_value_rp: float | None = None
    gross_economic_value_ref_rp: float | None = None
    gross_economic_value_low_rp: float | None = None
    gross_economic_value_high_rp: float | None = None
    margin_core_rp: float | None = None
    margin_core_ref_rp: float | None = None
    margin_core_low_rp: float | None = None
    margin_core_high_rp: float | None = None
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
# POST /dss/visualize -- R2 presentation-only contract
# ---------------------------------------------------------------------------


class VisualizationSelectedInput(BaseModel):
    land_area_are: float
    duck_count: int
    planting_date: date
    planting_system: str
    rice_variety: str
    duck_age_days: int
    p_duck_buy_manual: float | None = None
    p_duck_buy_effective: float
    p_duck_buy_source: PurchasePriceSource
    density_are: float


class DensitySupportZone(BaseModel):
    key: str
    label: str
    min: float | None = None
    max: float | None = None
    min_inclusive: bool
    max_inclusive: bool
    status: DensitySupportFlag
    selected_value_in_zone: bool


class AgeSupportZone(BaseModel):
    key: str
    label: str
    min_days: int | None = None
    max_days: int | None = None
    min_inclusive: bool
    max_inclusive: bool
    status: AgeSupportFlag
    selected_value_in_zone: bool


class InfrastructureVisualization(BaseModel):
    availability: Literal["AVAILABLE_RANGE"]
    area_are: float
    equivalent_perimeter_m: float
    cost_min_rp_per_cycle: float
    cost_ref_rp_per_cycle: float
    cost_max_rp_per_cycle: float
    geometry_assumption: GeometryAssumption
    series_semantics: Literal["CALCULATED_REQUEST_RANGE"]


class FertilizerVisualizationComponent(BaseModel):
    key: Literal["NPK_PHONSKA", "UREA"]
    label: str
    quantity_kg: float
    cost_rp: float


class FertilizerVisualization(BaseModel):
    availability: Literal["AVAILABLE"]
    baseline_label: Literal["BASELINE-NO-CREDIT"]
    nutrient_basis: NutrientBasis
    manure_credit_applied: Literal[False]
    components: list[FertilizerVisualizationComponent]
    total_cost_rp: float


class YieldVisualizationPoint(BaseModel):
    """Reserved for a future docs-first sourced yield series.

    Phase 4 production responses always return an empty point list.
    """

    density_are: float
    release_hst: int
    yield_kg_per_are: float


class YieldVisualization(BaseModel):
    availability: AvailabilityStatus
    points: list[YieldVisualizationPoint] = Field(default_factory=list)
    reason_codes: list[ReasonCode] = Field(default_factory=list)
    yield_ref_kg_per_are: float | None = None
    yield_low_kg_per_are: float | None = None
    yield_high_kg_per_are: float | None = None
    yield_range_type: str | None = None
    yield_evidence_strength: str | None = None
    yield_evidence_warning: str | None = None


class FinancialVisualizationKind(str, Enum):
    CASH_REVENUE = "CASH_REVENUE"
    ASSET_VALUE = "ASSET_VALUE"
    COST = "COST"
    AVAILABLE_COST_SUBTOTAL = "AVAILABLE_COST_SUBTOTAL"
    FULL_PROFIT = "FULL_PROFIT"


class FinancialVisualizationNode(BaseModel):
    key: str
    label: str
    kind: FinancialVisualizationKind
    availability: AvailabilityStatus
    amount_rp: float | None = None
    affects_cash_total: bool
    note: str | None = None


class FinancialVisualization(BaseModel):
    availability: Literal["PARTIAL"]
    cost_completeness: CostCompletenessFlag
    nodes: list[FinancialVisualizationNode]


class VisualizationResponse(BaseModel):
    """R2 visualization is a view over a canonical simulation, not an engine."""

    model: ModelMeta
    selected_input: VisualizationSelectedInput
    density_zones: list[DensitySupportZone]
    age_zones: list[AgeSupportZone]
    calendar: CalendarWindow
    infrastructure: InfrastructureVisualization
    fertilizer: FertilizerVisualization
    yield_series: YieldVisualization
    financial_waterfall: FinancialVisualization
    warnings: list[str] = Field(default_factory=list)


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
    "AgeSupportZone",
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
    "DensitySupportZone",
    "DuckOutputs",
    "DuckPurchaseCost",
    "EconomicsOutputs",
    "ExtrapolationFlag",
    "FeedCost",
    "FinancialVisualization",
    "FinancialVisualizationKind",
    "FinancialVisualizationNode",
    "FertilizerBaseline",
    "FertilizerVisualization",
    "FertilizerVisualizationComponent",
    "HistoryListItem",
    "HistoryListResponse",
    "InfrastructureVisualization",
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
    "VisualizationResponse",
    "VisualizationSelectedInput",
    "WeedingCost",
    "YieldOutputs",
    "YieldVisualization",
    "YieldVisualizationPoint",
]
