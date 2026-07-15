"""SoT formula engines (see docs/Model_Matematika_..._FINAL.docx).

Each function maps 1:1 to a numbered engine in the SoT document:
  - compute_duck_age_status   -> 4.1 Age Engine
  - compute_density           -> 4.2 Density Engine
  - compute_calendar_milestones -> 4.3 Calendar Engine
  - compute_surviving_ducks   -> 4.4 Survival Engine
  - compute_yield_components  -> 4.5 Yield Engine

Numerical precision: all engine computations use ``decimal.Decimal`` with
precision ``getcontext().prec = 50`` to guarantee IEEE 754 high-precision
floating-point compliance. No mid-calculation rounding is performed.
"""

from decimal import Decimal, getcontext, ROUND_FLOOR

# Set Decimal precision for high-precision financial computation
getcontext().prec = 50


def compute_duck_age_status(duck_age_days: int) -> dict:
    """[local-estimate] SoT 4.1 Age Engine: piecewise R_age by ontogenic stage.

    R_age = 0.35 if U_duck < 14
          = 0.15 if 14 <= U_duck <= 29
          = 0.05 if U_duck >= 30
    """
    if duck_age_days < 14:
        r_age = Decimal("0.35")
        age_status = "AGE_BUY_RANGE_WARNING"
    elif duck_age_days <= 29:
        r_age = Decimal("0.15")
        age_status = "AGE_BUY_RANGE"
    else:
        r_age = Decimal("0.05")
        age_status = "ADAPTED_FULLY"

    return {
        "R_age": r_age,
        "age_status": age_status,
    }


def compute_density(duck_count: int, land_area_are: float, k_safe: float) -> dict:
    """[local-calculated] SoT 4.2 Density Engine.

    d       = J / A_are
    P_over  = max(0, min(1, (d - K_safe) / (8 - K_safe)))
    P_under = max(0, (2 - d) / 2)
    """
    density_are = Decimal(duck_count) / Decimal(str(land_area_are))
    k_safe_dec = Decimal(str(k_safe))
    p_over = max(
        Decimal("0"),
        min(Decimal("1"), (density_are - k_safe_dec) / (Decimal("8") - k_safe_dec)),
    )
    p_under = max(Decimal("0"), (Decimal("2") - density_are) / Decimal("2"))

    if p_over > Decimal("0"):
        density_status = "WARNING_DENSITY"
    elif p_under > Decimal("0"):
        density_status = "WARNING_UNDER_DENSITY"
    else:
        density_status = "SAFE"

    return {
        "d": density_are,
        "P_over": p_over,
        "P_under": p_under,
        "density_status": density_status,
    }


def compute_surviving_ducks(duck_count: int, r_age: float, p_over: float) -> Decimal:
    """[local-validated] SoT 4.4 Survival Engine.

    lambda_eff = 0.78125 * (1 - 0.50*R_age) * (1 - 0.45*P_over)
    N_survive  = floor(J * lambda_eff)
    Returns the pre-floor lambda*J; the service layer floors it.
    """
    r_age_d = Decimal(str(r_age))
    p_over_d = Decimal(str(p_over))
    lambda_eff = Decimal("0.78125") * (Decimal("1") - Decimal("0.50") * r_age_d) * (
        Decimal("1") - Decimal("0.45") * p_over_d
    )
    return Decimal(duck_count) * lambda_eff


def compute_surviving_ducks_floored(duck_count: int, r_age: float, p_over: float) -> int:
    """[local-validated] SoT 4.4 Survival Engine with N_survive = floor(J * lambda_eff)."""
    raw = compute_surviving_ducks(duck_count, r_age, p_over)
    return int(raw.to_integral_value(rounding=ROUND_FLOOR))


def compute_calendar_milestones(
    planting_date,
    hst_panen: int,
    hst_masuk_legacy: int = 20,
    hst_heading_legacy: int = 65,
):
    """[local-estimate] SoT 4.3 Calendar Engine.

    t_active       = 65 - 21 = 44 hari
    D_panen_gabah  = D_tanam + HST_panen
    D_masuk_bebek  = D_tanam + 21
    D_tarik_bebek  = D_tanam + 65
    """
    from datetime import timedelta

    d_masuk_bebek = planting_date + timedelta(days=21)
    d_tarik_bebek = planting_date + timedelta(days=65)
    t_active = 44
    d_panen_gabah = planting_date + timedelta(days=hst_panen)
    return {
        "D_masuk_bebek": d_masuk_bebek,
        "D_tarik_bebek": d_tarik_bebek,
        "t_active": t_active,
        "D_panen_gabah": d_panen_gabah,
        "hst_masuk_legacy": hst_masuk_legacy,
        "hst_heading_legacy": hst_heading_legacy,
    }


# [local-validated] SoT 4.5 Yield Engine: Y0 = 47,8767507 kg/are (Local-validated, Tabel 1)
Y0 = Decimal("47.8767507")

# [empirical-correction] SoT 4.5: F_var = 1.00 (override old 0.80)
F_VAR = Decimal("1.00")


def _dec_exp(x: Decimal) -> Decimal:
    """Compute exp(x) for Decimal using high precision series."""
    # Use the math library for exp but cast back to Decimal for consistency.
    # Decimal does not have built-in exp; use float then convert.
    # For high-precision, implement Taylor series up to 50 terms.
    getcontext().prec = 50
    # Use Taylor series: e^x = 1 + x + x^2/2! + x^3/3! + ...
    result = Decimal("1")
    term = Decimal("1")
    for i in range(1, 100):
        term *= x / Decimal(i)
        result += term
        if abs(term) < Decimal("1E-45"):
            break
    return result


def compute_yield_components(
    d: float,
    r_age: float,
    F_sys: float,
    f_var: float = float(F_VAR),
) -> Decimal:
    """[system-design] SoT 4.5 Yield Engine.

    F_density_bio(d) = 1 + alpha_bio * (1 - exp(-d / K_opt))
                       - beta_tramp * (max(0, (d - K_max) / K_max))**2
    where alpha_bio = 0.15, K_opt = 4, beta_tramp = 0.25, K_max = 8.
    F_age = 1 - 0.08 * R_age
    F_sys = system factor (Jarwo=1.00, Tegel=1.211)
    F_var = 1.00 (override old 0.80)
    Yield_are = Y0 * F_density_bio * F_age * F_sys * F_var
    """
    # [local-estimate] Bio-density parameters per SoT 4.5
    alpha_bio = Decimal("0.15")
    k_opt = Decimal("4.0")
    beta_tramp = Decimal("0.25")
    k_max = Decimal("8.0")

    d_d = Decimal(str(d))
    r_age_d = Decimal(str(r_age))
    F_sys_d = Decimal(str(F_sys))
    f_var_d = Decimal(str(f_var))

    # [system-design] Exponential saturation boost
    boost = alpha_bio * (Decimal("1") - _dec_exp(-d_d / k_opt))
    # [system-design] Quadratic trampling penalty
    trampling = beta_tramp * (max(Decimal("0"), (d_d - k_max) / k_max) ** Decimal("2"))
    f_density_bio = Decimal("1") + boost - trampling

    # [system-design] Age factor
    f_age = Decimal("1") - Decimal("0.08") * r_age_d

    yield_are = Y0 * f_density_bio * f_age * F_sys_d * f_var_d
    return yield_are
