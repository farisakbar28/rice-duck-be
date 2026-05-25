# Rice Duck DSS Backend

Backend ini adalah fondasi awal untuk sistem Decision Support System (DSS) prediksi hasil panen padi-bebek berbasis API. Fokus setup ini adalah:

- evaluasi skenario aktual petani,
- rekomendasi skenario proaktif dengan Differential Evolution (DE),
- dokumentasi yang lebih ketat terhadap satuan, asumsi, dan keterbatasan model,
- struktur kode yang siap dilanjutkan ke database, kalibrasi lapangan, dan integrasi frontend.

Versi ini sengaja dibangun sebagai `seed setup`, bukan produk ilmiah final. Beberapa formula berasal dari literatur dan workbook variabel yang Anda lampirkan, tetapi parameter pasar dan koefisien lokal tetap wajib divalidasi sebelum dipakai untuk luaran paper atau keputusan lapangan.

## Status Repo

Sebelum setup ini, repo hanya berisi `README.md`. Sekarang repo sudah memiliki:

- scaffold FastAPI,
- domain model dan engine simulasi,
- optimizer DE,
- seed lookup untuk varietas dan sistem tanam,
- endpoint API dasar,
- test dasar,
- dokumentasi yang diselaraskan ulang.

## Prinsip Desain

Setup ini mengikuti beberapa keputusan yang lebih aman secara metodologis:

1. Variabel `t` dinormalisasi sebagai `durasi integrasi bebek dalam hari`, bukan absolute HST. Ini membuat rumus yield dan optimizer konsisten secara dimensi.
2. `P_rate` dibatasi maksimum `0.5` karena workbook menyebut penalti maksimum 50 persen. README lama masih ambigu karena rumusnya memungkinkan penalti 100 persen.
3. Output emisi belum dihitung sebagai angka final. Status emisi tetap `limited` atau `not_calculated` sampai ada konversi fluks musiman, baseline lokal, dan variabel pendukung seperti `X_DO`.
4. Mode ekonomi default memakai `local_gross`, bukan langsung memakai polinomial net-value dari literatur luar. Ini menghindari campuran satuan mata uang dan risiko double counting biaya pakan.
5. Seed market price di repo ini hanya untuk bootstrap API dan test. Nilainya tidak boleh langsung dipakai untuk interpretasi ilmiah.

## Arsitektur

Struktur proyek saat ini:

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

Peran tiap lapisan:

- `api`: route FastAPI.
- `core`: konfigurasi aplikasi.
- `data`: seed lookup dan parameter awal.
- `domain`: enum dan model domain.
- `engines`: formula bisnis dan optimizer DE.
- `schemas`: request-response API.
- `services`: orkestrasi simulasi.

## Model Domain yang Dipakai

### Input utama

Request minimal:

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

Field:

- `duck_count`: jumlah bebek aktual.
- `land_area`: luas lahan.
- `land_area_unit`: `are` atau `hectare`.
- `rice_variety`: kode varietas dari lookup.
- `planting_system`: kode sistem tanam dari lookup.
- `planting_date`: tanggal tanam untuk konversi kalender.

### Lookup yang sudah disediakan

Varietas seed:

- `ciherang`
- `inpari32`
- `ratoon`
- `lokal`

Sistem tanam seed:

- `konvensional`
- `legowo`
- `sri`
- `double-transplant`

Nilai `K_max` dan `f_yield` mengikuti workbook variabel sebagai seed awal, bukan hasil kalibrasi final.

## Formula yang Diimplementasikan

### Konversi area

```text
1 hectare = 100 are
1 are = 0.01 hectare
```

### Kepadatan bebek aktual

```text
d_actual = J / A
```

Dengan:

- `J`: jumlah bebek.
- `A`: luas lahan dalam hektar.

### Jendela aman durasi

Implementasi backend:

```text
safe_window_days = min(HST_heading - HST_entry, t_max_eff)
```

Catatan penting:

- sumber workbook beberapa kali mencampur `t` sebagai HST dan durasi,
- backend ini menormalkan `t` sebagai durasi saja,
- artinya domain optimizer menjadi `1 <= t <= safe_window_days`.

### Model yield dasar

```text
x(d,t) = (-0.0103 d^2 + 2.6314 d + 7569.4) * exp(-((t - 80)^2) / (2 * 80^2))
```

Hasil internal tetap `kg/ha`, lalu:

```text
x_penalized = x(d,t) * (1 - P_rate)
x_final_ton_per_ha = x_penalized * f_yield / 1000
```

### Risk level

```text
NORMAL  if d <= K_max
WASPADA if K_max < d <= 1.3 * K_max
BAHAYA  if d > 1.3 * K_max
```

### Penalti kepadatan

Implementasi yang dipakai:

```text
if d <= K_max:
  P_rate = 0
else:
  P_rate = min(0.5, ((d - K_max) / K_max) * 0.5)
```

Keputusan ini mengikuti catatan workbook bahwa penalti maksimum harus 50 persen.

### Delta nilai beras

```text
delta_v_rice = ((p * x_final * 1000) - (p0 * x0 * 1000)) * A
```

Koreksi dari README lama:

- `p` dan `p0` dalam `Rp/kg`,
- `x_final` dan `x0` dalam `ton/ha`,
- karena itu yield harus dikalikan `1000` sebelum dihitung ke nilai rupiah.

### Nilai ekologis

Komponen pupuk:

```text
v_eco1 = ((0.02 * t) - 0.6) * (0.107 * P_N + 0.424 * P_P + 0.058 * P_K) * d * lambda * A
```

Komponen pestisida-herbisida:

```text
if d > 300:
  v_eco2 = (400 / (1 + exp(-0.036626 * d)) - 3.327) * A
else:
  v_eco2 = linear interpolation from 0 to value_at_300
```

### Mode ekonomi yang dipilih di setup ini

Backend awal ini memakai `local_gross`:

```text
duck_revenue = harvested_ducks * average_duck_sale_weight_kg * duck_price
duck_net_value = duck_revenue - feed_penalty
total_benefit = delta_v_rice + duck_net_value + v_eco
```

Alasannya:

- model polinomial `V_duck` dari literatur memakai konteks harga dan koefisien luar negeri,
- jika langsung dipaksa ke rupiah lokal, risiko bias sangat tinggi,
- workbook juga menandai adanya risiko double counting pada biaya pakan.

## Differential Evolution

Optimizer berjalan pada dua variabel keputusan:

- `d`: kepadatan bebek per hektar.
- `t`: durasi integrasi bebek dalam hari.

Domain yang dipakai di kode:

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

Optimizer ada di [app/engines/differential_evolution.py](app/engines/differential_evolution.py).

## Endpoint

### Health check

```text
GET /api/v1/health
```

### Rice varieties

```text
GET /api/v1/lookups/rice-varieties
```

### Planting systems

```text
GET /api/v1/lookups/planting-systems
```

### Evaluate simulation

```text
POST /api/v1/simulations/evaluate
```

Response berisi:

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

Windows PowerShell:

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

Server:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

### 5. Jalankan test

```powershell
pytest
```

## Contoh Respons Ringkas

Contoh alur yang sekarang tersedia:

- skenario aktual dihitung dari `duck_count` dan `land_area`,
- sistem menghitung risiko, yield, total benefit, serta timeline,
- optimizer DE mencari kombinasi `d` dan `t` terbaik dalam jendela aman,
- hasil aktual dan hasil rekomendasi dikembalikan side by side.

## Limitasi yang Harus Ditulis Jujur

Ini penting untuk posisi riset dan target publikasi:

1. Seed market price di repo ini bukan data validasi lokal.
2. Koefisien yield dasar masih berbasis literatur luar dan perlu kalibrasi dengan data Indonesia.
3. Lookup `K_max` dan `f_yield` masih asumsi awal dari workbook dan belum dikaitkan ke dataset lapangan.
4. Emisi GRK belum boleh dilaporkan sebagai angka final karena belum ada integrasi musiman dan baseline lokal.
5. Nilai ekonomi duck pada setup awal belum memodelkan seluruh biaya operasional kandang, tenaga kerja, mortalitas non-linier, atau variasi bobot jual aktual.
6. Output backend adalah alat simulasi keputusan, bukan pengganti validasi agronomi dan ekonomi lapangan.

## Perubahan Penting Dibanding README Lama

Perubahan yang sengaja dilakukan:

- menghapus masalah encoding dan karakter rusak,
- menyesuaikan struktur repo nyata, bukan struktur imajiner `backend/`,
- menormalkan domain `t`,
- memperbaiki konsistensi satuan pada `delta_v_rice`,
- membatasi `P_rate` ke 50 persen,
- menahan implementasi emisi ke status `limited`,
- mengganti mode ekonomi default menjadi model lokal yang lebih audit-friendly.

## Langkah Lanjut yang Disarankan

Untuk fase berikutnya, prioritas yang paling layak:

1. pindahkan seed data ke PostgreSQL atau Supabase,
2. tambahkan migration dan repository database,
3. masukkan dataset harga lokal per wilayah dan musim,
4. tambah test formula terhadap skenario referensi dari workbook,
5. tambahkan endpoint admin untuk parameter set versioning,
6. kalibrasi model yield dan duck-value memakai data historis lokal.

## File Kunci

- [app/main.py](app/main.py)
- [app/services/simulation_service.py](app/services/simulation_service.py)
- [app/engines/formula_engine.py](app/engines/formula_engine.py)
- [app/engines/differential_evolution.py](app/engines/differential_evolution.py)
- [tests/test_api.py](tests/test_api.py)
