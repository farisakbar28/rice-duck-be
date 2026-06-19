from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class RiceVariety:
    code: str
    label: str
    hst_masuk: int
    hst_heading: int
    harvest_age_days: int
    risk_note: str
    hst_masuk_min: int
    hst_masuk_max: int
    hst_heading_min: int
    hst_heading_max: int
    status: str


@dataclass(frozen=True)
class PlantingSystem:
    code: str
    label: str
    k_max_are: float
    f_yield: float
    note: str = ""
    k_max_min_are: float = 0
    k_max_max_are: float = 0
    limited_test_max_are: float | None = None
    k_max_status: str = "estimation"
    f_yield_status: str = "estimation"


@dataclass(frozen=True)
class DSSConstants:
    survival_lambda: float
    t_max_eff_days: int
    t_phase_1_days: int
    local_feed_warning_phase_days: int
    dung_phase_1_total_kg: float
    dung_phase_2_daily_kg: float
    minimum_density_are: float
    p_max: float
    penalty_gamma: float
    alpha_local: float
    daily_duck_grazing_hours: float
    baseline_grazing_hours: float
    feed_requirement_kg_per_duck_day: float | None
    feed_natural_saving_rate: float | None
    feed_greedy_kg_per_duck_day: float | None
    rice_duck_price_rp_per_kg: float | None
    conventional_rice_price_rp_per_kg: float
    conventional_yield_kg_per_ha: float | None
    duck_sale_price_rp_per_duck: float
    duck_buy_price_rp_per_duck: float
    feed_price_rp_per_kg: float | None
    nitrogen_price_rp_per_kg: float
    phosphate_price_rp_per_kg: float
    potassium_price_rp_per_kg: float
    weeding_cost_rp_per_are: float
    net_cost_rp: float
    net_lifetime_seasons: int
    shelter_cost_rp: float
    shelter_lifetime_seasons: int
    infrastructure_maintenance_rp_per_season: float
    additional_cost_rp_per_season: float
    kappa_n: float | None
    kappa_p: float | None
    kappa_k: float | None
    gwp_ch4: float
    gwp_n2o: float
    seasonal_ch4_rice_duck_kg_per_ha: float | None
    seasonal_ch4_conventional_kg_per_ha: float | None
    seasonal_n2o_kg_per_ha: float | None
    calibration_note: str


@dataclass(frozen=True)
class ParameterMetadata:
    value: Any
    unit: str
    source: str
    status: str
    note: str
    minimum: float | int | None = None
    maximum: float | int | None = None


@dataclass(frozen=True)
class User:
    id: str
    name: str
    email: str
    password_hash: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class SimulationHistory:
    id: str
    user_id: str
    input_data: dict
    actual_scenario: dict
    recommended_scenario: dict
    comparison: dict
    risk: dict
    trace: dict
    notes: list[str]
    economics: dict
    ecology: dict
    environment: dict
    lookup: dict
    validation: dict
    data_readiness: dict
    created_at: datetime


@dataclass(frozen=True)
class AuthContext:
    user: User
