# DSS Padi-Bebek A+C

Backend FastAPI untuk arsitektur dual-evidence sesuai [Source of Truth](docs/Model%20Matematika%20Data%20Collection%20DSS%20Padi%20Bebek%20FINAL.md).

- Primary produksi lokal adalah C0 tetap: `50 kg/are` dan `50 × land_area_are`.
- Xiong et al. (2014) adalah reference literature opsional, `VALID_DOMAIN` hanya pada `0 < density_ha <= 600` dan `literature_duration_days=50..80` yang eksplisit.
- Tidak ada average, weight, ensemble, fallback, atau koreksi numerik antara C0 dan Xiong.
- Ekonomi (`revenue_gabah` dan cash contribution) selalu memakai primary C0, juga ketika reference valid.
- `d > 8` hanya menghasilkan `survival_risk=HIGH`; sistem tidak menghitung numerical survival/N_sold dan revenue all-sold bebek menjadi `null`.

## Menjalankan

Set `JWT_SECRET_KEY` melalui environment atau `.env` lokal (gunakan nilai acak yang tidak pernah di-commit), kemudian:

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

`yield_are_kg` dan `yield_total_kg` selalu PRIMARY C0. `yield_literature_reference_*` dan `literature_gap_kg_are` adalah diagnostic reference-only; `literature_gap_kg_are` tidak mengubah economics. Harga default: gabah 6000, beli bebek 25000, jual bebek 45000. Input `0` adalah runtime value yang sah.

History authenticated memakai schema v4 dan menyimpan request serta exact response A+C. v1-v3 dipertahankan secara fisik tetapi current history API tidak mengeksposnya. API riset saat ini tidak mengekspos optimizer.

Lihat [tes skenario](docs/tes_skenario.md), [runtime evidence](docs/runtime_evidence_model_ac.json), [stale semantics audit](docs/stale_semantics_audit_model_ac.md), dan [research evidence manifest](docs/research_evidence_manifest_model_ac.md).
