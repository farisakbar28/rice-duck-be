"""Pydantic contracts for Model A DSS Core."""
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Any, Literal
from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, Field, StrictInt, WithJsonSchema, model_validator


def _require_json_number(value: Any) -> Any:
    """Reject string coercion while preserving Decimal arithmetic internally."""
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise ValueError("must be a JSON number, not a string or boolean")
    return value


JsonNumber = Annotated[
    Decimal,
    BeforeValidator(_require_json_number),
    WithJsonSchema({"type": "number"}, mode="validation"),
]


def _require_positive(value: Decimal) -> Decimal:
    if value <= 0:
        raise ValueError("must be greater than zero")
    return value


def _require_non_negative(value: Decimal) -> Decimal:
    if value < 0:
        raise ValueError("must be greater than or equal to zero")
    return value


JsonPositiveNumber = Annotated[
    Decimal,
    BeforeValidator(_require_json_number),
    AfterValidator(_require_positive),
    WithJsonSchema({"type": "number", "exclusiveMinimum": 0}, mode="validation"),
]
JsonNonNegativeNumber = Annotated[
    Decimal,
    BeforeValidator(_require_json_number),
    AfterValidator(_require_non_negative),
    WithJsonSchema({"type": "number", "minimum": 0}, mode="validation"),
]

class RiceVarietyOption(BaseModel):
    code: str; label: str; risk_note: str; status: str
class PlantingSystemOption(BaseModel):
    code: str; label: str; recommended_density_max_are: float; recommended_density_min_are: float; note: str
class DSSOptionsResponse(BaseModel):
    rice_varieties: list[RiceVarietyOption]; planting_systems: list[PlantingSystemOption]

class DSSSimulationRequest(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False, json_schema_extra={"example":{"land_area_are":10,"duck_count":40,"rice_variety":"sertani","planting_system":"jajar_legowo","duck_age_days":21,"literature_duration_days":50}})
    land_area_are: JsonPositiveNumber = Field(description="Active duck-access area in are; required JSON number greater than zero.")
    duck_count: StrictInt = Field(ge=0, description="Required non-negative integer count of released ducks; Model A accepts zero and does not coerce strings or decimal numbers.")
    rice_variety: str = Field(min_length=1, description="Reference code: sertani or inpari.")
    planting_system: str = Field(min_length=1, description="Reference code: jajar_legowo or tegel.")
    duck_age_days: StrictInt = Field(ge=0, description="Required non-negative integer age in days; it is an information status input, not an economic multiplier, and does not coerce strings or decimal numbers.")
    planting_date: date | None = Field(default=None, description="Optional calendar anchor; dates are unavailable when omitted.")
    p_gabah: JsonNonNegativeNumber | None = Field(default=None, description="Optional runtime rice price as a JSON number; otherwise local-estimate fallback applies.")
    p_duck_buy: JsonNonNegativeNumber | None = Field(default=None, description="Optional runtime duck purchase price as a JSON number; otherwise local-estimate fallback applies.")
    p_duck_sell: JsonNonNegativeNumber | None = Field(default=None, description="Optional all-sold scenario price as a JSON number; otherwise local-estimate fallback applies.")
    literature_duration_days: JsonNumber | None = Field(default=None, description="Optional technical Xiong JSON-number input; yield abstains when omitted or outside the 50-80 day domain.")
    c_feed_scenario: JsonNonNegativeNumber | None = Field(default=None, description="Optional total JSON-number feed cost for the selected cycle scenario. It is not multiplied by duck_count and is unavailable when omitted.")
    c_jaring_purchase: JsonNonNegativeNumber | None = Field(default=None, description="Optional JSON-number net/jaring purchase cost. When supplied, n_jaring_cycles must also be supplied and greater than zero.")
    n_jaring_cycles: JsonPositiveNumber | None = Field(default=None, description="Optional positive JSON-number allocation denominator for c_jaring_purchase; used only when the purchase cost is selected.")
    c_kandang_purchase: JsonNonNegativeNumber | None = Field(default=None, description="Optional JSON-number cage/kandang purchase cost. When supplied, n_kandang_cycles must also be supplied and greater than zero.")
    n_kandang_cycles: JsonPositiveNumber | None = Field(default=None, description="Optional positive JSON-number allocation denominator for c_kandang_purchase; used only when the purchase cost is selected.")
    @model_validator(mode="after")
    def validate_cost_pairs(self):
        if self.c_jaring_purchase is not None and self.n_jaring_cycles is None: raise ValueError("n_jaring_cycles is required when c_jaring_purchase is supplied")
        if self.c_kandang_purchase is not None and self.n_kandang_cycles is None: raise ValueError("n_kandang_cycles is required when c_kandang_purchase is supplied")
        return self

class DSSSimulationResponse(BaseModel):
    """Canonical strict-separation DTO; unavailable scientific values are null."""

    model_config = ConfigDict(json_schema_extra={"example": {
        "model_variant": "A_STRICT_SEPARATION", "age_status": "LOCAL_READY",
        "density_are": 4.0, "density_ha": 400.0, "density_status": "RECOMMENDED",
        "release_hst_min": 21, "release_hst_max": 30, "withdraw_hst_min": 56, "withdraw_hst_max": 60,
        "release_date_min": None, "release_date_max": None, "withdraw_date_min": None, "withdraw_date_max": None,
        "survival_risk": None, "yield_status": "OUTSIDE_LITERATURE_DOMAIN", "yield_are_kg": None,
        "yield_total_kg": None, "revenue_gabah": None, "revenue_duck_all_sold_scenario": 1800000.0,
        "cost_duck_buy": 1000000.0, "cost_feed_scenario": None, "cost_infra_cycle": None,
        "cash_contribution_before_optional": None, "cash_contribution_after_optional": None,
        "warnings": ["literature_duration_days was not supplied"],
        "provenance": {"yield": {"source": "Xiong et al. (2014)", "status": "literature-uncalibrated", "reason": "literature_duration_days was not supplied"}}
    }})

    model_variant: Literal["A_STRICT_SEPARATION"] = Field(default="A_STRICT_SEPARATION", description="Fixed canonical response variant for Model A strict separation.")
    age_status: str = Field(description="Informational readiness status: NOT_RECOMMENDED (<21), LOCAL_READY (21-30), or OLDER_CONSERVATIVE (>30); never a yield/economic multiplier.")
    density_are: float = Field(description="Duck density J/A in ducks per are.")
    density_ha: float = Field(description="Duck density converted as 100 * density_are in ducks per hectare.")
    density_status: str = Field(description="Density zone: UNDER, RECOMMENDED, WARNING_ABOVE_RECOMMENDED, or HIGH_RISK.")
    release_hst_min: int = Field(description="Earliest canonical release day after planting: 21 HST.")
    release_hst_max: int = Field(description="Latest canonical release day after planting: 30 HST.")
    withdraw_hst_min: int = Field(description="Earliest canonical withdrawal day after planting: 56 HST.")
    withdraw_hst_max: int = Field(description="Latest canonical withdrawal day after planting: 60 HST.")
    release_date_min: date | None = Field(description="Calendar release lower bound, or null when planting_date is omitted.")
    release_date_max: date | None = Field(description="Calendar release upper bound, or null when planting_date is omitted.")
    withdraw_date_min: date | None = Field(description="Calendar withdrawal lower bound, or null when planting_date is omitted.")
    withdraw_date_max: date | None = Field(description="Calendar withdrawal upper bound, or null when planting_date is omitted.")
    survival_risk: str | None = Field(description="HIGH only when density_are > 8; null otherwise. This is a risk status, never a numerical survival prediction.")
    yield_status: str = Field(description="VALID only inside the Xiong literature domain; otherwise OUTSIDE_LITERATURE_DOMAIN and numerical yield fields are null.")
    yield_are_kg: float | None = Field(description="Xiong literature-uncalibrated yield in kg/are, or null outside its valid density/duration domain.")
    yield_total_kg: float | None = Field(description="yield_are_kg * land_area_are, or null whenever numerical Xiong yield is unavailable.")
    revenue_gabah: float | None = Field(description="Scenario rice revenue from numerical yield and p_gabah, or null when yield is unavailable.")
    revenue_duck_all_sold_scenario: float | None = Field(description="All-sold duck revenue scenario J * p_duck_sell; null above density_are 8 because survival is not modelled there.")
    cost_duck_buy: float | None = Field(description="Scenario duck purchase cost J * p_duck_buy; it is not a survival-adjusted value.")
    cost_feed_scenario: float | None = Field(description="Optional total feed scenario cost exactly as supplied; null when the optional scenario is not selected.")
    cost_infra_cycle: float | None = Field(description="Optional amortized infrastructure cycle cost from supplied purchase/positive-denominator pairs; null when not selected.")
    cash_contribution_before_optional: float | None = Field(description="Conditional scenario cash contribution before optional feed/infrastructure; not accounting profit or realized farmer profit.")
    cash_contribution_after_optional: float | None = Field(description="Conditional scenario cash contribution after selected optional costs; null when no optional scenario cost is selected or prerequisites are unavailable.")
    warnings: list[str] = Field(description="Scientific availability, readiness, or high-risk warnings; warnings do not fabricate unavailable values.")
    provenance: dict[str, Any] = Field(description="Source/provenance for Xiong status, runtime versus local-estimate prices, and non-numerical survival semantics.")

class HistorySummary(BaseModel): rice_variety: str; planting_system: str; duck_count: int; land_area_are: float; density_are: float; yield_status: str
class HistoryListItem(BaseModel): id: str; schema_version: int; created_at: datetime; summary: HistorySummary
class HistoryListResponse(BaseModel): data: list[HistoryListItem]
class DeleteHistoryResponse(BaseModel): message: str
class DensityZonePoint(BaseModel): density: float; density_status: str; is_recommended_jarwo: bool; is_recommended_tegel: bool; is_high_risk: bool
class AgeZonePoint(BaseModel): age_days: int; age_status: str; zone: str
class WaterfallNode(BaseModel): name: str; amount: float; type: str
class ReferenceBenchmarks(BaseModel): recommended_density_max_jarwo: float = 4; recommended_density_max_tegel: float = 3; high_risk_threshold: float = 8; xiong_duration_min_days: float = 50; xiong_duration_max_days: float = 80
class VisualizationResponse(BaseModel): density_zones: list[DensityZonePoint]; age_zones: list[AgeZonePoint]; financial_waterfall: list[WaterfallNode]; reference_benchmarks: ReferenceBenchmarks; survival_note: str; yield_note: str
