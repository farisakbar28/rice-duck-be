# DSS Padi-Bebek Backend

Backend **FastAPI** untuk kalkulator Decision Support System (DSS) padi-bebek. Model DSS Core bersifat **deterministik matematis**: bukan machine learning, bukan IoT, dan tidak mengambil data historis real-time saat simulasi.

## Source of Truth

Source-of-truth aktif dan tunggal:

[`docs/Model Matematika Data Collection DSS Padi Bebek FINAL.md`](docs/Model Matematika Data Collection DSS Padi Bebek FINAL.md)

Semua dokumen model lama atau versi "FINAL_BANGET" telah usang dan digantikan oleh SoT terbaru di atas. Logika runtime DSS Core mutlak mengikuti file SoT ini.

## Scope Sistem

- **DSS Core**: `POST /api/v1/dss/simulate`, mematuhi struktur output (Core vs Isolated) dari SoT Bagian 5, serta parameter-parameter konstan dari Bab 4 dan jurnal pelengkap.
- **Optimizer**: `POST /api/v1/optimizer/recommend`, fitur produk terpisah di luar scope SoT DSS Core.
- **History DB**: struktur history menyimpan kolom eksplisit (termasuk isolated outputs) untuk audit komprehensif.

## Stack

- Python 3.12+
- FastAPI
- Pydantic
- SQLite
- Pytest

## Endpoint Utama

| Method | Path | Auth | Keterangan |
|---|---|---|---|
| `GET` | `/health` | tidak | Health check |
| `POST` | `/api/v1/auth/register` | tidak | Registrasi user |
| `POST` | `/api/v1/auth/login` | tidak | Login JWT |
| `GET` | `/api/v1/auth/me` | Bearer | Data user aktif |
| `GET` | `/api/v1/dss/options` | tidak | Dropdown varietas dan sistem tanam |
| `POST` | `/api/v1/dss/simulate` | opsional | Simulasi DSS Core |
| `GET` | `/api/v1/dss/histories` | Bearer | Daftar history, saat ini stub kosong |
| `GET` | `/api/v1/dss/histories/{id}` | Bearer | Detail history, saat ini stub not found |
| `DELETE` | `/api/v1/dss/histories/{id}` | Bearer | Hapus history, stub response |
| `POST` | `/api/v1/optimizer/recommend` | tidak | Optimizer stand-alone stub, di luar SoT |

## Input DSS Core

Endpoint:

```http
POST /api/v1/dss/simulate
Content-Type: application/json
Authorization: Bearer <token>   # opsional
```

Payload mengikuti 6 input manual Tabel 2.1 plus harga beli bebek opsional:

| Field | Tipe | Satuan | Keterangan |
|---|---:|---|---|
| `land_area_are` | float `> 0` | are | Luas lahan aktif yang dimasuki bebek |
| `duck_count` | integer `> 0` | ekor | Populasi bibit bebek (`J`) |
| `rice_variety` | string | kategori | `sertani` atau `inpari` |
| `planting_system` | string | kategori | `jajar_legowo` atau `tegel` |
| `planting_date` | date | `YYYY-MM-DD` | Tanggal tanam |
| `duck_age_days` | integer `> 0` | hari | Umur bebek saat masuk sawah (`U_duck`) |
| `duck_buy_price_rp_per_duck` | float `> 0`, optional | Rp/ekor | Override harga beli bebek; default Rp25.000 |

Contoh golden case SoT:

```json
{
  "land_area_are": 10,
  "duck_count": 50,
  "rice_variety": "sertani",
  "planting_system": "jajar_legowo",
  "planting_date": "2026-01-01",
  "duck_age_days": 14
}
```

## Lookup Options

Endpoint:

```http
GET /api/v1/dss/options
```

Nilai aktif:

| Varietas | `hst_panen` | Catatan |
|---|---:|---|
| `sertani` | 114 | mencakup Sertani/Seratih |
| `inpari` | 134 | hasil kalibrasi SoT |

| Sistem tanam | `k_safe_are` | `F_sys` |
|---|---:|---:|
| `jajar_legowo` | 4.0 | 1.00 |
| `tegel` | 3.0 | 1.211 |

Beberapa field deprecated tetap ada di response options untuk backward compatibility (`hst_masuk`, `hst_heading`, `harvest_age_days`, `k_max_are`, `f_yield`), tetapi code path baru memakai field canonical `hst_panen`, `k_safe_are`, dan `F_sys`.

## Formula Runtime DSS Core

### Age Engine

```text
R_age = 0.35 jika U_duck < 14
R_age = 0.15 jika 14 <= U_duck <= 29
R_age = 0.05 jika U_duck >= 30
```

`age_status`:

- `AGE_BUY_RANGE` untuk umur 14-29 hari.
- `AGE_BUY_RANGE_WARNING` jika < 14 hari.
- `ADAPTED_FULLY` jika >= 30 hari.

### Density Engine

```text
d = J / A_are
K_safe = 4 untuk Jarwo, 3 untuk Tegel
P_over = max(0, min(1, (d - K_safe) / (8 - K_safe)))
P_under = max(0, (2 - d) / 2)
```

`density_status`:

- `WARNING_DENSITY` jika `P_over > 0`
- `WARNING_UNDER_DENSITY` jika `P_under > 0`
- `SAFE` jika tidak ada penalty

### Calendar Engine

```text
D_masuk_bebek = D_tanam + 21 hari
D_tarik_bebek = D_tanam + 65 hari
t_active = 44 hari
D_panen_gabah = D_tanam + HST_panen
```

`HST_panen`: Sertani/Seratih = 114, Inpari = 134.

### Survival Engine

```text
lambda_eff = 0.78125 * (1 - 0.50 * R_age) * (1 - 0.45 * P_over)
N_survive = floor(J * lambda_eff)
```

Output `N_survive` memakai `floor`, bukan `round`, untuk prinsip kehati-hatian.

### Yield Engine (SoT v2 — Economic Differential-Costing Engine)

```text
F_density_bio(d) = 1 + 0.15 * (1 - exp(-d / 4)) - 0.25 * (max(0, (d - 8) / 8))^2
F_age = 1 - 0.08 * R_age
F_sys = 1.00 untuk Jarwo, 1.211 untuk Tegel
F_var = 1.00
Y0 = 47.8767507 kg/are (lokal-validated)

Yield_are_predict = Y0 * F_density_bio(d) * F_age * F_sys * F_var
Yield_total_predict = Yield_are_predict * A_are
```

**Catatan presisi:** Semua perhitungan engine menggunakan `decimal.Decimal` dengan presisi 50 digit (IEEE 754 compliance). Fungsi eksponensial menggunakan deret Taylor 100 suku; akar kuadrat menggunakan Newton-Raphson 50 iterasi. **Tidak ada pembulatan di tengah kalkulasi** — pembulatan hanya terjadi pada layer serialisasi JSON response (2 desimal untuk yield are, 1 desimal untuk yield total).

### Material Engine

```text
sub_base = max(0, 0.02 * t_active - 0.6)
N_duck = sub_base * 0.049 * (J * lambda_eff)
P_duck = sub_base * 0.072 * (J * lambda_eff)
K_duck = sub_base * 0.032 * (J * lambda_eff)

N_need = 1.1761 * A_are
P_need = 0.2745 * A_are
K_need = 0.2745 * A_are

N_rem = max(0, N_need - N_duck)
P_rem = max(0, P_need - P_duck)
K_rem = max(0, K_need - K_duck)

Q_phonska = P_rem / 0.04364
Q_urea = max(0, N_rem - Q_phonska * 0.15) / 0.46
Q_kcl = max(0, K_rem - Q_phonska * 0.09961) / 0.49806

Cost_fertilizer_total = Q_phonska * 1840 + Q_urea * 1800 + Q_kcl * 9500
```

HET pupuk:

| Pupuk | HET |
|---|---:|
| Urea | Rp1.800/kg |
| Phonska | Rp1.840/kg |
| KCl | Rp9.500/kg |

### Cost Engine (Two-Tier Architecture)

**Core Validated Output Group (Active Circuit):**
```text
Cost_duck_buy = J * p_duck_buy
Cost_total_cash = Cost_duck_buy
```

**Empirically Uncorrelated Isolated Output Group (Sandbox Circuit):**
```text
Cost_feed_isolated = J * 4500 * (1 + 0.75 * P_over + 0.50 * R_age)

R_weed(d) = 0.93 * (1 - exp(-0.35 * d))
Cost_weeding_isolated = 26178 * A_are * (1 - R_weed(d))

R_pest(d) = 0.80 * (1 - exp(-0.35 * d))
Cost_pesticide_isolated = 2135 * A_are * (1 - R_pest(d))

Cost_infra_net_isolated = 0.5 * 289260 * sqrt(A_are)
Cost_infra_cage_isolated = 175000
Cost_infra_isolated = Cost_infra_net_isolated + Cost_infra_cage_isolated
```

**Penting:** Semua biaya *Sandbox* (`Cost_weeding_isolated`, `Cost_pesticide_isolated`, `Cost_infra_isolated`, `Cost_fertilizer_isolated`, `Cost_feed_isolated`) **diisolasi sepenuhnya** dan **TIDAK BOLEH** mengurangi `Profit_net_cash` atau menjadi bagian dari `Cost_total_cash`. `Cost_total_cash` murni hanya berisi `Cost_duck_buy`.

### Revenue & Profit (Core Circuit Only)

```text
Revenue_gabah = Yield_total_predict * 6000
Revenue_duck = N_survive * 35000
Total_Revenue = Revenue_gabah + Revenue_duck

Profit_net_cash = Total_Revenue - Cost_total_cash
```

**Catatan:** `Valuation_weed_eco` (Ecology Engine) dan `Profit_net_full` **telah dihapus total** dari SoT v2. Fokus sistem adalah pada **likuiditas tunai nyata** (`Profit_net_cash`) saja.

## Output Response Schema (DSSSimulationResponse)

### Core Validated Output Group
| Field | Tipe | Deskripsi |
|---|---|---|
| `density_status` | string | `SAFE` / `WARNING_DENSITY` / `WARNING_UNDER_DENSITY` |
| `age_status` | string | `AGE_BUY_RANGE` / `AGE_BUY_RANGE_WARNING` / `ADAPTED_FULLY` |
| `D_masuk_bebek` | date | Tanggal masuk bebek |
| `D_tarik_bebek` | date | Tanggal tarik bebek |
| `D_panen_gabah` | date | Tanggal panen gabah |
| `N_survive` | float | Populasi bebek survive (floor) |
| `Yield_are_predict` | float | Yield prediksi per are (2 desimal) |
| `Yield_total_predict` | float | Yield prediksi total (1 desimal) |
| `Revenue_gabah` | float | Pendapatan gabah |
| `Revenue_duck` | float | Pendapatan bebek |
| `Total_Revenue` | float | Total pendapatan |
| `Cost_duck_buy` | float | Biaya beli bebek |
| `Cost_total_cash` | float | **= Cost_duck_buy** (biaya inti kas) |
| `Profit_net_cash` | float | **Likuiditas tunai bersih** = Total_Revenue - Cost_total_cash |
| `F_sys` | float | Faktor sistem tanam (1.00 / 1.211) |

### Empirically Uncorrelated Isolated Output Group (Indicative)
| Field | Tipe | Deskripsi |
|---|---|---|
| `Cost_feed_isolated` | float | Biaya pakan bebek (indikatif) |
| `Cost_weeding_isolated` | float | Biaya penyiangan (indikatif) |
| `Cost_pesticide_isolated` | float | Biaya pestisida (indikatif) |
| `Cost_infra_isolated` | float | Total biaya infrastruktur (indikatif) |
| `Cost_fertilizer_isolated` | float | Total biaya pupuk (indikatif) |
| `Cost_infra_net_isolated` | float | Biaya jaring (indikatif) |
| `Cost_infra_cage_isolated` | float | Biaya kandang (indikatif) |
| `Cost_fert_urea_isolated` | float | Biaya Urea (indikatif) |
| `Cost_fert_phonska_isolated` | float | Biaya Phonska (indikatif) |
| `Cost_fert_kcl_isolated` | float | Biaya KCl (indikatif) |

## Contoh Response (Golden Case)

```json
{
  "density_status": "WARNING_DENSITY",
  "age_status": "AGE_BUY_RANGE",
  "D_masuk_bebek": "2026-01-22",
  "D_tarik_bebek": "2026-03-07",
  "D_panen_gabah": "2026-04-25",
  "N_survive": 32.0,
  "Yield_are_predict": 52.36,
  "Yield_total_predict": 523.6,
  "Revenue_gabah": 3141883.01,
  "Revenue_duck": 1120000.0,
  "Total_Revenue": 4261883.01,
  "Cost_duck_buy": 1250000.0,
  "Cost_feed_isolated": 284062.5,
  "Cost_weeding_isolated": 60630.8,
  "Cost_pesticide_isolated": 7238.06,
  "Cost_infra_isolated": 632360.22,
  "Cost_fertilizer_isolated": 104554.64,
  "Cost_infra_net_isolated": 457360.22,
  "Cost_infra_cage_isolated": 175000.0,
  "Cost_fert_urea_isolated": 16074.77,
  "Cost_fert_phonska_isolated": 88479.87,
  "Cost_fert_kcl_isolated": 0.0,
  "Cost_total_cash": 1250000.0,
  "Profit_net_cash": 3011883.01,
  "F_sys": 1.0
}
```