# Rice Duck DSS Backend

Backend FastAPI minimal untuk penelitian **DSS Yield Prediction Padi-Bebek**. Sistem ini adalah DSS deterministik berbasis model matematika, bukan machine learning, IoT, atau platform industri.

Referensi parameter hanya berasal dari dokumen model 74 variabel dan `data_collection_padi_bebek.xlsx`. File data collection dipakai sebagai referensi lokal dengan metadata nilai, satuan, sumber, status, rentang, dan catatan. Nilai parsial tidak diperlakukan sebagai konstanta final.

## Akses API

Public:

- `GET /health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/dss/options`
- `POST /api/v1/dss/simulate`

Protected:

- `GET /api/v1/auth/me`
- `GET /api/v1/dss/histories`
- `GET /api/v1/dss/histories/{id}`
- `DELETE /api/v1/dss/histories/{id}`

Simulasi tanpa token tetap berjalan dengan `history_id: null`. Jika Bearer token valid dikirim, seluruh response disimpan sebagai history user di SQLite. Token yang dikirim tetapi tidak valid menghasilkan `401`.

## Menjalankan

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Swagger tersedia di `http://127.0.0.1:8000/docs`.

Konfigurasi utama:

```env
DATABASE_PATH="data/rice_duck.db"
JWT_SECRET_KEY="replace-with-a-long-random-secret"
JWT_ACCESS_TOKEN_MINUTES=120
PASSWORD_HASH_ITERATIONS=600000
```

SQLite dan tabel `users` serta `dss_simulation_histories` dibuat otomatis saat aplikasi dimulai. Tidak ada migration command atau ORM.

## Auth

Register:

```json
{
  "name": "Faris",
  "email": "faris@example.com",
  "password": "password123"
}
```

Login menggunakan email dan password yang sama. Password disimpan dengan PBKDF2-SHA256 dan salt acak; access token menggunakan JWT HS256. Backend tidak memiliki role, admin, OAuth, refresh token, atau email verification.

## Simulasi

Request `POST /api/v1/dss/simulate`:

```json
{
  "duck_count": 28,
  "land_area_are": 7,
  "planting_date": "2026-06-01",
  "rice_variety": "sertani",
  "planting_system": "jajar_legowo",
  "duck_age_days": 30
}
```

Enam field tersebut adalah satu-satunya input runtime. `rice_variety` dan `planting_system` harus memakai kode dari `GET /api/v1/dss/options`.

Struktur response:

```json
{
  "history_id": null,
  "input": {},
  "lookup": {},
  "actual_scenario": {},
  "recommended_scenario": {},
  "comparison": {},
  "risk": {},
  "economics": {},
  "ecology": {},
  "environment": {},
  "validation": {},
  "data_readiness": {},
  "trace": {},
  "notes": []
}
```

## Output dan Status

Output agronomi yang dihitung:

- luas ha, densitas ekor/are dan ekor/ha;
- durasi, tanggal lepas/tarik, `t_effective`;
- estimasi survival dan kotoran per ekor;
- `x_base`, `P_rate`, `x_penalized`, yield kg/ha, kg/are, ton/ha, dan total kg;
- status risiko kepadatan, fase, pakan, dan peringatan kualitas data.

Output infrastruktur yang dihitung:

- biaya jaring per siklus;
- biaya kandang per siklus;
- total biaya infrastruktur.

Maintenance menggunakan placeholder `0` karena tidak tercatat dan selalu diberi catatan bahwa nilai tersebut bukan bukti biaya nihil.

Output bersyarat:

- `delta_rice_value_rp`, `feed_cost_rp`, `duck_net_value_rp`, `net_profit_rp`, dan `delta_profit_rp` bernilai `null` selama harga gabah padi-bebek, baseline yield, atau kuantitas pakan belum lengkap.
- `V_eco1`, `V_eco2`, dan `V_gulma` berstatus `estimation_only`; total ekologis adalah jumlah ketiga komponen tersebut.
- N, P2O5, dan K2O tanah bernilai `null` karena koefisien kappa dan uji kotoran lokal belum tersedia.
- CO2e, GHGI, dan reduksi CH4 bernilai `null` dengan status `disabled` karena data CH4/N2O musiman tidak tersedia.

Status data:

- `ready`: parameter cukup untuk perhitungan yang dinyatakan.
- `partial`: hanya sebagian komponen tersedia.
- `estimation_only`: hasil memakai nilai awal/rentang konservatif dan bukan klaim final.
- `unavailable`: parameter wajib tidak tersedia.
- `disabled`: modul sengaja tidak dihitung agar tidak menghasilkan klaim tanpa data.

## Parameter Konservatif

- Jajar Legowo memakai `K_max = 4` ekor/are; rentang data 4-8 dan 5-6 hanya skenario uji terbatas.
- Tegel memakai `K_max = 2.5` ekor/are; rentang data 2-3.
- Survival `lambda = 0.67` adalah estimasi batas atas dari indikasi 35%-67%, bukan rata-rata tervalidasi.
- HST masuk memiliki rentang 21-30; heading sekitar 60 dengan rentang 40-65.
- Aktivitas bebek memakai 10 jam/hari dan baseline model 12 jam/hari.
- Umur bebek lokal 14-21 hari hanya menjadi konteks risiko dan belum mengubah yield.
- Biaya penyiangan memakai batas bawah rentang tipikal Rp6.000-Rp25.000/are/siklus; Rp70.000-Rp72.000 dicatat sebagai outlier.

Metadata lengkap parameter tersebut tersedia pada blok `lookup.parameters`.

## Rumus Inti

```text
A_ha = A_are / 100
d_are = J / A_are
d_ha = d_are * 100
t = HST_heading - HST_masuk
t_effective = t * daily_grazing_hours / baseline_hours
N_d = J * lambda
```

```text
x(d,t) =
  (-0.0103*d_ha^2 + 2.6314*d_ha + 7569.4)
  * exp(-((t-80)^2 / (2*80^2)))

P_rate = 0                                      jika d_are <= K_max
P_rate = min(P_max, gamma*(d_are-K_max)/K_max) jika d_are > K_max

x_penalized = x(d,t) * (1-P_rate)
x_final = alpha_local * x_penalized * f_yield
```

```text
C_infra =
  C_jaring/life_jaring
  + C_kandang/life_kandang
  + maintenance
```

Rumus ekonomi, ekologis, hara, dan emisi tetap tersedia dalam engine, tetapi hanya dieksekusi menjadi angka jika parameter wajib tersedia.

## Rekomendasi

Grid search menggunakan jumlah bebek integer:

```text
J_candidate = ceil(min_density*A_are) ... floor(K_max_conservative*A_are)
d_candidate_are = J_candidate / A_are
t_candidate = 1 ... min(HST_heading-HST_masuk, t_max_eff)
```

Objective aktif saat ini:

```text
score = normalized_yield - risk_penalty
```

Profit dan ekologi tidak digunakan dalam ranking karena data belum lengkap. Trace mencatat komponen yang digunakan/dilewati, rentang kandidat, jumlah kandidat, kandidat terbaik, densitas hasil pembagian jumlah bebek terhadap luas, durasi, dan seluruh constraint.

## Pengujian

```powershell
.venv\Scripts\python -m pytest
```

Test mencakup rumus agronomi, batas HST, yield contoh 28 bebek/7 are, K_max konservatif, status data ekonomi/hara/emisi, konsistensi grid search, auth, optional history, dan isolasi history antar-user.

Postman:

- `postman/Rice_Duck_DSS.postman_collection.json`
- `postman/Rice_Duck_DSS.postman_environment.json`

Import kedua file, pilih environment, jalankan backend, lalu jalankan collection berurutan.

## Limitasi Akademik

Yield, survival, kotoran, dan faktor lookup masih perlu kalibrasi lapangan Astungkara Way. Profit tidak final selama data pakan dan baseline ekonomi belum lengkap. Manfaat ekologis tidak boleh dibaca sebagai total final. Emisi tidak dihitung sampai tersedia data CH4 dan N2O musiman yang valid.
