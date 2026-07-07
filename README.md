# DSS Padi-Bebek Backend

Backend **FastAPI** untuk kalkulator Decision Support System (DSS) padi-bebek. Model DSS Core bersifat **deterministik matematis**: bukan machine learning, bukan IoT, dan tidak mengambil data historis real-time saat simulasi.

## Source of Truth

Source-of-truth aktif dan tunggal:

[`docs/Model_Matematika_Data_Collection_DSS_Padi_Bebek_FINAL_BANGET.md`](docs/Model_Matematika_Data_Collection_DSS_Padi_Bebek_FINAL_BANGET.md)

Dokumen model lama, termasuk `Model_Matematika_Data_Collection_DSS_Padi_Bebek_FINAL_terbaru.md`, hanya dipakai sebagai arsip historis. Logika runtime DSS Core wajib mengikuti `FINAL_BANGET`.

## Scope Sistem

- **DSS Core**: `POST /api/v1/dss/simulate`, mengikuti `FINAL_BANGET` Tabel 2.1, Tabel 2.2, Tabel 2.3, dan Catatan Finalisasi 1-12.
- **Optimizer**: `POST /api/v1/optimizer/recommend`, fitur produk terpisah di luar scope SoT DSS Core. Saat ini stub stand-alone dan boleh mempertahankan model legacy/Xiong-style tanpa mempengaruhi DSS Core.
- **History DB**: struktur history menyimpan kolom eksplisit untuk audit. Kolom DB `cost_labor_tending` tetap ada sebagai deprecated compatibility field, default `0`, dan tidak diekspos API.

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
| `sertani` | 99 | mencakup Sertani/Seratih |
| `inpari` | 112 | hasil kalibrasi sekunder |

| Sistem tanam | `k_safe_are` | `F_sys` |
|---|---:|---:|
| `jajar_legowo` | 4.0 | 1.00 |
| `tegel` | 3.0 | 0.95 |

Beberapa field deprecated tetap ada di response options untuk backward compatibility (`hst_masuk`, `hst_heading`, `harvest_age_days`, `k_max_are`, `f_yield`), tetapi code path baru memakai field canonical `hst_panen`, `k_safe_are`, dan `F_sys`.

## Formula Runtime DSS Core

### Age Engine

```text
R_age = 0.35 jika U_duck < 14
R_age = 0.15 jika 14 <= U_duck <= 20
R_age = 0.05 jika U_duck > 20
```

`age_status`:

- `AGE_BUY_RANGE` untuk umur 14-20 hari.
- `AGE_BUY_RANGE_WARNING` untuk umur di luar rentang itu.

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

`HST_panen`: Sertani/Seratih = 99, Inpari = 112.

### Survival Engine

```text
lambda_eff = 0.67 * (1 - 0.50 * R_age) * (1 - 0.45 * P_over)
N_survive = floor(J * lambda_eff)
```

Output `N_survive` memakai `floor`, bukan `round`, untuk prinsip kehati-hatian.

### Yield Engine

```text
F_density = 1 - 0.12 * P_under - 0.25 * P_over
F_age = 1 - 0.08 * R_age
F_sys = 1.00 untuk Jarwo, 0.95 untuk Tegel
F_var = 1.00
Yield_are_predict = 48.039 * F_density * F_age * F_sys * F_var
Yield_total_predict = Yield_are_predict * A_are
```

Implementasi display meng-floor `Yield_are_predict` ke 2 desimal lalu menghitung total yield 1 desimal.

### Material Engine

```text
N_duck = max(0, 0.02 * t_active - 0.6) * 0.107 * (J * lambda_eff)
P_duck = 0.28 * 0.424 * (J * lambda_eff)       # untuk t_active=44
K_duck = 0.28 * 0.058 * (J * lambda_eff)       # untuk t_active=44

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
Cost_feed = J * 5000 * (1 + 0.75 * P_over + 0.50 * R_age)

R_weed(d) = 0.95 * (1 - exp(-0.35 * d))
Cost_labor_base = 47527 * A_are
Cost_labor_weed_hired = 30539 * A_are * (1 - R_weed(d))
Cost_labor_total = Cost_labor_base + Cost_labor_weed_hired

Cost_infra_net_raw = 0.5 * 49435 * sqrt(A_are)
Cost_infra_cage_raw = 0.5 * 8333 * J
Cost_infra = max(58333, Cost_infra_net_raw + Cost_infra_cage_raw)
```

Jika floor infra aktif dan raw sum `< 58333`, `Cost_infra_net` dan `Cost_infra_cage` diskalakan proporsional agar:

```text
Cost_infra_net + Cost_infra_cage = Cost_infra
```

Jika raw sum `<= 0`, implementasi membagi floor 50/50 sebagai edge-case interim; endpoint normal menolak `A_are <= 0`.

**Penting:** `Cost_labor_tending` sudah dihapus permanen dari formula Cost Engine sesuai Catatan Finalisasi poin 12 `FINAL_BANGET`. Field tersebut tidak ada di response API DSS Core.

### Ecology Engine

```text
Valuation_weed_eco = (0.29 * Cost_labor_base) * R_weed(d) * (1 - 0.25 * P_over)
```

Basis ekologi adalah `Cost_labor_base` murni:

- tanpa `Cost_labor_weed_hired`
- tanpa `Cost_labor_tending`

Ini mencegah double-counting manfaat gulma.

### Revenue & Profit

```text
Revenue_gabah = Yield_total_predict * 6000
Revenue_duck = N_survive * 35000
Total_Revenue = Revenue_gabah + Revenue_duck

Cost_pesticide = 6440
Cost_total_cash = Cost_duck_buy + Cost_feed + Cost_labor_total + Cost_infra + Cost_fertilizer_total + Cost_pesticide

Profit_net_cash = Total_Revenue - Cost_total_cash
Profit_net_full = Profit_net_cash + Valuation_weed_eco
```

## Response DSS Core

`POST /api/v1/dss/simulate` mengembalikan object flat sesuai Tabel 2.3:

| Field | Satuan/Keterangan |
|---|---|
| `density_status` | status kepadatan |
| `age_status` | status umur bebek |
| `D_masuk_bebek` | tanggal lepas bebek |
| `D_tarik_bebek` | tanggal tarik bebek |
| `D_panen_gabah` | tanggal panen gabah |
| `N_survive` | prediksi bebek hidup, floor |
| `Yield_are_predict` | kg/are |
| `Yield_total_predict` | kg |
| `Revenue_gabah` | Rp |
| `Revenue_duck` | Rp |
| `Total_Revenue` | Rp |
| `Cost_duck_buy` | Rp |
| `Cost_feed` | Rp |
| `Cost_labor_base` | Rp |
| `Cost_labor_weed_hired` | Rp |
| `Cost_labor_total` | Rp |
| `Cost_infra_net` | Rp |
| `Cost_infra_cage` | Rp |
| `Cost_infra` | Rp |
| `Cost_fertilizer_total` | Rp |
| `Cost_fert_urea` | Rp |
| `Cost_fert_phonska` | Rp |
| `Cost_fert_kcl` | Rp |
| `Cost_pesticide` | Rp |
| `Cost_total_cash` | Rp |
| `Profit_net_cash` | Rp |
| `Valuation_weed_eco` | Rp |
| `Profit_net_full` | Rp |
| `F_sys` | faktor sistem tanam |

Tidak ada field optimizer (`recommended_scenario`, `optimality_assessment`, `comparison`, `trace`, dll.) di response DSS Core.

Tidak ada field `Cost_labor_tending` di response DSS Core.

## Golden Case FINAL_BANGET

Payload:

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

Output penting yang harus cocok:

| Field | Nilai |
|---|---:|
| `density_status` | `WARNING_DENSITY` |
| `age_status` | `AGE_BUY_RANGE` |
| `D_masuk_bebek` | `2026-01-22` |
| `D_tarik_bebek` | `2026-03-07` |
| `D_panen_gabah` | `2026-04-10` |
| `N_survive` | 27 |
| `Yield_are_predict` | 44.49 |
| `Yield_total_predict` | 444.9 |
| `Revenue_gabah` | 2,669,400 |
| `Revenue_duck` | 945,000 |
| `Total_Revenue` | 3,614,400 |
| `Cost_duck_buy` | 1,250,000 |
| `Cost_feed` | 315,625 |
| `Cost_labor_base` | 475,270 |
| `Cost_labor_weed_hired` | 65,685 |
| `Cost_labor_total` | 540,955 |
| `Cost_infra_net` | 78,163 |
| `Cost_infra_cage` | 208,325 |
| `Cost_infra` | 286,488 |
| `Cost_fertilizer_total` | 161,500 |
| `Cost_pesticide` | 6,440 |
| `Cost_total_cash` | 2,561,008 |
| `Profit_net_cash` | 1,053,392 |
| `Valuation_weed_eco` | 101,422 |
| `Profit_net_full` | 1,154,814 |

Angka exact runtime dapat memiliki pecahan desimal kecil karena operasi floating-point; test memakai toleransi rupiah kecil sesuai golden case.

## Optimizer Stand-Alone

Endpoint:

```http
POST /api/v1/optimizer/recommend
```

Status saat ini:

- Out-of-scope dari `FINAL_BANGET` DSS Core.
- Stub terstruktur, bukan kalkulator SoT.
- Tidak boleh mengubah formula DSS Core.
- Response memiliki `scope_notice` yang menyatakan optimizer di luar scope dokumen DSS Core.

Gunakan `/api/v1/dss/simulate` untuk kalkulasi operasional yang mengikuti `FINAL_BANGET`.

## Auth

Register:

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "name": "Pak Wayan",
  "email": "wayan@sawah.id",
  "password": "password123"
}
```

Login:

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
  "user": {
    "id": "...",
    "name": "Pak Wayan",
    "email": "wayan@sawah.id"
  }
}
```

Token bersifat opsional untuk `/api/v1/dss/simulate`. Jika token dikirim valid, service menerima `user_id`; penyimpanan history aktif belum diimplementasikan di service saat ini.

## Struktur Project

```text
app/
├── api/
│   ├── router.py
│   └── routes/
│       ├── auth.py
│       ├── dss.py
│       ├── health.py
│       └── optimizer.py
├── core/
│   ├── config.py
│   ├── database.py
│   ├── exceptions.py
│   └── security.py
├── data/seed.py
├── domain/models.py
├── engines/
│   ├── formula_engine.py
│   └── impact_engine.py
├── repositories/
├── schemas/
│   ├── auth.py
│   ├── dss.py
│   └── optimizer.py
└── services/
    ├── auth_service.py
    └── simulation_service.py

docs/
├── Model_Matematika_Data_Collection_DSS_Padi_Bebek_FINAL_BANGET.md
└── Model_Matematika_Data_Collection_DSS_Padi_Bebek_FINAL_terbaru.md

tests/
├── test_api.py
├── test_formula_engine.py
└── test_sot_golden_case.py
```

## File Kode Utama

| Area | File |
|---|---|
| Orkestrasi simulasi | `app/services/simulation_service.py` |
| Age, Density, Calendar, Survival, Yield | `app/engines/formula_engine.py` |
| Cost, Material, Ecology | `app/engines/impact_engine.py` |
| Request/response DSS | `app/schemas/dss.py` |
| Seed lookup dan constants | `app/data/seed.py` |
| Route DSS | `app/api/routes/dss.py` |
| Route optimizer stand-alone | `app/api/routes/optimizer.py` |

## Menjalankan Lokal

Buat virtual environment:

```bash
python -m venv .venv
```

Aktifkan di Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependency:

```bash
pip install -r requirements.txt
```

Salin env bila diperlukan:

```powershell
copy .env.example .env
```

Jalankan server:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Menjalankan Test

Semua test:

```bash
python -m pytest -q
```

Golden SoT:

```bash
python -m pytest tests/test_sot_golden_case.py -q
```

API integration:

```bash
python -m pytest tests/test_api.py -q
```

Formula/engine:

```bash
python -m pytest tests/test_formula_engine.py -q
```

## Guardrail Penting

- Jangan mengubah formula DSS Core tanpa merujuk langsung ke `FINAL_BANGET`.
- Jangan mengembalikan `Cost_labor_tending` ke response API.
- Jangan memakai `Cost_labor_total` sebagai basis `Valuation_weed_eco`; basis wajib `Cost_labor_base`.
- Jangan menduplikasi rumus `R_weed(d)`; Cost Engine dan Ekologi Engine harus memakai fungsi yang sama.
- Jangan mencampur optimizer legacy dengan DSS Core.
- Jangan drop kolom DB `cost_labor_tending` tanpa migrasi terpisah dan keputusan eksplisit; kolom itu hanya compatibility historis.

## Status Verifikasi Saat Ini

Test suite yang relevan mengunci:

- Formula Tabel 2.2.
- Output Tabel 2.3.
- Golden case `A_are=10, J=50, Sertani, Jarwo, U_duck=14`.
- `N_survive` memakai floor.
- `Cost_labor_tending` tidak ada di response API.
- `R_weed(d)` memakai faktor asimtot `0.95`.
- `Valuation_weed_eco` memakai `Cost_labor_base`.

Perintah verifikasi utama:

```bash
python -m pytest -q
```
