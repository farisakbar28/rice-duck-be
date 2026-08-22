# Numerical Validation DSS Padi-Bebek

## 1. Tujuan dan Ruang Lingkup

Dokumen ini memuat pengujian numerik terhadap komponen DSS Padi-Bebek yang memiliki ground truth lokal yang kompatibel. Pengujian hanya dilakukan pada endpoint yang dapat dibandingkan secara sah dengan data aktual. Komponen yang tidak mempunyai ground truth kompatibel tidak dipaksakan menjadi validasi numerik dan dijelaskan secara terpisah.

## 2. Basis Data Validasi

- Rekap sumber: **44 siklus**.
- Siklus clean: **36**.
- Siklus excluded: **8**.
- Petani unik pada clean set: **19**.

Sumber internal digunakan berdasarkan hierarki evidence penelitian: expert judgement terbaru, diskusi lanjutan, data collection awal, rekap mentah primer, dataset clean, dan literatur pendukung.

### 2.1 Eligibility guardrails

1. Hanya siklus yang termasuk clean set yang digunakan sebagai kandidat numerical validation.
2. Ground truth endpoint harus berasal dari observation aktual, bukan default, placeholder, atau imputasi.
3. Field default atau imputasi tidak diperlakukan sebagai ground truth.
4. Seluruh input yang diperlukan oleh endpoint yang diuji harus tersedia.
5. Field yang berasal dari formula spreadsheet error tidak digunakan.
6. Data petani yang sama tidak boleh berada sekaligus pada calibration dan validation fold untuk pengujian Yield Engine.
7. Row tidak boleh dipilih atau dibuang setelah melihat besar error model.
8. Jumlah observation mengikuti jumlah data valid yang tersedia; tidak dipaksakan menjadi jumlah tertentu.

### 2.2 Audit formula spreadsheet

Audit rekap mentah menemukan **78 sel `#NAME?`**: 64 berada pada row yang kemudian masuk clean set dan 14 pada row excluded.

Error tersebut terbatas pada field `Pre-paid amount Loss` dan `Pre-paid amount Loss/are` yang menggunakan formula `_xludf.IFS`. Kedua field tersebut tidak digunakan oleh endpoint numerical validation pada dokumen ini.

## 3. Yield Engine yang Diuji

Baseline production yang diuji adalah **47.8767507 kg/are**.

```text
Y_base             = 47.8767507 kg/are
F_sys_Tegel        = 1
F_sys_Jarwo_2_1    = 1
F_var_Sertani      = 1
F_var_Inpari       = 1

Yield_are_pred     = 47.8767507
Yield_total_pred   = 47.8767507 * A_are
```

Tidak terdapat multiplier numerik berdasarkan umur bebek, kepadatan bebek, varietas, atau sistem tanam pada Yield Engine. Density dan planting system tetap digunakan untuk klasifikasi boundary dan risk semantics.

## 4. Audit Struktur Yield Engine

Sebelum pengujian final, beberapa struktur yield dibandingkan pada **26 observasi yang mempunyai sistem tanam eksplisit** agar seluruh kandidat dievaluasi pada evaluation set yang sama.

| Struktur | MAE | RMSE | MedAE |
|---|---:|---:|---:|
| System-neutral; training seluruh clean set di luar farmer holdout | 11.3957 | 14.9313 | 8.7043 |
| System-neutral; training hanya explicit-system rows | 11.4310 | 14.6890 | 8.1586 |
| Local system-specific | 13.0187 | 15.8047 | 11.5642 |
| Hybrid local + literature-relative | 13.0288 | 16.1411 | 10.5052 |

Pada evaluation set yang sama, struktur system-neutral menghasilkan error lebih rendah daripada struktur system-specific dan hybrid literature-relative. Karena itu numerical validation final menggunakan baseline lokal system-neutral.

## 5. Metode Pengujian Yield

Yield Engine diuji menggunakan **Leave-One-Farmer-Out Cross-Validation (LOFO-CV)**.

Pada setiap fold:

1. Seluruh siklus milik satu petani dikeluarkan dari calibration set.
2. Median yield dihitung ulang hanya dari petani lain.
3. Median training digunakan untuk memprediksi seluruh siklus milik petani yang dikeluarkan.
4. Proses diulang sampai seluruh petani pernah menjadi validation fold.
5. Residual seluruh fold digabungkan untuk menghitung metrik final.

Metrik:

```text
e_i   = Yield_pred_i - Yield_actual_i
MAE   = mean(abs(e_i))
RMSE  = sqrt(mean(e_i^2))
MedAE = median(abs(e_i))
```

## 6. Hasil LOFO-CV Yield

- Observation: **36**
- Farmer fold: **19**
- Median baseline production: **47.8767507 kg/are**
- Mean actual yield: **47.0045 kg/are**
- Range actual yield: **7.5362–65.7292 kg/are**
- **MAE = 10.1151 kg/are**
- **RMSE = 13.4146 kg/are**
- **MedAE = 8.4625 kg/are**

### 6.1 Ringkasan per farmer fold

| Farmer | n test | n train | Median training | MAE | RMSE | MedAE |
|---|---:|---:|---:|---:|---:|---:|
| Alm. I Ketut Tantra | 1 | 35 | 48.0392 | 40.5030 | 40.5030 | 40.5030 |
| I Gusti Ngurah Putu Suka Nada | 1 | 35 | 48.0392 | 34.5392 | 34.5392 | 34.5392 |
| I Gusti Ngurah Rai Sukarta | 4 | 32 | 47.4556 | 3.6813 | 4.3452 | 4.0898 |
| I Gusti Nyoman Ngurah Wirasuta | 2 | 34 | 47.8768 | 7.4803 | 9.2436 | 7.4803 |
| I Ketut Alit Sudarsana | 4 | 32 | 47.4556 | 8.1919 | 8.7716 | 7.3750 |
| I Ketut Buda | 1 | 35 | 48.0392 | 14.2920 | 14.2920 | 14.2920 |
| I Ketut Tantra | 2 | 34 | 47.4556 | 5.4333 | 6.1535 | 5.4333 |
| I Made Arsania | 2 | 34 | 49.0196 | 5.8946 | 6.4870 | 5.8946 |
| I Made Suardika | 1 | 35 | 48.0392 | 11.5671 | 11.5671 | 11.5671 |
| I Made Widana | 2 | 34 | 49.0196 | 2.4577 | 2.7145 | 2.4577 |
| I Nyoman Ranes | 2 | 34 | 48.8571 | 14.3277 | 19.6926 | 14.3277 |
| I Nyoman Suwitra | 1 | 35 | 48.0392 | 7.9350 | 7.9350 | 7.9350 |
| I Wayan Arta Susila | 1 | 35 | 48.0392 | 10.0110 | 10.0110 | 10.0110 |
| I Wayan Buana | 1 | 35 | 48.0392 | 7.8365 | 7.8365 | 7.8365 |
| I Wayan Jana | 1 | 35 | 47.7143 | 15.1746 | 15.1746 | 15.1746 |
| I Wayan Sadia | 1 | 35 | 47.7143 | 11.6521 | 11.6521 | 11.6521 |
| I Wayan Suarta | 3 | 33 | 47.7143 | 7.3276 | 9.8205 | 5.3160 |
| I Wayan Suwendhi Artha | 4 | 32 | 47.4556 | 11.7896 | 12.8454 | 12.4402 |
| I Wayan Wiratna | 2 | 34 | 47.8768 | 11.4062 | 11.4526 | 11.4062 |

### 6.2 Error per observation

| Raw row | Farmer | Sistem | Varietas | A_are | J | d | Actual | Pred | Error | Abs Error |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 4 | I Wayan Suarta | Null(default Jarwo 2:1) | Sertani 13 | 6.60 | 30 | 4.5455 | 53.0303 | 47.7143 | -5.3160 | 5.3160 |
| 5 | I Made Widana | Null(default Jarwo 2:1) | Sertani 13 | 10.50 | 28 | 2.6667 | 47.7143 | 49.0196 | 1.3053 | 1.3053 |
| 6 | I Wayan Suwendhi Artha | Null(default Jarwo 2:1) | Sertani 13 | 4.80 | 10 | 2.0833 | 59.3750 | 47.4556 | -11.9194 | 11.9194 |
| 7 | I Ketut Tantra | Null(default Jarwo 2:1) | Sertani 13 | 4.50 | 16 | 3.5556 | 50.0000 | 47.4556 | -2.5444 | 2.5444 |
| 8 | I Made Arsania | Null(default Jarwo 2:1) | Sertani 13 | 3.60 | 13 | 3.6111 | 45.8333 | 49.0196 | 3.1863 | 3.1863 |
| 9 | I Nyoman Ranes | Null(default Jarwo 2:1) | Sertani 13 | 5.10 | 5 | 0.9804 | 48.0392 | 48.8571 | 0.8179 | 0.8179 |
| 10 | I Wayan Wiratna | Null(default Jarwo 2:1) | Sertani 13 | 3.20 | 10 | 3.1250 | 60.3125 | 47.8768 | -12.4357 | 12.4357 |
| 11 | I Ketut Alit Sudarsana | Null(default Jarwo 2:1) | Sertani 13 | 10.00 | 65 | 6.5000 | 60.5000 | 47.4556 | -13.0444 | 13.0444 |
| 12 | I Gusti Ngurah Rai Sukarta | Null(default Jarwo 2:1) | Sertani 13 | 5.50 | 40 | 7.2727 | 53.0909 | 47.4556 | -5.6353 | 5.6353 |
| 14 | I Wayan Sadia | Null(default Jarwo 2:1) | Sertani | 7.26 | 9 | 1.2397 | 59.3664 | 47.7143 | -11.6521 | 11.6521 |
| 18 | I Wayan Suarta | Jarwo 2:1 | Sertani | 6.60 | 30 | 4.5455 | 63.8636 | 47.7143 | -16.1494 | 16.1494 |
| 19 | I Made Widana | Jarwo 2:1 | Sertani | 10.50 | 28 | 2.6667 | 45.4095 | 49.0196 | 3.6101 | 3.6101 |
| 20 | I Wayan Suwendhi Artha | Jarwo 2:1 | Sertani | 4.80 | 8 | 1.6667 | 65.7292 | 47.4556 | -18.2735 | 18.2735 |
| 21 | I Ketut Tantra | Jarwo 2:1 | Inpari | 4.50 | 10 | 2.2222 | 55.7778 | 47.4556 | -8.3222 | 8.3222 |
| 23 | I Nyoman Ranes | Jarwo 2:1 | Inpari  | 5.10 | 10 | 1.9608 | 21.0196 | 48.8571 | 27.8375 | 27.8375 |
| 24 | I Wayan Wiratna | Jarwo 2:1 | Sertani | 3.20 | 3 | 0.9375 | 37.5000 | 47.8768 | 10.3768 | 10.3768 |
| 25 | I Ketut Alit Sudarsana | Jarwo 2:1 | Sertani | 14.41 | 30 | 2.0819 | 52.4289 | 47.4556 | -4.9732 | 4.9732 |
| 26 | I Gusti Ngurah Rai Sukarta | Jarwo 2:1 | Sertani | 5.50 | 50 | 9.0909 | 53.5455 | 47.4556 | -6.0898 | 6.0898 |
| 28 | I Gusti Nyoman Ngurah Wirasuta | Jarwo 2:1 | Sertani | 6.35 | 20 | 3.1496 | 45.8268 | 47.8768 | 2.0500 | 2.0500 |
| 34 | I Gusti Ngurah Rai Sukarta | Jarwo 2:1 | Sertani | 10.21 | 32 | 3.1342 | 50.0000 | 47.4556 | -2.5444 | 2.5444 |
| 36 | I Wayan Suarta | Tegel | Inpari | 6.60 | 19 | 2.8788 | 47.1970 | 47.7143 | 0.5173 | 0.5173 |
| 37 | I Wayan Suwendhi Artha | Tegel | Sertani a 13 | 4.80 | 9 | 1.8750 | 60.4167 | 47.4556 | -12.9610 | 12.9610 |
| 38 | I Ketut Alit Sudarsana | Jarwo 2:1 | Sertani | 10.00 | 32 | 3.2000 | 53.4000 | 47.4556 | -5.9444 | 5.9444 |
| 39 | I Gusti Ngurah Rai Sukarta | Jarwo 2:1 | Sertani | 5.50 | 18 | 3.2727 | 47.0000 | 47.4556 | 0.4556 | 0.4556 |
| 41 | I Gusti Nyoman Ngurah Wirasuta | Tegel | Inpari 32 | 6.35 | 5 | 0.7874 | 60.7874 | 47.8768 | -12.9107 | 12.9107 |
| 43 | I Made Arsania | Jarwo 2:1 | Sertani | 3.60 | 15 | 4.1667 | 40.4167 | 49.0196 | 8.6029 | 8.6029 |
| 44 | I Ketut Alit Sudarsana | Tegel | Inpari | 10.00 | 29 | 2.9000 | 38.6500 | 47.4556 | 8.8056 | 8.8056 |
| 46 | I Wayan Jana | Jarwo 2:1 | Sertani | 4.50 | 9 | 2.0000 | 62.8889 | 47.7143 | -15.1746 | 15.1746 |
| 47 | I Gusti Ngurah Putu Suka Nada | Jarwo 2:1 | Sertani | 3.00 | 6 | 2.0000 | 13.5000 | 48.0392 | 34.5392 | 34.5392 |
| 49 | I Wayan Arta Susila | Jarwo 2:1 | Sertani | 3.55 | 7 | 1.9718 | 38.0282 | 48.0392 | 10.0110 | 10.0110 |
| 51 | I Wayan Suwendhi Artha | Jarwo 2:1 | Sertani | 4.81 | 10 | 2.0790 | 43.4511 | 47.4556 | 4.0045 | 4.0045 |
| 53 | I Nyoman Suwitra | Jarwo 2:1 | Sertani | 4.80 | 10 | 2.0833 | 40.1042 | 48.0392 | 7.9350 | 7.9350 |
| 55 | Alm. I Ketut Tantra | Jarwo 2:1 | Sertani | 3.45 | 7 | 2.0290 | 7.5362 | 48.0392 | 40.5030 | 40.5030 |
| 60 | I Wayan Buana | Jarwo 2:1 | Sertani | 4.44 | 9 | 2.0270 | 40.2027 | 48.0392 | 7.8365 | 7.8365 |
| 61 | I Ketut Buda | Jarwo 2:1 | Sertani | 4.43 | 9 | 2.0316 | 33.7472 | 48.0392 | 14.2920 | 14.2920 |
| 62 | I Made Suardika | Jarwo 2:1 | Sertani | 3.77 | 8 | 2.1220 | 36.4721 | 48.0392 | 11.5671 | 11.5671 |

Tidak ada observation yang dihapus karena menghasilkan error tinggi.

## 7. Calendar Diagnostics

Calendar diagnostic hanya menggunakan clean cycle dengan **tanggal tanam dan tanggal panen aktual**.

### 7.1 Observation langsung

| Raw row | Farmer | Varietas | Sistem | Tanggal tanam | Tanggal panen | HST observed |
|---:|---|---|---|---|---|---:|
| 28 | I Gusti Nyoman Ngurah Wirasuta | Sertani | Jarwo 2:1 | 2024-02-19 | 2024-05-22 | 93 |
| 34 | I Gusti Ngurah Rai Sukarta | Sertani | Jarwo 2:1 | 2024-04-15 | 2024-07-19 | 95 |
| 36 | I Wayan Suarta | Inpari | Tegel | 2024-04-12 | 2024-08-06 | 116 |
| 37 | I Wayan Suwendhi Artha | Sertani a 13 | Tegel | 2024-04-23 | 2024-07-31 | 99 |
| 38 | I Ketut Alit Sudarsana | Sertani | Jarwo 2:1 | 2024-04-22 | 2024-07-31 | 100 |
| 39 | I Gusti Ngurah Rai Sukarta | Sertani | Jarwo 2:1 | 2024-04-15 | 2024-07-19 | 95 |
| 41 | I Gusti Nyoman Ngurah Wirasuta | Inpari 32 | Tegel | 2024-07-17 | 2024-11-03 | 109 |
| 43 | I Made Arsania | Sertani | Jarwo 2:1 | 2024-10-01 | 2025-01-17 | 108 |
| 44 | I Ketut Alit Sudarsana | Inpari | Tegel | 2024-09-28 | 2025-01-18 | 112 |
| 51 | I Wayan Suwendhi Artha (Data collection, level 4) | Sertani | Jarwo 2:1 | 2025-04-09 | 2025-07-19 | 101 |
| 53 | I Nyoman Suwitra  (Data collection, level 6) | Sertani | Jarwo 2:1 | 2025-04-09 | 2025-07-19 | 101 |
| 55 | Alm. I Ketut Tantra (Data collection, level 7) | Sertani | Jarwo 2:1 | 2025-04-19 | 2025-07-23 | 95 |

### 7.2 Sertani

Reference model: **100–110 HST**.

Observed n = **9**: 93, 95, 99, 100, 95, 108, 101, 101, 95.

Observation di dalam window 100–110 HST: **4/9**.

- MAE distance-to-window: **2.5556 hari**
- RMSE distance-to-window: **3.7268 hari**
- MedAE distance-to-window: **1.0000 hari**

Distance-to-window bernilai 0 jika HST aktual berada di dalam rentang 100–110. Metrik ini bersifat diagnostic karena output Sertani adalah window, bukan satu point estimate.

### 7.3 Inpari

Reference model: **134 HST** dengan status generic estimate.

Observed n = **3**: 116, 109, 112.

- MAE terhadap 134: **21.6667 hari**
- RMSE terhadap 134: **21.8556 hari**
- MedAE terhadap 134: **22.0000 hari**

Seluruh observation Inpari lokal pada subset ini berada di bawah 134 HST. Hasil tersebut dicatat sebagai limitation diagnostic dan tidak digunakan untuk mengganti parameter tanpa keputusan penelitian baru.

## 8. Descriptive Numerical Checks untuk Parameter Ekonomi

### 8.1 Harga gabah

- n: **36**
- median: **Rp6.000/kg**
- range: **Rp6.000–Rp7.500/kg**
- distribusi: Rp6.000: 21, Rp6.200: 1, Rp6.300: 5, Rp7.500: 9

Nilai production Rp6.000/kg sesuai dengan median lokal clean set.

### 8.2 Harga beli bebek

- positive records: **29**
- median positive: **Rp25.000/ekor**
- zero records: **4**
- null records: **3**

Pada production model, `p_duck_buy` merupakan input wajib dan nilai `0` diperbolehkan bila tidak ada current-cycle cash purchase. Median Rp25.000 berfungsi sebagai reference lokal, bukan hardcoded fallback.

### 8.3 Harga jual bebek

- historical positive price records: **15**
- historical median: **Rp35.000/ekor**
- historical range: **Rp26.000–Rp60.000/ekor**

Nilai production Rp52.500/ekor berasal dari expert-derived operational reference dan tidak diperlakukan sebagai direct numerical fit terhadap median historis.

### 8.4 Feed

- positive feed-cost records: **23**
- historical median feed cost per duck: **Rp5.000/ekor/siklus**
- historical range: **Rp1.000–Rp100.508/ekor/siklus**

Nilai production Rp20.000/ekor/siklus tetap diperlakukan sebagai expert-supported simplified default karena praktik dan pencatatan feed historis tidak terstandardisasi.

## 9. Endpoint yang Tidak Memiliki Ground Truth Numerik Kompatibel

| Endpoint | Status | Alasan |
|---|---|---|
| Age readiness | Tidak diuji numerik | Umur bebek aktual saat masuk tidak tersedia sebagai observation per cycle. |
| HST masuk/keluar bebek | Tidak diuji numerik | Tanggal/HST aktual pelepasan dan penarikan bebek tidak tersedia secara konsisten. |
| Survival biologis | Tidak diuji numerik | `N_sold_actual` tidak identik dengan `N_survive_actual`; bebek hidup dapat tidak dijual. |
| Revenue bebek potential | Tidak diuji sebagai realized outcome | Model menghitung potensi revenue dari survivor, sedangkan keputusan penjualan aktual berada di luar scope. |
| Net_Cash_Contribution_DSS | Tidak diuji terhadap raw profit | Tidak tersedia historical endpoint dengan semantic identik terhadap partial cash contribution DSS. |
| Weeding | Sandbox | Frekuensi kegiatan dan cash-out aktual tidak cukup seragam untuk core numerical validation. |
| Pesticide | Sandbox | 80% merupakan upper-bound nonmonetary indicator, bukan realized cash saving. |
| Fertilizer | Sandbox | Magnitude substitution belum terkalibrasi lokal. |
| Infrastructure | Reference only | Tidak mempunyai production formula final yang memerlukan numerical fit. |

## 10. Density dan Survival Checks

Density dihitung langsung sebagai:

```text
d    = J / A_are
d_ha = 100 * d
```

Boundary:

```text
d < 2                                  -> UNDER_DENSITY
Jarwo 2:1, 2 <= d <= 4                -> RECOMMENDED
Tegel, 2 <= d <= 3                    -> RECOMMENDED
di atas ceiling sistem dan d <= 8     -> ABOVE_RECOMMENDED
d > 8                                  -> OVERLOAD_HIGH_RISK
```

Survival semantics:

```text
N_survive = J                    jika d <= 8
N_survive = floor(0.60 * J)      jika d > 8
N_sold_DSS := N_survive
```

Formula survival tersebut tidak dibandingkan dengan `N_sold_actual` sebagai biological ground truth karena kedua konsep tersebut tidak identik.

## 11. Interpretasi

1. Yield baseline merupakan **empirical local central estimate**, bukan causal agronomic equation.
2. LOFO-CV mengurangi farmer leakage dengan memisahkan seluruh siklus seorang petani dari calibration fold ketika petani tersebut menjadi validation fold.
3. Error tinggi pada observation tertentu tetap dilaporkan dan tidak dijadikan alasan post-hoc exclusion.
4. Model tidak mengklaim generalisasi numerik di luar konteks lokal tanpa validasi tambahan.
5. Production input menerima `A_are > 0`, tetapi local numerical validation hanya dibangun dari clean set dengan `A_are >= 2.5`; prediksi di bawah 2.5 are berada di luar domain local numerical validation.
6. MAPE tidak digunakan sebagai primary metric karena yield aktual yang sangat rendah dapat mendistorsi percentage error. R² juga tidak digunakan sebagai primary metric untuk central-estimate baseline.
