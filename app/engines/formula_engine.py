"""Model A mathematical engines (strict separation + evidence reset)."""

from datetime import date, timedelta
from decimal import Decimal, getcontext

getcontext().prec = 50

RELEASE_HST_MIN, RELEASE_HST_MAX = 21, 30
WITHDRAW_HST_MIN, WITHDRAW_HST_MAX = 56, 60
P_GABAH_FALLBACK = Decimal("6000")
P_DUCK_BUY_FALLBACK = Decimal("25000")
P_DUCK_SELL_FALLBACK = Decimal("45000")


def decimal(value: object) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def compute_age_status(age_days: int) -> dict:
    if age_days < 21:
        return {"age_status": "NOT_RECOMMENDED", "warnings": ["Umur bebek di bawah rentang kesiapan lokal 21–30 hari."]}
    if age_days <= 30:
        return {"age_status": "LOCAL_READY", "warnings": []}
    return {"age_status": "OLDER_CONSERVATIVE", "warnings": ["Umur bebek di atas rentang kesiapan lokal 21–30 hari."]}


def compute_density(duck_count: int, land_area_are: object, planting_system: str) -> dict:
    density_are = Decimal(duck_count) / decimal(land_area_are)
    density_ha = density_are * Decimal("100")
    ceiling = Decimal("4") if planting_system == "jajar_legowo" else Decimal("3")
    if density_are < 2: status = "UNDER"
    elif density_are <= ceiling: status = "RECOMMENDED"
    elif density_are <= 8: status = "WARNING_ABOVE_RECOMMENDED"
    else: status = "HIGH_RISK"
    return {"density_are": density_are, "density_ha": density_ha, "density_status": status}


def compute_calendar(planting_date: date | None) -> dict:
    result = {"release_hst_min": RELEASE_HST_MIN, "release_hst_max": RELEASE_HST_MAX, "withdraw_hst_min": WITHDRAW_HST_MIN, "withdraw_hst_max": WITHDRAW_HST_MAX, "release_date_min": None, "release_date_max": None, "withdraw_date_min": None, "withdraw_date_max": None}
    if planting_date is not None:
        result.update({"release_date_min": planting_date + timedelta(days=RELEASE_HST_MIN), "release_date_max": planting_date + timedelta(days=RELEASE_HST_MAX), "withdraw_date_min": planting_date + timedelta(days=WITHDRAW_HST_MIN), "withdraw_date_max": planting_date + timedelta(days=WITHDRAW_HST_MAX)})
    return result


def compute_xiong_yield(density_ha: Decimal, duration_days: object | None, land_area_are: object) -> dict:
    if duration_days is None:
        return {"yield_status": "OUTSIDE_LITERATURE_DOMAIN", "yield_are_kg": None, "yield_total_kg": None, "reason": "literature_duration_days was not supplied"}
    t = decimal(duration_days)
    if not (Decimal("0") < density_ha <= Decimal("600") and Decimal("50") <= t <= Decimal("80")):
        return {"yield_status": "OUTSIDE_LITERATURE_DOMAIN", "yield_are_kg": None, "yield_total_kg": None, "reason": "Xiong requires 0 < density_ha <= 600 and 50 <= literature_duration_days <= 80"}
    polynomial = Decimal("-0.0103") * density_ha * density_ha + Decimal("2.6314") * density_ha + Decimal("7569.4")
    exponent = -((t - Decimal("80")) ** 2) / (Decimal("2") * (Decimal("80") ** 2))
    yield_are = polynomial * exponent.exp() / Decimal("100")
    return {"yield_status": "VALID", "yield_are_kg": yield_are, "yield_total_kg": yield_are * decimal(land_area_are), "reason": None}


def compute_economics(*, duck_count: int, density_are: Decimal, yield_total_kg: Decimal | None, p_gabah: object, p_duck_buy: object, p_duck_sell: object, c_feed_scenario: object | None, c_jaring_purchase: object | None, n_jaring_cycles: object | None, c_kandang_purchase: object | None, n_kandang_cycles: object | None) -> dict:
    revenue_gabah = yield_total_kg * decimal(p_gabah) if yield_total_kg is not None else None
    duck_revenue = None if density_are > 8 else Decimal(duck_count) * decimal(p_duck_sell)
    cost_buy = Decimal(duck_count) * decimal(p_duck_buy)
    before = revenue_gabah + duck_revenue - cost_buy if revenue_gabah is not None and duck_revenue is not None else None
    infra, infra_selected = Decimal("0"), False
    if c_jaring_purchase is not None: infra, infra_selected = infra + decimal(c_jaring_purchase) / decimal(n_jaring_cycles), True
    if c_kandang_purchase is not None: infra, infra_selected = infra + decimal(c_kandang_purchase) / decimal(n_kandang_cycles), True
    feed = decimal(c_feed_scenario) if c_feed_scenario is not None else None
    after = before - (feed or Decimal("0")) - (infra if infra_selected else Decimal("0")) if before is not None and (feed is not None or infra_selected) else None
    return {"revenue_gabah": revenue_gabah, "revenue_duck_all_sold_scenario": duck_revenue, "cost_duck_buy": cost_buy, "cost_feed_scenario": feed, "cost_infra_cycle": infra if infra_selected else None, "cash_contribution_before_optional": before, "cash_contribution_after_optional": after}
