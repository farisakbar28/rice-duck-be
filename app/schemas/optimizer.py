"""Schemas for the Optimizer feature.

WARNING — scope notice
----------------------
The optimizer is a **separate product feature** and is **out of scope** of the
rice-duck DSS mathematics documented in
``docs/Model Matematika Data Collection DSS Padi Bebek FINAL.md``.

It is a non-calculating product stub. It does not retain or execute legacy
formula implementations. Its scope is the academic recommendation layer — not
the operational calculator exposed under ``/api/v1/dss/simulate``.

Do **not** import or reuse functions from ``app.engines.formula_engine`` or
``app.engines.impact_engine`` here. This stub does not call the DSS Core and
does not expose Model A calculations as optimizer output.
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


# Rev 1 R-12: Type alias for profit_data_purity field
# MUST NOT accept 'partial' - only 'local-calibrated', 'mixed', 'literature-uncalibrated'
ProfitDataPurity = Literal["local-calibrated", "mixed", "literature-uncalibrated"]


class PredictedYield(BaseModel):
    kg_per_ha: float
    kg_per_are: float
    ton_per_ha: float
    estimated_total_kg: float


class DuckAgeAssessment(BaseModel):
    duck_age_days: int
    u_status: str
    c_age: float
    p_duck_buy_age_rp: float | None
    p_duck_buy_age_source: str
    p_duck_buy_age_status: str
    requires_actual_duck_buy_price: bool
    note: str


class DurationConstraintSummary(BaseModel):
    t_max_eff_days: int
    hst_phase_limit_days: int
    t_age_max_days: int
    t_maks_rekomendasi_days: int
    u_target_out_max_days: int


class QualityOutput(BaseModel):
    q_output: str
    score: float
    components: dict[str, float]
    notes: list[str]


class ActualScenario(BaseModel):
    duck_count: int
    land_area_are: float
    land_area_ha: float
    land_area_ha_note: float | None = None
    density_are: float
    density_ha: float
    density_lit_ha: float | None = None
    duration_days: int
    release_date: date
    pull_date: date
    t_age_max_days: int | None = None
    t_maks_rekomendasi_days: int | None = None
    surviving_ducks: float
    dung_total_per_duck_kg: float
    dung_status: str
    effective_duration_days: float
    x_base_kg_per_ha: float
    x_base_kg_are: float | None = None
    penalty_rate: float
    x_penalized_kg_per_ha: float
    x_penalized_kg_are: float | None = None
    predicted_yield: PredictedYield
    risk_status: str
    rey: float | None
    rey_status: str
    rey_notes: str


class RecommendedScenario(BaseModel):
    recommended_duck_count: int
    recommended_density_are: float
    recommended_density_ha: float
    recommended_density_lit_ha: float | None = None
    recommended_duration_days: int
    recommended_release_date: date
    recommended_pull_date: date
    t_age_max_days: int | None = None
    t_maks_rekomendasi_days: int | None = None
    surviving_ducks: float
    dung_total_per_duck_kg: float
    dung_status: str
    effective_duration_days: float
    x_base_kg_per_ha: float
    x_base_kg_are: float | None = None
    penalty_rate: float
    x_penalized_kg_per_ha: float
    x_penalized_kg_are: float | None = None
    predicted_yield: PredictedYield
    risk_status: str
    reasoning_summary: str
    rey: float | None
    rey_status: str
    rey_notes: str


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
    status_data: str | None = None
    perspective: str
    rice_revenue_rp: float | None
    conventional_rice_revenue_rp: float | None
    delta_rice_value_rp: float | None
    duck_revenue_rp: float
    duck_purchase_cost_rp: float | None
    duck_purchase_price_rp_per_duck: float | None = None
    duck_purchase_price_source: str | None = None
    duck_purchase_price_status: str | None = None
    duck_purchase_price_requires_actual: bool = False
    feed_cost_rp: float | None
    feed_cost_status: str
    duck_net_value_rp: float | None
    infrastructure: InfrastructureOutput
    penalty_yield_rp: float | None
    penalty_feed_rp: float | None
    net_profit_rp: float | None
    net_profit_rp_per_are: float | None
    missing_parameters: list[str]
    sumber_data: str
    data_readiness: str | None = None
    formula_available: bool = True
    numeric_ready: bool | None = None
    q_feed_source: str | None = None
    q_feed_status: str | None = None
    q_feed_assumption_note: str | None = None
    v_duck_xiong_reference: float | None = None
    v_duck_xiong_model_value: float | None = None
    v_duck_xiong_status: str = "literature-uncalibrated"
    additional_cost: float


class EconomicsSummary(BaseModel):
    status: str
    actual: ScenarioEconomics
    recommended: ScenarioEconomics
    delta_profit_rp: float | None
    assumptions: list[str]


class SoilNutrients(BaseModel):
    status: str
    n_kg_per_are: float | None = None
    p2o5_kg_per_are: float | None = None
    k2o_kg_per_are: float | None = None
    n_kg_per_ha: float | None = None
    p2o5_kg_per_ha: float | None = None
    k2o_kg_per_ha: float | None = None
    n_total_kg: float | None = None
    p2o5_total_kg: float | None = None
    k2o_total_kg: float | None = None
    missing_parameters: list[str]


class ScenarioEcology(BaseModel):
    status: str
    fertilizer_saving_rp: float
    fertilizer_saving_raw_rp: float
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
    calibration_note: str
    co2e_kg_per_ha_season: float | None = None
    ghgi_kg_co2e_per_kg_yield: float | None = None
    ch4_reduction_percent: float | None = None
    y_ch4_do_model: float | None = None
    missing_parameters: list[str]
    sumber_data: str
    status_data: str | None = None
    catatan_kalibrasi: str | None = None
    data_readiness: str | None = None
    formula_available: bool = True
    numeric_ready: bool | None = None
    co2e_are: float | None = None
    f_ch4_are: float | None = None
    f_n2o_are: float | None = None
    ghgi: float | None = None
    ch4_reduction_pct: float | None = None
    co2e_ha_note: float | None = None
    f_ch4_ha_note: float | None = None
    f_n2o_ha_note: float | None = None


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


class OptimalityAssessment(BaseModel):
    is_optimal: bool
    score_safety: bool
    density_gap_ratio: float | None
    density_gap_within_threshold: bool | None
    delta_yield_pct: float | None
    delta_yield_within_threshold: bool | None
    delta_profit_ratio: float | None
    delta_profit_within_threshold: bool | None
    profit_component_included: bool
    optimality_basis: str
    catatan_kalibrasi: str
    thresholds: dict[str, float]
    threshold_status: str
    sumber_data: str
    profit_data_purity: ProfitDataPurity


class DataReadinessSummary(BaseModel):
    agronomy_ready: str
    yield_ready: str
    economics_ready: str
    ecology_ready: str
    environment_ready: str
    overall_status: str


class OptimizerRecommendRequest(BaseModel):
    """Minimal request — optimizer needs only the inputs already used by /dss/simulate.

    This stub does not call the DSS Core or execute optimizer calculations.
    """

    duck_count: int = Field(gt=0)
    land_area_are: float = Field(gt=0)
    planting_date: date
    rice_variety: str
    planting_system: str
    duck_age_days: int = Field(gt=0)
    duck_buy_price_rp_per_duck: float | None = Field(default=None, gt=0)


class OptimizerRecommendResponse(BaseModel):
    """Optimizer output (NOT a SoT response).

    This response is an explicit optimizer-stub placeholder and has no
    literature, local-calibration, or Model A calculation semantics.
    """

    actual_scenario: ActualScenario
    recommended_scenario: RecommendedScenario | None
    comparison: ComparisonSummary | None
    economics: EconomicsSummary
    ecology: EcologySummary
    environment: EnvironmentSummary
    risk: RiskSummary
    optimality: OptimalityAssessment
    validation: ValidationSummary
    data_readiness: DataReadinessSummary
    assumptions: list[str]
    scope_notice: str = (
        "Out of scope of the Model A DSS Core"
    )
