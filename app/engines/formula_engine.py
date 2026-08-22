"""SoT formula engines — docs/Model Matematika Data Collection DSS Padi Bebek FINAL.md

Each function maps 1:1 to a numbered engine in the SoT document:
  - compute_age_flag          -> §4  Age Readiness Engine
  - compute_density           -> §5  Density Engine
  - compute_calendar          -> §6  Calendar Engine
  - compute_surviving_ducks   -> §7  Survival Engine
  - compute_yield             -> §8  Yield Engine

SoT §13 Legacy Semantics yang Dilarang pada Production Path:
  R_age, F_age, lambda_eff=0.78125, P_over/P_under as yield multiplier,
  F_density_bio, alpha_bio, beta_tramp, F_sys != 1, feed=4500,
  p_duck_sell=35000, survival floor(J*0.90) for d<=8, etc.

Numerical precision: all computations use decimal.Decimal with prec=50.
No mid-calculation rounding. Conversion to float only at DTO boundary.
"""

from datetime import date, timedelta
from decimal import ROUND_FLOOR, Decimal, getcontext

getcontext().prec = 50

# ---------------------------------------------------------------------------
# SoT §8: Yield Engine — baseline empiris lokal (local-validated)
# ---------------------------------------------------------------------------
Y_BASE = Decimal("47.8767507")

# ---------------------------------------------------------------------------
# SoT §6: Calendar Engine — fixed HST constants
# ---------------------------------------------------------------------------
HST_IN = 21
HST_OUT = 65
T_ACTIVE = 44  # 65 - 21

# Sertani harvest window
HST_PANEN_SERTANI_MIN = 100
HST_PANEN_SERTANI_MAX = 110

# Generic Inpari harvest
HST_PANEN_INPARI = 134

# ---------------------------------------------------------------------------
# SoT §9: Core Economic Engine — production backend constants (not user input)
# ---------------------------------------------------------------------------
P_GABAH_RP_PER_KG = Decimal("6000")
P_DUCK_SELL_RP_PER_DUCK = Decimal("52500")
C_FEED_RP_PER_DUCK_CYCLE = Decimal("20000")

# ---------------------------------------------------------------------------
# SoT §4: Age Readiness Engine
# ---------------------------------------------------------------------------


def compute_age_flag(duck_age_days: int) -> dict:
    """SoT §4: Age Readiness Engine.

    AgeFlag(U_duck) =
        TOO_YOUNG               jika U_duck < 21
        RECOMMENDED             jika 21 <= U_duck <= 30
        ABOVE_RECOMMENDED_AGE   jika U_duck > 30

    Returns dict with 'age_flag' and 'warnings'.
    No R_age, no F_age, no yield/survival/feed multiplier.
    """
    if duck_age_days < 21:
        age_flag = "TOO_YOUNG"
        warnings = [
            "Umur bebek di bawah 21 hari (terlalu muda / di bawah rentang readiness)."
        ]
    elif duck_age_days <= 30:
        age_flag = "RECOMMENDED"
        warnings: list[str] = []
    else:
        age_flag = "ABOVE_RECOMMENDED_AGE"
        warnings = [
            "Umur bebek di atas 30 hari (di atas rentang umur yang direkomendasikan)."
        ]
    return {"age_flag": age_flag, "warnings": warnings}


# ---------------------------------------------------------------------------
# SoT §5: Density Engine
# ---------------------------------------------------------------------------


def compute_density(duck_count: int, land_area_are: float, planting_system: str) -> dict:
    """SoT §5: Density Engine.

    d    = duck_count / land_area_are   (ekor/are)
    d_ha = 100 * d                      (ekor/ha)

    DensityStatus:
        d < 2                              -> UNDER_DENSITY
        jajar_legowo dan 2 <= d <= 4       -> RECOMMENDED
        tegel dan 2 <= d <= 3              -> RECOMMENDED
        di atas ceiling sistem tetapi d <= 8 -> ABOVE_RECOMMENDED
        d > 8                              -> OVERLOAD_HIGH_RISK

    No P_over, no P_under, no yield multiplier.
    """
    d = Decimal(duck_count) / Decimal(str(land_area_are))
    d_ha = Decimal("100") * d

    warnings: list[str] = []

    if d > Decimal("8"):
        density_status = "OVERLOAD_HIGH_RISK"
        warnings.append(
            "Kepadatan > 8 ekor/are: OVERLOAD_HIGH_RISK — pengaruh numerik diterapkan pada Survival Engine."
        )
    elif d < Decimal("2"):
        density_status = "UNDER_DENSITY"
    else:
        # 2 <= d <= 8
        sys = planting_system.strip().lower()
        if sys == "jajar_legowo":
            ceiling = Decimal("4")
        else:
            ceiling = Decimal("3")

        if d <= ceiling:
            density_status = "RECOMMENDED"
        else:
            density_status = "ABOVE_RECOMMENDED"

    return {
        "d": d,
        "d_ha": d_ha,
        "density_status": density_status,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# SoT §6: Calendar Engine
# ---------------------------------------------------------------------------


def compute_calendar(planting_date: date, rice_variety: str) -> dict:
    """SoT §6: Calendar Engine.

    D_in  = planting_date + 21
    D_out = planting_date + 65

    Sertani:
        D_panen_min = planting_date + 100
        D_panen_max = planting_date + 110
        harvest_hst_min = 100
        harvest_hst_max = 110

    Generic Inpari:
        D_panen     = planting_date + 134
        harvest_hst = 134
        + warning generic estimate

    No planting_date fallback, no midpoint, no synthetic date.
    """
    d_in = planting_date + timedelta(days=HST_IN)
    d_out = planting_date + timedelta(days=HST_OUT)
    warnings: list[str] = []

    variety = rice_variety.strip().lower()
    if variety == "inpari":
        harvest_hst_min = HST_PANEN_INPARI
        harvest_hst_max = HST_PANEN_INPARI
        d_panen_min = planting_date + timedelta(days=HST_PANEN_INPARI)
        d_panen_max = d_panen_min
        warnings.append(
            "HST panen Inpari masih generic estimate (134 HST) dan membutuhkan kalibrasi varietas/subvarietas lebih lanjut."
        )
    else:
        # sertani (default)
        harvest_hst_min = HST_PANEN_SERTANI_MIN
        harvest_hst_max = HST_PANEN_SERTANI_MAX
        d_panen_min = planting_date + timedelta(days=HST_PANEN_SERTANI_MIN)
        d_panen_max = planting_date + timedelta(days=HST_PANEN_SERTANI_MAX)

    return {
        "HST_in": HST_IN,
        "HST_out": HST_OUT,
        "t_active": T_ACTIVE,
        "D_in": d_in,
        "D_out": d_out,
        "harvest_hst_min": harvest_hst_min,
        "harvest_hst_max": harvest_hst_max,
        "D_panen_min": d_panen_min,
        "D_panen_max": d_panen_max,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# SoT §7: Survival Engine
# ---------------------------------------------------------------------------


def compute_surviving_ducks(duck_count: int, d: Decimal) -> int:
    """SoT §7: Survival Engine.

    N_survive =
        duck_count              jika d <= 8
        floor(0.60 * duck_count) jika d > 8

    No lambda_eff, no 0.78125, no R_age multiplier, no P_over multiplier.
    No 90% normal survival.
    """
    if d > Decimal("8"):
        raw = Decimal("0.60") * Decimal(duck_count)
        return int(raw.to_integral_value(rounding=ROUND_FLOOR))
    else:
        return duck_count


# ---------------------------------------------------------------------------
# SoT §8: Yield Engine
# ---------------------------------------------------------------------------


def compute_yield(land_area_are: float) -> dict:
    """SoT §8: Yield Engine.

    Y_base = 47.8767507 kg/are (local-validated baseline)

    F_sys_JARWO_2_1 = 1  (system-neutral)
    F_sys_TEGEL     = 1  (system-neutral)
    F_var_SERTANI   = 1  (variety-neutral)
    F_var_INPARI    = 1  (variety-neutral)

    Yield_are_pred   = 47.8767507
    Yield_total_pred = 47.8767507 * land_area_are

    No F_density_bio, no F_age, no alpha_bio, no beta_tramp.
    No density yield multiplier. No variety yield multiplier.
    """
    land_area_d = Decimal(str(land_area_are))
    yield_are_pred = Y_BASE
    yield_total_pred = yield_are_pred * land_area_d
    return {
        "Yield_are_pred": yield_are_pred,
        "Yield_total_pred": yield_total_pred,
    }


# ---------------------------------------------------------------------------
# SoT §9: Core Economic Engine
# ---------------------------------------------------------------------------


def compute_core_economics(
    *,
    yield_total_pred: Decimal,
    n_survive: int,
    duck_count: int,
    p_duck_buy: float,
) -> dict:
    """SoT §9: Core Economic Engine.

    Revenue_gabah          = Yield_total_pred * 6000
    Revenue_duck_potential = N_survive * 52500
    Cost_duck_buy          = duck_count * p_duck_buy
    Cost_feed              = duck_count * 20000
    Core_Cash_Cost         = Cost_duck_buy + Cost_feed
    Total_Revenue_DSS      = Revenue_gabah + Revenue_duck_potential
    Net_Cash_Contribution_DSS = Total_Revenue_DSS - Core_Cash_Cost

    p_duck_buy=0 is valid (no current-cycle cash purchase).
    No fallback Rp25000. No fertilizer/pesticide/infrastructure in Core.
    """
    p_buy_d = Decimal(str(p_duck_buy))
    duck_count_d = Decimal(duck_count)

    revenue_gabah = yield_total_pred * P_GABAH_RP_PER_KG
    revenue_duck_potential = Decimal(n_survive) * P_DUCK_SELL_RP_PER_DUCK

    cost_duck_buy = duck_count_d * p_buy_d
    cost_feed = duck_count_d * C_FEED_RP_PER_DUCK_CYCLE

    core_cash_cost = cost_duck_buy + cost_feed
    total_revenue_dss = revenue_gabah + revenue_duck_potential
    net_cash_contribution_dss = total_revenue_dss - core_cash_cost

    return {
        "Revenue_gabah": revenue_gabah,
        "Revenue_duck_potential": revenue_duck_potential,
        "Cost_duck_buy": cost_duck_buy,
        "Cost_feed": cost_feed,
        "Core_Cash_Cost": core_cash_cost,
        "Total_Revenue_DSS": total_revenue_dss,
        "Net_Cash_Contribution_DSS": net_cash_contribution_dss,
    }
