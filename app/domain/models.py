from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class RiceVariety:
    code: str
    label: str
    # SoT §6.1 — harvest HST range
    # Sertani: hst_panen_min=100, hst_panen_max=110
    # Inpari:  hst_panen_min=134, hst_panen_max=134 (single point + generic warning)
    hst_panen_min: int
    hst_panen_max: int
    risk_note: str
    status: str
    # legacy alias kept for backward-compat read of old data only
    hst_panen: int = 0          # deprecated: use hst_panen_min/max
    hst_masuk: int = 21         # fixed HST_in=21 per SoT §6
    hst_heading: int = 65       # fixed HST_out=65 per SoT §6
    harvest_age_days: int = 0   # deprecated alias
    hst_masuk_min: int = 21
    hst_masuk_max: int = 21
    hst_heading_min: int = 65
    hst_heading_max: int = 65


@dataclass(frozen=True)
class PlantingSystem:
    code: str
    label: str
    # SoT §5.1 — RECOMMENDED density ceiling per system
    # jajar_legowo: 2 <= d <= 4  (Jajar Legowo 2:1 only)
    # tegel:        2 <= d <= 3
    recommended_density_max_are: float
    note: str = ""
    # Legacy fields retained for backward-compat read only; not used in Core
    k_safe_are: float = 0.0
    k_max_are: float = 0.0
    f_yield: float = 1.0
    recommended_density_min_are: float = 2.0
    k_safe_min_are: float = 0.0
    k_safe_max_are: float = 0.0
    k_max_min_are: float = 0.0
    k_max_max_are: float = 0.0
    limited_test_max_are: float | None = None
    k_max_status: str = "legacy"
    f_yield_status: str = "legacy"


@dataclass(frozen=True)
class DSSConstants:
    # HET pupuk (hardware-locked)
    HET_urea: float = 1800.0
    HET_phonska: float = 1840.0
    HET_kcl: float = 9500.0
    # Misc reference values (not used in Core)
    survival_lambda: float = 0.67               # legacy reference only
    t_max_eff_days: int = 45
    t_phase_1_days: int = 50
    local_feed_warning_phase_days: int = 30
    dung_phase_1_total_kg: float = 4.0
    dung_phase_2_daily_kg: float = 0.2
    minimum_density_are: float = 1.0
    p_max: float = 0.8
    penalty_gamma: float = 0.5
    daily_duck_grazing_hours: float = 10.0
    baseline_grazing_hours: float = 10.0
    feed_requirement_kg_per_duck_day: float | None = None
    feed_natural_saving_rate: float | None = None
    feed_greedy_kg_per_duck_day: float | None = None
    rice_duck_price_rp_per_kg: float | None = None
    duck_sale_price_rp_per_duck: float = 52500.0   # SoT §9: p_duck_sell
    duck_buy_price_rp_per_duck: float = 0.0         # placeholder; actual from request
    duck_target_out_max_days: int = 65
    feed_price_rp_per_kg: float | None = None
    nitrogen_price_rp_per_kg: float = 1800.0
    potassium_price_rp_per_kg: float = 9500.0
    weeding_cost_rp_per_are: float = 21000.0        # SoT §10.1
    gwp_ch4: float = 34.0
    gwp_n2o: float = 265.0
    seasonal_ch4_rice_duck_kg_per_ha: float | None = None
    seasonal_ch4_conventional_kg_per_ha: float | None = None
    seasonal_n2o_kg_per_ha: float | None = None
    calibration_note: str = ""
    feed_requirement_kg_per_duck_day_reference: float = 0.10
    feed_natural_saving_rate_reference: float = 0.66


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
class SimulationHistoryLegacy:
    """Legacy schema (schema_version <= 2). Read-only for audit."""
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
    schema_version: int = 1


@dataclass(frozen=True)
class SimulationHistory:
    """v3 schema — aligned with SoT FINAL (docs/Model Matematika Data Collection DSS Padi Bebek FINAL.md)."""
    id: str
    user_id: str
    schema_version: int
    # Input snapshot
    land_area_are: float
    duck_count: int
    rice_variety: str
    planting_system: str
    duck_age_days: int
    planting_date: str
    p_duck_buy: float
    # Age Engine
    age_flag: str
    # Density Engine
    density_are: float
    density_ha: float
    density_status: str
    # Calendar Engine
    hst_in: int
    hst_out: int
    t_active: int
    d_in: str
    d_out: str
    harvest_hst_min: int
    harvest_hst_max: int
    d_panen_min: str
    d_panen_max: str
    # Survival Engine
    n_survive: int
    # Yield Engine
    yield_are_pred: float
    yield_total_pred: float
    # Core Economics
    revenue_gabah: float
    revenue_duck_potential: float
    cost_duck_buy: float
    cost_feed: float
    core_cash_cost: float
    total_revenue_dss: float
    net_cash_contribution_dss: float
    # Warnings (JSON string)
    warnings_json: str
    created_at: datetime


@dataclass(frozen=True)
class AuthContext:
    user: User
