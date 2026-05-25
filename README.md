# Rice Duck DSS Backend

Backend ini adalah fondasi API untuk sistem Decision Support System (DSS) prediksi hasil panen padi-bebek. Sistem berfokus pada evaluasi skenario budidaya aktual, estimasi manfaat agronomis dan ekonomi, serta rekomendasi skenario yang lebih optimal menggunakan algoritma Differential Evolution (DE).

Dokumentasi ini memakai aturan satuan yang konsisten:

- luas lahan hanya dalam `are`,
- hasil panen dan berat hanya dalam `kg` atau turunan yang lebih kecil.

## Tujuan Sistem

Backend ini dirancang untuk:

- menerima input skenario padi-bebek dari pengguna,
- menghitung evaluasi kondisi aktual,
- mengukur tingkat risiko kepadatan bebek,
- memperkirakan hasil panen padi,
- memperkirakan nilai manfaat ekonomi dan ekologis,
- menghasilkan rekomendasi jumlah bebek dan durasi integrasi yang lebih baik,
- menyediakan hasil komparatif yang siap dipakai frontend DSS.

## Ruang Lingkup Backend

Backend menangani:

- validasi input,
- lookup varietas padi,
- lookup sistem tanam,
- perhitungan kepadatan bebek,
- perhitungan jendela aman integrasi,
- perhitungan yield model,
- klasifikasi risiko,
- estimasi manfaat ekonomi,
- estimasi manfaat ekologis,
- optimasi dengan Differential Evolution,
- penyusunan output komparatif,
- histori simulasi.

## Arsitektur Proyek

```text
app/
  api/
    routes/
  core/
  data/
  domain/
  engines/
  repositories/
  schemas/
  services/
tests/
.env.example
requirements.txt
README.md
```

Penjelasan singkat:

- `api`: endpoint FastAPI.
- `core`: konfigurasi aplikasi.
- `data`: seed lookup dan parameter awal.
- `domain`: enum dan model domain.
- `engines`: formula bisnis dan optimizer.
- `repositories`: akses data lookup, parameter, dan histori simulasi.
- `schemas`: kontrak request-response.
- `services`: orkestrasi simulasi.

Mode persistence tahap ini:

- lookup, parameter, dan histori simulasi masih memakai repository in-memory,
- struktur repository sudah dipisah agar mudah diganti ke PostgreSQL atau Supabase.

## Stack Teknis

- Python 3.11+
- FastAPI
- Pydantic v2
- Pydantic Settings
- Uvicorn
- Pytest
- HTTPX

## Model Input

Contoh request minimal:

```json
{
  "duck_count": 40,
  "land_area_are": 10,
  "rice_variety": "ciherang",
  "planting_system": "legowo",
  "planting_date": "2026-06-01"
}
```

Field utama:

- `duck_count`: jumlah bebek aktual.
- `land_area_are`: luas lahan dalam are.
- `rice_variety`: kode varietas padi dari lookup.
- `planting_system`: kode sistem tanam dari lookup.
- `planting_date`: tanggal tanam untuk konversi kalender.
- `parameter_set_id`: identitas parameter set aktif.
- `market_overrides`: override harga pasar jika diperlukan.

## Lookup yang Digunakan

Lookup varietas seed:

- `ciherang`
- `inpari32`
- `ratoon`
- `lokal`

Lookup sistem tanam seed:

- `konvensional`
- `legowo`
- `sri`
- `double-transplant`

Lookup sistem tanam mengembalikan:

- `k_max_per_are`
- `f_yield`

Lookup seed ini tetap harus divalidasi atau dikalibrasi dengan data lokal penelitian.

## Formula Inti

### Kepadatan bebek aktual

```text
d_actual = J / A
```

Keterangan:

- `J`: jumlah bebek.
- `A`: luas lahan dalam are.
- `d_actual`: kepadatan bebek per are.

### Jendela aman integrasi

```text
safe_window_days = min(HST_heading - HST_entry, t_max_eff)
```

Keterangan:

- `HST_entry`: hari setelah tanam saat bebek mulai masuk.
- `HST_heading`: batas akhir sebelum heading stage.
- `t_max_eff`: batas efisiensi ekonomi maksimum.

### Model yield dasar

Backend memakai bentuk yang sudah dinormalisasi ke `kg/are`:

```text
x(d,t) = (-1.03 d^2 + 2.6314 d + 75.694) * exp(-((t - 80)^2) / (2 * 80^2))
```

Keterangan:

- `d`: kepadatan bebek per are.
- `t`: durasi integrasi bebek dalam hari.
- `x(d,t)`: hasil panen dasar dalam `kg/are`.

### Penalti kepadatan

```text
if d <= K_max:
  P_rate = 0
else:
  P_rate = min(0.5, ((d - K_max) / K_max) * 0.5)
```

Yield setelah penalti:

```text
x_penalized = x(d,t) * (1 - P_rate)
```

### Yield akhir

```text
x_final_kg_per_are = x_penalized * f_yield
```

### Klasifikasi risiko

```text
NORMAL  if d <= K_max
WASPADA if K_max < d <= 1.3 * K_max
BAHAYA  if d > 1.3 * K_max
```

Semua threshold kepadatan dinyatakan dalam `bebek/are`.

### Nilai tambah beras

```text
delta_v_rice = ((p * x_final) - (p0 * x0)) * A
```

Keterangan:

- `p`: harga beras sistem padi-bebek dalam `Rp/kg`.
- `p0`: harga beras konvensional dalam `Rp/kg`.
- `x_final`: yield akhir dalam `kg/are`.
- `x0`: baseline yield konvensional dalam `kg/are`.
- `A`: luas lahan dalam are.

### Nilai ekologis pupuk

```text
v_eco1 = ((0.02 * t) - 0.6) * (0.107 * P_N + 0.424 * P_P + 0.058 * P_K) * d * lambda * A
```

### Nilai ekologis pengendalian hayati

Komponen ini tetap memakai basis literatur yang berasal dari skala area yang lebih besar. Backend mengonversi kepadatan `bebek/are` ke basis internal literatur hanya di dalam engine, tetapi kontrak API tetap memakai `are`.

```text
if d is above the literature threshold equivalent to 3 ducks/are:
  v_eco2 = logistic_model(...)
else:
  v_eco2 = linear_interpolation(...)
```

### Nilai ekonomi bebek

Implementasi seed saat ini memakai pendekatan `local_gross`:

```text
duck_revenue = harvested_ducks * average_duck_sale_weight_kg * duck_price
duck_net_value = duck_revenue - feed_penalty
```

### Objective function

```text
total_benefit = delta_v_rice + duck_net_value + v_eco
```

Fungsi ini dipakai sebagai objective pada mode optimasi proaktif.

## Differential Evolution

Variabel keputusan:

- `d`: kepadatan bebek per are.
- `t`: durasi integrasi bebek dalam hari.

Domain optimasi:

```text
0 <= d <= K_max
1 <= t <= safe_window_days
```

Parameter seed:

```text
population_size = 40
mutation_factor = 0.8
crossover_rate = 0.9
max_generations = 150
epsilon = 1e-5
```

File implementasi:

- [app/engines/differential_evolution.py](app/engines/differential_evolution.py)

## Endpoint API

### Health check

```text
GET /api/v1/health
```

### Lookup varietas padi

```text
GET /api/v1/lookups/rice-varieties
```

### Lookup sistem tanam

```text
GET /api/v1/lookups/planting-systems
```

### Parameter aktif

```text
GET /api/v1/parameters/active
```

### Evaluasi simulasi

```text
POST /api/v1/simulations/evaluate
```

### List histori simulasi

```text
GET /api/v1/simulations
```

### Detail histori simulasi

```text
GET /api/v1/simulations/{simulation_id}
```

Response utama evaluasi berisi:

- `simulation_id`
- `created_at`
- `input_summary`
- `agronomic_context`
- `reactive_result`
- `proactive_result`
- `comparison`
- `optimization_meta`
- `calculation_status`
- `assumptions`

## Bentuk Output

Kontrak output utama sekarang mengikuti satuan berikut:

- area: `are`
- density: `duck/are`
- yield: `kg/are` dan `kg total`
- nutrisi tanah: `kg/are` dan `kg total`
- harga dan manfaat ekonomi: `Rp`

Response `evaluate` juga membawa:

- context agronomis yang dipakai mesin, seperti `HST_entry`, `HST_heading`, `safe_window_days`, `k_max_per_are`, dan `f_yield`,
- risk summary terstruktur untuk skenario aktual dan rekomendasi,
- metadata optimasi, termasuk batas pencarian, jumlah generasi yang dieksekusi, status konvergensi, dan objective terbaik.

Backend mengembalikan area dalam `are` serta hasil panen dalam `kg/are` dan `kg total`.

## Setup Lokal

Prasyarat:

- Python 3.11 atau lebih baru
- `pip`

### 1. Buat virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependency

```powershell
pip install -r requirements.txt
```

### 3. Siapkan environment

```powershell
Copy-Item .env.example .env
```

### 4. Jalankan server

```powershell
uvicorn app.main:app --reload
```

Alamat default:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

### 5. Jalankan test

```powershell
pytest
```

## File Kunci

- [app/main.py](app/main.py)
- [app/core/config.py](app/core/config.py)
- [app/services/simulation_service.py](app/services/simulation_service.py)
- [app/engines/formula_engine.py](app/engines/formula_engine.py)
- [app/engines/differential_evolution.py](app/engines/differential_evolution.py)
- [tests/test_api.py](tests/test_api.py)

## Batas Validasi Ilmiah

Beberapa batas penting yang harus dijaga:

1. Koefisien yield dasar tetap perlu kalibrasi dengan data lokal Indonesia.
2. Lookup `K_max` dan `f_yield` tetap harus divalidasi terhadap data lapangan.
3. Parameter harga pasar tidak boleh dianggap universal; harus mengikuti lokasi, musim, dan periode observasi.
4. Output emisi belum layak dipakai sebagai angka final tanpa konversi fluks musiman dan baseline lokal.
5. Output finansial tetap harus diposisikan sebagai proyeksi model.
6. Hasil backend tidak menggantikan validasi agronomi, ekonomi, dan pakar lapangan.

## Pengembangan Lanjutan

Area pengembangan berikut yang relevan:

1. integrasi PostgreSQL atau Supabase,
2. migration dan repository persistence,
3. versioning parameter set,
4. seed data harga lokal dan lookup lapangan,
5. pengujian formula berbasis skenario referensi penelitian,
6. modul admin untuk kalibrasi parameter,
7. ekstensi model emisi saat data pendukung tersedia.
