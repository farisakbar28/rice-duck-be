import math

from app.domain.models import DSSConstants


def compute_v_eco2(density_ha: float, area_ha: float) -> float:
    """V_eco2: estimasi penghematan pestisida/herbisida dari DOCX §5.7.

    Jika d_ha > 300:
        V_eco2 = (400 / (1 + exp(-0.036626 * d_ha)) - 3.327) * A_ha
    Jika d_ha <= 300:
        interpolasi linear dari 0 sampai nilai d_ha=300.
    """
    threshold_ha = 300.0
    value_at_threshold = (
        (400.0 / (1.0 + math.exp(-0.036626 * threshold_ha))) - 3.327
    ) * area_ha
    if density_ha > threshold_ha:
        return (
            (400.0 / (1.0 + math.exp(-0.036626 * density_ha))) - 3.327
        ) * area_ha
    if density_ha <= 0:
        return 0.0
    return value_at_threshold * (density_ha / threshold_ha)


def compute_infrastructure(constants: DSSConstants) -> dict:
    net_per_cycle = constants.net_cost_rp / constants.net_lifetime_seasons
    shelter_per_cycle = (
        constants.shelter_cost_rp / constants.shelter_lifetime_seasons
    )
    return {
        "status": "estimation",
        "net_cost_per_cycle_rp": net_per_cycle,
        "shelter_cost_per_cycle_rp": shelter_per_cycle,
        "maintenance_cost_rp": constants.infrastructure_maintenance_rp_per_season,
        "total_infrastructure_cost_rp": (
            net_per_cycle
            + shelter_per_cycle
            + constants.infrastructure_maintenance_rp_per_season
        ),
        "note": (
            "Maintenance uses 0 only as an unavailable-data placeholder; "
            "it is not evidence that maintenance is free."
        ),
    }


def compute_soil_nutrients(
    *,
    dung_total_per_duck_kg: float,
    density_ha: float,
    constants: DSSConstants,
) -> dict:
    if (
        constants.kappa_n is None
        or constants.kappa_p is None
        or constants.kappa_k is None
    ):
        return {
            "status": "unavailable",
            "n_kg_per_ha": None,
            "p2o5_kg_per_ha": None,
            "k2o_kg_per_ha": None,
            "missing_parameters": ["kappa_n", "kappa_p", "kappa_k"],
        }

    scale = (
        (dung_total_per_duck_kg / 10.0)
        * density_ha
        * constants.survival_lambda
    )
    return {
        "status": "estimation_only",
        "n_kg_per_ha": constants.kappa_n * scale,
        "p2o5_kg_per_ha": constants.kappa_p * scale,
        "k2o_kg_per_ha": constants.kappa_k * scale,
        "missing_parameters": [],
    }


def compute_feed_costs(
    *,
    duck_count: int,
    density_are: float,
    duration_days: int,
    effective_duration_days: float,
    area_ha: float,
    k_max_are: float,
    constants: DSSConstants,
) -> dict:
    required = {
        "feed_requirement_kg_per_duck_day": constants.feed_requirement_kg_per_duck_day,
        "feed_natural_saving_rate": constants.feed_natural_saving_rate,
        "feed_price_rp_per_kg": constants.feed_price_rp_per_kg,
    }
    missing = [name for name, value in required.items() if value is None]
    if missing:
        return {
            "status": "unavailable",
            "base_feed_cost_rp": None,
            "density_penalty_rp": None,
            "duration_penalty_rp": None,
            "penalty_feed_rp": None,
            "missing_parameters": missing,
        }

    base_feed_cost = (
        duck_count
        * constants.feed_requirement_kg_per_duck_day
        * effective_duration_days
        * constants.feed_price_rp_per_kg
        * (1.0 - constants.feed_natural_saving_rate)
    )
    penalty_missing = []
    if constants.feed_greedy_kg_per_duck_day is None:
        penalty_missing.append("feed_greedy_kg_per_duck_day")
        density_penalty = None
        duration_penalty = None
        penalty_feed = None
    else:
        density_ha = density_are * 100.0
        k_max_ha = k_max_are * 100.0
        density_penalty = (
            max(0.0, density_ha - k_max_ha)
            * constants.feed_greedy_kg_per_duck_day
            * duration_days
            * constants.feed_price_rp_per_kg
            * area_ha
        )
        duration_penalty = (
            density_ha
            * constants.feed_greedy_kg_per_duck_day
            * max(0, duration_days - constants.local_feed_warning_phase_days)
            * constants.feed_price_rp_per_kg
            * area_ha
        )
        penalty_feed = density_penalty + duration_penalty

    return {
        "status": "estimation_only" if not penalty_missing else "partial",
        "base_feed_cost_rp": base_feed_cost,
        "density_penalty_rp": density_penalty,
        "duration_penalty_rp": duration_penalty,
        "penalty_feed_rp": penalty_feed,
        "missing_parameters": penalty_missing,
    }


def compute_ecology(
    *,
    density_are: float,
    duration_days: int,
    area_are: float,
    k_max_are: float,
    constants: DSSConstants,
) -> dict:
    density_ha = density_are * 100.0
    area_ha = area_are / 100.0
    fertilizer_price_factor = (
        (0.107 * constants.nitrogen_price_rp_per_kg)
        + (0.424 * constants.phosphate_price_rp_per_kg)
        + (0.058 * constants.potassium_price_rp_per_kg)
    )
    v_eco1 = (
        ((0.02 * duration_days) - 0.6)
        * fertilizer_price_factor
        * density_ha
        * constants.survival_lambda
        * area_ha
    )
    v_eco2 = compute_v_eco2(density_ha, area_ha)
    weed_reduction_rate = (
        min(1.0, density_are / k_max_are) if k_max_are > 0 else 0.0
    )
    v_gulma = (
        constants.weeding_cost_rp_per_are
        * area_are
        * weed_reduction_rate
    )
    v_eco_total = v_eco1 + v_eco2 + v_gulma
    return {
        "status": "estimation_only",
        "fertilizer_saving_rp": v_eco1,
        "fertilizer_saving_status": "estimation_only",
        "pesticide_herbicide_saving_rp": v_eco2,
        "pesticide_herbicide_saving_status": "estimation_only",
        "weed_reduction_rate": weed_reduction_rate,
        "weeding_saving_rp": v_gulma,
        "weeding_saving_status": "estimation_only",
        "partial_ecological_value_rp": v_eco_total,
        "included_components": ["v_eco1", "v_eco2", "v_gulma"],
        "missing_parameters": [],
    }


def compute_economics(
    *,
    duck_count: int,
    surviving_ducks: float,
    density_are: float,
    duration_days: int,
    effective_duration_days: float,
    area_are: float,
    final_yield_kg_per_ha: float,
    base_yield_kg_per_ha: float,
    penalty_rate: float,
    k_max_are: float,
    partial_ecological_value_rp: float,
    constants: DSSConstants,
) -> dict:
    area_ha = area_are / 100.0
    infrastructure = compute_infrastructure(constants)
    feed = compute_feed_costs(
        duck_count=duck_count,
        density_are=density_are,
        duration_days=duration_days,
        effective_duration_days=effective_duration_days,
        area_ha=area_ha,
        k_max_are=k_max_are,
        constants=constants,
    )

    rice_revenue = None
    if constants.rice_duck_price_rp_per_kg is not None:
        rice_revenue = (
            final_yield_kg_per_ha
            * area_ha
            * constants.rice_duck_price_rp_per_kg
        )
    conventional_rice_revenue = None
    if constants.conventional_yield_kg_per_ha is not None:
        conventional_rice_revenue = (
            constants.conventional_yield_kg_per_ha
            * area_ha
            * constants.conventional_rice_price_rp_per_kg
        )
    delta_rice_value = (
        rice_revenue - conventional_rice_revenue
        if rice_revenue is not None and conventional_rice_revenue is not None
        else None
    )

    duck_revenue = surviving_ducks * constants.duck_sale_price_rp_per_duck
    duck_purchase_cost = duck_count * constants.duck_buy_price_rp_per_duck
    duck_net_value = None
    if (
        feed["base_feed_cost_rp"] is not None
        and feed["penalty_feed_rp"] is not None
    ):
        duck_net_value = (
            duck_revenue
            - duck_purchase_cost
            - feed["base_feed_cost_rp"]
            - feed["penalty_feed_rp"]
        )

    penalty_yield = None
    if constants.rice_duck_price_rp_per_kg is not None:
        penalty_yield = (
            base_yield_kg_per_ha
            * penalty_rate
            * area_ha
            * constants.rice_duck_price_rp_per_kg
        )

    net_profit = None
    if rice_revenue is not None and duck_net_value is not None:
        net_profit = (
            rice_revenue
            + duck_net_value
            + partial_ecological_value_rp
            - infrastructure["total_infrastructure_cost_rp"]
            - constants.additional_cost_rp_per_season
        )

    missing = []
    if constants.rice_duck_price_rp_per_kg is None:
        missing.append("rice_duck_price_rp_per_kg")
    if constants.conventional_yield_kg_per_ha is None:
        missing.append("conventional_yield_kg_per_ha")
    missing.extend(feed["missing_parameters"])
    return {
        "status": "partial",
        "perspective": "gabah",
        "rice_revenue_rp": rice_revenue,
        "conventional_rice_revenue_rp": conventional_rice_revenue,
        "delta_rice_value_rp": delta_rice_value,
        "duck_revenue_rp": duck_revenue,
        "duck_purchase_cost_rp": duck_purchase_cost,
        "feed_cost_rp": feed["base_feed_cost_rp"],
        "feed_cost_status": feed["status"],
        "penalty_feed_rp": feed["penalty_feed_rp"],
        "duck_net_value_rp": duck_net_value,
        "infrastructure": infrastructure,
        "penalty_yield_rp": penalty_yield,
        "additional_cost_rp": constants.additional_cost_rp_per_season,
        "net_profit_rp": net_profit,
        "net_profit_rp_per_are": (
            net_profit / area_are if net_profit is not None else None
        ),
        "missing_parameters": sorted(set(missing)),
    }


def compute_environment(
    *,
    final_yield_kg_per_ha: float,
    constants: DSSConstants,
) -> dict:
    ch4_rd = constants.seasonal_ch4_rice_duck_kg_per_ha
    ch4_conventional = constants.seasonal_ch4_conventional_kg_per_ha
    n2o = constants.seasonal_n2o_kg_per_ha
    if ch4_rd is None or n2o is None:
        return {
            "status": "disabled",
            "co2e_kg_per_ha_season": None,
            "ghgi_kg_co2e_per_kg_yield": None,
            "ch4_reduction_percent": None,
            "missing_parameters": ["f_ch4_kg_per_ha_season", "f_n2o_kg_per_ha_season"],
        }

    co2e = (ch4_rd * constants.gwp_ch4) + (n2o * constants.gwp_n2o)
    ghgi = co2e / final_yield_kg_per_ha if final_yield_kg_per_ha > 0 else None
    ch4_reduction = None
    if ch4_conventional is not None and ch4_conventional > 0:
        ch4_reduction = (
            (ch4_conventional - ch4_rd) / ch4_conventional
        ) * 100.0
    return {
        "status": "estimation_only",
        "co2e_kg_per_ha_season": co2e,
        "ghgi_kg_co2e_per_kg_yield": ghgi,
        "ch4_reduction_percent": ch4_reduction,
        "missing_parameters": (
            [] if ch4_conventional is not None else ["f_ch4_conventional_kg_per_ha_season"]
        ),
    }
