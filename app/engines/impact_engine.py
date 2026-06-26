import math

from app.domain.models import DSSConstants


def compute_v_eco2(density_ha: float, area_ha: float) -> float:
    """V_eco2: estimasi penghematan pestisida/herbisida. Rev 2 §5.7.

    Rev 2: threshold d_aktual_are > 3 (ekuivalen d_lit_ha > 300).
    Fungsi menerima d_lit_ha dan A_ha_note (catatan konversi rumus literatur).

    Jika d_aktual_are > 3 (d_lit_ha > 300):
        V_eco2 = (400 / (1 + exp(-0.036626 * d_lit_ha)) - 3.327) * A_ha_note
    Jika d_aktual_are <= 3 (d_lit_ha <= 300):
        interpolasi linear dari 0 sampai nilai d_aktual_are=3 (d_lit_ha=300).

    Pastikan operator adalah pembagian (400/(...)), bukan pangkat (400^(...)).
    """
    # threshold: d_aktual_are > 3 = d_lit_ha > 300 (Rev 2 R-09)
    threshold_ha = 300.0  # = d_are threshold 3.0 * 100
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

    missing = []
    if feed_price is None:
        missing.append("feed_price_rp_per_kg")

    if missing:
        return {
            "status": "unavailable",
            "feed_cost_source": "unavailable",
            "base_feed_cost_rp": None,
            "density_penalty_rp": None,
            "duration_penalty_rp": None,
            "penalty_feed_rp": None,
            "missing_parameters": missing,
            "q_feed_source": q_feed_source,
            "q_feed_status": q_feed_status,
            "q_feed_assumption_note": q_feed_assumption_note,
        }

    # Sekarang feed_req dan feed_save pasti ada (lokal atau referensi)
    base_feed_cost = (
        duck_count
        * feed_req
        * effective_duration_days
        * feed_price  # type: ignore[operator]
        * (1.0 - feed_save)
    )

    # Status feed berdasarkan sumber data
    if using_reference_fallback:
        feed_status = "literature-uncalibrated"
    elif constants.feed_requirement_kg_per_duck_day is not None:
        feed_status = "local-calibrated"
    else:
        feed_status = "literature-uncalibrated"

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
            * feed_price  # type: ignore[operator]
            * area_ha
        )
        duration_penalty = (
            density_ha
            * constants.feed_greedy_kg_per_duck_day
            * max(0, duration_days - constants.local_feed_warning_phase_days)
            * feed_price  # type: ignore[operator]
            * area_ha
        )
        penalty_feed = density_penalty + duration_penalty

    return {
        "status": feed_status if not penalty_missing else feed_status,
        "feed_cost_source": "literature-uncalibrated" if using_reference_fallback else "local",
        "base_feed_cost_rp": base_feed_cost,
        "density_penalty_rp": density_penalty,
        "duration_penalty_rp": duration_penalty,
        "penalty_feed_rp": penalty_feed if penalty_feed is not None else 0.0,
        "missing_parameters": penalty_missing,
        "q_feed_source": q_feed_source,
        "q_feed_status": q_feed_status,
        "q_feed_assumption_note": q_feed_assumption_note,
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
    final_yield_kg_per_ha: float,   # x_final_kg_ha_note — catatan literatur, bukan primary
    x_final_kg_are: float | None = None,  # Rev 2 primary: x_final_kg_are = final_yield_kg_per_ha / 100
    base_yield_kg_per_ha: float,    # x_base_kg_ha_note — catatan literatur
    x0_kg_are: float | None = None,  # Rev 2: conventional yield dalam kg/are
    penalty_rate: float,
    k_max_are: float,
    partial_ecological_value_rp: float,
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
    if constants.rice_duck_price_rp_per_kg is not None:
        rice_revenue = (
            x_final_kg_are
            * area_are
            * constants.rice_duck_price_rp_per_kg
        )

    # Rev 2 §5.6: R_gabah_K = x0_kg_are * A_are * p_gabah_konv
    conventional_rice_revenue = None
    if x0_kg_are is not None:
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
    duck_purchase_cost = duck_count * constants.duck_buy_price_rp_per_duck

    # V_duck_lokal = N_d * p_duck - C_duck_buy - C_feed
    duck_net_value = None
    if feed["base_feed_cost_rp"] is not None:
        duck_net_value = (
            duck_revenue
            - duck_purchase_cost
            - feed["base_feed_cost_rp"]
            - (feed["penalty_feed_rp"] or 0.0)
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
    """Hitung emisi dan lingkungan. Rev 2 §5.8.

    Rev 2: satuan utama adalah kg/are/musim.
    CO2e_are = F_CH4_are * GWP_CH4 + F_N2O_are * GWP_N2O
    F_CH4_are = F_CH4_ha / 100 (jika sumber masih kg/ha/musim)
    GHGI = CO2e_are / x_final_kg_are
    Reduksi_CH4 = (F_CH4_konv_are - F_CH4_RD_are) / F_CH4_konv_are * 100%
    Y_CH4 = -1.5276 * X_DO + 14.770  (X_DO belum tersedia)

    Field ha boleh ada sebagai note: co2e_ha_note = co2e_are * 100
    Environment TIDAK PERNAH disabled — status = literature-uncalibrated.
    """
    ch4_rd_ha = constants.seasonal_ch4_rice_duck_kg_per_ha
    ch4_conventional_ha = constants.seasonal_ch4_conventional_kg_per_ha
    n2o_ha = constants.seasonal_n2o_kg_per_ha

    # Rev 2: x_final_kg_are primary; fallback dari ha note
    if x_final_kg_are is None:
        x_final_kg_are = final_yield_kg_per_ha / 100.0

    if ch4_rd_ha is None or n2o_ha is None:
        return {
            "status": "literature-uncalibrated",
            "sumber_data": "literature-uncalibrated",
            "status_data": "partial",
            "data_readiness": "missing",
            "formula_available": True,
            "numeric_ready": False,
            "calibration_note": (
                "Modul emisi belum terkalibrasi lokal oleh Astungkara Way. "
                "F_CH4, F_N2O, dan DO musiman belum tersedia. "
                "Output null bukan berarti emisi nol — data belum cukup untuk klaim."
            ),
            "catatan_kalibrasi": (
                "Modul emisi belum terkalibrasi lokal oleh Astungkara Way. "
                "F_CH4, F_N2O, dan DO musiman belum tersedia. "
                "Output null bukan berarti emisi nol — data belum cukup untuk klaim."
            ),
            # Rev 2 primary fields (are):
            "f_ch4_are": None,
            "f_n2o_are": None,
            "co2e_are": None,
            "ghgi": None,
            "ch4_reduction_pct": None,
            "y_ch4_do_model": None,
            # Backward compat (ha note):
            "co2e_kg_per_ha_season": None,
            "co2e_ha_note": None,
            "f_ch4_ha_note": None,
            "f_n2o_ha_note": None,
            "ghgi_kg_co2e_per_kg_yield": None,
            "ch4_reduction_percent": None,
            "missing_parameters": ["f_ch4_kg_per_ha_season", "f_n2o_kg_per_ha_season"],
        }

    # Rev 2: konversi dari kg/ha/musim ke kg/are/musim dengan /100
    f_ch4_are = ch4_rd_ha / 100.0
    f_n2o_are = n2o_ha / 100.0
    f_ch4_konv_are = ch4_conventional_ha / 100.0 if ch4_conventional_ha is not None else None

    # Rev 2 CO2e_are = F_CH4_are * GWP_CH4 + F_N2O_are * GWP_N2O
    co2e_are = (f_ch4_are * constants.gwp_ch4) + (f_n2o_are * constants.gwp_n2o)
    co2e_ha_note = co2e_are * 100.0  # catatan ha

    # Rev 2 GHGI = CO2e_are / x_final_kg_are
    ghgi = co2e_are / x_final_kg_are if x_final_kg_are > 0 else None

    # Rev 2 Reduksi_CH4 = (F_CH4_konv_are - F_CH4_RD_are) / F_CH4_konv_are * 100%
    ch4_reduction = None
    if f_ch4_konv_are is not None and f_ch4_konv_are > 0:
        ch4_reduction = (
            (f_ch4_konv_are - f_ch4_are) / f_ch4_konv_are
        ) * 100.0

    missing = [] if ch4_conventional_ha is not None else ["f_ch4_conventional_kg_per_ha_season"]

    return {
        "status": "literature-uncalibrated",
        "sumber_data": "literature-uncalibrated",
        "status_data": "literature-uncalibrated",
        "data_readiness": "partial" if ch4_conventional_ha is None else "complete",
        "formula_available": True,
        "numeric_ready": True,
        "calibration_note": (
            "CO2e dan GHGI dihitung dari data flux yang tersedia, tetapi "
            "belum terkalibrasi lokal oleh Astungkara Way. "
            "Satuan utama Rev 2: kg CO2e/are/musim."
        ),
        "catatan_kalibrasi": (
            "CO2e dan GHGI dihitung dari data flux yang tersedia, tetapi "
            "belum terkalibrasi lokal oleh Astungkara Way. "
            "Satuan utama Rev 2: kg CO2e/are/musim."
        ),
        # Rev 2 primary fields (are):
        "f_ch4_are": f_ch4_are,
        "f_n2o_are": f_n2o_are,
        "co2e_are": co2e_are,
        "ghgi": ghgi,
        "ch4_reduction_pct": ch4_reduction,
        "y_ch4_do_model": None,  # Y_CH4 = -1.5276*X_DO + 14.770 — X_DO belum tersedia lokal
        # Backward compat note (ha):
        "co2e_kg_per_ha_season": co2e_ha_note,   # co2e_ha_note alias
        "co2e_ha_note": co2e_ha_note,
        "f_ch4_ha_note": ch4_rd_ha,
        "f_n2o_ha_note": n2o_ha,
        "ghgi_kg_co2e_per_kg_yield": ghgi,       # alias backward compat
        "ch4_reduction_percent": ch4_reduction,   # alias backward compat
        "missing_parameters": missing,
    }
