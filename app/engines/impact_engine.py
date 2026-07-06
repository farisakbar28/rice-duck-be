import math
from app.domain.models import DSSConstants

def compute_feed_costs(duck_count: int, p_over: float, r_age: float) -> float:
    return duck_count * 5000.0 * (1.0 + 0.75 * p_over + 0.50 * r_age)

def compute_labor_costs(land_area_are: float, duck_count: int, p_over: float, r_age: float) -> float:
    return (47527.0 * land_area_are) + (duck_count * 1000.0 * (1.0 + p_over + r_age))

def compute_infrastructure(duck_count: int, land_area_are: float) -> float:
    return max(58333.0, (0.5 * 8333.0 * duck_count) + (0.5 * 49435.0 * math.sqrt(land_area_are)))

def compute_ecology_weed(c_labor: float, density_are: float, p_over: float) -> float:
    return (0.29 * c_labor) * (1.0 - math.exp(-0.35 * density_are)) * (1.0 - 0.25 * p_over)

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

