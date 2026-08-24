# DSS Padi-Bebek A+C

Backend FastAPI untuk arsitektur **dual-evidence**, mengikuti [Source of Truth](docs/Model%20Matematika%20Data%20Collection%20DSS%20Padi%20Bebek%20FINAL.md).

- Primary local production adalah C0 tetap: `50 kg/are` dan `50 * land_area_are`.
- Xiong et al. (2014) hanya reference literature opsional, valid pada `0 < density_ha <= 600` dan durasi eksplisit `50..80` hari.
- Tidak ada average, weight, ensemble, fallback, atau koreksi numerik antara C0 dan Xiong.
- Ekonomi selalu memakai yield primary C0, termasuk saat reference valid.
- `d > 8` menghasilkan `survival_risk=HIGH`; sistem tidak membuat survival/N_sold numerik dan revenue all-sold bebek menjadi `null`.

## Menjalankan

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
python -m pytest -q
python scripts/validate_model_ac_runtime.py
```

Swagger: `http://127.0.0.1:8000/docs`.

## Request utama

Lima input required: `land_area_are` (JSON number >0), `duck_count` (StrictInt >=0), `rice_variety`, `planting_system`, dan `duck_age_days` (StrictInt >=0). `planting_date`, harga, biaya scenario, dan `literature_duration_days` opsional. Numeric strings, boolean, NaN, dan Infinity ditolak; kode referensi harus exact.

```json
{"land_area_are":10,"duck_count":40,"rice_variety":"sertani","planting_system":"jajar_legowo","duck_age_days":21,"literature_duration_days":50}
```

Response memisahkan `yield_are_kg`/`yield_total_kg` (PRIMARY C0) dari `literature_reference_status`, `yield_literature_reference_*`, dan `literature_gap_kg_are`. Defaults harga adalah gabah 6000 (local-calibrated), beli bebek 25000 (local-calibrated), jual bebek 45000 (local-estimate); input `0` tetap runtime value. Feed dan infrastruktur hanya mengurangi cash contribution bila optional scenario dipilih.

History authenticated memakai schema v4 dan menyimpan request serta exact response A+C. v1–v3 dipertahankan secara fisik dan tidak disajikan sebagai history A+C. Optimizer berada di luar scope.

Lihat [tes_skenario.md](docs/tes_skenario.md), [runtime evidence](docs/runtime_evidence_model_ac.json), dan [stale semantics audit](docs/stale_semantics_audit_model_ac.md).
