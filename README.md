# DSS Padi-Bebek Backend — Frozen Model C

Backend FastAPI ini mengimplementasikan Model C dengan production model C0 yang **frozen**: `yield_are_kg = 50.0`. C0 dikalibrasi pada 25 siklus dari 13 petani memakai farmer-grouped development split, lalu divalidasi sekali pada 11 holdout cycles dari 6 petani. Tidak ada retuning setelah holdout dibuka.

Metrik holdout frozen adalah MAE 11.979, RMSE 15.990, MedAE 9.583, dan bias +7.307 kg/are. C0 adalah baseline lokal defensif—bukan prediktor hasil petak berpresisi tinggi. Candidate C1/C3/C4 hanya catatan riset dan tidak pernah dipakai pada runtime.

Source of Truth: [Model Matematika Data Collection DSS Padi Bebek FINAL.md](docs/Model%20Matematika%20Data%20Collection%20DSS%20Padi%20Bebek%20FINAL.md).

## Kontrak simulasi

`POST /api/v1/dss/simulate` memerlukan lima input: `land_area_are` (>0), `duck_count` (integer >=0), `rice_variety` (`sertani`/`inpari`), `planting_system` (`jajar_legowo`/`tegel`), dan `duck_age_days` (integer >=0). Semua angka harus JSON number finite; string angka, boolean, NaN, Infinity, dan field legacy ditolak.

Input opsional adalah `planting_date`, `p_gabah`, `p_duck_buy`, `p_duck_sell`, `c_feed_scenario`, serta pasangan biaya/amortisasi jaring dan kandang. Tidak ada `literature_duration_days`, input Xiong, atau feed default tersembunyi.

```json
{
  "land_area_are": 10,
  "duck_count": 20,
  "rice_variety": "sertani",
  "planting_system": "jajar_legowo",
  "duck_age_days": 21
}
```

Respons selalu memiliki `model_variant = C_FARMER_GROUPED_LOCAL`, `yield_are_kg = 50.0`, dan `yield_total_kg = 50 * land_area_are`, selama area valid. Status usia, varietas, sistem tanam, dan density adalah gate—tidak mengalikan yield. Parameter uncertainty `[42.81, 55.78]` adalah uncertainty parameter deskriptif, bukan prediction interval individual.

Density 2–4 (Jarwo) atau 2–3 (Tegel) direkomendasikan. Di atas 8 ekor/are backend hanya menetapkan `survival_risk = HIGH`; tidak ada survival rate atau jumlah bebek hidup yang diprediksi. Skenario revenue bebek seluruhnya terjual dan cash contribution bergantung padanya menjadi `null` pada kondisi itu.

Kalender menampilkan rekomendasi pelepasan 21–30 HST dan penarikan 56–60 HST. Jika `planting_date` tidak dikirim, seluruh tanggal bernilai `null` tanpa membuat tanggal sintetis.

Default harga Model C adalah gabah Rp6.000/kg dan beli bebek Rp25.000/ekor (keduanya `local-calibrated`), serta harga jual scenario Rp45.000/ekor (`local-estimate`). Harga runtime mengesampingkan default. Feed dan infrastruktur hanya dikurangkan bila scenario caller memilihnya; output ini adalah scenario cash contribution, bukan final accounting profit atau realized farmer profit.

## History dan validasi

Simulasi dengan Bearer token disimpan sebagai `schema_version=4`, menyimpan request dan response Model C secara deterministik. Row v1–v3 dipertahankan secara fisik tetapi tidak ditampilkan, dibaca, atau dihapus sebagai history Model C.

Jalankan pemeriksaan unit dan acceptance HTTP nyata:

```bash
python -m pytest -q
python scripts/validate_model_c_runtime.py
```

Runner menyalakan Uvicorn pada loopback port acak dengan SQLite runtime terisolasi, memverifikasi nonce `/health`, menjalankan H01–H11, S-C01–S-C12, kalender, dan history v4. Bukti raw HTTP tersimpan di [docs/runtime_evidence_model_c.json](docs/runtime_evidence_model_c.json). Optimizer tetap fitur terpisah dan di luar scope DSS Core.
