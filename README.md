# DSS Padi-Bebek Backend

Backend FastAPI untuk kalkulator deterministik DSS Padi-Bebek. Source of Truth tunggal adalah [Model Matematika Data Collection DSS Padi Bebek FINAL.md](docs/Model%20Matematika%20Data%20Collection%20DSS%20Padi%20Bebek%20FINAL.md). Jika kontrak API atau dokumentasi lain berbeda, SoT tersebut yang berlaku.

## Scope

`POST /api/v1/dss/simulate` menghitung estimasi **Net_Cash_Contribution_DSS**. Nilai ini adalah kontribusi kas parsial, bukan laba akuntansi, realized farmer profit, atau profit incremental murni.

Optimizer adalah fitur stub terpisah dan berada di luar scope matematika DSS Core.

## Menjalankan aplikasi

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
python -m pytest -q
```

Swagger tersedia di `http://127.0.0.1:8000/docs`.

## Endpoint

| Method | Path | Auth | Keterangan |
|---|---|---|---|
| GET | `/health` | Tidak | Health check |
| GET | `/api/v1/dss/options` | Tidak | Varietas dan sistem tanam valid |
| POST | `/api/v1/dss/simulate` | Opsional | Simulasi DSS Core |
| POST | `/api/v1/dss/visualize` | Tidak | Zona density/umur dan waterfall Core |
| GET/DELETE | `/api/v1/dss/histories/{id}` | Bearer | Baca/hapus history v3 |

## Input production

Semua tujuh field wajib dikirim. Tidak ada fallback tanggal, umur, atau harga beli bebek.

| Field | Aturan |
|---|---|
| `land_area_are` | float `> 0` |
| `duck_count` | integer `> 0` |
| `rice_variety` | `sertani` atau `inpari` (generic) |
| `planting_system` | `jajar_legowo` hanya Jajar Legowo 2:1, atau `tegel` |
| `duck_age_days` | integer `>= 0` |
| `planting_date` | tanggal ISO `YYYY-MM-DD` |
| `p_duck_buy` | float `>= 0`; `0` berarti tidak ada current-cycle cash purchase |

```json
{
  "land_area_are": 10,
  "duck_count": 20,
  "rice_variety": "sertani",
  "planting_system": "jajar_legowo",
  "duck_age_days": 21,
  "planting_date": "2026-01-01",
  "p_duck_buy": 15000
}
```

Schema validation errors memakai HTTP `400`; varietas/sistem yang tidak terdapat pada lookup memakai `422`.

## Model runtime

```text
AgeFlag: <21 TOO_YOUNG; 21–30 RECOMMENDED; >30 ABOVE_RECOMMENDED_AGE
d = duck_count / land_area_are
d_ha = 100 * d
N_survive = duck_count                 jika d <= 8
          = floor(0.60 * duck_count)   jika d > 8
Yield_are_pred = 47.8767507 kg/are
Yield_total_pred = Yield_are_pred * land_area_are
```

Sertani memiliki jendela panen 100–110 HST; Inpari memakai reference window empiris lokal 109–116 HST. Window Inpari dibentuk dari tiga observasi lokal (109, 112, dan 116 HST; median deskriptif 112) dan bukan generalisasi seluruh subvarietas. Age dan density tidak mengalikan yield. Density hanya memengaruhi survival ketika `d > 8`.

```text
Revenue_gabah = Yield_total_pred * 6000
Revenue_duck_potential = N_survive * 52500
Cost_duck_buy = duck_count * p_duck_buy
Cost_feed = duck_count * 20000
Core_Cash_Cost = Cost_duck_buy + Cost_feed
Total_Revenue_DSS = Revenue_gabah + Revenue_duck_potential
Net_Cash_Contribution_DSS = Total_Revenue_DSS - Core_Cash_Cost
```

## Response canonical

Response memuat `age_flag`, `density_are`, `density_ha`, `density_status`, kalender (`HST_in`, `HST_out`, `D_in`, `D_out`, dan window panen), `N_survive`, yield, seluruh field ekonomi Core, `warnings`, dan `sandbox`.

Sandbox weeding adalah estimasi per kegiatan; pestisida adalah indikator upper bound nonmoneter; fertilizer/material adalah research reference; infrastructure hanya context/reference tanpa formula biaya. Tidak ada bagian sandbox yang memengaruhi Core.

Prediction untuk area di bawah 2,5 are tetap diterima, tetapi response menampilkan warning karena berada di luar domain numerical validation lokal.

## History dan validation

Simulasi dengan Bearer token disimpan sebagai schema version 3. Detail history mengembalikan semantic response yang sama dengan simulasi asal. Record v1/v2 tetap berada pada persistence legacy dan tidak diinterpretasikan sebagai output SoT final.

Protokol replay dan boundary test ada pada [docs/tes_skenario.md](docs/tes_skenario.md). H01–H11 hanya membandingkan field yang semantik-kompatibel; `N_sold_actual` dan raw farmer profit bukan ground truth untuk survival atau `Net_Cash_Contribution_DSS`.
