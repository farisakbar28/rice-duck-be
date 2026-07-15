# PANDUAN PENGUJIAN SKENARIO INPUT MANUAL

## DSS Padi-Bebek — Uji Input Manual vs Rekap Bersih (1 Skenario = 1 Baris Rekap)

**Ruang lingkup dokumen ini:** menyusun daftar skenario input uji manual, satu skenario untuk **setiap baris/siklus** yang tercatat pada sheet "Dataset Actual Bersih" file rekap bersih terbaru (v10), tanpa mengecualikan satu baris pun — termasuk baris yang memiliki kolom kosong/bernilai default. Dokumen ini **tidak** menghitung yield/cost/profit prediksi, **tidak** menjalankan model, dan **tidak** menghasilkan metrik akurasi apa pun. **Bagian "Output" pada setiap skenario di bawah ini telah diisi, diverifikasi, dan divalidasi otomatis berdasarkan hasil eksekusi nyata dari sistem backend live (SoT v2 - Economic Differential-Costing Engine).** **[Update]** File ini telah diperbarui: `duck_age_days` diubah dari 21 menjadi 30 (mengikuti pembaruan U_bebek kualitatif pada Dataset Actual Bersih, sesuai klarifikasi mitra bahwa 30 hari adalah usia masuk lahan paling aman), dan seluruh nilai pada blok Output telah terisi otomatis dari response API backend.

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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "WARNING_DENSITY",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-03",
        "N_survive": 21.0,
        "Yield_are_predict": 52.54,
        "Yield_total_predict": 346.8,
        "Revenue_gabah": 2080667.14,
        "Revenue_duck": 735000.0,
        "Total_Revenue": 2815667.14,
        "Cost_duck_buy": 750000.0,
        "Cost_feed_isolated": 152181.82,
        "Cost_weeding_isolated": 44831.34,
        "Cost_pesticide_isolated": 5114.92,
        "Cost_infra_isolated": 546561.2,
        "Cost_fertilizer_isolated": 68826.09,
        "Cost_infra_net_isolated": 371561.2,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 10671.22,
        "Cost_fert_phonska_isolated": 58154.88,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 750000.0,
        "Profit_net_cash": 2065667.14,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "SAFE",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-03",
        "N_survive": 21.0,
        "Yield_are_predict": 51.17,
        "Yield_total_predict": 537.2,
        "Revenue_gabah": 3223437.03,
        "Revenue_duck": 735000.0,
        "Total_Revenue": 3958437.03,
        "Cost_duck_buy": 700000.0,
        "Cost_feed_isolated": 129150.0,
        "Cost_weeding_isolated": 119764.24,
        "Cost_pesticide_isolated": 11535.88,
        "Cost_infra_isolated": 643654.76,
        "Cost_fertilizer_isolated": 117589.96,
        "Cost_infra_net_isolated": 468654.76,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 14194.31,
        "Cost_fert_phonska_isolated": 103395.65,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 700000.0,
        "Profit_net_cash": 3258437.03,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "SAFE",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-03",
        "N_survive": 7.0,
        "Yield_are_predict": 50.59,
        "Yield_total_predict": 242.8,
        "Revenue_gabah": 1456965.91,
        "Revenue_duck": 245000.0,
        "Total_Revenue": 1701965.91,
        "Cost_duck_buy": 250000.0,
        "Cost_feed_isolated": 46125.0,
        "Cost_weeding_isolated": 65157.96,
        "Cost_pesticide_isolated": 6003.78,
        "Cost_infra_isolated": 491868.45,
        "Cost_fertilizer_isolated": 55104.51,
        "Cost_infra_net_isolated": 316868.45,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 6025.02,
        "Cost_fert_phonska_isolated": 49079.49,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 250000.0,
        "Profit_net_cash": 1451965.91,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "SAFE",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-03",
        "N_survive": 12.0,
        "Yield_are_predict": 51.9,
        "Yield_total_predict": 233.5,
        "Revenue_gabah": 1401230.66,
        "Revenue_duck": 420000.0,
        "Total_Revenue": 1821230.66,
        "Cost_duck_buy": 400000.0,
        "Cost_feed_isolated": 73800.0,
        "Cost_weeding_isolated": 39808.95,
        "Cost_pesticide_isolated": 4135.84,
        "Cost_infra_isolated": 481806.56,
        "Cost_fertilizer_isolated": 48468.41,
        "Cost_infra_net_isolated": 306806.56,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 6745.86,
        "Cost_fert_phonska_isolated": 41722.55,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 400000.0,
        "Profit_net_cash": 1421230.66,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "SAFE",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-03",
        "N_survive": 9.0,
        "Yield_are_predict": 51.94,
        "Yield_total_predict": 187.0,
        "Revenue_gabah": 1121860.61,
        "Revenue_duck": 315000.0,
        "Total_Revenue": 1436860.61,
        "Cost_duck_buy": 325000.0,
        "Cost_feed_isolated": 59962.5,
        "Cost_weeding_isolated": 31360.92,
        "Cost_pesticide_isolated": 3274.56,
        "Cost_infra_isolated": 449416.13,
        "Cost_fertilizer_isolated": 38678.36,
        "Cost_infra_net_isolated": 274416.13,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 5429.82,
        "Cost_fert_phonska_isolated": 33248.54,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 325000.0,
        "Profit_net_cash": 1111860.61,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "WARNING_UNDER_DENSITY",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-03",
        "N_survive": 3.0,
        "Yield_are_predict": 49.24,
        "Yield_total_predict": 251.1,
        "Revenue_gabah": 1506745.85,
        "Revenue_duck": 105000.0,
        "Total_Revenue": 1611745.85,
        "Cost_duck_buy": 125000.0,
        "Cost_feed_isolated": 23062.5,
        "Cost_weeding_isolated": 97443.73,
        "Cost_pesticide_isolated": 8358.37,
        "Cost_infra_isolated": 501620.53,
        "Cost_fertilizer_isolated": 61258.79,
        "Cost_infra_net_isolated": 326620.53,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 5469.82,
        "Cost_fert_phonska_isolated": 55788.97,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 125000.0,
        "Profit_net_cash": 1486745.85,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "SAFE",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-03",
        "N_survive": 7.0,
        "Yield_are_predict": 51.56,
        "Yield_total_predict": 165.0,
        "Revenue_gabah": 990014.32,
        "Revenue_duck": 245000.0,
        "Total_Revenue": 1235014.32,
        "Cost_duck_buy": 250000.0,
        "Cost_feed_isolated": 46125.0,
        "Cost_weeding_isolated": 31959.02,
        "Cost_pesticide_isolated": 3197.15,
        "Cost_infra_isolated": 433722.01,
        "Cost_fertilizer_isolated": 35130.27,
        "Cost_infra_net_isolated": 258722.01,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 4568.83,
        "Cost_fert_phonska_isolated": 30561.43,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 250000.0,
        "Profit_net_cash": 985014.32,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "WARNING_DENSITY",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-03",
        "N_survive": 35.0,
        "Yield_are_predict": 53.43,
        "Yield_total_predict": 534.3,
        "Revenue_gabah": 3205773.78,
        "Revenue_duck": 1225000.0,
        "Total_Revenue": 4430773.78,
        "Cost_duck_buy": 1625000.0,
        "Cost_feed_isolated": 436921.88,
        "Cost_weeding_isolated": 43351.06,
        "Cost_pesticide_isolated": 6025.77,
        "Cost_infra_isolated": 632360.22,
        "Cost_fertilizer_isolated": 102328.92,
        "Cost_infra_net_isolated": 457360.22,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 16839.95,
        "Cost_fert_phonska_isolated": 85488.96,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 1625000.0,
        "Profit_net_cash": 2805773.78,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "WARNING_DENSITY",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-03",
        "N_survive": 19.0,
        "Yield_are_predict": 53.68,
        "Yield_total_predict": 295.2,
        "Revenue_gabah": 1771340.52,
        "Revenue_duck": 665000.0,
        "Total_Revenue": 2436340.52,
        "Cost_duck_buy": 1000000.0,
        "Cost_feed_isolated": 294954.55,
        "Cost_weeding_isolated": 20581.33,
        "Cost_pesticide_isolated": 3085.34,
        "Cost_infra_isolated": 514187.42,
        "Cost_fertilizer_isolated": 56484.51,
        "Cost_infra_net_isolated": 339187.42,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 9191.97,
        "Cost_fert_phonska_isolated": 47292.54,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 1000000.0,
        "Profit_net_cash": 1436340.52,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "WARNING_UNDER_DENSITY",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-03",
        "N_survive": 6.0,
        "Yield_are_predict": 49.59,
        "Yield_total_predict": 360.0,
        "Revenue_gabah": 2160201.69,
        "Revenue_duck": 210000.0,
        "Total_Revenue": 2370201.69,
        "Cost_duck_buy": 225000.0,
        "Cost_feed_isolated": 41512.5,
        "Cost_weeding_isolated": 127834.51,
        "Cost_pesticide_isolated": 11135.11,
        "Cost_infra_isolated": 564696.67,
        "Cost_fertilizer_isolated": 86296.72,
        "Cost_infra_net_isolated": 389696.67,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 8098.25,
        "Cost_fert_phonska_isolated": 78198.47,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 225000.0,
        "Profit_net_cash": 2145201.69,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "WARNING_DENSITY",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-03",
        "N_survive": 21.0,
        "Yield_are_predict": 52.54,
        "Yield_total_predict": 346.8,
        "Revenue_gabah": 2080667.14,
        "Revenue_duck": 735000.0,
        "Total_Revenue": 2815667.14,
        "Cost_duck_buy": 750000.0,
        "Cost_feed_isolated": 152181.82,
        "Cost_weeding_isolated": 44831.34,
        "Cost_pesticide_isolated": 5114.92,
        "Cost_infra_isolated": 546561.2,
        "Cost_fertilizer_isolated": 68826.09,
        "Cost_infra_net_isolated": 371561.2,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 10671.22,
        "Cost_fert_phonska_isolated": 58154.88,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 750000.0,
        "Profit_net_cash": 2065667.14,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "SAFE",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-03",
        "N_survive": 21.0,
        "Yield_are_predict": 51.17,
        "Yield_total_predict": 537.2,
        "Revenue_gabah": 3223437.03,
        "Revenue_duck": 735000.0,
        "Total_Revenue": 3958437.03,
        "Cost_duck_buy": 700000.0,
        "Cost_feed_isolated": 129150.0,
        "Cost_weeding_isolated": 119764.24,
        "Cost_pesticide_isolated": 11535.88,
        "Cost_infra_isolated": 643654.76,
        "Cost_fertilizer_isolated": 117589.96,
        "Cost_infra_net_isolated": 468654.76,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 14194.31,
        "Cost_fert_phonska_isolated": 103395.65,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 700000.0,
        "Profit_net_cash": 3258437.03,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "WARNING_UNDER_DENSITY",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-03",
        "N_survive": 6.0,
        "Yield_are_predict": 50.12,
        "Yield_total_predict": 240.6,
        "Revenue_gabah": 1443531.53,
        "Revenue_duck": 210000.0,
        "Total_Revenue": 1653531.53,
        "Cost_duck_buy": 200000.0,
        "Cost_feed_isolated": 36900.0,
        "Cost_weeding_isolated": 74007.01,
        "Cost_pesticide_isolated": 6624.6,
        "Cost_infra_isolated": 491868.45,
        "Cost_fertilizer_isolated": 56068.15,
        "Cost_infra_net_isolated": 316868.45,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 5693.72,
        "Cost_fert_phonska_isolated": 50374.43,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 200000.0,
        "Profit_net_cash": 1453531.53,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "SAFE",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-23",
        "N_survive": 7.0,
        "Yield_are_predict": 50.73,
        "Yield_total_predict": 228.3,
        "Revenue_gabah": 1369820.55,
        "Revenue_duck": 245000.0,
        "Total_Revenue": 1614820.55,
        "Cost_duck_buy": 250000.0,
        "Cost_feed_isolated": 46125.0,
        "Cost_weeding_isolated": 58578.43,
        "Cost_pesticide_isolated": 5452.65,
        "Cost_infra_isolated": 481806.56,
        "Cost_fertilizer_isolated": 51359.34,
        "Cost_infra_net_isolated": 306806.56,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 5751.98,
        "Cost_fert_phonska_isolated": 45607.36,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 250000.0,
        "Profit_net_cash": 1364820.55,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "WARNING_UNDER_DENSITY",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-23",
        "N_survive": 7.0,
        "Yield_are_predict": 50.46,
        "Yield_total_predict": 257.3,
        "Revenue_gabah": 1543981.25,
        "Revenue_duck": 245000.0,
        "Total_Revenue": 1788981.25,
        "Cost_duck_buy": 250000.0,
        "Cost_feed_isolated": 46125.0,
        "Cost_weeding_isolated": 71854.81,
        "Cost_pesticide_isolated": 6563.14,
        "Cost_infra_isolated": 501620.53,
        "Cost_fertilizer_isolated": 58849.68,
        "Cost_infra_net_isolated": 326620.53,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 6298.05,
        "Cost_fert_phonska_isolated": 52551.63,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 250000.0,
        "Profit_net_cash": 1538981.25,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "WARNING_UNDER_DENSITY",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-03",
        "N_survive": 2.0,
        "Yield_are_predict": 49.18,
        "Yield_total_predict": 157.4,
        "Revenue_gabah": 944250.44,
        "Revenue_duck": 70000.0,
        "Total_Revenue": 1014250.44,
        "Cost_duck_buy": 75000.0,
        "Cost_feed_isolated": 13837.5,
        "Cost_weeding_isolated": 61977.26,
        "Cost_pesticide_isolated": 5303.12,
        "Cost_infra_isolated": 433722.01,
        "Cost_fertilizer_isolated": 38503.02,
        "Cost_infra_net_isolated": 258722.01,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 3409.31,
        "Cost_fert_phonska_isolated": 35093.71,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 75000.0,
        "Profit_net_cash": 939250.44,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "SAFE",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-03",
        "N_survive": 22.0,
        "Yield_are_predict": 50.59,
        "Yield_total_predict": 729.0,
        "Revenue_gabah": 4373800.26,
        "Revenue_duck": 770000.0,
        "Total_Revenue": 5143800.26,
        "Cost_duck_buy": 750000.0,
        "Cost_feed_isolated": 138375.0,
        "Cost_weeding_isolated": 195695.28,
        "Cost_pesticide_isolated": 18029.85,
        "Cost_infra_isolated": 724022.8,
        "Cost_fertilizer_isolated": 165438.37,
        "Cost_infra_net_isolated": 549022.8,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 18084.15,
        "Cost_fert_phonska_isolated": 147354.21,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 750000.0,
        "Profit_net_cash": 4393800.26,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "WARNING_DENSITY",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-03",
        "N_survive": 20.0,
        "Yield_are_predict": 53.88,
        "Yield_total_predict": 296.3,
        "Revenue_gabah": 1778020.06,
        "Revenue_duck": 700000.0,
        "Total_Revenue": 2478020.06,
        "Cost_duck_buy": 1250000.0,
        "Cost_feed_isolated": 399375.0,
        "Cost_weeding_isolated": 15636.75,
        "Cost_pesticide_isolated": 2738.45,
        "Cost_infra_isolated": 514187.42,
        "Cost_fertilizer_isolated": 55411.37,
        "Cost_infra_net_isolated": 339187.42,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 9560.91,
        "Cost_fert_phonska_isolated": 45850.45,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 1250000.0,
        "Profit_net_cash": 1228020.06,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "SAFE",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2024-03-11",
        "D_tarik_bebek": "2024-04-24",
        "D_panen_gabah": "2024-06-12",
        "N_survive": 15.0,
        "Yield_are_predict": 51.58,
        "Yield_total_predict": 327.6,
        "Revenue_gabah": 1965324.84,
        "Revenue_duck": 525000.0,
        "Total_Revenue": 2490324.84,
        "Cost_duck_buy": 500000.0,
        "Cost_feed_isolated": 92250.0,
        "Cost_weeding_isolated": 62974.64,
        "Cost_pesticide_isolated": 6313.19,
        "Cost_infra_isolated": 539456.12,
        "Cost_fertilizer_isolated": 69636.34,
        "Cost_infra_net_isolated": 364456.12,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 9092.16,
        "Cost_fert_phonska_isolated": 60544.18,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 500000.0,
        "Profit_net_cash": 1990324.84,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "SAFE",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2024-05-06",
        "D_tarik_bebek": "2024-06-19",
        "D_panen_gabah": "2024-08-07",
        "N_survive": 24.0,
        "Yield_are_predict": 51.57,
        "Yield_total_predict": 526.5,
        "Revenue_gabah": 3159224.43,
        "Revenue_duck": 840000.0,
        "Total_Revenue": 3999224.43,
        "Cost_duck_buy": 800000.0,
        "Cost_feed_isolated": 147600.0,
        "Cost_weeding_isolated": 101702.11,
        "Cost_pesticide_isolated": 10182.15,
        "Cost_infra_isolated": 637137.55,
        "Cost_fertilizer_isolated": 112042.34,
        "Cost_infra_net_isolated": 462137.55,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 14592.97,
        "Cost_fert_phonska_isolated": 97449.38,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 800000.0,
        "Profit_net_cash": 3199224.43,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "SAFE",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2024-05-03",
        "D_tarik_bebek": "2024-06-16",
        "D_panen_gabah": "2024-08-24",
        "N_survive": 14.0,
        "Yield_are_predict": 62.19,
        "Yield_total_predict": 410.5,
        "Revenue_gabah": 2462776.15,
        "Revenue_duck": 490000.0,
        "Total_Revenue": 2952776.15,
        "Cost_duck_buy": 475000.0,
        "Cost_feed_isolated": 87637.5,
        "Cost_weeding_isolated": 70759.19,
        "Cost_pesticide_isolated": 6933.93,
        "Cost_infra_isolated": 546561.2,
        "Cost_fertilizer_isolated": 73239.14,
        "Cost_infra_net_isolated": 371561.2,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 9154.04,
        "Cost_fert_phonska_isolated": 64085.09,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 475000.0,
        "Profit_net_cash": 2477776.15,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "WARNING_UNDER_DENSITY",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2024-05-14",
        "D_tarik_bebek": "2024-06-27",
        "D_panen_gabah": "2024-08-15",
        "N_survive": 6.0,
        "Yield_are_predict": 60.99,
        "Yield_total_predict": 292.7,
        "Revenue_gabah": 1756462.99,
        "Revenue_duck": 210000.0,
        "Total_Revenue": 1966462.99,
        "Cost_duck_buy": 225000.0,
        "Cost_feed_isolated": 41512.5,
        "Cost_weeding_isolated": 69421.25,
        "Cost_pesticide_isolated": 6302.87,
        "Cost_infra_isolated": 491868.45,
        "Cost_fertilizer_isolated": 55586.33,
        "Cost_infra_net_isolated": 316868.45,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 5859.37,
        "Cost_fert_phonska_isolated": 49726.96,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 225000.0,
        "Profit_net_cash": 1741462.99,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "SAFE",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2024-05-13",
        "D_tarik_bebek": "2024-06-26",
        "D_panen_gabah": "2024-08-14",
        "N_survive": 24.0,
        "Yield_are_predict": 51.62,
        "Yield_total_predict": 516.2,
        "Revenue_gabah": 3097444.56,
        "Revenue_duck": 840000.0,
        "Total_Revenue": 3937444.56,
        "Cost_duck_buy": 800000.0,
        "Cost_feed_isolated": 147600.0,
        "Cost_weeding_isolated": 97759.18,
        "Cost_pesticide_isolated": 9842.86,
        "Cost_infra_isolated": 632360.22,
        "Cost_fertilizer_isolated": 109420.72,
        "Cost_infra_net_isolated": 457360.22,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 14401.84,
        "Cost_fert_phonska_isolated": 95018.88,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 800000.0,
        "Profit_net_cash": 3137444.56,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "SAFE",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2024-05-06",
        "D_tarik_bebek": "2024-06-19",
        "D_panen_gabah": "2024-08-07",
        "N_survive": 13.0,
        "Yield_are_predict": 51.68,
        "Yield_total_predict": 284.3,
        "Revenue_gabah": 1705505.46,
        "Revenue_duck": 455000.0,
        "Total_Revenue": 2160505.46,
        "Cost_duck_buy": 450000.0,
        "Cost_feed_isolated": 83025.0,
        "Cost_weeding_isolated": 52669.5,
        "Cost_pesticide_isolated": 5336.54,
        "Cost_infra_isolated": 514187.42,
        "Cost_fertilizer_isolated": 59988.67,
        "Cost_infra_net_isolated": 339187.42,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 7987.27,
        "Cost_fert_phonska_isolated": 52001.4,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 450000.0,
        "Profit_net_cash": 1710505.46,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "WARNING_UNDER_DENSITY",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2024-08-07",
        "D_tarik_bebek": "2024-09-20",
        "D_panen_gabah": "2024-11-28",
        "N_survive": 3.0,
        "Yield_are_predict": 59.29,
        "Yield_total_predict": 376.5,
        "Revenue_gabah": 2259124.91,
        "Revenue_duck": 105000.0,
        "Total_Revenue": 2364124.91,
        "Cost_duck_buy": 125000.0,
        "Cost_feed_isolated": 23062.5,
        "Cost_weeding_isolated": 128992.22,
        "Cost_pesticide_isolated": 10944.75,
        "Cost_infra_isolated": 539456.12,
        "Cost_fertilizer_isolated": 76863.66,
        "Cost_infra_net_isolated": 364456.12,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 6607.46,
        "Cost_fert_phonska_isolated": 70256.2,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 125000.0,
        "Profit_net_cash": 2239124.91,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "WARNING_DENSITY",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2024-10-22",
        "D_tarik_bebek": "2024-12-05",
        "D_panen_gabah": "2025-01-23",
        "N_survive": 11.0,
        "Yield_are_predict": 52.31,
        "Yield_total_predict": 188.3,
        "Revenue_gabah": 1129983.58,
        "Revenue_duck": 385000.0,
        "Total_Revenue": 1514983.58,
        "Cost_duck_buy": 375000.0,
        "Cost_feed_isolated": 71296.88,
        "Cost_weeding_isolated": 26984.91,
        "Cost_pesticide_isolated": 2967.56,
        "Cost_infra_isolated": 449416.13,
        "Cost_fertilizer_isolated": 37850.23,
        "Cost_infra_net_isolated": 274416.13,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 5714.53,
        "Cost_fert_phonska_isolated": 32135.71,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 375000.0,
        "Profit_net_cash": 1139983.58,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "SAFE",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2024-10-19",
        "D_tarik_bebek": "2024-12-02",
        "D_panen_gabah": "2025-02-09",
        "N_survive": 22.0,
        "Yield_are_predict": 62.21,
        "Yield_total_predict": 622.1,
        "Revenue_gabah": 3732817.4,
        "Revenue_duck": 770000.0,
        "Total_Revenue": 4502817.4,
        "Cost_duck_buy": 725000.0,
        "Cost_feed_isolated": 133762.5,
        "Cost_weeding_isolated": 106553.43,
        "Cost_pesticide_isolated": 10459.83,
        "Cost_infra_isolated": 632360.22,
        "Cost_fertilizer_isolated": 110866.19,
        "Cost_infra_net_isolated": 457360.22,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 13904.9,
        "Cost_fert_phonska_isolated": 96961.29,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 725000.0,
        "Profit_net_cash": 3777817.4,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "SAFE",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-03",
        "N_survive": 6.0,
        "Yield_are_predict": 50.5,
        "Yield_total_predict": 227.2,
        "Revenue_gabah": 1363490.44,
        "Revenue_duck": 210000.0,
        "Total_Revenue": 1573490.44,
        "Cost_duck_buy": 225000.0,
        "Cost_feed_isolated": 41512.5,
        "Cost_weeding_isolated": 62649.44,
        "Cost_pesticide_isolated": 5738.25,
        "Cost_infra_isolated": 481806.56,
        "Cost_fertilizer_isolated": 51841.16,
        "Cost_infra_net_isolated": 306806.56,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 5586.34,
        "Cost_fert_phonska_isolated": 46254.82,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 225000.0,
        "Profit_net_cash": 1348490.44,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "SAFE",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-03",
        "N_survive": 4.0,
        "Yield_are_predict": 50.5,
        "Yield_total_predict": 151.5,
        "Revenue_gabah": 908993.63,
        "Revenue_duck": 140000.0,
        "Total_Revenue": 1048993.63,
        "Cost_duck_buy": 150000.0,
        "Cost_feed_isolated": 27675.0,
        "Cost_weeding_isolated": 41766.29,
        "Cost_pesticide_isolated": 3825.5,
        "Cost_infra_isolated": 425506.51,
        "Cost_fertilizer_isolated": 34560.77,
        "Cost_infra_net_isolated": 250506.51,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 3724.22,
        "Cost_fert_phonska_isolated": 30836.55,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 150000.0,
        "Profit_net_cash": 898993.63,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "WARNING_UNDER_DENSITY",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-03",
        "N_survive": 5.0,
        "Yield_are_predict": 50.47,
        "Yield_total_predict": 179.2,
        "Revenue_gabah": 1074989.4,
        "Revenue_duck": 175000.0,
        "Total_Revenue": 1249989.4,
        "Cost_duck_buy": 175000.0,
        "Cost_feed_isolated": 32287.5,
        "Cost_weeding_isolated": 49848.68,
        "Cost_pesticide_isolated": 4556.68,
        "Cost_infra_isolated": 447503.8,
        "Cost_fertilizer_isolated": 40945.1,
        "Cost_infra_net_isolated": 272503.8,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 4390.43,
        "Cost_fert_phonska_isolated": 36554.66,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 175000.0,
        "Profit_net_cash": 1074989.4,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "SAFE",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2025-04-30",
        "D_tarik_bebek": "2025-06-13",
        "D_panen_gabah": "2025-08-01",
        "N_survive": 7.0,
        "Yield_are_predict": 50.58,
        "Yield_total_predict": 243.3,
        "Revenue_gabah": 1459868.4,
        "Revenue_duck": 245000.0,
        "Total_Revenue": 1704868.4,
        "Cost_duck_buy": 250000.0,
        "Cost_feed_isolated": 46125.0,
        "Cost_weeding_isolated": 65379.39,
        "Cost_pesticide_isolated": 6022.3,
        "Cost_infra_isolated": 492198.35,
        "Cost_fertilizer_isolated": 55229.35,
        "Cost_infra_net_isolated": 317198.35,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 6034.12,
        "Cost_fert_phonska_isolated": 49195.23,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 250000.0,
        "Profit_net_cash": 1454868.4,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "SAFE",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2025-04-30",
        "D_tarik_bebek": "2025-06-13",
        "D_panen_gabah": "2025-08-01",
        "N_survive": 7.0,
        "Yield_are_predict": 50.59,
        "Yield_total_predict": 242.8,
        "Revenue_gabah": 1456965.91,
        "Revenue_duck": 245000.0,
        "Total_Revenue": 1701965.91,
        "Cost_duck_buy": 250000.0,
        "Cost_feed_isolated": 46125.0,
        "Cost_weeding_isolated": 65157.96,
        "Cost_pesticide_isolated": 6003.78,
        "Cost_infra_isolated": 491868.45,
        "Cost_fertilizer_isolated": 55104.51,
        "Cost_infra_net_isolated": 316868.45,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 6025.02,
        "Cost_fert_phonska_isolated": 49079.49,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 250000.0,
        "Profit_net_cash": 1451965.91,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "SAFE",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2025-05-10",
        "D_tarik_bebek": "2025-06-23",
        "D_panen_gabah": "2025-08-11",
        "N_survive": 5.0,
        "Yield_are_predict": 50.53,
        "Yield_total_predict": 174.3,
        "Revenue_gabah": 1045991.08,
        "Revenue_duck": 175000.0,
        "Total_Revenue": 1220991.08,
        "Cost_duck_buy": 175000.0,
        "Cost_feed_isolated": 32287.5,
        "Cost_weeding_isolated": 47610.24,
        "Cost_pesticide_isolated": 4369.79,
        "Cost_infra_isolated": 443638.3,
        "Cost_fertilizer_isolated": 39696.71,
        "Cost_infra_net_isolated": 268638.3,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 4299.42,
        "Cost_fert_phonska_isolated": 35397.28,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 175000.0,
        "Profit_net_cash": 1045991.08,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "SAFE",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-03",
        "N_survive": 6.0,
        "Yield_are_predict": 50.53,
        "Yield_total_predict": 224.3,
        "Revenue_gabah": 1346088.84,
        "Revenue_duck": 210000.0,
        "Total_Revenue": 1556088.84,
        "Cost_duck_buy": 225000.0,
        "Cost_feed_isolated": 41512.5,
        "Cost_weeding_isolated": 61308.74,
        "Cost_pesticide_isolated": 5626.29,
        "Cost_infra_isolated": 479754.32,
        "Cost_fertilizer_isolated": 51092.13,
        "Cost_infra_net_isolated": 304754.32,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 5531.73,
        "Cost_fert_phonska_isolated": 45560.4,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 225000.0,
        "Profit_net_cash": 1331088.84,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "SAFE",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-03",
        "N_survive": 6.0,
        "Yield_are_predict": 50.53,
        "Yield_total_predict": 223.9,
        "Revenue_gabah": 1343188.06,
        "Revenue_duck": 210000.0,
        "Total_Revenue": 1553188.06,
        "Cost_duck_buy": 225000.0,
        "Cost_feed_isolated": 41512.5,
        "Cost_weeding_isolated": 61085.76,
        "Cost_pesticide_isolated": 5607.66,
        "Cost_infra_isolated": 479410.94,
        "Cost_fertilizer_isolated": 50967.29,
        "Cost_infra_net_isolated": 304410.94,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 5522.63,
        "Cost_fert_phonska_isolated": 45444.66,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 225000.0,
        "Profit_net_cash": 1328188.06,
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
    "duck_age_days": 30
}
```

**Output:**

```postman_json
    {
        "density_status": "SAFE",
        "age_status": "ADAPTED_FULLY",
        "D_masuk_bebek": "2026-08-02",
        "D_tarik_bebek": "2026-09-15",
        "D_panen_gabah": "2026-11-03",
        "N_survive": 6.0,
        "Yield_are_predict": 50.63,
        "Yield_total_predict": 190.9,
        "Revenue_gabah": 1145250.28,
        "Revenue_duck": 210000.0,
        "Total_Revenue": 1355250.28,
        "Cost_duck_buy": 200000.0,
        "Cost_feed_isolated": 36900.0,
        "Cost_weeding_isolated": 50580.85,
        "Cost_pesticide_isolated": 4673.7,
        "Cost_infra_isolated": 455820.66,
        "Cost_fertilizer_isolated": 43209.73,
        "Cost_infra_net_isolated": 280820.66,
        "Cost_infra_cage_isolated": 175000.0,
        "Cost_fert_urea_isolated": 4756.31,
        "Cost_fert_phonska_isolated": 38453.43,
        "Cost_fert_kcl_isolated": 0.0,
        "Cost_total_cash": 200000.0,
        "Profit_net_cash": 1155250.28,
        "F_sys": 1.0
    }
```
