# PANDUAN PENGUJIAN SKENARIO — BACKEND DSS PADI-BEBEK VERSI KOMBINASI A+C

> **Branch:** A+C — Dual-Evidence Architecture  
> **SoT:** `docs/Model Matematika Data Collection DSS Padi Bebek FINAL.md` pada branch kombinasi A+C.  
> **Critical rule:** final evaluation menggunakan **11 untouched holdout cycles dari 6 farmer** yang sudah ditetapkan sebelum fitting. Jangan mengganti row setelah melihat response.

## 1. Tujuan

1. Memastikan backend nyata mengimplementasikan production C0 `50 kg/are` dan DSS gates secara tepat.
2. Mereplay **untouched holdout** dengan input yang sama/sepadan dari clean recap.
3. Menghitung ulang error yield dari **raw HTTP output**, bukan menyalin angka dokumen.
4. Memverifikasi economics sebagai scenario cash contribution, bukan realized farmer profit.
Selain primary C0, historical local replay harus mengembalikan `Yield_literature_reference=null` dengan `literature_reference_status=OUTSIDE_LITERATURE_DOMAIN` ketika tidak ada explicit valid `literature_duration_days`. Reference Xiong tidak boleh mengubah primary yield/economics.


Endpoint canonical: `POST /api/v1/dss/simulate`.

## 2. Aturan Mutlak

- Simpan commit, command start, request timestamp, request body, status, raw JSON.
- Jangan membuka calibration cycles sebagai "extra test" lalu men-tune model lagi.
- Untuk `DefaultJarwo*`, mapping ke `jajar_legowo` adalah imputation yang sudah ada di clean dataset; jangan menyebutnya raw observed system.
- `duck_age_days=21` pada replay adalah estimasi clean dataset dan tidak dinilai sebagai biological ground truth.
- `N_sold_actual`, feed historical, duck sale revenue, dan raw farmer profit bukan target langsung output model.
- Bila source `planting_date` kosong, **omit/null**; jangan membuat tanggal sintetis.
- Runtime `p_gabah` dan `p_duck_buy` pada replay menggunakan source value agar arithmetic economics dapat diaudit; nilai default hanya diuji pada synthetic cases.

## 3. Untouched Holdout Replay

| ID | Raw row | Farmer | A are | J | d/are | Var | Sistem | Actual yield | Expected pred | Error pred-actual | Expected total kg | p_gabah | Expected Revenue_gabah |
|---|---:|---|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|
| H01 | 8 | I Made Arsania | 3.60 | 13 | 3.611 | sertani | DefaultJarwo* | 45.83 | 50.00 | 4.17 | 180.00 | 6000 | 1080000.00 |
| H02 | 9 | I Nyoman Ranes | 5.10 | 5 | 0.980 | sertani | DefaultJarwo* | 48.04 | 50.00 | 1.96 | 255.00 | 6000 | 1530000.00 |
| H03 | 11 | I Ketut Alit Sudarsana | 10.00 | 65 | 6.500 | sertani | DefaultJarwo* | 60.50 | 50.00 | -10.50 | 500.00 | 6000 | 3000000.00 |
| H04 | 14 | I Wayan Sadia | 7.26 | 9 | 1.240 | sertani | DefaultJarwo* | 59.37 | 50.00 | -9.37 | 363.00 | 7500 | 2722500.00 |
| H05 | 23 | I Nyoman Ranes | 5.10 | 10 | 1.961 | inpari | Jarwo | 21.02 | 50.00 | 28.98 | 255.00 | 7500 | 1912500.00 |
| H06 | 25 | I Ketut Alit Sudarsana | 14.41 | 30 | 2.082 | sertani | Jarwo | 52.43 | 50.00 | -2.43 | 720.50 | 7500 | 5403750.00 |
| H07 | 38 | I Ketut Alit Sudarsana | 10.00 | 32 | 3.200 | sertani | Jarwo | 53.40 | 50.00 | -3.40 | 500.00 | 6300 | 3150000.00 |
| H08 | 43 | I Made Arsania | 3.60 | 15 | 4.167 | sertani | Jarwo | 40.42 | 50.00 | 9.58 | 180.00 | 6000 | 1080000.00 |
| H09 | 44 | I Ketut Alit Sudarsana | 10.00 | 29 | 2.900 | inpari | Tegel | 38.65 | 50.00 | 11.35 | 500.00 | 6000 | 3000000.00 |
| H10 | 47 | I Gusti Ngurah Putu Suka Nada | 3.00 | 6 | 2.000 | sertani | Jarwo | 13.50 | 50.00 | 36.50 | 150.00 | 6000 | 900000.00 |
| H11 | 62 | I Made Suardika | 3.77 | 8 | 2.122 | sertani | Jarwo | 36.47 | 50.00 | 13.53 | 188.50 | 6000 | 1131000.00 |

\* `DefaultJarwo` = `Null(default Jarwo 2:1)` pada clean dataset; provenance harus dipertahankan.

### Expected aggregate metrics

Backend raw yield outputs pada 11 row harus menghasilkan, dengan toleransi floating-point wajar:

```text
MAE   = 11.979 kg/are
RMSE  = 15.990 kg/are
MedAE = 9.583 kg/are
Bias  = +7.307 kg/are
```

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
- cash contribution tidak dibandingkan ke raw farmer profit sebagai accuracy metric.

Selain primary C0, historical local replay harus mengembalikan `Yield_literature_reference=null` dengan `literature_reference_status=OUTSIDE_LITERATURE_DOMAIN` ketika tidak ada explicit valid `literature_duration_days`. Reference Xiong tidak boleh mengubah primary yield/economics.


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


### Reference-layer synthetic tests (khusus A+C)

| ID | Input | Expected |
|---|---|---|
| AC-R01 | `A=10,J=40,t=49` | primary `50`; reference `null`; status `OUTSIDE_LITERATURE_DOMAIN` |
| AC-R02 | `A=10,J=40,t=50` | primary `50`; reference `≈65.004455`; gap `≈15.004455` |
| AC-R03 | `A=10,J=40,t=80` | primary `50`; reference `≈69.739600`; gap `≈19.739600` |
| AC-R04 | `A=10,J=40,t=81` | primary `50`; reference `null` |
| AC-R05 | `A=10,J=61,t=80` | primary `50`; reference `null` karena `d_ha>600` |

Untuk AC-R02, economic primary tetap memakai `50 kg/are`; dengan harga 6000/25000/45000 dan J=40, `revenue_gabah_primary=Rp3.000.000` dan `cash_contribution_before_optional=Rp3.800.000`. Xiong reference **tidak** mengubah angka tersebut.

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

- 11 untouched holdout menghasilkan frozen C0 dan aggregate metrics di atas;
- tidak ada numerical survival model atau `N_survive`;
- `yield_primary_are=50` tidak berubah oleh density/system/variety/age;
- d>8 hanya risk gate + disable all-sold duck revenue;
- calendar memakai ranges terbaru, bukan 21/65/44;
- feed/infrastructure tidak menjadi hidden Core defaults;
- old `47.8767507`, `52500`, survival 60%, dan old `Net_Cash_Contribution_DSS` semantics tidak aktif;
- tidak ada averaging/weighted fusion antara primary C dan reference A;
- reference Xiong tidak pernah mengubah `revenue_gabah_primary` atau cash contribution;
- raw farmer profit tidak dipakai sebagai numerical ground truth cash contribution.

## 10. Corrected A+C purchase-price replay and runtime evidence

The authoritative `Buy Price Duck (Rp/ekor)` mapping is H01 25000, H02 25000, H03 7539, H04 22222.22222, H05 5000, H06 10000, H07 0, H08 0, H09 0, H10 25000, H11 25000. Explicit zero is a runtime source value, never a missing-value fallback. Expected `Cost_duck_buy` is respectively 325000, 125000, 490035, 199999.99998, 50000, 300000, 0, 0, 0, 150000, 200000; expected primary cash contribution is 1340000, 1630000, 5434965, 2927500.00002, 2312500, 6453750, 4590000, 1755000, 4305000, 1020000, 1291000.

Real HTTP execution on branch `focus-model-ac` is recorded in `docs/runtime_evidence_model_ac.json`: H01-H11 11/11 passed, purchase-cost and cash audits 11/11, reference abstention 11/11, AC-R01–R05 plus `t=32` 6/6, primary/reference decoupling passed, calendar isolation passed, history v4 round-trip/delete passed, and the main database hash was unchanged.
