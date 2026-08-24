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

### Provenance input sumber untuk replay

Tabel ini adalah transkripsi field yang semantically compatible dari
`DSS_Padi_Bebek_Rekap_Bersih_v10(1).xlsx`, sheet `Dataset Actual Bersih`,
dijoin dengan `Excel Row (Sumber)`. Workbook tidak disalin ke Git. Nilai
`missing` sengaja tidak dikirim agar fallback backend terlihat; `0` adalah
nilai source eksplisit dan tetap dikirim sebagai runtime `0`.

| ID | Source planting date | Source p_gabah | Source p_duck_buy | Field provenance |
|---|---|---:|---:|---|
| A01 | missing | 6000 | 10000 | A/J source; variety normalized; DefaultJarwo*; U_bebek=21 imputed |
| A02 | missing | 6000 | 25000 | A/J source; variety normalized; DefaultJarwo*; U_bebek=21 imputed |
| A03 | missing | 6000 | 30000 | A/J source; variety normalized; DefaultJarwo*; U_bebek=21 imputed |
| A04 | missing | 6000 | 25000 | A/J source; variety normalized; DefaultJarwo*; U_bebek=21 imputed |
| A05 | missing | 6000 | 25000 | A/J source; variety normalized; DefaultJarwo*; U_bebek=21 imputed |
| A06 | missing | 6000 | 25000 | A/J source; variety normalized; DefaultJarwo*; U_bebek=21 imputed |
| A07 | missing | 6000 | 32000 | A/J source; variety normalized; DefaultJarwo*; U_bebek=21 imputed |
| A08 | missing | 6000 | 7539 | A/J source; variety normalized; DefaultJarwo*; U_bebek=21 imputed |
| A09 | missing | 6000 | 8550 | A/J source; variety normalized; DefaultJarwo*; U_bebek=21 imputed |
| A10 | missing | 7500 | 22222.22222 | A/J source; variety normalized; DefaultJarwo*; U_bebek=21 imputed |
| A11 | missing | 7500 | 6666.666667 | A/J source; variety/system normalized; U_bebek=21 imputed |
| A12 | missing | 7500 | 7000 | A/J source; variety/system normalized; U_bebek=21 imputed |
| A13 | missing | 7500 | missing | A/J source; variety/system normalized; U_bebek=21 imputed; p_duck_buy missing |
| A14 | missing | 7500 | 15000 | A/J source; variety/system normalized; U_bebek=21 imputed |
| A15 | missing | 7500 | 5000 | A/J source; variety/system normalized; U_bebek=21 imputed |
| A16 | missing | 7500 | missing | A/J source; variety/system normalized; U_bebek=21 imputed; p_duck_buy missing |
| A17 | missing | 7500 | 10000 | A/J source; variety/system normalized; U_bebek=21 imputed |
| A18 | missing | 7500 | 7000 | A/J source; variety/system normalized; U_bebek=21 imputed |
| A19 | 2024-02-19 | 6000 | 15000 | A/J source; variety/system normalized; U_bebek=21 imputed |
| A20 | 2024-04-15 | 6300 | 12000 | A/J source; variety/system normalized; U_bebek=21 imputed |
| A21 | 2024-04-12 | 6300 | 12000 | A/J source; variety/system normalized; U_bebek=21 imputed |
| A22 | 2024-04-23 | 6300 | 0 | A/J source; variety/system normalized; U_bebek=21 imputed; explicit zero |
| A23 | 2024-04-22 | 6300 | 0 | A/J source; variety/system normalized; U_bebek=21 imputed; explicit zero |
| A24 | 2024-04-15 | 6300 | 12000 | A/J source; variety/system normalized; U_bebek=21 imputed |
| A25 | 2024-07-17 | 6200 | missing | A/J source; variety/system normalized; U_bebek=21 imputed; p_duck_buy missing |
| A26 | 2024-10-01 | 6000 | 0 | A/J source; variety/system normalized; U_bebek=21 imputed; explicit zero |
| A27 | 2024-09-28 | 6000 | 0 | A/J source; variety/system normalized; U_bebek=21 imputed; explicit zero |
| A28 | missing | 6000 | 25000 | A/J source; variety/system normalized; U_bebek=21 imputed |
| A29 | missing | 6000 | 25000 | A/J source; variety/system normalized; U_bebek=21 imputed |
| A30 | missing | 6000 | 25000 | A/J source; variety/system normalized; U_bebek=21 imputed |
| A31 | 2025-04-09 | 6000 | 25000 | A/J source; variety/system normalized; U_bebek=21 imputed |
| A32 | 2025-04-09 | 6000 | 25000 | A/J source; variety/system normalized; U_bebek=21 imputed |
| A33 | 2025-04-19 | 6000 | 25000 | A/J source; variety/system normalized; U_bebek=21 imputed |
| A34 | missing | 6000 | 25000 | A/J source; variety/system normalized; U_bebek=21 imputed |
| A35 | missing | 6000 | 25000 | A/J source; variety/system normalized; U_bebek=21 imputed |
| A36 | missing | 6000 | 25000 | A/J source; variety/system normalized; U_bebek=21 imputed |

`t_duck=45` tidak pernah menjadi `literature_duration_days`: itu imputed/estimated
dan raw individual Xiong duration tidak tersedia. Evidence lokal 28â€“40 hari
juga tidak dikirim sebagai durasi Xiong. `p_duck_sell=45000` tetap nilai
skenario, bukan harga jual aktual sumber.

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

## 9. Runtime Evidence — 2026-08-24

Raw request/response evidence for every HTTP call is stored in [runtime_evidence_model_a.json](runtime_evidence_model_a.json). It includes timestamps, request JSON, HTTP status, expected semantics, the exact raw response body, and PASS/FAIL for A01–A36, S-A01–S-A19, health, and the authenticated v4 history sequence. The credential-bearing login body is redacted before writing, while its original byte length and SHA-256 commitment are retained so the exact received body remains independently verifiable without publishing a bearer token.

- Branch: `focus-model-a`; exact tested HEAD: `8ffb1c6fb3889f0643d6ac5e988645266995a080`; `working_tree_dirty=false` at server test start.
- Runtime capture timestamp (UTC): `2026-08-24T19:02:03.428267+00:00`.

<!-- RUNTIME_GENERATED_SUMMARY_START -->
- Generated from the latest real HTTP run at `2026-08-24T19:02:03.428267+00:00`.
- Required branch `focus-model-a`; captured branch `focus-model-a`.
- Exact tested HEAD `8ffb1c6fb3889f0643d6ac5e988645266995a080`; working tree at server start=`false`.
- Isolated runtime database: `data\model_a_runtime_20260824190159277305.db` (launcher PID `8388`).
- Isolation verification: runtime DB changed=`True`; main DB unchanged by SHA-256 content snapshot=`True`.
- Health: HTTP `200`, instance nonce verified, payload `{"status":"ok","service":"rice-duck-dss-backend","runtime_instance_id":"j8HLMe6U7vEGBh64UX2ptqK_U5SNH3ZRnfvZjNtSg08"}`, PASS=`True`.
- Historical A01-A36: `36/36` PASS.
- Synthetic S-A01-S-A19: `19/19` PASS.
- S-A14 actual: `yield_are_kg=65.00445497615651`, numerical difference `-4.349e-11`.
- Calendar PASS=`True`; v4 history PASS=`True` with HTTP sequence `201,200,200,200,200,200,404`.
- Discrepancy: `none`.
<!-- RUNTIME_GENERATED_SUMMARY_END -->
- Server: the validator launches and terminates its own backend subprocess on a free loopback port with a unique ignored `data/model_a_runtime_*.db`; evidence records its PID, URL, and before/after database metadata. Acceptance state is verified isolated from `data/rice_duck.db`.
- Real HTTP replay A01–A36: **36/36 PASS**. Each request omitted `literature_duration_days`; each response had `yield_status=OUTSIDE_LITERATURE_DOMAIN` and `yield_are_kg=null`.
- S-A14 real HTTP output: `yield_are_kg=65.00445497615651`, `cash_contribution_before_optional=4700267.298569391`; expected yield `65.0044549762` (difference below 5e-11).
- Synthetic S-A01–S-A19: **19/19 PASS**. Key actual results: S-A05 `density_status=WARNING_ABOVE_RECOMMENDED`, `survival_risk=null`; S-A06 `density_status=HIGH_RISK`, `survival_risk=HIGH`, duck all-sold revenue `null`; S-A13/S-A16/S-A17 abstained; S-A15 returned `yield_are_kg=69.7396`; S-A18 returned HTTP 400; S-A19 returned `density_are=0`, `UNDER`, and null numerical yield.
- Calendar contract: **PASS**. With `planting_date=2026-01-01`, actual release was `21–30` / `2026-01-22–2026-01-31`; withdraw was `56–60` / `2026-02-26–2026-03-02`.
- Authenticated v4 history: **PASS**. Real HTTP register/login/simulate/list/detail/delete sequence returned `schema_version=4`; detail was semantically equal to the original response (only JSON object key order differed in the stored provenance object); GET after delete returned HTTP 404.

### Actual HTTP results: historical replay A01-A36

Each request uses its documented source-compatible `p_gabah`, source `p_duck_buy` when present, source planting date when present, and scenario `p_duck_sell=45000`. `duck_age_days=21` remains imputed/estimated. No request sends `literature_duration_days`; no local `t_duck=45` or local 28-40 duration is converted into a Xiong input. Actual yield remains context only: no local yield MAE/RMSE is calculated.

| ID | HTTP | Source p_gabah | Backend price provenance | Source p_duck_buy | Backend cost_duck_buy | Source planting date | Actual backend date window | Density | Density status | Survival risk | Yield status | Yield are kg | Result |
|---|---:|---:|---|---:|---:|---|---|---:|---|---|---|---:|---|
| A01 | 200 | 6000.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 10000.0 | 300000.0 | missing | missing | 4.545454545454546 | WARNING_ABOVE_RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A02 | 200 | 6000.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 25000.0 | 700000.0 | missing | missing | 2.6666666666666665 | RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A03 | 200 | 6000.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 30000.0 | 300000.0 | missing | missing | 2.0833333333333335 | RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A04 | 200 | 6000.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 25000.0 | 400000.0 | missing | missing | 3.5555555555555554 | RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A05 | 200 | 6000.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 25000.0 | 325000.0 | missing | missing | 3.611111111111111 | RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A06 | 200 | 6000.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 25000.0 | 125000.0 | missing | missing | 0.9803921568627451 | UNDER | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A07 | 200 | 6000.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 32000.0 | 320000.0 | missing | missing | 3.125 | RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A08 | 200 | 6000.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 7539.0 | 490035.0 | missing | missing | 6.5 | WARNING_ABOVE_RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A09 | 200 | 6000.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 8550.0 | 342000.0 | missing | missing | 7.2727272727272725 | WARNING_ABOVE_RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A10 | 200 | 7500.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 22222.22222 | 199999.99998 | missing | missing | 1.2396694214876034 | UNDER | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A11 | 200 | 7500.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 6666.666667 | 200000.00001 | missing | missing | 4.545454545454546 | WARNING_ABOVE_RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A12 | 200 | 7500.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 7000.0 | 196000.0 | missing | missing | 2.6666666666666665 | RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A13 | 200 | 7500.0 | p_gabah=runtime; p_duck_buy=local-estimate fallback Rp25000/ekor; p_duck_sell=runtime | missing | 200000.0 | missing | missing | 1.6666666666666667 | UNDER | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A14 | 200 | 7500.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 15000.0 | 150000.0 | missing | missing | 2.2222222222222223 | RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A15 | 200 | 7500.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 5000.0 | 50000.0 | missing | missing | 1.9607843137254901 | UNDER | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A16 | 200 | 7500.0 | p_gabah=runtime; p_duck_buy=local-estimate fallback Rp25000/ekor; p_duck_sell=runtime | missing | 75000.0 | missing | missing | 0.9375 | UNDER | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A17 | 200 | 7500.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 10000.0 | 300000.0 | missing | missing | 2.081887578070784 | RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A18 | 200 | 7500.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 7000.0 | 350000.0 | missing | missing | 9.090909090909092 | HIGH_RISK | HIGH | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A19 | 200 | 6000.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 15000.0 | 300000.0 | 2024-02-19 | 2024-03-11..2024-04-19 | 3.1496062992125986 | RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A20 | 200 | 6300.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 12000.0 | 384000.0 | 2024-04-15 | 2024-05-06..2024-06-14 | 3.1341821743388834 | RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A21 | 200 | 6300.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 12000.0 | 228000.0 | 2024-04-12 | 2024-05-03..2024-06-11 | 2.878787878787879 | RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A22 | 200 | 6300.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 0.0 | 0.0 | 2024-04-23 | 2024-05-14..2024-06-22 | 1.875 | UNDER | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A23 | 200 | 6300.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 0.0 | 0.0 | 2024-04-22 | 2024-05-13..2024-06-21 | 3.2 | RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A24 | 200 | 6300.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 12000.0 | 216000.0 | 2024-04-15 | 2024-05-06..2024-06-14 | 3.272727272727273 | RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A25 | 200 | 6200.0 | p_gabah=runtime; p_duck_buy=local-estimate fallback Rp25000/ekor; p_duck_sell=runtime | missing | 125000.0 | 2024-07-17 | 2024-08-07..2024-09-15 | 0.7874015748031497 | UNDER | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A26 | 200 | 6000.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 0.0 | 0.0 | 2024-10-01 | 2024-10-22..2024-11-30 | 4.166666666666667 | WARNING_ABOVE_RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A27 | 200 | 6000.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 0.0 | 0.0 | 2024-09-28 | 2024-10-19..2024-11-27 | 2.9 | RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A28 | 200 | 6000.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 25000.0 | 225000.0 | missing | missing | 2.0 | RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A29 | 200 | 6000.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 25000.0 | 150000.0 | missing | missing | 2.0 | RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A30 | 200 | 6000.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 25000.0 | 175000.0 | missing | missing | 1.971830985915493 | UNDER | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A31 | 200 | 6000.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 25000.0 | 250000.0 | 2025-04-09 | 2025-04-30..2025-06-08 | 2.079002079002079 | RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A32 | 200 | 6000.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 25000.0 | 250000.0 | 2025-04-09 | 2025-04-30..2025-06-08 | 2.0833333333333335 | RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A33 | 200 | 6000.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 25000.0 | 175000.0 | 2025-04-19 | 2025-05-10..2025-06-18 | 2.028985507246377 | RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A34 | 200 | 6000.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 25000.0 | 225000.0 | missing | missing | 2.027027027027027 | RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A35 | 200 | 6000.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 25000.0 | 225000.0 | missing | missing | 2.0316027088036117 | RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
| A36 | 200 | 6000.0 | p_gabah=runtime; p_duck_buy=runtime; p_duck_sell=runtime | 25000.0 | 200000.0 | missing | missing | 2.1220159151193636 | RECOMMENDED | null | OUTSIDE_LITERATURE_DOMAIN | null | PASS |
### Actual HTTP results: synthetic S-A01–S-A19

| ID | HTTP | Actual principal output | Result |
|---|---:|---|---|
| S-A01 | 200 | `d=1.9`, `UNDER` | PASS |
| S-A02 | 200 | `d=2`, `RECOMMENDED` | PASS |
| S-A03 | 200 | `d=4`, `RECOMMENDED` | PASS |
| S-A04 | 200 | `d=4.1`, `WARNING_ABOVE_RECOMMENDED` | PASS |
| S-A05 | 200 | `d=8`, `WARNING_ABOVE_RECOMMENDED`, `survival_risk=null` | PASS |
| S-A06 | 200 | `d=8.1`, `HIGH_RISK`, `survival_risk=HIGH`, duck revenue `null` | PASS |
| S-A07 | 200 | Tegel `d=3`, `RECOMMENDED` | PASS |
| S-A08 | 200 | Tegel `d=3.1`, `WARNING_ABOVE_RECOMMENDED` | PASS |
| S-A09 | 200 | `age_status=NOT_RECOMMENDED` | PASS |
| S-A10 | 200 | `age_status=LOCAL_READY` | PASS |
| S-A11 | 200 | `age_status=LOCAL_READY` | PASS |
| S-A12 | 200 | `age_status=OLDER_CONSERVATIVE` | PASS |
| S-A13 | 200 | `yield_status=OUTSIDE_LITERATURE_DOMAIN`, numerical yield `null` | PASS |
| S-A14 | 200 | `yield_are_kg=65.00445497615651`, `yield_total_kg=650.0445497615651` | PASS |
| S-A15 | 200 | `yield_are_kg=69.7396`, `yield_total_kg=697.396` | PASS |
| S-A16 | 200 | `yield_status=OUTSIDE_LITERATURE_DOMAIN`, numerical yield `null` | PASS |
| S-A17 | 200 | `density_ha=610`, `yield_status=OUTSIDE_LITERATURE_DOMAIN` | PASS |
| S-A18 | 400 | validation error for `land_area_are=0` | PASS |
| S-A19 | 200 | `duck_count=0`, `density_are=0`, `UNDER`, numerical yield `null` | PASS |

Branch A dianggap sesuai SoT hanya jika:

- historical local replay **tidak** memaksakan numerical Xiong yield;
- Xiong hanya menghasilkan angka pada domain `0<d_ha<=600` dan `50<=t<=80`;
- tidak ada `N_survive`/survival percentage;
- `d>8` hanya menjadi risk gate dan menonaktifkan duck all-sold revenue;
- tidak ada fixed feed Core, old yield `47.8767507`, old p_sell `52500`, atau fixed calendar `21/65/44`;
- optional/missing data tetap `null`/explicitly unavailable, bukan synthetic zero.
