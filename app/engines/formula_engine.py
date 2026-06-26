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
    """Yield basis literatur (kg/ha note). d_lit_ha = d_aktual_are * 100.

    Rev 2: rumus ini memakai d_lit_ha sebagai catatan konversi rumus literatur.
    Output utama DSS memakai x_base_kg_are = x_base_kg_ha_note / 100.
    """
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
    """Compute yield. Returns (x_base_kg_ha_note, penalty_rate, x_penalized_kg_ha_note, x_final_kg_ha_note).

    Rev 2: semua nilai dalam kg/ha adalah catatan (note) untuk rumus literatur.
    Output utama = x_final_kg_are = x_final_kg_ha_note / 100.
    d_lit_ha = d_aktual_are * 100 digunakan hanya untuk rumus Xiong/backbone.
    """
    density_ha = density_are * 100.0  # d_lit_ha — catatan konversi untuk rumus literatur
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
    """Convert yield dari kg/ha (note) ke kg/are (utama) dan total kg.

    Rev 2: x_final_kg_are = x_final_kg_ha_note / 100 adalah output utama petani.
    x_final_ton_ha_note = x_final_kg_are / 10 (catatan ton/ha untuk pembanding).
    estimated_total_kg = x_final_kg_are * A_are.
    """
    kg_per_are = final_yield_kg_per_ha / 100.0  # x_final_kg_are = x_final_kg_ha_note / 100
    estimated_total_kg = kg_per_are * land_area_are  # total = x_final_kg_are * A_are
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


_REY_NOTES = (
    "REY (Rice Equivalent Yield) memiliki minimal 5 variasi notasi di literatur "
    "yang secara konsep setara — A17: 'Rice Equivalent Yield', A08: 'REY', "
    "A19: 'Grain Equivalent Yield (GEY)', A18: 'Rice Equivalent Production', "
    "B5A06: 'Land Equivalent Ratio-based yield'. "
    "Implementasi ini mengikuti rumus dari dokumen model matematis (Rev1_Doc): "
    "REY = Σ(Y_i * P_i) / P_rice."
)


def compute_rey(
    *,
    rice_yield_kg: float | None,
    rice_price_rp_per_kg: float | None,
    duck_revenue_rp: float | None,
    rice_reference_price_rp_per_kg: float | None,
) -> dict:
    """REY = Σ(Y_i * P_i) / P_rice  (Rev1_Doc)

    Komponen:
      - Y_rice * P_rice_RD  (nilai produksi padi padi-bebek)
      - Y_duck_revenue       (pendapatan bebek = N_d * p_duck)
    Dibagi P_rice_reference untuk konversi ke setara beras.

    Returns dict:
        rey:           float | None
        rey_status:    "calculated" | "missing_params"
        missing_params: list[str]
        rey_notes:     str  — catatan variasi notasi di literatur
    """
    missing: list[str] = []
    if rice_yield_kg is None:
        missing.append("rice_yield_kg")
    if rice_price_rp_per_kg is None:
        missing.append("rice_price_rp_per_kg")
    if duck_revenue_rp is None:
        missing.append("duck_revenue_rp")
    if rice_reference_price_rp_per_kg is None:
        missing.append("rice_reference_price_rp_per_kg")

    if missing or (rice_reference_price_rp_per_kg is not None and rice_reference_price_rp_per_kg == 0):
        return {
            "rey": None,
            "rey_status": "missing_params",
            "missing_params": missing or ["rice_reference_price_rp_per_kg_is_zero"],
            "rey_notes": _REY_NOTES,
        }

    # Σ(Y_i * P_i) = nilai padi + pendapatan bebek
    total_value = (rice_yield_kg * rice_price_rp_per_kg) + duck_revenue_rp  # type: ignore[operator]
    rey = total_value / rice_reference_price_rp_per_kg  # type: ignore[operator]
    return {
        "rey": rey,
        "rey_status": "calculated",
        "missing_params": [],
        "rey_notes": _REY_NOTES,
    }
