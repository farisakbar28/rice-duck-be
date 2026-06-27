# DSS Yield Prediction Padi-Bebek — Dokumentasi Sistem

Backend **FastAPI** untuk Decision Support System (DSS) pertanian padi-bebek (_rice-duck farming_).
Model bersifat **deterministik matematis** — bukan machine learning, bukan IoT.

---

## Daftar Isi

1. [Gambaran Umum](#1-gambaran-umum)
2. [Input Sistem](#2-input-sistem)
3. [Alur Perhitungan](#3-alur-perhitungan)
4. [Modul Utama](#4-modul-utama)
5. [Rumus-Rumus Penting](#5-rumus-rumus-penting)
6. [Status Klaim Data](#6-status-klaim-data)
7. [Data Tersedia & Belum Tersedia](#7-data-tersedia--belum-tersedia)
8. [Penanganan Data Tidak Lengkap](#8-penanganan-data-tidak-lengkap)
9. [API & Endpoint](#9-api--endpoint)
10. [Struktur Response Simulasi](#10-struktur-response-simulasi)
11. [Panduan Frontend](#11-panduan-frontend)
12. [Contoh Simulasi](#12-contoh-simulasi)
13. [Batasan & Catatan Kalibrasi](#13-batasan--catatan-kalibrasi)
14. [Cara Menjalankan](#14-cara-menjalankan)

---

## 1. Gambaran Umum

**Konteks penelitian:** Sistem ini mendukung penelitian Astungkara Way tentang integrasi bebek
di lahan padi sawah. Bebek dilepas selama fase vegetatif padi untuk membantu pengendalian hama,
gulma, dan pemupukan alami. DSS membantu petani memutuskan:

- Berapa ekor bebek yang optimal untuk luas lahan tertentu
- Kapan bebek dilepas dan ditarik kembali
- Estimasi yield padi yang dihasilkan
- Perkiraan keuntungan bersih per musim
- Dampak ekologis yang diharapkan
- Kualitas rekomendasi (Q_output) berdasarkan kelengkapan data Rev 4

**Arsitektur sistem:**

- Backend: Python 3.12 + FastAPI + SQLite
- Model: persamaan matematika deterministik dari dokumen model Rev 4
- Rekomendasi: grid search atas kombinasi jumlah bebek × durasi penempatan
- Auth: JWT sederhana untuk menyimpan history simulasi per user

---

## 2. Input Sistem

Semua input dikirim ke endpoint `POST /api/v1/dss/simulate`:

| Field             | Tipe              | Keterangan                                                             |
| ----------------- | ----------------- | ---------------------------------------------------------------------- |
| `duck_count`      | integer ≥ 0       | Jumlah bebek yang akan dilepas                                         |
| `land_area_are`   | float > 0         | Luas lahan **dalam are** (satuan utama — wajib area aktif bebek)       |
| `planting_date`   | date (YYYY-MM-DD) | Tanggal tanam padi                                                     |
| `rice_variety`    | string            | Kode varietas padi (`sertani` atau `inpari`)                           |
| `planting_system` | string            | Sistem tanam (`jajar_legowo` atau `tegel`)                             |
| `duck_age_days`   | integer > 0       | Umur bebek saat masuk sawah; aktif untuk U_status, p_duck_buy_age, batas durasi, tanggal tarik, dan quality output |
| `duck_buy_price_rp_per_duck` | float > 0, optional | Harga beli aktual bebek. Diprioritaskan; diwajibkan untuk profit saat umur di luar 14–30 hari |

> **Penting — satuan lahan:** `land_area_are` diasumsikan adalah **area aktif yang benar-benar
> dimasuki bebek**, bukan total lahan jika keduanya berbeda. Jika pakai total lahan,
> kepadatan bebek bisa bias dan sistem akan mengeluarkan warning.

**Satuan utama sistem: ARE**

Sistem menggunakan **are** sebagai satuan utama untuk semua output kepada pengguna/petani.
Konversi ke hektar dibuat hanya sebagai catatan internal untuk rumus-rumus yang bersumber dari
literatur akademik berbasis ha (rumus Xiong, dll).

| Konversi                               | Arah             | Catatan                 |
| -------------------------------------- | ---------------- | ----------------------- |
| `A_ha = A_are / 100`                   | Internal         | Hanya untuk rumus Xiong |
| `d_lit_ha = d_are × 100`               | Internal         | Hanya untuk rumus Xiong |
| `x_final_kg_are = x_final_kg_ha / 100` | **Output utama** | Dilaporkan ke petani    |

---

## 3. Alur Perhitungan

```
INPUT (duck_count, land_area_are, planting_date, variety, system, duck_age_days)
  │
  ▼
[LOOKUP] Ambil HST masuk, HST heading, K_max_are, f_yield, konstanta sistem
  │
  ▼
[AGRONOMI]
  ├─ Kepadatan: d_are = duck_count / land_area_are
  ├─ Tanggal lepas: planting_date + HST_masuk
  ├─ Batas fase padi: HST_heading - HST_masuk
  ├─ Batas umur bebek: t_age_max = max(0, min(t_lokal_max, U_target_out_max - U_bebek))
  ├─ Durasi rekomendasi: t_maks_rekomendasi = min(t_max_eff, HST_heading - HST_masuk, t_age_max)
  └─ Tanggal tarik: planting_date + HST_masuk + t
  │
  ▼
[BIOLOGI BEBEK]
  ├─ Survival: N_d = duck_count × λ (λ=0.67, local-estimate)
  ├─ Kotoran per bebek: Dung(t) — rumus dua fase
  └─ Durasi efektif: t_eff = t × (10 jam / 12 jam baseline)
  │
  ▼
[UMUR BEBEK REV 4]
  ├─ U_status = lookup(U_bebek)
  ├─ p_duck_buy_age = harga aktual user atau fallback lokal umur 14–30 hari
  ├─ Q_output = min(C_area, C_calendar, C_age, C_price, C_baseline)
  └─ Catatan: umur tidak langsung mengubah yield, q_feed, survival, Dung, N/P/K, V_eco, bobot jual, atau emisi
  │
  ▼
[YIELD PADI]
  ├─ x_base = fungsi kuadratik-Gaussian Xiong (d_ha, t)
  ├─ Penalti kepadatan: P_rate = 0 jika d_are ≤ K_max; sin bertahap jika lebih
  ├─ x_penalized = x_base × (1 - P_rate)
  └─ x_final_kg_are = α × x_penalized × f_yield / 100  ← OUTPUT UTAMA
  │
  ├─────────────────────────────────────────────┐
  ▼                                             ▼
[EKONOMI]                               [EKOLOGI & EMISI]
  ├─ Pendapatan padi (jika harga ada)     ├─ Nilai penghematan pupuk (V_eco1)
  ├─ Pendapatan bebek: N_d × p_duck       ├─ Penghematan pestisida (V_eco2)
  ├─ C_duck_buy = J × p_duck_buy_age      ├─ Penghematan biaya gulma (V_gulma)
  ├─ Biaya pakan (fallback 0.10)          ├─ Hara tanah: N/P/K dari kotoran bebek
  └─ Laba bersih (parsial)                └─ Emisi = limitation, bukan output numerik aktif Rev 4
  │
  ▼
[GRID SEARCH REKOMENDASI]
  Cari kombinasi (duck_count, durasi) yang menghasilkan score terbaik:
  score = normalized_yield + normalized_ecology + normalized_profit_if_ready - risk_penalty
  dengan constraint: d_are ≤ K_max_are, durasi ≤ t_maks_rekomendasi
  catatan: profit hanya masuk objective jika numeric-ready; environment tidak masuk objective Rev 4
  │
  ▼
[EVALUASI OPTIMALITAS]
  Bandingkan skenario aktual vs rekomendasi.
  is_optimal = True → tampilkan catatan saja
  is_optimal = False → tampilkan blok rekomendasi + perbandingan
  │
  ▼
[RESPONSE DSS]
  actual_scenario, recommended_scenario, economics, ecology, environment,
  risk, data_readiness, trace, notes
```

---

## 4. Modul Utama

### 4.1 Agronomi & Kalender Tanam

Mengelola lookup varietas padi, sistem tanam, dan penghitungan tanggal.

| Parameter                 | Nilai Default        | Status                  |
| ------------------------- | -------------------- | ----------------------- |
| HST masuk bebek           | 28 HST (range 21–30) | local-estimate          |
| HST heading (batas tarik) | 60 HST (range 40–65) | local-estimate          |
| K_max Jajar Legowo        | 4.0 ekor/are         | local-estimate          |
| K_max Tegel               | 2.5 ekor/are         | local-estimate          |
| f_yield Jajar Legowo      | 1.05×                | literature-uncalibrated |
| f_yield Tegel             | 1.00×                | literature-uncalibrated |

Tanggal lepas = `planting_date + HST_masuk`
Tanggal tarik = `planting_date + HST_heading`

### 4.2 Kepadatan Bebek

Kepadatan aktual dihitung dalam **ekor/are** (satuan utama):

```
d_are = duck_count / land_area_are
```

Zona risiko kepadatan:

| Zona    | Kondisi                      | Status                   |
| ------- | ---------------------------- | ------------------------ |
| LOW     | d_are < 0.8 × K_max          | Kepadatan terlalu rendah |
| SAFE    | 0.8 × K_max ≤ d_are ≤ K_max  | Optimal                  |
| WARNING | K_max < d_are ≤ 1.25 × K_max | Di atas kapasitas        |
| HIGH    | d_are > 1.25 × K_max         | Risiko tinggi            |

### 4.3 Survival Bebek

```
N_d = duck_count × λ       λ = 0.67 (local-estimate, nilai atas, range 0.35–0.67)
```

> λ = 0.67 adalah estimasi atas dari range data lokal, **bukan rata-rata final**.
> Status: `local-estimate` (weak/indicative). Perlu kalibrasi 3–5 siklus panen.

### 4.4 Kotoran & Hara Tanah

Kotoran per bebek dihitung dengan model dua fase:

```
Dung(t) = (t / 50) × 4 kg            jika t ≤ 50 hari
Dung(t) = 4 + (t - 50) × 0.2 kg      jika t > 50 hari
```

Kontribusi hara tanah (satuan utama: **kg/are**):

```
N_tanah_are   = κ_N × (Dung/10) × d_are × λ    κ_N = 0.049
P_tanah_are   = κ_P × (Dung/10) × d_are × λ    κ_P = 0.072
K_tanah_are   = κ_K × (Dung/10) × d_are × λ    κ_K = 0.032
```

> κ_N/P/K dari literatur (MATCH_EXACT, artikel A02). Status: `literature-uncalibrated`.
> Belum divalidasi dengan uji kotoran lokal Astungkara Way.

### 4.5 Prediksi Yield Padi

Backbone: persamaan Xiong (polynomial-Gaussian) + faktor lokal:

```
x_base   = (-0.0103·d_ha² + 2.6314·d_ha + 7569.4) × exp(-((t-80)² / (2×80²)))
P_rate   = 0                                              jika d_are ≤ K_max
           min(1.0, 0.5 × (d_are - K_max) / K_max)        jika d_are > K_max
x_final  = α_local × x_base × (1 - P_rate) × f_yield
x_kg_are = x_final / 100                                  ← OUTPUT UTAMA
```

> `α_local = 1.0` (default netral, belum dikalibrasi dari panen lokal).
> `d_ha` hanya digunakan internal untuk rumus Xiong; semua output ke pengguna dalam **are**.

### 4.6 Ekonomi Padi

```
R_gabah_RD = x_final_kg_are × A_are × p_gabah_RD
R_gabah_K  = x0_kg_are × A_are × p_gabah_konv
```

> `p_gabah_RD` (harga gabah padi-bebek) belum tersedia lokal → `rice_revenue_rp = null`.
> `p_gabah_konv = 5.600 Rp/kg` (periode Maret 2026, local-estimate).

### 4.7 Ekonomi Bebek

```
Pendapatan bebek = N_d × p_duck                  p_duck = 30.000 Rp/ekor (local-estimate)
Biaya beli bebek = duck_count × p_duck_buy        p_duck_buy = 28.000 Rp/ekor (local-estimate)
Biaya pakan      = duck_count × q_feed × t_eff × p_feed × (1 - kappa_feed_save)
```

> `q_feed` lokal tidak tersedia. Fallback ke **0.10 kg/ekor/hari** dari literatur A02 (MATCH_EXACT).
> `p_feed` (harga pakan) belum tersedia → jika null, `feed_cost_rp = null`.

### 4.8 Biaya Infrastruktur

Biaya amortisasi per siklus:

| Komponen     | Nilai        | Masa Pakai | Per Siklus                         |
| ------------ | ------------ | ---------- | ---------------------------------- |
| Jaring       | Rp 1.350.000 | 2 musim    | Rp 675.000                         |
| Kandang      | Rp 600.000   | 3 musim    | Rp 200.000                         |
| Pemeliharaan | —            | —          | Rp 0 (placeholder, belum tersedia) |
| **Total**    |              |            | **Rp 875.000**                     |

> Biaya pemeliharaan bernilai 0 hanya sebagai placeholder. Bukan klaim biaya nol.

### 4.9 Manfaat Ekologis

Tiga komponen nilai ekologis-finansial (satuan: Rupiah/musim):

```
V_eco1 = max(0, (0.02·t - 0.6) × (0.107·P_N + 0.424·P_P + 0.058·P_K) × d_are × λ × A_are)
           ─ penghematan pupuk dari kotoran bebek (status: literature-uncalibrated)
           ─ guard max(0,·) karena rumus negatif jika t < 30 hari

V_eco2 = (400 / (1 + exp(-0.036626 × d_ha)) - 3.327) × A_ha   jika d_are > 3
         interpolasi linear 0 → nilai_d3                        jika d_are ≤ 3
           ─ estimasi penghematan pestisida/herbisida (status: literature-uncalibrated)
           ─ CATATAN: operator pembagian (400/(...)), bukan pangkat

r_gulma = min(1, d_are / K_max_are)
V_gulma = C_gulma × A_are × r_gulma     C_gulma = 6.000 Rp/are (local-estimate)
           ─ penghematan biaya penyiangan gulma

V_eco_total = V_eco1 + V_eco2 + V_gulma
```

> Harga pupuk yang digunakan: P_N = P_P = P_K = 2.400 Rp/kg (local-estimate).
> `V_eco1` dan `V_eco2` berstatus `literature-uncalibrated`. `V_gulma` berstatus `local-estimate`.

### 4.10 Emisi & Lingkungan

Modul ini **tidak pernah disabled**. Status selalu `literature-uncalibrated` karena flux CH4/N2O
lokal belum tersedia. Rumus tetap aktif dan output akan ada begitu data flux tersedia.

```
F_CH4_are    = F_CH4_ha / 100           (konversi dari sumber kg/ha/musim)
F_N2O_are    = F_N2O_ha / 100
CO2e_are     = F_CH4_are × 34 + F_N2O_are × 265     ← GWP IPCC 2014
GHGI         = CO2e_are / x_final_kg_are              ← intensitas emisi per kg gabah
Reduksi_CH4  = (F_CH4_konv_are - F_CH4_RD_are) / F_CH4_konv_are × 100%
```

> GWP CH4 = 34 dan GWP N2O = 265 (MATCH_EXACT, literatur A16/IPCC 2014).
> F_CH4, F_N2O, dan DO musiman lokal **belum tersedia** → semua field emisi = `null`.
> `null` berarti data belum cukup, **bukan berarti emisi nol**.

### 4.11 Laba Bersih & REY

```
Laba_bersih = R_gabah_RD + V_duck_lokal + V_eco_total - C_infra - biaya_tambahan

REY = (x_final_kg × p_gabah_RD + N_d × p_duck) / p_gabah_konv
    = null jika p_gabah_RD belum tersedia
```

> REY (Rice Equivalent Yield) memiliki ≥5 variasi notasi di literatur (A17, A08, A19, A18, B5A06)
> yang secara konsep setara. Implementasi mengikuti rumus dari dokumen model matematis.

### 4.12 Rekomendasi DSS

Grid search atas semua kombinasi valid `(duck_count, duration_days)`:

- Kandidat duck_count: integer dalam range praktis berbasis K_max dan luas lahan
- Batasan ketat: `d_are ≤ K_max_are`, `durasi ≤ HST_heading - HST_masuk`
- Kepadatan rekomendasi minimum: **2.0 ekor/are** (data lapangan, bukan boundary teknis 1.0)
- Objective: `score = normalized_yield - risk_penalty`
- Komponen ekonomi dan ekologi masuk ke score hanya jika datanya lengkap

Evaluasi optimalitas membandingkan skenario aktual petani vs rekomendasi:

| Kriteria                                          | Ambang | Status                     |
| ------------------------------------------------- | ------ | -------------------------- |
| Score safety (d_are ≤ K_max, HST valid, A > 0)    | = True | system-design              |
| `\|d_aktual - d_rec\| / d_rec`                    | ≤ 15%  | system-design-uncalibrated |
| `(yield_rec - yield_aktual) / yield_aktual × 100` | ≤ 5%   | system-design-uncalibrated |
| `ΔProfit / \|Laba_bersih_aktual\|`                | ≤ 10%  | system-design-uncalibrated |

Jika `ΔProfit = null` (ekonomi parsial): evaluasi tetap berjalan dengan basis safety + yield saja
(`optimality_basis = "safety+yield"`).

---

## 5. Rumus-Rumus Penting

Ringkasan rumus aktif yang benar-benar dijalankan sistem (bukan hanya referensi):

| Rumus          | Formula                                                                                                                                          | Status                  |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------- |
| Kepadatan      | `d_are = J / A_are`                                                                                                                              | local-calibrated        |
| Durasi aktual  | `t = HST_heading - HST_masuk`                                                                                                                    | local-estimate          |
| Survival bebek | `N_d = J × λ`                                                                                                                                    | local-estimate          |
| Durasi efektif | `t_eff = t × (10/12)`                                                                                                                            | system-design           |
| Kotoran fase-1 | `Dung = (t/50) × 4` jika t ≤ 50                                                                                                                  | literature-uncalibrated |
| Kotoran fase-2 | `Dung = 4 + (t-50) × 0.2` jika t > 50                                                                                                            | literature-uncalibrated |
| Yield base     | `x_base = (-0.0103d²+2.6314d+7569.4) × exp(-((t-80)²/12800))`                                                                                    | literature-uncalibrated |
| Penalti yield  | `P_rate = compute_penalty_rate (d_are vs K_max_are)` (P_rate = 0 jika d_are ≤ K_max; jika >K_max: min(p_max, penalty_gamma×(d_are-K_max)/K_max)) | system-design           |

| Yield final | `x_final_kg_are = α × x_base × (1-P_rate) × f_yield / 100` | mixed |
| Total yield | `total_kg = x_final_kg_are × A_are` | mixed |
| Hara N/P/K | `N_are = κ_N × (Dung/10) × d_are × λ` | literature-uncalibrated |
| V_eco1 | `max(0, (0.02t-0.6) × factor × d_are × λ × A_are)` | literature-uncalibrated |
| V_eco2 | sigmoid / linear interpolasi berbasis d_are > 3 | literature-uncalibrated |
| V_gulma | `C_gulma × A_are × min(1, d_are/K_max)` | local-estimate |
| Infra per siklus | `C_jaring/2 + C_kandang/3 + maintenance` | local-estimate |
| CO2e/are | `F_CH4_are × 34 + F_N2O_are × 265` | literature-uncalibrated |
| GHGI | `CO2e_are / x_final_kg_are` | literature-uncalibrated |
| REY | `(total_kg × p_gabah_RD + N_d × p_duck) / p_gabah_konv` | mixed |

---

## 6. Status Klaim Data

Setiap parameter dan output dalam sistem membawa salah satu status berikut:

| Status                       | Artinya                                       | Cara tampilkan di UI                                     |
| ---------------------------- | --------------------------------------------- | -------------------------------------------------------- |
| `local-calibrated`           | Data lokal kuat, konsisten multi-siklus       | Tampilkan normal, tanpa catatan                          |
| `local-estimate`             | Ada data lokal tapi belum final/lengkap       | Tampilkan dengan catatan "estimasi lokal"                |
| `literature-uncalibrated`    | Dari literatur, belum diuji lokal             | Tampilkan dengan badge/tooltip "belum dikalibrasi lokal" |
| `system-design`              | Aturan internal DSS, bukan dari data          | Tampilkan sebagai "aturan sistem"                        |
| `system-design-uncalibrated` | Ambang heuristik teknis, belum dari data      | Tampilkan dengan catatan kuat                            |
| `mixed`                      | Gabungan beberapa sumber                      | Tampilkan dengan breakdown sumber                        |
| `partial`                    | Hanya sebagian komponen terhitung             | Tampilkan nilai yang ada + field null                    |
| `unavailable`                | Parameter wajib tidak ada sama sekali         | Tampilkan pesan "data belum tersedia"                    |
| `literature-reference-a02`   | Nilai fallback dari artikel A02 (MATCH_EXACT) | Badge "referensi literatur"                              |

---

## 7. Data Tersedia & Belum Tersedia

### Sudah Tersedia (Lokal)

| Parameter                | Nilai                                             | Status                |
| ------------------------ | ------------------------------------------------- | --------------------- |
| Harga beli bebek         | Rp 28.000/ekor                                    | local-estimate        |
| Harga jual bebek         | Rp 30.000/ekor (nilai bawah, range 30.000–60.000) | local-estimate        |
| Harga gabah konvensional | Rp 5.600/kg (Maret 2026)                          | local-estimate        |
| Biaya jaring             | Rp 1.350.000/200m                                 | local-estimate        |
| Biaya kandang            | Rp 600.000/unit                                   | local-estimate        |
| Biaya gulma              | Rp 6.000/are/siklus (nilai bawah)                 | local-estimate        |
| Harga pupuk (N/P/K)      | Rp 2.400/kg                                       | local-estimate        |
| HST masuk bebek          | 28 HST (range 21–30)                              | local-estimate        |
| HST heading              | 60 HST (range 40–65)                              | local-estimate        |
| Survival rate (λ)        | 0.67 (nilai atas, range 0.35–0.67)                | local-estimate (weak) |
| K_max Jajar Legowo       | 4.0 ekor/are                                      | local-estimate        |
| K_max Tegel              | 2.5 ekor/are                                      | local-estimate        |

### Belum Tersedia (Lokal) — Menggunakan Fallback

| Parameter                                 | Status            | Sumber Fallback                                            |
| ----------------------------------------- | ----------------- | ---------------------------------------------------------- |
| Konsumsi pakan `q_feed`                   | unavailable lokal | **0.10 kg/ekor/hari** dari literatur A02 (MATCH_EXACT)     |
| Penghematan pakan alami `kappa_feed_save` | unavailable lokal | **0.66** dari literatur A03 (derived from text)            |
| κ_N, κ_P, κ_K (hara kotoran)              | unavailable lokal | **0.049 / 0.072 / 0.032** dari literatur A02 (MATCH_EXACT) |

### Belum Tersedia — Tidak Ada Fallback (Output = `null`)

| Parameter                           | Dampak ke Output                                                    |
| ----------------------------------- | ------------------------------------------------------------------- |
| Harga gabah padi-bebek `p_gabah_RD` | `rice_revenue_rp = null`, `REY = null`, `net_profit_rp = null`      |
| Harga pakan `p_feed`                | `feed_cost_rp = null`, `net_profit_rp = null`                       |
| Yield baseline konvensional `x0`    | `conventional_rice_revenue_rp = null`, `delta_rice_value_rp = null` |
| Flux CH4 musiman                    | semua field emisi = `null`                                          |
| Flux N2O musiman                    | semua field emisi = `null`                                          |
| Biaya pemeliharaan infra            | `maintenance_cost_rp = 0` (placeholder, bukan klaim nol)            |
| Bobot bebek saat jual               | harga jual per-ekor flat, bukan berbasis bobot                      |

---

## 8. Penanganan Data Tidak Lengkap

Sistem menggunakan prinsip **"selalu aktif"**: output tetap dihitung dengan data terbaik yang tersedia,
disertai penanda status yang jelas.

### Field Penanda Status di Response

| Field                    | Lokasi                                 | Arti                                                                                         |
| ------------------------ | -------------------------------------- | -------------------------------------------------------------------------------------------- |
| `numeric_ready`          | `economics`, `environment`             | `true` = nilai numerik tersedia; `false` = masih null                                        |
| `formula_available`      | `economics`, `environment`             | `true` = rumus ada, tinggal menunggu data                                                    |
| `data_readiness`         | root response                          | ringkasan per modul: `ready / estimation_only / partial / literature-uncalibrated / missing` |
| `missing_parameters`     | setiap sub-objek                       | daftar nama parameter yang hilang                                                            |
| `sumber_data`            | `economics`, `environment`             | asal data: `local-calibrated / mixed / literature-uncalibrated`                              |
| `status_data`            | setiap sub-objek                       | status detail data yang digunakan                                                            |
| `calibration_note`       | `environment`, `optimality_assessment` | penjelasan kenapa output belum final                                                         |
| `q_feed_assumption_note` | `economics.actual`                     | penjelasan lengkap fallback q_feed                                                           |

### Ringkasan `data_readiness` per Modul

| Modul               | Status Saat Ini           |
| ------------------- | ------------------------- |
| `agronomy_ready`    | `ready`                   |
| `yield_ready`       | `estimation_only`         |
| `economics_ready`   | `partial`                 |
| `ecology_ready`     | `estimation_only`         |
| `environment_ready` | `literature-uncalibrated` |
| `overall_status`    | `partial`                 |

### Aturan Output Null

- `null` di field ekonomi (rice_revenue, net_profit, dll) → **bukan berarti nol** → tampilkan "belum tersedia"
- `null` di field emisi → **bukan berarti emisi nol** → tampilkan pesan kalibrasi
- `0` di `maintenance_cost_rp` → **placeholder**, bukan klaim biaya nol
- `formula_available: true` + `numeric_ready: false` → rumus ada, data belum lengkap

---

## 9. API & Endpoint

### Base URL

```
http://127.0.0.1:8000
```

Dokumentasi interaktif: `GET /docs` (Swagger UI) atau `GET /redoc`.

### Daftar Endpoint

| Method   | Path                         | Auth              | Deskripsi                        |
| -------- | ---------------------------- | ----------------- | -------------------------------- |
| `GET`    | `/health`                    | —                 | Health check                     |
| `POST`   | `/api/v1/auth/register`      | —                 | Daftar user baru                 |
| `POST`   | `/api/v1/auth/login`         | —                 | Login, dapat JWT token           |
| `GET`    | `/api/v1/auth/me`            | Bearer            | Info user aktif                  |
| `GET`    | `/api/v1/dss/options`        | —                 | Dropdown varietas & sistem tanam |
| `POST`   | `/api/v1/dss/simulate`       | Bearer (opsional) | Jalankan simulasi DSS            |
| `GET`    | `/api/v1/dss/histories`      | Bearer            | Daftar history simulasi user     |
| `GET`    | `/api/v1/dss/histories/{id}` | Bearer            | Detail history simulasi          |
| `DELETE` | `/api/v1/dss/histories/{id}` | Bearer            | Hapus history simulasi           |

> Endpoint `POST /api/v1/dss/simulate` dapat diakses tanpa token (simulasi tidak disimpan)
> atau dengan token Bearer JWT (simulasi disimpan ke history).

### Auth

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "name": "Pak Wayan",
  "email": "wayan@sawah.id",
  "password": "password123"
}
```

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "wayan@sawah.id",
  "password": "password123"
}
```

Response login:

```json
{
  "access_token": "<jwt_token>",
  "token_type": "bearer",
  "user": { "id": "...", "name": "Pak Wayan", "email": "wayan@sawah.id" }
}
```

### Dropdown Options

```http
GET /api/v1/dss/options
```

Response (ringkasan):

```json
{
  "rice_varieties": [
    {
      "code": "sertani",
      "label": "Sertani / Seratih",
      "hst_masuk": 28,
      "hst_heading": 60,
      "harvest_age_days": 105,
      "hst_masuk_range": { "min": 21, "max": 30 },
      "hst_heading_range": { "min": 40, "max": 65 },
      "status": "estimation"
    }
  ],
  "planting_systems": [
    {
      "code": "jajar_legowo",
      "label": "Jajar Legowo",
      "k_max_are": 4.0,
      "f_yield": 1.05,
      "k_max_range_are": { "min": 4.0, "max": 8.0 },
      "k_max_status": "local-estimate",
      "f_yield_status": "literature-uncalibrated"
    }
  ]
}
```

### Payload Simulasi

```http
POST /api/v1/dss/simulate
Content-Type: application/json
Authorization: Bearer <token>   (opsional)

{
  "duck_count": 28,
  "land_area_are": 7,
  "planting_date": "2026-06-01",
  "rice_variety": "sertani",
  "planting_system": "jajar_legowo",
  "duck_age_days": 30
}
```

---

## 10. Struktur Response Simulasi

Response `POST /api/v1/dss/simulate` memiliki struktur utama sebagai berikut:

```json
{
  "history_id": "uuid | null",
  "input": { ... },
  "lookup": { ... },
  "actual_scenario": { ... },
  "optimality_assessment": { ... },
  "recommended_scenario": "objek | null",
  "comparison": "objek | null",
  "risk": { ... },
  "economics": { ... },
  "ecology": { ... },
  "environment": { ... },
  "data_readiness": { ... },
  "validation": { ... },
  "trace": { ... },
  "notes": [ "..." ]
}
```

### `actual_scenario` — Kondisi Aktual Petani

Field penting untuk frontend:

| Field                                | Tipe        | Satuan          | Keterangan                             |
| ------------------------------------ | ----------- | --------------- | -------------------------------------- |
| `duck_count`                         | int         | ekor            | Jumlah bebek input                     |
| `land_area_are`                      | float       | **are**         | Luas lahan input                       |
| `density_are`                        | float       | ekor/are        | **Kepadatan utama**                    |
| `duration_days`                      | int         | hari            | Durasi bebek di sawah                  |
| `release_date`                       | date        | —               | Tanggal lepas bebek                    |
| `pull_date`                          | date        | —               | Tanggal tarik bebek                    |
| `surviving_ducks`                    | float       | ekor            | Perkiraan bebek bertahan               |
| `dung_total_per_duck_kg`             | float       | kg/ekor         | Kotoran per bebek                      |
| `dung_status`                        | string      | —               | `"estimation_only"`                    |
| `predicted_yield.kg_per_are`         | float       | **kg/are**      | **Yield utama untuk petani**           |
| `predicted_yield.estimated_total_kg` | float       | kg              | Total produksi gabah                   |
| `predicted_yield.kg_per_ha`          | float       | kg/ha           | Catatan konversi                       |
| `predicted_yield.ton_per_ha`         | float       | ton/ha          | Catatan konversi                       |
| `penalty_rate`                       | float       | 0–1             | Penalti kepadatan (0 = tidak ada)      |
| `risk_status`                        | string      | —               | `LOW / SAFE / WARNING / HIGH`          |
| `rey`                                | float\|null | kg setara gabah | REY; null jika harga belum ada         |
| `rey_status`                         | string      | —               | `"calculated"` atau `"missing_params"` |

### `recommended_scenario` — Rekomendasi Sistem

Muncul hanya jika `optimality_assessment.is_optimal = false`. Struktur mirip `actual_scenario`
dengan field tambahan:

| Field                       | Keterangan                                 |
| --------------------------- | ------------------------------------------ |
| `recommended_duck_count`    | Jumlah bebek yang direkomendasikan         |
| `recommended_density_are`   | Kepadatan rekomendasi (ekor/are)           |
| `recommended_duration_days` | Durasi yang direkomendasikan (hari)        |
| `reasoning_summary`         | Teks penjelasan singkat alasan rekomendasi |

### `optimality_assessment` — Apakah Kondisi Sudah Optimal?

| Field                       | Tipe        | Keterangan                                           |
| --------------------------- | ----------- | ---------------------------------------------------- |
| `is_optimal`                | bool        | `true` → kondisi sudah baik, tidak perlu rekomendasi |
| `score_safety`              | bool        | Semua constraint safety terpenuhi                    |
| `density_gap_ratio`         | float\|null | Selisih kepadatan aktual vs rekomendasi              |
| `delta_yield_pct`           | float\|null | Selisih yield dalam persen                           |
| `delta_profit_ratio`        | float\|null | Selisih profit; null jika data ekonomi parsial       |
| `optimality_basis`          | string      | `"safety+yield+profit"` atau `"safety+yield"`        |
| `profit_component_included` | bool        | `false` jika profit null — evaluasi parsial          |
| `profit_data_purity`        | string      | `local-calibrated / mixed / literature-uncalibrated` |
| `catatan_kalibrasi`         | string      | Penjelasan status kalibrasi ambang                   |

### `economics` — Ringkasan Ekonomi

```json
{
  "status": "partial",
  "actual": {
    "status": "partial",
    "status_data": "mixed",
    "rice_revenue_rp": null,
    "conventional_rice_revenue_rp": null,
    "duck_revenue_rp": 562800.0,
    "duck_purchase_cost_rp": 784000.0,
    "feed_cost_rp": null,
    "feed_cost_status": "unavailable",
    "duck_net_value_rp": null,
    "infrastructure": {
      "total_infrastructure_cost_rp": 875000.0,
      "net_cost_per_cycle_rp": 675000.0,
      "shelter_cost_per_cycle_rp": 200000.0,
      "maintenance_cost_rp": 0.0,
      "note": "Maintenance uses 0 only as an unavailable-data placeholder..."
    },
    "net_profit_rp": null,
    "net_profit_rp_per_are": null,
    "missing_parameters": ["rice_duck_price_rp_per_kg", "feed_price_rp_per_kg"],
    "sumber_data": "mixed",
    "formula_available": true,
    "numeric_ready": false,
    "q_feed_source": "literature-reference-a02",
    "q_feed_status": "literature-uncalibrated",
    "q_feed_assumption_note": "...",
    "v_duck_xiong_reference": 1234.56,
    "v_duck_xiong_status": "literature-uncalibrated"
  },
  "delta_profit_rp": null,
  "assumptions": ["..."]
}
```

### `ecology` — Manfaat Ekologis

```json
{
  "status": "estimation_only",
  "actual": {
    "status": "estimation_only",
    "fertilizer_saving_rp": 12345.0,
    "fertilizer_saving_status": "literature-uncalibrated",
    "pesticide_herbicide_saving_rp": 98.7,
    "pesticide_herbicide_saving_status": "literature-uncalibrated",
    "weed_reduction_rate": 1.0,
    "weeding_saving_rp": 42000.0,
    "weeding_saving_status": "local-estimate",
    "partial_ecological_value_rp": 54443.7,
    "included_components": ["v_eco1", "v_eco2", "v_gulma"],
    "soil_nutrients": {
      "status": "estimation_only",
      "n_kg_per_are": 0.0336,
      "p2o5_kg_per_are": 0.0494,
      "k2o_kg_per_are": 0.022,
      "n_kg_per_ha": 3.36,
      "missing_parameters": []
    }
  }
}
```

### `environment` — Emisi & Lingkungan

```json
{
  "status": "literature-uncalibrated",
  "actual": {
    "status": "literature-uncalibrated",
    "formula_available": true,
    "numeric_ready": false,
    "co2e_are": null,
    "f_ch4_are": null,
    "f_n2o_are": null,
    "ghgi": null,
    "ch4_reduction_pct": null,
    "calibration_note": "Modul emisi belum terkalibrasi lokal. F_CH4, F_N2O belum tersedia...",
    "missing_parameters": ["f_ch4_kg_per_ha_season", "f_n2o_kg_per_ha_season"]
  }
}
```

### `risk` — Ringkasan Risiko

| Field                     | Keterangan                                       |
| ------------------------- | ------------------------------------------------ |
| `actual_status`           | `LOW / SAFE / WARNING / HIGH`                    |
| `density_risk`            | Status risiko kepadatan                          |
| `phase_risk`              | `SAFE` atau `HIGH` (apakah melebihi HST heading) |
| `feed_warning`            | `LOW` atau `WARNING` (durasi/kepadatan berlebih) |
| `thresholds.safe_max_are` | Nilai K_max_are yang dipakai                     |

### `data_readiness` — Ringkasan Kesiapan Data

```json
{
  "agronomy_ready": "ready",
  "yield_ready": "estimation_only",
  "economics_ready": "partial",
  "ecology_ready": "estimation_only",
  "environment_ready": "literature-uncalibrated",
  "overall_status": "partial"
}
```

### `comparison` — Perbandingan Aktual vs Rekomendasi

Muncul hanya jika `optimality_assessment.is_optimal = false`.
Jika `optimality_assessment.is_optimal = true`, `recommended_scenario` dan `comparison` bernilai `null` (bukan error).

| Field                        | Keterangan                        |
| ---------------------------- | --------------------------------- |
| `duck_count_difference`      | Selisih jumlah bebek (int)        |
| `density_difference_are`     | Selisih kepadatan dalam are       |
| `yield_difference_kg_per_ha` | Selisih yield per ha (catatan)    |
| `yield_difference_total_kg`  | Selisih total yield dalam kg      |
| `risk_change`                | Deskripsi perubahan status risiko |
| `profit_difference_rp`       | Selisih laba; null jika parsial   |

---

## 11. Panduan Frontend

### Field Utama yang Ditampilkan ke User

Prioritaskan field berikut untuk tampilan utama (card/dashboard):

| Field                                                          | Sumber                  | Label Tampilan             |
| -------------------------------------------------------------- | ----------------------- | -------------------------- |
| `actual_scenario.predicted_yield.kg_per_are`                   | `actual_scenario`       | Estimasi Yield (kg/are)    |
| `actual_scenario.predicted_yield.estimated_total_kg`           | `actual_scenario`       | Total Produksi (kg)        |
| `actual_scenario.density_are`                                  | `actual_scenario`       | Kepadatan Bebek (ekor/are) |
| `actual_scenario.risk_status`                                  | `actual_scenario`       | Status Risiko              |
| `actual_scenario.release_date`                                 | `actual_scenario`       | Tanggal Lepas Bebek        |
| `actual_scenario.pull_date`                                    | `actual_scenario`       | Tanggal Tarik Bebek        |
| `actual_scenario.surviving_ducks`                              | `actual_scenario`       | Estimasi Bebek Bertahan    |
| `economics.actual.duck_revenue_rp`                             | `economics.actual`      | Pendapatan Bebek (Rp)      |
| `economics.actual.infrastructure.total_infrastructure_cost_rp` | `economics`             | Biaya Infrastruktur (Rp)   |
| `ecology.actual.weeding_saving_rp`                             | `ecology.actual`        | Penghematan Gulma (Rp)     |
| `ecology.actual.partial_ecological_value_rp`                   | `ecology.actual`        | Nilai Ekologis (Rp)        |
| `optimality_assessment.is_optimal`                             | `optimality_assessment` | Perlu Rekomendasi?         |

### Field yang Sebaiknya Hanya di Detail/Tooltip

Field-field ini informatif untuk researcher/developer, tetapi bisa membingungkan petani:

| Field                                     | Keterangan                                                   |
| ----------------------------------------- | ------------------------------------------------------------ |
| `actual_scenario.density_ha`              | Versi ha dari kepadatan (catatan internal)                   |
| `actual_scenario.x_base_kg_per_ha`        | Yield base sebelum penalti (catatan)                         |
| `actual_scenario.penalty_rate`            | Angka penalti kepadatan                                      |
| `actual_scenario.dung_total_per_duck_kg`  | Kotoran per bebek                                            |
| `economics.actual.v_duck_xiong_reference` | Nilai Xiong akademik (bukan profit operasional)              |
| `economics.actual.q_feed_assumption_note` | Catatan panjang fallback q_feed                              |
| `trace`                                   | Seluruh blok trace (untuk debug/audit)                       |
| `rey`                                     | REY (hanya jika frontend ingin tampilkan indikator akademik) |

### Menampilkan Badge Status Data

Gunakan field `status_data` atau `sumber_data` di setiap sub-modul:

```
"local-calibrated"         → Badge hijau: "Data Lokal"
"local-estimate"           → Badge kuning: "Estimasi Lokal"
"literature-uncalibrated"  → Badge oranye: "Referensi Literatur"
"mixed"                    → Badge abu: "Data Campuran"
"partial"                  → Badge merah muda: "Parsial"
```

Untuk modul environment, tampilkan selalu `calibration_note` sebagai tooltip/pesan info.

### Menampilkan Output Null atau Parsial

**Aturan wajib:**

| Kondisi                                            | Cara Tampilkan                                                                  |
| -------------------------------------------------- | ------------------------------------------------------------------------------- |
| `net_profit_rp = null`                             | "Laba bersih belum dapat dihitung. Data harga gabah/pakan belum tersedia."      |
| `rice_revenue_rp = null`                           | "Pendapatan padi belum dapat dihitung (harga gabah padi-bebek belum tersedia)." |
| `co2e_are = null`                                  | "Data emisi belum tersedia. Modul aktif, menunggu data flux lokal."             |
| `formula_available: true` + `numeric_ready: false` | Tampilkan ikon ⏳ dengan tooltip "Rumus tersedia, menunggu data"                |
| `maintenance_cost_rp = 0`                          | Jangan tampilkan "Rp 0". Gunakan teks "Belum tercatat" atau tooltip dari `note` |
| `rey = null`                                       | Sembunyikan atau tampilkan "Belum dapat dihitung"                               |

**Jangan:**

- Menampilkan `null` sebagai angka `0`
- Menampilkan `null` sebagai `-` tanpa keterangan
- Menampilkan `maintenance_cost_rp: 0` seolah biaya nol

### Membedakan Sumber Data di UI

Gunakan `q_feed_status` dan `sumber_data` untuk menentukan pola tampilan:

```
q_feed_status = "local-calibrated"        → tampilkan normal
q_feed_status = "literature-uncalibrated" → tambahkan catatan kecil:
                                            "* Biaya pakan dihitung dari referensi literatur,
                                             bukan data lokal Astungkara Way."
sumber_data = "mixed"                     → tampilkan: "Data campuran (lokal + referensi)"
```

### Menampilkan Rekomendasi

Frontend wajib mengecek `optimality_assessment.is_optimal` terlebih dahulu:

```
is_optimal = true  → tampilkan kartu/status "Kondisi sudah optimal / aman"
                     - jangan tampilkan blok recommended_scenario
                     - jangan tampilkan comparison
                     - tampilkan notes dari backend sebagai penjelasan
                     (recommended_scenario dan comparison bernilai null di response).

is_optimal = false → tampilkan blok rekomendasi lengkap:
                     recommended_scenario + comparison + reasoning_summary
```

Jika `profit_component_included = false`:

```
Tambahkan catatan: "Evaluasi optimalitas berjalan tanpa komponen profit
karena data harga belum lengkap."
```

### Risk Badge

```
risk_status = "LOW"     → biru: "Kepadatan terlalu rendah"
risk_status = "SAFE"    → hijau: "Kepadatan aman"
risk_status = "WARNING" → kuning: "Di atas kapasitas, perhatikan pakan"
risk_status = "HIGH"    → merah: "Risiko tinggi, kurangi jumlah bebek"
```

---

## 12. Contoh Simulasi

### Skenario: 28 Bebek, 7 Are, Jajar Legowo, Sertani

**Input:**

```json
{
  "duck_count": 28,
  "land_area_are": 7,
  "planting_date": "2026-06-01",
  "rice_variety": "sertani",
  "planting_system": "jajar_legowo",
  "duck_age_days": 30
}
```

**Kalkulasi kunci:**

| Langkah        | Nilai                                    |
| -------------- | ---------------------------------------- |
| Kepadatan      | 28 / 7 = **4.0 ekor/are** = K_max → SAFE |
| Durasi         | 60 - 28 = **32 hari**                    |
| Tanggal lepas  | 2026-06-01 + 28 hari = 2026-06-29        |
| Tanggal tarik  | 2026-06-01 + 60 hari = 2026-07-31        |
| Survival bebek | 28 × 0.67 = **18.76 ekor**               |
| Kotoran/bebek  | (32/50) × 4 = **2.56 kg**                |
| Durasi efektif | 32 × (10/12) = **26.67 hari**            |
| x_base (Xiong) | ≈ 5.825 kg/ha → **58.25 kg/are**         |
| Penalti rate   | 0 (kepadatan tepat di K_max)             |
| x_final_kg_are | 1.0 × 58.25 × 1.05 = **≈ 61.16 kg/are**  |
| Total yield    | 61.16 × 7 = **≈ 428 kg**                 |

**Nilai ekologis:**

| Komponen                    | Nilai                                            |
| --------------------------- | ------------------------------------------------ |
| Hara N tanah                | 0.049 × (2.56/10) × 4 × 0.67 = **0.0336 kg/are** |
| Hara P tanah                | **0.0494 kg/are**                                |
| Hara K tanah                | **0.0220 kg/are**                                |
| Penghematan gulma (V_gulma) | 6.000 × 7 × 1.0 = **Rp 42.000**                  |
| V_eco1                      | > 0 (t=32 > 30, rumus positif)                   |

**Ekonomi (skenario saat ini — parsial):**

| Komponen            | Nilai                           | Status                       |
| ------------------- | ------------------------------- | ---------------------------- |
| Pendapatan bebek    | 18.76 × 30.000 = **Rp 562.800** | Tersedia                     |
| Biaya beli bebek    | 28 × 28.000 = **Rp 784.000**    | Tersedia                     |
| Biaya pakan         | null (`p_feed` belum ada)       | Belum tersedia               |
| Pendapatan padi     | null (`p_gabah_RD` belum ada)   | Belum tersedia               |
| Biaya infrastruktur | **Rp 875.000**                  | Tersedia                     |
| Laba bersih         | **null**                        | Menunggu harga pakan & gabah |

**Status risk:** SAFE — kepadatan tepat di K_max, durasi dalam batas.

---

### Skenario: Kepadatan Berlebih (Contoh Penalti)

**Input:** 35 bebek, 7 are → kepadatan = 5.0 ekor/are (> K_max 4.0)

| Kalkulasi    | Nilai                                             |
| ------------ | ------------------------------------------------- |
| Kepadatan    | 5.0 ekor/are → **WARNING**                        |
| Penalti rate | min(1.0, 0.5 × (5.0-4.0)/4.0) = **0.125** (12.5%) |
| x_final      | dikurangi 12.5% dari x_penalized                  |
| risk_status  | WARNING                                           |

---

## 13. Batasan & Catatan Kalibrasi

### Batasan Model Saat Ini

1. **α_local = 1.0** — faktor kalibrasi lokal belum tersedia. Yield model dijalankan dengan
   default netral. Setelah 3–5 siklus panen lokal Astungkara Way tersedia, nilai ini harus dikalibrasi.

2. **Survival rate (λ = 0.67)** — ini nilai **atas** dari range data lokal (0.35–0.67),
   bukan rata-rata. Bersifat indicative/weak. Estimasi pendapatan bebek bisa terlalu optimistis.

3. **q_feed dari literatur** — konsumsi pakan harian menggunakan fallback 0.10 kg/ekor/hari
   dari artikel A02. Nilai ini bukan data lapangan Astungkara Way. Jika nilai lokal berbeda,
   biaya pakan dan laba bersih akan berubah signifikan.

4. **Emisi belum terkalibrasi** — flux CH4 dan N2O lokal (kg/ha/musim) belum tersedia.
   Klaim pengurangan emisi padi-bebek vs konvensional belum bisa dibuat secara kuantitatif.

5. **Ambang optimalitas heuristik** — threshold density_gap 15%, delta_yield 5%, delta_profit 10%
   adalah nilai engineering murni. Belum ada data atau literatur yang mendasari angka ini secara
   eksplisit untuk konteks lokal. **Wajib direvisi** setelah α_local dikalibrasi.

6. **K_max dan f_yield** — nilai K_max (Jarwo: 4.0, Tegel: 2.5) dan f_yield (Jarwo: 1.05, Tegel: 1.0)
   adalah estimasi lokal dan nilai literatur. Belum dikalibrasi kuat dari multi-siklus lapangan.

7. **Harga berbatas waktu** — `p_gabah_konv = Rp 5.600/kg` berlaku untuk periode Maret 2026.
   Jangan digunakan sebagai harga "selalu berlaku".

8. **Model tidak memodelkan** variasi cuaca, irigasi, jenis tanah, atau kondisi kesehatan bebek
   secara eksplisit.

### Kalibrasi yang Dibutuhkan

| Parameter          | Kebutuhan Kalibrasi                                   |
| ------------------ | ----------------------------------------------------- |
| `α_local`          | 3–5 data panen lokal (yield aktual vs prediksi model) |
| `λ` (survival)     | Rata-rata dari minimal 3 siklus pemeliharaan bebek    |
| `q_feed`           | Pengukuran langsung konsumsi pakan harian per ekor    |
| `kappa_feed_save`  | Uji lapangan berapa % pakan tersubstitusi dari alam   |
| `κ_N/P/K`          | Uji laboratorium kotoran bebek lokal                  |
| `F_CH4`, `F_N2O`   | Pengukuran flux gas musiman di sawah lokal            |
| `K_max_are`        | Observasi multi-siklus titik jenuh produktivitas      |
| Ambang optimalitas | Dikalibrasi setelah α_local tersedia                  |

---

## 14. Cara Menjalankan

### Prasyarat

- Python 3.12+
- `pip` atau package manager Python lainnya

### Instalasi

```bash
# Clone atau masuk ke direktori project
cd rice-duck-be

# Buat virtual environment
python -m venv .venv

# Aktifkan virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependensi
pip install -r requirements.txt
```

### Konfigurasi Environment

Salin `.env.example` menjadi `.env` dan sesuaikan jika perlu:

```bash
copy .env.example .env
```

Variabel yang bisa dikonfigurasi (nilai default sudah berfungsi untuk development):

```ini
APP_ENV=development
APP_DEBUG=true
DATABASE_PATH=data/rice_duck.db
CORS_ALLOWED_ORIGINS=*
JWT_SECRET_KEY=<ganti-untuk-production>
JWT_ACCESS_TOKEN_MINUTES=120
```

### Menjalankan Server

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Server berjalan di `http://127.0.0.1:8000`.
Dokumentasi API: `http://127.0.0.1:8000/docs`

### Menjalankan Test

```bash
# Semua test
pytest

# Test spesifik dengan output verbose
pytest tests/test_formula_engine.py -v

# Test API end-to-end
pytest tests/test_api.py -v
```

Test database otomatis menggunakan `tests/rice_duck_test.db` (terpisah dari database utama).

### Struktur Direktori Penting

```
app/
├── api/routes/         # Endpoint FastAPI (auth.py, dss.py, health.py)
├── core/               # Config, database, security, exceptions
├── data/seed.py        # Konstanta, varietas, sistem tanam, metadata parameter
├── domain/models.py    # Dataclass domain (RiceVariety, PlantingSystem, DSSConstants)
├── engines/
│   ├── formula_engine.py   # Rumus agronomi, yield, kalender
│   └── impact_engine.py    # Ekonomi, ekologi, emisi, infrastruktur
├── repositories/       # Akses data (lookup, history, user)
├── schemas/dss.py      # Request/response schema Pydantic
└── services/simulation_service.py  # Orkestrasi simulasi end-to-end

tests/
├── conftest.py             # Setup test database
├── test_formula_engine.py  # Unit test rumus dan engine
├── test_api.py             # Integration test endpoint
└── test_audit_fixes.py     # Regression test untuk audit Rev 1 & Rev 2

data/
└── rice_duck.db            # Database SQLite (dibuat otomatis)
```

---

## Catatan Versi

**Rev 2 (aktif):** Satuan utama berubah dari ha ke **are** di semua output ke pengguna.
`x_final_kg_are` = output yield utama. `d_aktual_are` = kepadatan utama. Hektar hanya catatan
internal untuk kompatibilitas rumus Xiong berbasis literatur.

**Rev 1:** Filosofi "selalu aktif" — tidak ada modul yang di-disabled. Fallback q_feed ke literatur.
`calibration_note` wajib ada di semua output yang belum terkalibrasi. `net_profit_rp` null hanya
jika `p_feed` atau `p_gabah_RD` benar-benar tidak tersedia.

---

_Dokumentasi ini mencerminkan kondisi sistem per Rev 2. Status kalibrasi dan ketersediaan data
akan diperbarui seiring pengumpulan data lapangan Astungkara Way._
