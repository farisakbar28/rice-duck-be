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

def compute_yield_components(p_under: float, p_over: float, r_age: float, f_sys: float, f_var: float = 1.0) -> float:
    f_density = 1.0 - 0.12 * p_under - 0.25 * p_over
    f_age = 1.0 - 0.08 * r_age
    yield_are = 48.039 * f_density * f_age * f_sys * f_var
    return yield_are

