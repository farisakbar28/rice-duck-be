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
        # Canonical SoT — Tabel 2.2 Calendar Engine (Catatan Finalisasi poin 8).
        hst_panen=99,
        # Deprecated legacy fields. ``harvest_age_days`` is kept in sync with
        # ``hst_panen`` (additive per keputusan #2).
        hst_masuk=20,
        hst_heading=65,
        harvest_age_days=99,
        risk_note="Default awal dari dokumen; bebek sebaiknya ditarik sebelum fase keluar malai.",
        hst_masuk_min=20,
        hst_masuk_max=20,
        hst_heading_min=60,
        hst_heading_max=65,
        status="estimation",
    ),
    RiceVariety(
        code="inpari",
        label="Inpari",
        # Canonical SoT — Tabel 2.2 Calendar Engine (Catatan Finalisasi poin 8).
        hst_panen=112,
        hst_masuk=20,
        hst_heading=65,
        harvest_age_days=112,
        risk_note="Umur panen lebih panjang sehingga jadwal panen gabah bergeser mundur.",
        hst_masuk_min=20,
        hst_masuk_max=20,
        hst_heading_min=60,
        hst_heading_max=65,
        status="estimation",
    ),
]

PLANTING_SYSTEMS = [
    PlantingSystem(
        code="jajar_legowo",
        label="Jajar Legowo",
        # Canonical SoT — Tabel 2.2 Density & Yield Engine.
        k_safe_are=4.0,
        F_sys=1.00,
        # Deprecated aliases kept in sync with canonical values.
        k_max_are=4.0,
        f_yield=1.00,
        note="Ruang gerak bebek lebih baik; K_safe = 4.0 ekor/are; F_sys = 1.00.",
        k_safe_min_are=4.0,
        k_safe_max_are=8.0,
        k_max_min_are=4.0,
        k_max_max_are=8.0,
        limited_test_max_are=6.0,
        k_max_status="local-estimate",
        f_yield_status="local-calibrated",
        recommended_density_min_are=2.0,
        recommended_density_max_are=4.0,
    ),
    PlantingSystem(
        code="tegel",
        label="Tegel / Konvensional",
        # Canonical SoT — Tabel 2.2. Tegel receives a PENALTY (0.95), NOT the
        # legacy bonus 1.39 from FINAL.md. (Catatan Finalisasi poin: Yield
        # Engine Fase B.)
        k_safe_are=3.0,
        F_sys=0.95,
        k_max_are=3.0,
        f_yield=0.95,
        note=(
            "Ruang gerak lebih sempit sehingga K_safe lebih rendah (3.0). "
            "F_sys = 0.95 adalah penalti struktural (Tabel 2.2), bukan bonus 1.39."
        ),
        k_safe_min_are=2.0,
        k_safe_max_are=3.0,
        k_max_min_are=2.0,
        k_max_max_are=3.0,
        limited_test_max_are=None,
        k_max_status="local-estimate",
        f_yield_status="local-calibrated",
        recommended_density_min_are=2.0,
        recommended_density_max_are=3.0,
    ),
]

DSS_CONSTANTS = DSSConstants(
    survival_lambda=0.67,
    t_max_eff_days=45,
    t_phase_1_days=50,
    local_feed_warning_phase_days=30,
    dung_phase_1_total_kg=4.0,
    dung_phase_2_daily_kg=0.2,
    minimum_density_are=1.0,
    p_max=0.8,
    penalty_gamma=0.5,
    # Fase 6 cleanup: ``alpha_local`` removed.
    daily_duck_grazing_hours=10.0,
    baseline_grazing_hours=10.0,
    feed_requirement_kg_per_duck_day=0.10,
    feed_natural_saving_rate=1.0,
    feed_greedy_kg_per_duck_day=0.15,
    rice_duck_price_rp_per_kg=6000.0,
    # Fase 6 cleanup: conventional_* removed.
    duck_sale_price_rp_per_duck=35000.0,
    duck_buy_price_rp_per_duck=25000.0,
    duck_target_out_max_days=60,
    duck_buy_price_fallback_min_rp=25000.0,
    duck_buy_price_fallback_max_rp=25000.0,
    duck_buy_price_fallback_mid_rp=25000.0,
    feed_price_rp_per_kg=0.0,
    # Fase 6 cleanup: phosphate_price (2700) removed — stale, unused.
    nitrogen_price_rp_per_kg=1800.0,
    potassium_price_rp_per_kg=9500.0,
    weeding_cost_rp_per_are=15000.0,
    # True-cost interview artifacts — dokumentasi saja, bukan model aktif.
    net_cost_rp=1350000.0,
    net_lifetime_seasons=3,
    shelter_cost_rp=600000.0,
    shelter_lifetime_seasons=4,
    infrastructure_maintenance_rp_per_season=0.0,
    additional_cost_rp_per_season=0.0,
    # Fase 6 cleanup: kappa_n/p/k removed.
    gwp_ch4=34.0,
    gwp_n2o=265.0,
    seasonal_ch4_rice_duck_kg_per_ha=None,
    seasonal_ch4_conventional_kg_per_ha=None,
    seasonal_n2o_kg_per_ha=None,
    calibration_note=(
        "Nilai biologis, harga, biaya, hara, dan lookup adalah default awal dari "
        "dokumen model dan masih perlu validasi lapangan Astungkara Way. "
        "alpha_local, kappa_n/p/k lama, conventional_* telah dihapus (Fase 6 cleanup)."
    ),
)

PARAMETER_METADATA = {
    "survival_lambda": ParameterMetadata(
        value=0.67,
        unit="ratio",
        source="data_collection",
        status="local-estimate",
        minimum=0.35,
        maximum=0.67,
        note="Range 0.35-0.67 dari Field_Data row 29 adalah contoh indikatif; 0.67 estimasi atas, bukan rata-rata final dan bukan local-calibrated. Perlu kalibrasi keras 3-5 siklus.",
    ),
    "hst_masuk": ParameterMetadata(
        value=20,
        unit="HST",
        source="data_collection",
        status="local-calibrated",
        minimum=20,
        maximum=20,
        note="DIKUNCI 20 HST (Standar fase vegetatif akar padi mapan).",
    ),
    "hst_heading": ParameterMetadata(
        value=65,
        unit="HST",
        source="data_collection",
        status="local-estimate",
        minimum=60,
        maximum=65,
        note="DIKUNCI 60-65 HST (Batas ditarik sebelum malai keluar).",
    ),
    "duck_age_days": ParameterMetadata(
        value=None,
        unit="day",
        source="data_collection",
        status="local-estimate",
        minimum=14,
        maximum=30,
        note="Catatan: dipakai untuk U_status, p_duck_buy_age, t_age_max, t_maks_rekomendasi, tanggal_tarik, dan Q_output. Tidak langsung mengubah yield, pakan, survival, kotoran, N/P/K, V_eco, bobot jual, atau emisi.",
    ),
    "daily_duck_grazing_hours": ParameterMetadata(
        value=10,
        unit="hour/day",
        source="data_collection",
        status="estimation",
        note="Jam aktivitas bebek sekitar 10 jam/hari.",
    ),
    "baseline_grazing_hours": ParameterMetadata(
        value=12,
        unit="hour/day",
        source="model",
        status="estimation",
        note="Baseline normalisasi t_effective dari dokumen model.",
    ),
    "rice_duck_price": ParameterMetadata(
        value=None,
        unit="Rp/kg gabah",
        source="data_collection",
        status="partial",
        note="Harga padi-bebek final belum terkunci; tidak dipakai menghitung DeltaV_rice.",
    ),
    "conventional_rice_price": ParameterMetadata(
        value=None,  # Fase 6: removed from active model.
        unit="Rp/kg gabah",
        source="data_collection",
        status="deprecated",
        minimum=5600,
        maximum=5700,
        note=(
            "DEPRECATED Fase 6. SoT _terbaru tidak memakai harga konvensional "
            "sebagai output aktif. Entry dipertahankan untuk audit historis saja."
        ),
    ),
    "conventional_yield": ParameterMetadata(
        value=None,  # Fase 6: removed from active model.
        unit="kg/ha",
        source="data_collection",
        status="deprecated",
        note=(
            "DEPRECATED Fase 6. SoT _terbaru tidak memakai yield konvensional "
            "sebagai output aktif."
        ),
    ),
    "duck_buy_price": ParameterMetadata(
        value=28000,
        unit="Rp/duck",
        source="data_collection",
        status="local-estimate",
        minimum=25000,
        maximum=28000,
        note="Nilai biaya atas digunakan sebagai default konservatif.",
    ),
    "duck_sale_price": ParameterMetadata(
        value=30000,
        unit="Rp/duck",
        source="data_collection",
        status="local-estimate",
        minimum=30000,
        maximum=60000,
        note="Nilai pendapatan bawah digunakan secara konservatif.",
    ),
    "feed_quantity": ParameterMetadata(
        value=None,
        unit="kg/duck/day",
        source="data_collection",
        status="unavailable",
        note=(
            "q_feed lokal tidak dicatat (Excel lokal row 48: 'Jumlah pakan tambahan = Belum ada'). "
            "Fallback referensi Opsi A: 0.10 kg/ekor/hari dari A02 row 975 "
            "'Average feed consumed per duck per day = 0.1 kg/day' (MATCH_EXACT, literature-uncalibrated). "
            "Cluster referensi ditemukan: A13 130g/day=0.13, A13 80-110g/day, A16 80g/day=0.08, "
            "B5A02 ~0.096-0.099 kg/day. "
            "Nilai 0.12-0.225 kg/ekor/hari TIDAK ditemukan sebagai angka eksplisit di workbook referensi."
        ),
    ),
    "net_cost": ParameterMetadata(
        value=1350000,
        unit="Rp/200m",
        source="data_collection",
        status="local-estimate",
        minimum=1200000,
        maximum=1350000,
        note="Nilai terbaru Rp1.350.000 digunakan.",
    ),
    "net_lifetime": ParameterMetadata(
        value=2,
        unit="cycle",
        source="data_collection",
        status="local-estimate",
        minimum=2,
        maximum=3,
        note="Masa pakai terpendek dipakai untuk amortisasi konservatif.",
    ),
    "shelter_cost": ParameterMetadata(
        value=600000,
        unit="Rp/unit",
        source="data_collection",
        status="local-estimate",
        note="Kandang ukuran sekitar 2x1 meter.",
    ),
    "shelter_lifetime": ParameterMetadata(
        value=3,
        unit="cycle",
        source="data_collection",
        status="local-estimate",
        minimum=3,
        maximum=4,
        note="Masa pakai terpendek dipakai untuk amortisasi konservatif.",
    ),
    "infrastructure_maintenance": ParameterMetadata(
        value=0,
        unit="Rp/cycle",
        source="data_collection",
        status="unavailable",
        note="Tidak tercatat; nol hanya placeholder perhitungan dan bukan klaim biaya nihil.",
    ),
    "weeding_cost": ParameterMetadata(
        value=6000,
        unit="Rp/are/cycle",
        source="data_collection",
        status="local-estimate",
        minimum=6000,
        maximum=25000,
        note="Nilai bawah rentang tipikal; Rp70.000-Rp72.000 diperlakukan sebagai outlier.",
    ),
    "kappa_feed_save": ParameterMetadata(
        value=0.66,
        unit="ratio",
        source="literature",
        status="literature-uncalibrated",
        note=(
            "0.66 berasal dari teks referensi: 'ducks ... eat pests, rice, weeds to substitute "
            "part of their feed ... which accounts for around two thirds of their total feed' "
            "(A03 row 630, workbook referensi sheet Data). Klasifikasi: MATCH_DERIVED_FROM_TEXT. "
            "Belum divalidasi lokal; Excel lokal row 88 menyatakan 'Angka 66% belum bisa dipastikan'."
        ),
    ),
    "K_max_are": ParameterMetadata(
        value=None,
        unit="ekor/are",
        source="data_collection",
        status="local-estimate",
        note="Daya dukung/safety constraint; Jarwo default aman 4.0 dari range 4-8; Tegel memakai rentang lokal 2-3 dengan batas praktis 3.0.",
    ),
    "f_yield": ParameterMetadata(
        value=None,
        unit="multiplier",
        source="literature",
        status="literature-uncalibrated",
        note="Faktor pengali yield; belum ada faktor numerik lokal final.",
    ),
    "technical_min_density_are": ParameterMetadata(
        value=1.0,
        unit="ekor/are",
        source="model",
        status="system-design-uncalibrated",
        note="Boundary internal grid search, bukan rekomendasi praktis.",
    ),
    "recommended_density_min_are": ParameterMetadata(
        value=2.0,
        unit="ekor/are",
        source="data_collection",
        status="local-estimate",
        note="Batas praktis rekomendasi umum dari Field_Data row 22.",
    ),
    "recommended_density_max_are": ParameterMetadata(
        value=None,
        unit="ekor/are",
        source="data_collection",
        status="local-estimate",
        note="Batas praktis rekomendasi umum dari Field_Data row 22; Jarwo 4.0, Tegel 3.0.",
    ),
    "q_feed_reference_range": ParameterMetadata(
        value=None,
        unit="kg/ekor/hari",
        source="literature",
        status="literature-uncalibrated",
        minimum=0.08,
        maximum=0.13,
        note=(
            "Cluster referensi yang ditemukan di workbook (sheet Data): "
            "A02 row 975: 0.10 kg/day (MATCH_EXACT); "
            "A13 row 487: 130g/day=0.13 kg/day; "
            "A13 row 492: 80-110g/day; "
            "A16 row 535: 80g/day=0.08 kg/day; "
            "B5A02 row 1389: 689.48g/head/week≈0.0985 kg/day; "
            "B5A02 row 1395: 670.22g/head/week≈0.0957 kg/day. "
            "Nilai 0.12-0.225 kg/ekor/hari TIDAK ditemukan eksplisit di workbook. "
            "Opsi A dipilih: fallback 0.10 dari A02 row 975 (MATCH_EXACT)."
        ),
    ),
    "q_feed_default_0_10": ParameterMetadata(
        value=0.10,
        unit="kg/ekor/hari",
        source="literature",
        status="literature-uncalibrated",
        note=(
            "OPSI A (dipilih): MATCH_EXACT dari workbook referensi sheet Data row 975, "
            "article A02: 'Average feed consumed per duck per day = 0.1 kg/day'. "
            "Ini adalah angka eksplisit yang paling traceable dari workbook. "
            "q_feed lokal belum tersedia. Nilai ini bukan data lokal Astungkara Way."
        ),
    ),
    "soil_kappa": ParameterMetadata(
        value=None,
        unit="coefficient",
        source="data_collection",
        status="unavailable",
        note=(
            "Uji kotoran bebek lokal belum tersedia. "
            "Nilai referensi literatur (MATCH_EXACT, workbook referensi sheet Data, article A02): "
            "kappa_N=0.049 (row 977), kappa_P=0.072 (row 978), kappa_K=0.032 (row 979). "
            "Status literature-uncalibrated; belum divalidasi lokal."
        ),
    ),
    "kappa_n_reference": ParameterMetadata(
        value=None,  # Fase 6: removed from active model.
        unit="kg-N / (10 kg kotoran)",
        source="literature",
        status="deprecated",
        note=(
            "DEPRECATED Fase 6. SoT _terbaru Material Engine menggunakan "
            "koefisien 0.107/0.424/0.058 (Tabel 2.2), bukan 0.049/0.072/0.032. "
            "Entry dipertahankan untuk audit historis saja."
        ),
    ),
    "kappa_p_reference": ParameterMetadata(
        value=None,
        unit="kg-P2O5 / (10 kg kotoran)",
        source="literature",
        status="deprecated",
        note="DEPRECATED Fase 6. Lihat catatan kappa_n_reference.",
    ),
    "kappa_k_reference": ParameterMetadata(
        value=None,
        unit="kg-K2O / (10 kg kotoran)",
        source="literature",
        status="deprecated",
        note="DEPRECATED Fase 6. Lihat catatan kappa_n_reference.",
    ),
    "pesticide_reduction": ParameterMetadata(
        value=None,
        unit="ratio",
        source="data_collection",
        status="unavailable",
        note="Pengaruh bersifat kualitatif dan belum kuantitatif; V_eco2 tidak dihitung.",
    ),
    "emission_flux": ParameterMetadata(
        value=None,
        unit="kg/ha/season",
        source="data_collection",
        status="unavailable",
        note="CH4, N2O, dan DO belum tersedia lokal; modul environment berstatus literature-uncalibrated dengan rumus dari basis literatur akademik.",
    ),

    "dung_phase_1_total_kg": ParameterMetadata(
        value=4.0,
        unit="kg/ekor/fase-1 (≤50 hari)",
        source="literature",
        status="literature-uncalibrated",
        note=(
            "PARTIAL_SOURCE / MODEL_ASSUMPTION. "
            "Workbook referensi Data row 976 menyebut 10 kg dung per duck untuk >=80 hari. "
            "Pembagian 4 kg fase-1 (≤50 hari) adalah asumsi model dua-fase DSS; "
            "tidak ada baris eksplisit di workbook untuk nilai 4 kg pada 50 hari. "
            "Tidak boleh diklaim sebagai angka eksplisit lokal atau referensi eksak."
        ),
    ),
    "dung_phase_2_daily_kg": ParameterMetadata(
        value=0.2,
        unit="kg/ekor/hari (fase-2, >50 hari)",
        source="literature",
        status="literature-uncalibrated",
        note=(
            "PARTIAL_SOURCE / MODEL_ASSUMPTION. "
            "Workbook referensi Data row 976: 10 kg per duck untuk >=80 hari. "
            "Rate 0.2 kg/hari adalah kelanjutan model fase-2 DSS; "
            "tidak ada baris eksplisit di workbook untuk nilai harian ini. "
            "Tidak boleh diklaim sebagai angka eksplisit lokal."
        ),
    ),
    "gwp_ch4": ParameterMetadata(
        value=34.0,
        unit="CO2-equivalent factor",
        source="literature",
        status="literature-uncalibrated",
        note=(
            "MATCH_EXACT: workbook referensi Data row 855, article A16: "
            "'GWP CH4 = 34 (IPCC, 2014)'. "
            "Formula: GWP = 34*fCH4 + 265*fN2O."
        ),
    ),
    "gwp_n2o": ParameterMetadata(
        value=265.0,
        unit="CO2-equivalent factor",
        source="literature",
        status="literature-uncalibrated",
        note=(
            "MATCH_EXACT: workbook referensi Data row 855, article A16: "
            "'GWP N2O = 265 (IPCC, 2014)'. "
            "Formula: GWP = 34*fCH4 + 265*fN2O."
        ),
    ),
    "minimum_density_are": ParameterMetadata(
        value=1.0,
        unit="ekor/are",
        source="model",
        status="system-design",
        note=(
            "SYSTEM_DESIGN. Boundary internal grid search optimizer, bukan rekomendasi praktis. "
            "Rekomendasi praktis tetap 2-4 ekor/are (Excel lokal row 22)."
        ),
    ),
    "p_max": ParameterMetadata(
        value=1.0,
        unit="dimensionless",
        source="model",
        status="system-design",
        note="SYSTEM_DESIGN. Batas maksimum fungsi penalti.",
    ),
    "penalty_gamma": ParameterMetadata(
        value=0.5,
        unit="dimensionless",
        source="model",
        status="system-design",
        note="SYSTEM_DESIGN. Koefisien penalti desain sistem, bukan data Excel.",
    ),
    # Fase 6 cleanup: ``alpha_local`` removed (Generasi-A artifact).
    "alpha_local_legacy": ParameterMetadata(
        value=None,
        unit="dimensionless",
        source="model",
        status="deprecated",
        note=(
            "DEPRECATED Fase 6. SoT _terbaru menggunakan formula "
            "Yield_are = 48.039 * F_density * F_age * F_sys * F_var (Tabel 2.2) "
            "tanpa alpha_local. Entry ini hanya sisa dokumentasi."
        ),
    ),
    "baseline_grazing_hours_system": ParameterMetadata(
        value=12.0,
        unit="jam/hari",
        source="model",
        status="system-design",
        note=(
            "SYSTEM_DESIGN. Baseline operasional untuk menghitung t_effective, "
            "bukan data lokal. "
            "Data lokal (Excel row 82): jam aktivitas bebek di sawah ~10 jam/hari."
        ),
    ),
    "infrastructure_maintenance_placeholder": ParameterMetadata(
        value=0.0,
        unit="Rp/siklus",
        source="data_collection",
        status="unavailable",
        note=(
            "PLACEHOLDER_WITH_NOTE. Biaya maintenance belum tercatat (Excel lokal row 56: "
            "'Tidak ada catatan biaya perawatan tetap'). "
            "Nilai 0 hanya placeholder agar rumus berjalan; bukan klaim biaya nol."
        ),
    ),
    "additional_cost_placeholder": ParameterMetadata(
        value=0.0,
        unit="Rp/siklus",
        source="data_collection",
        status="unavailable",
        note=(
            "PLACEHOLDER_WITH_NOTE. Biaya tambahan belum tercatat. "
            "Nilai 0 hanya placeholder; bukan klaim biaya nol."
        ),
    ),
    "t_max_eff_days": ParameterMetadata(
        value=80,
        unit="hari",
        source="literature",
        status="literature-uncalibrated",
        note=(
            "MATCH_RANGE_SELECTED_MAX / FORMULA_CONTEXT. "
            "Workbook referensi menyebut practical stocking time 50-80 hari; "
            "rumus yield model memakai t=80 sebagai batas atas parameter Gaussian. "
            "Klasifikasi: dipilih sebagai batas atas range."
        ),
    ),
    "q_feed_reference_a02": ParameterMetadata(
        value=0.10,
        unit="kg/ekor/hari",
        source="literature",
        status="literature-uncalibrated",
        note=(
            "MATCH_EXACT. Workbook referensi sheet Data row 975, article A02: "
            "'Average feed consumed per duck per day = 0.1 kg/day'. "
            "Ini adalah sumber q_feed fallback yang dipilih (Opsi A). "
            "q_feed_source=literature-reference-a02, q_feed_match_type=MATCH_EXACT, "
            "q_feed_source_file='Kumpulan Variabel, Rumus, dan Data dari Artikel Referensi.xlsx', "
            "q_feed_source_sheet='Data', q_feed_source_row=975."
        ),
    ),
    "feed_natural_saving_rate_ref": ParameterMetadata(
        value=0.66,
        unit="ratio",
        source="literature",
        status="literature-uncalibrated",
        note=(
            "MATCH_DERIVED_FROM_TEXT. Workbook referensi Data row 630, article A03: "
            "'ducks eat pests, rice, weeds ... which accounts for around two thirds of their total feed'. "
            "Dua pertiga ≈ 2/3 ≈ 0.66. Belum tervalidasi lokal (Excel lokal row 88: 'Belum bisa dipastikan')."
        ),
    ),
}


