from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class RiceVarietyOption(BaseModel):
    code: str
    label: str
    hst_masuk: int
    hst_heading: int
    harvest_age_days: int
    risk_note: str
    hst_masuk_range: dict[str, int]
    hst_heading_range: dict[str, int]
    status: str


class PlantingSystemOption(BaseModel):
    code: str
    label: str
    k_max_are: float
    f_yield: float
    note: str
    k_max_range_are: dict[str, float]
    limited_test_max_are: float | None
    k_max_status: str
    f_yield_status: str


class DSSOptionsResponse(BaseModel):
    rice_varieties: list[RiceVarietyOption]
    planting_systems: list[PlantingSystemOption]


class DSSSimulationRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "duck_count": 28,
                "land_area_are": 7,
                "planting_date": "2026-06-01",
                "rice_variety": "sertani",
                "planting_system": "jajar_legowo",
                "duck_age_days": 30,
            }
        }
    )

    duck_count: int = Field(ge=0)
    land_area_are: float = Field(gt=0)
    planting_date: date
    rice_variety: str = Field(min_length=1)
    planting_system: str = Field(min_length=1)
    duck_age_days: int = Field(gt=0)


class DSSInput(BaseModel):
    duck_count: int
    land_area_are: float
    planting_date: date
    rice_variety: str
    planting_system: str
    duck_age_days: int


class PredictedYield(BaseModel):
    kg_per_ha: float
    kg_per_are: float
    ton_per_ha: float
    estimated_total_kg: float


class ActualScenario(BaseModel):
    duck_count: int
    land_area_are: float
    land_area_ha: float
    density_are: float
    density_ha: float
    duration_days: int
    release_date: date
    pull_date: date
    surviving_ducks: float
    dung_total_per_duck_kg: float
    dung_status: str
    effective_duration_days: float
    x_base_kg_per_ha: float
    penalty_rate: float
    x_penalized_kg_per_ha: float
    predicted_yield: PredictedYield
    risk_status: str


class RecommendedScenario(BaseModel):
    recommended_duck_count: int
    recommended_density_are: float
    recommended_density_ha: float
    recommended_duration_days: int
    recommended_release_date: date
    recommended_pull_date: date
    surviving_ducks: float
    dung_total_per_duck_kg: float
    dung_status: str
    effective_duration_days: float
    x_base_kg_per_ha: float
    penalty_rate: float
    x_penalized_kg_per_ha: float
    predicted_yield: PredictedYield
    risk_status: str
    reasoning_summary: str


class ComparisonSummary(BaseModel):
    duck_count_difference: int
    density_difference_are: float
    yield_difference_kg_per_ha: float
    yield_difference_total_kg: float
    risk_change: str
    profit_difference_rp: float | None


class RiskSummary(BaseModel):
    actual_status: str
    recommended_status: str
    density_risk: str
    phase_risk: str
    feed_warning: str
    survival_data_warning: str
    thresholds: dict[str, float]
    notes: list[str]


class InfrastructureOutput(BaseModel):
    status: str
    net_cost_per_cycle_rp: float
    shelter_cost_per_cycle_rp: float
    maintenance_cost_rp: float
    total_infrastructure_cost_rp: float
    note: str


class ScenarioEconomics(BaseModel):
    status: str
    perspective: str
    rice_revenue_rp: float | None
    conventional_rice_revenue_rp: float | None
    delta_rice_value_rp: float | None
    duck_revenue_rp: float
    duck_purchase_cost_rp: float
    feed_cost_rp: float | None
    feed_cost_status: str
    duck_net_value_rp: float | None
    infrastructure: InfrastructureOutput
    penalty_yield_rp: float | None
    penalty_feed_rp: float | None
    net_profit_rp: float | None
    net_profit_rp_per_are: float | None
    missing_parameters: list[str]


class EconomicsSummary(BaseModel):
    status: str
    actual: ScenarioEconomics
    recommended: ScenarioEconomics
    delta_profit_rp: float | None
    assumptions: list[str]


class SoilNutrients(BaseModel):
    status: str
    n_kg_per_ha: float | None
    p2o5_kg_per_ha: float | None
    k2o_kg_per_ha: float | None
    n_total_kg: float | None
    p2o5_total_kg: float | None
    k2o_total_kg: float | None
    missing_parameters: list[str]


class ScenarioEcology(BaseModel):
    status: str
    fertilizer_saving_rp: float
    fertilizer_saving_status: str
    pesticide_herbicide_saving_rp: float | None
    pesticide_herbicide_saving_status: str
    weed_reduction_rate: float
    weeding_saving_rp: float
    weeding_saving_status: str
    partial_ecological_value_rp: float
    total_ecological_value_rp: float | None
    included_components: list[str]
    missing_parameters: list[str]
    soil_nutrients: SoilNutrients


class EcologySummary(BaseModel):
    status: str
    actual: ScenarioEcology
    recommended: ScenarioEcology
    assumptions: list[str]


class ScenarioEnvironment(BaseModel):
    status: str
    co2e_kg_per_ha_season: float | None
    ghgi_kg_co2e_per_kg_yield: float | None
    ch4_reduction_percent: float | None
    missing_parameters: list[str]


class EnvironmentSummary(BaseModel):
    status: str
    actual: ScenarioEnvironment
    recommended: ScenarioEnvironment
    assumptions: list[str]


class ValidationSummary(BaseModel):
    input_valid: bool
    constraint_violations: list[str]
    warnings: list[str]
    missing_parameters: list[str]


class DataReadinessSummary(BaseModel):
    agronomy_ready: str
    yield_ready: str
    economics_ready: str
    ecology_ready: str
    environment_ready: str
    overall_status: str


class DSSSimulationResponse(BaseModel):
    history_id: str | None
    input: DSSInput
    lookup: dict
    actual_scenario: ActualScenario
    recommended_scenario: RecommendedScenario
    comparison: ComparisonSummary
    risk: RiskSummary
    trace: dict
    notes: list[str]
    economics: EconomicsSummary
    ecology: EcologySummary
    environment: EnvironmentSummary
    validation: ValidationSummary
    data_readiness: DataReadinessSummary


class HistorySummary(BaseModel):
    rice_variety: str
    planting_system: str
    duck_count: int
    land_area_are: float
    actual_density_are: float
    recommended_duck_count: int
    risk_status: str
    estimated_total_yield_kg: float


class HistoryListItem(BaseModel):
    id: str
    created_at: datetime
    summary: HistorySummary


class HistoryListResponse(BaseModel):
    data: list[HistoryListItem]


class DeleteHistoryResponse(BaseModel):
    message: str
