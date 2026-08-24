"""Strict A+C HTTP contracts: C0 production plus optional Xiong reference."""
from datetime import date, datetime
from decimal import Decimal
from math import isfinite
from typing import Annotated, Any, Literal
from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, Field, StrictInt, WithJsonSchema, model_validator

def _json_number(value: Any) -> Any:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)): raise ValueError("must be a JSON number, not a string or boolean")
    if isinstance(value, float) and not isfinite(value): raise ValueError("must be finite")
    if isinstance(value, Decimal) and not value.is_finite(): raise ValueError("must be finite")
    return value
def _positive(value: Decimal) -> Decimal:
    if value <= 0: raise ValueError("must be greater than zero")
    return value
def _nonnegative(value: Decimal) -> Decimal:
    if value < 0: raise ValueError("must be greater than or equal to zero")
    return value
JsonNumber = Annotated[Decimal, BeforeValidator(_json_number), WithJsonSchema({"type":"number"}, mode="validation")]
JsonPositiveNumber = Annotated[Decimal, BeforeValidator(_json_number), AfterValidator(_positive), WithJsonSchema({"type":"number","exclusiveMinimum":0}, mode="validation")]
JsonNonNegativeNumber = Annotated[Decimal, BeforeValidator(_json_number), AfterValidator(_nonnegative), WithJsonSchema({"type":"number","minimum":0}, mode="validation")]
class RiceVarietyOption(BaseModel): code: str; label: str; risk_note: str; status: str
class PlantingSystemOption(BaseModel): code: str; label: str; recommended_density_max_are: float; recommended_density_min_are: float; note: str
class DSSOptionsResponse(BaseModel): rice_varieties: list[RiceVarietyOption]; planting_systems: list[PlantingSystemOption]
class DSSSimulationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, json_schema_extra={"example":{"land_area_are":10,"duck_count":40,"rice_variety":"sertani","planting_system":"jajar_legowo","duck_age_days":21,"literature_duration_days":50}})
    land_area_are: JsonPositiveNumber = Field(description="Required finite JSON number greater than zero.")
    duck_count: StrictInt = Field(ge=0, description="Required non-negative strict JSON integer; zero is accepted.")
    rice_variety: str = Field(min_length=1, description="Exact code: sertani or inpari; no normalization.")
    planting_system: str = Field(min_length=1, description="Exact code: jajar_legowo or tegel; no normalization.")
    duck_age_days: StrictInt = Field(ge=0, description="Required non-negative strict JSON integer.")
    planting_date: date | None = Field(default=None, description="Optional calendar anchor; dates are null when omitted.")
    p_gabah: JsonNonNegativeNumber | None = Field(default=None, description="Optional runtime price; fallback local-calibrated Rp6000/kg.")
    p_duck_buy: JsonNonNegativeNumber | None = Field(default=None, description="Optional runtime price; fallback local-calibrated Rp25000/duck. Zero is valid.")
    p_duck_sell: JsonNonNegativeNumber | None = Field(default=None, description="Optional all-sold scenario price; fallback local-estimate Rp45000/duck.")
    literature_duration_days: JsonNumber | None = Field(default=None, description="Optional technical Xiong duration; it never changes primary yield or economics.")
    c_feed_scenario: JsonNonNegativeNumber | None = Field(default=None, description="Optional total selected cycle feed scenario; no hidden default.")
    c_jaring_purchase: JsonNonNegativeNumber | None = None
    n_jaring_cycles: JsonPositiveNumber | None = None
    c_kandang_purchase: JsonNonNegativeNumber | None = None
    n_kandang_cycles: JsonPositiveNumber | None = None
    @model_validator(mode="after")
    def validate_cost_pairs(self):
        if self.c_jaring_purchase is not None and self.n_jaring_cycles is None: raise ValueError("n_jaring_cycles is required when c_jaring_purchase is supplied")
        if self.c_kandang_purchase is not None and self.n_kandang_cycles is None: raise ValueError("n_kandang_cycles is required when c_kandang_purchase is supplied")
        return self
class DSSSimulationResponse(BaseModel):
    model_variant: Literal["AC_DUAL_EVIDENCE"] = "AC_DUAL_EVIDENCE"
    yield_are_kg: float = Field(description="PRIMARY local C0 production yield: always 50 kg/are.")
    yield_total_kg: float = Field(description="PRIMARY local C0 total yield: 50 multiplied by land area.")
    model_validation_status: Literal["LOCAL_CALIBRATED_WITH_LIMITED_HOLDOUT_PERFORMANCE"] = "LOCAL_CALIBRATED_WITH_LIMITED_HOLDOUT_PERFORMANCE"
    parameter_uncertainty_y0_95pct: list[float]
    literature_reference_status: Literal["VALID","OUTSIDE_LITERATURE_DOMAIN"] = Field(description="Xiong literature-reference availability; never a production routing status.")
    yield_literature_reference_are_kg: float | None = Field(description="Optional Xiong reference only; null outside literature domain.")
    yield_literature_reference_total_kg: float | None = Field(description="Optional Xiong reference total only; never used by economics.")
    literature_gap_kg_are: float | None = Field(description="Reference minus PRIMARY C0 yield; diagnostic only.")
    age_status: str; density_are: float; density_ha: float; density_status: str
    release_hst_min: int; release_hst_max: int; withdraw_hst_min: int; withdraw_hst_max: int
    release_date_min: date | None; release_date_max: date | None; withdraw_date_min: date | None; withdraw_date_max: date | None
    survival_risk: str | None
    revenue_gabah: float; revenue_duck_all_sold_scenario: float | None; cost_duck_buy: float; cost_feed_scenario: float | None; cost_infra_cycle: float | None; cash_contribution_before_optional: float | None; cash_contribution_after_optional: float | None
    warnings: list[str]; provenance: dict[str, Any]
class HistorySummary(BaseModel): rice_variety: str; planting_system: str; duck_count: int; land_area_are: float; density_are: float; yield_are_kg: float
class HistoryListItem(BaseModel): id: str; schema_version: int; created_at: datetime; summary: HistorySummary
class HistoryListResponse(BaseModel): data: list[HistoryListItem]
class DeleteHistoryResponse(BaseModel): message: str
class DensityZonePoint(BaseModel): density: float; density_status: str; is_recommended_jarwo: bool; is_recommended_tegel: bool; is_high_risk: bool
class AgeZonePoint(BaseModel): age_days: int; age_status: str; zone: str
class WaterfallNode(BaseModel): name: str; amount: float | None; type: str
class ReferenceBenchmarks(BaseModel): recommended_density_max_jarwo: float = 4; recommended_density_max_tegel: float = 3; high_risk_threshold: float = 8; yield_baseline_kg_per_are: float = 50; xiong_duration_min_days: float = 50; xiong_duration_max_days: float = 80
class VisualizationResponse(BaseModel): density_zones: list[DensityZonePoint]; age_zones: list[AgeZonePoint]; financial_waterfall: list[WaterfallNode]; reference_benchmarks: ReferenceBenchmarks; survival_note: str; yield_note: str
