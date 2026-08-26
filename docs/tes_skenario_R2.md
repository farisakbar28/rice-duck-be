# Panduan Pengujian Skenario R2 — Runtime Evidence

> **Status:** TEMPLATE.  
> Jangan isi output backend sebelum implementasi R2 benar-benar dijalankan.  
> Jangan menyalin output/metric dari `docs/tes_skenario.md` lama.

## 1. Tujuan

Dokumen ini menyimpan evidence runtime setelah backend R2 diimplementasikan. Ia bukan source of truth formula dan bukan tempat melakukan kalibrasi.

Tiga kelompok test:

1. synthetic contract/boundary tests;
2. historical replay dengan provenance;
3. stress tests pada 8 excluded cycles.

## 2. Evidence Header Wajib

Isi setiap execution batch:

```text
model_version: R2
parameter_registry_version: R2-2026-08-26.3
backend_commit_sha:
python_version:
app_version:
database_schema_version: 4
start_command:
execution_timestamp_utc:
```

## 3. Synthetic Contract Cases

Synthetic cases tidak boleh disebut observasi lapangan.

### B01 — Supported Jarwo + default purchase price

```json
{
  "land_area_are": 10,
  "duck_count": 30,
  "planting_date": "2026-01-01",
  "planting_system": "jajar_legowo",
  "rice_variety": "sertani",
  "duck_age_days": 30
}
```

Expected contract invariants:

```text
HTTP 200
p_duck_buy_effective = 26500
age_support = SUPPORTED
density_are = 3
density_support = SUPPORTED
survival_availability = AVAILABLE
lambda_eff = 0.90
N_survive = floor(27) = 27
release HST = 21..30
pull HST = 56..60
harvest HST = 100..110
yield_availability = AVAILABLE with ref/low/high literature evidence envelope
baseline/F_RD source IDs present; full profit remains null
feed availability = UNAVAILABLE
cost_completeness = INCOMPLETE
profit_full_est = null
```

### B02 — Supported Tegel

`A=10`, `J=30`, `S=tegel`, age=30.

Expected:

```text
density=3
DensitySupportFlag=SUPPORTED
survival numeric available
```

### B03 — Jarwo upper supported boundary

`A=10`, `J=40` -> density 4.

Expected `SUPPORTED`.

### B04 — Tegel above supported but below limited-test band

`A=10`, `J=40` -> density 4.

Expected `EXTRAPOLATION`, not a penalty coefficient.

### B05 — Limited test

`A=10`, `J=55` -> density 5.5.

Expected:

```text
density_support = LIMITED_TEST
survival_availability = UNAVAILABLE
N_survive = null
```

### B06 — High risk

`A=10`, `J=80` -> density 8.

Expected:

```text
density_support = HIGH_RISK
survival_availability = UNAVAILABLE
N_survive = null
```

No 60% survival fallback.

### B07–B09 — Age boundaries

| Case | Age | Expected |
|---|---:|---|
| B07 | 20 | `CAUTION`; survival unavailable |
| B08 | 21 | `SUPPORTED` |
| B09 | 30 | `SUPPORTED` |
| B10 | 31 | `OUTSIDE_LOCAL_RANGE`; survival unavailable |

### B11 — Inpari calendar

Expected harvest HST:

```text
90..100
```

Any `109..116` or `134` is a regression failure.

### B12 — Manual purchase price

Supply `p_duck_buy=30000`.

Expected:

```text
p_duck_buy_effective=30000
C_duck_buy=J*30000
source=USER_INPUT
```

### B13 — Null purchase price

Supply `p_duck_buy=null`.

Expected default Rp26,500.

### B14 — Invalid zero purchase price

Supply `p_duck_buy=0`.

Expected validation failure; zero is not R2 missing-value semantics.

### B15 — Unsupported-age yield gate

Expected:

```text
age=20; yield_availability=UNAVAILABLE
yield_kg_per_are=null
yield_total_kg=null
paddy_revenue=null
margin_core=null
```

No fallback constant.

### B16 — Fertilizer baseline

For a chosen area, independently verify:

```text
N_need=1.1761*A
P2O5_need=0.2745*A
K2O_need=0.2745*A
Q_npk=max(P2O5/0.10,K2O/0.12)
Q_urea=max(0,(N-0.15*Q_npk)/0.46)
C=1800*Q_urea+1840*Q_npk
```

Verify manure credit is false/not applied and KCl absent.

### B17 — Net infrastructure range

Verify:

```text
L=4*sqrt(100*A)
min=L*6000/3
ref=L*6750/2.5
max=L*6750/2
min <= ref <= max
```

### B18 — Terminal value not revenue

For a supported case with `N_survive` available:

```text
V_duck_end_ref=N_survive*45000
terminal_value_is_cash_revenue=false
CashRevenue must not add V_duck_end
```

## 4. Runtime Evidence Template per Case

```text
case_id:
case_type: SYNTHETIC | HISTORICAL | STRESS
source_row_if_any:
input_provenance:
request_json:
http_status:
raw_response_json:

expected_invariants:
observed_invariants:
pass_fail:
discrepancy:
notes:
```

## 5. Historical Replay Rules

Historical replay is rebuilt from the raw/clean source after R2 implementation.

Do not reuse the old 11-row fixture without provenance review because:

- `duck_age_days=21` was a qualitative legacy estimate, not observation;
- some `p_duck_buy=0` values are not safe to interpret as true zero purchase cost;
- old fixture eligibility depended on the wrong mandatory-price contract;
- old test asserted fixed yield 47.8767507.

### 5.1 Required field-level provenance

For every historical request field:

```text
field
value
provenance: OBSERVED | LOCAL_DEFAULT | VALIDATION_ASSUMPTION | UNAVAILABLE
source_file
source_row
note
```

### 5.2 Historical actual/comparator provenance

```text
field
value
provenance: OBSERVED_VALUE | EXPLICIT_ZERO | MISSING_UNKNOWN | DERIVED_ACTUAL | LEGACY_IMPUTATION
```

Only semantically compatible actual values receive residual/error metrics.

## 6. Yield Comparator

Do not run/publish R2 yield metrics while yield availability is unavailable.

After approved yield lookup is implemented and frozen:

- all clean cohort `N=36`;
- strict supported-domain cohort `N=17`;
- metrics MAE/RMSE/MedAE/MBE/WAPE;
- release scenario-envelope coverage;
- cluster-bootstrap interval by farmer if uncertainty is reported.

Do not recalculate R2 parameters from these residuals.

## 7. Calendar Comparator

Harvest-date validation only on the 12 cycles with both planting and harvest dates observed.

For transplanted rice, the observed planting date is treated as the field
transplanting date and HST is counted from transplanting. This is recorded as
`VALIDATION_ASSUMPTION`; unresolved equivalence excludes the row with
`TIMING_SEMANTICS_UNRESOLVED`.

Report:

```text
window coverage
mean/median distance-to-window error
N=12
```

No accuracy metric for release/pull/active duration because actual values are absent.

## 8. Economic Comparator

- duck purchase cost: identity/contract test plus observed-price plausibility;
- feed: no metric until R2 feed is available;
- net/cage: secondary eligible-record comparison only;
- weeding/pest/fertilizer sparse/absent values: descriptive/case-level only;
- old raw farmer profit is not a target for `Margin_core` or `Profit_full_est`.

## 9. Stress Set

Run the 8 excluded cycles separately when input data permit.

Purpose:

- ensure no crashes/NaN/overflow;
- check `EXTRAPOLATION/HIGH_RISK` semantics;
- document confounders that seven user inputs cannot represent;
- never merge stress rows into headline accuracy metrics.

## 10. Result Publication Rule

A scenario result may be entered into this document only when:

1. backend R2 commit is recorded;
2. request was actually sent through runtime path;
3. raw JSON response is preserved;
4. no manual formula result was substituted for backend output;
5. provenance of historical fields is recorded.

## 11. Generated Runtime Evidence — Phase-5 Harness

B01–B18 synthetic runtime evidence is now produced mechanically by the
research-only validation harness (`python -m validation`, see
`docs/11_R2_FREEZE_MANIFEST.md`), which satisfies all five conditions above by
construction: it records the backend commit, sends every request through the
canonical FastAPI HTTP path, stores each raw response JSON verbatim, computes
invariant pass/fail from observed responses, and captures provenance policies.

## 12. Current Phase-6 Test Addendum (freeze `.4`)

Required deterministic cases: Inpari and Sertani supported-domain reference
and low/high yields; exact arithmetic (`54.998/20.56/80.5952` for Inpari and
`45.746/22.9244/68.5676` for Sertani per are); area scaling; Jarwo boundaries
2 and 4; Tegel boundaries 2 and 3; age 20/21/30/31; unknown group; missing F_RD;
no interpolation or extrapolation; source metadata; Sertani low-evidence
metadata; reference-alias backward compatibility; reference/low/high economics;
full-profit unavailability; v4 persistence round-trip; registry/freeze `.3`;
serialization precision; and stress null propagation.

Outside the joint supported domain, every yield reference/envelope field and
its aliases must be null. The Phase-6 range is named
`LITERATURE_EVIDENCE_ENVELOPE`, not a confidence or prediction interval. These
synthetic checks are not comparator access; historical yield replay begins only
under docs/06 section 22 after the committed freeze.

Artifacts live under `validation/results/<run_id>/` (notably
`synthetic_cases.json`). Any run executed on a dirty tree, or before the
official clean-tree frozen-execution run, is watermarked
`NON_OFFICIAL_PRE_FREEZE` in every artifact header and MUST NOT be cited as an
official frozen validation result. Synthetic cases remain contract evidence;
they are never field observations.
