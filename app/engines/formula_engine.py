"""SoT formula engines (see docs/Model_Matematika_..._FINAL.docx).

Each function maps 1:1 to a numbered engine in the SoT document:
  - compute_duck_age_status   -> 4.1 Age Engine
  - compute_density           -> 4.2 Density Engine
  - compute_calendar_milestones -> 4.3 Calendar Engine
  - compute_surviving_ducks   -> 4.4 Survival Engine
  - compute_yield_components  -> 4.5 Yield Engine
"""

import math


def compute_duck_age_status(duck_age_days: int) -> dict:
    """SoT 4.1 Age Engine: piecewise R_age by ontogenic stage.

    R_age = 0.35 if U_duck < 14
          = 0.15 if 14 <= U_duck <= 29
          = 0.05 if U_duck >= 30
    """
    if duck_age_days < 14:
        r_age = 0.35
        age_status = "AGE_BUY_RANGE_WARNING"
    elif duck_age_days <= 29:
        r_age = 0.15
        age_status = "AGE_BUY_RANGE"
    else:
        r_age = 0.05
        age_status = "ADAPTED_FULLY"

    return {
        "R_age": r_age,
        "age_status": age_status,
    }


def compute_density(duck_count: int, land_area_are: float, k_safe: float) -> dict:
    """SoT 4.2 Density Engine.

    d       = J / A_are
    P_over  = max(0, min(1, (d - K_safe) / (8 - K_safe)))
    P_under = max(0, (2 - d) / 2)
    """
    density_are = duck_count / land_area_are
    p_over = max(0.0, min(1.0, (density_are - k_safe) / (8.0 - k_safe)))
    p_under = max(0.0, (2.0 - density_are) / 2.0)

    if p_over > 0:
        density_status = "WARNING_DENSITY"
    elif p_under > 0:
        density_status = "WARNING_UNDER_DENSITY"
    else:
        density_status = "SAFE"

    return {
        "d": density_are,
        "P_over": p_over,
        "P_under": p_under,
        "density_status": density_status,
    }


def compute_surviving_ducks(duck_count: int, r_age: float, p_over: float) -> float:
    """SoT 4.4 Survival Engine.

    lambda_eff = 0.78125 * (1 - 0.50*R_age) * (1 - 0.45*P_over)
    N_survive  = floor(J * lambda_eff)
    Returns the pre-floor lambda*J; the service layer floors it.
    """
    lambda_eff = 0.78125 * (1.0 - 0.50 * r_age) * (1.0 - 0.45 * p_over)
    return duck_count * lambda_eff


def compute_surviving_ducks_floored(duck_count: int, r_age: float, p_over: float) -> int:
    """SoT 4.4 Survival Engine with N_survive = floor(J * lambda_eff)."""
    return math.floor(compute_surviving_ducks(duck_count, r_age, p_over))


def compute_calendar_milestones(
    planting_date,
    hst_panen: int,
    hst_masuk_legacy: int = 20,
    hst_heading_legacy: int = 65,
):
    """SoT 4.3 Calendar Engine.

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


# SoT 4.5 Yield Engine: Y0 = 47,8767507 kg/are (Local-validated, Tabel 1)
Y0 = 47.8767507

# SoT 4.5: F_var = 0,80 (system-design, Tabel 1)
F_VAR_DEFAULT = 0.80


def compute_yield_components(
    p_under: float,
    p_over: float,
    r_age: float,
    F_sys: float,
    f_var: float = F_VAR_DEFAULT,
) -> float:
    """SoT 4.5 Yield Engine.

    F_density = 1 - 0.12*P_under - 0.25*P_over
    F_age     = 1 - 0.08*R_age
    F_sys     = 1.00 (Jarwo) or 1.211 (Tegel)
    F_var     = 0.80
    Yield_are = Y0 * F_density * F_age * F_sys * F_var
    """
    f_density = 1.0 - 0.12 * p_under - 0.25 * p_over
    f_age = 1.0 - 0.08 * r_age
    yield_are = Y0 * f_density * f_age * F_sys * f_var
    return yield_are
