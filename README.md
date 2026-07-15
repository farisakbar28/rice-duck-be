# DSS Padi-Bebek Backend

Backend **FastAPI** untuk kalkulator Decision Support System (DSS) padi-bebek. Model DSS Core bersifat **deterministik matematis**: bukan machine learning, bukan IoT, dan tidak mengambil data historis real-time saat simulasi.

## Source of Truth

Source-of-truth aktif dan tunggal:

[`docs/Model Matematika Data Collection DSS Padi Bebek FINAL.docx`](docs/Model Matematika Data Collection DSS Padi Bebek FINAL.docx)

Semua dokumen model lama atau versi "FINAL_BANGET" telah usang dan digantikan oleh DOCX SoT terbaru di atas. Logika runtime DSS Core mutlak mengikuti file DOCX ini.

## Scope Sistem

- **DSS Core**: `POST /api/v1/dss/simulate`, mematuhi struktur output (Core vs Isolated) dari Tabel 3 dan 4 DOCX SoT, serta parameter-parameter konstan dari Bab 4 dan jurnal pelengkap.
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
| `inpari` | 134 | hasil kalibrasi DOCX |

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

### Yield Engine

```text
F_density = 1 - 0.12 * P_under - 0.25 * P_over
F_age = 1 - 0.08 * R_age
F_sys = 1.00 untuk Jarwo, 1.211 untuk Tegel
F_var = 0.80
Yield_are_predict = 47.8767507 * F_density * F_age * F_sys * F_var
Yield_total_predict = Yield_are_predict * A_are
```

Implementasi display membulatkan `Yield_are_predict` ke 2 desimal lalu menghitung total yield 1 desimal.

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

### Cost Engine

```text
Cost_duck_buy = J * p_duck_buy
Cost_feed_isolated = J * 4500 * (1 + 0.75 * P_over + 0.50 * R_age)

R_weed(d) = 0.93 * (1 - exp(-0.35 * d))
Cost_labor_weeding = 26178 * A_are * (1 - R_weed(d))

Cost_infra_net = 0.5 * 289260 * sqrt(A_are)
Cost_infra_cage = 175000
Cost_infra = Cost_infra_net + Cost_infra_cage
```

**Penting:** `Cost_labor_base`, `Cost_labor_tending`, dan `Cost_labor_total` sudah dihapus permanen dari formula Cost Engine sesuai DOCX SoT. Pakan, pemeliharaan infrastruktur, pupuk, penyiangan, dan pestisida diisolasi sepenuhnya sebagai *Isolated Outputs*.

### Ecology Engine

```text
Valuation_weed_eco = (13500 * A_are) * R_weed(d) * (1 - 0.25 * P_over)
```

Basis ekologi murni Rp13.500/are.

### Revenue & Profit

```text
Revenue_gabah = Yield_total_predict * 6000
Revenue_duck = N_survive * 35000
Total_Revenue = Revenue_gabah + Revenue_duck

Cost_pesticide_isolated = 2135 * A_are * (1 - R_pest(d))
Cost_total_cash = Cost_duck_buy

Profit_net_cash = Total_Revenue - Cost_total_cash
Profit_net_full = Profit_net_cash + Valuation_weed_eco
```

