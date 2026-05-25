from datetime import datetime
from datetime import date

from pydantic import BaseModel, Field

from app.domain.enums import DuckEconomicModel


class MarketPriceOverrides(BaseModel):
    rice_duck_price_rp_per_kg: float | None = Field(default=None, gt=0)
    conventional_rice_price_rp_per_kg: float | None = Field(default=None, gt=0)
    baseline_yield_kg_per_are: float | None = Field(default=None, gt=0)
    nitrogen_price_rp_per_kg: float | None = Field(default=None, gt=0)
    phosphate_price_rp_per_kg: float | None = Field(default=None, gt=0)
    potassium_price_rp_per_kg: float | None = Field(default=None, gt=0)
    duck_price_rp_per_kg: float | None = Field(default=None, gt=0)
    feed_price_rp_per_kg: float | None = Field(default=None, gt=0)


class SimulationRequest(BaseModel):
    duck_count: int = Field(ge=0)
    land_area_are: float = Field(gt=0)
    rice_variety: str = Field(min_length=1)
    planting_system: str = Field(min_length=1)
    planting_date: date
    parameter_set_id: str = "active"
    duck_economic_model: DuckEconomicModel = DuckEconomicModel.LOCAL_GROSS
    include_emission: bool = False
    market_overrides: MarketPriceOverrides | None = None


class SimulationPreviewRequest(BaseModel):
    duck_count: int = Field(ge=0)
    land_area_are: float = Field(gt=0)
    rice_variety: str = Field(min_length=1)
    planting_system: str = Field(min_length=1)
    planting_date: date
    parameter_set_id: str = "active"


class AreaSummary(BaseModel):
    value_are: float


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


class AgronomicContext(BaseModel):
    rice_variety_code: str
    rice_variety_name: str
    planting_system_code: str
    planting_system_name: str
    hst_entry: int
    hst_heading: int
    safe_window_days: int
    k_max_per_are: float
    warning_limit_per_are: float
    f_yield: float
    baseline_yield_kg_per_are: float


class RiskSummary(BaseModel):
    level: str
    current_density_per_are: float
    k_max_per_are: float
    warning_limit_per_are: float
    exceeded_density_per_are: float
    exceeded_ratio_pct: float


class SoilNutrientSummary(BaseModel):
    n_kg_per_are: float
    p2o5_kg_per_are: float
    k2o_kg_per_are: float
    n_total_kg: float
    p2o5_total_kg: float
    k2o_total_kg: float


class ReactiveResult(BaseModel):
    duck_density_per_are: float
    duration_days: int
    risk_level: str
    risk_summary: RiskSummary
    penalty_rate: float
    predicted_rice_yield_kg_per_are: float
    predicted_rice_yield_total_kg: float
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
    recommended_duration_days: int
    risk_summary: RiskSummary
    predicted_optimal_yield_kg_per_are: float
    predicted_optimal_yield_total_kg: float
    projected_total_benefit_rp: float
    delta_profit_rp: float
    timeline: TimelineSummary
    warnings: list[str]


class ComparisonSummary(BaseModel):
    display_mode: str
    yield_gain_kg_per_are: float
    yield_gain_total_kg: float
    profit_gain_rp: float
    risk_transition: str
    summary: str


class CalculationStatus(BaseModel):
    economy: str
    emission: str
    calibration: str


class OptimizationBounds(BaseModel):
    density_min_per_are: float
    density_max_per_are: float
    duration_min_days: int
    duration_max_days: int


class OptimizationMeta(BaseModel):
    algorithm: str
    objective_name: str
    population_size: int
    mutation_factor: float
    crossover_rate: float
    max_generations: int
    executed_generations: int
    converged: bool
    best_objective_value_rp: float
    bounds: OptimizationBounds


class PreviewSummary(BaseModel):
    duck_count: int
    land_area_are: float
    duck_density_per_are: float
    duration_days: int
    max_duck_capacity: int
    recommended_duck_upper_bound: int
    estimated_rice_yield_kg_per_are: float
    estimated_rice_yield_total_kg: float
    timeline: TimelineSummary
    risk_summary: RiskSummary
    warnings: list[str]


class SimulationPreviewResponse(BaseModel):
    input_summary: InputSummary
    agronomic_context: AgronomicContext
    preview: PreviewSummary
    calculation_status: CalculationStatus
    assumptions: list[str]


class SimulationListItem(BaseModel):
    simulation_id: str
    created_at: datetime
    rice_variety: str
    planting_system: str
    planting_date: date
    duck_count: int
    area_are: float
    reactive_risk_level: str
    reactive_total_benefit_rp: float
    proactive_total_benefit_rp: float
    recommended_duck_total: int
    calibration_status: str


class SimulationListResponse(BaseModel):
    data: list[SimulationListItem]


class SimulationResponse(BaseModel):
    simulation_id: str
    created_at: datetime
    input_summary: InputSummary
    agronomic_context: AgronomicContext
    reactive_result: ReactiveResult
    proactive_result: ProactiveResult
    comparison: ComparisonSummary
    optimization_meta: OptimizationMeta
    calculation_status: CalculationStatus
    assumptions: list[str]
