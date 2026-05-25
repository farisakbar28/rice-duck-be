import math
from datetime import date, timedelta

from app.domain.enums import RiskLevel
from app.domain.models import BiologicalConstants, MarketPrices, PlantingSystem, RiceVariety


def compute_safe_window_days(variety: RiceVariety, biology: BiologicalConstants) -> int:
    raw_window = variety.hst_heading - variety.hst_entry
    return max(1, min(raw_window, biology.t_max_eff_days))


def compute_dung_total_per_duck(duration_days: float, biology: BiologicalConstants) -> float:
    if duration_days <= biology.t_phase_1_days:
        return (duration_days / biology.t_phase_1_days) * biology.dung_phase_1_total_kg
    return biology.dung_phase_1_total_kg + (
        (duration_days - biology.t_phase_1_days) * biology.dung_phase_2_daily_kg
    )


def compute_risk_level(density_per_are: float, k_max_per_are: float) -> RiskLevel:
    if density_per_are <= k_max_per_are:
        return RiskLevel.NORMAL
    if density_per_are <= 1.3 * k_max_per_are:
        return RiskLevel.WASPADA
    return RiskLevel.BAHAYA


def compute_penalty_rate(density_per_are: float, k_max_per_are: float) -> float:
    if density_per_are <= k_max_per_are:
        return 0.0
    over_capacity = (density_per_are - k_max_per_are) / k_max_per_are
    return min(0.5, over_capacity * 0.5)


def compute_base_yield_kg_per_are(density_per_are: float, duration_days: float) -> float:
    density_term = (-1.03 * density_per_are**2) + (2.6314 * density_per_are) + 75.694
    duration_term = math.exp(-((duration_days - 80.0) ** 2) / (2.0 * (80.0**2)))
    return max(0.0, density_term * duration_term)


def compute_final_yield_kg_per_are(
    density_per_are: float,
    duration_days: float,
    planting_system: PlantingSystem,
) -> tuple[float, float, float]:
    base_yield = compute_base_yield_kg_per_are(density_per_are, duration_days)
    penalty_rate = compute_penalty_rate(density_per_are, planting_system.k_max_per_are)
    penalized_yield = base_yield * (1.0 - penalty_rate)
    final_yield_kg = penalized_yield * planting_system.f_yield
    return base_yield, penalty_rate, final_yield_kg


def compute_delta_v_rice_rp(
    prices: MarketPrices,
    final_yield_kg_per_are: float,
    area_are: float,
) -> float:
    rice_duck_value = prices.rice_duck_price_rp_per_kg * final_yield_kg_per_are
    baseline_value = (
        prices.conventional_rice_price_rp_per_kg * prices.baseline_yield_kg_per_are
    )
    return (rice_duck_value - baseline_value) * area_are


def compute_v_eco1_rp(
    prices: MarketPrices,
    density_per_are: float,
    duration_days: float,
    area_are: float,
    biology: BiologicalConstants,
) -> float:
    nutrient_value = (
        (0.107 * prices.nitrogen_price_rp_per_kg)
        + (0.424 * prices.phosphate_price_rp_per_kg)
        + (0.058 * prices.potassium_price_rp_per_kg)
    )
    return max(
        0.0,
        ((0.02 * duration_days) - 0.6)
        * nutrient_value
        * density_per_are
        * biology.survival_rate
        * area_are,
    )


def compute_v_eco2_rp(density_per_are: float, area_are: float) -> float:
    density_reference = density_per_are * 100.0
    area_reference = area_are / 100.0
    if density_reference > 300.0:
        return ((400.0 / (1.0 + math.exp(-0.036626 * density_reference))) - 3.327) * area_reference
    value_at_300 = (400.0 / (1.0 + math.exp(-0.036626 * 300.0))) - 3.327
    return max(0.0, (density_reference / 300.0) * value_at_300 * area_reference)


def compute_duck_gross_value_rp(
    duck_count: int,
    density_per_are: float,
    duration_days: float,
    area_are: float,
    prices: MarketPrices,
    planting_system: PlantingSystem,
    biology: BiologicalConstants,
) -> tuple[float, float]:
    harvested_ducks = duck_count * biology.survival_rate
    duck_revenue = harvested_ducks * biology.average_duck_sale_weight_kg * prices.duck_price_rp_per_kg
    feed_penalty = compute_feed_penalty_rp(
        density_per_are=density_per_are,
        duration_days=duration_days,
        area_are=area_are,
        feed_price_rp_per_kg=prices.feed_price_rp_per_kg,
        k_max_per_are=planting_system.k_max_per_are,
        biology=biology,
    )
    return duck_revenue - feed_penalty, feed_penalty


def compute_feed_penalty_rp(
    density_per_are: float,
    duration_days: float,
    area_are: float,
    feed_price_rp_per_kg: float,
    k_max_per_are: float,
    biology: BiologicalConstants,
) -> float:
    excessive_density = max(0.0, density_per_are - k_max_per_are)
    excessive_duration = max(0.0, duration_days - biology.t_phase_1_days)

    if excessive_density > 0.0:
        return (
            excessive_density
            * biology.feed_greedy_kg_per_day
            * duration_days
            * feed_price_rp_per_kg
            * area_are
        )

    if excessive_duration > 0.0:
        return (
            density_per_are
            * biology.feed_greedy_kg_per_day
            * excessive_duration
            * feed_price_rp_per_kg
            * area_are
        )

    return 0.0


def compute_penalty_yield_rp(
    base_yield_kg_per_are: float,
    penalty_rate: float,
    area_are: float,
    prices: MarketPrices,
) -> float:
    return base_yield_kg_per_are * penalty_rate * area_are * prices.rice_duck_price_rp_per_kg


def compute_npk_contribution(
    density_per_are: float,
    duration_days: float,
    biology: BiologicalConstants,
) -> tuple[float, float, float]:
    dung_total = compute_dung_total_per_duck(duration_days, biology)
    density_reference = density_per_are * 100.0
    scale_reference = (dung_total / 10.0) * density_reference * biology.survival_rate
    n_reference = biology.kappa_n_kg_per_duck * scale_reference
    p_reference = biology.kappa_p2o5_kg_per_duck * scale_reference
    k_reference = biology.kappa_k2o_kg_per_duck * scale_reference
    return n_reference / 100.0, p_reference / 100.0, k_reference / 100.0


def build_timeline(planting_date: date, hst_entry: int, duration_days: int) -> tuple[date, date]:
    release_date = planting_date + timedelta(days=hst_entry)
    pull_date = release_date + timedelta(days=duration_days)
    return release_date, pull_date
