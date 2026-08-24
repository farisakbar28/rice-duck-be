# PANDUAN PENGUJIAN SKENARIO — BACKEND DSS PADI-BEBEK VERSI A

> **Branch:** A — Strict Separation + Evidence Reset  
> **SoT:** `docs/Model Matematika Data Collection DSS Padi Bebek FINAL.md` pada branch A.  
> **Critical rule:** 36 clean cycles adalah **test-only**. Hasil replay tidak boleh digunakan mengubah parameter/formula branch A.

## 1. Tujuan

Dokumen ini menguji dua hal yang harus dipisahkan:

1. **Historical Test-Only Replay**: seluruh 36 clean cycles dipakai untuk memverifikasi density/risk/domain semantics terhadap backend nyata. Actual yield disimpan sebagai context, tetapi tidak dibuat MAE production karena local duration evidence tidak overlap dengan domain Xiong.
2. **Synthetic Contract & Formula Tests**: input buatan dipakai untuk menguji boundary, Xiong validity guard, arithmetic economics, optional-cost handling, dan HTTP/schema contract.

Endpoint canonical tetap `POST /api/v1/dss/simulate`.

## 2. Aturan Evidence

1. Jalankan service nyata; jangan mengganti response dengan kalkulasi manual.
2. Simpan `backend_commit`, command start, timestamp, request, HTTP status, dan raw JSON response.
3. `Actual Yield` bukan ground truth untuk numerical Xiong production bila `yield_status=OUTSIDE_LITERATURE_DOMAIN`.
4. `U_bebek=21` dan `t_duck=45` pada clean workbook adalah estimasi/imputasi; keduanya **bukan raw biological ground truth**.
5. `Null(default Jarwo 2:1)` diberi tanda `DefaultJarwo*`; boleh dinormalisasi ke `jajar_legowo` hanya untuk replay semantics, dan provenance harus menyebut bahwa sistem berasal dari default clean dataset.
6. Jangan menggunakan `N_sold_actual` sebagai survival ground truth.
7. Jangan menghitung realized-profit error terhadap cash contribution model.
8. Jangan menghapus row setelah melihat error/response.

## 3. Historical Test-Only Replay — 36 Siklus

`literature_duration_days` **tidak diisi** pada historical replay karena durasi aktual individual tidak tersedia. Backend harus abstain dari numerical Xiong local prediction. Actual yield ditampilkan hanya untuk audit transferability.

| ID | Raw row | Farmer | A are | J | d/are | Varietas | Sistem | Actual yield | Expected density status | Xiong density domain | Expected yield result |
|---|---:|---|---:|---:|---:|---|---|---:|---|---|---|
| A01 | 4 | I Wayan Suarta | 6.60 | 30 | 4.545 | sertani | DefaultJarwo* | 53.03 | WARNING_ABOVE_RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A02 | 5 | I Made Widana | 10.50 | 28 | 2.667 | sertani | DefaultJarwo* | 47.71 | RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A03 | 6 | I Wayan Suwendhi Artha | 4.80 | 10 | 2.083 | sertani | DefaultJarwo* | 59.38 | RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A04 | 7 | I Ketut Tantra | 4.50 | 16 | 3.556 | sertani | DefaultJarwo* | 50.00 | RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A05 | 8 | I Made Arsania | 3.60 | 13 | 3.611 | sertani | DefaultJarwo* | 45.83 | RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A06 | 9 | I Nyoman Ranes | 5.10 | 5 | 0.980 | sertani | DefaultJarwo* | 48.04 | UNDER | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A07 | 10 | I Wayan Wiratna | 3.20 | 10 | 3.125 | sertani | DefaultJarwo* | 60.31 | RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A08 | 11 | I Ketut Alit Sudarsana | 10.00 | 65 | 6.500 | sertani | DefaultJarwo* | 60.50 | WARNING_ABOVE_RECOMMENDED | OUT | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A09 | 12 | I Gusti Ngurah Rai Sukarta | 5.50 | 40 | 7.273 | sertani | DefaultJarwo* | 53.09 | WARNING_ABOVE_RECOMMENDED | OUT | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A10 | 14 | I Wayan Sadia | 7.26 | 9 | 1.240 | sertani | DefaultJarwo* | 59.37 | UNDER | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A11 | 18 | I Wayan Suarta | 6.60 | 30 | 4.545 | sertani | Jarwo | 63.86 | WARNING_ABOVE_RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A12 | 19 | I Made Widana | 10.50 | 28 | 2.667 | sertani | Jarwo | 45.41 | RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A13 | 20 | I Wayan Suwendhi Artha | 4.80 | 8 | 1.667 | sertani | Jarwo | 65.73 | UNDER | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A14 | 21 | I Ketut Tantra | 4.50 | 10 | 2.222 | inpari | Jarwo | 55.78 | RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A15 | 23 | I Nyoman Ranes | 5.10 | 10 | 1.961 | inpari | Jarwo | 21.02 | UNDER | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A16 | 24 | I Wayan Wiratna | 3.20 | 3 | 0.938 | sertani | Jarwo | 37.50 | UNDER | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A17 | 25 | I Ketut Alit Sudarsana | 14.41 | 30 | 2.082 | sertani | Jarwo | 52.43 | RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A18 | 26 | I Gusti Ngurah Rai Sukarta | 5.50 | 50 | 9.091 | sertani | Jarwo | 53.55 | HIGH_RISK | OUT | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A19 | 28 | I Gusti Nyoman Ngurah Wirasuta | 6.35 | 20 | 3.150 | sertani | Jarwo | 45.83 | RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A20 | 34 | I Gusti Ngurah Rai Sukarta | 10.21 | 32 | 3.134 | sertani | Jarwo | 50.00 | RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A21 | 36 | I Wayan Suarta | 6.60 | 19 | 2.879 | inpari | Tegel | 47.20 | RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A22 | 37 | I Wayan Suwendhi Artha | 4.80 | 9 | 1.875 | sertani | Tegel | 60.42 | UNDER | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A23 | 38 | I Ketut Alit Sudarsana | 10.00 | 32 | 3.200 | sertani | Jarwo | 53.40 | RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A24 | 39 | I Gusti Ngurah Rai Sukarta | 5.50 | 18 | 3.273 | sertani | Jarwo | 47.00 | RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A25 | 41 | I Gusti Nyoman Ngurah Wirasuta | 6.35 | 5 | 0.787 | inpari | Tegel | 60.79 | UNDER | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A26 | 43 | I Made Arsania | 3.60 | 15 | 4.167 | sertani | Jarwo | 40.42 | WARNING_ABOVE_RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A27 | 44 | I Ketut Alit Sudarsana | 10.00 | 29 | 2.900 | inpari | Tegel | 38.65 | RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A28 | 46 | I Wayan Jana | 4.50 | 9 | 2.000 | sertani | Jarwo | 62.89 | RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A29 | 47 | I Gusti Ngurah Putu Suka Nada | 3.00 | 6 | 2.000 | sertani | Jarwo | 13.50 | RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A30 | 49 | I Wayan Arta Susila | 3.55 | 7 | 1.972 | sertani | Jarwo | 38.03 | UNDER | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A31 | 51 | I Wayan Suwendhi Artha | 4.81 | 10 | 2.079 | sertani | Jarwo | 43.45 | RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A32 | 53 | I Nyoman Suwitra | 4.80 | 10 | 2.083 | sertani | Jarwo | 40.10 | RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A33 | 55 | Alm. I Ketut Tantra | 3.45 | 7 | 2.029 | sertani | Jarwo | 7.54 | RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A34 | 60 | I Wayan Buana | 4.44 | 9 | 2.027 | sertani | Jarwo | 40.20 | RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A35 | 61 | I Ketut Buda | 4.43 | 9 | 2.032 | sertani | Jarwo | 33.75 | RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |
| A36 | 62 | I Made Suardika | 3.77 | 8 | 2.122 | sertani | Jarwo | 36.47 | RECOMMENDED | VALID | `OUTSIDE_LITERATURE_DOMAIN` / no production numeric yield |

\* `DefaultJarwo` berasal dari field clean dataset `Null(default Jarwo 2:1)`, bukan observasi sistem tanam eksplisit.

### Expected aggregate result

- `36/36` replay mempertahankan row; tidak ada post-hoc deletion.
- `33/36` berada pada Xiong density domain (`d_ha<=600`); `3/36` di luar density domain.
- Local operational duration evidence sekitar `28–40` hari tidak overlap dengan Xiong `50–80` hari.
- **Primary numerical MAE/RMSE Versi A tidak dihitung.** Backend yang menghasilkan numerical local yield secara diam-diam pada suite ini adalah **FAIL**.

## 4. Request Template Historical Replay

```json
{
  "land_area_are": "<A_are>",
  "duck_count": "<J>",
  "rice_variety": "sertani|inpari",
  "planting_system": "jajar_legowo|tegel",
  "duck_age_days": 21,
  "planting_date": "<source date if available, otherwise omit>",
  "p_gabah": "<source price if available, otherwise omit>",
  "p_duck_buy": "<source price if available, otherwise omit>",
  "p_duck_sell": 45000
}
```

Do **not** add `literature_duration_days=45` merely because clean workbook stores `t_duck=45`; that field is an imputation and bukan observasi durasi individual.

## 5. Synthetic Boundary & Golden Tests

| ID | Input inti | Expected |
|---|---|---|
| S-A01 | `A=10,J=19,Jarwo` | `d=1.9`, `UNDER` |
| S-A02 | `A=10,J=20,Jarwo` | `d=2`, `RECOMMENDED` |
| S-A03 | `A=10,J=40,Jarwo` | `d=4`, `RECOMMENDED` |
| S-A04 | `A=10,J=41,Jarwo` | `WARNING_ABOVE_RECOMMENDED` |
| S-A05 | `A=10,J=80,Jarwo` | warning, **not** survival high risk |
| S-A06 | `A=10,J=81,Jarwo` | `HIGH_RISK`, `survival_risk=HIGH`, duck all-sold revenue `null` |
| S-A07 | `A=10,J=30,Tegel` | `d=3`, `RECOMMENDED` |
| S-A08 | `A=10,J=31,Tegel` | `WARNING_ABOVE_RECOMMENDED` |
| S-A09 | `duck_age_days=20` | `NOT_RECOMMENDED` |
| S-A10 | `duck_age_days=21` | `LOCAL_READY` |
| S-A11 | `duck_age_days=30` | `LOCAL_READY` |
| S-A12 | `duck_age_days=31` | `OLDER_CONSERVATIVE` |
| S-A13 | `A=10,J=40,t=49` | `OUTSIDE_LITERATURE_DOMAIN`, yield `null` |
| S-A14 | `A=10,J=40,t=50` | valid Xiong; `yield_are≈65.004455 kg/are` |
| S-A15 | `A=10,J=40,t=80` | valid Xiong; `yield_are≈69.739600 kg/are` |
| S-A16 | `A=10,J=40,t=81` | `OUTSIDE_LITERATURE_DOMAIN` |
| S-A17 | `A=10,J=61,t=80` | density `610/ha`; `OUTSIDE_LITERATURE_DOMAIN` |
| S-A18 | `A<=0` | HTTP validation failure |
| S-A19 | `J=0` | accepted model input; `d=0`, `UNDER`; duck cash terms zero |

### Golden numerical Xiong + economy case S-A14

Gunakan `A=10`, `J=40`, `Jarwo`, `duck_age_days=21`, `literature_duration_days=50`, `p_gabah=6000`, `p_duck_buy=25000`, `p_duck_sell=45000`.

Expected before DTO rounding:

```text
yield_are_kg                 ≈ 65.0044549762
yield_total_kg               ≈ 650.0445497616
revenue_gabah                ≈ Rp3,900,267.30
revenue_duck_all_sold        = Rp1,800,000
cost_duck_buy                = Rp1,000,000
cash_contribution_before_optional ≈ Rp4,700,267.30
```

No hidden feed or infrastructure deduction.

## 6. Calendar Contract Tests

Dengan `planting_date=2026-01-01`, backend harus mengembalikan HST recommendation window `release=21–30`, `withdraw=56–60` dan date range hasil penambahan kalender. Backend **tidak boleh** mengembalikan kembali fixed `HST_out=65`, `t_active=44`, atau harvest window legacy.

## 7. Evidence Template

Untuk setiap case:

```text
backend_branch:
backend_commit:
backend_start_command:
endpoint:
request_timestamp:
request_body:
http_status:
raw_response_json:

expected_semantics:
actual_semantics:
result: PASS|FAIL
numerical_difference_if_applicable:
discrepancy:
```

## 8. Pass/Fail Global

Branch A dianggap sesuai SoT hanya jika:

- historical local replay **tidak** memaksakan numerical Xiong yield;
- Xiong hanya menghasilkan angka pada domain `0<d_ha<=600` dan `50<=t<=80`;
- tidak ada `N_survive`/survival percentage;
- `d>8` hanya menjadi risk gate dan menonaktifkan duck all-sold revenue;
- tidak ada fixed feed Core, old yield `47.8767507`, old p_sell `52500`, atau fixed calendar `21/65/44`;
- optional/missing data tetap `null`/explicitly unavailable, bukan synthetic zero.
