# PANDUAN PENGUJIAN SKENARIO — BACKEND FINAL DSS PADI-BEBEK

> **STATUS SETELAH KOREKSI KALENDER INPARI:** Rule Inpari berubah dari point estimate 134 HST menjadi local empirical window 109–116 HST. Semua runtime evidence lama yang memuat output Inpari 134 HST (minimal H03, H08, B14, serta ringkasan terkait calendar) **tidak boleh digunakan sebagai evidence model terbaru** dan wajib dijalankan ulang setelah implementasi model diperbarui. Nilai baru tidak boleh diisi melalui kalkulasi manual.


## 1. Tujuan

Dokumen ini memverifikasi implementasi backend melalui **dua jenis pengujian yang dipisahkan secara tegas**:

1. **Historical Replay / Aktual vs Sistem** — baris aktual yang mempunyai input mandatory yang cukup dikirim ulang ke backend nyata, kemudian output backend dibandingkan dengan ground truth aktual yang semantik-kompatibel.
2. **Synthetic Contract & Boundary Test** — input buatan digunakan hanya untuk menguji boundary, validation contract, dan branch yang tidak mempunyai padanan aktual memadai.

Dokumen ini bukan pengganti dokumen numerical validation penelitian. Numerical validation penelitian tetap memakai protokol LOFO-CV yang telah ditetapkan. Historical Replay di sini berfungsi memastikan **backend yang sudah diimplementasikan** menghasilkan output yang dapat dibandingkan kembali terhadap observasi aktual melalui jalur HTTP nyata.

---

## 2. Aturan Mutlak

1. Backend harus dijalankan sebagai service nyata.
2. Setiap skenario harus dikirim melalui endpoint HTTP yang digunakan aplikasi.
3. Raw request, HTTP status, dan raw JSON response wajib disimpan.
4. Jangan mengisi nilai backend sebelum request benar-benar dijalankan.
5. Jangan mengganti raw backend response dengan kalkulasi manual dari formula.
6. Historical Replay hanya boleh memakai nilai sumber aktual untuk field yang tersedia.
7. Jika mandatory input historis tidak tersedia, baris tersebut tidak boleh dimasukkan ke Historical Replay dengan nilai buatan.
8. Nilai `duck_age_days = 21` pada Historical Replay berasal dari **estimasi kualitatif dataset**, bukan pengukuran umur individual. Karena itu AgeFlag tidak dinilai sebagai ground truth historis.
9. `N_sold_actual` tidak boleh diperlakukan sebagai ground truth biologis `N_survive`.
10. Raw historical farmer profit tidak boleh diperlakukan sebagai ground truth langsung `Net_Cash_Contribution_DSS` karena semantik biaya, feed, harga, dan potensi penjualan tidak identik.
11. Synthetic fixture harus diberi label synthetic dan tidak boleh disebut observasi aktual.
12. Row tidak boleh dipilih/dihapus setelah melihat besar error backend.

---

## 3. Field yang Sah Dibandingkan Aktual vs Sistem

| Field | Pembanding aktual | Status | Cara membandingkan |
|---|---|---|---|
| `density_are` | `J/A_are` dari row aktual | **Direct-compatible** | Backend vs hasil aritmetika sumber |
| `Yield_are_pred` | `Actual Yield (kg/are)` | **Direct-compatible** | Error = backend - actual |
| `Yield_total_pred` | `Actual Yield * A_are` | **Direct-compatible** | Error = backend - actual total |
| Harvest HST/date | tanggal panen aktual | **Direct-compatible untuk replay terpilih** | Sertani: actual vs window 100–110; Inpari: actual vs window 109–116 |
| `Revenue_gabah` | actual yield distandardisasi ke Rp6.000/kg | **Derived like-for-like** | Backend vs `ActualYield*A_are*6000` |
| `Cost_duck_buy` | `J*p_duck_buy` request | **Contract equality** | Harus mengikuti input request |
| `AgeFlag` | tidak ada umur individual actual | **Tidak validasi historis** | Hanya contract check |
| `N_survive` | tidak ada survival biologis actual kompatibel | **Tidak validasi historis** | Jangan bandingkan dengan `N_sold_actual` |
| `Revenue_duck_potential` | realized duck sale berbeda semantik | **Context only** | Jangan jadikan error akurasi |
| `Cost_feed` | feed historis tidak terstandardisasi | **Context only** | Model selalu `J*20.000` |
| `Net_Cash_Contribution_DSS` | raw farmer profit berbeda semantik | **Tidak direct-compatible** | Catat berdampingan hanya sebagai context, bukan accuracy metric |

---

## 4. Eligibility Historical Replay

Historical Replay membutuhkan minimal:

- `A_are` aktual;
- `J` aktual;
- varietas yang dapat dipetakan ke domain production;
- sistem tanam eksplisit `Jarwo 2:1` atau `Tegel`;
- `planting_date` aktual;
- `p_duck_buy` numerik pada sumber (termasuk 0 bila sumber memang merekam 0).

Dari clean set, **11 row** memenuhi kebutuhan request tersebut. Raw row 41 mempunyai tanggal tanam aktual tetapi `p_duck_buy = null`, sehingga **tidak dimasukkan** ke Historical Replay. Tidak ada nilai pengganti yang dibuat.

### 4.1 Catatan umur bebek

Seluruh replay menggunakan:

```text
duck_age_days = 21
```

karena dataset clean mencatat estimasi kualitatif 21 hari. Angka ini **bukan ground truth umur individual per row**. Oleh sebab itu hasil AgeFlag tidak masuk metrik aktual-vs-sistem.

---

## 5. Daftar Historical Replay

| ID | Raw row | Petani | A (are) | J | d aktual | Sistem | Varietas | Planting date | Harvest date aktual | HST aktual | p_duck_buy | Yield aktual kg/are |
|---|---:|---|---:|---:|---:|---|---|---|---|---:|---:|---:|
| H01 | 28 | I Gusti Nyoman Ngurah Wirasuta | 6.35 | 20 | 3.1496 | Jarwo 2:1 | Sertani | 2024-02-19 | 2024-05-22 | 93 | 15000 | 45.82677165 |
| H02 | 34 | I Gusti Ngurah Rai Sukarta | 10.21 | 32 | 3.1342 | Jarwo 2:1 | Sertani | 2024-04-15 | 2024-07-19 | 95 | 12000 | 50.00000000 |
| H03 | 36 | I Wayan Suarta | 6.60 | 19 | 2.8788 | Tegel | Inpari | 2024-04-12 | 2024-08-06 | 116 | 12000 | 47.19696970 |
| H04 | 37 | I Wayan Suwendhi Artha | 4.80 | 9 | 1.8750 | Tegel | Sertani a 13 | 2024-04-23 | 2024-07-31 | 99 | 0 | 60.41666667 |
| H05 | 38 | I Ketut Alit Sudarsana | 10.00 | 32 | 3.2000 | Jarwo 2:1 | Sertani | 2024-04-22 | 2024-07-31 | 100 | 0 | 53.40000000 |
| H06 | 39 | I Gusti Ngurah Rai Sukarta | 5.50 | 18 | 3.2727 | Jarwo 2:1 | Sertani | 2024-04-15 | 2024-07-19 | 95 | 12000 | 47.00000000 |
| H07 | 43 | I Made Arsania | 3.60 | 15 | 4.1667 | Jarwo 2:1 | Sertani | 2024-10-01 | 2025-01-17 | 108 | 0 | 40.41666667 |
| H08 | 44 | I Ketut Alit Sudarsana | 10.00 | 29 | 2.9000 | Tegel | Inpari | 2024-09-28 | 2025-01-18 | 112 | 0 | 38.65000000 |
| H09 | 51 | I Wayan Suwendhi Artha | 4.81 | 10 | 2.0790 | Jarwo 2:1 | Sertani | 2025-04-09 | 2025-07-19 | 101 | 25000 | 43.45114345 |
| H10 | 53 | I Nyoman Suwitra | 4.80 | 10 | 2.0833 | Jarwo 2:1 | Sertani | 2025-04-09 | 2025-07-19 | 101 | 25000 | 40.10416667 |
| H11 | 55 | Alm. I Ketut Tantra | 3.45 | 7 | 2.0290 | Jarwo 2:1 | Sertani | 2025-04-19 | 2025-07-23 | 95 | 25000 | 7.53623188 |

---

## 6. Format Evidence per Historical Replay

Untuk **setiap H01–H11**, isi setelah backend dijalankan:

```text
backend_commit:
backend_start_command:
endpoint:
http_method:
request_timestamp:
request_body_actual:
http_status:
raw_response_json:

response_path_density_are:
response_density_are:
response_path_yield_are_pred:
response_yield_are_pred:
response_path_yield_total_pred:
response_yield_total_pred:
response_path_harvest_hst:
response_harvest_hst:
response_path_harvest_date:
response_harvest_date:
response_path_revenue_gabah:
response_revenue_gabah:
response_path_cost_duck_buy:
response_cost_duck_buy:
response_path_cost_feed:
response_cost_feed:
response_path_net_cash_contribution_dss:
response_net_cash_contribution_dss:
warnings_actual:

comparison_yield_error:
comparison_yield_abs_error:
comparison_harvest_status:
comparison_density_error:
comparison_standardized_gabah_revenue_error:
result:
discrepancy_if_any:
```

---

## 7. Historical Replay Requests dan Ground Truth

### H01 — Raw Row 28 — I Gusti Nyoman Ngurah Wirasuta

**Ground truth / source values**

- Area: `6.35` are
- Duck count: `20`
- Density aktual: `3.14960630` ekor/are
- Sistem: `Jarwo 2:1`
- Varietas: `Sertani`
- Planting date aktual: `2024-02-19`
- Harvest date aktual: `2024-05-22`
- HST panen aktual: `93` hari
- p_duck_buy sumber: `Rp15.000/ekor`
- Yield aktual: `45.82677165 kg/are`
- Yield total aktual: `291.0000 kg`
- Standardized actual gabah revenue @Rp6.000/kg: `Rp1.746.000.00`
- Historical feed cost (context only): `Rp200.000`
- Historical duck sale revenue (context only): `Rp0`
- Historical core profit field (context only; bukan ground truth Net_Cash): `Rp1.246.000`
- Catatan sumber: He only had 7 ducks left (not sell yet).


**Request yang harus dikirim ke backend**

```json
{
  "land_area_are": 6.35,
  "duck_count": 20,
  "rice_variety": "sertani",
  "planting_system": "jajar_legowo",
  "duck_age_days": 21,
  "planting_date": "2024-02-19",
  "p_duck_buy": 15000
}
```

**Hasil backend nyata — jangan diisi sebelum runtime**

```text
http_status:
raw_response_json:

density_are_backend:
Yield_are_pred_backend:
Yield_total_pred_backend:
harvest_hst_backend:
harvest_date_backend:
Revenue_gabah_backend:
Cost_duck_buy_backend:
Cost_feed_backend:
Net_Cash_Contribution_DSS_backend:
warnings_backend:

Yield_error_backend_minus_actual:
Harvest_comparison:
Density_error_backend_minus_actual:
Standardized_Gabah_Revenue_error:
result:
```

---

### H02 — Raw Row 34 — I Gusti Ngurah Rai Sukarta

**Ground truth / source values**

- Area: `10.21` are
- Duck count: `32`
- Density aktual: `3.13418217` ekor/are
- Sistem: `Jarwo 2:1`
- Varietas: `Sertani`
- Planting date aktual: `2024-04-15`
- Harvest date aktual: `2024-07-19`
- HST panen aktual: `95` hari
- p_duck_buy sumber: `Rp12.000/ekor`
- Yield aktual: `50.00000000 kg/are`
- Yield total aktual: `510.5000 kg`
- Standardized actual gabah revenue @Rp6.000/kg: `Rp3.063.000.00`
- Historical feed cost (context only): `Rp256.000`
- Historical duck sale revenue (context only): `Rp875.000`
- Historical core profit field (context only; bukan ground truth Net_Cash): `Rp3.451.150`
- Catatan sumber: Data source records ecoenzyme and natural pesticide use.


**Request yang harus dikirim ke backend**

```json
{
  "land_area_are": 10.21,
  "duck_count": 32,
  "rice_variety": "sertani",
  "planting_system": "jajar_legowo",
  "duck_age_days": 21,
  "planting_date": "2024-04-15",
  "p_duck_buy": 12000
}
```

**Hasil backend nyata — jangan diisi sebelum runtime**

```text
http_status:
raw_response_json:

density_are_backend:
Yield_are_pred_backend:
Yield_total_pred_backend:
harvest_hst_backend:
harvest_date_backend:
Revenue_gabah_backend:
Cost_duck_buy_backend:
Cost_feed_backend:
Net_Cash_Contribution_DSS_backend:
warnings_backend:

Yield_error_backend_minus_actual:
Harvest_comparison:
Density_error_backend_minus_actual:
Standardized_Gabah_Revenue_error:
result:
```

---

### H03 — Raw Row 36 — I Wayan Suarta

**Ground truth / source values**

- Area: `6.6` are
- Duck count: `19`
- Density aktual: `2.87878788` ekor/are
- Sistem: `Tegel`
- Varietas: `Inpari`
- Planting date aktual: `2024-04-12`
- Harvest date aktual: `2024-08-06`
- HST panen aktual: `116` hari
- p_duck_buy sumber: `Rp12.000/ekor`
- Yield aktual: `47.19696970 kg/are`
- Yield total aktual: `311.5000 kg`
- Standardized actual gabah revenue @Rp6.000/kg: `Rp1.869.000.00`
- Historical feed cost (context only): `Rp25.000`
- Historical duck sale revenue (context only): `Rp0`
- Historical core profit field (context only; bukan ground truth Net_Cash): `Rp1.709.450`
- Catatan sumber: Not plant the border plant yet.


**Request yang harus dikirim ke backend**

```json
{
  "land_area_are": 6.6,
  "duck_count": 19,
  "rice_variety": "inpari",
  "planting_system": "tegel",
  "duck_age_days": 21,
  "planting_date": "2024-04-12",
  "p_duck_buy": 12000
}
```

**Hasil backend nyata — jangan diisi sebelum runtime**

```text
http_status:
raw_response_json:

density_are_backend:
Yield_are_pred_backend:
Yield_total_pred_backend:
harvest_hst_backend:
harvest_date_backend:
Revenue_gabah_backend:
Cost_duck_buy_backend:
Cost_feed_backend:
Net_Cash_Contribution_DSS_backend:
warnings_backend:

Yield_error_backend_minus_actual:
Harvest_comparison:
Density_error_backend_minus_actual:
Standardized_Gabah_Revenue_error:
result:
```

---

### H04 — Raw Row 37 — I Wayan Suwendhi Artha

**Ground truth / source values**

- Area: `4.8` are
- Duck count: `9`
- Density aktual: `1.87500000` ekor/are
- Sistem: `Tegel`
- Varietas: `Sertani a 13`
- Planting date aktual: `2024-04-23`
- Harvest date aktual: `2024-07-31`
- HST panen aktual: `99` hari
- p_duck_buy sumber: `Rp0/ekor`
- Yield aktual: `60.41666667 kg/are`
- Yield total aktual: `290.0000 kg`
- Standardized actual gabah revenue @Rp6.000/kg: `Rp1.740.000.00`
- Historical feed cost (context only): `Rp0`
- Historical duck sale revenue (context only): `Rp0`
- Historical core profit field (context only; bukan ground truth Net_Cash): `Rp1.827.000`
- Catatan sumber: Buy-price field is recorded as 0; no explicit note proves the economic reason for the zero.

> **Catatan `p_duck_buy=0`:** angka 0 berasal dari field sumber. Untuk row ini, jangan menyimpulkan alasan ekonominya kecuali field note memang menjelaskannya.

**Request yang harus dikirim ke backend**

```json
{
  "land_area_are": 4.8,
  "duck_count": 9,
  "rice_variety": "sertani",
  "planting_system": "tegel",
  "duck_age_days": 21,
  "planting_date": "2024-04-23",
  "p_duck_buy": 0
}
```

**Hasil backend nyata — jangan diisi sebelum runtime**

```text
http_status:
raw_response_json:

density_are_backend:
Yield_are_pred_backend:
Yield_total_pred_backend:
harvest_hst_backend:
harvest_date_backend:
Revenue_gabah_backend:
Cost_duck_buy_backend:
Cost_feed_backend:
Net_Cash_Contribution_DSS_backend:
warnings_backend:

Yield_error_backend_minus_actual:
Harvest_comparison:
Density_error_backend_minus_actual:
Standardized_Gabah_Revenue_error:
result:
```

---

### H05 — Raw Row 38 — I Ketut Alit Sudarsana

**Ground truth / source values**

- Area: `10.0` are
- Duck count: `32`
- Density aktual: `3.20000000` ekor/are
- Sistem: `Jarwo 2:1`
- Varietas: `Sertani`
- Planting date aktual: `2024-04-22`
- Harvest date aktual: `2024-07-31`
- HST panen aktual: `100` hari
- p_duck_buy sumber: `Rp0/ekor`
- Yield aktual: `53.40000000 kg/are`
- Yield total aktual: `534.0000 kg`
- Standardized actual gabah revenue @Rp6.000/kg: `Rp3.204.000.00`
- Historical feed cost (context only): `Rp3.216.250`
- Historical duck sale revenue (context only): `Rp3.825.000`
- Historical core profit field (context only; bukan ground truth Net_Cash): `Rp3.972.950`
- Catatan sumber: Buy-price field is recorded as 0; no explicit note proves the economic reason for the zero.

> **Catatan `p_duck_buy=0`:** angka 0 berasal dari field sumber. Untuk row ini, jangan menyimpulkan alasan ekonominya kecuali field note memang menjelaskannya.

**Request yang harus dikirim ke backend**

```json
{
  "land_area_are": 10.0,
  "duck_count": 32,
  "rice_variety": "sertani",
  "planting_system": "jajar_legowo",
  "duck_age_days": 21,
  "planting_date": "2024-04-22",
  "p_duck_buy": 0
}
```

**Hasil backend nyata — jangan diisi sebelum runtime**

```text
http_status:
raw_response_json:

density_are_backend:
Yield_are_pred_backend:
Yield_total_pred_backend:
harvest_hst_backend:
harvest_date_backend:
Revenue_gabah_backend:
Cost_duck_buy_backend:
Cost_feed_backend:
Net_Cash_Contribution_DSS_backend:
warnings_backend:

Yield_error_backend_minus_actual:
Harvest_comparison:
Density_error_backend_minus_actual:
Standardized_Gabah_Revenue_error:
result:
```

---

### H06 — Raw Row 39 — I Gusti Ngurah Rai Sukarta

**Ground truth / source values**

- Area: `5.5` are
- Duck count: `18`
- Density aktual: `3.27272727` ekor/are
- Sistem: `Jarwo 2:1`
- Varietas: `Sertani`
- Planting date aktual: `2024-04-15`
- Harvest date aktual: `2024-07-19`
- HST panen aktual: `95` hari
- p_duck_buy sumber: `Rp12.000/ekor`
- Yield aktual: `47.00000000 kg/are`
- Yield total aktual: `258.5000 kg`
- Standardized actual gabah revenue @Rp6.000/kg: `Rp1.551.000.00`
- Historical feed cost (context only): `Rp144.000`
- Historical duck sale revenue (context only): `Rp455.000`
- Historical core profit field (context only; bukan ground truth Net_Cash): `Rp1.723.550`
- Catatan sumber: Data source records ecoenzyme and natural pesticide use.


**Request yang harus dikirim ke backend**

```json
{
  "land_area_are": 5.5,
  "duck_count": 18,
  "rice_variety": "sertani",
  "planting_system": "jajar_legowo",
  "duck_age_days": 21,
  "planting_date": "2024-04-15",
  "p_duck_buy": 12000
}
```

**Hasil backend nyata — jangan diisi sebelum runtime**

```text
http_status:
raw_response_json:

density_are_backend:
Yield_are_pred_backend:
Yield_total_pred_backend:
harvest_hst_backend:
harvest_date_backend:
Revenue_gabah_backend:
Cost_duck_buy_backend:
Cost_feed_backend:
Net_Cash_Contribution_DSS_backend:
warnings_backend:

Yield_error_backend_minus_actual:
Harvest_comparison:
Density_error_backend_minus_actual:
Standardized_Gabah_Revenue_error:
result:
```

---

### H07 — Raw Row 43 — I Made Arsania

**Ground truth / source values**

- Area: `3.6` are
- Duck count: `15`
- Density aktual: `4.16666667` ekor/are
- Sistem: `Jarwo 2:1`
- Varietas: `Sertani`
- Planting date aktual: `2024-10-01`
- Harvest date aktual: `2025-01-17`
- HST panen aktual: `108` hari
- p_duck_buy sumber: `Rp0/ekor`
- Yield aktual: `40.41666667 kg/are`
- Yield total aktual: `145.5000 kg`
- Standardized actual gabah revenue @Rp6.000/kg: `Rp873.000.00`
- Historical feed cost (context only): `Rp0`
- Historical duck sale revenue (context only): `Rp0`
- Historical core profit field (context only; bukan ground truth Net_Cash): `Rp873.000`
- Catatan sumber: Buy-price field is recorded as 0; no explicit note proves the economic reason for the zero.

> **Catatan `p_duck_buy=0`:** angka 0 berasal dari field sumber. Untuk row ini, jangan menyimpulkan alasan ekonominya kecuali field note memang menjelaskannya.

**Request yang harus dikirim ke backend**

```json
{
  "land_area_are": 3.6,
  "duck_count": 15,
  "rice_variety": "sertani",
  "planting_system": "jajar_legowo",
  "duck_age_days": 21,
  "planting_date": "2024-10-01",
  "p_duck_buy": 0
}
```

**Hasil backend nyata — jangan diisi sebelum runtime**

```text
http_status:
raw_response_json:

density_are_backend:
Yield_are_pred_backend:
Yield_total_pred_backend:
harvest_hst_backend:
harvest_date_backend:
Revenue_gabah_backend:
Cost_duck_buy_backend:
Cost_feed_backend:
Net_Cash_Contribution_DSS_backend:
warnings_backend:

Yield_error_backend_minus_actual:
Harvest_comparison:
Density_error_backend_minus_actual:
Standardized_Gabah_Revenue_error:
result:
```

---

### H08 — Raw Row 44 — I Ketut Alit Sudarsana

**Ground truth / source values**

- Area: `10.0` are
- Duck count: `29`
- Density aktual: `2.90000000` ekor/are
- Sistem: `Tegel`
- Varietas: `Inpari`
- Planting date aktual: `2024-09-28`
- Harvest date aktual: `2025-01-18`
- HST panen aktual: `112` hari
- p_duck_buy sumber: `Rp0/ekor`
- Yield aktual: `38.65000000 kg/are`
- Yield total aktual: `386.5000 kg`
- Standardized actual gabah revenue @Rp6.000/kg: `Rp2.319.000.00`
- Historical feed cost (context only): `Rp0`
- Historical duck sale revenue (context only): `Rp0`
- Historical core profit field (context only; bukan ground truth Net_Cash): `Rp2.319.000`
- Catatan sumber: Source explicitly states: use duck from previous cycle.

> **Catatan `p_duck_buy=0`:** sumber secara eksplisit menyatakan bebek berasal dari siklus sebelumnya, sehingga 0 mempunyai provenance operasional yang jelas.

**Request yang harus dikirim ke backend**

```json
{
  "land_area_are": 10.0,
  "duck_count": 29,
  "rice_variety": "inpari",
  "planting_system": "tegel",
  "duck_age_days": 21,
  "planting_date": "2024-09-28",
  "p_duck_buy": 0
}
```

**Hasil backend nyata — jangan diisi sebelum runtime**

```text
http_status:
raw_response_json:

density_are_backend:
Yield_are_pred_backend:
Yield_total_pred_backend:
harvest_hst_backend:
harvest_date_backend:
Revenue_gabah_backend:
Cost_duck_buy_backend:
Cost_feed_backend:
Net_Cash_Contribution_DSS_backend:
warnings_backend:

Yield_error_backend_minus_actual:
Harvest_comparison:
Density_error_backend_minus_actual:
Standardized_Gabah_Revenue_error:
result:
```

---

### H09 — Raw Row 51 — I Wayan Suwendhi Artha

**Ground truth / source values**

- Area: `4.81` are
- Duck count: `10`
- Density aktual: `2.07900208` ekor/are
- Sistem: `Jarwo 2:1`
- Varietas: `Sertani`
- Planting date aktual: `2025-04-09`
- Harvest date aktual: `2025-07-19`
- HST panen aktual: `101` hari
- p_duck_buy sumber: `Rp25.000/ekor`
- Yield aktual: `43.45114345 kg/are`
- Yield total aktual: `209.0000 kg`
- Standardized actual gabah revenue @Rp6.000/kg: `Rp1.254.000.00`
- Historical feed cost (context only): `Rp0`
- Historical duck sale revenue (context only): `Rp400.000`
- Historical core profit field (context only; bukan ground truth Net_Cash): `Rp1.404.000`
- Catatan sumber: Source notes Azolla appeared naturally.


**Request yang harus dikirim ke backend**

```json
{
  "land_area_are": 4.81,
  "duck_count": 10,
  "rice_variety": "sertani",
  "planting_system": "jajar_legowo",
  "duck_age_days": 21,
  "planting_date": "2025-04-09",
  "p_duck_buy": 25000
}
```

**Hasil backend nyata — jangan diisi sebelum runtime**

```text
http_status:
raw_response_json:

density_are_backend:
Yield_are_pred_backend:
Yield_total_pred_backend:
harvest_hst_backend:
harvest_date_backend:
Revenue_gabah_backend:
Cost_duck_buy_backend:
Cost_feed_backend:
Net_Cash_Contribution_DSS_backend:
warnings_backend:

Yield_error_backend_minus_actual:
Harvest_comparison:
Density_error_backend_minus_actual:
Standardized_Gabah_Revenue_error:
result:
```

---

### H10 — Raw Row 53 — I Nyoman Suwitra

**Ground truth / source values**

- Area: `4.8` are
- Duck count: `10`
- Density aktual: `2.08333333` ekor/are
- Sistem: `Jarwo 2:1`
- Varietas: `Sertani`
- Planting date aktual: `2025-04-09`
- Harvest date aktual: `2025-07-19`
- HST panen aktual: `101` hari
- p_duck_buy sumber: `Rp25.000/ekor`
- Yield aktual: `40.10416667 kg/are`
- Yield total aktual: `192.5000 kg`
- Standardized actual gabah revenue @Rp6.000/kg: `Rp1.155.000.00`
- Historical feed cost (context only): `Rp0`
- Historical duck sale revenue (context only): `Rp400.000`
- Historical core profit field (context only; bukan ground truth Net_Cash): `Rp1.305.000`
- Catatan sumber: Source notes duck/livestock investment subsidy by AW; historical cash semantics therefore require caution.


**Request yang harus dikirim ke backend**

```json
{
  "land_area_are": 4.8,
  "duck_count": 10,
  "rice_variety": "sertani",
  "planting_system": "jajar_legowo",
  "duck_age_days": 21,
  "planting_date": "2025-04-09",
  "p_duck_buy": 25000
}
```

**Hasil backend nyata — jangan diisi sebelum runtime**

```text
http_status:
raw_response_json:

density_are_backend:
Yield_are_pred_backend:
Yield_total_pred_backend:
harvest_hst_backend:
harvest_date_backend:
Revenue_gabah_backend:
Cost_duck_buy_backend:
Cost_feed_backend:
Net_Cash_Contribution_DSS_backend:
warnings_backend:

Yield_error_backend_minus_actual:
Harvest_comparison:
Density_error_backend_minus_actual:
Standardized_Gabah_Revenue_error:
result:
```

---

### H11 — Raw Row 55 — Alm. I Ketut Tantra

**Ground truth / source values**

- Area: `3.45` are
- Duck count: `7`
- Density aktual: `2.02898551` ekor/are
- Sistem: `Jarwo 2:1`
- Varietas: `Sertani`
- Planting date aktual: `2025-04-19`
- Harvest date aktual: `2025-07-23`
- HST panen aktual: `95` hari
- p_duck_buy sumber: `Rp25.000/ekor`
- Yield aktual: `7.53623188 kg/are`
- Yield total aktual: `26.0000 kg`
- Standardized actual gabah revenue @Rp6.000/kg: `Rp156.000.00`
- Historical feed cost (context only): `Rp0`
- Historical duck sale revenue (context only): `Rp280.000`
- Historical core profit field (context only; bukan ground truth Net_Cash): `Rp261.000`
- Catatan sumber: Source notes duck/livestock investment subsidy by AW; historical cash semantics therefore require caution.


**Request yang harus dikirim ke backend**

```json
{
  "land_area_are": 3.45,
  "duck_count": 7,
  "rice_variety": "sertani",
  "planting_system": "jajar_legowo",
  "duck_age_days": 21,
  "planting_date": "2025-04-19",
  "p_duck_buy": 25000
}
```

**Hasil backend nyata — jangan diisi sebelum runtime**

```text
http_status:
raw_response_json:

density_are_backend:
Yield_are_pred_backend:
Yield_total_pred_backend:
harvest_hst_backend:
harvest_date_backend:
Revenue_gabah_backend:
Cost_duck_buy_backend:
Cost_feed_backend:
Net_Cash_Contribution_DSS_backend:
warnings_backend:

Yield_error_backend_minus_actual:
Harvest_comparison:
Density_error_backend_minus_actual:
Standardized_Gabah_Revenue_error:
result:
```

---

## 8. Rekap Aktual vs Sistem Setelah Runtime

Isi tabel ini **hanya dari raw response backend aktual**.

| ID | Yield aktual | Yield backend | Error | Abs Error | HST aktual | Harvest backend | Density aktual | Density backend | Std. actual gabah revenue | Backend gabah revenue | Status |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| H01 | 45.82677165 | 47.87675070 | +2.04997905 | 2.04997905 | 93 | 100–110 | 3.14960630 | 3.1496063 | 1746000.00 | 1824104.20 | COMPLETED (BELOW_WINDOW) |
| H02 | 50.00000000 | 47.87675070 | -2.12324930 | 2.12324930 | 95 | 100–110 | 3.13418217 | 3.1341822 | 3063000.00 | 2932929.75 | COMPLETED (BELOW_WINDOW) |
| H03 | 47.19696970 | 47.87675070 | +0.67978100 | 0.67978100 | 116 | 109–116 | 2.87878788 | 2.8787879 | 1869000.00 | 1895919.33 | COMPLETED (IN_WINDOW) |
| H04 | 60.41666667 | 47.87675070 | -12.53991597 | 12.53991597 | 99 | 100–110 | 1.87500000 | 1.8750000 | 1740000.00 | 1378850.42 | COMPLETED (BELOW_WINDOW) |
| H05 | 53.40000000 | 47.87675070 | -5.52324930 | 5.52324930 | 100 | 100–110 | 3.20000000 | 3.2000000 | 3204000.00 | 2872605.04 | COMPLETED (IN_WINDOW) |
| H06 | 47.00000000 | 47.87675070 | +0.87675070 | 0.87675070 | 95 | 100–110 | 3.27272727 | 3.2727273 | 1551000.00 | 1579932.77 | COMPLETED (BELOW_WINDOW) |
| H07 | 40.41666667 | 47.87675070 | +7.46008403 | 7.46008403 | 108 | 100–110 | 4.16666667 | 4.1666667 | 873000.00 | 1034137.82 | COMPLETED (IN_WINDOW) |
| H08 | 38.65000000 | 47.87675070 | +9.22675070 | 9.22675070 | 112 | 109–116 | 2.90000000 | 2.9000000 | 2319000.00 | 2872605.04 | COMPLETED (IN_WINDOW) |
| H09 | 43.45114345 | 47.87675070 | +4.42560725 | 4.42560725 | 101 | 100–110 | 2.07900208 | 2.0790021 | 1254000.00 | 1381723.03 | COMPLETED (IN_WINDOW) |
| H10 | 40.10416667 | 47.87675070 | +7.77258403 | 7.77258403 | 101 | 100–110 | 2.08333333 | 2.0833333 | 1155000.00 | 1378850.42 | COMPLETED (IN_WINDOW) |
| H11 | 7.53623188 | 47.87675070 | +40.34051882 | 40.34051882 | 95 | 100–110 | 2.02898551 | 2.0289855 | 156000.00 | 991048.74 | COMPLETED (BELOW_WINDOW) |

### 8.1 Runtime diagnostic metrics untuk Historical Replay

Setelah seluruh H01–H11 selesai:

```text
e_y_i   = Yield_are_backend_i - Yield_actual_i
MAE_y   = mean(abs(e_y_i))
RMSE_y  = sqrt(mean(e_y_i^2))
MedAE_y = median(abs(e_y_i))
```

Catat:

```text
n_historical_replay: 11
MAE_y: 8.45622456 kg/are
RMSE_y: 13.63764667 kg/are
MedAE_y: 5.52324930 kg/are
```

Metrik ini adalah **runtime replay diagnostic terhadap production backend**. Ia tidak menggantikan numerical validation penelitian LOFO-CV.

---

## 9. Calendar Comparison

### Sertani

Backend menghasilkan harvest window 100–110 HST.

Untuk setiap Sertani replay:

```text
IN_WINDOW      jika 100 <= HST_actual <= 110
BELOW_WINDOW   jika HST_actual < 100
ABOVE_WINDOW   jika HST_actual > 110
```

Jika diperlukan diagnostic distance:

```text
distance = 0                      jika 100 <= HST_actual <= 110
distance = 100 - HST_actual       jika HST_actual < 100
distance = HST_actual - 110       jika HST_actual > 110
```

### Inpari

Backend terbaru **harus** menghasilkan harvest window 109–116 HST. Untuk setiap replay Inpari:

```text
IN_WINDOW      jika 109 <= HST_actual <= 116
BELOW_WINDOW   jika HST_actual < 109
ABOVE_WINDOW   jika HST_actual > 116
```

Jika diperlukan diagnostic distance pada data yang **tidak digunakan membentuk window**:

```text
distance = 0                      jika 109 <= HST_actual <= 116
distance = 109 - HST_actual       jika HST_actual < 109
distance = HST_actual - 116       jika HST_actual > 116
```

Tiga observation lokal yang saat ini tersedia (109, 112, 116 HST) merupakan basis pembentukan window, sehingga tidak boleh dipresentasikan sebagai independent validation dengan error nol. Median deskriptifnya adalah 112 HST.

---

## 10. Economic Comparison — Batas yang Boleh dan Tidak Boleh

### 10.1 Boleh dibandingkan

`Revenue_gabah` dapat dibandingkan secara like-for-like dengan actual yield yang distandardisasi pada harga model:

```text
Actual_Standardized_Revenue_Gabah
    = Yield_actual * A_are * 6000

Error_Revenue_Gabah
    = Revenue_gabah_backend
    - Actual_Standardized_Revenue_Gabah
```

`Cost_duck_buy` dapat diperiksa sebagai contract equality:

```text
Cost_duck_buy_backend == J * p_duck_buy_request
```

### 10.2 Tidak boleh disebut accuracy comparison

- historical `Feed Cost` vs `Cost_feed_backend`, karena model memakai simplified Rp20.000/ekor/siklus;
- historical `Duck Sale Revenue` vs `Revenue_duck_potential`, karena realized sales berbeda dari potential availability;
- historical core/raw profit vs `Net_Cash_Contribution_DSS`, karena semantics biaya dan revenue tidak identik.

Nilai-nilai tersebut boleh ditampilkan berdampingan sebagai **context**, tetapi jangan menghitung MAE/RMSE seolah-olah endpoint-nya identik.

---

## 11. Synthetic Contract & Boundary Tests

Historical Replay tidak mencakup seluruh branch. Skenario berikut **sengaja sintetis** dan hanya menguji contract/model boundary.

| ID | Kondisi | Input utama | Expected semantic |
|---|---|---|---|
| B01 | Age too young | `duck_age_days=20` | `TOO_YOUNG`; yield/survival tidak berubah karena age |
| B02 | Age upper recommended | `duck_age_days=30` | `RECOMMENDED` |
| B03 | Age above recommended | `duck_age_days=31` | `ABOVE_RECOMMENDED_AGE` |
| B04 | Jarwo under-density | `A=10,J=10` | `UNDER_DENSITY` |
| B05 | Jarwo lower boundary | `A=10,J=20` | `RECOMMENDED` |
| B06 | Jarwo upper boundary | `A=10,J=40` | `RECOMMENDED` |
| B07 | Jarwo above recommended | `A=10,J=50` | `ABOVE_RECOMMENDED`; normal survival |
| B08 | Overload | `A=10,J=81` | `OVERLOAD_HIGH_RISK`; `floor(0.60J)` |
| B09 | Tegel lower boundary | `A=10,J=20` | `RECOMMENDED` |
| B10 | Tegel upper boundary | `A=10,J=30` | `RECOMMENDED` |
| B11 | Tegel above recommended | `A=10,J=40` | `ABOVE_RECOMMENDED` |
| B12 | Purchase price zero | `p_duck_buy=0` | accepted; no Rp25k fallback |
| B13 | Purchase price passthrough | `p_duck_buy=30000` | cost uses 30k request |
| B14 | Inpari calendar | `rice_variety=inpari` | harvest window 109–116 HST |

Gunakan fixture lengkap yang valid untuk field lain. Nilai synthetic harus diberi label synthetic pada evidence.

---

## 12. Invalid Input Tests

| ID | Invalid condition | Expected semantic |
|---|---|---|
| I01 | missing `planting_date` | request ditolak; tidak ada fallback tanggal |
| I02 | missing `duck_age_days` | request ditolak; tidak ada default 21 |
| I03 | missing `p_duck_buy` | request ditolak; tidak ada fallback Rp25.000 |
| I04 | `land_area_are=0` | request ditolak |
| I05 | `duck_count=0` | request ditolak |
| I06 | Jarwo ratio/category non-2:1 | request ditolak atau tidak dipetakan diam-diam ke production `jajar_legowo` |

Exact HTTP status mengikuti error-handling convention repository. Jangan mengarang status code sebelum schema/backend diperiksa.

---

## 13. Endpoint dan Persistence Checks

Selain `/simulate`, periksa bila endpoint tersedia:

- `/api/v1/dss/options`: domain Jarwo hanya 2:1; tidak ada legacy coefficients;
- `/api/v1/dss/visualize`: tidak memvisualisasikan `R_age`, `lambda_eff`, atau `F_density_bio` sebagai production science;
- history/persistence: response final tetap konsisten setelah write/read;
- legacy records boleh tetap terbaca jika repository membutuhkan compatibility, tetapi tidak boleh direinterpretasikan sebagai semantics final.

---

## 14. Repository-Wide Legacy Search

Setelah runtime test, cari minimal:

```text
R_age
F_age
lambda_eff
0.78125
F_density_bio
alpha_bio
beta_tramp
46.9363
47.1970
Profit_net_cash
Cost_feed_isolated
35000
4500
0.90
r_sale
planting_date optional
duck_age_days default
p_duck_buy default
```

Temuan hanya dianggap bug jika memengaruhi production path, active docs/schema, tests, visualization, atau canonical output. Historical migration/changelog boleh menyimpan istilah lama bila jelas berstatus legacy.

---

## 15. Definition of Done

- [ ] H01–H11 dikirim melalui backend HTTP nyata.
- [ ] Raw request dan raw response H01–H11 tersimpan.
- [ ] Tabel aktual-vs-sistem diisi dari raw response, bukan kalkulasi manual.
- [ ] Runtime replay MAE/RMSE/MedAE yield dihitung dari response backend.
- [ ] Calendar actual-vs-system comparison selesai.
- [ ] Standardized gabah-revenue comparison selesai.
- [ ] Tidak ada survival-vs-sales metric yang disalahartikan sebagai biological validation.
- [ ] Synthetic boundary tests B01–B14 dijalankan.
- [ ] Invalid-input tests I01–I06 dijalankan.
- [ ] Endpoint options/visualization/history diperiksa bila tersedia.
- [ ] Repository-wide legacy search selesai.
- [ ] Setiap discrepancy dicatat apa adanya.
- [ ] Tidak ada skenario sintetis yang disebut data aktual.

---

## 16. Ringkasan Eksekusi

```text
backend_commit: 2d23130b1cf57685f6f161c9e7e565112f369c65 (working tree includes current SoT alignment)
backend_start_command: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
base_url: http://127.0.0.1:8000
execution_started_at: 2026-08-23T10:45:53.7845961Z
execution_finished_at: 2026-08-23T10:45:53.7845961Z

historical_replay:
  total: 11
  passed: 11
  failed: 0
  MAE_y: 8.45622456 kg/are
  RMSE_y: 13.63764667 kg/are
  MedAE_y: 5.52324930 kg/are

calendar_comparison:
  result: Sertani 4 IN_WINDOW and 5 BELOW_WINDOW. Inpari H03 (116 HST) and H08 (112 HST) both IN_WINDOW under the 109-116 local empirical window; no independent zero-error validation is claimed because the three observations form that window.

standardized_gabah_revenue_comparison:
  result: completed; per-row diagnostic errors are recorded in Section 8 and are not a Net Cash accuracy metric.

synthetic_boundary:
  passed: 14
  failed: 0

invalid_input:
  passed: 6
  failed: 0

options_contract:
  result: HTTP 200; Inpari metadata reports hst_panen_min=109, hst_panen_max=116, status=local-empirical-reference.

visualization_contract:
  result: HTTP 200; 100 density points, 45 age points, and final Core waterfall node Net_Cash_Contribution_DSS.

history_persistence:
  result: register/login/simulate/list/detail/delete = 201/200/200/200/200/200; persisted Inpari detail reports 109-116 and equals its simulate response byte-for-byte.

legacy_search:
  result: completed; no active 134-HST Inpari production semantics remain.

failed_or_unverified: []
```

Jangan menandai seluruh pengujian PASS sebelum backend dan seluruh HTTP request benar-benar dijalankan.

---

## 17. Runtime Evidence — 23 August 2026 (current working tree)

All evidence below was generated through the real HTTP service identified in Section 16. The table in Section 8 is a projection of the raw HTTP responses; it is not a manual formula substitution.

```text
H03: HTTP 200; harvest_hst=109-116; harvest_date=2024-07-30..2024-08-06; warnings=survival-assumption only; calendar=IN_WINDOW (actual 116).
H08: HTTP 200; harvest_hst=109-116; harvest_date=2025-01-15..2025-01-22; warnings=survival-assumption only; calendar=IN_WINDOW (actual 112).
B14: HTTP 200; harvest_hst=109-116; harvest_date=2026-04-20..2026-04-27; warnings=survival-assumption only.
I01/I02/I03/I04/I05: HTTP 400.
I06: HTTP 422.
```

Raw JSON from the live Inpari historical replay H03:

```json
{"age_flag":"RECOMMENDED","density_are":2.8787879,"density_ha":287.87879,"density_status":"RECOMMENDED","HST_in":21,"HST_out":65,"t_active":44,"D_in":"2024-05-03","D_out":"2024-06-16","harvest_hst_min":109,"harvest_hst_max":116,"D_panen_min":"2024-07-30","D_panen_max":"2024-08-06","N_survive":19,"Yield_are_pred":47.8767507,"Yield_total_pred":315.9866,"Revenue_gabah":1895919.33,"Revenue_duck_potential":997500.0,"Cost_duck_buy":228000.0,"Cost_feed":380000.0,"Core_Cash_Cost":608000.0,"Total_Revenue_DSS":2893419.33,"Net_Cash_Contribution_DSS":2285419.33,"warnings":["Estimasi survival mengasumsikan pemeliharaan memadai; actual mortality dapat berbeda akibat penyakit, predator, cuaca, atau faktor husbandry lain."]}
```
