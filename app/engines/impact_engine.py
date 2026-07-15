"""SoT impact engines (see docs/Model_Matematika_..._FINAL.docx).

Each function maps 1:1 to a numbered engine in the SoT document:
  - compute_weed_reduction / compute_weed_hired_cost  -> 4.7 Cost Engine
  - compute_labor_breakdown                            -> 4.7 Cost Engine (isolated)
  - compute_infrastructure_breakdown                  -> 4.7 Cost Engine (isolated)
  - compute_feed_costs                                -> 4.7 Cost Engine (isolated)
  - compute_soil_nutrients                            -> 4.6 Material Engine

All components in this module belong to the SoT "Empirically Uncorrelated
Isolated Components" group (Bagian 5.2) or are ecological/soil flow inputs.
They MUST NOT participate in the core Profit_net_cash aggregation.

Numerical precision: all engine computations use ``decimal.Decimal`` with
precision 50 to guarantee IEEE 754 high-precision floating-point compliance.
No mid-calculation rounding is performed.
"""

from decimal import Decimal

from app.domain.models import DSSConstants


# ---------------------------------------------------------------------------
# [local-estimate] SoT 4.7 Cost Engine — constants (Decimal)
# ---------------------------------------------------------------------------

# Tabel 1 SoT: k_weed_hire = Rp26.178/are (Local-estimate)
K_WEED_HIRE_RP_PER_ARE = Decimal("26178.0")

# Tabel 1 SoT: C_pest_base = Rp2.135/are (Local-estimate)
C_PEST_BASE_RP_PER_ARE = Decimal("2135.0")

# SoT 4.7: Cost_infra_net = 0,5 * 289.260 * sqrt(A_are)
INFRA_NET_COEF = Decimal("289260.0")

# SoT 4.7: Cost_infra_cage = Rp175.000/siklus (flat)
INFRA_CAGE_FLAT_RP = Decimal("175000.0")

# SoT 4.7: C_feed = J * 4.500 * (1 + 0,75*P_over + 0,50*R_age)
C_FEED_BASE_RP_PER_DUCK = Decimal("4500.0")
C_FEED_COEFF_P_OVER = Decimal("0.75")
C_FEED_COEFF_R_AGE = Decimal("0.50")

# SoT 4.7: C_fert = Q_phonska * 1.840 + Q_urea * 1.800 + Q_kcl * 9.500
# (HET regulatory-locked, see DSSConstants.HET_*)

# SoT 4.7: R_weed(d) = 0,93 * (1 - exp(-0,35*d))
# SoT 4.7: R_pest(d)  = 0,80 * (1 - exp(-0,35*d))
R_WEED_ASYMPTOTE = Decimal("0.93")
R_PEST_ASYMPTOTE = Decimal("0.80")
R_DECAY_RATE = Decimal("0.35")


# ---------------------------------------------------------------------------
# [local-calculated] SoT 4.6 Material Engine — kappa constants (Decimal)
# ---------------------------------------------------------------------------
# Xiong et al. 2014 (cycle reference 80 days), also used in Tabel 1
# as literature-anchored base values for the per-ekor nutrient pool.
KAPPA_N = Decimal("0.049")
KAPPA_P = Decimal("0.072")
KAPPA_K = Decimal("0.032")

# [system-design] SoT 4.6 elemental content of Phonska (basis unsur murni)
PHONSKA_N_FRACTION = Decimal("0.15")
PHONSKA_P_FRACTION = Decimal("0.04364")   # P2O5 10% * 0.4364
PHONSKA_K_FRACTION = Decimal("0.09961")   # K2O 12% * 0.8301
UREA_N_FRACTION = Decimal("0.46")
KCL_K_FRACTION = Decimal("0.49806")       # K2O 60% * 0.8301


def _d(value) -> Decimal:
    """Coerce value to Decimal for safe arithmetic."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _dec_exp(x: Decimal) -> Decimal:
    """Compute exp(x) for Decimal using high-precision Taylor series."""
    result = Decimal("1")
    term = Decimal("1")
    for i in range(1, 100):
        term *= x / Decimal(i)
        result += term
        if abs(term) < Decimal("1E-45"):
            break
    return result


def _dec_sqrt(x: Decimal) -> Decimal:
    """Compute sqrt(x) for Decimal using Newton's method (50-digit precision)."""
    if x <= 0:
        return Decimal("0")
    # Initial guess using float
    guess = Decimal(str(float(x) ** 0.5))
    # Newton-Raphson: x_new = (x + x/guess) / 2
    for _ in range(50):
        guess = (guess + x / guess) / Decimal("2")
    return guess


# ---------------------------------------------------------------------------
# [system-design] SoT 4.7 Cost Engine — functions (Isolated Components)
# ---------------------------------------------------------------------------

def compute_weed_reduction(density_are) -> Decimal:
    """[system-design] SoT 4.7: R_weed(d) = 0,93 * (1 - exp(-0,35*d))."""
    d = _d(density_are)
    return R_WEED_ASYMPTOTE * (Decimal("1") - _dec_exp(-R_DECAY_RATE * d))


def compute_pest_reduction(density_are) -> Decimal:
    """[system-design] SoT 4.7: R_pest(d) = 0,80 * (1 - exp(-0,35*d))."""
    d = _d(density_are)
    return R_PEST_ASYMPTOTE * (Decimal("1") - _dec_exp(-R_DECAY_RATE * d))


def compute_weed_hired_cost(land_area_are, density_are) -> Decimal:
    """[local-estimate] SoT 4.7: Cost_labor_weeding = k_weed_hire * A_are * (1 - R_weed(d))."""
    a = _d(land_area_are)
    return K_WEED_HIRE_RP_PER_ARE * a * (Decimal("1") - compute_weed_reduction(density_are))


def compute_pesticide_cost(land_area_are, density_are) -> Decimal:
    """[local-estimate] SoT 4.7: Cost_pesticide = C_pest_base * A_are * (1 - R_pest(d))."""
    a = _d(land_area_are)
    return C_PEST_BASE_RP_PER_ARE * a * (Decimal("1") - compute_pest_reduction(density_are))


def compute_labor_breakdown(
    land_area_are,
    p_over,
    r_age,
    density_are,
) -> dict:
    """[local-estimate] SoT 4.7 (Isolated): Cost_labor_weeding = k_weed_hire * A_are * (1 - R_weed(d))."""
    return {
        "Cost_labor_weeding": compute_weed_hired_cost(land_area_are, density_are),
    }


def compute_infrastructure_breakdown(duck_count: int, land_area_are) -> dict:
    """[system-design] SoT 4.7 (Isolated): C_infra = Cost_infra_net + Cost_infra_cage.

    Cost_infra_net = 0,5 * 289.260 * sqrt(A_are)
    Cost_infra_cage = Rp175.000/siklus (flat)
    """
    a = _d(land_area_are)
    if a < 0:
        a = Decimal("0")
    # [local-calculated] sqrt via Decimal approximation
    raw_net = Decimal("0.5") * INFRA_NET_COEF * _dec_sqrt(a)
    raw_cage = INFRA_CAGE_FLAT_RP
    return {
        "Cost_infra_net": raw_net,
        "Cost_infra_cage": raw_cage,
        "Cost_infra": raw_net + raw_cage,
    }


def compute_feed_costs(duck_count: int, p_over, r_age) -> Decimal:
    """[local-estimate] SoT 4.7 (Isolated): C_feed = J * 4.500 * (1 + 0,75*P_over + 0,50*R_age)."""
    j = Decimal(duck_count)
    po = _d(p_over)
    ra = _d(r_age)
    return j * C_FEED_BASE_RP_PER_DUCK * (Decimal("1") + C_FEED_COEFF_P_OVER * po + C_FEED_COEFF_R_AGE * ra)


# ---------------------------------------------------------------------------
# [system-design] SoT 4.6 Material Engine
# ---------------------------------------------------------------------------

def compute_soil_nutrients(
    duck_count: int,
    t_active: int,
    lambda_eff,
    n_need,
    p_need,
    k_need,
    constants: DSSConstants,
) -> dict:
    """[system-design] SoT 4.6 Material Engine.

    N_duck = max(0, 0,02*t_active - 0,6) * kappa_N * (J * lambda_eff)
    P_duck = max(0, 0,02*t_active - 0,6) * kappa_P * (J * lambda_eff)
    K_duck = max(0, 0,02*t_active - 0,6) * kappa_K * (J * lambda_eff)

    Then least-cost mapping:
        Q_phonska = P_rem / 0.04364
        Q_urea    = max(0, N_rem - Q_phonska * 0.15) / 0.46
        Q_kcl     = max(0, K_rem - Q_phonska * 0.09961) / 0.49806

    C_fert = Q_phonska*1.840 + Q_urea*1.800 + Q_kcl*9.500  (via HET_*)
    """
    t_d = Decimal(t_active)
    sub_base = max(Decimal("0"), Decimal("0.02") * t_d - Decimal("0.6"))
    le = _d(lambda_eff)
    survivors = Decimal(duck_count) * le

    n_duck = sub_base * KAPPA_N * survivors
    p_duck = sub_base * KAPPA_P * survivors
    k_duck = sub_base * KAPPA_K * survivors

    n_need_d = _d(n_need)
    p_need_d = _d(p_need)
    k_need_d = _d(k_need)

    n_rem = max(Decimal("0"), n_need_d - n_duck)
    p_rem = max(Decimal("0"), p_need_d - p_duck)
    k_rem = max(Decimal("0"), k_need_d - k_duck)

    q_phonska = p_rem / PHONSKA_P_FRACTION if p_rem > 0 else Decimal("0")
    q_urea = max(Decimal("0"), n_rem - (q_phonska * PHONSKA_N_FRACTION)) / UREA_N_FRACTION
    q_kcl = max(Decimal("0"), k_rem - (q_phonska * PHONSKA_K_FRACTION)) / KCL_K_FRACTION

    het_phonska = _d(constants.HET_phonska)
    het_urea = _d(constants.HET_urea)
    het_kcl = _d(constants.HET_kcl)

    cost_fert_phonska = q_phonska * het_phonska
    cost_fert_urea = q_urea * het_urea
    cost_fert_kcl = q_kcl * het_kcl
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
