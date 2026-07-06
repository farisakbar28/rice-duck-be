from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# Rev 1 R-12: Type alias for profit_data_purity field
# MUST NOT accept 'partial' - only 'local-calibrated', 'mixed', 'literature-uncalibrated'
ProfitDataPurity = Literal["local-calibrated", "mixed", "literature-uncalibrated"]


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
                "duck_buy_price_rp_per_duck": 26500,
            }
        }
    )

    duck_count: int = Field(gt=0)
    land_area_are: float = Field(gt=0)
    planting_date: date
    rice_variety: str = Field(min_length=1)
    planting_system: str = Field(min_length=1)
    duck_age_days: int = Field(gt=0)
    duck_buy_price_rp_per_duck: float | None = Field(default=None, gt=0)


class DSSInput(BaseModel):
    duck_count: int
    land_area_are: float
    planting_date: date
    rice_variety: str
    planting_system: str
    duck_age_days: int
    duck_buy_price_rp_per_duck: float | None = None


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
    land_area_ha_note: float | None = None    # Rev 2: A_ha_note = A_are / 100 (alias)
    density_are: float                         # Rev 2 primary: d_aktual_are
    density_ha: float                          # Backward compat
    density_lit_ha: float | None = None        # Rev 2: d_lit_ha = d_aktual_are * 100 (note)
    duration_days: int
    release_date: date
    pull_date: date
    t_age_max_days: int | None = None
    t_maks_rekomendasi_days: int | None = None
    surviving_ducks: float
    dung_total_per_duck_kg: float
    dung_status: str
    effective_duration_days: float
    x_base_kg_per_ha: float                    # x_base_kg_ha_note
    x_base_kg_are: float | None = None         # Rev 2: x_base_kg_ha_note / 100
    penalty_rate: float
    x_penalized_kg_per_ha: float               # backward compat
    x_penalized_kg_are: float | None = None    # Rev 2
    predicted_yield: PredictedYield
    risk_status: str
    # Rev 1 R-4: Rice Equivalent Yield
    rey: float | None
    rey_status: str
    rey_notes: str


class RecommendedScenario(BaseModel):
    recommended_duck_count: int
    recommended_density_are: float              # Rev 2 primary
    recommended_density_ha: float               # Backward compat
    recommended_density_lit_ha: float | None = None  # Rev 2 note
    recommended_duration_days: int
    recommended_release_date: date
    recommended_pull_date: date
    t_age_max_days: int | None = None
    t_maks_rekomendasi_days: int | None = None
    surviving_ducks: float
    dung_total_per_duck_kg: float
    dung_status: str
    effective_duration_days: float
    x_base_kg_per_ha: float                    # note
    x_base_kg_are: float | None = None         # Rev 2 primary
    penalty_rate: float
    x_penalized_kg_per_ha: float               # backward compat
    x_penalized_kg_are: float | None = None    # Rev 2
    predicted_yield: PredictedYield
    risk_status: str
    reasoning_summary: str
    # Rev 1 R-4: Rice Equivalent Yield
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
    # Rev 1 R-12: field sumber data
    sumber_data: str
    data_readiness: str | None = None
    formula_available: bool = True
    numeric_ready: bool | None = None
    # Rev 1 R-12: q_feed fields
    q_feed_source: str | None = None
    q_feed_status: str | None = None
    q_feed_assumption_note: str | None = None
    # Rev 1 R-17: V_duck_Xiong sebagai pembanding akademik (bukan nilai operasional)
    # Field name tidak pakai suffix _rp karena koefisien Xiong bukan rupiah lokal
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
    # Rev 2 primary: kg/are (basis are)
    n_kg_per_are: float | None = None
    p2o5_kg_per_are: float | None = None
    k2o_kg_per_are: float | None = None
    # Backward compat note: kg/ha = kg/are * 100
    n_kg_per_ha: float | None = None
    p2o5_kg_per_ha: float | None = None
    k2o_kg_per_ha: float | None = None
    # Totals (optional, based on are primary)
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
    # Backward compat (ha note)
    co2e_kg_per_ha_season: float | None = None
    ghgi_kg_co2e_per_kg_yield: float | None = None
    ch4_reduction_percent: float | None = None
    y_ch4_do_model: float | None = None
    missing_parameters: list[str]
    # Rev 1 R-12: sumber data modul emisi
    sumber_data: str
    status_data: str | None = None
    catatan_kalibrasi: str | None = None
    data_readiness: str | None = None
    formula_available: bool = True
    numeric_ready: bool | None = None
    # Rev 2 primary fields (are basis)
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
    """Bagian B: evaluasi apakah kondisi aktual petani sudah optimal.

    Kriteria (Opsi 3 — Safety + yield + profit dengan fallback):
      1. score_safety = True  (d_are <= K_max, HST_masuk+t <= HST_heading, A_are > 0)
      2. density_gap_ratio  = |d_aktual - d_rec| / d_rec   <= 0.15
      3. delta_yield_pct    = (x_rec - x_aktual) / x_aktual * 100  <= 5.0%
      4. delta_profit_ratio = DeltaProfit / |Laba_bersih_aktual|   <= 0.10
         (hanya jika DeltaProfit tersedia; jika null → evaluasi parsial tanpa komponen ini)

    Ambang 15% dan 5% adalah heuristik engineering (system-design-uncalibrated)
    — wajib direvisi setelah alpha_local dikalibrasi dari 3-5 siklus panen lokal.
    """

    is_optimal: bool
    """True → kondisi petani sudah optimal; False → tampilkan rekomendasi."""

    score_safety: bool
    """PDF §5.9: I(HST_masuk+t<=HST_heading) * I(d_are<=K_max) * I(A_are>0)."""

    density_gap_ratio: float | None
    """|(d_aktual - d_rec)| / d_rec. None jika d_rec = 0."""

    density_gap_within_threshold: bool | None
    """True jika density_gap_ratio <= 0.15."""

    delta_yield_pct: float | None
    """(x_rec - x_aktual) / x_aktual * 100. None jika x_aktual = 0."""

    delta_yield_within_threshold: bool | None
    """True jika delta_yield_pct <= 5.0."""

    delta_profit_ratio: float | None
    """DeltaProfit / |Laba_bersih_aktual|. None jika profit tidak tersedia."""

    delta_profit_within_threshold: bool | None
    """True jika delta_profit_ratio <= 0.10. None jika profit tidak tersedia."""

    profit_component_included: bool
    """False jika DeltaProfit null — evaluasi berjalan parsial tanpa komponen profit."""

    optimality_basis: str
    """'safety+yield+profit', 'safety+yield' (parsial), atau 'safety_failed'."""

    catatan_kalibrasi: str
    """Penjelasan eksplisit status kalibrasi ambang dan evaluasi."""

    thresholds: dict[str, float]
    """Ambang numerik yang dipakai: density_gap=0.15, delta_yield_pct=5.0, delta_profit=0.10."""

    threshold_status: str
    """'system-design-uncalibrated' — ambang belum dari literatur/data lokal."""

    # Rev 1 R-12: sumber evaluasi optimalitas
    sumber_data: str
    """Asal data yang mendasari evaluasi: 'local-calibrated'|'mixed'|'literature-uncalibrated'."""

    # Rev 1 R-7: kemurnian data profit
    profit_data_purity: ProfitDataPurity
    """'local-calibrated'|'mixed'|'literature-uncalibrated'. Berdasarkan sumber Laba_bersih aktual."""


class DataReadinessSummary(BaseModel):
    agronomy_ready: str
    yield_ready: str
    economics_ready: str
    ecology_ready: str
    environment_ready: str
    overall_status: str


class DSSSimulationResponse(BaseModel):
    density_status: str
    age_status: str
    D_masuk_bebek: date
    D_tarik_bebek: date
    N_survive: float
    Yield_are_predict: float
    Yield_total_predict: float
    Revenue_gabah: float
    Revenue_duck: float
    Total_Revenue: float
    Cost_duck_buy: float
    Cost_feed: float
    Cost_labor_total: float
    Cost_infra: float
    Cost_fertilizer_total: float
    Cost_fert_urea: float
    Cost_fert_phonska: float
    Cost_fert_kcl: float
    Cost_pesticide: float
    Cost_total_cash: float
    Profit_net_cash: float
    Valuation_weed_eco: float
    Profit_net_full: float


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
