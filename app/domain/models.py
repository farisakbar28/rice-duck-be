from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class RiceVariety:
    code: str
    label: str
    hst_masuk: int
    hst_heading: int
    harvest_age_days: int
    risk_note: str
    hst_masuk_min: int
    hst_masuk_max: int
    hst_heading_min: int
    hst_heading_max: int
    status: str


@dataclass(frozen=True)
class PlantingSystem:
    code: str
    label: str
    k_max_are: float
    f_yield: float
    note: str = ""
    k_max_min_are: float = 0
    k_max_max_are: float = 0
    limited_test_max_are: float | None = None
    k_max_status: str = "estimation"
    f_yield_status: str = "estimation"
    # R1: Density constraint separation (audit-fixes-post-rev1)
    # recommended_density_min_are: batas bawah rekomendasi praktis (2.0 untuk kedua sistem)
    # recommended_density_max_are: batas atas rekomendasi praktis (4.0 Jarwo, 3.0 Tegel)
    recommended_density_min_are: float = 2.0
    recommended_density_max_are: float = 4.0


@dataclass(frozen=True)
class DSSConstants:
    survival_lambda: float
    t_max_eff_days: int
    t_phase_1_days: int
    local_feed_warning_phase_days: int
    dung_phase_1_total_kg: float
    dung_phase_2_daily_kg: float
    minimum_density_are: float
    p_max: float
    penalty_gamma: float
    alpha_local: float
    daily_duck_grazing_hours: float
    baseline_grazing_hours: float
    feed_requirement_kg_per_duck_day: float | None
    feed_natural_saving_rate: float | None
    feed_greedy_kg_per_duck_day: float | None
    rice_duck_price_rp_per_kg: float | None
    conventional_rice_price_rp_per_kg: float | None
    conventional_yield_kg_per_ha: float | None
    duck_sale_price_rp_per_duck: float
    duck_buy_price_rp_per_duck: float
    duck_target_out_max_days: int
    duck_buy_price_fallback_min_rp: float
    duck_buy_price_fallback_max_rp: float
    duck_buy_price_fallback_mid_rp: float
    feed_price_rp_per_kg: float | None
    nitrogen_price_rp_per_kg: float
    phosphate_price_rp_per_kg: float
    potassium_price_rp_per_kg: float
    weeding_cost_rp_per_are: float
    net_cost_rp: float
    net_lifetime_seasons: int
    shelter_cost_rp: float
    shelter_lifetime_seasons: int
    infrastructure_maintenance_rp_per_season: float
    additional_cost_rp_per_season: float
    kappa_n: float | None
    kappa_p: float | None
    kappa_k: float | None
    gwp_ch4: float
    gwp_n2o: float
    seasonal_ch4_rice_duck_kg_per_ha: float | None
    seasonal_ch4_conventional_kg_per_ha: float | None
    seasonal_n2o_kg_per_ha: float | None
    calibration_note: str
    # R-13 AC-4: metadata periode waktu untuk parameter harga yang terbatas waktu
    valid_period_conventional_rice_price: str = "Maret 2026"
    # Referensi nilai q_feed dari literatur (Lit_DB fallback) — Rev1_Doc §5.6
    # feed_requirement_kg_per_duck_day_reference digunakan sebagai fallback saat
    # feed_requirement_kg_per_duck_day (lokal) = None.
    #
    # OPSI A (dipilih): 0.10 kg/ekor/hari dari A02 row 975:
    #   "Average feed consumed per duck per day = 0.1 kg/day" (MATCH_EXACT).
    #   Sumber: Kumpulan Variabel... .xlsx, sheet Data, row 975, article A02.
    #   Status: literature-uncalibrated.
    #   Cluster referensi lain yang ditemukan di workbook (tidak ada yang > 0.13 sebagai angka
    #   per duck/day siap pakai): A13 130g/day=0.13, A13 80-110g/day, A16 80g/day=0.08,
    #   B5A02 689.48g/head/week≈0.099, B5A02 670.22g/head/week≈0.096.
    #   Nilai 0.12–0.225 TIDAK ditemukan sebagai angka eksplisit siap pakai di workbook referensi.
    #   q_feed lokal: belum tersedia (Excel lokal: "Jumlah pakan tambahan = Belum ada").
    feed_requirement_kg_per_duck_day_reference: float = 0.10
    # feed_natural_saving_rate_reference: 0.66 dari teks referensi "two thirds ≈ 2/3 ≈ 0.66"
    # (A03 row 630, Kumpulan Variabel... .xlsx, sheet Data). Klasifikasi: MATCH_DERIVED_FROM_TEXT.
    # Status: literature-uncalibrated. Belum tervalidasi lokal (Excel lokal row 88: "Belum bisa dipastikan").
    feed_natural_saving_rate_reference: float = 0.66


@dataclass(frozen=True)
class ParameterMetadata:
    value: Any
    unit: str
    source: str
    status: str
    note: str
    minimum: float | int | None = None
    maximum: float | int | None = None


@dataclass(frozen=True)
class User:
    id: str
    name: str
    email: str
    password_hash: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class SimulationHistory:
    id: str
    user_id: str
    input_data: dict
    actual_scenario: dict
    recommended_scenario: dict
    comparison: dict
    risk: dict
    trace: dict
    notes: list[str]
    economics: dict
    ecology: dict
    environment: dict
    lookup: dict
    validation: dict
    data_readiness: dict
    created_at: datetime


@dataclass(frozen=True)
class AuthContext:
    user: User
