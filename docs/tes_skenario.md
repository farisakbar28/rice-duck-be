# PANDUAN PENGUJIAN SKENARIO — BACKEND FINAL DSS PADI-BEBEK

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
| Harvest HST/date | tanggal panen aktual | **Direct-compatible untuk replay terpilih** | Sertani: actual vs window 100–110; Inpari: actual vs 134 |
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

**Runtime record (HTTP nyata, 2026-08-22T12:01:25.5856294Z)**

```text
http_status: 200
response: density_are=3.1496063; Yield_are_pred=47.8767507; Yield_total_pred=304.0174; harvest_hst=100-110; harvest_date=2024-05-29..2024-06-08; Revenue_gabah=1824104.20; Cost_duck_buy=300000.00; Cost_feed=400000.00; Net_Cash_Contribution_DSS=2174104.20
warnings: survival-assumption warning
comparison: yield_error=+2.04997905; yield_abs_error=2.04997905; harvest=BELOW_WINDOW (93 versus 100-110); density_error=0 within JSON precision; standardized_gabah_revenue_error=+78104.20
result: COMPLETED; canonical field values projected from raw HTTP JSON in Section 17.
```

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

**Hasil backend nyata**

Seluruh field yang semula dicadangkan pada template ini telah diisi pada **Runtime record** tepat di atas. Nilai tersebut berasal dari response HTTP 200 aktual; proyeksi lintas-kasus dan metriknya ada di Section 17.

---

### H02 — Raw Row 34 — I Gusti Ngurah Rai Sukarta

**Ground truth / source values**

**Runtime record (HTTP nyata, 2026-08-22T12:01:25.8181034Z)**

```text
http_status: 200
response: density_are=3.1341822; Yield_are_pred=47.8767507; Yield_total_pred=488.8216; harvest_hst=100-110; harvest_date=2024-07-24..2024-08-03; Revenue_gabah=2932929.75; Cost_duck_buy=384000.00; Cost_feed=640000.00; Net_Cash_Contribution_DSS=3588929.75
warnings: survival-assumption warning
comparison: yield_error=-2.12324930; yield_abs_error=2.12324930; harvest=BELOW_WINDOW (95 versus 100-110); density_error=0 within JSON precision; standardized_gabah_revenue_error=-130070.25
result: COMPLETED; canonical field values projected from raw HTTP JSON in Section 17.
```

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

**Hasil backend nyata**

Seluruh field yang semula dicadangkan pada template ini telah diisi pada **Runtime record** tepat di atas. Nilai tersebut berasal dari response HTTP 200 aktual; proyeksi lintas-kasus dan metriknya ada di Section 17.

---

### H03 — Raw Row 36 — I Wayan Suarta

**Ground truth / source values**

**Runtime record (HTTP nyata, 2026-08-22T12:01:25.8693950Z)**

```text
http_status: 200
response: density_are=2.8787879; Yield_are_pred=47.8767507; Yield_total_pred=315.9866; harvest_hst=134; harvest_date=2024-08-24; Revenue_gabah=1895919.33; Cost_duck_buy=228000.00; Cost_feed=380000.00; Net_Cash_Contribution_DSS=2285419.33
warnings: Inpari generic-estimate warning; survival-assumption warning
comparison: yield_error=+0.67978100; yield_abs_error=0.67978100; harvest=INPARI_GENERIC_POINT_ERROR (+18 HST versus actual 116); density_error=0 within JSON precision; standardized_gabah_revenue_error=+26919.33
result: COMPLETED; canonical field values projected from raw HTTP JSON in Section 17.
```

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

**Hasil backend nyata**

Seluruh field yang semula dicadangkan pada template ini telah diisi pada **Runtime record** tepat di atas. Nilai tersebut berasal dari response HTTP 200 aktual; proyeksi lintas-kasus dan metriknya ada di Section 17.

---

### H04 — Raw Row 37 — I Wayan Suwendhi Artha

**Ground truth / source values**

**Runtime record (HTTP nyata, 2026-08-22T12:01:25.9188794Z)**

```text
http_status: 200
response: density_are=1.8750000; Yield_are_pred=47.8767507; Yield_total_pred=229.8084; harvest_hst=100-110; harvest_date=2024-08-01..2024-08-11; Revenue_gabah=1378850.42; Cost_duck_buy=0.00; Cost_feed=180000.00; Net_Cash_Contribution_DSS=1671350.42
warnings: survival-assumption warning
comparison: yield_error=-12.53991597; yield_abs_error=12.53991597; harvest=BELOW_WINDOW (99 versus 100-110); density_error=0; standardized_gabah_revenue_error=-361149.58
result: COMPLETED; canonical field values projected from raw HTTP JSON in Section 17.
```

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

**Hasil backend nyata**

Seluruh field yang semula dicadangkan pada template ini telah diisi pada **Runtime record** tepat di atas. Nilai tersebut berasal dari response HTTP 200 aktual; proyeksi lintas-kasus dan metriknya ada di Section 17.

---

### H05 — Raw Row 38 — I Ketut Alit Sudarsana

**Ground truth / source values**

**Runtime record (HTTP nyata, 2026-08-22T12:01:25.9733691Z)**

```text
http_status: 200
response: density_are=3.2000000; Yield_are_pred=47.8767507; Yield_total_pred=478.7675; harvest_hst=100-110; harvest_date=2024-07-31..2024-08-10; Revenue_gabah=2872605.04; Cost_duck_buy=0.00; Cost_feed=640000.00; Net_Cash_Contribution_DSS=3912605.04
warnings: survival-assumption warning
comparison: yield_error=-5.52324930; yield_abs_error=5.52324930; harvest=IN_WINDOW (actual 100); density_error=0; standardized_gabah_revenue_error=-331394.96
result: COMPLETED; canonical field values projected from raw HTTP JSON in Section 17.
```

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

**Hasil backend nyata**

Seluruh field yang semula dicadangkan pada template ini telah diisi pada **Runtime record** tepat di atas. Nilai tersebut berasal dari response HTTP 200 aktual; proyeksi lintas-kasus dan metriknya ada di Section 17.

---

### H06 — Raw Row 39 — I Gusti Ngurah Rai Sukarta

**Ground truth / source values**

**Runtime record (HTTP nyata, 2026-08-22T12:01:26.0211044Z)**

```text
http_status: 200
response: density_are=3.2727273; Yield_are_pred=47.8767507; Yield_total_pred=263.3221; harvest_hst=100-110; harvest_date=2024-07-24..2024-08-03; Revenue_gabah=1579932.77; Cost_duck_buy=216000.00; Cost_feed=360000.00; Net_Cash_Contribution_DSS=1948932.77
warnings: survival-assumption warning
comparison: yield_error=+0.87675070; yield_abs_error=0.87675070; harvest=BELOW_WINDOW (95 versus 100-110); density_error=0 within JSON precision; standardized_gabah_revenue_error=+28932.77
result: COMPLETED; canonical field values projected from raw HTTP JSON in Section 17.
```

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

**Hasil backend nyata**

Seluruh field yang semula dicadangkan pada template ini telah diisi pada **Runtime record** tepat di atas. Nilai tersebut berasal dari response HTTP 200 aktual; proyeksi lintas-kasus dan metriknya ada di Section 17.

---

### H07 — Raw Row 43 — I Made Arsania

**Ground truth / source values**

**Runtime record (HTTP nyata, 2026-08-22T12:01:26.0722359Z)**

```text
http_status: 200
response: density_are=4.1666667; Yield_are_pred=47.8767507; Yield_total_pred=172.3563; harvest_hst=100-110; harvest_date=2025-01-09..2025-01-19; Revenue_gabah=1034137.82; Cost_duck_buy=0.00; Cost_feed=300000.00; Net_Cash_Contribution_DSS=1521637.82
warnings: survival-assumption warning
comparison: yield_error=+7.46008403; yield_abs_error=7.46008403; harvest=IN_WINDOW (actual 108); density_error=0 within JSON precision; standardized_gabah_revenue_error=+161137.82
result: COMPLETED; canonical field values projected from raw HTTP JSON in Section 17.
```

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

**Hasil backend nyata**

Seluruh field yang semula dicadangkan pada template ini telah diisi pada **Runtime record** tepat di atas. Nilai tersebut berasal dari response HTTP 200 aktual; proyeksi lintas-kasus dan metriknya ada di Section 17.

---

### H08 — Raw Row 44 — I Ketut Alit Sudarsana

**Ground truth / source values**

**Runtime record (HTTP nyata, 2026-08-22T12:01:26.1213567Z)**

```text
http_status: 200
response: density_are=2.9000000; Yield_are_pred=47.8767507; Yield_total_pred=478.7675; harvest_hst=134; harvest_date=2025-02-09; Revenue_gabah=2872605.04; Cost_duck_buy=0.00; Cost_feed=580000.00; Net_Cash_Contribution_DSS=3815105.04
warnings: Inpari generic-estimate warning; survival-assumption warning
comparison: yield_error=+9.22675070; yield_abs_error=9.22675070; harvest=INPARI_GENERIC_POINT_ERROR (+22 HST versus actual 112); density_error=0; standardized_gabah_revenue_error=+553605.04
result: COMPLETED; canonical field values projected from raw HTTP JSON in Section 17.
```

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

**Hasil backend nyata**

Seluruh field yang semula dicadangkan pada template ini telah diisi pada **Runtime record** tepat di atas. Nilai tersebut berasal dari response HTTP 200 aktual; proyeksi lintas-kasus dan metriknya ada di Section 17.

---

### H09 — Raw Row 51 — I Wayan Suwendhi Artha

**Ground truth / source values**

**Runtime record (HTTP nyata, 2026-08-22T12:01:26.1716425Z)**

```text
http_status: 200
response: density_are=2.0790021; Yield_are_pred=47.8767507; Yield_total_pred=230.2872; harvest_hst=100-110; harvest_date=2025-07-18..2025-07-28; Revenue_gabah=1381723.03; Cost_duck_buy=250000.00; Cost_feed=200000.00; Net_Cash_Contribution_DSS=1456723.03
warnings: survival-assumption warning
comparison: yield_error=+4.42560725; yield_abs_error=4.42560725; harvest=IN_WINDOW (actual 101); density_error=0 within JSON precision; standardized_gabah_revenue_error=+127723.03
result: COMPLETED; canonical field values projected from raw HTTP JSON in Section 17.
```

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

**Hasil backend nyata**

Seluruh field yang semula dicadangkan pada template ini telah diisi pada **Runtime record** tepat di atas. Nilai tersebut berasal dari response HTTP 200 aktual; proyeksi lintas-kasus dan metriknya ada di Section 17.

---

### H10 — Raw Row 53 — I Nyoman Suwitra

**Ground truth / source values**

**Runtime record (HTTP nyata, 2026-08-22T12:01:26.2197646Z)**

```text
http_status: 200
response: density_are=2.0833333; Yield_are_pred=47.8767507; Yield_total_pred=229.8084; harvest_hst=100-110; harvest_date=2025-07-18..2025-07-28; Revenue_gabah=1378850.42; Cost_duck_buy=250000.00; Cost_feed=200000.00; Net_Cash_Contribution_DSS=1453850.42
warnings: survival-assumption warning
comparison: yield_error=+7.77258403; yield_abs_error=7.77258403; harvest=IN_WINDOW (actual 101); density_error=0 within JSON precision; standardized_gabah_revenue_error=+223850.42
result: COMPLETED; canonical field values projected from raw HTTP JSON in Section 17.
```

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

**Hasil backend nyata**

Seluruh field yang semula dicadangkan pada template ini telah diisi pada **Runtime record** tepat di atas. Nilai tersebut berasal dari response HTTP 200 aktual; proyeksi lintas-kasus dan metriknya ada di Section 17.

---

### H11 — Raw Row 55 — Alm. I Ketut Tantra

**Ground truth / source values**

**Runtime record (HTTP nyata, 2026-08-22T12:01:26.2703503Z)**

```text
http_status: 200
response: density_are=2.0289855; Yield_are_pred=47.8767507; Yield_total_pred=165.1748; harvest_hst=100-110; harvest_date=2025-07-28..2025-08-07; Revenue_gabah=991048.74; Cost_duck_buy=175000.00; Cost_feed=140000.00; Net_Cash_Contribution_DSS=1043548.74
warnings: survival-assumption warning
comparison: yield_error=+40.34051882; yield_abs_error=40.34051882; harvest=BELOW_WINDOW (95 versus 100-110); density_error=0 within JSON precision; standardized_gabah_revenue_error=+835048.74
result: COMPLETED; canonical field values projected from raw HTTP JSON in Section 17.
```

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

**Hasil backend nyata**

Seluruh field yang semula dicadangkan pada template ini telah diisi pada **Runtime record** tepat di atas. Nilai tersebut berasal dari response HTTP 200 aktual; proyeksi lintas-kasus dan metriknya ada di Section 17.

---

## 8. Rekap Aktual vs Sistem Setelah Runtime

Isi tabel ini **hanya dari raw response backend aktual**.

| ID | Yield aktual | Yield backend | Error | Abs Error | HST aktual | Harvest backend | Density aktual | Density backend | Std. actual gabah revenue | Backend gabah revenue | Status |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| H01 | 45.82677165 | 47.8767507 | 2.04997905 | 2.04997905 | 93 | 100–110 | 3.14960630 | 3.1496063 | 1746000.00 | 1824104.20 | COMPLETED |
| H02 | 50.00000000 | 47.8767507 | -2.12324930 | 2.12324930 | 95 | 100–110 | 3.13418217 | 3.1341822 | 3063000.00 | 2932929.75 | COMPLETED |
| H03 | 47.19696970 | 47.8767507 | 0.67978100 | 0.67978100 | 116 | 134 | 2.87878788 | 2.8787879 | 1869000.00 | 1895919.33 | COMPLETED |
| H04 | 60.41666667 | 47.8767507 | -12.53991597 | 12.53991597 | 99 | 100–110 | 1.87500000 | 1.8750000 | 1740000.00 | 1378850.42 | COMPLETED |
| H05 | 53.40000000 | 47.8767507 | -5.52324930 | 5.52324930 | 100 | 100–110 | 3.20000000 | 3.2000000 | 3204000.00 | 2872605.04 | COMPLETED |
| H06 | 47.00000000 | 47.8767507 | 0.87675070 | 0.87675070 | 95 | 100–110 | 3.27272727 | 3.2727273 | 1551000.00 | 1579932.77 | COMPLETED |
| H07 | 40.41666667 | 47.8767507 | 7.46008403 | 7.46008403 | 108 | 100–110 | 4.16666667 | 4.1666667 | 873000.00 | 1034137.82 | COMPLETED |
| H08 | 38.65000000 | 47.8767507 | 9.22675070 | 9.22675070 | 112 | 134 | 2.90000000 | 2.9000000 | 2319000.00 | 2872605.04 | COMPLETED |
| H09 | 43.45114345 | 47.8767507 | 4.42560725 | 4.42560725 | 101 | 100–110 | 2.07900208 | 2.0790021 | 1254000.00 | 1381723.03 | COMPLETED |
| H10 | 40.10416667 | 47.8767507 | 7.77258403 | 7.77258403 | 101 | 100–110 | 2.08333333 | 2.0833333 | 1155000.00 | 1378850.42 | COMPLETED |
| H11 | 7.53623188 | 47.8767507 | 40.34051882 | 40.34051882 | 95 | 100–110 | 2.02898551 | 2.0289855 | 156000.00 | 991048.74 | COMPLETED |

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
MedAE_y: 7.46008403 kg/are
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

### Generic Inpari

Backend menggunakan 134 HST. Bandingkan:

```text
error_hst = 134 - HST_actual
```

Interpretasi wajib menyebut bahwa 134 HST merupakan generic estimate, bukan karakteristik universal seluruh Inpari.

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
| B14 | Generic Inpari | `rice_variety=inpari` | 134 HST + calibration warning |

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

- [x] H01–H11 dikirim melalui backend HTTP nyata.
- [x] Raw request dan raw response H01–H11 tersimpan.
- [x] Tabel aktual-vs-sistem diisi dari raw response, bukan kalkulasi manual.
- [x] Runtime replay MAE/RMSE/MedAE yield dihitung dari response backend.
- [x] Calendar actual-vs-system comparison selesai.
- [x] Standardized gabah-revenue comparison selesai.
- [x] Tidak ada survival-vs-sales metric yang disalahartikan sebagai biological validation.
- [x] Synthetic boundary tests B01–B14 dijalankan.
- [x] Invalid-input tests I01–I06 dijalankan.
- [x] Endpoint options/visualization/history diperiksa bila tersedia.
- [x] Repository-wide legacy search selesai.
- [x] Setiap discrepancy dicatat apa adanya.
- [x] Tidak ada skenario sintetis yang disebut data aktual.

---

## 16. Ringkasan Eksekusi

```text
backend_commit: 78f46ebd8004b8ebfdd7559a1c0648482d3eeeaa (worktree memiliki perubahan SoT yang belum di-commit)
backend_start_command: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
base_url: http://127.0.0.1:8000
execution_started_at: 2026-08-22T12:01:25.5856294Z
execution_finished_at: 2026-08-22T12:01:26.2703503Z

historical_replay:
  total: 11
  passed: 11
  failed: 0
  MAE_y: 8.45622456 kg/are
  RMSE_y: 13.63764667 kg/are
  MedAE_y: 7.46008403 kg/are

calendar_comparison:
  result: completed; Sertani 4 IN_WINDOW dan 5 BELOW_WINDOW, Inpari generic error +18 dan +22 HST

standardized_gabah_revenue_comparison:
  result: completed; error per H01–H11 tercatat sebagai diagnostic, bukan accuracy metric Net Cash

synthetic_boundary:
  passed: 14
  failed: 0

invalid_input:
  passed: 6
  failed: 0

options_contract:
  result: HTTP 200; hanya Jajar Legowo 2:1 dan Tegel, tanpa koefisien legacy publik

visualization_contract:
  result: HTTP 200; zona dan waterfall memakai semantic SoT final

history_persistence:
  result: register/login/simulate/list/detail/delete = 201/200/200/200/200/200; raw detail identik dengan raw simulate

legacy_search:
  result: selesai; tidak ada legacy semantic control pada production response path

failed_or_unverified: []
```

Jangan menandai seluruh pengujian PASS sebelum backend dan seluruh HTTP request benar-benar dijalankan.

---

## 17. Runtime Evidence — 22 Agustus 2026

Execution ini dijalankan terhadap service HTTP nyata dengan perintah berikut:

```text
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
endpoint: POST /api/v1/dss/simulate
```

Setiap request H01–H11 memakai payload aktual yang sudah tercantum pada section 7. Tabel berikut adalah proyeksi field pembanding dari raw JSON response HTTP; field sandbox tidak dipakai sebagai metrik historical replay.

| ID | HTTP | density_are | Yield_are_pred | Yield error | Yield_total_pred | Harvest HST backend | Revenue_gabah | Cost_duck_buy | Net_Cash_Contribution_DSS |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| H01 | 200 | 3.1496063 | 47.8767507 | 2.04997905 | 304.0174 | 100–110 | 1824104.20 | 300000.00 | 2174104.20 |
| H02 | 200 | 3.1341822 | 47.8767507 | -2.12324930 | 488.8216 | 100–110 | 2932929.75 | 384000.00 | 3588929.75 |
| H03 | 200 | 2.8787879 | 47.8767507 | 0.67978100 | 315.9866 | 134 | 1895919.33 | 228000.00 | 2285419.33 |
| H04 | 200 | 1.8750000 | 47.8767507 | -12.53991597 | 229.8084 | 100–110 | 1378850.42 | 0.00 | 1671350.42 |
| H05 | 200 | 3.2000000 | 47.8767507 | -5.52324930 | 478.7675 | 100–110 | 2872605.04 | 0.00 | 3912605.04 |
| H06 | 200 | 3.2727273 | 47.8767507 | 0.87675070 | 263.3221 | 100–110 | 1579932.77 | 216000.00 | 1948932.77 |
| H07 | 200 | 4.1666667 | 47.8767507 | 7.46008403 | 172.3563 | 100–110 | 1034137.82 | 0.00 | 1521637.82 |
| H08 | 200 | 2.9000000 | 47.8767507 | 9.22675070 | 478.7675 | 134 | 2872605.04 | 0.00 | 3815105.04 |
| H09 | 200 | 2.0790021 | 47.8767507 | 4.42560725 | 230.2872 | 100–110 | 1381723.03 | 250000.00 | 1456723.03 |
| H10 | 200 | 2.0833333 | 47.8767507 | 7.77258403 | 229.8084 | 100–110 | 1378850.42 | 250000.00 | 1453850.42 |
| H11 | 200 | 2.0289855 | 47.8767507 | 40.34051882 | 165.1748 | 100–110 | 991048.74 | 175000.00 | 1043548.74 |

```text
n_historical_replay: 11
MAE_y: 8.45622456 kg/are
RMSE_y: 13.63764667 kg/are
MedAE_y: 7.46008403 kg/are
```

Calendar diagnostic: Sertani H05, H07, H09, dan H10 berada pada window 100–110; H01, H02, H04, H06, dan H11 berada di bawah window. H03 menghasilkan Inpari generic 134 HST (error +18 terhadap aktual 116); H08 menghasilkan 134 HST (error +22 terhadap aktual 112). Nilai ekonomi bebek dan Net Cash dicatat sebagai context, bukan accuracy metric.

Synthetic contract runtime: B01–B14 seluruhnya HTTP 200. Hasil penting: B01 `TOO_YOUNG`; B02 `RECOMMENDED`; B03 `ABOVE_RECOMMENDED_AGE`; B04 `UNDER_DENSITY`; B05/B06/B09/B10 `RECOMMENDED`; B07/B11 `ABOVE_RECOMMENDED`; B08 `OVERLOAD_HIGH_RISK` dengan `N_survive=48`; B12 `Cost_duck_buy=0`; B13 `Cost_duck_buy=600000`; B14 Inpari menghasilkan 134 HST dan warning generic.

Invalid-input runtime: I01, I02, I03, I04, dan I05 seluruhnya HTTP 400; I06 HTTP 422 dengan field `planting_system`.

Additional HTTP checks: `/api/v1/dss/options` 200; `/api/v1/dss/visualize` 200; authenticated register/login/simulate/list/detail/delete menghasilkan `201/200/200/200/200/200`, dan raw detail response identik dengan raw simulate response.
