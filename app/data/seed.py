"""Seed data — aligned with SoT FINAL.

SoT §3: rice_variety values: 'sertani', 'inpari'
SoT §6.1: Sertani HST_panen_min=100, HST_panen_max=110
          Inpari  HST_panen=134 (generic estimate)
SoT §5.1: jajar_legowo recommended ceiling=4 ekor/are (Jajar Legowo 2:1 only)
          tegel recommended ceiling=3 ekor/are
SoT §9: p_duck_sell=52500
"""

from app.domain.models import (
    DSSConstants,
    ParameterMetadata,
    PlantingSystem,
    RiceVariety,
)


RICE_VARIETIES = [
    RiceVariety(
        code="sertani",
        label="Sertani / Seratih",
        hst_panen_min=100,
        hst_panen_max=110,
        hst_panen=100,           # legacy alias: use hst_panen_min for compatibility
        hst_masuk=21,
        hst_heading=65,
        harvest_age_days=100,    # legacy alias
        risk_note=(
            "Bebek sebaiknya ditarik sebelum fase keluar malai (HST 65). "
            "Panen Sertani: estimasi 100–110 HST dari tanggal tanam."
        ),
        hst_masuk_min=21,
        hst_masuk_max=21,
        hst_heading_min=65,
        hst_heading_max=65,
        status="local-estimate",
    ),
    RiceVariety(
        code="inpari",
        label="Inpari (Generic)",
        hst_panen_min=134,
        hst_panen_max=134,
        hst_panen=134,
        hst_masuk=21,
        hst_heading=65,
        harvest_age_days=134,
        risk_note=(
            "HST panen Inpari masih generic estimate (134 HST). "
            "Membutuhkan kalibrasi varietas/subvarietas lebih lanjut."
        ),
        hst_masuk_min=21,
        hst_masuk_max=21,
        hst_heading_min=65,
        hst_heading_max=65,
        status="generic-estimate",
    ),
]

PLANTING_SYSTEMS = [
    PlantingSystem(
        code="jajar_legowo",
        label="Jajar Legowo 2:1",
        recommended_density_max_are=4.0,
        note=(
            "Jajar Legowo 2:1 saja. Recommended density: 2–4 ekor/are. "
            "Yield production bersifat system-neutral per SoT §8."
        ),
        k_safe_are=4.0,
        k_max_are=4.0,
        f_yield=1.0,
        recommended_density_min_are=2.0,
        k_safe_min_are=4.0,
        k_safe_max_are=8.0,
        k_max_min_are=4.0,
        k_max_max_are=8.0,
        limited_test_max_are=None,
        k_max_status="local-estimate",
        f_yield_status="system-neutral-SoT",
    ),
    PlantingSystem(
        code="tegel",
        label="Tegel / Konvensional",
        recommended_density_max_are=3.0,
        note=(
            "Tegel/Konvensional. Recommended density: 2–3 ekor/are. "
            "Yield production bersifat system-neutral per SoT §8."
        ),
        k_safe_are=3.0,
        k_max_are=3.0,
        f_yield=1.0,
        recommended_density_min_are=2.0,
        k_safe_min_are=2.0,
        k_safe_max_are=3.0,
        k_max_min_are=2.0,
        k_max_max_are=3.0,
        limited_test_max_are=None,
        k_max_status="local-estimate",
        f_yield_status="system-neutral-SoT",
    ),
]

DSS_CONSTANTS = DSSConstants(
    # SoT §9: production backend constants
    duck_sale_price_rp_per_duck=52500.0,
    # HET pupuk (locked)
    HET_urea=1800.0,
    HET_phonska=1840.0,
    HET_kcl=9500.0,
    # §10.1: Weeding
    weeding_cost_rp_per_are=21000.0,
    # Misc reference
    survival_lambda=0.67,
    t_max_eff_days=45,
    t_phase_1_days=50,
    local_feed_warning_phase_days=30,
    dung_phase_1_total_kg=4.0,
    dung_phase_2_daily_kg=0.2,
    minimum_density_are=1.0,
    p_max=0.8,
    penalty_gamma=0.5,
    daily_duck_grazing_hours=10.0,
    baseline_grazing_hours=10.0,
    feed_requirement_kg_per_duck_day=0.10,
    feed_natural_saving_rate=1.0,
    feed_greedy_kg_per_duck_day=0.15,
    rice_duck_price_rp_per_kg=6000.0,
    duck_buy_price_rp_per_duck=0.0,
    duck_target_out_max_days=65,
    feed_price_rp_per_kg=None,
    nitrogen_price_rp_per_kg=1800.0,
    potassium_price_rp_per_kg=9500.0,
    gwp_ch4=34.0,
    gwp_n2o=265.0,
    seasonal_ch4_rice_duck_kg_per_ha=None,
    seasonal_ch4_conventional_kg_per_ha=None,
    seasonal_n2o_kg_per_ha=None,
    calibration_note=(
        "Parameter production: p_duck_sell=52500, c_feed=20000, p_gabah=6000 (SoT §9). "
        "Weeding sandbox: k_weeding=21000, R_weeding=0.77 (SoT §10.1). "
        "Yield production system-neutral untuk seluruh sistem tanam (SoT §8)."
    ),
)

PARAMETER_METADATA: dict[str, ParameterMetadata] = {
    "yield_baseline": ParameterMetadata(
        value=47.8767507,
        unit="kg/are",
        source="data_collection",
        status="local-validated",
        note="Y_base = 47.8767507 kg/are. Baseline empiris lokal dan system-neutral. SoT §8.",
    ),
    "p_duck_sell": ParameterMetadata(
        value=52500,
        unit="Rp/ekor",
        source="data_collection",
        status="local-estimate",
        note="Harga jual bebek production = Rp52.500/ekor. SoT §9.",
    ),
    "c_feed": ParameterMetadata(
        value=20000,
        unit="Rp/ekor/siklus",
        source="data_collection",
        status="local-estimate",
        note="Biaya pakan simplified = J * 20.000. Core, bukan isolated. SoT §9.",
    ),
    "p_gabah": ParameterMetadata(
        value=6000,
        unit="Rp/kg",
        source="data_collection",
        status="local-estimate",
        note="Harga gabah production = Rp6.000/kg. SoT §9.",
    ),
    "k_weeding": ParameterMetadata(
        value=21000,
        unit="Rp/are/kegiatan",
        source="data_collection",
        status="local-estimate",
        note="Biaya penyiangan per are per kegiatan. Sandbox saja. SoT §10.1.",
    ),
    "R_weeding": ParameterMetadata(
        value=0.77,
        unit="ratio",
        source="data_collection",
        status="local-estimate",
        note="Reduction rate weeding. Sandbox saja. SoT §10.1.",
    ),
    "HET_urea": ParameterMetadata(
        value=1800.0,
        unit="Rp/kg",
        source="regulatory",
        status="locked",
        note="HET Urea Rp1.800/kg.",
    ),
    "HET_phonska": ParameterMetadata(
        value=1840.0,
        unit="Rp/kg",
        source="regulatory",
        status="locked",
        note="HET Phonska Rp1.840/kg.",
    ),
    "HET_kcl": ParameterMetadata(
        value=9500.0,
        unit="Rp/kg",
        source="regulatory",
        status="locked",
        note="HET KCl Rp9.500/kg.",
    ),
}
