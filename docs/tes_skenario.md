# PANDUAN PENGUJIAN SKENARIO — BACKEND DSS PADI-BEBEK VERSI C

> **Branch:** C — Farmer-Grouped Calibration/Validation Split  
> **SoT:** `docs/Model Matematika Data Collection DSS Padi Bebek FINAL.md` pada branch C.  
> **Critical rule:** final evaluation menggunakan **11 holdout cycles dari 6 farmer** yang sudah ditetapkan sebelum fitting. Holdout ini kini sudah dibuka; jangan memakai ulang untuk model generation, selection, atau tuning.

## 1. Tujuan

1. Memastikan backend nyata mengimplementasikan production C0 `50 kg/are` dan DSS gates secara tepat.
2. Mereplay holdout yang telah dibuka dengan input yang sama/sepadan dari clean recap.
3. Menghitung ulang error yield dari **raw HTTP output**, bukan menyalin angka dokumen.
4. Memverifikasi economics sebagai scenario cash contribution, bukan realized farmer profit.

Endpoint canonical: `POST /api/v1/dss/simulate`.

## 2. Aturan Mutlak

- Simpan commit, command start, request timestamp, request body, status, raw JSON.
- Jangan membuka calibration cycles sebagai "extra test" lalu men-tune model lagi.
- Untuk `DefaultJarwo*`, mapping ke `jajar_legowo` adalah imputation yang sudah ada di clean dataset; jangan menyebutnya raw observed system.
- `duck_age_days=21` pada replay adalah estimasi clean dataset dan tidak dinilai sebagai biological ground truth.
- `N_sold_actual`, feed historical, duck sale revenue, dan raw farmer profit bukan target langsung output model.
- Bila source `planting_date` kosong, **omit/null**; jangan membuat tanggal sintetis.
- Source `Tanggal Tanam (Sumber)` tersedia hanya untuk H07/raw row 38
  (`2024-04-22`), H08/raw row 43 (`2024-10-01`), dan H09/raw row 44
  (`2024-09-28`); ketiganya harus dikirim dalam request HTTP replay.
- Runtime `p_gabah` dan `p_duck_buy` pada replay menggunakan source value agar arithmetic economics dapat diaudit; nilai default hanya diuji pada synthetic cases.

## 3. Pre-specified Holdout Replay

| ID | Raw row | Farmer | A are | J | d/are | Var | Sistem | Actual yield | Expected pred | Error pred-actual | Expected total kg | p_gabah | p_duck_buy source | Expected Cost_duck_buy | Expected CashContribution_before_optional |
|---|---:|---|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| H01 | 8 | I Made Arsania | 3.60 | 13 | 3.611 | sertani | DefaultJarwo* | 45.83 | 50.00 | 4.17 | 180.00 | 6000 | 25000 | 325000 | 1340000 |
| H02 | 9 | I Nyoman Ranes | 5.10 | 5 | 0.980 | sertani | DefaultJarwo* | 48.04 | 50.00 | 1.96 | 255.00 | 6000 | 25000 | 125000 | 1630000 |
| H03 | 11 | I Ketut Alit Sudarsana | 10.00 | 65 | 6.500 | sertani | DefaultJarwo* | 60.50 | 50.00 | -10.50 | 500.00 | 6000 | 7539 | 490035 | 5434965 |
| H04 | 14 | I Wayan Sadia | 7.26 | 9 | 1.240 | sertani | DefaultJarwo* | 59.37 | 50.00 | -9.37 | 363.00 | 7500 | 22222.22222 | 199999.99998 | 2927500.00002 |
| H05 | 23 | I Nyoman Ranes | 5.10 | 10 | 1.961 | inpari | Jarwo | 21.02 | 50.00 | 28.98 | 255.00 | 7500 | 5000 | 50000 | 2312500 |
| H06 | 25 | I Ketut Alit Sudarsana | 14.41 | 30 | 2.082 | sertani | Jarwo | 52.43 | 50.00 | -2.43 | 720.50 | 7500 | 10000 | 300000 | 6453750 |
| H07 | 38 | I Ketut Alit Sudarsana | 10.00 | 32 | 3.200 | sertani | Jarwo | 53.40 | 50.00 | -3.40 | 500.00 | 6300 | 0 | 0 | 4590000 |
| H08 | 43 | I Made Arsania | 3.60 | 15 | 4.167 | sertani | Jarwo | 40.42 | 50.00 | 9.58 | 180.00 | 6000 | 0 | 0 | 1755000 |
| H09 | 44 | I Ketut Alit Sudarsana | 10.00 | 29 | 2.900 | inpari | Tegel | 38.65 | 50.00 | 11.35 | 500.00 | 6000 | 0 | 0 | 4305000 |
| H10 | 47 | I Gusti Ngurah Putu Suka Nada | 3.00 | 6 | 2.000 | sertani | Jarwo | 13.50 | 50.00 | 36.50 | 150.00 | 6000 | 25000 | 150000 | 1020000 |
| H11 | 62 | I Made Suardika | 3.77 | 8 | 2.122 | sertani | Jarwo | 36.47 | 50.00 | 13.53 | 188.50 | 6000 | 25000 | 200000 | 1291000 |

\* `DefaultJarwo` = `Null(default Jarwo 2:1)` pada clean dataset; provenance harus dipertahankan.

Mapping `p_duck_buy` memakai source file `DSS_Padi_Bebek_Rekap_Bersih_v10(1).xlsx`, sheet `Dataset Actual Bersih`, join key `Excel Row (Sumber)`, field `Buy Price Duck (Rp/ekor)`. Join dilakukan memakai raw row, bukan nama farmer, karena satu farmer dapat memiliki beberapa cycle. Nilai `0` pada H07, H08, dan H09 adalah runtime source value eksplisit; H09 mempunyai evidence operasional bahwa bebek memakai cycle sebelumnya, sedangkan H07/H08 hanya didokumentasikan sebagai `recorded source value = Rp0/duck`.

Mapping `planting_date` memakai workbook/sheet/join key yang sama, dengan field
`Tanggal Tanam (Sumber)`. H07/H08/H09 membawa tanggal sumber di atas; seluruh
row lain tidak membawa field itu dalam HTTP request sehingga backend wajib
mempertahankan returned date fields sebagai `null`.

Source-level duck purchase prices were subsequently restored to the holdout replay fixture from the cleaned local dataset using the original source-row identifier. This correction affects only the arithmetic audit of `Cost_duck_buy` and scenario cash contribution. It does not alter the frozen yield model, model-selection process, holdout composition, or yield-validation metrics.

`actual_yield` and `actual_gabah_revenue` use the same workbook, sheet, and
`Excel Row (Sumber)` join. They retain the exact source cells from `Actual
Yield (kg/are)` and `Actual Gabah Revenue (Rp)`, respectively. The two-decimal
Actual Yield values in this document are display-only; metric calculation uses
the exact fixture values preserved in `docs/runtime_evidence_model_c.json`.

### Expected aggregate metrics

Backend raw yield outputs pada 11 row harus menghasilkan, dengan toleransi floating-point wajar:

```text
MAE   = 11.9785716318 kg/are
RMSE  = 15.9898352553 kg/are
MedAE = 9.5833333300 kg/are
Bias  = +7.3067061736 kg/are
```

Nilai akademik yang ditampilkan tetap: `11.979 / 15.990 / 9.583 / +7.307`.

Jika aggregate metrics berbeda material, implementation dianggap tidak identik dengan frozen production C0 atau row mapping salah.

## 4. Request Construction

Untuk setiap H01–H11:

```json
{
  "land_area_are": "<A>",
  "duck_count": "<J>",
  "rice_variety": "sertani|inpari",
  "planting_system": "jajar_legowo|tegel",
  "duck_age_days": 21,
  "planting_date": "<source date if present; otherwise omit>",
  "p_gabah": "<source Price Gabah>",
  "p_duck_buy": "<source Buy Price Duck>",
  "p_duck_sell": 45000
}
```

Jangan kirim historical feed sebagai Core default. Feed hanya boleh diuji terpisah sebagai `c_feed_scenario` bila memang ingin menjalankan sensitivity scenario.

## 5. Expected Row Semantics

- `yield_are_kg` / `yield_primary_are` harus tepat `50.0` untuk seluruh holdout.
- `yield_total_kg = 50*A_are`.
- `density_status` diturunkan dari input; tidak mengubah yield C0.
- Tidak ada `N_survive` atau survival percentage.
- Hanya `d_are>8` yang menghasilkan `survival_risk=HIGH`; tidak ada holdout row di atas 8, sehingga `survival_risk` normalnya `null` pada H01–H11.
- `revenue_duck_all_sold_scenario=J*45000` pada H01–H11; ini scenario ceiling, bukan actual-sale prediction.
- `cost_duck_buy=J*p_duck_buy` menggunakan source runtime input, termasuk `0` bila source memang `0`.
- `cash_contribution_before_optional = revenue_gabah + J*45000 - cost_duck_buy`; gunakan toleransi Rp0.01 untuk H04 karena harga sumber decimal.
- cash contribution tidak dibandingkan ke raw farmer profit sebagai accuracy metric.

### Comparison validity

Perbandingan yang valid adalah backend yield terhadap actual yield dan
`revenue_gabah` backend terhadap field sumber `Actual Gabah Revenue (Rp)` yang
eksplisit (bukan hasil turunan `actual_yield` yang ditampilkan). `cost_duck_buy`
dibandingkan terhadap `J × source p_duck_buy`. Skenario
`revenue_duck_all_sold_scenario` **tidak** valid dibandingkan dengan raw Duck
Sale Revenue, karena ia adalah ceiling scenario seluruh bebek terjual. Demikian
juga `cash_contribution_before_optional` **tidak** valid dibandingkan dengan
raw farmer profit; ia bukan realized profit petani.


## 6. Synthetic Contract & Boundary Tests

| ID | Input | Expected |
|---|---|---|
| S-C01 | `A=10,J=20,Jarwo` | `d=2`, `RECOMMENDED`, yield `50` |
| S-C02 | `A=10,J=40,Jarwo` | `d=4`, `RECOMMENDED`, yield `50` |
| S-C03 | `A=10,J=41,Jarwo` | `WARNING_ABOVE_RECOMMENDED`, yield tetap `50` |
| S-C04 | `A=10,J=80,Jarwo` | warning, no survival numeric, yield `50` |
| S-C05 | `A=10,J=81,Jarwo` | `HIGH_RISK`, `survival_risk=HIGH`, duck all-sold revenue `null`, yield tetap `50` |
| S-C06 | `A=10,J=30,Tegel` | `RECOMMENDED` |
| S-C07 | `A=10,J=31,Tegel` | `WARNING_ABOVE_RECOMMENDED` |
| S-C08 | age `20/21/30/31` | `NOT_RECOMMENDED/LOCAL_READY/LOCAL_READY/OLDER_CONSERVATIVE` |
| S-C09 | prices omitted, `A=10,J=20` | fallback `p_gabah=6000`, `p_buy=25000`, `p_sell=45000` dengan provenance |
| S-C10 | optional costs omitted | no hidden feed/infra deduction; after-optional may be `null`/same only per explicit schema rule |
| S-C11 | `J=0,A=10` | accepted; yield still `50 kg/are`; duck cash components zero |
| S-C12 | `A<=0` | request validation failure |

Golden S-C09 sebelum optional costs:

```text
yield_total_kg = 500
revenue_gabah = 3,000,000
revenue_duck_all_sold_scenario = 900,000
cost_duck_buy = 500,000
cash_contribution_before_optional = 3,400,000
```


## 7. Calendar Tests

Calendar terbaru hanya merepresentasikan recommendation window:

```text
release HST = 21–30
withdraw/heading HST ≈ 56–60
```

Jika `planting_date` tersedia, backend mengubah boundary HST menjadi date ranges. Jika tidak tersedia, date fields `null` tetapi HST ranges tetap tersedia. Fixed `HST_out=65`, `t_active=44`, dan harvest windows lama adalah **FAIL**.

## 8. Evidence Template

```text
backend_branch:
backend_commit:
backend_start_command:
endpoint:
request_timestamp:
request_body:
http_status:
raw_response_json:

actual_yield_source:
predicted_yield_backend:
error_backend_minus_actual:
density_expected:
density_backend:
economic_arithmetic_check:
result: PASS|FAIL
discrepancy:
```

## 9. Pass/Fail Global

Branch dianggap sesuai SoT jika:

- 11 pre-specified holdout menghasilkan frozen C0 dan aggregate metrics di atas;
- tidak ada numerical survival model atau `N_survive`;
- `yield_are=50` tidak berubah oleh density/system/variety/age;
- d>8 hanya risk gate + disable all-sold duck revenue;
- calendar memakai ranges terbaru, bukan 21/65/44;
- feed/infrastructure tidak menjadi hidden Core defaults;
- old `47.8767507`, `52500`, survival 60%, dan old `Net_Cash_Contribution_DSS` semantics tidak aktif;
- raw farmer profit tidak dipakai sebagai numerical ground truth cash contribution.

## Final clean-HEAD runtime result

Evidence was captured over real loopback Uvicorn HTTP from clean HEAD
`ffb4fd7c3e865061e1475192039c00836442aa81`: `working_tree_dirty=false` at
startup, and the isolated runtime SQLite database left the main database
unchanged. Raw requests and responses are preserved in
`docs/runtime_evidence_model_c.json`.

| ID | Raw row | Source planting_date | Actual Yield (displayed) | Backend Yield | Yield Error | Actual Gabah Revenue (source) | Backend Revenue_gabah | density | density status | Backend Cost_duck_buy | Backend CashContribution_before_optional | price provenance | Release / withdraw window returned | HTTP | PASS/FAIL |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- | --- | ---: | --- |
| H01 | 8 | omitted / null | 45.83 | 50.00 | +4.17 | 990,000.00 | 1,080,000.00 | 3.611111 | RECOMMENDED | 325,000.00 | 1,340,000.00 | `p_gabah`/`p_duck_buy`: runtime (source row) | null / null | 200 | PASS |
| H02 | 9 | omitted / null | 48.04 | 50.00 | +1.96 | 1,470,000.00 | 1,530,000.00 | 0.980392 | UNDER | 125,000.00 | 1,630,000.00 | `p_gabah`/`p_duck_buy`: runtime (source row) | null / null | 200 | PASS |
| H03 | 11 | omitted / null | 60.50 | 50.00 | -10.50 | 3,630,000.00 | 3,000,000.00 | 6.500000 | WARNING_ABOVE_RECOMMENDED | 490,035.00 | 5,434,965.00 | `p_gabah`/`p_duck_buy`: runtime (source row) | null / null | 200 | PASS |
| H04 | 14 | omitted / null | 59.37 | 50.00 | -9.37 | 3,232,500.00 | 2,722,500.00 | 1.239669 | UNDER | 200,000.00 | 2,927,500.00 | `p_gabah`/`p_duck_buy`: runtime (source row) | null / null | 200 | PASS |
| H05 | 23 | omitted / null | 21.02 | 50.00 | +28.98 | 804,000.00 | 1,912,500.00 | 1.960784 | UNDER | 50,000.00 | 2,312,500.00 | `p_gabah`/`p_duck_buy`: runtime (source row) | null / null | 200 | PASS |
| H06 | 25 | omitted / null | 52.43 | 50.00 | -2.43 | 5,666,250.00 | 5,403,750.00 | 2.081888 | RECOMMENDED | 300,000.00 | 6,453,750.00 | `p_gabah`/`p_duck_buy`: runtime (source row) | null / null | 200 | PASS |
| H07 | 38 | 2024-04-22 | 53.40 | 50.00 | -3.40 | 3,364,200.00 | 3,150,000.00 | 3.200000 | RECOMMENDED | 0.00 | 4,590,000.00 | `p_gabah`/`p_duck_buy`: runtime (source row) | release 2024-05-13–2024-05-22; withdraw 2024-06-17–2024-06-21 | 200 | PASS |
| H08 | 43 | 2024-10-01 | 40.42 | 50.00 | +9.58 | 873,000.00 | 1,080,000.00 | 4.166667 | WARNING_ABOVE_RECOMMENDED | 0.00 | 1,755,000.00 | `p_gabah`/`p_duck_buy`: runtime (source row) | release 2024-10-22–2024-10-31; withdraw 2024-11-26–2024-11-30 | 200 | PASS |
| H09 | 44 | 2024-09-28 | 38.65 | 50.00 | +11.35 | 2,319,000.00 | 3,000,000.00 | 2.900000 | RECOMMENDED | 0.00 | 4,305,000.00 | `p_gabah`/`p_duck_buy`: runtime (source row) | release 2024-10-19–2024-10-28; withdraw 2024-11-23–2024-11-27 | 200 | PASS |
| H10 | 47 | omitted / null | 13.50 | 50.00 | +36.50 | 243,000.00 | 900,000.00 | 2.000000 | RECOMMENDED | 150,000.00 | 1,020,000.00 | `p_gabah`/`p_duck_buy`: runtime (source row) | null / null | 200 | PASS |
| H11 | 62 | omitted / null | 36.47 | 50.00 | +13.53 | 825,000.00 | 1,131,000.00 | 2.122016 | RECOMMENDED | 200,000.00 | 1,291,000.00 | `p_gabah`/`p_duck_buy`: runtime (source row) | null / null | 200 | PASS |

Final metrics from those 11 HTTP responses, calculated from the exact retained
source yields: MAE `11.9785716318`, RMSE `15.9898352553`, MedAE
`9.5833333300`, and Bias `+7.3067061736` kg/are. Academic display values are
`11.979 / 15.990 / 9.583 / +7.307`; this table's yield cells are rounded only
for readability. Each actual revenue value is the explicit source `Actual
Gabah Revenue (Rp)` cell, and the JSON evidence records its comparison with
`backend_revenue_gabah`; it is never calculated from the displayed yield.
`Cost_duck_buy`
and `CashContribution_before_optional` arithmetic both passed 11/11. Calendar
source-date audit passed 11/11; S-C01–S-C12 passed 12/12; calendar and history
v4 passed; v1–v3 history was physically preserved and hidden over current HTTP.
