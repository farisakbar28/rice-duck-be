from app.domain.enums import CalibrationStatus
from app.domain.models import (
    BiologicalConstants,
    EmissionConstants,
    MarketPrices,
    OptimizationParameters,
    ParameterSet,
    PlantingSystem,
    RiceVariety,
)

RICE_VARIETIES = [
    RiceVariety(
        code="ciherang",
        name="Ciherang",
        hst_entry=15,
        hst_heading=75,
        plant_height_category="medium",
        notes="Main crop reference used as default seed.",
    ),
    RiceVariety(
        code="inpari32",
        name="Inpari 32",
        hst_entry=14,
        hst_heading=76,
        plant_height_category="medium",
        notes="Illustrative lookup; validate with local calendar.",
    ),
    RiceVariety(
        code="ratoon",
        name="Ratoon Crop",
        hst_entry=10,
        hst_heading=50,
        plant_height_category="short",
        notes="Shorter safe window based on the workbook note for RC.",
    ),
    RiceVariety(
        code="lokal",
        name="Varietas Lokal",
        hst_entry=16,
        hst_heading=80,
        plant_height_category="variable",
        notes="Fallback seed for local cultivars pending site calibration.",
    ),
]

PLANTING_SYSTEMS = [
    PlantingSystem(
        code="konvensional",
        name="Konvensional",
        k_max_per_hectare=250.0,
        f_yield=1.0,
        notes="Baseline system.",
    ),
    PlantingSystem(
        code="legowo",
        name="Legowo",
        k_max_per_hectare=375.0,
        f_yield=1.05,
        notes="Initial lookup from the variable workbook.",
    ),
    PlantingSystem(
        code="sri",
        name="SRI",
        k_max_per_hectare=400.0,
        f_yield=1.10,
        notes="Initial lookup from the variable workbook.",
    ),
    PlantingSystem(
        code="double-transplant",
        name="Double Transplant",
        k_max_per_hectare=375.0,
        f_yield=1.175,
        notes="Initial lookup from the variable workbook.",
    ),
]

ACTIVE_PARAMETER_SET = ParameterSet(
    id="active",
    name="Seed Parameter Set",
    version="0.1.0",
    calibration_status=CalibrationStatus.REQUIRES_LOCAL_VALIDATION,
    market_prices=MarketPrices(
        rice_duck_price_rp_per_kg=14000.0,
        conventional_rice_price_rp_per_kg=12500.0,
        baseline_yield_ton_per_ha=5.5,
        nitrogen_price_rp_per_kg=2500.0,
        phosphate_price_rp_per_kg=4000.0,
        potassium_price_rp_per_kg=7000.0,
        duck_price_rp_per_kg=38000.0,
        feed_price_rp_per_kg=7000.0,
    ),
    biological_constants=BiologicalConstants(
        survival_rate=0.97,
        average_duck_sale_weight_kg=1.6,
        kappa_dung_daily_kg_per_day=0.1,
        kappa_n_kg_per_duck=0.049,
        kappa_p2o5_kg_per_duck=0.072,
        kappa_k2o_kg_per_duck=0.032,
        t_phase_1_days=50,
        dung_phase_1_total_kg=4.0,
        dung_phase_2_daily_kg=0.2,
        feed_greedy_kg_per_day=0.1,
        t_max_eff_days=80,
    ),
    emission_constants=EmissionConstants(
        gwp_ch4=34.0,
        gwp_n2o=265.0,
        do_slope=-1.5276,
        do_intercept=14.770,
    ),
    optimization=OptimizationParameters(
        population_size=40,
        mutation_factor=0.8,
        crossover_rate=0.9,
        max_generations=150,
        epsilon=1e-5,
    ),
)

