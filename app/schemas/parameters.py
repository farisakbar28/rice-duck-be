from pydantic import BaseModel


class MarketPricesResponse(BaseModel):
    rice_duck_price_rp_per_kg: float
    conventional_rice_price_rp_per_kg: float
    baseline_yield_kg_per_are: float
    nitrogen_price_rp_per_kg: float
    phosphate_price_rp_per_kg: float
    potassium_price_rp_per_kg: float
    duck_price_rp_per_kg: float
    feed_price_rp_per_kg: float


class BiologicalConstantsResponse(BaseModel):
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


class EmissionConstantsResponse(BaseModel):
    gwp_ch4: float
    gwp_n2o: float
    do_slope: float
    do_intercept: float


class OptimizationParametersResponse(BaseModel):
    population_size: int
    mutation_factor: float
    crossover_rate: float
    max_generations: int
    epsilon: float


class ParameterSetResponse(BaseModel):
    id: str
    name: str
    version: str
    calibration_status: str
    market_prices: MarketPricesResponse
    biological_constants: BiologicalConstantsResponse
    emission_constants: EmissionConstantsResponse
    optimization: OptimizationParametersResponse


class ActiveParameterSetResponse(BaseModel):
    data: ParameterSetResponse
