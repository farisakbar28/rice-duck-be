import math
from datetime import date, timedelta

from app.domain.models import DSSConstants


def convert_are_to_ha(area_are: float) -> float:
    return area_are / 100.0


def compute_density(duck_count: int, land_area_are: float) -> tuple[float, float]:
    density_are = duck_count / land_area_are
    density_ha = density_are * 100.0
    return density_are, density_ha


def compute_actual_duration_days(hst_masuk: int, hst_heading: int) -> int:
    return hst_heading - hst_masuk


def compute_release_date(planting_date: date, hst_masuk: int) -> date:
    return planting_date + timedelta(days=hst_masuk)


def compute_pull_date_from_hst(planting_date: date, hst_heading: int) -> date:
    return planting_date + timedelta(days=hst_heading)


def compute_pull_date_from_duration(planting_date: date, hst_masuk: int, duration_days: int) -> date:
    return planting_date + timedelta(days=hst_masuk + duration_days)


def compute_surviving_ducks(duck_count: int, survival_lambda: float) -> float:
    return duck_count * survival_lambda


def compute_dung_total(duration_days: int, constants: DSSConstants) -> float:
    if duration_days <= constants.t_phase_1_days:
        return (duration_days / constants.t_phase_1_days) * constants.dung_phase_1_total_kg
    return constants.dung_phase_1_total_kg + (
        (duration_days - constants.t_phase_1_days) * constants.dung_phase_2_daily_kg
    )


def compute_effective_duration(duration_days: int, constants: DSSConstants) -> float:
    return duration_days * (
        constants.daily_duck_grazing_hours / constants.baseline_grazing_hours
    )


def compute_penalty_rate(
    density_are: float,
    k_max_are: float,
    constants: DSSConstants,
) -> float:
    if density_are <= k_max_are:
        return 0.0
    over_capacity_ratio = (density_are - k_max_are) / k_max_are
    return min(constants.p_max, constants.penalty_gamma * over_capacity_ratio)


def compute_base_yield_kg_per_ha(density_ha: float, duration_days: int) -> float:
    return (
        (-0.0103 * (density_ha**2)) + (2.6314 * density_ha) + 7569.4
    ) * math.exp(-(((duration_days - 80) ** 2) / (2 * (80**2))))


def compute_final_yield_kg_per_ha(
    density_are: float,
    duration_days: int,
    k_max_are: float,
    f_yield: float,
    constants: DSSConstants,
) -> tuple[float, float, float, float]:
    density_ha = density_are * 100.0
    x_base = compute_base_yield_kg_per_ha(density_ha=density_ha, duration_days=duration_days)
    penalty_rate = compute_penalty_rate(
        density_are=density_are,
        k_max_are=k_max_are,
        constants=constants,
    )
    x_penalized = x_base * (1.0 - penalty_rate)
    x_final = constants.alpha_local * x_penalized * f_yield
    return x_base, penalty_rate, x_penalized, x_final


def convert_yield_units(final_yield_kg_per_ha: float, land_area_are: float) -> tuple[float, float]:
    kg_per_are = final_yield_kg_per_ha / 100.0
    estimated_total_kg = kg_per_are * land_area_are
    return kg_per_are, estimated_total_kg


def compute_risk_status(
    density_are: float,
    k_max_are: float,
    duration_days: int,
    max_duration_days: int,
) -> str:
    if density_are > (1.25 * k_max_are) or duration_days > max_duration_days:
        return "HIGH"
    if density_are > k_max_are:
        return "WARNING"
    if density_are > (0.8 * k_max_are):
        return "SAFE"
    return "LOW"


def risk_rank(status: str) -> int:
    order = {
        "LOW": 0,
        "SAFE": 1,
        "WARNING": 2,
        "HIGH": 3,
    }
    return order[status]
