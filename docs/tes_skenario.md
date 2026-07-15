# PANDUAN PENGUJIAN SKENARIO INPUT MANUAL

## DSS Padi-Bebek — Uji Input Manual vs Rekap Bersih (1 Skenario = 1 Baris Rekap)

**Ruang lingkup dokumen ini:** menyusun daftar skenario input uji manual, satu skenario untuk **setiap baris/siklus** yang tercatat pada sheet "Dataset Actual Bersih" file rekap bersih terbaru (v10), tanpa mengecualikan satu baris pun — termasuk baris yang memiliki kolom kosong/bernilai default. Dokumen ini **tidak** menghitung yield/cost/profit prediksi, **tidak** menjalankan model, dan **tidak** menghasilkan metrik akurasi apa pun. Bagian "Output" pada setiap skenario sengaja **dikosongkan** — akan diisi setelah pengujian dijalankan langsung pada backend sistem.

**Sumber yang dirujuk:**

- Model: `Model Matematika Data Collection DSS Padi Bebek FINAL.docx`.
- Rekap: `Dataset Bersih Rekap Include Hasil Simulasi Baru.xlsx`, sheet **"Dataset Actual Bersih"**.
- Nomor baris yang disebut pada kolom "Excel Row (Sumber)" mengacu ke kolom `Excel Row (Sumber)` pada sheet "Dataset Actual Bersih", bukan nomor baris fisik file xlsx.

---

## A. Tabel Daftar Skenario Uji (1:1 dengan Baris Rekap Bersih)

| No  | Excel Row (Sumber) | Batch/Section (Sumber)                             | Nama Petani                    | Subak / Munduk        | Tanggal Tanam (Sumber)   | Catatan Khusus                                                                                 |
| --- | ------------------ | -------------------------------------------------- | ------------------------------ | --------------------- | ------------------------ | ---------------------------------------------------------------------------------------------- |
| 1   | 4                  | Subak Uma Lambing Munduk Lambing Batch 1 (cyle 1)  | I Wayan Suarta                 | Uma Lambing / Lambing | Tidak tersedia           | Sistem Tanam default (tidak tercatat eksplisit)                                                |
| 2   | 5                  | Subak Uma Lambing Munduk Lambing Batch 1 (cyle 1)  | I Made Widana                  | Uma Lambing / Lambing | Tidak tersedia           | Sistem Tanam default (tidak tercatat eksplisit)                                                |
| 3   | 6                  | Subak Uma Lambing Munduk Lambing Batch 1 (cyle 1)  | I Wayan Suwendhi Artha         | Uma Lambing / Lambing | Tidak tersedia           | Sistem Tanam default (tidak tercatat eksplisit)                                                |
| 4   | 7                  | Subak Uma Lambing Munduk Lambing Batch 1 (cyle 1)  | I Ketut Tantra                 | Uma Lambing / Lambing | Tidak tersedia           | Sistem Tanam default (tidak tercatat eksplisit)                                                |
| 5   | 8                  | Subak Uma Lambing Munduk Lambing Batch 1 (cyle 1)  | I Made Arsania                 | Uma Lambing / Lambing | Tidak tersedia           | Sistem Tanam default (tidak tercatat eksplisit)                                                |
| 6   | 9                  | Subak Uma Lambing Munduk Lambing Batch 1 (cyle 1)  | I Nyoman Ranes                 | Uma Lambing / Lambing | Tidak tersedia           | FLAG: Densitas kepadatan per are < 1 ekor/are; Sistem Tanam default (tidak tercatat eksplisit) |
| 7   | 10                 | Subak Uma Lambing Munduk Lambing Batch 1 (cyle 1)  | I Wayan Wiratna                | Uma Lambing / Lambing | Tidak tersedia           | Sistem Tanam default (tidak tercatat eksplisit)                                                |
| 8   | 11                 | Subak Uma Lambing Munduk Lambing Batch 1 (cyle 1)  | I Ketut Alit Sudarsana         | Uma Lambing / Lambing | Tidak tersedia           | Sistem Tanam default (tidak tercatat eksplisit)                                                |
| 9   | 12                 | Subak Uma Lambing Munduk Lambing Batch 1 (cyle 1)  | I Gusti Ngurah Rai Sukarta     | Uma Lambing / Lambing | Tidak tersedia           | Sistem Tanam default (tidak tercatat eksplisit)                                                |
| 10  | 14                 | Subak Uma Lambing Munduk Bias Batch 1 (cyle 1)     | I Wayan Sadia                  | Uma Lambing / Bias    | Tidak tersedia           | Sistem Tanam default (tidak tercatat eksplisit)                                                |
| 11  | 18                 | Subak Uma Lambing Munduk Lambing Batch 1 (cyle 2)  | I Wayan Suarta                 | Uma Lambing / Lambing | Tidak tersedia           | FLAG: Densitas (4.55 ekor/are) > K_max_are acuan lokal (4.0)                                   |
| 12  | 19                 | Subak Uma Lambing Munduk Lambing Batch 1 (cyle 2)  | I Made Widana                  | Uma Lambing / Lambing | Tidak tersedia           | —                                                                                              |
| 13  | 20                 | Subak Uma Lambing Munduk Lambing Batch 1 (cyle 2)  | I Wayan Suwendhi Artha         | Uma Lambing / Lambing | Tidak tersedia           | —                                                                                              |
| 14  | 21                 | Subak Uma Lambing Munduk Lambing Batch 1 (cyle 2)  | I Ketut Tantra                 | Uma Lambing / Lambing | Tidak tersedia           | —                                                                                              |
| 15  | 23                 | Subak Uma Lambing Munduk Lambing Batch 1 (cyle 2)  | I Nyoman Ranes                 | Uma Lambing / Lambing | Tidak tersedia           | —                                                                                              |
| 16  | 24                 | Subak Uma Lambing Munduk Lambing Batch 1 (cyle 2)  | I Wayan Wiratna                | Uma Lambing / Lambing | Tidak tersedia           | FLAG: Densitas kepadatan per are < 1 ekor/are                                                  |
| 17  | 25                 | Subak Uma Lambing Munduk Lambing Batch 1 (cyle 2)  | I Ketut Alit Sudarsana         | Uma Lambing / Lambing | Tidak tersedia           | —                                                                                              |
| 18  | 26                 | Subak Uma Lambing Munduk Lambing Batch 1 (cyle 2)  | I Gusti Ngurah Rai Sukarta     | Uma Lambing / Lambing | Tidak tersedia           | FLAG: Densitas (9.09 ekor/are) > K_max_are acuan lokal (4.0)                                   |
| 19  | 28                 | Subak Uma Lambing Munduk Bias Batch 2 (cycle 1)    | I Gusti Nyoman Ngurah Wirasuta | Uma Lambing / Bias    | 2024-02-19               | —                                                                                              |
| 20  | 34                 | Subak Uma Lambing Munduk Lambing Batch 3 (cycle 1) | I Gusti Ngurah Rai Sukarta     | Uma Lambing / Lambing | 2024-04-15               | —                                                                                              |
| 21  | 36                 | Subak Uma Lambing Munduk Lambing Batch 1 (cycle 3) | I Wayan Suarta                 | Uma Lambing / Lambing | 2024-04-12               | —                                                                                              |
| 22  | 37                 | Subak Uma Lambing Munduk Lambing Batch 1 (cycle 3) | I Wayan Suwendhi Artha         | Uma Lambing / Lambing | 2024-04-23               | —                                                                                              |
| 23  | 38                 | Subak Uma Lambing Munduk Lambing Batch 1 (cycle 3) | I Ketut Alit Sudarsana         | Uma Lambing / Lambing | 2024-04-22               | —                                                                                              |
| 24  | 39                 | Subak Uma Lambing Munduk Lambing Batch 1 (cycle 3) | I Gusti Ngurah Rai Sukarta     | Uma Lambing / Lambing | 2024-04-15               | —                                                                                              |
| 25  | 41                 | Subak Uma Lambing Munduk Bias Batch 2 (cycle 2)    | I Gusti Nyoman Ngurah Wirasuta | Uma Lambing / Bias    | 2024-07-17               | FLAG: Densitas kepadatan per are < 1 ekor/are                                                  |
| 26  | 43                 | SUL Munduk Lambing Batch 1 (cycle 4)               | I Made Arsania                 | Uma Lambing / Lambing | 2024-10-01               | FLAG: Densitas (4.17 ekor/are) > K_max_are acuan lokal (4.0)                                   |
| 27  | 44                 | SUL Munduk Lambing Batch 1 (cycle 4)               | I Ketut Alit Sudarsana         | Uma Lambing / Lambing | 2024-09-28               | —                                                                                              |
| 28  | 46                 | Subak Pedahanan, Munduk Babakan (cycle 2)          | I Wayan Jana                   | Pedahanan / Babakan   | Tidak tersedia           | —                                                                                              |
| 29  | 47                 | Subak Pedahanan, Munduk Babakan (cycle 2)          | I Gusti Ngurah Putu Suka Nada  | Pedahanan / Babakan   | Tidak tersedia           | —                                                                                              |
| 30  | 49                 | Subak Pedahanan, Munduk Babakan (cycle 2)          | I Wayan Arta Susila            | Pedahanan / Babakan   | Tidak tersedia           | —                                                                                              |
| 31  | 51                 | SUL Munduk Lambing Batch 1 (cycle 5)               | I Wayan Suwendhi Artha         | Uma Lambing / Lambing | 2025-04-09               | —                                                                                              |
| 32  | 53                 | SUL Munduk Lambing Batch 2 (cycle 4)               | I Nyoman Suwitra               | Uma Lambing / Lambing | 2025-04-09               | —                                                                                              |
| 33  | 55                 | SUL Munduk Lambing Batch 3 (cycle 3)               | Alm. I Ketut Tantra            | Uma Lambing / Lambing | 2025-04-19               | Farmer Cycle No kosong pada sumber                                                             |
| 34  | 60                 | Subak Ketapang, Munduk Ketapang Batch 1 (cycle 3)  | I Wayan Buana                  | Ketapang / Ketapang   | (panen saja: 2025-07-19) | —                                                                                              |
| 35  | 61                 | Subak Ketapang, Munduk Ketapang Batch 1 (cycle 3)  | I Ketut Buda                   | Ketapang / Ketapang   | (panen saja: 2025-07-20) | —                                                                                              |
| 36  | 62                 | Subak Ketapang, Munduk Ketapang Batch 1 (cycle 3)  | I Made Suardika                | Ketapang / Ketapang   | (panen saja: 2025-07-17) | —                                                                                              |

---

### Skenario 1 — I Wayan Suarta (Uma Lambing, Lambing) — Subak Uma Lambing Munduk Lambing Batch 1 (cyle 1)

**Sumber acuan:** Excel Row (Sumber) = 4 | Group No = 1 | Farmer Cycle No = 1 | Varietas tercatat = "Sertani 13" → `sertani` | Sistem Tanam tercatat = "Null(default Jarwo 2:1)" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam/Panen tercatat = tidak tersedia di sumber

**Input:**

```postman_json
{
    "land_area_are": 6.6,
    "duck_count": 30,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_DENSITY",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-03",
    "N_survive": 20.0,
    "Yield_are_predict": 36.55,
    "Yield_total_predict": 241.2,
    "Revenue_gabah": 1447200.0,
    "Revenue_duck": 700000.0,
    "Total_Revenue": 2147200.0,
    "Cost_duck_buy": 750000.0,
    "Cost_feed": 158931.82,
    "Cost_weeding_isolated": 44831.34,
    "Cost_pesticide_isolated": 5114.92,
    "Cost_infra_isolated": 546561.2,
    "Cost_fertilizer_isolated": 69521.87,
    "Cost_infra_net_isolated": 371561.2,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 10432.01,
    "Cost_fert_phonska_isolated": 59089.86,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 750000.0,
    "Profit_net_cash": 1397200.0,
    "Valuation_weed_eco": 63731.13,
    "Profit_net_full": 1460931.13,
    "F_sys": 1.0
}
```

---

### Skenario 2 — I Made Widana (Uma Lambing, Lambing) — Subak Uma Lambing Munduk Lambing Batch 1 (cyle 1)

**Sumber acuan:** Excel Row (Sumber) = 5 | Group No = 1 | Farmer Cycle No = 1 | Varietas tercatat = "Sertani 13" → `sertani` | Sistem Tanam tercatat = "Null(default Jarwo 2:1)" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam/Panen tercatat = tidak tersedia di sumber

**Input:**

```postman_json
{
    "land_area_are": 10.5,
    "duck_count": 28,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-03",
    "N_survive": 20.0,
    "Yield_are_predict": 37.84,
    "Yield_total_predict": 397.3,
    "Revenue_gabah": 2383800.0,
    "Revenue_duck": 700000.0,
    "Total_Revenue": 3083800.0,
    "Cost_duck_buy": 700000.0,
    "Cost_feed": 135450.0,
    "Cost_weeding_isolated": 119764.24,
    "Cost_pesticide_isolated": 11535.88,
    "Cost_infra_isolated": 643654.76,
    "Cost_fertilizer_isolated": 118281.8,
    "Cost_infra_net_isolated": 468654.76,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 13956.46,
    "Cost_fert_phonska_isolated": 104325.34,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 700000.0,
    "Profit_net_cash": 2383800.0,
    "Valuation_weed_eco": 79987.56,
    "Profit_net_full": 2463787.56,
    "F_sys": 1.0
}
```

---

### Skenario 3 — I Wayan Suwendhi Artha (Uma Lambing, Lambing) — Subak Uma Lambing Munduk Lambing Batch 1 (cyle 1)

**Sumber acuan:** Excel Row (Sumber) = 6 | Group No = 1 | Farmer Cycle No = 1 | Varietas tercatat = "Sertani 13" → `sertani` | Sistem Tanam tercatat = "Null(default Jarwo 2:1)" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam/Panen tercatat = tidak tersedia di sumber

**Input:**

```postman_json
{
    "land_area_are": 4.8,
    "duck_count": 10,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-03",
    "N_survive": 7.0,
    "Yield_are_predict": 37.84,
    "Yield_total_predict": 181.6,
    "Revenue_gabah": 1089600.0,
    "Revenue_duck": 245000.0,
    "Total_Revenue": 1334600.0,
    "Cost_duck_buy": 250000.0,
    "Cost_feed": 48375.0,
    "Cost_weeding_isolated": 65157.96,
    "Cost_pesticide_isolated": 6003.78,
    "Cost_infra_isolated": 491868.45,
    "Cost_fertilizer_isolated": 55351.6,
    "Cost_infra_net_isolated": 316868.45,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 5940.07,
    "Cost_fert_phonska_isolated": 49411.53,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 250000.0,
    "Profit_net_cash": 1084600.0,
    "Valuation_weed_eco": 31198.03,
    "Profit_net_full": 1115798.03,
    "F_sys": 1.0
}
```

---

### Skenario 4 — I Ketut Tantra (Uma Lambing, Lambing) — Subak Uma Lambing Munduk Lambing Batch 1 (cyle 1)

**Sumber acuan:** Excel Row (Sumber) = 7 | Group No = 1 | Farmer Cycle No = 1 | Varietas tercatat = "Sertani 13" → `sertani` | Sistem Tanam tercatat = "Null(default Jarwo 2:1)" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam/Panen tercatat = tidak tersedia di sumber

**Input:**

```postman_json
{
    "land_area_are": 4.5,
    "duck_count": 16,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-03",
    "N_survive": 11.0,
    "Yield_are_predict": 37.84,
    "Yield_total_predict": 170.3,
    "Revenue_gabah": 1021800.0,
    "Revenue_duck": 385000.0,
    "Total_Revenue": 1406800.0,
    "Cost_duck_buy": 400000.0,
    "Cost_feed": 77400.0,
    "Cost_weeding_isolated": 39808.95,
    "Cost_pesticide_isolated": 4135.84,
    "Cost_infra_isolated": 481806.56,
    "Cost_fertilizer_isolated": 48863.75,
    "Cost_infra_net_isolated": 306806.56,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 6609.95,
    "Cost_fert_phonska_isolated": 42253.8,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 400000.0,
    "Profit_net_cash": 1006800.0,
    "Valuation_weed_eco": 40220.52,
    "Profit_net_full": 1047020.52,
    "F_sys": 1.0
}
```

---

### Skenario 5 — I Made Arsania (Uma Lambing, Lambing) — Subak Uma Lambing Munduk Lambing Batch 1 (cyle 1)

**Sumber acuan:** Excel Row (Sumber) = 8 | Group No = 1 | Farmer Cycle No = 1 | Varietas tercatat = "Sertani 13" → `sertani` | Sistem Tanam tercatat = "Null(default Jarwo 2:1)" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam/Panen tercatat = tidak tersedia di sumber

**Input:**

```postman_json
{
    "land_area_are": 3.6,
    "duck_count": 13,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-03",
    "N_survive": 9.0,
    "Yield_are_predict": 37.84,
    "Yield_total_predict": 136.2,
    "Revenue_gabah": 817200.0,
    "Revenue_duck": 315000.0,
    "Total_Revenue": 1132200.0,
    "Cost_duck_buy": 325000.0,
    "Cost_feed": 62887.5,
    "Cost_weeding_isolated": 31360.92,
    "Cost_pesticide_isolated": 3274.56,
    "Cost_infra_isolated": 449416.13,
    "Cost_fertilizer_isolated": 38999.58,
    "Cost_infra_net_isolated": 274416.13,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 5319.39,
    "Cost_fert_phonska_isolated": 33680.19,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 325000.0,
    "Profit_net_cash": 807200.0,
    "Valuation_weed_eco": 32427.17,
    "Profit_net_full": 839627.17,
    "F_sys": 1.0
}
```

---

### Skenario 6 — I Nyoman Ranes (Uma Lambing, Lambing) — Subak Uma Lambing Munduk Lambing Batch 1 (cyle 1)

**Sumber acuan:** Excel Row (Sumber) = 9 | Group No = 1 | Farmer Cycle No = 1 | Varietas tercatat = "Sertani 13" → `sertani` | Sistem Tanam tercatat = "Null(default Jarwo 2:1)" → `jajar_legowo` | Density Flag = FLAG: Densitas kepadatan per are < 1 ekor/are | Tanggal Tanam/Panen tercatat = tidak tersedia di sumber

**Input:**

```postman_json
{
    "land_area_are": 5.1,
    "duck_count": 5,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_UNDER_DENSITY",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-03",
    "N_survive": 3.0,
    "Yield_are_predict": 35.52,
    "Yield_total_predict": 181.2,
    "Revenue_gabah": 1087200.0,
    "Revenue_duck": 105000.0,
    "Total_Revenue": 1192200.0,
    "Cost_duck_buy": 125000.0,
    "Cost_feed": 24187.5,
    "Cost_weeding_isolated": 97443.73,
    "Cost_pesticide_isolated": 8358.37,
    "Cost_infra_isolated": 501620.53,
    "Cost_fertilizer_isolated": 61382.33,
    "Cost_infra_net_isolated": 326620.53,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 5427.35,
    "Cost_fert_phonska_isolated": 55954.98,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 125000.0,
    "Profit_net_cash": 1067200.0,
    "Valuation_weed_eco": 18598.25,
    "Profit_net_full": 1085798.25,
    "F_sys": 1.0
}
```

---

### Skenario 7 — I Wayan Wiratna (Uma Lambing, Lambing) — Subak Uma Lambing Munduk Lambing Batch 1 (cyle 1)

**Sumber acuan:** Excel Row (Sumber) = 10 | Group No = 1 | Farmer Cycle No = 1 | Varietas tercatat = "Sertani 13" → `sertani` | Sistem Tanam tercatat = "Null(default Jarwo 2:1)" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam/Panen tercatat = tidak tersedia di sumber

**Input:**

```postman_json
{
    "land_area_are": 3.2,
    "duck_count": 10,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-03",
    "N_survive": 7.0,
    "Yield_are_predict": 37.84,
    "Yield_total_predict": 121.1,
    "Revenue_gabah": 726600.0,
    "Revenue_duck": 245000.0,
    "Total_Revenue": 971600.0,
    "Cost_duck_buy": 250000.0,
    "Cost_feed": 48375.0,
    "Cost_weeding_isolated": 31959.02,
    "Cost_pesticide_isolated": 3197.15,
    "Cost_infra_isolated": 433722.01,
    "Cost_fertilizer_isolated": 35377.36,
    "Cost_infra_net_isolated": 258722.01,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 4483.89,
    "Cost_fert_phonska_isolated": 30893.47,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 250000.0,
    "Profit_net_cash": 721600.0,
    "Valuation_weed_eco": 26718.73,
    "Profit_net_full": 748318.73,
    "F_sys": 1.0
}
```

---

### Skenario 8 — I Ketut Alit Sudarsana (Uma Lambing, Lambing) — Subak Uma Lambing Munduk Lambing Batch 1 (cyle 1)

**Sumber acuan:** Excel Row (Sumber) = 11 | Group No = 1 | Farmer Cycle No = 1 | Varietas tercatat = "Sertani 13" → `sertani` | Sistem Tanam tercatat = "Null(default Jarwo 2:1)" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam/Panen tercatat = tidak tersedia di sumber

**Input:**

```postman_json
{
    "land_area_are": 10,
    "duck_count": 65,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_DENSITY",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-03",
    "N_survive": 33.0,
    "Yield_are_predict": 31.92,
    "Yield_total_predict": 319.2,
    "Revenue_gabah": 1915200.0,
    "Revenue_duck": 1155000.0,
    "Total_Revenue": 3070200.0,
    "Cost_duck_buy": 1625000.0,
    "Cost_feed": 451546.88,
    "Cost_weeding_isolated": 43351.06,
    "Cost_pesticide_isolated": 6025.77,
    "Cost_infra_isolated": 632360.22,
    "Cost_fertilizer_isolated": 103483.28,
    "Cost_infra_net_isolated": 457360.22,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 16443.09,
    "Cost_fert_phonska_isolated": 87040.19,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 1625000.0,
    "Profit_net_cash": 1445200.0,
    "Valuation_weed_eco": 95043.25,
    "Profit_net_full": 1540243.25,
    "F_sys": 1.0
}
```

---

### Skenario 9 — I Gusti Ngurah Rai Sukarta (Uma Lambing, Lambing) — Subak Uma Lambing Munduk Lambing Batch 1 (cyle 1)

**Sumber acuan:** Excel Row (Sumber) = 12 | Group No = 1 | Farmer Cycle No = 1 | Varietas tercatat = "Sertani 13" → `sertani` | Sistem Tanam tercatat = "Null(default Jarwo 2:1)" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam/Panen tercatat = tidak tersedia di sumber

**Input:**

```postman_json
{
    "land_area_are": 5.5,
    "duck_count": 40,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_DENSITY",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-03",
    "N_survive": 18.0,
    "Yield_are_predict": 30.1,
    "Yield_total_predict": 165.6,
    "Revenue_gabah": 993600.0,
    "Revenue_duck": 630000.0,
    "Total_Revenue": 1623600.0,
    "Cost_duck_buy": 1000000.0,
    "Cost_feed": 303954.55,
    "Cost_weeding_isolated": 20581.33,
    "Cost_pesticide_isolated": 3085.34,
    "Cost_infra_isolated": 514187.42,
    "Cost_fertilizer_isolated": 57108.97,
    "Cost_infra_net_isolated": 339187.42,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 8977.29,
    "Cost_fert_phonska_isolated": 48131.68,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 1000000.0,
    "Profit_net_cash": 623600.0,
    "Valuation_weed_eco": 50619.71,
    "Profit_net_full": 674219.71,
    "F_sys": 1.0
}
```

---

### Skenario 10 — I Wayan Sadia (Uma Lambing, Bias) — Subak Uma Lambing Munduk Bias Batch 1 (cyle 1)

**Sumber acuan:** Excel Row (Sumber) = 14 | Group No = 2 | Farmer Cycle No = 1 | Varietas tercatat = "Sertani" → `sertani` | Sistem Tanam tercatat = "Null(default Jarwo 2:1)" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam/Panen tercatat = tidak tersedia di sumber

**Input:**

```postman_json
{
    "land_area_are": 7.26,
    "duck_count": 9,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_UNDER_DENSITY",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-03",
    "N_survive": 6.0,
    "Yield_are_predict": 36.11,
    "Yield_total_predict": 262.2,
    "Revenue_gabah": 1573200.0,
    "Revenue_duck": 210000.0,
    "Total_Revenue": 1783200.0,
    "Cost_duck_buy": 225000.0,
    "Cost_feed": 43537.5,
    "Cost_weeding_isolated": 127834.51,
    "Cost_pesticide_isolated": 11135.11,
    "Cost_infra_isolated": 564696.67,
    "Cost_fertilizer_isolated": 86519.1,
    "Cost_infra_net_isolated": 389696.67,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 8021.8,
    "Cost_fert_phonska_isolated": 78497.3,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 225000.0,
    "Profit_net_cash": 1558200.0,
    "Valuation_weed_eco": 32085.72,
    "Profit_net_full": 1590285.72,
    "F_sys": 1.0
}
```

---

### Skenario 11 — I Wayan Suarta (Uma Lambing, Lambing) — Subak Uma Lambing Munduk Lambing Batch 1 (cyle 2)

**Sumber acuan:** Excel Row (Sumber) = 18 | Group No = 4 | Farmer Cycle No = 2 | Varietas tercatat = "Sertani" → `sertani` | Sistem Tanam tercatat = "Jarwo 2:1" → `jajar_legowo` | Density Flag = FLAG: Densitas (4.55 ekor/are) > K_max_are acuan lokal (4.0) | Tanggal Tanam/Panen tercatat = tidak tersedia di sumber

**Input:**

```postman_json
{
    "land_area_are": 6.6,
    "duck_count": 30,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_DENSITY",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-03",
    "N_survive": 20.0,
    "Yield_are_predict": 36.55,
    "Yield_total_predict": 241.2,
    "Revenue_gabah": 1447200.0,
    "Revenue_duck": 700000.0,
    "Total_Revenue": 2147200.0,
    "Cost_duck_buy": 750000.0,
    "Cost_feed": 158931.82,
    "Cost_weeding_isolated": 44831.34,
    "Cost_pesticide_isolated": 5114.92,
    "Cost_infra_isolated": 546561.2,
    "Cost_fertilizer_isolated": 69521.87,
    "Cost_infra_net_isolated": 371561.2,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 10432.01,
    "Cost_fert_phonska_isolated": 59089.86,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 750000.0,
    "Profit_net_cash": 1397200.0,
    "Valuation_weed_eco": 63731.13,
    "Profit_net_full": 1460931.13,
    "F_sys": 1.0
}
```

---

### Skenario 12 — I Made Widana (Uma Lambing, Lambing) — Subak Uma Lambing Munduk Lambing Batch 1 (cyle 2)

**Sumber acuan:** Excel Row (Sumber) = 19 | Group No = 4 | Farmer Cycle No = 2 | Varietas tercatat = "Sertani" → `sertani` | Sistem Tanam tercatat = "Jarwo 2:1" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam/Panen tercatat = tidak tersedia di sumber

**Input:**

```postman_json
{
    "land_area_are": 10.5,
    "duck_count": 28,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-03",
    "N_survive": 20.0,
    "Yield_are_predict": 37.84,
    "Yield_total_predict": 397.3,
    "Revenue_gabah": 2383800.0,
    "Revenue_duck": 700000.0,
    "Total_Revenue": 3083800.0,
    "Cost_duck_buy": 700000.0,
    "Cost_feed": 135450.0,
    "Cost_weeding_isolated": 119764.24,
    "Cost_pesticide_isolated": 11535.88,
    "Cost_infra_isolated": 643654.76,
    "Cost_fertilizer_isolated": 118281.8,
    "Cost_infra_net_isolated": 468654.76,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 13956.46,
    "Cost_fert_phonska_isolated": 104325.34,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 700000.0,
    "Profit_net_cash": 2383800.0,
    "Valuation_weed_eco": 79987.56,
    "Profit_net_full": 2463787.56,
    "F_sys": 1.0
}
```

---

### Skenario 13 — I Wayan Suwendhi Artha (Uma Lambing, Lambing) — Subak Uma Lambing Munduk Lambing Batch 1 (cyle 2)

**Sumber acuan:** Excel Row (Sumber) = 20 | Group No = 4 | Farmer Cycle No = 2 | Varietas tercatat = "Sertani" → `sertani` | Sistem Tanam tercatat = "Jarwo 2:1" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam/Panen tercatat = tidak tersedia di sumber

**Input:**

```postman_json
{
    "land_area_are": 4.8,
    "duck_count": 8,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_UNDER_DENSITY",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-03",
    "N_survive": 5.0,
    "Yield_are_predict": 37.08,
    "Yield_total_predict": 178.0,
    "Revenue_gabah": 1068000.0,
    "Revenue_duck": 175000.0,
    "Total_Revenue": 1243000.0,
    "Cost_duck_buy": 200000.0,
    "Cost_feed": 38700.0,
    "Cost_weeding_isolated": 74007.01,
    "Cost_pesticide_isolated": 6624.6,
    "Cost_infra_isolated": 491868.45,
    "Cost_fertilizer_isolated": 56265.82,
    "Cost_infra_net_isolated": 316868.45,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 5625.77,
    "Cost_fert_phonska_isolated": 50640.05,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 200000.0,
    "Profit_net_cash": 1043000.0,
    "Valuation_weed_eco": 26634.57,
    "Profit_net_full": 1069634.57,
    "F_sys": 1.0
}
```

---

### Skenario 14 — I Ketut Tantra (Uma Lambing, Lambing) — Subak Uma Lambing Munduk Lambing Batch 1 (cyle 2)

**Sumber acuan:** Excel Row (Sumber) = 21 | Group No = 4 | Farmer Cycle No = 2 | Varietas tercatat = "Inpari" → `inpari` | Sistem Tanam tercatat = "Jarwo 2:1" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam/Panen tercatat = tidak tersedia di sumber

**Input:**

```postman_json
{
    "land_area_are": 4.5,
    "duck_count": 10,
    "rice_variety": "inpari",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-23",
    "N_survive": 7.0,
    "Yield_are_predict": 37.84,
    "Yield_total_predict": 170.3,
    "Revenue_gabah": 1021800.0,
    "Revenue_duck": 245000.0,
    "Total_Revenue": 1266800.0,
    "Cost_duck_buy": 250000.0,
    "Cost_feed": 48375.0,
    "Cost_weeding_isolated": 58578.43,
    "Cost_pesticide_isolated": 5452.65,
    "Cost_infra_isolated": 481806.56,
    "Cost_fertilizer_isolated": 51606.43,
    "Cost_infra_net_isolated": 306806.56,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 5667.04,
    "Cost_fert_phonska_isolated": 45939.39,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 250000.0,
    "Profit_net_cash": 1016800.0,
    "Valuation_weed_eco": 30541.09,
    "Profit_net_full": 1047341.09,
    "F_sys": 1.0
}
```

---

### Skenario 15 — I Nyoman Ranes (Uma Lambing, Lambing) — Subak Uma Lambing Munduk Lambing Batch 1 (cyle 2)

**Sumber acuan:** Excel Row (Sumber) = 23 | Group No = 4 | Farmer Cycle No = 2 | Varietas tercatat = "Inpari " → `inpari` | Sistem Tanam tercatat = "Jarwo 2:1" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam/Panen tercatat = tidak tersedia di sumber

**Input:**

```postman_json
{
    "land_area_are": 5.1,
    "duck_count": 10,
    "rice_variety": "inpari",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_UNDER_DENSITY",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-23",
    "N_survive": 7.0,
    "Yield_are_predict": 37.75,
    "Yield_total_predict": 192.5,
    "Revenue_gabah": 1155000.0,
    "Revenue_duck": 245000.0,
    "Total_Revenue": 1400000.0,
    "Cost_duck_buy": 250000.0,
    "Cost_feed": 48375.0,
    "Cost_weeding_isolated": 71854.81,
    "Cost_pesticide_isolated": 6563.14,
    "Cost_infra_isolated": 501620.53,
    "Cost_fertilizer_isolated": 59096.77,
    "Cost_infra_net_isolated": 326620.53,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 6213.1,
    "Cost_fert_phonska_isolated": 52883.66,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 250000.0,
    "Profit_net_cash": 1150000.0,
    "Valuation_weed_eco": 31794.46,
    "Profit_net_full": 1181794.46,
    "F_sys": 1.0
}
```

---

### Skenario 16 — I Wayan Wiratna (Uma Lambing, Lambing) — Subak Uma Lambing Munduk Lambing Batch 1 (cyle 2)

**Sumber acuan:** Excel Row (Sumber) = 24 | Group No = 4 | Farmer Cycle No = 2 | Varietas tercatat = "Sertani" → `sertani` | Sistem Tanam tercatat = "Jarwo 2:1" → `jajar_legowo` | Density Flag = FLAG: Densitas kepadatan per are < 1 ekor/are | Tanggal Tanam/Panen tercatat = tidak tersedia di sumber

**Input:**

```postman_json
{
    "land_area_are": 3.2,
    "duck_count": 3,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_UNDER_DENSITY",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-03",
    "N_survive": 2.0,
    "Yield_are_predict": 35.42,
    "Yield_total_predict": 113.3,
    "Revenue_gabah": 679800.0,
    "Revenue_duck": 70000.0,
    "Total_Revenue": 749800.0,
    "Cost_duck_buy": 75000.0,
    "Cost_feed": 14512.5,
    "Cost_weeding_isolated": 61977.26,
    "Cost_pesticide_isolated": 5303.12,
    "Cost_infra_isolated": 433722.01,
    "Cost_fertilizer_isolated": 38577.14,
    "Cost_infra_net_isolated": 258722.01,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 3383.82,
    "Cost_fert_phonska_isolated": 35193.32,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 75000.0,
    "Profit_net_cash": 674800.0,
    "Valuation_weed_eco": 11238.31,
    "Profit_net_full": 686038.31,
    "F_sys": 1.0
}
```

---

### Skenario 17 — I Ketut Alit Sudarsana (Uma Lambing, Lambing) — Subak Uma Lambing Munduk Lambing Batch 1 (cyle 2)

**Sumber acuan:** Excel Row (Sumber) = 25 | Group No = 4 | Farmer Cycle No = 2 | Varietas tercatat = "Sertani" → `sertani` | Sistem Tanam tercatat = "Jarwo 2:1" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam/Panen tercatat = tidak tersedia di sumber

**Input:**

```postman_json
{
    "land_area_are": 14.41,
    "duck_count": 30,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-03",
    "N_survive": 21.0,
    "Yield_are_predict": 37.84,
    "Yield_total_predict": 545.3,
    "Revenue_gabah": 3271800.0,
    "Revenue_duck": 735000.0,
    "Total_Revenue": 4006800.0,
    "Cost_duck_buy": 750000.0,
    "Cost_feed": 145125.0,
    "Cost_weeding_isolated": 195695.28,
    "Cost_pesticide_isolated": 18029.85,
    "Cost_infra_isolated": 724022.8,
    "Cost_fertilizer_isolated": 166179.63,
    "Cost_infra_net_isolated": 549022.8,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 17829.31,
    "Cost_fert_phonska_isolated": 148350.32,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 750000.0,
    "Profit_net_cash": 3256800.0,
    "Valuation_weed_eco": 93614.91,
    "Profit_net_full": 3350414.91,
    "F_sys": 1.0
}
```

---

### Skenario 18 — I Gusti Ngurah Rai Sukarta (Uma Lambing, Lambing) — Subak Uma Lambing Munduk Lambing Batch 1 (cyle 2)

**Sumber acuan:** Excel Row (Sumber) = 26 | Group No = 4 | Farmer Cycle No = 2 | Varietas tercatat = "Sertani" → `sertani` | Sistem Tanam tercatat = "Jarwo 2:1" → `jajar_legowo` | Density Flag = FLAG: Densitas (9.09 ekor/are) > K_max_are acuan lokal (4.0) | Tanggal Tanam/Panen tercatat = tidak tersedia di sumber

**Input:**

```postman_json
{
    "land_area_are": 5.5,
    "duck_count": 50,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_DENSITY",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-03",
    "N_survive": 19.0,
    "Yield_are_predict": 28.38,
    "Yield_total_predict": 156.1,
    "Revenue_gabah": 936600.0,
    "Revenue_duck": 665000.0,
    "Total_Revenue": 1601600.0,
    "Cost_duck_buy": 1250000.0,
    "Cost_feed": 410625.0,
    "Cost_weeding_isolated": 15636.75,
    "Cost_pesticide_isolated": 2738.45,
    "Cost_infra_isolated": 514187.42,
    "Cost_fertilizer_isolated": 56090.86,
    "Cost_infra_net_isolated": 339187.42,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 9327.31,
    "Cost_fert_phonska_isolated": 46763.55,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 1250000.0,
    "Profit_net_cash": 351600.0,
    "Valuation_weed_eco": 49639.59,
    "Profit_net_full": 401239.59,
    "F_sys": 1.0
}
```

---

### Skenario 19 — I Gusti Nyoman Ngurah Wirasuta (Uma Lambing, Bias) — Subak Uma Lambing Munduk Bias Batch 2 (cycle 1)

**Sumber acuan:** Excel Row (Sumber) = 28 | Group No = 6 | Farmer Cycle No = 1 | Varietas tercatat = "Sertani" → `sertani` | Sistem Tanam tercatat = "Jarwo 2:1" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam tercatat = 2024-02-19 | Tanggal Panen tercatat = 2024-05-22

**Input:**

```postman_json
{
    "land_area_are": 6.35,
    "duck_count": 20,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2024-02-19",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2024-03-11",
    "D_tarik_bebek": "2024-04-24",
    "D_panen_gabah": "2024-06-12",
    "N_survive": 14.0,
    "Yield_are_predict": 37.84,
    "Yield_total_predict": 240.3,
    "Revenue_gabah": 1441800.0,
    "Revenue_duck": 490000.0,
    "Total_Revenue": 1931800.0,
    "Cost_duck_buy": 500000.0,
    "Cost_feed": 96750.0,
    "Cost_weeding_isolated": 62974.64,
    "Cost_pesticide_isolated": 6313.19,
    "Cost_infra_isolated": 539456.12,
    "Cost_fertilizer_isolated": 70130.52,
    "Cost_infra_net_isolated": 364456.12,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 8922.27,
    "Cost_fert_phonska_isolated": 61208.25,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 500000.0,
    "Profit_net_cash": 1431800.0,
    "Valuation_weed_eco": 53248.97,
    "Profit_net_full": 1485048.97,
    "F_sys": 1.0
}
```

---

### Skenario 20 — I Gusti Ngurah Rai Sukarta (Uma Lambing, Lambing) — Subak Uma Lambing Munduk Lambing Batch 3 (cycle 1)

**Sumber acuan:** Excel Row (Sumber) = 34 | Group No = 9 | Farmer Cycle No = 1 | Varietas tercatat = "Sertani" → `sertani` | Sistem Tanam tercatat = "Jarwo 2:1" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam tercatat = 2024-04-15 | Tanggal Panen tercatat = 2024-07-19

**Input:**

```postman_json
{
    "land_area_are": 10.21,
    "duck_count": 32,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2024-04-15",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2024-05-06",
    "D_tarik_bebek": "2024-06-19",
    "D_panen_gabah": "2024-08-07",
    "N_survive": 23.0,
    "Yield_are_predict": 37.84,
    "Yield_total_predict": 386.3,
    "Revenue_gabah": 2317800.0,
    "Revenue_duck": 805000.0,
    "Total_Revenue": 3122800.0,
    "Cost_duck_buy": 800000.0,
    "Cost_feed": 154800.0,
    "Cost_weeding_isolated": 101702.11,
    "Cost_pesticide_isolated": 10182.15,
    "Cost_infra_isolated": 637137.55,
    "Cost_fertilizer_isolated": 112833.02,
    "Cost_infra_net_isolated": 462137.55,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 14321.13,
    "Cost_fert_phonska_isolated": 98511.89,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 800000.0,
    "Profit_net_cash": 2322800.0,
    "Valuation_weed_eco": 85387.2,
    "Profit_net_full": 2408187.2,
    "F_sys": 1.0
}
```

---

### Skenario 21 — I Wayan Suarta (Uma Lambing, Lambing) — Subak Uma Lambing Munduk Lambing Batch 1 (cycle 3)

**Sumber acuan:** Excel Row (Sumber) = 36 | Group No = 10 | Farmer Cycle No = 3 | Varietas tercatat = "Inpari" → `inpari` | Sistem Tanam tercatat = "Tegel" → `tegel` | Density Flag = (tidak ada flag) | Tanggal Tanam tercatat = 2024-04-12 | Tanggal Panen tercatat = 2024-08-06

**Input:**

```postman_json
{
    "land_area_are": 6.6,
    "duck_count": 19,
    "rice_variety": "inpari",
    "planting_system": "tegel",
    "planting_date": "2024-04-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2024-05-03",
    "D_tarik_bebek": "2024-06-16",
    "D_panen_gabah": "2024-08-24",
    "N_survive": 13.0,
    "Yield_are_predict": 45.82,
    "Yield_total_predict": 302.4,
    "Revenue_gabah": 1814400.0,
    "Revenue_duck": 455000.0,
    "Total_Revenue": 2269400.0,
    "Cost_duck_buy": 475000.0,
    "Cost_feed": 91912.5,
    "Cost_weeding_isolated": 70759.19,
    "Cost_pesticide_isolated": 6933.93,
    "Cost_infra_isolated": 546561.2,
    "Cost_fertilizer_isolated": 73708.6,
    "Cost_infra_net_isolated": 371561.2,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 8992.64,
    "Cost_fert_phonska_isolated": 64715.96,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 475000.0,
    "Profit_net_cash": 1794400.0,
    "Valuation_weed_eco": 52609.47,
    "Profit_net_full": 1847009.47,
    "F_sys": 1.211
}
```

---

### Skenario 22 — I Wayan Suwendhi Artha (Uma Lambing, Lambing) — Subak Uma Lambing Munduk Lambing Batch 1 (cycle 3)

**Sumber acuan:** Excel Row (Sumber) = 37 | Group No = 10 | Farmer Cycle No = 3 | Varietas tercatat = "Sertani a 13" → `sertani` | Sistem Tanam tercatat = "Tegel" → `tegel` | Density Flag = (tidak ada flag) | Tanggal Tanam tercatat = 2024-04-23 | Tanggal Panen tercatat = 2024-07-31

**Input:**

```postman_json
{
    "land_area_are": 4.8,
    "duck_count": 9,
    "rice_variety": "sertani",
    "planting_system": "tegel",
    "planting_date": "2024-04-23",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_UNDER_DENSITY",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2024-05-14",
    "D_tarik_bebek": "2024-06-27",
    "D_panen_gabah": "2024-08-15",
    "N_survive": 6.0,
    "Yield_are_predict": 45.48,
    "Yield_total_predict": 218.3,
    "Revenue_gabah": 1309800.0,
    "Revenue_duck": 210000.0,
    "Total_Revenue": 1519800.0,
    "Cost_duck_buy": 225000.0,
    "Cost_feed": 43537.5,
    "Cost_weeding_isolated": 69421.25,
    "Cost_pesticide_isolated": 6302.87,
    "Cost_infra_isolated": 491868.45,
    "Cost_fertilizer_isolated": 55808.71,
    "Cost_infra_net_isolated": 316868.45,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 5782.92,
    "Cost_fert_phonska_isolated": 50025.79,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 225000.0,
    "Profit_net_cash": 1294800.0,
    "Valuation_weed_eco": 28999.45,
    "Profit_net_full": 1323799.45,
    "F_sys": 1.211
}
```

---

### Skenario 23 — I Ketut Alit Sudarsana (Uma Lambing, Lambing) — Subak Uma Lambing Munduk Lambing Batch 1 (cycle 3)

**Sumber acuan:** Excel Row (Sumber) = 38 | Group No = 10 | Farmer Cycle No = 3 | Varietas tercatat = "Sertani" → `sertani` | Sistem Tanam tercatat = "Jarwo 2:1" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam tercatat = 2024-04-22 | Tanggal Panen tercatat = 2024-07-31

**Input:**

```postman_json
{
    "land_area_are": 10,
    "duck_count": 32,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2024-04-22",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2024-05-13",
    "D_tarik_bebek": "2024-06-26",
    "D_panen_gabah": "2024-08-14",
    "N_survive": 23.0,
    "Yield_are_predict": 37.84,
    "Yield_total_predict": 378.4,
    "Revenue_gabah": 2270400.0,
    "Revenue_duck": 805000.0,
    "Total_Revenue": 3075400.0,
    "Cost_duck_buy": 800000.0,
    "Cost_feed": 154800.0,
    "Cost_weeding_isolated": 97759.18,
    "Cost_pesticide_isolated": 9842.86,
    "Cost_infra_isolated": 632360.22,
    "Cost_fertilizer_isolated": 110211.4,
    "Cost_infra_net_isolated": 457360.22,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 14130.01,
    "Cost_fert_phonska_isolated": 96081.39,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 800000.0,
    "Profit_net_cash": 2275400.0,
    "Valuation_weed_eco": 84585.57,
    "Profit_net_full": 2359985.57,
    "F_sys": 1.0
}
```

---

### Skenario 24 — I Gusti Ngurah Rai Sukarta (Uma Lambing, Lambing) — Subak Uma Lambing Munduk Lambing Batch 1 (cycle 3)

**Sumber acuan:** Excel Row (Sumber) = 39 | Group No = 10 | Farmer Cycle No = 3 | Varietas tercatat = "Sertani" → `sertani` | Sistem Tanam tercatat = "Jarwo 2:1" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam tercatat = 2024-04-15 | Tanggal Panen tercatat = 2024-07-19

**Input:**

```postman_json
{
    "land_area_are": 5.5,
    "duck_count": 18,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2024-04-15",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2024-05-06",
    "D_tarik_bebek": "2024-06-19",
    "D_panen_gabah": "2024-08-07",
    "N_survive": 13.0,
    "Yield_are_predict": 37.84,
    "Yield_total_predict": 208.1,
    "Revenue_gabah": 1248600.0,
    "Revenue_duck": 455000.0,
    "Total_Revenue": 1703600.0,
    "Cost_duck_buy": 450000.0,
    "Cost_feed": 87075.0,
    "Cost_weeding_isolated": 52669.5,
    "Cost_pesticide_isolated": 5336.54,
    "Cost_infra_isolated": 514187.42,
    "Cost_fertilizer_isolated": 60433.43,
    "Cost_infra_net_isolated": 339187.42,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 7834.37,
    "Cost_fert_phonska_isolated": 52599.06,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 450000.0,
    "Profit_net_cash": 1253600.0,
    "Valuation_weed_eco": 47088.33,
    "Profit_net_full": 1300688.33,
    "F_sys": 1.0
}
```

---

### Skenario 25 — I Gusti Nyoman Ngurah Wirasuta (Uma Lambing, Bias) — Subak Uma Lambing Munduk Bias Batch 2 (cycle 2)

**Sumber acuan:** Excel Row (Sumber) = 41 | Group No = 16 | Farmer Cycle No = 2 | Varietas tercatat = "Inpari 32" → `inpari` | Sistem Tanam tercatat = "Tegel" → `tegel` | Density Flag = FLAG: Densitas kepadatan per are < 1 ekor/are | Tanggal Tanam tercatat = 2024-07-17 | Tanggal Panen tercatat = 2024-11-03

**Input:**

```postman_json
{
    "land_area_are": 6.35,
    "duck_count": 5,
    "rice_variety": "inpari",
    "planting_system": "tegel",
    "planting_date": "2024-07-17",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_UNDER_DENSITY",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2024-08-07",
    "D_tarik_bebek": "2024-09-20",
    "D_panen_gabah": "2024-11-28",
    "N_survive": 3.0,
    "Yield_are_predict": 42.49,
    "Yield_total_predict": 269.8,
    "Revenue_gabah": 1618800.0,
    "Revenue_duck": 105000.0,
    "Total_Revenue": 1723800.0,
    "Cost_duck_buy": 125000.0,
    "Cost_feed": 24187.5,
    "Cost_weeding_isolated": 128992.22,
    "Cost_pesticide_isolated": 10944.75,
    "Cost_infra_isolated": 539456.12,
    "Cost_fertilizer_isolated": 76987.2,
    "Cost_infra_net_isolated": 364456.12,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 6564.99,
    "Cost_fert_phonska_isolated": 70422.22,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 125000.0,
    "Profit_net_cash": 1598800.0,
    "Valuation_weed_eco": 19203.68,
    "Profit_net_full": 1618003.68,
    "F_sys": 1.211
}
```

---

### Skenario 26 — I Made Arsania (Uma Lambing, Lambing) — SUL Munduk Lambing Batch 1 (cycle 4)

**Sumber acuan:** Excel Row (Sumber) = 43 | Group No = 19 | Farmer Cycle No = 4 | Varietas tercatat = "Sertani" → `sertani` | Sistem Tanam tercatat = "Jarwo 2:1" → `jajar_legowo` | Density Flag = FLAG: Densitas (4.17 ekor/are) > K_max_are acuan lokal (4.0) | Tanggal Tanam tercatat = 2024-10-01 | Tanggal Panen tercatat = 2025-01-17

**Input:**

```postman_json
{
    "land_area_are": 3.6,
    "duck_count": 15,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2024-10-01",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_DENSITY",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2024-10-22",
    "D_tarik_bebek": "2024-12-05",
    "D_panen_gabah": "2025-01-23",
    "N_survive": 10.0,
    "Yield_are_predict": 37.44,
    "Yield_total_predict": 134.8,
    "Revenue_gabah": 808800.0,
    "Revenue_duck": 350000.0,
    "Total_Revenue": 1158800.0,
    "Cost_duck_buy": 375000.0,
    "Cost_feed": 74671.88,
    "Cost_weeding_isolated": 26984.91,
    "Cost_pesticide_isolated": 2967.56,
    "Cost_infra_isolated": 449416.13,
    "Cost_fertilizer_isolated": 38213.92,
    "Cost_infra_net_isolated": 274416.13,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 5589.49,
    "Cost_fert_phonska_isolated": 32624.42,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 375000.0,
    "Profit_net_cash": 783800.0,
    "Valuation_weed_eco": 34322.59,
    "Profit_net_full": 818122.59,
    "F_sys": 1.0
}
```

---

### Skenario 27 — I Ketut Alit Sudarsana (Uma Lambing, Lambing) — SUL Munduk Lambing Batch 1 (cycle 4)

**Sumber acuan:** Excel Row (Sumber) = 44 | Group No = 19 | Farmer Cycle No = 4 | Varietas tercatat = "Inpari" → `inpari` | Sistem Tanam tercatat = "Tegel" → `tegel` | Density Flag = (tidak ada flag) | Tanggal Tanam tercatat = 2024-09-28 | Tanggal Panen tercatat = 2025-01-18

**Input:**

```postman_json
{
    "land_area_are": 10,
    "duck_count": 29,
    "rice_variety": "inpari",
    "planting_system": "tegel",
    "planting_date": "2024-09-28",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2024-10-19",
    "D_tarik_bebek": "2024-12-02",
    "D_panen_gabah": "2025-02-09",
    "N_survive": 20.0,
    "Yield_are_predict": 45.82,
    "Yield_total_predict": 458.2,
    "Revenue_gabah": 2749200.0,
    "Revenue_duck": 700000.0,
    "Total_Revenue": 3449200.0,
    "Cost_duck_buy": 725000.0,
    "Cost_feed": 140287.5,
    "Cost_weeding_isolated": 106553.43,
    "Cost_pesticide_isolated": 10459.83,
    "Cost_infra_isolated": 632360.22,
    "Cost_fertilizer_isolated": 111582.74,
    "Cost_infra_net_isolated": 457360.22,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 13658.55,
    "Cost_fert_phonska_isolated": 97924.19,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 725000.0,
    "Profit_net_cash": 2724200.0,
    "Valuation_weed_eco": 80050.37,
    "Profit_net_full": 2804250.37,
    "F_sys": 1.211
}
```

---

### Skenario 28 — I Wayan Jana (Pedahanan, Babakan) — Subak Pedahanan, Munduk Babakan (cycle 2)

**Sumber acuan:** Excel Row (Sumber) = 46 | Group No = 42 | Farmer Cycle No = 2 | Varietas tercatat = "Sertani" → `sertani` | Sistem Tanam tercatat = "Jarwo 2:1" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam/Panen tercatat = tidak tersedia di sumber

**Input:**

```postman_json
{
    "land_area_are": 4.5,
    "duck_count": 9,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-03",
    "N_survive": 6.0,
    "Yield_are_predict": 37.84,
    "Yield_total_predict": 170.3,
    "Revenue_gabah": 1021800.0,
    "Revenue_duck": 210000.0,
    "Total_Revenue": 1231800.0,
    "Cost_duck_buy": 225000.0,
    "Cost_feed": 43537.5,
    "Cost_weeding_isolated": 62649.44,
    "Cost_pesticide_isolated": 5738.25,
    "Cost_infra_isolated": 481806.56,
    "Cost_fertilizer_isolated": 52063.54,
    "Cost_infra_net_isolated": 306806.56,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 5509.88,
    "Cost_fert_phonska_isolated": 46553.65,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 225000.0,
    "Profit_net_cash": 1006800.0,
    "Valuation_weed_eco": 28441.67,
    "Profit_net_full": 1035241.67,
    "F_sys": 1.0
}
```

---

### Skenario 29 — I Gusti Ngurah Putu Suka Nada (Pedahanan, Babakan) — Subak Pedahanan, Munduk Babakan (cycle 2)

**Sumber acuan:** Excel Row (Sumber) = 47 | Group No = 42 | Farmer Cycle No = 2 | Varietas tercatat = "Sertani" → `sertani` | Sistem Tanam tercatat = "Jarwo 2:1" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam/Panen tercatat = tidak tersedia di sumber

**Input:**

```postman_json
{
    "land_area_are": 3,
    "duck_count": 6,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-03",
    "N_survive": 4.0,
    "Yield_are_predict": 37.84,
    "Yield_total_predict": 113.5,
    "Revenue_gabah": 681000.0,
    "Revenue_duck": 140000.0,
    "Total_Revenue": 821000.0,
    "Cost_duck_buy": 150000.0,
    "Cost_feed": 29025.0,
    "Cost_weeding_isolated": 41766.29,
    "Cost_pesticide_isolated": 3825.5,
    "Cost_infra_isolated": 425506.51,
    "Cost_fertilizer_isolated": 34709.03,
    "Cost_infra_net_isolated": 250506.51,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 3673.26,
    "Cost_fert_phonska_isolated": 31035.77,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 150000.0,
    "Profit_net_cash": 671000.0,
    "Valuation_weed_eco": 18961.11,
    "Profit_net_full": 689961.11,
    "F_sys": 1.0
}
```

---

### Skenario 30 — I Wayan Arta Susila (Pedahanan, Babakan) — Subak Pedahanan, Munduk Babakan (cycle 2)

**Sumber acuan:** Excel Row (Sumber) = 49 | Group No = 42 | Farmer Cycle No = 2 | Varietas tercatat = "Sertani" → `sertani` | Sistem Tanam tercatat = "Jarwo 2:1" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam/Panen tercatat = tidak tersedia di sumber

**Input:**

```postman_json
{
    "land_area_are": 3.55,
    "duck_count": 7,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "WARNING_UNDER_DENSITY",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-03",
    "N_survive": 5.0,
    "Yield_are_predict": 37.77,
    "Yield_total_predict": 134.1,
    "Revenue_gabah": 804600.0,
    "Revenue_duck": 175000.0,
    "Total_Revenue": 979600.0,
    "Cost_duck_buy": 175000.0,
    "Cost_feed": 33862.5,
    "Cost_weeding_isolated": 49848.68,
    "Cost_pesticide_isolated": 4556.68,
    "Cost_infra_isolated": 447503.8,
    "Cost_fertilizer_isolated": 41118.06,
    "Cost_infra_net_isolated": 272503.8,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 4330.97,
    "Cost_fert_phonska_isolated": 36787.09,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 175000.0,
    "Profit_net_cash": 804600.0,
    "Valuation_weed_eco": 22218.03,
    "Profit_net_full": 826818.03,
    "F_sys": 1.0
}
```

---

### Skenario 31 — I Wayan Suwendhi Artha (Uma Lambing, Lambing) — SUL Munduk Lambing Batch 1 (cycle 5)

**Sumber acuan:** Excel Row (Sumber) = 51 | Group No = 44 | Farmer Cycle No = 5 | Varietas tercatat = "Sertani" → `sertani` | Sistem Tanam tercatat = "Jarwo 2:1" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam tercatat = 2025-04-09 | Tanggal Panen tercatat = 2025-07-19

**Input:**

```postman_json
{
    "land_area_are": 4.81,
    "duck_count": 10,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2025-04-09",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2025-04-30",
    "D_tarik_bebek": "2025-06-13",
    "D_panen_gabah": "2025-08-01",
    "N_survive": 7.0,
    "Yield_are_predict": 37.84,
    "Yield_total_predict": 182.0,
    "Revenue_gabah": 1092000.0,
    "Revenue_duck": 245000.0,
    "Total_Revenue": 1337000.0,
    "Cost_duck_buy": 250000.0,
    "Cost_feed": 48375.0,
    "Cost_weeding_isolated": 65379.39,
    "Cost_pesticide_isolated": 6022.3,
    "Cost_infra_isolated": 492198.35,
    "Cost_fertilizer_isolated": 55476.44,
    "Cost_infra_net_isolated": 317198.35,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 5949.17,
    "Cost_fert_phonska_isolated": 49527.26,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 250000.0,
    "Profit_net_cash": 1087000.0,
    "Valuation_weed_eco": 31218.83,
    "Profit_net_full": 1118218.83,
    "F_sys": 1.0
}
```

---

### Skenario 32 — I Nyoman Suwitra (Uma Lambing, Lambing) — SUL Munduk Lambing Batch 2 (cycle 4)

**Sumber acuan:** Excel Row (Sumber) = 53 | Group No = 45 | Farmer Cycle No = 4 | Varietas tercatat = "Sertani" → `sertani` | Sistem Tanam tercatat = "Jarwo 2:1" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam tercatat = 2025-04-09 | Tanggal Panen tercatat = 2025-07-19

**Input:**

```postman_json
{
    "land_area_are": 4.8,
    "duck_count": 10,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2025-04-09",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2025-04-30",
    "D_tarik_bebek": "2025-06-13",
    "D_panen_gabah": "2025-08-01",
    "N_survive": 7.0,
    "Yield_are_predict": 37.84,
    "Yield_total_predict": 181.6,
    "Revenue_gabah": 1089600.0,
    "Revenue_duck": 245000.0,
    "Total_Revenue": 1334600.0,
    "Cost_duck_buy": 250000.0,
    "Cost_feed": 48375.0,
    "Cost_weeding_isolated": 65157.96,
    "Cost_pesticide_isolated": 6003.78,
    "Cost_infra_isolated": 491868.45,
    "Cost_fertilizer_isolated": 55351.6,
    "Cost_infra_net_isolated": 316868.45,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 5940.07,
    "Cost_fert_phonska_isolated": 49411.53,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 250000.0,
    "Profit_net_cash": 1084600.0,
    "Valuation_weed_eco": 31198.03,
    "Profit_net_full": 1115798.03,
    "F_sys": 1.0
}
```

---

### Skenario 33 — Alm. I Ketut Tantra (Uma Lambing, Lambing) — SUL Munduk Lambing Batch 3 (cycle 3)

**Sumber acuan:** Excel Row (Sumber) = 55 | Group No = 46 | Farmer Cycle No = (kosong pada sumber) | Varietas tercatat = "Sertani" → `sertani` | Sistem Tanam tercatat = "Jarwo 2:1" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam tercatat = 2025-04-19 | Tanggal Panen tercatat = 2025-07-23

**Input:**

```postman_json
{
    "land_area_are": 3.45,
    "duck_count": 7,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2025-04-19",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2025-05-10",
    "D_tarik_bebek": "2025-06-23",
    "D_panen_gabah": "2025-08-11",
    "N_survive": 5.0,
    "Yield_are_predict": 37.84,
    "Yield_total_predict": 130.5,
    "Revenue_gabah": 783000.0,
    "Revenue_duck": 175000.0,
    "Total_Revenue": 958000.0,
    "Cost_duck_buy": 175000.0,
    "Cost_feed": 33862.5,
    "Cost_weeding_isolated": 47610.24,
    "Cost_pesticide_isolated": 4369.79,
    "Cost_infra_isolated": 443638.3,
    "Cost_fertilizer_isolated": 39869.67,
    "Cost_infra_net_isolated": 268638.3,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 4239.96,
    "Cost_fert_phonska_isolated": 35629.71,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 175000.0,
    "Profit_net_cash": 783000.0,
    "Valuation_weed_eco": 22022.39,
    "Profit_net_full": 805022.39,
    "F_sys": 1.0
}
```

---

### Skenario 34 — I Wayan Buana (Ketapang, Ketapang) — Subak Ketapang, Munduk Ketapang Batch 1 (cycle 3)

**Sumber acuan:** Excel Row (Sumber) = 60 | Group No = 48 | Farmer Cycle No = 3 | Varietas tercatat = "Sertani" → `sertani` | Sistem Tanam tercatat = "Jarwo 2:1" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam tercatat = tidak tersedia | Tanggal Panen tercatat = 2025-07-19 (planting_date tetap null karena tanggal tanam tidak tercatat)

**Input:**

```postman_json
{
    "land_area_are": 4.44,
    "duck_count": 9,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-03",
    "N_survive": 6.0,
    "Yield_are_predict": 37.84,
    "Yield_total_predict": 168.0,
    "Revenue_gabah": 1008000.0,
    "Revenue_duck": 210000.0,
    "Total_Revenue": 1218000.0,
    "Cost_duck_buy": 225000.0,
    "Cost_feed": 43537.5,
    "Cost_weeding_isolated": 61308.74,
    "Cost_pesticide_isolated": 5626.29,
    "Cost_infra_isolated": 479754.32,
    "Cost_fertilizer_isolated": 51314.51,
    "Cost_infra_net_isolated": 304754.32,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 5455.28,
    "Cost_fert_phonska_isolated": 45859.23,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 225000.0,
    "Profit_net_cash": 993000.0,
    "Valuation_weed_eco": 28323.07,
    "Profit_net_full": 1021323.07,
    "F_sys": 1.0
}
```

---

### Skenario 35 — I Ketut Buda (Ketapang, Ketapang) — Subak Ketapang, Munduk Ketapang Batch 1 (cycle 3)

**Sumber acuan:** Excel Row (Sumber) = 61 | Group No = 48 | Farmer Cycle No = 3 | Varietas tercatat = "Sertani" → `sertani` | Sistem Tanam tercatat = "Jarwo 2:1" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam tercatat = tidak tersedia | Tanggal Panen tercatat = 2025-07-20 (planting_date tetap null karena tanggal tanam tidak tercatat)

**Input:**

```postman_json
{
    "land_area_are": 4.43,
    "duck_count": 9,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-03",
    "N_survive": 6.0,
    "Yield_are_predict": 37.84,
    "Yield_total_predict": 167.6,
    "Revenue_gabah": 1005600.0,
    "Revenue_duck": 210000.0,
    "Total_Revenue": 1215600.0,
    "Cost_duck_buy": 225000.0,
    "Cost_feed": 43537.5,
    "Cost_weeding_isolated": 61085.76,
    "Cost_pesticide_isolated": 5607.66,
    "Cost_infra_isolated": 479410.94,
    "Cost_fertilizer_isolated": 51189.67,
    "Cost_infra_net_isolated": 304410.94,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 5446.18,
    "Cost_fert_phonska_isolated": 45743.49,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 225000.0,
    "Profit_net_cash": 990600.0,
    "Valuation_weed_eco": 28303.06,
    "Profit_net_full": 1018903.06,
    "F_sys": 1.0
}
```

---

### Skenario 36 — I Made Suardika (Ketapang, Ketapang) — Subak Ketapang, Munduk Ketapang Batch 1 (cycle 3)

**Sumber acuan:** Excel Row (Sumber) = 62 | Group No = 48 | Farmer Cycle No = 3 | Varietas tercatat = "Sertani" → `sertani` | Sistem Tanam tercatat = "Jarwo 2:1" → `jajar_legowo` | Density Flag = (tidak ada flag) | Tanggal Tanam tercatat = tidak tersedia | Tanggal Panen tercatat = 2025-07-17 (planting_date tetap null karena tanggal tanam tidak tercatat)

**Input:**

```postman_json
{
    "land_area_are": 3.77,
    "duck_count": 8,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-07-12",
    "duck_age_days": 21
}
```

**Output:**

```postman_json
{
    "density_status": "SAFE",
    "age_status": "AGE_BUY_RANGE",
    "D_masuk_bebek": "2026-08-02",
    "D_tarik_bebek": "2026-09-15",
    "D_panen_gabah": "2026-11-03",
    "N_survive": 5.0,
    "Yield_are_predict": 37.84,
    "Yield_total_predict": 142.7,
    "Revenue_gabah": 856200.0,
    "Revenue_duck": 175000.0,
    "Total_Revenue": 1031200.0,
    "Cost_duck_buy": 200000.0,
    "Cost_feed": 38700.0,
    "Cost_weeding_isolated": 50580.85,
    "Cost_pesticide_isolated": 4673.7,
    "Cost_infra_isolated": 455820.66,
    "Cost_fertilizer_isolated": 43407.4,
    "Cost_infra_net_isolated": 280820.66,
    "Cost_infra_cage_isolated": 175000.0,
    "Cost_fert_urea_isolated": 4688.35,
    "Cost_fert_phonska_isolated": 38719.06,
    "Cost_fert_kcl_isolated": 0.0,
    "Cost_total_cash": 200000.0,
    "Profit_net_cash": 831200.0,
    "Valuation_weed_eco": 24810.44,
    "Profit_net_full": 856010.44,
    "F_sys": 1.0
}
```
