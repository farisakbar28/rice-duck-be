import math

from app.domain.models import DSSConstants


def compute_v_eco2(density_ha: float, area_ha: float) -> float:
    """V_eco2: estimasi penghematan pestisida. Rev Final.
    
    Formula: max(0, (400 / (1 + exp(-0.036626 * d_lit_ha)) - 3.327) * (A_are / 100))
    """
    if density_ha <= 0:
        return 0.0

    v_eco2_raw = (
        (400.0 / (1.0 + math.exp(-0.036626 * density_ha))) - 3.327
    ) * area_ha
    return max(0.0, v_eco2_raw)


def compute_infrastructure(constants: DSSConstants) -> dict:
    net_per_cycle = constants.net_cost_rp / constants.net_lifetime_seasons
    shelter_per_cycle = (
        constants.shelter_cost_rp / constants.shelter_lifetime_seasons
    )
    return {
        "status": "estimation",
        "net_cost_per_cycle_rp": net_per_cycle,
        "shelter_cost_per_cycle_rp": shelter_per_cycle,
        "maintenance_cost_rp": 0.0,
        "total_infrastructure_cost_rp": (
            net_per_cycle
            + shelter_per_cycle
        ),
        "note": "Maintenance cost dianulir/tidak dicatat.",
    }


def compute_soil_nutrients(
    *,
    dung_total_per_duck_kg: float,
    density_are: float,
    constants: DSSConstants,
) -> dict:
    """Hitung N/P/K tanah dari kotoran bebek. Rev 2 §5.4.

    Rev 2: rumus berbasis d_aktual_are (bukan density_ha).
    N_tanah_are = kappa_N * (Dung_total / 10) * d_aktual_are * lambda
    P_tanah_are = kappa_P * (Dung_total / 10) * d_aktual_are * lambda
    K_tanah_are = kappa_K * (Dung_total / 10) * d_aktual_are * lambda

    Output utama kg/are. Catatan kg/ha = n_tanah_are * 100 (disimpan sebagai note).
    Status: literature-uncalibrated (kappa belum diuji lokal).
    """
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
            "n_kg_per_are": None,
            "p2o5_kg_per_are": None,
            "k2o_kg_per_are": None,
            "missing_parameters": ["kappa_n", "kappa_p", "kappa_k"],
        }

    # Rev 2: basis are — d_aktual_are * lambda (bukan d_ha * lambda)
    scale_are = (
        (dung_total_per_duck_kg / 10.0)
        * density_are
        * constants.survival_lambda
    )
    n_are = constants.kappa_n * scale_are
    p_are = constants.kappa_p * scale_are
    k_are = constants.kappa_k * scale_are

    return {
        "status": "estimation_only",
        # Rev 2 primary output: kg/are
        "n_kg_per_are": n_are,
        "p2o5_kg_per_are": p_are,
        "k2o_kg_per_are": k_are,
        # Backward compat note: kg/ha = kg/are * 100
        "n_kg_per_ha": n_are * 100.0,   # N_tanah_ha_note
        "p2o5_kg_per_ha": p_are * 100.0,  # P_tanah_ha_note
        "k2o_kg_per_ha": k_are * 100.0,   # K_tanah_ha_note
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
    # R-1 / R-9 (Rev1_Doc §5.6): fallback ke referensi Lit_DB jika q_feed lokal None
    # Nilai referensi: A02 'Average feed consumed per duck per day' = 0.10 kg/ekor/hari,
    # saving_rate=0.66
    feed_req = constants.feed_requirement_kg_per_duck_day

    feed_save = constants.feed_natural_saving_rate
    feed_price = constants.feed_price_rp_per_kg

    using_reference_fallback = False
    q_feed_source = None
    q_feed_status = None
    q_feed_assumption_note = None

    if feed_req is None:
        feed_req = constants.feed_requirement_kg_per_duck_day_reference
        using_reference_fallback = True
        q_feed_source = "literature-reference-a02"
        q_feed_status = "literature-uncalibrated"
        q_feed_assumption_note = (
            "q_feed lokal tidak tersedia (Excel lokal: 'Jumlah pakan tambahan = Belum ada'). "
            "Fallback Opsi A: 0.10 kg/ekor/hari dari workbook referensi sheet Data row 975, "
            "article A02: 'Average feed consumed per duck per day = 0.1 kg/day' (MATCH_EXACT). "
            "Cluster referensi lain: A13 130g/day=0.13, A13 80-110g/day, A16 80g/day=0.08, "
            "B5A02 ~0.096-0.099 kg/day. "
            "Nilai 0.12-0.225 kg/ekor/hari TIDAK ditemukan sebagai angka eksplisit di workbook referensi. "
            "Nilai ini bukan data lokal dan bukan exact reference row untuk 0.15."
        )
    else:
        q_feed_source = "local"
        q_feed_status = "local-estimate"
        q_feed_assumption_note = None

    if feed_save is None:
        feed_save = constants.feed_natural_saving_rate_reference
        using_reference_fallback = True

    return {
        "status": "hard_override_zero",
        "feed_cost_source": "system-design",
        "base_feed_cost_rp": 0.0,
        "density_penalty_rp": 0.0,
        "duration_penalty_rp": 0.0,
        "penalty_feed_rp": 0.0,
        "missing_parameters": [],
        "q_feed_source": "literature-reference-a02",
        "q_feed_status": "literature-uncalibrated",
        "q_feed_assumption_note": "q_feed=0.10 kg/ekor/hari hanya output edukasi fisik; C_feed=0 hard override sesuai model final.",
    }


def compute_ecology(
    *,
    density_are: float,
    duration_days: int,
    area_are: float,
    k_max_are: float,
    constants: DSSConstants,
) -> dict:
    """Hitung manfaat ekologis-finansial. Rev 2 §5.7.

    V_eco1 Rev 2: (0.02*t - 0.6) * (0.107*P_N + 0.424*P_P + 0.058*P_K) * d_aktual_are * lambda * A_are
    V_eco2 Rev 2: sigmoid formula pakai d_lit_ha dan A_ha_note (catatan literatur)
    V_gulma Rev 2: C_gulma * A_are * r_gulma; r_gulma = min(1, d_aktual_are / K_max_are)
    """
    density_ha = density_are * 100.0   # d_lit_ha — catatan konversi rumus literatur
    area_ha = area_are / 100.0         # A_ha_note — catatan konversi rumus literatur
    fertilizer_price_factor = (
        (0.107 * constants.nitrogen_price_rp_per_kg)
        + (0.424 * constants.phosphate_price_rp_per_kg)
        + (0.058 * constants.potassium_price_rp_per_kg)
    )
    # Rev 2 §5.7 V_eco1: d_aktual_are * lambda * A_are (bukan d_ha * lambda * A_ha)
    # Numerik ekuivalen karena d_are * A_are = (d_ha/100) * (A_ha*100) = d_ha * A_ha
    # Tapi semantik Rev 2 menggunakan d_aktual_are * A_are sebagai satuan utama are.
    # Guard: V_eco1_raw negatif jika t < 30 (0.02*t - 0.6 < 0)
    v_eco1_raw = (
        ((0.02 * duration_days) - 0.6)
        * fertilizer_price_factor
        * density_are             # d_aktual_are (Rev 2 utama)
        * constants.survival_lambda
        * area_are                # A_are (Rev 2 utama)
    )
    v_eco1 = max(0.0, v_eco1_raw)
    # V_eco2: d_lit_ha dan A_ha_note sebagai catatan literatur (Rev 2 §5.7)
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
        "fertilizer_saving_raw_rp": v_eco1_raw,  # exposed for trace/audit
        "fertilizer_saving_status": "literature-uncalibrated",
        "pesticide_herbicide_saving_rp": v_eco2,
        "pesticide_herbicide_saving_status": "literature-uncalibrated",
        "weed_reduction_rate": weed_reduction_rate,
        "weeding_saving_rp": v_gulma,
        "weeding_saving_status": "local-estimate",
        "partial_ecological_value_rp": v_eco_total,
        "included_components": ["v_eco1", "v_eco2", "v_gulma"],
        "missing_parameters": [],
    }


def _compute_v_duck_xiong(
    *,
    density_ha: float,
    survival_lambda: float,
    duration_days: int,
    area_ha: float,
) -> float:
    """V_duck_Xiong dari Rev1_Doc (rumus Xiong akademik).

    PENTING: JANGAN kurangi C_feed dari hasil ini —
    rumus Xiong sudah memperhitungkan biaya pakan secara implisit (R-07 Rev1_Doc).
    Nilai ini hanya untuk pembanding akademik, bukan kalkulasi Laba_bersih operasional.
    """
    return (
        -0.0096 * (density_ha ** 2)
        + (11.3861 + 14.4 * survival_lambda) * density_ha
        - 0.18 * survival_lambda * duration_days * density_ha
        + 17.0857
    ) * area_ha


def compute_economics(
    *,
    duck_count: int,
    surviving_ducks: float,
    density_are: float,
    duration_days: int,
    effective_duration_days: float,
    area_are: float,
    final_yield_kg_per_ha: float,
    x_final_kg_are: float | None = None,
    base_yield_kg_per_ha: float,
    x0_kg_are: float | None = None,
    penalty_rate: float,
    k_max_are: float,
    partial_ecological_value_rp: float,
    duck_buy_price_rp_per_duck: float | None = None,
    duck_buy_price_source: str = "default-constant",
    duck_buy_price_status: str = "local-estimate",
    duck_buy_price_requires_actual: bool = False,
    constants: DSSConstants,
) -> dict:
    """Hitung ekonomi padi dan bebek. Rev 2 §5.6.

    Rev 2: R_gabah_RD = x_final_kg_are * A_are * p_gabah_RD
    Bukan: x_final_kg_ha * A_ha * p_gabah_RD
    x_final_kg_are adalah output utama; x_final_kg_ha_note hanya catatan.
    """
    area_ha = area_are / 100.0          # A_ha_note — catatan konversi
    density_ha = density_are * 100.0    # d_lit_ha — catatan konversi

    # Rev 2: x_final_kg_are = x_final_kg_ha_note / 100 (primary)
    if x_final_kg_are is None:
        x_final_kg_are = final_yield_kg_per_ha / 100.0

    # Rev 2: x0_kg_are = conventional baseline dalam kg/are
    if x0_kg_are is None and constants.conventional_yield_kg_per_ha is not None:
        x0_kg_are = constants.conventional_yield_kg_per_ha / 100.0

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

    # Rev 2 §5.6: R_gabah_RD = x_final_kg_are * A_are * p_gabah_RD
    rice_revenue = None
    if (
        constants.rice_duck_price_rp_per_kg is not None
        and x_final_kg_are is not None
    ):
        rice_revenue = (
            x_final_kg_are
            * area_are
            * constants.rice_duck_price_rp_per_kg
        )

    # Rev 2 §5.6: R_gabah_K = x0_kg_are * A_are * p_gabah_konv
    conventional_rice_revenue = None
    if (
        x0_kg_are is not None
        and constants.conventional_rice_price_rp_per_kg is not None
    ):
        conventional_rice_revenue = (
            x0_kg_are
            * area_are
            * constants.conventional_rice_price_rp_per_kg
        )
    delta_rice_value = (
        rice_revenue - conventional_rice_revenue
        if rice_revenue is not None and conventional_rice_revenue is not None
        else None
    )

    duck_revenue = surviving_ducks * constants.duck_sale_price_rp_per_duck
    resolved_duck_buy_price = duck_buy_price_rp_per_duck
    duck_purchase_cost = (
        duck_count * resolved_duck_buy_price
        if resolved_duck_buy_price is not None
        else None
    )

    # V_duck_lokal = N_d * p_duck - C_duck_buy (C_feed = 0)
    duck_net_value = None
    if duck_purchase_cost is not None:
        duck_net_value = (
            duck_revenue
            - duck_purchase_cost
        )

    # penalty_yield: nilai kehilangan akibat penalti
    penalty_yield = None
    if constants.rice_duck_price_rp_per_kg is not None:
        # penalty yield dalam are basis
        penalty_yield = (
            (base_yield_kg_per_ha / 100.0)  # x_base_kg_are
            * penalty_rate
            * area_are
            * constants.rice_duck_price_rp_per_kg
        )

    # Laba_bersih = R_gabah_RD + V_duck_lokal + V_eco - C_infra - biaya_tambahan
    net_profit = None
    if rice_revenue is not None and duck_net_value is not None:
        net_profit = (
            rice_revenue
            + duck_net_value
            + partial_ecological_value_rp
            - infrastructure["total_infrastructure_cost_rp"]
            - constants.additional_cost_rp_per_season
        )
    elif duck_net_value is not None:
        # Feed tersedia tapi rice_revenue null — tetap hitung partial profit
        net_profit = (
            duck_net_value
            + partial_ecological_value_rp
            - infrastructure["total_infrastructure_cost_rp"]
            - constants.additional_cost_rp_per_season
        )

    # V_duck_Xiong (Rev 2 §5.6): [-0.0096*d_lit_ha^2 + (11.3861+14.4*lambda)*d_lit_ha
    #   - 0.18*lambda*t*d_lit_ha + 17.0857] * A_ha_note
    # Jangan kurangi C_feed — rumus Xiong adalah net-revenue akademik.
    v_duck_xiong = _compute_v_duck_xiong(
        density_ha=density_ha,
        survival_lambda=constants.survival_lambda,
        duration_days=duration_days,
        area_ha=area_ha,
    )

    # Penentuan sumber_data
    feed_source = feed.get("feed_cost_source", "unavailable")
    duck_price_local = True  # duck_sale_price dan duck_buy_price sudah local-calibrated
    rice_price_local = constants.rice_duck_price_rp_per_kg is not None

    if feed_source == "unavailable":
        sumber_data = "literature-uncalibrated"
        data_readiness = "missing"
    elif feed_source == "literature-uncalibrated":
        sumber_data = "mixed" if duck_price_local else "literature-uncalibrated"
        data_readiness = "partial"
    else:
        sumber_data = "local-calibrated" if duck_price_local and rice_price_local else "mixed"
        data_readiness = "complete" if (duck_price_local and rice_price_local) else "partial"

    missing = []
    if constants.rice_duck_price_rp_per_kg is None:
        missing.append("rice_duck_price_rp_per_kg")
    if constants.conventional_yield_kg_per_ha is None:
        missing.append("conventional_yield_kg_per_ha")
    if duck_purchase_cost is None:
        missing.append("duck_buy_price_rp_per_duck")
    missing.extend(feed["missing_parameters"])

    formula_available = True
    numeric_ready = net_profit is not None

    if duck_price_local and rice_price_local and feed_source == "local-calibrated":
        status_data = "local-calibrated"
    elif missing:
        status_data = "partial"
    else:
        status_data = "mixed"

    return {
        "status": "partial",
        "status_data": status_data,
        "perspective": "gabah",
        "rice_revenue_rp": rice_revenue,
        "conventional_rice_revenue_rp": conventional_rice_revenue,
        "delta_rice_value_rp": delta_rice_value,
        "duck_revenue_rp": duck_revenue,
        "duck_purchase_cost_rp": duck_purchase_cost,
        "duck_purchase_price_rp_per_duck": resolved_duck_buy_price,
        "duck_purchase_price_source": duck_buy_price_source,
        "duck_purchase_price_status": duck_buy_price_status,
        "duck_purchase_price_requires_actual": duck_buy_price_requires_actual,
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
        "sumber_data": sumber_data,
        "data_readiness": data_readiness,
        "formula_available": formula_available,
        "numeric_ready": numeric_ready,
        "q_feed_source": feed.get("q_feed_source"),
        "q_feed_status": feed.get("q_feed_status"),
        "q_feed_assumption_note": feed.get("q_feed_assumption_note"),
        "v_duck_xiong_reference": v_duck_xiong,
        "v_duck_xiong_model_value": v_duck_xiong,
        "v_duck_xiong_status": "literature-uncalibrated",
    }


def compute_environment(
    *,
    final_yield_kg_per_ha: float,
    x_final_kg_are: float | None = None,
    constants: DSSConstants,
) -> dict:
    """Catatan: environment/emission jadi limitation, bukan output numerik aktif."""
    return {
        "status": "limitation",
        "sumber_data": "limitation",
        "status_data": "limitation",
        "data_readiness": "limitation",
        "formula_available": False,
        "numeric_ready": False,
        "calibration_note": (
            "Catatan: CO2e, GHGI, Reduksi_CH4, dan DO-to-CH4 tidak dihitung sebagai output numerik aktif. "
            "Data F_CH4, F_N2O, baseline emisi konvensional, dan DO tidak tersedia dari mitra."
        ),
        "catatan_kalibrasi": (
            "Environment/emission tetap limitation penelitian dan tidak masuk objective function."
        ),
        "f_ch4_are": None,
        "f_n2o_are": None,
        "co2e_are": None,
        "ghgi": None,
        "ch4_reduction_pct": None,
        "y_ch4_do_model": None,
        "co2e_kg_per_ha_season": None,
        "co2e_ha_note": None,
        "f_ch4_ha_note": None,
        "f_n2o_ha_note": None,
        "ghgi_kg_co2e_per_kg_yield": None,
        "ch4_reduction_percent": None,
        "missing_parameters": [
            "f_ch4_kg_per_ha_season",
            "f_n2o_kg_per_ha_season",
            "f_ch4_conventional_kg_per_ha_season",
            "x_do",
        ],
    }
