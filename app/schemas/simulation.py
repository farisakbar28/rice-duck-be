from datetime import date

from pydantic import BaseModel, Field

from app.domain.enums import DuckEconomicModel, LandAreaUnit


class MarketPriceOverrides(BaseModel):
    rice_duck_price_rp_per_kg: float | None = Field(default=None, gt=0)
    conventional_rice_price_rp_per_kg: float | None = Field(default=None, gt=0)
    baseline_yield_ton_per_ha: float | None = Field(default=None, gt=0)
    nitrogen_price_rp_per_kg: float | None = Field(default=None, gt=0)
    phosphate_price_rp_per_kg: float | None = Field(default=None, gt=0)
    potassium_price_rp_per_kg: float | None = Field(default=None, gt=0)
    duck_price_rp_per_kg: float | None = Field(default=None, gt=0)
    feed_price_rp_per_kg: float | None = Field(default=None, gt=0)


class SimulationRequest(BaseModel):
    duck_count: int = Field(ge=0)
    land_area: float = Field(gt=0)
    land_area_unit: LandAreaUnit = LandAreaUnit.ARE
    rice_variety: str = Field(min_length=1)
    planting_system: str = Field(min_length=1)
    planting_date: date
    parameter_set_id: str = "active"
    duck_economic_model: DuckEconomicModel = DuckEconomicModel.LOCAL_GROSS
    include_emission: bool = False
    market_overrides: MarketPriceOverrides | None = None


class AreaSummary(BaseModel):
    value_are: float
    value_hectare: float


class InputSummary(BaseModel):
    duck_count: int
    area: AreaSummary
    rice_variety: str
    planting_system: str
    planting_date: date
    parameter_set_id: str


class TimelineSummary(BaseModel):
    duck_release_date: date
    duck_pull_date: date
    safe_window_days: int


class SoilNutrientSummary(BaseModel):
    n_kg_per_ha: float
    p2o5_kg_per_ha: float
    k2o_kg_per_ha: float


class ReactiveResult(BaseModel):
    duck_density_per_are: float
    duck_density_per_hectare: float
    duration_days: int
    risk_level: str
    penalty_rate: float
    predicted_rice_yield_ton_per_ha: float
    total_benefit_rp: float
    delta_rice_value_rp: float
    duck_net_value_rp: float
    ecological_value_rp: float
    penalty_yield_rp: float
    penalty_feed_rp: float
    soil_nutrients: SoilNutrientSummary
    timeline: TimelineSummary
    warnings: list[str]


class ProactiveResult(BaseModel):
    recommended_duck_total: int
    recommended_duck_density_per_are: float
    recommended_duck_density_per_hectare: float
    recommended_duration_days: int
    predicted_optimal_yield_ton_per_ha: float
    projected_total_benefit_rp: float
    delta_profit_rp: float
    timeline: TimelineSummary
    warnings: list[str]


class ComparisonSummary(BaseModel):
    display_mode: str
    yield_gain_ton_per_ha: float
    profit_gain_rp: float
    risk_transition: str
    summary: str


class CalculationStatus(BaseModel):
    economy: str
    emission: str
    calibration: str


class SimulationResponse(BaseModel):
    input_summary: InputSummary
    reactive_result: ReactiveResult
    proactive_result: ProactiveResult
    comparison: ComparisonSummary
    calculation_status: CalculationStatus
    assumptions: list[str]

