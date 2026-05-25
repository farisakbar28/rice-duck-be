from dataclasses import dataclass

from app.domain.enums import CalibrationStatus


@dataclass(frozen=True)
class RiceVariety:
    code: str
    name: str
    hst_entry: int
    hst_heading: int
    plant_height_category: str
    notes: str = ""


@dataclass(frozen=True)
class PlantingSystem:
    code: str
    name: str
    k_max_per_hectare: float
    f_yield: float
    notes: str = ""


@dataclass(frozen=True)
class MarketPrices:
    rice_duck_price_rp_per_kg: float
    conventional_rice_price_rp_per_kg: float
    baseline_yield_ton_per_ha: float
    nitrogen_price_rp_per_kg: float
    phosphate_price_rp_per_kg: float
    potassium_price_rp_per_kg: float
    duck_price_rp_per_kg: float
    feed_price_rp_per_kg: float


@dataclass(frozen=True)
class BiologicalConstants:
    survival_rate: float
    average_duck_sale_weight_kg: float
    kappa_dung_daily_kg_per_day: float
    kappa_n_kg_per_duck: float
    kappa_p2o5_kg_per_duck: float
    kappa_k2o_kg_per_duck: float
    t_phase_1_days: int
    dung_phase_1_total_kg: float
    dung_phase_2_daily_kg: float
    feed_greedy_kg_per_day: float
    t_max_eff_days: int


@dataclass(frozen=True)
class EmissionConstants:
    gwp_ch4: float
    gwp_n2o: float
    do_slope: float
    do_intercept: float


@dataclass(frozen=True)
class OptimizationParameters:
    population_size: int
    mutation_factor: float
    crossover_rate: float
    max_generations: int
    epsilon: float


@dataclass(frozen=True)
class ParameterSet:
    id: str
    name: str
    version: str
    calibration_status: CalibrationStatus
    market_prices: MarketPrices
    biological_constants: BiologicalConstants
    emission_constants: EmissionConstants
    optimization: OptimizationParameters

