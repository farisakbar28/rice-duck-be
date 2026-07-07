# PANDUAN PENGUJIAN SKENARIO INPUT MANUAL

## DSS Padi-Bebek — Uji Input Manual vs Rekap Bersih

**Ruang lingkup dokumen ini:** hanya menyusun daftar skenario input uji manual dan format isian untuk dimasukkan ke sistem DSS. Dokumen ini **tidak** menghitung yield/cost/profit prediksi, **tidak** menjalankan model, dan **tidak** menghasilkan metrik akurasi apa pun. Perbandingan hasil sistem vs rekap dilakukan sendiri oleh pengguna di luar dokumen ini.

**Sumber yang dirujuk:**

- Model: `Model_Matematika_Data_Collection_DSS_Padi_Bebek_FINAL.md` (Tabel 2.1 Input Manual, Tabel 2.2 Proses Komputasi, Tabel 2.3 Output).
- Rekap: `DSS_Padi_Bebek_Rekap_Bersih.xlsx`, sheet **"Dataset Actual Bersih"** (37 baris clean) dan \*\*"Protokol & Klasifikasi"`.
- Nomor baris yang disebut pada kolom "Sumber acuan" di bawah mengacu ke kolom **`Excel Row (Sumber)`** pada sheet "Dataset Actual Bersih", bukan nomor baris fisik file xlsx.

---

## A. Tabel Daftar Skenario Uji

| No  | Nama/Kategori Skenario                                               | Sumber Acuan                                                                                                                                                                                          | Tujuan Pengujian                                                                                                                                                 |
| --- | -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Baseline — kondisi ideal sesuai contoh flow model                    | Contoh flow perhitungan pada model (Tabel 2.1–2.2 file .md), bukan baris rekap                                                                                                                        | Memastikan sistem menghasilkan output yang konsisten dengan worked example resmi di dokumen model, sebagai sanity check dasar sebelum masuk ke skenario ekstrem. |
| 2   | Kepadatan normal — sistem Jarwo                                      | Excel Row 28 (I Gusti Nyoman Ngurah Wirasuta, A=6,35, J=20, d=3,15, Jarwo 2:1)                                                                                                                        | Memvalidasi `density_status` normal (tanpa flag) pada sistem Jarwo dengan kondisi lapangan riil.                                                                 |
| 3   | Kepadatan normal — sistem Tegel                                      | Excel Row 36 (I Wayan Suarta, A=6,6, J=19, d=2,88, Tegel)                                                                                                                                             | Memvalidasi status normal pada Tegel (K_safe=3) sekaligus memastikan penalti `F_sys=0,95` diterapkan meski densitas mendekati ambang.                            |
| 4   | Kepadatan rendah (under-density) — Jarwo                             | Excel Row 9 (I Nyoman Ranes, A=5,1, J=5, d=0,98, Jarwo, Density Flag: <1 ekor/are)                                                                                                                    | Memvalidasi kemunculan `P_under` > 0 dan flag under-density pada kondisi riil rekap sistem Jarwo.                                                                |
| 5   | Kepadatan rendah (under-density) — Tegel                             | Excel Row 41 (I Gusti Nyoman Ngurah Wirasuta, A=6,35, J=5, d=0,79, Tegel, Density Flag: <1 ekor/are)                                                                                                  | Memvalidasi `P_under` pada kombinasi Tegel (K_safe=3) dengan densitas sangat rendah.                                                                             |
| 6   | Kepadatan sangat rendah ekstrem + luas lahan maksimum rekap          | Excel Row 64 (I Wayan Sari Merta, A=17,19, J=8, d=0,47, Tabela/Jarwo 2:1, Density Flag: <1 ekor/are)                                                                                                  | Menguji ketahanan sistem pada kombinasi luas lahan terbesar di rekap dengan densitas ekstrem rendah.                                                             |
| 7   | Batas ambang bawah densitas tepat (d=2,0) + luas lahan minimum rekap | Excel Row 47 (I Gusti Ngurah Putu Suka Nada, A=3, J=6, d=2,0, Jarwo, tanpa flag)                                                                                                                      | Menguji titik ambang persis rumus `P_under` (d=2 → penalti nol) sekaligus luas lahan terkecil yang masih lolos filter clean (A≥2,5).                             |
| 8   | Kepadatan tinggi (over-density) tepat di atas K_safe — Jarwo         | Excel Row 43 (I Made Arsania, A=3,6, J=15, d=4,17, Jarwo, Density Flag: >K_max 4,0)                                                                                                                   | Menguji sensitivitas `P_over` pada titik sedikit di atas ambang K_safe Jarwo.                                                                                    |
| 9   | Kepadatan tinggi ekstrem — Jarwo                                     | Excel Row 26 (I Gusti Ngurah Rai Sukarta, A=5,5, J=50, d=9,09, Jarwo, Density Flag: >K_max 4,0)                                                                                                       | Menguji batas atas `P_over` (capped di 1) dan efek beruntunnya ke seluruh engine biaya/yield pada densitas ekstrem.                                              |
| 10  | Populasi bebek terbesar di rekap (J=65)                              | Excel Row 11 (I Ketut Alit Sudarsana, A=10, J=65, d=6,5, Jarwo, tanpa flag tercatat di baris ini)                                                                                                     | Menguji skala absolut populasi bebek maksimum rekap terhadap engine biaya (pakan, infra, labor) dan survival.                                                    |
| 11  | Batas ambang atas densitas tepat (d=K_safe=4,0) — Jarwo              | Ekstrapolasi dari rule model (tidak ada baris rekap dengan d persis 4,0; nilai terdekat 4,17 dan 4,55)                                                                                                | Menguji perilaku sistem tepat di titik K_safe Jarwo (transisi `P_over` dari 0 ke >0).                                                                            |
| 12  | Batas ambang atas densitas tepat (d=K_safe=3,0) — Tegel              | Ekstrapolasi dari rule model (tidak ada baris rekap Tegel dengan d persis 3,0)                                                                                                                        | Menguji titik K_safe Tegel secara presisi, kondisi yang belum pernah tercatat di rekap riil.                                                                     |
| 13  | Over-density pada sistem Tegel                                       | Ekstrapolasi dari rule model (seluruh baris Tegel di rekap memiliki d maksimum 2,9; tidak ada baris Tegel yang over-density)                                                                          | Menguji interaksi `P_over` dengan `F_sys=0,95` pada Tegel over-density, kombinasi yang tidak pernah terjadi di data lapangan.                                    |
| 14  | Umur bebek ideal — batas bawah (U=14)                                | Rentang kualitatif rekap "14-21" (berlaku sama di seluruh 37 baris, hasil estimasi wawancara — bukan titik presisi per baris); kondisi lahan mengacu Excel Row 7 (I Ketut Tantra, A=4,5, J=16, Jarwo) | Memvalidasi `R_age=0,15` tepat di batas bawah rentang ideal tanpa memicu input opsional.                                                                         |
| 15a | Umur bebek ideal — titik internal band (U=20)                        | Rentang kualitatif rekap "14-21"; titik presisi U=20 adalah ekstrapolasi dari rumus piecewise `R_age` di dalam rentang tersebut                                                                       | Menguji band internal `R_age=0,15` (U 14–20) sebelum turun ke band berikutnya.                                                                                   |
| 15b | Umur bebek ideal — titik internal band (U=21)                        | Rentang kualitatif rekap "14-21"; titik presisi U=21 adalah ekstrapolasi dari rumus piecewise `R_age`                                                                                                 | Menguji transisi `R_age` dari 0,15 menjadi 0,05 tepat di U=21, tanpa memicu input manual (masih dalam rentang ideal 14–21 versi Tabel 2.1).                      |
| 16  | Umur bebek di bawah rentang ideal (U<14) — memicu input opsional     | Ekstrapolasi dari rule model (seluruh 37 baris rekap tercatat rentang "14-21"; tidak ada baris dengan umur di bawah 14)                                                                               | Memvalidasi kemunculan input opsional `p_duck_buy_manual` dan `R_age=0,35` saat umur di bawah ideal.                                                             |
| 17  | Umur bebek di atas rentang ideal (U>21) — memicu input opsional      | Ekstrapolasi dari rule model (tidak ada baris rekap dengan umur di atas 21)                                                                                                                           | Memvalidasi `R_age=0,05` dan kemunculan input manual saat umur di atas rentang ideal.                                                                            |
| 18  | Kombinasi silang — banyak faktor tidak ideal sekaligus (set A)       | Ekstrapolasi gabungan: pola densitas & luas lahan minimum mengacu pola Excel Row 47 (A=3), kombinasi Tegel over-density (skenario 13) dan umur ekstrem rendah (skenario 16) tidak punya padanan rekap | Menguji ketahanan sistem saat densitas tinggi, sistem tanam Tegel, umur ekstrem rendah, dan luas lahan minimum terjadi bersamaan.                                |
| 19  | Kombinasi silang — banyak faktor tidak ideal sekaligus (set B)       | Sebagian riil: pola densitas sangat rendah + luas lahan besar mengacu Excel Row 64 (A=17,19, J=8); umur ekstrem tinggi (skenario 17) adalah ekstrapolasi                                              | Menguji kombinasi densitas sangat rendah, luas lahan besar, dan umur bebek jauh di atas ideal secara bersamaan.                                                  |
| 20a | Variasi Varietas — Inpari                                            | Ekstrapolasi total (rekap tidak memiliki kolom Varietas sama sekali); kondisi lahan mengacu Excel Row 28                                                                                              | Menguji apakah `F_var=1,00` konsisten dan `HST_panen` berubah menjadi 95 hari sesuai definisi Calendar Engine untuk Inpari.                                      |
| 20b | Variasi Varietas — Sertani/Seratih                                   | Ekstrapolasi total (rekap tidak memiliki kolom Varietas sama sekali); kondisi lahan mengacu Excel Row 28 (identik dengan 20a kecuali Varietas)                                                        | Menguji `HST_panen`=105 hari untuk Sertani/Seratih sebagai pembanding langsung terhadap skenario 20a.                                                            |

---

## B. Format Isian Input Per Skenario (JSON siap copy-paste ke Postman)

Setiap blok JSON berikut siap ditempel langsung ke body request Postman, satu per satu sesuai skenario. Mapping kategori ke value string:

- `rice_variety`: `"sertani"` (untuk Sertani/Seratih) atau `"inpari"`.
- `planting_system`: `"jajar_legowo"` (untuk Jarwo) atau `"tegel"`.

**Catatan penting soal field opsional:** nama key untuk input opsional "Harga Beli Bebek Manual" **tidak disebutkan** di file model maupun rekap (file model hanya menyebut simbol `p_duck_buy_manual`, bukan nama field API). Di bawah ini dipakai nama tentatif `"duck_buy_price_manual_rp"` — **mohon sesuaikan dengan nama field aktual di endpoint backend Anda** sebelum submit, karena ini bukan hasil pembacaan sumber, melainkan asumsi penamaan agar formatnya konsisten dengan 6 field lain.

**Skenario 1 — Baseline**

```postman_json
{
    "land_area_are": 10,
    "duck_count": 50,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-01-01",
    "duck_age_days": 14
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_DENSITY",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-01-22",
    "D_tarik_bebek": "2026-03-07",
    "D_panen_gabah": "2026-04-10",
    "N_survive": 27.5014,
    "Yield_are_predict": 44.4961,
    "Yield_total_predict": 444.9612,
    "Revenue_gabah": 2669767.43,
    "Revenue_duck": 962549.22,
    "Total_Revenue": 3632316.64,
    "Cost_duck_buy": 1250000.0,
    "Cost_feed": 315625.0,
    "Cost_labor_base": 475270.0,
    "Cost_labor_weed_hired": 65684.88,
    "Cost_labor_total": 540954.88,
    "Cost_infra_net": 78163.6,
    "Cost_infra_cage": 208325.0,
    "Cost_infra": 286488.6,
    "Cost_fertilizer_total": 142734.51,
    "Cost_fert_urea": 37269.7,
    "Cost_fert_phonska": 14126.05,
    "Cost_fert_kcl": 91338.77,
    "Cost_pesticide": 6440.0,
    "Cost_total_cash": 2612242.99,
    "Profit_net_cash": 1020073.65,
    "Valuation_weed_eco": 122484.11,
    "Profit_net_full": 1142557.76,
    "F_sys": 1.0
}
```

**Skenario 2 — Kepadatan normal, Jarwo**

```postman_json
{
    "land_area_are": 6.35,
    "duck_count": 20,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-02-05",
    "duck_age_days": 17
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-02-26",
    "D_tarik_bebek": "2026-04-11",
    "D_panen_gabah": "2026-05-15",
    "N_survive": 12.395,
    "Yield_are_predict": 47.4625,
    "Yield_total_predict": 301.3871,
    "Revenue_gabah": 1808322.47,
    "Revenue_duck": 433825.0,
    "Total_Revenue": 2242147.47,
    "Cost_duck_buy": 500000.0,
    "Cost_feed": 107500.0,
    "Cost_labor_base": 301796.45,
    "Cost_labor_weed_hired": 70875.12,
    "Cost_labor_total": 372671.57,
    "Cost_infra_net": 62286.14,
    "Cost_infra_cage": 83330.0,
    "Cost_infra": 145616.14,
    "Cost_fertilizer_total": 83880.72,
    "Cost_fert_urea": 16167.34,
    "Cost_fert_phonska": 34340.44,
    "Cost_fert_kcl": 33372.95,
    "Cost_pesticide": 6440.0,
    "Cost_total_cash": 1216108.44,
    "Profit_net_cash": 1026039.03,
    "Valuation_weed_eco": 62911.5,
    "Profit_net_full": 1088950.53,
    "F_sys": 1.0
}
```

**Skenario 3 — Kepadatan normal, Tegel**

```postman_json
{
    "land_area_are": 6.6,
    "duck_count": 19,
    "rice_variety": "inpari",
    "planting_system": "tegel",
    "planting_date": "2026-02-10",
    "duck_age_days": 16
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-03-03",
    "D_tarik_bebek": "2026-04-16",
    "D_panen_gabah": "2026-06-02",
    "N_survive": 11.7752,
    "Yield_are_predict": 45.0894,
    "Yield_total_predict": 297.5901,
    "Revenue_gabah": 1785540.45,
    "Revenue_duck": 412133.75,
    "Total_Revenue": 2197674.2,
    "Cost_duck_buy": 475000.0,
    "Cost_feed": 102125.0,
    "Cost_labor_base": 313678.2,
    "Cost_labor_weed_hired": 79987.62,
    "Cost_labor_total": 393665.82,
    "Cost_infra_net": 63500.41,
    "Cost_infra_cage": 79163.5,
    "Cost_infra": 142663.91,
    "Cost_fertilizer_total": 85706.6,
    "Cost_fert_urea": 15164.9,
    "Cost_fert_phonska": 41237.35,
    "Cost_fert_kcl": 29304.36,
    "Cost_pesticide": 6440.0,
    "Cost_total_cash": 1205601.33,
    "Profit_net_cash": 992072.88,
    "Valuation_weed_eco": 61777.5,
    "Profit_net_full": 1053850.37,
    "F_sys": 0.95
}
```

**Skenario 4 — Under-density, Jarwo**

```postman_json
{
    "land_area_are": 5.1,
    "duck_count": 5,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-03-12",
    "duck_age_days": 15
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_UNDER_DENSITY",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-04-02",
    "D_tarik_bebek": "2026-05-16",
    "D_panen_gabah": "2026-06-19",
    "N_survive": 3.0987,
    "Yield_are_predict": 44.5589,
    "Yield_total_predict": 227.2506,
    "Revenue_gabah": 1363503.62,
    "Revenue_duck": 108456.25,
    "Total_Revenue": 1471959.87,
    "Cost_duck_buy": 125000.0,
    "Cost_feed": 26875.0,
    "Cost_labor_base": 242387.7,
    "Cost_labor_weed_hired": 112772.14,
    "Cost_labor_total": 355159.84,
    "Cost_infra_net": 55819.97,
    "Cost_infra_cage": 20832.5,
    "Cost_infra": 76652.47,
    "Cost_fertilizer_total": 64741.02,
    "Cost_fert_urea": 2840.6,
    "Cost_fert_phonska": 61900.42,
    "Cost_fert_kcl": 0.0,
    "Cost_pesticide": 6440.0,
    "Cost_total_cash": 654868.33,
    "Profit_net_cash": 817091.54,
    "Valuation_weed_eco": 20901.42,
    "Profit_net_full": 837992.96,
    "F_sys": 1.0
}
```

**Skenario 5 — Under-density, Tegel**

```postman_json
{
    "land_area_are": 6.35,
    "duck_count": 5,
    "rice_variety": "inpari",
    "planting_system": "tegel",
    "planting_date": "2026-03-15",
    "duck_age_days": 18
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_UNDER_DENSITY",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-04-05",
    "D_tarik_bebek": "2026-05-19",
    "D_panen_gabah": "2026-07-05",
    "N_survive": 3.0987,
    "Yield_are_predict": 41.8089,
    "Yield_total_predict": 265.4864,
    "Revenue_gabah": 1592918.51,
    "Revenue_duck": 108456.25,
    "Total_Revenue": 1701374.76,
    "Cost_duck_buy": 125000.0,
    "Cost_feed": 26875.0,
    "Cost_labor_base": 301796.45,
    "Cost_labor_weed_hired": 149546.85,
    "Cost_labor_total": 451343.30000000005,
    "Cost_infra_net": 62286.14,
    "Cost_infra_cage": 20832.5,
    "Cost_infra": 83118.64,
    "Cost_fertilizer_total": 83286.95,
    "Cost_fert_urea": 2413.12,
    "Cost_fert_phonska": 80873.84,
    "Cost_fert_kcl": 0.0,
    "Cost_pesticide": 6440.0,
    "Cost_total_cash": 776063.8900000001,
    "Profit_net_cash": 925310.8799999999,
    "Valuation_weed_eco": 21483.39,
    "Profit_net_full": 946794.27,
    "F_sys": 0.95
}
```

**Skenario 6 — Under-density ekstrem + luas lahan maksimum**

```postman_json
{
    "land_area_are": 17.19,
    "duck_count": 8,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-04-20",
    "duck_age_days": 20
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_UNDER_DENSITY",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-05-11",
    "D_tarik_bebek": "2026-06-24",
    "D_panen_gabah": "2026-07-28",
    "N_survive": 4.958,
    "Yield_are_predict": 43.0923,
    "Yield_total_predict": 740.7572,
    "Revenue_gabah": 4444543.38,
    "Revenue_duck": 173530.0,
    "Total_Revenue": 4618073.38,
    "Cost_duck_buy": 200000.0,
    "Cost_feed": 43000.0,
    "Cost_labor_base": 816989.13,
    "Cost_labor_weed_hired": 450002.52,
    "Cost_labor_total": 1266991.65,
    "Cost_infra_net": 102480.79,
    "Cost_infra_cage": 33332.0,
    "Cost_infra": 135812.79,
    "Cost_fertilizer_total": 237561.46,
    "Cost_fert_urea": 1456.81,
    "Cost_fert_phonska": 236104.64,
    "Cost_fert_kcl": 0.0,
    "Cost_pesticide": 6440.0,
    "Cost_total_cash": 1889805.9,
    "Profit_net_cash": 2728267.48,
    "Valuation_weed_eco": 36013.85,
    "Profit_net_full": 2764281.32,
    "F_sys": 1.0
}
```

**Skenario 7 — Batas ambang bawah densitas (d=2,0) + luas lahan minimum**

```postman_json
{
    "land_area_are": 3,
    "duck_count": 6,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-05-01",
    "duck_age_days": 14
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-05-22",
    "D_tarik_bebek": "2026-07-05",
    "D_panen_gabah": "2026-08-08",
    "N_survive": 3.7185,
    "Yield_are_predict": 47.4625,
    "Yield_total_predict": 142.3876,
    "Revenue_gabah": 854325.58,
    "Revenue_duck": 130147.5,
    "Total_Revenue": 984473.08,
    "Cost_duck_buy": 150000.0,
    "Cost_feed": 32250.0,
    "Cost_labor_base": 142581.0,
    "Cost_labor_weed_hired": 47801.72,
    "Cost_labor_total": 190382.72,
    "Cost_infra_net": 42811.97,
    "Cost_infra_cage": 24999.0,
    "Cost_infra": 67810.97,
    "Cost_fertilizer_total": 36779.73,
    "Cost_fert_urea": 4475.73,
    "Cost_fert_phonska": 26922.85,
    "Cost_fert_kcl": 5381.16,
    "Cost_pesticide": 6440.0,
    "Cost_total_cash": 483663.42,
    "Profit_net_cash": 500809.66,
    "Valuation_weed_eco": 21822.77,
    "Profit_net_full": 522632.43,
    "F_sys": 1.0
}
```

**Skenario 8 — Over-density tepat di atas K_safe, Jarwo**

```postman_json
{
    "land_area_are": 3.6,
    "duck_count": 15,
    "rice_variety": "inpari",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-05-03",
    "duck_age_days": 16
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_DENSITY",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-05-24",
    "D_tarik_bebek": "2026-07-07",
    "D_panen_gabah": "2026-08-23",
    "N_survive": 9.1219,
    "Yield_are_predict": 46.9681,
    "Yield_total_predict": 169.0853,
    "Revenue_gabah": 1014511.62,
    "Revenue_duck": 319268.09,
    "Total_Revenue": 1333779.71,
    "Cost_duck_buy": 375000.0,
    "Cost_feed": 82968.75,
    "Cost_labor_base": 171097.2,
    "Cost_labor_weed_hired": 29793.02,
    "Cost_labor_total": 200890.22,
    "Cost_infra_net": 46898.16,
    "Cost_infra_cage": 62497.5,
    "Cost_infra": 109395.66,
    "Cost_fertilizer_total": 50346.68,
    "Cost_fert_urea": 12265.17,
    "Cost_fert_phonska": 8982.55,
    "Cost_fert_kcl": 29098.95,
    "Cost_pesticide": 6440.0,
    "Cost_total_cash": 825041.31,
    "Profit_net_cash": 508738.4,
    "Valuation_weed_eco": 41615.65,
    "Profit_net_full": 550354.05,
    "F_sys": 1.0
}
```

**Skenario 9 — Over-density ekstrem, Jarwo**

```postman_json
{
    "land_area_are": 5.5,
    "duck_count": 50,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-05-10",
    "duck_age_days": 15
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_DENSITY",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-05-31",
    "D_tarik_bebek": "2026-07-14",
    "D_panen_gabah": "2026-08-17",
    "N_survive": 17.0431,
    "Yield_are_predict": 35.5969,
    "Yield_total_predict": 195.7829,
    "Revenue_gabah": 1174697.67,
    "Revenue_duck": 596509.38,
    "Total_Revenue": 1771207.04,
    "Cost_duck_buy": 1250000.0,
    "Cost_feed": 456250.0,
    "Cost_labor_base": 261398.5,
    "Cost_labor_weed_hired": 15021.84,
    "Cost_labor_total": 276420.34,
    "Cost_infra_net": 57967.68,
    "Cost_infra_cage": 208325.0,
    "Cost_infra": 266292.68,
    "Cost_fertilizer_total": 80416.87,
    "Cost_fert_urea": 22751.95,
    "Cost_fert_phonska": 0.0,
    "Cost_fert_kcl": 57664.91,
    "Cost_pesticide": 6440.0,
    "Cost_total_cash": 2335819.88,
    "Profit_net_cash": -564612.84,
    "Valuation_weed_eco": 76904.84,
    "Profit_net_full": -487708.0,
    "F_sys": 1.0
}
```

**Skenario 10 — Populasi terbesar rekap (J=65)**

```postman_json
{
    "land_area_are": 10,
    "duck_count": 65,
    "rice_variety": "inpari",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-05-15",
    "duck_age_days": 17
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_DENSITY",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-06-05",
    "D_tarik_bebek": "2026-07-19",
    "D_panen_gabah": "2026-09-04",
    "N_survive": 28.9539,
    "Yield_are_predict": 40.0465,
    "Yield_total_predict": 400.4651,
    "Revenue_gabah": 2402790.68,
    "Revenue_duck": 1013388.09,
    "Total_Revenue": 3416178.77,
    "Cost_duck_buy": 1625000.0,
    "Cost_feed": 501718.75,
    "Cost_labor_base": 475270.0,
    "Cost_labor_weed_hired": 45092.99,
    "Cost_labor_total": 520362.99,
    "Cost_infra_net": 78163.6,
    "Cost_infra_cage": 270822.5,
    "Cost_infra": 348986.1,
    "Cost_fertilizer_total": 144670.61,
    "Cost_fert_urea": 39418.79,
    "Cost_fert_phonska": 6855.21,
    "Cost_fert_kcl": 98396.61,
    "Cost_pesticide": 6440.0,
    "Cost_total_cash": 3147178.45,
    "Profit_net_cash": 269000.32,
    "Valuation_weed_eco": 129666.88,
    "Profit_net_full": 398667.2,
    "F_sys": 1.0
}
```

**Skenario 11 — Batas ambang atas densitas tepat (d=4,0), Jarwo [ekstrapolasi]**

```postman_json
{
    "land_area_are": 10,
    "duck_count": 40,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-06-01",
    "duck_age_days": 16
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-06-22",
    "D_tarik_bebek": "2026-08-05",
    "D_panen_gabah": "2026-09-08",
    "N_survive": 24.79,
    "Yield_are_predict": 47.4625,
    "Yield_total_predict": 474.6253,
    "Revenue_gabah": 2847751.92,
    "Revenue_duck": 867650.0,
    "Total_Revenue": 3715401.92,
    "Cost_duck_buy": 1000000.0,
    "Cost_feed": 215000.0,
    "Cost_labor_base": 475270.0,
    "Cost_labor_weed_hired": 86812.33,
    "Cost_labor_total": 562082.33,
    "Cost_infra_net": 78163.6,
    "Cost_infra_cage": 166660.0,
    "Cost_infra": 244823.6,
    "Cost_fertilizer_total": 139120.46,
    "Cost_fert_urea": 33258.05,
    "Cost_fert_phonska": 27698.29,
    "Cost_fert_kcl": 78164.12,
    "Cost_pesticide": 6440.0,
    "Cost_total_cash": 2167466.39,
    "Profit_net_cash": 1547935.53,
    "Valuation_weed_eco": 113890.66,
    "Profit_net_full": 1661826.18,
    "F_sys": 1.0
}
```

**Skenario 12 — Batas ambang atas densitas tepat (d=3,0), Tegel [ekstrapolasi]**

```postman_json
{
    "land_area_are": 10,
    "duck_count": 30,
    "rice_variety": "inpari",
    "planting_system": "tegel",
    "planting_date": "2026-06-05",
    "duck_age_days": 16
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-06-26",
    "D_tarik_bebek": "2026-08-09",
    "D_panen_gabah": "2026-09-25",
    "N_survive": 18.5925,
    "Yield_are_predict": 45.0894,
    "Yield_total_predict": 450.8941,
    "Revenue_gabah": 2705364.32,
    "Revenue_duck": 650737.5,
    "Total_Revenue": 3356101.82,
    "Cost_duck_buy": 750000.0,
    "Cost_feed": 161250.0,
    "Cost_labor_base": 475270.0,
    "Cost_labor_weed_hired": 116793.61,
    "Cost_labor_total": 592063.61,
    "Cost_infra_net": 78163.6,
    "Cost_infra_cage": 124995.0,
    "Cost_infra": 203158.6,
    "Cost_fertilizer_total": 130859.78,
    "Cost_fert_urea": 24088.57,
    "Cost_fert_phonska": 58720.56,
    "Cost_fert_kcl": 48050.66,
    "Cost_pesticide": 6440.0,
    "Cost_total_cash": 1843771.99,
    "Profit_net_cash": 1512329.83,
    "Valuation_weed_eco": 96100.85,
    "Profit_net_full": 1608430.68,
    "F_sys": 0.95
}
```

**Skenario 13 — Over-density pada Tegel [ekstrapolasi]**

```postman_json
{
    "land_area_are": 5,
    "duck_count": 20,
    "rice_variety": "sertani",
    "planting_system": "tegel",
    "planting_date": "2026-06-10",
    "duck_age_days": 15
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_DENSITY",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-07-01",
    "D_tarik_bebek": "2026-08-14",
    "D_panen_gabah": "2026-09-17",
    "N_survive": 11.2795,
    "Yield_are_predict": 42.8349,
    "Yield_total_predict": 214.1747,
    "Revenue_gabah": 1285048.05,
    "Revenue_duck": 394780.75,
    "Total_Revenue": 1679828.8,
    "Cost_duck_buy": 500000.0,
    "Cost_feed": 122500.0,
    "Cost_labor_base": 237635.0,
    "Cost_labor_weed_hired": 43406.17,
    "Cost_labor_total": 281041.17,
    "Cost_infra_net": 55270.01,
    "Cost_infra_cage": 83330.0,
    "Cost_infra": 138600.01,
    "Cost_fertilizer_total": 68073.31,
    "Cost_fert_urea": 14978.52,
    "Cost_fert_phonska": 19433.15,
    "Cost_fert_kcl": 33661.64,
    "Cost_pesticide": 6440.0,
    "Cost_total_cash": 1116654.49,
    "Profit_net_cash": 563174.32,
    "Valuation_weed_eco": 54928.31,
    "Profit_net_full": 618102.63,
    "F_sys": 0.95
}
```

**Skenario 14 — Umur ideal batas bawah (U=14)**

```postman_json
{
    "land_area_are": 4.5,
    "duck_count": 16,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-06-15",
    "duck_age_days": 14
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-07-06",
    "D_tarik_bebek": "2026-08-19",
    "D_panen_gabah": "2026-09-22",
    "N_survive": 9.916,
    "Yield_are_predict": 47.4625,
    "Yield_total_predict": 213.5814,
    "Revenue_gabah": 1281488.36,
    "Revenue_duck": 347060.0,
    "Total_Revenue": 1628548.36,
    "Cost_duck_buy": 400000.0,
    "Cost_feed": 86000.0,
    "Cost_labor_base": 213871.5,
    "Cost_labor_weed_hired": 44484.07,
    "Cost_labor_total": 258355.57,
    "Cost_infra_net": 52433.74,
    "Cost_infra_cage": 66664.0,
    "Cost_infra": 119097.74,
    "Cost_fertilizer_total": 60952.07,
    "Cost_fert_urea": 13132.23,
    "Cost_fert_phonska": 18668.68,
    "Cost_fert_kcl": 29151.16,
    "Cost_pesticide": 6440.0,
    "Cost_total_cash": 930845.37,
    "Profit_net_cash": 697702.99,
    "Valuation_weed_eco": 47952.62,
    "Profit_net_full": 745655.61,
    "F_sys": 1.0
}
```

**Skenario 15a — Umur ideal titik internal (U=20)**

```postman_json
{
    "land_area_are": 4.5,
    "duck_count": 16,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-06-20",
    "duck_age_days": 20
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-07-11",
    "D_tarik_bebek": "2026-08-24",
    "D_panen_gabah": "2026-09-27",
    "N_survive": 9.916,
    "Yield_are_predict": 47.4625,
    "Yield_total_predict": 213.5814,
    "Revenue_gabah": 1281488.36,
    "Revenue_duck": 347060.0,
    "Total_Revenue": 1628548.36,
    "Cost_duck_buy": 400000.0,
    "Cost_feed": 86000.0,
    "Cost_labor_base": 213871.5,
    "Cost_labor_weed_hired": 44484.07,
    "Cost_labor_total": 258355.57,
    "Cost_infra_net": 52433.74,
    "Cost_infra_cage": 66664.0,
    "Cost_infra": 119097.74,
    "Cost_fertilizer_total": 60952.07,
    "Cost_fert_urea": 13132.23,
    "Cost_fert_phonska": 18668.68,
    "Cost_fert_kcl": 29151.16,
    "Cost_pesticide": 6440.0,
    "Cost_total_cash": 930845.37,
    "Profit_net_cash": 697702.99,
    "Valuation_weed_eco": 47952.62,
    "Profit_net_full": 745655.61,
    "F_sys": 1.0
}
```

**Skenario 15b — Umur ideal titik internal (U=21)**

```postman_json
{
    "land_area_are": 4.5,
    "duck_count": 16,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-06-25",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE_WARNING",
    "D_masuk_bebek": "2026-07-16",
    "D_tarik_bebek": "2026-08-29",
    "D_panen_gabah": "2026-10-02",
    "N_survive": 10.452,
    "Yield_are_predict": 47.8468,
    "Yield_total_predict": 215.3108,
    "Revenue_gabah": 1291864.79,
    "Revenue_duck": 365820.0,
    "Total_Revenue": 1657684.79,
    "Cost_duck_buy": 400000.0,
    "Cost_feed": 82000.0,
    "Cost_labor_base": 213871.5,
    "Cost_labor_weed_hired": 44484.07,
    "Cost_labor_total": 258355.57,
    "Cost_infra_net": 52433.74,
    "Cost_infra_cage": 66664.0,
    "Cost_infra": 119097.74,
    "Cost_fertilizer_total": 61666.51,
    "Cost_fert_urea": 13925.26,
    "Cost_fert_phonska": 15985.68,
    "Cost_fert_kcl": 31755.57,
    "Cost_pesticide": 6440.0,
    "Cost_total_cash": 927559.81,
    "Profit_net_cash": 730124.98,
    "Valuation_weed_eco": 47622.3,
    "Profit_net_full": 777747.28,
    "F_sys": 1.0
}
```

**Skenario 16 — Umur di bawah ideal, U<14 [ekstrapolasi, memicu input opsional]**

```postman_json
{
    "land_area_are": 5,
    "duck_count": 15,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-01",
    "duck_age_days": 10,
    "duck_buy_price_rp_per_duck": 8000
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE_WARNING",
    "D_masuk_bebek": "2026-07-22",
    "D_tarik_bebek": "2026-09-04",
    "D_panen_gabah": "2026-10-08",
    "N_survive": 8.2912,
    "Yield_are_predict": 46.6939,
    "Yield_total_predict": 233.4695,
    "Revenue_gabah": 1400817.24,
    "Revenue_duck": 290193.75,
    "Total_Revenue": 1691010.99,
    "Cost_duck_buy": 120000.0,
    "Cost_feed": 88125.0,
    "Cost_labor_base": 237635.0,
    "Cost_labor_weed_hired": 58396.81,
    "Cost_labor_total": 296031.81,
    "Cost_infra_net": 55270.01,
    "Cost_infra_cage": 62497.5,
    "Cost_infra": 117767.51,
    "Cost_fertilizer_total": 64090.32,
    "Cost_fert_urea": 10557.34,
    "Cost_fert_phonska": 34390.92,
    "Cost_fert_kcl": 19142.06,
    "Cost_pesticide": 6440.0,
    "Cost_total_cash": 692454.64,
    "Profit_net_cash": 998556.35,
    "Valuation_weed_eco": 48615.98,
    "Profit_net_full": 1047172.33,
    "F_sys": 1.0
}
```

_(nilai 8000 dipilih dalam rentang `Buy Price Duck` yang teramati di rekap: Rp0–Rp32.000/ekor)_

**Skenario 17 — Umur di atas ideal, U>21 [ekstrapolasi, memicu input opsional]**

```postman_json
{
    "land_area_are": 5,
    "duck_count": 15,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-05",
    "duck_age_days": 28,
    "duck_buy_price_rp_per_duck": 15000
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE_WARNING",
    "D_masuk_bebek": "2026-07-26",
    "D_tarik_bebek": "2026-09-08",
    "D_panen_gabah": "2026-10-12",
    "N_survive": 9.7988,
    "Yield_are_predict": 47.8468,
    "Yield_total_predict": 239.2342,
    "Revenue_gabah": 1435405.32,
    "Revenue_duck": 342956.25,
    "Total_Revenue": 1778361.57,
    "Cost_duck_buy": 225000.0,
    "Cost_feed": 76875.0,
    "Cost_labor_base": 237635.0,
    "Cost_labor_weed_hired": 58396.81,
    "Cost_labor_total": 296031.81,
    "Cost_infra_net": 55270.01,
    "Cost_infra_cage": 62497.5,
    "Cost_infra": 117767.51,
    "Cost_fertilizer_total": 66099.67,
    "Cost_fert_urea": 12787.75,
    "Cost_fert_phonska": 26844.96,
    "Cost_fert_kcl": 26466.96,
    "Cost_pesticide": 6440.0,
    "Cost_total_cash": 788213.99,
    "Profit_net_cash": 990147.58,
    "Valuation_weed_eco": 47767.65,
    "Profit_net_full": 1037915.23,
    "F_sys": 1.0
}
```

_(nilai 15000 dipilih dalam rentang `Buy Price Duck` rekap)_

**Skenario 18 — Kombinasi silang set A (Tegel + over-density + umur ekstrem rendah + lahan minimum) [ekstrapolasi gabungan]**

```postman_json
{
    "land_area_are": 3,
    "duck_count": 15,
    "rice_variety": "inpari",
    "planting_system": "tegel",
    "planting_date": "2026-07-10",
    "duck_age_days": 10,
    "duck_buy_price_rp_per_duck": 7500
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_DENSITY",
    "age_status": "AGE_BUY_RANGE_WARNING",
    "D_masuk_bebek": "2026-07-31",
    "D_tarik_bebek": "2026-09-13",
    "D_panen_gabah": "2026-10-30",
    "N_survive": 6.7988,
    "Yield_are_predict": 39.9233,
    "Yield_total_predict": 119.7699,
    "Revenue_gabah": 718619.24,
    "Revenue_duck": 237958.87,
    "Total_Revenue": 956578.12,
    "Cost_duck_buy": 112500.0,
    "Cost_feed": 110625.0,
    "Cost_labor_base": 142581.0,
    "Cost_labor_weed_hired": 19705.47,
    "Cost_labor_total": 162286.47,
    "Cost_infra_net": 42811.97,
    "Cost_infra_cage": 62497.5,
    "Cost_infra": 105309.47,
    "Cost_fertilizer_total": 40885.51,
    "Cost_fert_urea": 9033.21,
    "Cost_fert_phonska": 11503.94,
    "Cost_fert_kcl": 20348.36,
    "Cost_pesticide": 6440.0,
    "Cost_total_cash": 538046.44,
    "Profit_net_cash": 418531.68,
    "Valuation_weed_eco": 36407.56,
    "Profit_net_full": 454939.24,
    "F_sys": 0.95
}
```

**Skenario 19 — Kombinasi silang set B (under-density ekstrem + lahan besar + umur ekstrem tinggi) [sebagian riil, sebagian ekstrapolasi]**

```postman_json
{
    "land_area_are": 17,
    "duck_count": 8,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-15",
    "duck_age_days": 25,
    "duck_buy_price_rp_per_duck": 20000
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_UNDER_DENSITY",
    "age_status": "AGE_BUY_RANGE_WARNING",
    "D_masuk_bebek": "2026-08-05",
    "D_tarik_bebek": "2026-09-18",
    "D_panen_gabah": "2026-10-22",
    "N_survive": 5.226,
    "Yield_are_predict": 43.4562,
    "Yield_total_predict": 738.7553,
    "Revenue_gabah": 4432531.63,
    "Revenue_duck": 182910.0,
    "Total_Revenue": 4615441.63,
    "Cost_duck_buy": 160000.0,
    "Cost_feed": 41000.0,
    "Cost_labor_base": 807959.0,
    "Cost_labor_weed_hired": 444266.45,
    "Cost_labor_total": 1252225.45,
    "Cost_infra_net": 101912.86,
    "Cost_infra_cage": 33332.0,
    "Cost_infra": 135244.86,
    "Cost_fertilizer_total": 233797.49,
    "Cost_fert_urea": 1918.31,
    "Cost_fert_phonska": 231879.18,
    "Cost_fert_kcl": 0.0,
    "Cost_pesticide": 6440.0,
    "Cost_total_cash": 1828707.81,
    "Profit_net_cash": 2786733.82,
    "Valuation_weed_eco": 35951.22,
    "Profit_net_full": 2822685.04,
    "F_sys": 1.0
}
```

**Skenario 20a — Variasi Varietas: Inpari [ekstrapolasi total pada aspek Varietas]**

```postman_json
{
    "land_area_are": 6.35,
    "duck_count": 20,
    "rice_variety": "inpari",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-20",
    "duck_age_days": 17
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-10",
    "D_tarik_bebek": "2026-09-23",
    "D_panen_gabah": "2026-11-09",
    "N_survive": 12.395,
    "Yield_are_predict": 47.4625,
    "Yield_total_predict": 301.3871,
    "Revenue_gabah": 1808322.47,
    "Revenue_duck": 433825.0,
    "Total_Revenue": 2242147.47,
    "Cost_duck_buy": 500000.0,
    "Cost_feed": 107500.0,
    "Cost_labor_base": 301796.45,
    "Cost_labor_weed_hired": 70875.12,
    "Cost_labor_total": 372671.57,
    "Cost_infra_net": 62286.14,
    "Cost_infra_cage": 83330.0,
    "Cost_infra": 145616.14,
    "Cost_fertilizer_total": 83880.72,
    "Cost_fert_urea": 16167.34,
    "Cost_fert_phonska": 34340.44,
    "Cost_fert_kcl": 33372.95,
    "Cost_pesticide": 6440.0,
    "Cost_total_cash": 1216108.44,
    "Profit_net_cash": 1026039.03,
    "Valuation_weed_eco": 62911.5,
    "Profit_net_full": 1088950.53,
    "F_sys": 1.0
}
```

**Skenario 20b — Variasi Varietas: Sertani/Seratih [ekstrapolasi total pada aspek Varietas]**

```postman_json
{
    "land_area_are": 6.35,
    "duck_count": 20,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-20",
    "duck_age_days": 17
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-10",
    "D_tarik_bebek": "2026-09-23",
    "D_panen_gabah": "2026-10-27",
    "N_survive": 12.395,
    "Yield_are_predict": 47.4625,
    "Yield_total_predict": 301.3871,
    "Revenue_gabah": 1808322.47,
    "Revenue_duck": 433825.0,
    "Total_Revenue": 2242147.47,
    "Cost_duck_buy": 500000.0,
    "Cost_feed": 107500.0,
    "Cost_labor_base": 301796.45,
    "Cost_labor_weed_hired": 70875.12,
    "Cost_labor_total": 372671.57,
    "Cost_infra_net": 62286.14,
    "Cost_infra_cage": 83330.0,
    "Cost_infra": 145616.14,
    "Cost_fertilizer_total": 83880.72,
    "Cost_fert_urea": 16167.34,
    "Cost_fert_phonska": 34340.44,
    "Cost_fert_kcl": 33372.95,
    "Cost_pesticide": 6440.0,
    "Cost_total_cash": 1216108.44,
    "Profit_net_cash": 1026039.03,
    "Valuation_weed_eco": 62911.5,
    "Profit_net_full": 1088950.53,
    "F_sys": 1.0
}
```

---

## C. Catatan Penutup

### C.1 Kategori/kondisi yang tidak punya padanan nyata di rekap bersih

1. **Varietas Padi (Sertani/Seratih vs Inpari)** — Sheet "Dataset Actual Bersih" **tidak memiliki kolom Varietas sama sekali**. Seluruh 30 kolom yang ada (Excel Row s.d. Field Notes) tidak menyebut varietas padi. Akibatnya, **seluruh skenario yang menyoroti aspek Varietas (20a, 20b, dan penyertaan Varietas di skenario lain) murni ekstrapolasi dari rule model** (`F_var=1,00`; pembeda hanya di HST panen 95 vs 105 hari pada Calendar Engine). Tidak ada cara menyilangkan pilihan Varietas dengan baris rekap mana pun.
2. **Umur Bebek di luar rentang ideal (U<14 atau U>21)** — Kolom "Estimatasi Kualitatif U_bebek (Umur Masuk, hari)" bernilai **"14-21" secara konstan di seluruh 37 baris clean**, karena menurut sheet "Protokol & Klasifikasi" kolom ini memang tidak ada di file mentah dan diisi ulang berdasarkan estimasi wawancara, bukan pengukuran per siklus. Jadi tidak ada satu pun baris rekap yang mewakili kondisi umur di luar ideal (skenario 16, 17, 18, 19 murni ekstrapolasi rule model).
3. **Titik presisi umur di dalam rentang ideal (mis. U=14 persis, U=20, U=21)** — Karena kolom di atas hanya berupa rentang "14-21" (bukan angka presisi per baris), setiap skenario yang menyebut umur presisi (14/1520/21/dst) hanya bisa disebut "berada dalam rentang kualitatif rekap", bukan tervalidasi presisi dari satu baris nyata.
4. **Over-density pada sistem Tegel** — Empat baris Tegel di rekap memiliki densitas maksimum 2,9 ekor/are (di bawah K_safe Tegel=3). Tidak ada satu pun baris Tegel yang over-density, sehingga skenario 13 dan bagian Tegel pada skenario 18 murni ekstrapolasi.
5. **Titik ambang persis K_safe (d=4,0 untuk Jarwo; d=3,0 untuk Tegel)** — Tidak ada baris rekap dengan densitas persis di titik ini (nilai riil terdekat untuk Jarwo: 4,17 dan 4,55). Skenario 11 dan 12 disusun sebagai nilai buatan agar tepat di titik ambang.
6. **Durasi aktual bebek di sawah (`t_duck`)** — Sama seperti U_bebek, kolom ini juga hasil estimasi kualitatif konstan ("40-45" di seluruh baris), bukan data pengukuran lapangan riil, sehingga tidak relevan untuk membedakan skenario tapi dicatat di sini demi transparansi keterbatasan rekap.

### C.2 Nama kolom rekap bersih yang relevan sebagai pembanding manual (tanpa perhitungan apa pun di dokumen ini)

Gunakan nama kolom berikut pada sheet **"Dataset Actual Bersih"** sebagai acuan pembanding manual Anda per skenario yang bersumber dari baris rekap riil (skenario 2–10, 14, 15a/b sebagian):

- `A_are (Luas Program)`
- `J (Ekor Bebek)`
- `d_are (Ekor/Are)`
- `Sistem Tanam (S)`
- `Actual Yield (kg/are)`
- `Price Gabah (Rp/kg)`
- `Actual Gabah Revenue (Rp)`
- `Buy Price Duck (Rp/ekor)`
- `Feed Cost (Rp)`
- `Weeding Labor Cost (Rp)`
- `Total Labor Cost (Rp)`
- `Chemical Fertilizer Cost (Rp)`
- `Pesticide Cost (Rp)`
- `Total Livestock Investment / C_infra proxy (Rp)`
- `Total Profit — NET (Rp)`
- `Total Operating Profit (Rp, referensi saja)`
- `Density Flag (vs K_max_are lokal)`

Untuk skenario yang bersifat ekstrapolasi murni (11, 12, 13, 16, 17, 18, 19, 20a, 20b), tidak ada baris rekap yang bisa dijadikan pembanding langsung — perbandingan hanya bisa dilakukan terhadap logika rule di file model (mis. nilai `R_age`, `P_over`, `P_under` yang diharapkan secara teoritis), bukan terhadap angka aktual rekap.
