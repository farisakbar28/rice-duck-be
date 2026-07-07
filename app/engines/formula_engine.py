def compute_duck_age_status(duck_age_days: int) -> dict:
    if duck_age_days < 14:
        r_age = 0.35
        age_status = "AGE_BUY_RANGE_WARNING"
    elif duck_age_days <= 20:
        r_age = 0.15
        age_status = "AGE_BUY_RANGE"
    else:
        r_age = 0.05
        age_status = "AGE_BUY_RANGE_WARNING"
        
    return {
        "R_age": r_age,
        "age_status": age_status
    }

def compute_density(duck_count: int, land_area_are: float, k_safe: float) -> dict:
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
        "density_status": density_status
    }

def compute_surviving_ducks(duck_count: int, r_age: float, p_over: float) -> float:
    lambda_eff = 0.67 * (1.0 - 0.50 * r_age) * (1.0 - 0.45 * p_over)
    return duck_count * lambda_eff

def compute_calendar_milestones(
    planting_date,
    hst_panen: int,
    hst_masuk_legacy: int,
    hst_heading_legacy: int,
):
    """Calendar milestones per Tabel 2.2/2.3 SoT.

    SoT example uses ``D_masuk_bebek = D_tanam + 21`` and
    ``D_tarik_bebek = D_tanam + 65``, giving ``t_active = 44``. The legacy
    ``hst_masuk`` field remains 20 for backward-compat but the canonical
    date arithmetic is fixed at 21 / 65.
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


def compute_yield_components(p_under: float, p_over: float, r_age: float, F_sys: float, f_var: float = 1.0) -> float:
    """Yield_are = 48.039 * F_density * F_age * F_sys * F_var.

    ``F_sys`` is the canonical SoT name. The legacy ``f_yield`` field on
    ``PlantingSystem`` is kept in sync with ``F_sys`` for backward-compat.
    """
    f_density = 1.0 - 0.12 * p_under - 0.25 * p_over
    f_age = 1.0 - 0.08 * r_age
    yield_are = 48.039 * f_density * f_age * F_sys * f_var
    return yield_are

