"""Strict HTTP contracts for the frozen Model C DSS."""

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Any, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StrictInt,
    WithJsonSchema,
    model_validator,
)


def _number(value: Any) -> Any:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise ValueError("must be a JSON number, not a string or boolean")
    return value


def _positive(value: Decimal) -> Decimal:
    if value <= 0:
        raise ValueError("must be greater than zero")
    return value


def _nonnegative(value: Decimal) -> Decimal:
    if value < 0:
        raise ValueError("must be greater than or equal to zero")
    return value


JsonPositiveNumber = Annotated[
    Decimal,
    BeforeValidator(_number),
    AfterValidator(_positive),
    WithJsonSchema({"type": "number", "exclusiveMinimum": 0}, mode="validation"),
]
JsonNonNegativeNumber = Annotated[
    Decimal,
    BeforeValidator(_number),
    AfterValidator(_nonnegative),
    WithJsonSchema({"type": "number", "minimum": 0}, mode="validation"),
]


class RiceVarietyOption(BaseModel):
    code: str
    label: str
    risk_note: str
    status: str


class PlantingSystemOption(BaseModel):
    code: str
    label: str
    recommended_density_max_are: float
    recommended_density_min_are: float
    note: str


class DSSOptionsResponse(BaseModel):
    rice_varieties: list[RiceVarietyOption]
    planting_systems: list[PlantingSystemOption]


class DSSSimulationRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        allow_inf_nan=False,
        json_schema_extra={
            "example": {
                "land_area_are": 10,
                "duck_count": 20,
                "rice_variety": "sertani",
                "planting_system": "jajar_legowo",
                "duck_age_days": 21,
            }
        },
    )

    land_area_are: JsonPositiveNumber = Field(
        description="Required finite JSON number: active duck area in are, greater than zero."
    )
    duck_count: StrictInt = Field(
        ge=0, description="Required non-negative strict JSON integer; zero is accepted."
    )
    rice_variety: str = Field(
        min_length=1,
        json_schema_extra={"enum": ["sertani", "inpari"]},
        description="Required exact canonical code: sertani or inpari; no normalization is performed.",
    )
    planting_system: str = Field(
        min_length=1,
        json_schema_extra={"enum": ["jajar_legowo", "tegel"]},
        description="Required exact canonical code: jajar_legowo or tegel; no normalization is performed.",
    )
    duck_age_days: StrictInt = Field(
        ge=0, description="Required non-negative strict JSON integer; readiness gate only."
    )
    planting_date: date | None = Field(
        default=None, description="Optional calendar anchor; date outputs are null when omitted."
    )
    p_gabah: JsonNonNegativeNumber | None = Field(
        default=None, description="Optional finite JSON number; defaults to local-calibrated Rp6000/kg."
    )
    p_duck_buy: JsonNonNegativeNumber | None = Field(
        default=None, description="Optional finite JSON number; defaults to local-calibrated Rp25000/duck."
    )
    p_duck_sell: JsonNonNegativeNumber | None = Field(
        default=None,
        description="Optional finite JSON number; defaults to local-estimate all-sold scenario Rp45000/duck.",
    )
    c_feed_scenario: JsonNonNegativeNumber | None = Field(
        default=None, description="Optional total cycle feed scenario; there is no hidden default."
    )
    c_jaring_purchase: JsonNonNegativeNumber | None = Field(
        default=None, description="Optional net purchase cost; requires n_jaring_cycles."
    )
    n_jaring_cycles: JsonPositiveNumber | None = Field(
        default=None, description="Optional positive allocation denominator for net purchase cost."
    )
    c_kandang_purchase: JsonNonNegativeNumber | None = Field(
        default=None, description="Optional cage purchase cost; requires n_kandang_cycles."
    )
    n_kandang_cycles: JsonPositiveNumber | None = Field(
        default=None, description="Optional positive allocation denominator for cage purchase cost."
    )

    @model_validator(mode="after")
    def cost_pairs(self) -> "DSSSimulationRequest":
        if self.c_jaring_purchase is not None and self.n_jaring_cycles is None:
            raise ValueError("n_jaring_cycles is required when c_jaring_purchase is supplied")
        if self.c_kandang_purchase is not None and self.n_kandang_cycles is None:
            raise ValueError("n_kandang_cycles is required when c_kandang_purchase is supplied")
        return self


class DSSSimulationResponse(BaseModel):
    """Canonical Model C response; null means unavailable or not selected, never zero-filled."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "model_variant": "C_FARMER_GROUPED_LOCAL",
                "yield_are_kg": 50.0,
                "yield_total_kg": 500.0,
                "model_validation_status": "LOCAL_CALIBRATED_WITH_LIMITED_HOLDOUT_PERFORMANCE",
                "parameter_uncertainty_y0_95pct": [42.81, 55.78],
                "survival_risk": None,
                "cost_feed_scenario": None,
                "cost_infra_cycle": None,
                "cash_contribution_after_optional": None,
            }
        }
    )

    model_variant: Literal["C_FARMER_GROUPED_LOCAL"] = Field(
        default="C_FARMER_GROUPED_LOCAL", description="Frozen canonical Model C response variant."
    )
    yield_are_kg: float = Field(description="Frozen C0 production yield: always 50.0 kg/are for valid area.")
    yield_total_kg: float = Field(description="Total frozen yield: 50.0 multiplied by land_area_are.")
    model_validation_status: Literal["LOCAL_CALIBRATED_WITH_LIMITED_HOLDOUT_PERFORMANCE"] = Field(
        default="LOCAL_CALIBRATED_WITH_LIMITED_HOLDOUT_PERFORMANCE",
        description="Frozen Model C validation limitation status.",
    )
    parameter_uncertainty_y0_95pct: list[float] = Field(
        description="Descriptive 95% uncertainty for Y0_C [42.81, 55.78], not an individual prediction interval."
    )
    age_status: str = Field(description="Readiness gate: NOT_RECOMMENDED, LOCAL_READY, or OLDER_CONSERVATIVE.")
    density_are: float = Field(description="Duck density J / land_area_are in ducks per are.")
    density_ha: float = Field(description="Duck density converted to ducks per hectare: 100 * density_are.")
    density_status: str = Field(description="Density gate: UNDER, RECOMMENDED, WARNING_ABOVE_RECOMMENDED, or HIGH_RISK.")
    release_hst_min: int = Field(description="Earliest recommended release day: 21 HST.")
    release_hst_max: int = Field(description="Latest recommended release day: 30 HST.")
    withdraw_hst_min: int = Field(description="Earliest recommended withdrawal day: 56 HST.")
    withdraw_hst_max: int = Field(description="Latest recommended withdrawal day: 60 HST.")
    release_date_min: date | None = Field(description="Release lower-bound date, or null without planting_date.")
    release_date_max: date | None = Field(description="Release upper-bound date, or null without planting_date.")
    withdraw_date_min: date | None = Field(description="Withdrawal lower-bound date, or null without planting_date.")
    withdraw_date_max: date | None = Field(description="Withdrawal upper-bound date, or null without planting_date.")
    survival_risk: str | None = Field(description="HIGH only above 8 ducks/are; numerical survival is not modeled.")
    revenue_gabah: float = Field(description="Rice revenue: frozen yield total multiplied by selected rice price.")
    revenue_duck_all_sold_scenario: float | None = Field(
        description="All-sold scenario ceiling J * p_duck_sell, or null above 8 ducks/are."
    )
    cost_duck_buy: float = Field(description="Duck purchase scenario cost J * p_duck_buy.")
    cost_feed_scenario: float | None = Field(description="Selected total feed scenario, or null when omitted.")
    cost_infra_cycle: float | None = Field(description="Selected amortized infrastructure scenario, or null when omitted.")
    cash_contribution_before_optional: float | None = Field(
        description="Scenario cash contribution before optional costs; null when duck all-sold revenue is unavailable."
    )
    cash_contribution_after_optional: float | None = Field(
        description="Scenario cash contribution after selected optional costs; null when no optional cost is selected or prerequisite is unavailable."
    )
    warnings: list[str] = Field(description="Readiness and high-risk warnings; warnings do not change frozen yield.")
    provenance: dict[str, Any] = Field(
        description="Scientific traceability for frozen yield, validation metadata, prices, and non-numerical survival."
    )


class HistorySummary(BaseModel):
    rice_variety: str
    planting_system: str
    duck_count: int
    land_area_are: float
    density_are: float
    yield_are_kg: float


class HistoryListItem(BaseModel):
    id: str
    schema_version: int
    created_at: datetime
    summary: HistorySummary


class HistoryListResponse(BaseModel):
    data: list[HistoryListItem]


class DeleteHistoryResponse(BaseModel):
    message: str


class DensityZonePoint(BaseModel):
    density: float
    density_status: str
    is_recommended_jarwo: bool
    is_recommended_tegel: bool
    is_high_risk: bool


class AgeZonePoint(BaseModel):
    age_days: int
    age_status: str
    zone: str


class WaterfallNode(BaseModel):
    name: str
    amount: float | None
    type: str


class ReferenceBenchmarks(BaseModel):
    recommended_density_max_jarwo: float = 4
    recommended_density_max_tegel: float = 3
    high_risk_threshold: float = 8
    yield_baseline_kg_per_are: float = 50


class VisualizationResponse(BaseModel):
    density_zones: list[DensityZonePoint]
    age_zones: list[AgeZonePoint]
    financial_waterfall: list[WaterfallNode]
    reference_benchmarks: ReferenceBenchmarks
    survival_note: str
    yield_note: str
