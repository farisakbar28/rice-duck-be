# DSS Yield Prediction Padi-Bebek Backend

Backend ini dikembangkan untuk mendukung sistem **Decision Support System (DSS) Yield Prediction Padi-Bebek**, yaitu sistem pendukung keputusan untuk memprediksi hasil panen padi, mengevaluasi risiko kepadatan bebek, menghitung estimasi manfaat ekonomi-ekologis, serta memberikan rekomendasi jumlah bebek dan durasi integrasi yang lebih optimal pada sistem pertanian terpadu padi-bebek.

Sistem ini dirancang sebagai **calculation engine**, **optimization engine**, dan **decision support API**. Backend tidak berfokus pada monitoring IoT real-time, tetapi pada proses simulasi, evaluasi skenario, dan rekomendasi berbasis formula serta algoritma optimasi.

---

## 1. Tujuan Proyek

Tujuan utama backend ini adalah menyediakan layanan API yang mampu:

1. Menerima input data sederhana dari petani atau pengguna.
2. Menghitung skenario aktual berdasarkan kondisi yang dimasukkan pengguna.
3. Mengevaluasi risiko jumlah bebek terhadap luas lahan.
4. Menghitung estimasi hasil panen padi.
5. Menghitung estimasi manfaat ekonomi dan ekologis.
6. Menjalankan algoritma optimasi **Differential Evolution** untuk mencari kombinasi jumlah bebek dan durasi integrasi terbaik.
7. Membandingkan skenario aktual dengan skenario rekomendasi.
8. Menyediakan output yang mudah ditampilkan pada dashboard DSS.

---

## 2. Ruang Lingkup Sistem

Backend ini mencakup beberapa proses utama:

- Input data petani
- Konversi satuan lahan
- Validasi input
- Lookup varietas padi
- Lookup sistem tanam
- Perhitungan kepadatan bebek
- Perhitungan durasi integrasi bebek
- Perhitungan prediksi yield
- Perhitungan risiko kepadatan bebek
- Perhitungan estimasi manfaat ekonomi
- Perhitungan estimasi manfaat ekologis
- Optimasi rekomendasi menggunakan Differential Evolution
- Penyimpanan data simulasi ke Supabase
- Penyediaan response API untuk frontend dashboard

---

## 3. Teknologi yang Digunakan

Backend direkomendasikan menggunakan stack berikut:

| Komponen | Teknologi |
|---|---|
| Bahasa Pemrograman | Python |
| Framework Backend | FastAPI |
| Database | Supabase PostgreSQL |
| ORM | SQLAlchemy |
| Migration | Alembic |
| Data Validation | Pydantic |
| Numerical Computation | NumPy |
| Optimization Engine | Custom Differential Evolution |
| Testing | Pytest |
| API Documentation | OpenAPI / Swagger bawaan FastAPI |
| Deployment | VPS / Railway / Render / Docker |

---

## 4. Alasan Menggunakan FastAPI

FastAPI dipilih karena sesuai dengan kebutuhan sistem DSS yang membutuhkan API cepat, validasi input yang kuat, dan dokumentasi otomatis.

Keunggulan FastAPI untuk proyek ini:

1. Cocok untuk backend berbasis komputasi.
2. Mendukung validasi request dan response menggunakan Pydantic.
3. Dokumentasi API otomatis melalui Swagger UI.
4. Mudah diintegrasikan dengan Supabase PostgreSQL.
5. Struktur project mudah dipisahkan antara API, service, formula engine, dan optimization engine.
6. Cocok untuk penelitian karena alur proses backend dapat dibuat eksplisit dan mudah diuji.

---

## 5. Database

Database yang digunakan adalah **Supabase**.

Supabase digunakan sebagai layanan database berbasis PostgreSQL untuk menyimpan:

- Lookup varietas padi
- Lookup sistem tanam
- Parameter model
- Konstanta biologis
- Konstanta ekonomi
- Konstanta emisi
- Data request simulasi
- Hasil simulasi aktual
- Hasil optimasi rekomendasi
- Riwayat proses optimasi

Walaupun menggunakan Supabase, backend tetap disarankan terhubung menggunakan koneksi PostgreSQL langsung melalui `DATABASE_URL`.

Supabase dapat digunakan untuk:

1. PostgreSQL database.
2. Supabase dashboard untuk mengelola data parameter.
3. Supabase Auth jika sistem nantinya membutuhkan login admin.
4. Supabase Storage jika perlu menyimpan dokumen pendukung penelitian.

Catatan penting:

- `SUPABASE_SERVICE_ROLE_KEY` hanya boleh digunakan di backend.
- Jangan pernah menaruh service role key di frontend.
- Frontend hanya boleh menggunakan anon key jika memang diperlukan.
- Untuk proses calculation engine, backend lebih baik mengakses database melalui PostgreSQL connection string.

---

## 6. Input Utama Sistem

Input utama dari pengguna dibuat sederhana agar mudah digunakan oleh petani.

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

Penjelasan input:

| Field | Keterangan |
|---|---|
| `duck_count` | Jumlah bebek yang dimiliki atau akan dilepas ke sawah |
| `land_area` | Luas lahan |
| `land_area_unit` | Satuan luas lahan, dapat berupa `are` atau `hectare` |
| `rice_variety` | Varietas padi |
| `planting_system` | Sistem tanam padi |
| `planting_date` | Tanggal tanam padi |

---

## 7. Prinsip Satuan

Sistem menggunakan dua pendekatan satuan:

| Kebutuhan | Satuan |
|---|---|
| Perhitungan internal backend | Hektar |
| Tampilan untuk petani | Are |

Hal ini dilakukan karena rumus ilmiah umumnya menggunakan satuan hektar, sedangkan komunikasi ke petani lebih mudah menggunakan satuan are.

Konversi satuan:

```txt
1 hektar = 100 are
1 are = 0.01 hektar
```

Contoh konversi:

```txt
area_hectare = area_are / 100
area_are = area_hectare * 100
```

Backend sebaiknya selalu mengembalikan dua bentuk satuan:

```json
{
  "area": {
    "value_are": 10,
    "value_hectare": 0.1
  }
}
```

---

## 8. Variabel Utama Sistem

Sistem memiliki dua jenis variabel utama:

1. **Input Variable**
2. **Decision Variable**

### 8.1 Input Variable

Input variable adalah variabel yang dimasukkan oleh pengguna.

| Simbol | Nama Variabel | Keterangan |
|---|---|---|
| `J` | Jumlah bebek | Jumlah bebek aktual |
| `A` | Luas lahan | Luas sawah |
| `V` | Varietas padi | Jenis varietas padi |
| `S` | Sistem tanam | Pola/sistem tanam |
| `TD` | Tanggal tanam | Tanggal awal penanaman |

### 8.2 Decision Variable

Decision variable adalah variabel yang dicari oleh algoritma optimasi.

| Simbol | Nama Variabel | Keterangan |
|---|---|---|
| `d` | Kepadatan bebek | Jumlah bebek per hektar |
| `t` | Durasi bebek aktif | Lama bebek berada di sawah |

---

## 9. Output Utama Sistem

Sistem menghasilkan dua output utama:

### 9.1 Output 1 — Evaluasi Skenario Petani

Output ini menunjukkan hasil evaluasi berdasarkan kondisi aktual yang dimasukkan pengguna.

Contoh output:

- Kepadatan bebek aktual
- Prediksi yield aktual
- Risiko kepadatan bebek
- Estimasi laba bersih
- Estimasi penghematan input pertanian
- Timeline pelepasan dan penarikan bebek
- Peringatan jika bebek terlalu padat

### 9.2 Output 2 — Rekomendasi Solusi Optimal

Output ini menunjukkan hasil rekomendasi dari algoritma Differential Evolution.

Contoh output:

- Jumlah bebek optimal
- Kepadatan bebek optimal
- Durasi bebek optimal
- Prediksi yield maksimum
- Estimasi laba optimal
- Perbandingan dengan skenario aktual
- Rekomendasi tindakan untuk petani

---

## 10. Struktur Project Backend

Struktur project yang disarankan:

```txt
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── exceptions.py
│   ├── api/
│   │   └── v1/
│   │       ├── routes_simulation.py
│   │       ├── routes_lookup.py
│   │       ├── routes_parameters.py
│   │       └── routes_admin.py
│   ├── schemas/
│   │   ├── input_schema.py
│   │   ├── parameter_schema.py
│   │   ├── scenario_schema.py
│   │   └── output_schema.py
│   ├── domain/
│   │   ├── enums.py
│   │   ├── constants.py
│   │   └── units.py
│   ├── services/
│   │   ├── simulation_service.py
│   │   ├── reactive_service.py
│   │   ├── proactive_service.py
│   │   ├── risk_service.py
│   │   └── comparison_service.py
│   ├── engines/
│   │   ├── formula_engine.py
│   │   ├── yield_engine.py
│   │   ├── economy_engine.py
│   │   ├── ecology_engine.py
│   │   ├── emission_engine.py
│   │   └── differential_evolution.py
│   ├── repositories/
│   │   ├── parameter_repository.py
│   │   ├── lookup_repository.py
│   │   └── simulation_repository.py
│   ├── models/
│   │   ├── parameter_set.py
│   │   ├── lookup_table.py
│   │   ├── simulation.py
│   │   └── optimization_run.py
│   └── tests/
│       ├── test_formula_engine.py
│       ├── test_risk_service.py
│       ├── test_de_optimizer.py
│       └── test_api_simulation.py
├── alembic/
├── requirements.txt
├── .env.example
└── README.md
```

---

## 11. Modul Backend

### 11.1 Input Validation Module

Modul ini bertugas memvalidasi data input dari pengguna.

Aturan validasi:

```txt
duck_count >= 0
land_area > 0
land_area_unit harus berupa "are" atau "hectare"
rice_variety harus tersedia pada lookup table
planting_system harus tersedia pada lookup table
planting_date harus berupa tanggal valid
```

Jika input tidak valid, backend mengembalikan error response.

Contoh error:

```json
{
  "status": "error",
  "message": "land_area must be greater than 0"
}
```

---

### 11.2 Lookup Module

Lookup module menyimpan data referensi yang dipakai dalam perhitungan.

Lookup utama:

```txt
rice_variety_lookup
planting_system_lookup
```

Contoh data varietas padi:

```txt
name: Ciherang
hst_entry: 15
hst_heading: 75
plant_height_category: medium
```

Contoh data sistem tanam:

```txt
name: Legowo
k_max_per_hectare: 375
f_yield: 1.05
```

---

### 11.3 Parameter Module

Parameter module menyimpan nilai konstanta dan parameter model.

Parameter dibagi menjadi beberapa kelompok:

```txt
market_parameters
biological_constants
emission_constants
optimization_parameters
```

Setiap parameter sebaiknya memiliki versi agar hasil simulasi dapat diaudit.

Contoh struktur parameter set:

```json
{
  "id": "active",
  "name": "Default Parameter Set",
  "version": "1.0.0",
  "is_active": true,
  "calibration_status": "initial_assumption"
}
```

---

### 11.4 Formula Engine

Formula engine bertugas menjalankan seluruh proses perhitungan matematis.

Formula engine sebaiknya dipisahkan dari API route agar:

1. Mudah diuji.
2. Mudah dikembangkan.
3. Mudah dikalibrasi.
4. Tidak bercampur dengan logic request-response.

Proses utama formula engine:

```txt
Input petani
↓
Konversi satuan
↓
Ambil lookup varietas dan sistem tanam
↓
Hitung kepadatan bebek
↓
Hitung durasi aman
↓
Hitung prediksi yield
↓
Hitung risiko
↓
Hitung ekonomi
↓
Hitung ekologis
↓
Kembalikan hasil simulasi
```

---

## 12. Rumus Utama

### 12.1 Kepadatan Bebek Aktual

```txt
d_actual = J / A
```

Keterangan:

```txt
J = jumlah bebek
A = luas lahan dalam hektar
d_actual = kepadatan bebek per hektar
```

Untuk tampilan per are:

```txt
d_actual_per_are = d_actual / 100
```

---

### 12.2 Durasi Aman Bebek

Durasi aman dihitung berdasarkan waktu masuk bebek dan fase heading padi.

```txt
t_safe = HST_heading - HST_entry
```

Keterangan:

```txt
HST_entry = hari setelah tanam saat bebek mulai masuk sawah
HST_heading = hari setelah tanam saat padi mulai masuk fase heading
```

Catatan:

Nilai ini lebih tepat disebut sebagai durasi aman atau safe window, bukan selalu durasi aktual petani. Durasi aktual hanya dapat diketahui jika petani benar-benar memasukkan tanggal bebek masuk dan tanggal bebek ditarik.

---

### 12.3 Total Kotoran Bebek

```txt
Jika t <= 50:
Dung_total = (t / 50) × 4

Jika t > 50:
Dung_total = 4 + (t - 50) × 0.2
```

Keterangan:

```txt
t = durasi bebek aktif di sawah
Dung_total = estimasi total kotoran bebek
```

---

### 12.4 Model Prediksi Yield Dasar

```txt
x(d,t) = (-0.0103d² + 2.6314d + 7569.4) × e^(-(t-80)² / (2×80²))
```

Keterangan:

```txt
d = kepadatan bebek
t = durasi bebek aktif
x(d,t) = prediksi hasil padi awal dalam kg/ha
```

Setelah penyesuaian sistem tanam:

```txt
x_final = x_penalized × f_yield / 1000
```

Keterangan:

```txt
x_final = hasil akhir dalam ton/ha
f_yield = faktor koreksi sistem tanam
```

---

### 12.5 Risk Level

Risk level digunakan untuk menentukan keamanan kepadatan bebek.

```txt
Jika d <= K_max:
NORMAL

Jika K_max < d <= 1.3 × K_max:
WASPADA

Jika d > 1.3 × K_max:
BAHAYA
```

Keterangan:

```txt
d = kepadatan bebek aktual
K_max = batas daya dukung bebek berdasarkan sistem tanam
```

Penjelasan untuk pengguna:

| Status | Makna |
|---|---|
| NORMAL | Jumlah bebek masih aman untuk luas lahan |
| WASPADA | Jumlah bebek mulai melebihi daya dukung lahan |
| BAHAYA | Jumlah bebek terlalu padat dan berisiko merusak tanaman |

---

### 12.6 Penalti Kepadatan Bebek

```txt
Jika d > K_max:
P_rate = min(1.0, ((d - K_max) / K_max) × 0.5)

Jika d <= K_max:
P_rate = 0
```

Yield setelah penalti:

```txt
x_penalized = x_base × (1 - P_rate)
```

---

### 12.7 Nilai Tambah Beras

```txt
Delta_V_rice = (p × x_final × 1000 - p0 × x0 × 1000) × A
```

Keterangan:

```txt
p = harga beras hasil sistem padi-bebek
p0 = harga beras konvensional
x_final = yield final dalam ton/ha
x0 = yield baseline dalam ton/ha
A = luas lahan dalam hektar
```

Catatan:

Karena harga menggunakan Rp/kg dan yield menggunakan ton/ha, maka nilai yield perlu dikalikan 1000 agar satuannya menjadi kg.

---

### 12.8 Nilai Ekologis Pupuk

```txt
V_eco1 = [0.02t - 0.6] × [0.107P_N + 0.424P_P + 0.058P_K] × d × λ × A
```

Keterangan:

```txt
t = durasi bebek aktif
P_N = harga pupuk nitrogen
P_P = harga pupuk fosfor
P_K = harga pupuk kalium
d = kepadatan bebek
λ = faktor manfaat kotoran bebek
A = luas lahan dalam hektar
```

---

### 12.9 Nilai Ekologis Pestisida dan Herbisida

```txt
Jika d > 300:
V_eco2 = [400 / (1 + e^(-0.036626d)) - 3.327] × A

Jika d <= 300:
V_eco2 = interpolasi linear dari 0 ke nilai saat d = 300
```

Catatan:

Rumus logistic harus ditulis sebagai pembagian:

```txt
400 / (1 + e^...)
```

Bukan sebagai bentuk pangkat.

---

### 12.10 Objective Function

Objective function digunakan sebagai fungsi tujuan pada algoritma Differential Evolution.

```txt
Delta_y = Delta_V_rice + V_duck + V_eco
```

Keterangan:

```txt
Delta_y = total manfaat bersih
Delta_V_rice = nilai tambah dari hasil padi
V_duck = nilai ekonomi bebek
V_eco = nilai manfaat ekologis
```

---

## 13. Catatan Penting Tentang Double Counting

Bagian yang perlu sangat diperhatikan adalah perhitungan biaya pakan.

Jika backend menggunakan model `V_duck` berbasis literatur yang sudah menghitung nilai bersih ekonomi bebek, maka biaya pakan tidak boleh dikurangkan lagi secara langsung. Jika tetap dikurangkan, maka akan terjadi **double counting**.

Untuk menghindari hal tersebut, backend menyediakan mode ekonomi:

### 13.1 Literature Net Model

```txt
V_duck dianggap sudah berupa nilai bersih.
Penalty_feed hanya digunakan sebagai warning.
Penalty_feed tidak mengurangi laba akhir.
```

### 13.2 Local Gross Model

```txt
Pendapatan bebek dihitung dari harga jual bebek.
Biaya pakan dihitung secara eksplisit.
Penalty_feed boleh mengurangi laba.
```

Untuk versi awal penelitian, disarankan menggunakan:

```txt
duck_economic_model = "literature_net"
```

---

## 14. Emission Engine

Emission engine dibuat sebagai modul opsional.

Alasannya, perhitungan emisi membutuhkan data tambahan seperti:

- DO
- Redox potential
- CH₄ baseline
- N₂O flux
- Konversi fluks ke emisi musiman
- Data pembanding sistem konvensional

Jika data belum lengkap, backend tidak boleh menampilkan hasil emisi sebagai angka pasti.

Contoh response:

```json
{
  "emission": {
    "calculation_status": "limited",
    "message": "Indikator emisi membutuhkan data DO, N2O, baseline CH4, dan konversi musiman."
  }
}
```

Mode emission engine:

```txt
disabled  = emisi tidak dihitung
estimated = emisi dihitung dengan asumsi/default
measured  = emisi dihitung dari data pengukuran lapangan
```

Untuk versi awal penelitian, disarankan:

```txt
emission_mode = "disabled"
```

atau:

```txt
emission_mode = "limited"
```

---

## 15. Differential Evolution Engine

Differential Evolution digunakan untuk mencari kombinasi optimal:

```txt
d* = kepadatan bebek optimal
t* = durasi bebek optimal
```

Variabel keputusan:

```txt
X = [d, t]
```

Domain pencarian:

```txt
d_min = 0
d_max = K_max

t_min = HST_entry
t_max = min(HST_heading, t_max_eff)
```

Parameter awal algoritma:

```txt
NP = 50
F = 0.8
CR = 0.9
G_max = 500
epsilon = tolerance value
```

Keterangan:

| Parameter | Keterangan |
|---|---|
| `NP` | Jumlah populasi |
| `F` | Mutation factor |
| `CR` | Crossover rate |
| `G_max` | Maksimum generasi |
| `epsilon` | Batas konvergensi |

---

## 16. Alur Differential Evolution

```txt
Mulai
↓
Inisialisasi populasi
↓
Hitung fitness setiap individu
↓
Mutasi
↓
Crossover
↓
Evaluasi trial vector
↓
Seleksi greedy
↓
Update best solution
↓
Cek konvergensi
↓
Jika belum konvergen, ulangi proses
↓
Jika konvergen, kembalikan d* dan t*
↓
Selesai
```

Pseudocode:

```python
for generation in range(max_generation):
    for i in range(population_size):
        r1, r2, r3 = select_random_indices(i)

        mutant = population[r1] + F * (population[r2] - population[r3])
        mutant = clamp_to_domain(mutant)

        trial = binomial_crossover(
            target=population[i],
            mutant=mutant,
            crossover_rate=CR
        )

        trial_fitness = objective_function(trial)
        target_fitness = objective_function(population[i])

        if trial_fitness > target_fitness:
            population[i] = trial
            fitness[i] = trial_fitness

    update_best_solution()

    if has_converged():
        break
```

---

## 17. Konversi Hasil Optimasi ke Rekomendasi Praktis

Setelah algoritma menemukan `d*` dan `t*`, backend mengubah hasil tersebut menjadi rekomendasi praktis.

```txt
recommended_duck_density_per_hectare = d*
recommended_duck_density_per_are = d* / 100
recommended_duck_total = round(d* × A)
recommended_duration_days = t*
recommended_release_date = planting_date + HST_entry
recommended_pull_date = planting_date + HST_heading
```

Contoh output:

```json
{
  "recommended_duck_density_per_are": 3.7,
  "recommended_duck_density_per_hectare": 370,
  "recommended_duck_total": 37,
  "recommended_duration_days": 58,
  "recommended_release_date": "2026-06-16",
  "recommended_pull_date": "2026-08-15"
}
```

---

## 18. API Endpoint

### 18.1 Health Check

```txt
GET /api/v1/health
```

Response:

```json
{
  "status": "ok",
  "service": "dss-yield-prediction-backend"
}
```

---

### 18.2 Get Rice Varieties

```txt
GET /api/v1/lookups/rice-varieties
```

Response:

```json
{
  "data": [
    {
      "id": "ciherang",
      "name": "Ciherang",
      "hst_entry": 15,
      "hst_heading": 75,
      "plant_height_category": "medium"
    }
  ]
}
```

---

### 18.3 Get Planting Systems

```txt
GET /api/v1/lookups/planting-systems
```

Response:

```json
{
  "data": [
    {
      "id": "legowo",
      "name": "Legowo",
      "k_max_per_hectare": 375,
      "f_yield": 1.05
    }
  ]
}
```

---

### 18.4 Evaluate Simulation

```txt
POST /api/v1/simulations/evaluate
```

Endpoint ini menjalankan skenario aktual dan skenario optimasi.

Request:

```json
{
  "duck_count": 40,
  "land_area": 10,
  "land_area_unit": "are",
  "rice_variety": "ciherang",
  "planting_system": "legowo",
  "planting_date": "2026-06-01",
  "parameter_set_id": "active",
  "include_emission": false,
  "duck_economic_model": "literature_net"
}
```

Response:

```json
{
  "input_summary": {
    "duck_count": 40,
    "area_are": 10,
    "area_hectare": 0.1,
    "rice_variety": "ciherang",
    "planting_system": "legowo",
    "planting_date": "2026-06-01"
  },
  "reactive_result": {
    "duck_density_per_are": 4,
    "duck_density_per_hectare": 400,
    "risk_level": "WASPADA",
    "predicted_rice_yield_ton_per_ha": 7.2,
    "predicted_rice_yield_kg_per_are": 72,
    "estimated_profit_per_are": 150000,
    "timeline": {
      "duck_release_date": "2026-06-16",
      "duck_pull_date": "2026-08-15"
    },
    "warnings": [
      "Kepadatan bebek mulai melewati daya dukung awal sistem tanam."
    ]
  },
  "proactive_result": {
    "recommended_duck_density_per_are": 3.7,
    "recommended_duck_density_per_hectare": 370,
    "recommended_duck_total": 37,
    "recommended_duration_days": 58,
    "predicted_optimal_yield_ton_per_ha": 7.6,
    "estimated_profit_per_are": 170000,
    "delta_profit_per_are": 20000,
    "recommendation_notes": [
      "Jumlah bebek dapat dikurangi sedikit untuk menekan risiko kerusakan tanaman."
    ]
  },
  "comparison": {
    "display_mode": "side_by_side",
    "summary": "Skenario rekomendasi menghasilkan estimasi profit lebih tinggi dan risiko lebih rendah."
  },
  "calculation_status": {
    "economy": "estimated",
    "emission": "not_calculated",
    "calibration": "requires_local_validation"
  }
}
```

---

### 18.5 Get Simulation History

```txt
GET /api/v1/simulations
```

Fungsi:

```txt
Mengambil riwayat simulasi yang pernah dijalankan.
```

---

### 18.6 Get Simulation Detail

```txt
GET /api/v1/simulations/{simulation_id}
```

Fungsi:

```txt
Mengambil detail hasil simulasi berdasarkan ID.
```

---

## 19. Desain Database Supabase

### 19.1 `rice_variety_lookup`

```sql
create table rice_variety_lookup (
  id uuid primary key default gen_random_uuid(),
  code text unique not null,
  name text not null,
  local_name text,
  hst_entry integer not null,
  hst_heading integer not null,
  plant_height_category text,
  notes text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
```

---

### 19.2 `planting_system_lookup`

```sql
create table planting_system_lookup (
  id uuid primary key default gen_random_uuid(),
  code text unique not null,
  name text not null,
  k_max_per_hectare numeric not null,
  f_yield numeric not null,
  notes text,
  calibration_status text default 'initial_assumption',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
```

---

### 19.3 `parameter_sets`

```sql
create table parameter_sets (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  version text not null,
  description text,
  is_active boolean default false,
  calibration_status text default 'initial_assumption',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
```

---

### 19.4 `market_parameters`

```sql
create table market_parameters (
  id uuid primary key default gen_random_uuid(),
  parameter_set_id uuid references parameter_sets(id) on delete cascade,
  p numeric,
  p0 numeric,
  x0 numeric,
  p_n numeric,
  p_p numeric,
  p_k numeric,
  p_duck numeric,
  p_feed numeric,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
```

---

### 19.5 `biological_constants`

```sql
create table biological_constants (
  id uuid primary key default gen_random_uuid(),
  parameter_set_id uuid references parameter_sets(id) on delete cascade,
  lambda_value numeric,
  kappa_dung numeric,
  kappa_n numeric,
  kappa_p numeric,
  kappa_k numeric,
  t_phase1 integer,
  kappa_dung_p1 numeric,
  kappa_dung_p2 numeric,
  kappa_feed_save numeric,
  kappa_feed_greedy numeric,
  t_max_eff integer,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
```

---

### 19.6 `emission_constants`

```sql
create table emission_constants (
  id uuid primary key default gen_random_uuid(),
  parameter_set_id uuid references parameter_sets(id) on delete cascade,
  gwp_ch4 numeric,
  gwp_n2o numeric,
  beta_do_a numeric,
  beta_do_b numeric,
  beta_redox jsonb,
  beta_methanogen jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
```

---

### 19.7 `simulation_requests`

```sql
create table simulation_requests (
  id uuid primary key default gen_random_uuid(),
  duck_count integer not null,
  land_area_are numeric not null,
  land_area_hectare numeric not null,
  rice_variety_id uuid references rice_variety_lookup(id),
  planting_system_id uuid references planting_system_lookup(id),
  planting_date date not null,
  parameter_set_id uuid references parameter_sets(id),
  include_emission boolean default false,
  duck_economic_model text default 'literature_net',
  created_at timestamptz default now()
);
```

---

### 19.8 `simulation_results`

```sql
create table simulation_results (
  id uuid primary key default gen_random_uuid(),
  simulation_request_id uuid references simulation_requests(id) on delete cascade,
  reactive_result jsonb not null,
  proactive_result jsonb not null,
  comparison_result jsonb not null,
  calculation_status jsonb not null,
  created_at timestamptz default now()
);
```

---

### 19.9 `optimization_runs`

```sql
create table optimization_runs (
  id uuid primary key default gen_random_uuid(),
  simulation_request_id uuid references simulation_requests(id) on delete cascade,
  algorithm text default 'Differential Evolution',
  population_size integer,
  mutation_factor numeric,
  crossover_rate numeric,
  max_generation integer,
  best_solution jsonb,
  best_fitness numeric,
  convergence_status text,
  total_generation integer,
  created_at timestamptz default now()
);
```

---

## 20. Environment Variables

Contoh isi `.env`:

```env
APP_NAME="DSS Yield Prediction Padi-Bebek Backend"
APP_ENV=development
APP_DEBUG=true

API_V1_PREFIX=/api/v1

DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:5432/postgres

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

DE_DEFAULT_POPULATION_SIZE=50
DE_DEFAULT_MUTATION_FACTOR=0.8
DE_DEFAULT_CROSSOVER_RATE=0.9
DE_DEFAULT_MAX_GENERATION=500
DE_DEFAULT_EPSILON=0.000001
```

Catatan:

```txt
DATABASE_URL digunakan backend untuk koneksi langsung ke Supabase PostgreSQL.
SUPABASE_SERVICE_ROLE_KEY hanya boleh digunakan di backend.
SUPABASE_ANON_KEY dapat digunakan jika ada kebutuhan public client, tetapi tidak wajib untuk calculation API.
```

---

## 21. Instalasi Project

### 21.1 Clone Repository

```bash
git clone https://github.com/username/dss-yield-prediction-backend.git
cd dss-yield-prediction-backend
```

---

### 21.2 Buat Virtual Environment

```bash
python -m venv venv
```

Aktifkan virtual environment:

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

---

### 21.3 Install Dependency

```bash
pip install -r requirements.txt
```

Contoh `requirements.txt`:

```txt
fastapi
uvicorn
pydantic
pydantic-settings
sqlalchemy
asyncpg
alembic
numpy
python-dotenv
supabase
pytest
httpx
```

---

### 21.4 Setup Environment

Buat file `.env` berdasarkan `.env.example`.

```bash
cp .env.example .env
```

Lalu isi konfigurasi Supabase dan database connection string.

---

### 21.5 Jalankan Migration

```bash
alembic upgrade head
```

Jika menggunakan SQL langsung dari Supabase SQL Editor, migration dapat disesuaikan dengan kebutuhan project.

---

### 21.6 Jalankan Backend

```bash
uvicorn app.main:app --reload
```

Backend akan berjalan di:

```txt
http://localhost:8000
```

Swagger API documentation:

```txt
http://localhost:8000/docs
```

---

## 22. Testing

Jalankan unit test:

```bash
pytest
```

Area yang wajib diuji:

```txt
1. Unit conversion
2. Input validation
3. Formula yield
4. Risk level
5. Economic calculation
6. Differential Evolution
7. API response
8. Supabase database connection
```

---

## 23. Contoh Test Case

### 23.1 Unit Conversion

```txt
Input:
10 are

Expected:
0.1 hectare
```

---

### 23.2 Duck Density

```txt
Input:
J = 40 bebek
A = 0.1 hektar

Expected:
d = 400 bebek/hektar
d_per_are = 4 bebek/are
```

---

### 23.3 Risk Level

```txt
Input:
d = 400
K_max = 375

Expected:
WASPADA
```

---

### 23.4 Recommended Duck Total

```txt
Input:
d* = 370 bebek/hektar
A = 0.1 hektar

Expected:
recommended_duck_total = 37 bebek
```

---

## 24. Response Design untuk Dashboard

Backend sebaiknya mengembalikan response yang sudah siap ditampilkan oleh frontend.

Response dibagi menjadi beberapa bagian:

```txt
input_summary
reactive_result
proactive_result
comparison
calculation_status
warnings
```

Tujuannya agar frontend tidak perlu menghitung ulang logic utama.

Frontend hanya bertugas:

1. Menampilkan input summary.
2. Menampilkan kartu hasil aktual.
3. Menampilkan kartu rekomendasi.
4. Menampilkan perbandingan aktual vs rekomendasi.
5. Menampilkan warning.
6. Menampilkan grafik atau dashboard visual.

---

## 25. Prinsip Output untuk Petani

Output untuk petani harus sederhana dan tidak terlalu teknis.

Disarankan menggunakan istilah:

```txt
Jumlah bebek per are
Hasil panen kg per are
Laba bersih per are
Penghematan pupuk
Penghematan biaya gulma/hama
Status aman, waspada, atau bahaya
Tanggal bebek masuk sawah
Tanggal bebek ditarik dari sawah
```

Hindari menampilkan istilah terlalu teknis pada dashboard petani, seperti:

```txt
Objective function
Mutation factor
Crossover rate
GWP
GHGI
CH4 flux
N2O flux
Redox potential
```

Istilah teknis tersebut lebih cocok ditampilkan pada dashboard admin, halaman akademik, atau laporan penelitian.

---

## 26. Prinsip Output untuk Admin atau Peneliti

Output untuk admin atau peneliti dapat dibuat lebih lengkap.

Contoh informasi teknis:

```txt
Yield ton/ha
Kepadatan bebek per hektar
Nilai objective function
Best fitness
Jumlah generasi DE
Parameter set yang digunakan
Calibration status
NPK estimation
Emission calculation status
Economic model mode
```

---

## 27. Batasan Sistem

Sistem ini memiliki beberapa batasan:

1. Hasil prediksi bersifat estimasi, bukan angka pasti.
2. Model yield membutuhkan kalibrasi dengan data lokal.
3. Model ekonomi bergantung pada harga beras, harga bebek, biaya pakan, dan biaya input pertanian.
4. Model ekologis bergantung pada asumsi manfaat bebek terhadap pupuk, gulma, dan hama.
5. Model emisi belum layak ditampilkan sebagai angka final jika data DO, CH₄, N₂O, dan konversi musiman belum tersedia.
6. Rekomendasi dari algoritma harus tetap divalidasi dengan ahli lapangan.
7. Backend tidak menggantikan keputusan agronomis, tetapi membantu memberikan skenario pendukung keputusan.

---

## 28. Status Kalibrasi

Setiap hasil perhitungan sebaiknya memiliki status kalibrasi.

Contoh:

```json
{
  "calibration_status": "requires_local_validation"
}
```

Kemungkinan status:

```txt
initial_assumption
literature_based
field_validated
requires_local_validation
```

Status ini penting agar sistem tidak memberikan kesan bahwa angka prediksi sudah pasti benar tanpa validasi lokal.

---

## 29. Roadmap Implementasi

### Phase 1 — Backend Foundation

```txt
- Setup FastAPI
- Setup Supabase PostgreSQL
- Setup environment variable
- Setup database connection
- Setup folder structure
- Setup base API route
```

### Phase 2 — Lookup & Parameter

```txt
- Buat tabel varietas padi
- Buat tabel sistem tanam
- Buat tabel parameter set
- Buat tabel konstanta ekonomi
- Buat tabel konstanta biologis
- Buat seed data awal
```

### Phase 3 — Formula Engine

```txt
- Implementasi unit conversion
- Implementasi kepadatan bebek
- Implementasi durasi aman
- Implementasi yield model
- Implementasi risk engine
- Implementasi economic engine
- Implementasi ecology engine
```

### Phase 4 — Reactive Scenario

```txt
- Endpoint evaluasi skenario petani
- Output yield aktual
- Output risiko aktual
- Output estimasi laba aktual
- Output timeline aktual
```

### Phase 5 — Proactive Optimization

```txt
- Implementasi Differential Evolution
- Generate populasi awal
- Implementasi mutasi
- Implementasi crossover
- Implementasi seleksi
- Implementasi objective function
- Simpan optimization run
```

### Phase 6 — Scenario Comparison

```txt
- Bandingkan hasil aktual dan rekomendasi
- Hitung delta yield
- Hitung delta profit
- Hitung perubahan risiko
- Siapkan response dashboard
```

### Phase 7 — Validation & Calibration

```txt
- Validasi hasil bersama pihak lapangan
- Kalibrasi parameter lokal
- Tambahkan data historis panen
- Evaluasi akurasi model
- Revisi formula jika diperlukan
```

---

## 30. Rekomendasi Mode Versi Awal

Untuk versi awal penelitian, konfigurasi yang disarankan:

```txt
Backend framework: FastAPI
Database: Supabase PostgreSQL
Internal unit: hectare
Display unit: are
Optimization: Custom Differential Evolution
Economic model: literature_net
Emission mode: limited / disabled
Output target: petani + admin/peneliti
```

Output utama untuk petani:

```txt
Jumlah bebek per are
Prediksi hasil panen kg/are
Estimasi laba bersih per are
Status risiko
Tanggal bebek masuk
Tanggal bebek ditarik
Rekomendasi jumlah bebek optimal
```

Output utama untuk admin/peneliti:

```txt
Yield ton/ha
Kepadatan bebek per hektar
Fitness value
Objective function
Parameter set
Optimization run
Calibration status
```

---

## 31. Kesimpulan

Backend DSS Yield Prediction Padi-Bebek dirancang sebagai sistem komputasi dan optimasi berbasis API. Sistem menerima input sederhana dari pengguna, menjalankan evaluasi skenario aktual, menghitung risiko dan estimasi hasil panen, lalu memberikan rekomendasi skenario optimal menggunakan algoritma Differential Evolution.

Penggunaan **FastAPI** cocok karena backend membutuhkan struktur API yang rapi, validasi kuat, dokumentasi otomatis, dan pemisahan logic komputasi yang jelas. Penggunaan **Supabase PostgreSQL** cocok untuk menyimpan lookup table, parameter model, riwayat simulasi, dan hasil optimasi.

Sistem harus tetap menampilkan hasil sebagai estimasi atau proyeksi, bukan angka final mutlak. Model perlu terus dikalibrasi menggunakan data lokal agar rekomendasi yang diberikan semakin akurat dan sesuai dengan kondisi lapangan.
