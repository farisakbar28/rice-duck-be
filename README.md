# Rice Duck DSS Backend

Backend ini adalah fondasi API untuk sistem Decision Support System (DSS) prediksi hasil panen padi-bebek. Fokus utamanya adalah mengevaluasi skenario aktual petani, menghitung proyeksi manfaat agronomis dan ekonomi, lalu menghasilkan rekomendasi skenario yang lebih optimal dengan algoritma Differential Evolution (DE).

Dokumentasi ini hanya menjelaskan ruang lingkup backend, model domain, formula inti, struktur proyek, endpoint, setup lokal, serta batas validasi ilmiah yang perlu dijaga selama pengembangan penelitian.

## Tujuan Sistem

Backend ini dirancang untuk:

- menerima input skenario budidaya padi-bebek,
- menghitung evaluasi kondisi aktual,
- mengukur tingkat risiko kepadatan bebek,
- memperkirakan yield padi,
- memperkirakan nilai manfaat ekonomi dan ekologis,
- mencari kombinasi kepadatan bebek dan durasi integrasi yang lebih baik,
- menyiapkan hasil komparatif yang siap dipakai frontend DSS.

## Ruang Lingkup Backend

Backend menangani area berikut:

- validasi input petani,
- lookup varietas padi,
- lookup sistem tanam,
- konversi satuan area,
- perhitungan kepadatan bebek,
- perhitungan jendela aman integrasi bebek,
- perhitungan yield model,
- klasifikasi risiko,
- estimasi manfaat ekonomi,
- estimasi manfaat ekologis,
- optimasi dengan Differential Evolution,
- penyusunan output komparatif untuk dashboard.

## Prinsip Model

Beberapa prinsip yang dipakai dalam backend ini:

1. Semua perhitungan internal area dinormalisasi ke hektar.
2. Output tetap dapat ditampilkan dalam hektar dan are agar mudah dipakai pada dashboard petani.
3. Variabel `t` diperlakukan sebagai durasi integrasi bebek dalam hari, bukan HST absolut.
4. Output finansial dan ekologis diposisikan sebagai hasil estimasi model, bukan angka pasti lapangan.
5. Parameter pasar, lookup agronomi, dan koefisien model harus dianggap dapat dikalibrasi ulang.

## Arsitektur Proyek

Struktur proyek:

```text
app/
  api/
    routes/
  core/
  data/
  domain/
  engines/
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
- `schemas`: kontrak request-response.
- `services`: orkestrasi evaluasi simulasi.
- `tests`: test dasar API.

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
  "land_area": 10,
  "land_area_unit": "are",
  "rice_variety": "ciherang",
  "planting_system": "legowo",
  "planting_date": "2026-06-01"
}
```

Field utama:

- `duck_count`: jumlah bebek aktual.
- `land_area`: luas lahan.
- `land_area_unit`: `are` atau `hectare`.
- `rice_variety`: kode varietas padi dari lookup.
- `planting_system`: kode sistem tanam dari lookup.
- `planting_date`: tanggal tanam untuk konversi HST ke kalender.
- `parameter_set_id`: identitas parameter set aktif.
- `market_overrides`: override harga pasar per request jika diperlukan.

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

Lookup ini berfungsi sebagai parameter awal dan tetap harus divalidasi atau dikalibrasi dengan data lokal penelitian.

## Formula Inti

### Konversi area

```text
1 hectare = 100 are
1 are = 0.01 hectare
```

### Kepadatan bebek aktual

```text
d_actual = J / A
```

Keterangan:

- `J`: jumlah bebek.
- `A`: luas lahan dalam hektar.

### Jendela aman integrasi

```text
safe_window_days = min(HST_heading - HST_entry, t_max_eff)
```

Keterangan:

- `HST_entry`: hari setelah tanam saat bebek boleh mulai masuk.
- `HST_heading`: batas akhir sebelum heading stage.
- `t_max_eff`: batas efisiensi ekonomi maksimum.

### Model yield dasar

```text
x(d,t) = (-0.0103 d^2 + 2.6314 d + 7569.4) * exp(-((t - 80)^2) / (2 * 80^2))
```

Hasil model dasar dalam `kg/ha`.

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
x_final_ton_per_ha = x_penalized * f_yield / 1000
```

Keterangan:

- `f_yield`: faktor koreksi sistem tanam.
- pembagian `1000` digunakan untuk konversi dari `kg/ha` menjadi `ton/ha`.

### Klasifikasi risiko

```text
NORMAL  if d <= K_max
WASPADA if K_max < d <= 1.3 * K_max
BAHAYA  if d > 1.3 * K_max
```

### Nilai tambah beras

```text
delta_v_rice = ((p * x_final * 1000) - (p0 * x0 * 1000)) * A
```

Keterangan:

- `p`: harga beras sistem padi-bebek dalam `Rp/kg`.
- `p0`: harga beras konvensional dalam `Rp/kg`.
- `x_final`: yield akhir dalam `ton/ha`.
- `x0`: baseline yield konvensional dalam `ton/ha`.
- `A`: luas lahan dalam hektar.

### Nilai ekologis pupuk

```text
v_eco1 = ((0.02 * t) - 0.6) * (0.107 * P_N + 0.424 * P_P + 0.058 * P_K) * d * lambda * A
```

### Nilai ekologis pengendalian hayati

```text
if d > 300:
  v_eco2 = (400 / (1 + exp(-0.036626 * d)) - 3.327) * A
else:
  v_eco2 = linear interpolation from 0 to value_at_300
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

Fungsi ini dipakai sebagai objective untuk mode optimasi proaktif.

## Differential Evolution

Variabel keputusan:

- `d`: kepadatan bebek per hektar.
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

### Evaluasi simulasi

```text
POST /api/v1/simulations/evaluate
```

Response utama:

- `input_summary`
- `reactive_result`
- `proactive_result`
- `comparison`
- `calculation_status`
- `assumptions`

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

1. Koefisien yield dasar masih perlu kalibrasi dengan data lokal Indonesia.
2. Lookup `K_max` dan `f_yield` masih harus divalidasi terhadap data lapangan.
3. Parameter harga pasar tidak boleh dianggap universal; harus mengikuti lokasi, musim, dan periode observasi.
4. Output emisi belum layak dipakai sebagai angka final tanpa konversi fluks musiman dan baseline lokal.
5. Output finansial tetap harus diposisikan sebagai proyeksi model.
6. Hasil backend tidak menggantikan validasi agronomi, ekonomi, dan pakar lapangan.

## Pengembangan Lanjutan

Area pengembangan berikut yang relevan untuk backend ini:

1. integrasi PostgreSQL atau Supabase,
2. migration dan repository persistence,
3. versioning parameter set,
4. seed data harga lokal dan lookup lapangan,
5. pengujian formula berbasis skenario referensi penelitian,
6. modul admin untuk kalibrasi parameter,
7. ekstensi model emisi saat data pendukung telah tersedia.
