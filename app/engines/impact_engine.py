import math
from app.domain.models import DSSConstants


# ---------------------------------------------------------------------------
# Fase 2 — Cost Engine
# SoT ref: Tabel 2.2 (Cost Engine) + Catatan Finalisasi poin 9, 10, 11.
# Guardrails: ``Cost_feed`` and ``Cost_infra`` total scale MUST NOT change.
# ---------------------------------------------------------------------------

# Konstanta kalibrasi (Tabel 2.2 Cost Engine).
K_WEED_HIRE_RP_PER_ARE = 30539.0       # Rp/are — n=1, baris Excel #64.
INFRA_CAGE_COEF = 8333.0               # 0,5 * 8.333 (Tabel 2.2).
INFRA_NET_COEF = 49435.0               # 0,5 * 49.435 (Tabel 2.2).
INFRA_FLOOR_RP = 58333.0               # max(58.333, ...) — Tabel 2.2.
RHO_WEED = 0.29                        # Median data weeding positif / total labor.


def compute_weed_reduction(density_are: float) -> float:
    """R_weed(d) = 0.95 * (1 - exp(-0.35 * d)). Tabel 2.2."""
    return 0.95 * (1.0 - math.exp(-0.35 * density_are))


def compute_weed_hired_cost(land_area_are: float, density_are: float) -> float:
    """C_weed_hired = k_weed_hire * A_are * (1 - R_weed(d)). Tabel 2.2."""
    return K_WEED_HIRE_RP_PER_ARE * land_area_are * (1.0 - compute_weed_reduction(density_are))


def compute_labor_breakdown(
    land_area_are: float,
    p_over: float,
    r_age: float,
    density_are: float,
) -> dict:
    """Return Cost_labor breakdown (Tabel 2.2 Cost Engine).

    - ``Cost_labor_base``       = 47527 * A_are
    - ``Cost_labor_weed_hired`` = 30539 * A_are * (1 - R_weed(d))
    - ``Cost_labor_total``      = base + weed_hired

    Note: Cost_labor_tending dihapus permanen (Catatan Finalisasi poin 12, FINAL_BANGET.md).
    """
    cost_labor_base = 47527.0 * land_area_are
    cost_labor_weed_hired = compute_weed_hired_cost(land_area_are, density_are)
    cost_labor_total = cost_labor_base + cost_labor_weed_hired
    return {
        "Cost_labor_base": cost_labor_base,
        "Cost_labor_weed_hired": cost_labor_weed_hired,
        "Cost_labor_total": cost_labor_total,
    }


def compute_infrastructure_breakdown(duck_count: int, land_area_are: float) -> dict:
    """C_infra = max(58.333, raw_net + raw_cage). Both raw parts scaled
    proportionally if the raw sum is below the floor (and > 0).

    Edge case ``raw_net + raw_cage == 0`` (extremely small A/J): split the
    floor 50/50. This is an interim decision pending riset confirmation
    (see Fase 5 open question).
    """
    raw_net = 0.5 * INFRA_NET_COEF * math.sqrt(max(land_area_are, 0.0))
    raw_cage = 0.5 * INFRA_CAGE_COEF * duck_count
    raw_sum = raw_net + raw_cage

    if raw_sum <= 0:
        return {
            "Cost_infra_net": INFRA_FLOOR_RP / 2.0,
            "Cost_infra_cage": INFRA_FLOOR_RP / 2.0,
            "Cost_infra": INFRA_FLOOR_RP,
        }

    if raw_sum < INFRA_FLOOR_RP:
        scale = INFRA_FLOOR_RP / raw_sum
        return {
            "Cost_infra_net": raw_net * scale,
            "Cost_infra_cage": raw_cage * scale,
            "Cost_infra": INFRA_FLOOR_RP,
        }

    return {
        "Cost_infra_net": raw_net,
        "Cost_infra_cage": raw_cage,
        "Cost_infra": raw_sum,
    }


def compute_feed_costs(duck_count: int, p_over: float, r_age: float) -> float:
    """Cost_feed — Tabel 2.2. MUST NOT be rescaled (Catatan Finalisasi poin 9)."""
    return duck_count * 5000.0 * (1.0 + 0.75 * p_over + 0.50 * r_age)


def compute_ecology_weed(
    cost_labor_base: float,
    density_are: float,
    p_over: float,
) -> float:
    """V_weed_eco = (0.29 * Cost_labor_base) * R_weed(d) * (1 - 0.25 * P_over).

    Note (Catatan Finalisasi poin 10): basis is ``Cost_labor_base``
    (base, excluding ``C_weed_hired`` and tending) to avoid double-counting
    with the cost-saving component.
    """
    return (
        (RHO_WEED * cost_labor_base)
        * compute_weed_reduction(density_are)
        * (1.0 - 0.25 * p_over)
    )


def compute_soil_nutrients(duck_count: int, t_active: int, lambda_eff: float, n_need: float, p_need: float, k_need: float, constants: DSSConstants) -> dict:
    if t_active > 30:
        n_duck = max(0.0, 0.02 * t_active - 0.6) * 0.107 * (duck_count * lambda_eff)
    else:
        n_duck = 0.0

    sub_base = 0.28
    if t_active == 44:
        sub_base = 0.28
    else:
        sub_base = max(0.0, 0.02 * t_active - 0.6)

    p_duck = sub_base * 0.424 * (duck_count * lambda_eff)
    k_duck = sub_base * 0.058 * (duck_count * lambda_eff)

    n_rem = max(0.0, n_need - n_duck)
    p_rem = max(0.0, p_need - p_duck)
    k_rem = max(0.0, k_need - k_duck)

    q_phonska = p_rem / 0.04364 if p_rem > 0 else 0.0
    q_urea = max(0.0, n_rem - (q_phonska * 0.15)) / 0.46
    q_kcl = max(0.0, k_rem - (q_phonska * 0.09961)) / 0.49806

    cost_fert_phonska = q_phonska * constants.HET_phonska
    cost_fert_urea = q_urea * constants.HET_urea
    cost_fert_kcl = q_kcl * constants.HET_kcl
    cost_fertilizer_total = cost_fert_phonska + cost_fert_urea + cost_fert_kcl

    return {
        "Cost_fertilizer_total": cost_fertilizer_total,
        "Cost_fert_urea": cost_fert_urea,
        "Cost_fert_phonska": cost_fert_phonska,
        "Cost_fert_kcl": cost_fert_kcl,
        "Q_phonska": q_phonska,
        "Q_urea": q_urea,
        "Q_kcl": q_kcl
    }

