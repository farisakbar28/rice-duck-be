"""SoT impact engines (see docs/Model_Matematika_..._FINAL.docx).

Each function maps 1:1 to a numbered engine in the SoT document:
  - compute_weed_reduction / compute_weed_hired_cost  -> 4.7 Cost Engine
  - compute_labor_breakdown                            -> 4.7 Cost Engine (isolated)
  - compute_infrastructure_breakdown                  -> 4.7 Cost Engine (isolated)
  - compute_feed_costs                                -> 4.7 Cost Engine (isolated)
  - compute_soil_nutrients                            -> 4.6 Material Engine
  - compute_ecology_weed                              -> 4.8 Ecology Engine

All components in this module belong to the SoT "Empirically Uncorrelated
Isolated Components" group (Bagian 5.2) or are ecological/soil flow inputs.
They MUST NOT participate in the core Profit_net_cash aggregation.
"""

import math
from app.domain.models import DSSConstants


# ---------------------------------------------------------------------------
# SoT 4.7 Cost Engine — constants
# ---------------------------------------------------------------------------

# Tabel 1 SoT: k_weed_hire = Rp26.178/are (Local-estimate)
K_WEED_HIRE_RP_PER_ARE = 26178.0

# Tabel 1 SoT: C_pest_base = Rp2.135/are (Local-estimate)
C_PEST_BASE_RP_PER_ARE = 2135.0

# SoT 4.7: Cost_infra_net = 0,5 * 289.260 * sqrt(A_are)
INFRA_NET_COEF = 289260.0

# SoT 4.7: Cost_infra_cage = Rp175.000/siklus (flat)
INFRA_CAGE_FLAT_RP = 175000.0

# SoT 4.7: C_feed = J * 4.500 * (1 + 0,75*P_over + 0,50*R_age)
C_FEED_BASE_RP_PER_DUCK = 4500.0
C_FEED_COEFF_P_OVER = 0.75
C_FEED_COEFF_R_AGE = 0.50

# SoT 4.7: C_fert = Q_phonska * 1.840 + Q_urea * 1.800 + Q_kcl * 9.500
# (HET regulatory-locked, see DSSConstants.HET_*)

# SoT 4.8: V_weed_eco = 13.500 * A_are * R_weed(d) * (1 - 0,25*P_over)
V_WEED_ECO_BASE_RP_PER_ARE = 13500.0

# SoT 4.7: R_weed(d) = 0,93 * (1 - exp(-0,35*d))
# SoT 4.7: R_pest(d)  = 0,80 * (1 - exp(-0,35*d))
R_WEED_ASYMPTOTE = 0.93
R_PEST_ASYMPTOTE = 0.80
R_DECAY_RATE = 0.35


# ---------------------------------------------------------------------------
# SoT 4.6 Material Engine — kappa constants
# ---------------------------------------------------------------------------
# Xiong et al. 2014 (cycle reference 80 days), also used in Tabel 1
# as literature-anchored base values for the per-ekor nutrient pool.
# (The SoT classifies the temporal linearisation (0.02, -0.6) as
# literature-uncalibrated; the kappa values themselves are referenced.)
KAPPA_N = 0.049
KAPPA_P = 0.072
KAPPA_K = 0.032

# SoT 4.6 elemental content of Phonska (basis unsur murni, from oxide conversion)
PHONSKA_N_FRACTION = 0.15
PHONSKA_P_FRACTION = 0.04364   # P2O5 10% * 0.4364
PHONSKA_K_FRACTION = 0.09961   # K2O 12% * 0.8301
UREA_N_FRACTION = 0.46
KCL_K_FRACTION = 0.49806       # K2O 60% * 0.8301


# ---------------------------------------------------------------------------
# SoT 4.7 Cost Engine — functions (Isolated Components)
# ---------------------------------------------------------------------------

def compute_weed_reduction(density_are: float) -> float:
    """SoT 4.7: R_weed(d) = 0,93 * (1 - exp(-0,35*d))."""
    return R_WEED_ASYMPTOTE * (1.0 - math.exp(-R_DECAY_RATE * density_are))


def compute_pest_reduction(density_are: float) -> float:
    """SoT 4.7: R_pest(d) = 0,80 * (1 - exp(-0,35*d))."""
    return R_PEST_ASYMPTOTE * (1.0 - math.exp(-R_DECAY_RATE * density_are))


def compute_weed_hired_cost(land_area_are: float, density_are: float) -> float:
    """SoT 4.7: Cost_labor_weeding = k_weed_hire * A_are * (1 - R_weed(d))."""
    return (
        K_WEED_HIRE_RP_PER_ARE
        * land_area_are
        * (1.0 - compute_weed_reduction(density_are))
    )


def compute_pesticide_cost(land_area_are: float, density_are: float) -> float:
    """SoT 4.7: Cost_pesticide = C_pest_base * A_are * (1 - R_pest(d))."""
    return (
        C_PEST_BASE_RP_PER_ARE
        * land_area_are
        * (1.0 - compute_pest_reduction(density_are))
    )


def compute_labor_breakdown(
    land_area_are: float,
    p_over: float,
    r_age: float,
    density_are: float,
) -> dict:
    """SoT 4.7 (Isolated): Cost_labor_weeding = k_weed_hire * A_are * (1 - R_weed(d)).

    Returns a single ``Cost_labor_weeding`` slot for the Isolated output group.
    """
    return {
        "Cost_labor_weeding": compute_weed_hired_cost(land_area_are, density_are),
    }


def compute_infrastructure_breakdown(duck_count: int, land_area_are: float) -> dict:
    """SoT 4.7 (Isolated): C_infra = Cost_infra_net + Cost_infra_cage.

    Cost_infra_net = 0,5 * 289.260 * sqrt(A_are)
    Cost_infra_cage = Rp175.000/siklus (flat)
    """
    raw_net = 0.5 * INFRA_NET_COEF * math.sqrt(max(land_area_are, 0.0))
    raw_cage = float(INFRA_CAGE_FLAT_RP)
    return {
        "Cost_infra_net": raw_net,
        "Cost_infra_cage": raw_cage,
        "Cost_infra": raw_net + raw_cage,
    }


def compute_feed_costs(duck_count: int, p_over: float, r_age: float) -> float:
    """SoT 4.7 (Isolated): C_feed = J * 4.500 * (1 + 0,75*P_over + 0,50*R_age)."""
    return (
        duck_count
        * C_FEED_BASE_RP_PER_DUCK
        * (1.0 + C_FEED_COEFF_P_OVER * p_over + C_FEED_COEFF_R_AGE * r_age)
    )


# ---------------------------------------------------------------------------
# SoT 4.8 Ecology Engine
# ---------------------------------------------------------------------------

def compute_ecology_weed(
    land_area_are: float,
    density_are: float,
    p_over: float,
) -> float:
    """SoT 4.8: V_weed_eco = 13.500 * A_are * R_weed(d) * (1 - 0,25*P_over)."""
    return (
        V_WEED_ECO_BASE_RP_PER_ARE
        * land_area_are
        * compute_weed_reduction(density_are)
        * (1.0 - 0.25 * p_over)
    )


# ---------------------------------------------------------------------------
# SoT 4.6 Material Engine
# ---------------------------------------------------------------------------

def compute_soil_nutrients(
    duck_count: int,
    t_active: int,
    lambda_eff: float,
    n_need: float,
    p_need: float,
    k_need: float,
    constants: DSSConstants,
) -> dict:
    """SoT 4.6 Material Engine.

    N_duck = max(0, 0,02*t_active - 0,6) * kappa_N * (J * lambda_eff)
    P_duck = max(0, 0,02*t_active - 0,6) * kappa_P * (J * lambda_eff)
    K_duck = max(0, 0,02*t_active - 0,6) * kappa_K * (J * lambda_eff)

    Then least-cost mapping:
        Q_phonska = P_rem / 0.04364
        Q_urea    = max(0, N_rem - Q_phonska * 0.15) / 0.46
        Q_kcl     = max(0, K_rem - Q_phonska * 0.09961) / 0.49806

    C_fert = Q_phonska*1.840 + Q_urea*1.800 + Q_kcl*9.500  (via HET_*)
    """
    sub_base = max(0.0, 0.02 * t_active - 0.6)
    survivors = duck_count * lambda_eff

    n_duck = sub_base * KAPPA_N * survivors
    p_duck = sub_base * KAPPA_P * survivors
    k_duck = sub_base * KAPPA_K * survivors

    n_rem = max(0.0, n_need - n_duck)
    p_rem = max(0.0, p_need - p_duck)
    k_rem = max(0.0, k_need - k_duck)

    q_phonska = p_rem / PHONSKA_P_FRACTION if p_rem > 0 else 0.0
    q_urea = max(0.0, n_rem - (q_phonska * PHONSKA_N_FRACTION)) / UREA_N_FRACTION
    q_kcl = max(0.0, k_rem - (q_phonska * PHONSKA_K_FRACTION)) / KCL_K_FRACTION

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
        "Q_kcl": q_kcl,
    }
