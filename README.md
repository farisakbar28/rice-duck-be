# DSS Padi-Bebek Backend — Model A

Backend FastAPI ini menerapkan **A_STRICT_SEPARATION**. Sumber matematika tertinggi adalah [Model Matematika Data Collection DSS Padi Bebek FINAL.md](docs/Model%20Matematika%20Data%20Collection%20DSS%20Padi%20Bebek%20FINAL.md). Dataset 36 siklus hanya untuk pengujian; tidak digunakan untuk kalibrasi.

## Menjalankan

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
python -m pytest -q
```

Untuk acceptance HTTP, validator meluncurkan subprocess backend sendiri pada
port loopback bebas dengan database SQLite disposable. Ia juga memverifikasi
bahwa database utama tidak berubah selama replay dan mencocokkan nonce unik
`/health` dari subprocess yang diluncurkannya:

```powershell
python scripts/validate_model_a_runtime.py
```

## Kontrak Model A

`POST /api/v1/dss/simulate` memerlukan `land_area_are>0`, `duck_count>=0`, `rice_variety`, `planting_system`, dan `duck_age_days>=0`. Semua input numerik harus berupa JSON number; `duck_count` dan `duck_age_days` juga integer ketat. String dan angka pecahan untuk field integer ditolak. Tanggal tanam, harga gabah/beli/jual bebek, durasi literatur, dan biaya skenario semuanya opsional.

Age hanya status: `<21` adalah `NOT_RECOMMENDED`, `21–30` adalah `LOCAL_READY`, dan `>30` adalah `OLDER_CONSERVATIVE`. Density `<2` adalah `UNDER`; Jarwo `2–4` dan Tegel `2–3` adalah `RECOMMENDED`; nilai di atas batas sistem sampai `8` adalah `WARNING_ABOVE_RECOMMENDED`; nilai `>8` adalah `HIGH_RISK`. Risiko survival hanya `HIGH` jika density di atas 8 ekor/are; tidak ada prediksi survival numerik.

Kalender selalu memberi window release HST `21–30` dan withdraw HST `56–60`. Date range hanya tersedia bila `planting_date` dikirim; tidak ada tanggal sintetik, `HST_out=65`, atau `t_active=44`. Evidence durasi operasi lokal `28–40` hari adalah konteks dan tidak menjadi input Xiong otomatis.

Yield numerik memakai persamaan Xiong dengan status `literature-uncalibrated` dan hanya tersedia ketika `0 < density_ha <= 600` serta `50 <= literature_duration_days <= 80`. Jika tidak, response secara eksplisit abstain (`OUTSIDE_LITERATURE_DOMAIN` dan yield `null`).

Harga runtime diprioritaskan. Fallback berprovenance `local-estimate` adalah Rp6.000/kg gabah, Rp25.000/ekor beli bebek, dan Rp45.000/ekor skenario jual bebek. Economics memakai istilah cash contribution/scenario estimate, bukan laba nyata. Feed dan infrastruktur hanya mengurangi contribution jika biaya skenario itu memang dikirim.

Simulasi terautentikasi disimpan sebagai history schema v4, dengan payload request/response versioned yang round-trip. Baris v1–v3 tetap historical dan tidak ditafsirkan ulang sebagai Model A.

Endpoint optimizer adalah stub terpisah dan tidak memanggil DSS Core. Protokol dan hasil live validation ada di [docs/tes_skenario.md](docs/tes_skenario.md), dengan raw evidence di [docs/runtime_evidence_model_a.json](docs/runtime_evidence_model_a.json).
