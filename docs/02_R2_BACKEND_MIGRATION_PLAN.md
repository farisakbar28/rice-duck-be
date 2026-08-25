# R2 Backend Migration Plan — `78f46e` Baseline to R2

> **Baseline commit:** `78f46ebd8004b8ebfdd7559a1c0648482d3eeeaa`  
> **Audited master:** `2a4824d97933e662cfe9b7a70e1d442f7fb43ac4`  
> **Master relation:** 3 commits ahead of baseline, 0 behind.  
> **Rule:** baseline is a code-architecture recovery point, not a mathematical recovery point.

## 1. What Happened After the Baseline

Three commits after `78f46e...` materially rewrote the DSS:

1. `ff9b347adfffb885fc94964457a6e39c7ed1c73c` — `Migrate DSS core to final source of truth`
2. `2d23130b1cf57685f6f161c9e7e565112f369c65` — `docs: correct replay metrics and provenance`
3. `2a4824d97933e662cfe9b7a70e1d442f7fb43ac4` — `fix: align Inpari harvest calendar with local reference window`

The result is not a small constant drift. It changes:

- API input semantics;
- calendar;
- survival;
- yield;
- cost/revenue ledger;
- sandbox calculations;
- persistence columns/schema version;
- visualization payload;
- tests/golden values;
- historical replay protocol;
- Postman and README.

Therefore the R2 migration must not be implemented as `git checkout 78f... && change a few numbers`.

## 2. Baseline vs Current Master vs R2

| Concern | `78f46e` | Current master | R2 target |
|---|---|---|---|
| Duck purchase price | optional, default 25,000 | mandatory; `0` means no purchase | optional; missing/null -> 26,500; supplied value >0 |
| Age | numeric `R_age` 0.35/0.15/0.05 | readiness flag only | support flag only |
| Density | `P_over/P_under` penalties | support status + >8 branch | support/extrapolation flags only |
| Calendar | 21 -> 65, 44d; 114/134 harvest | 21 -> 65, 44d; 100–110 / 109–116 | release 21–30; pull 56–60; t ref 32 [28–40]; harvest 100–110 / 90–100 |
| Survival | 0.78125 with age/density penalties | 100% if d<=8; 60% if d>8 | 0.90 only in supported age+density domain; otherwise unavailable |
| Sale state | survivor used for duck revenue | survivor used for potential duck sale | survivor and sold state separated; no sale assumption |
| Yield | Y0 47.8767507 × invented factors | fixed 47.8767507 | PENDING `Y_base(V_exact)*F_RD_lookup`; unavailable until source lookup |
| Paddy price | 6,000 | 6,000 | 6,500 regulatory HPP benchmark |
| Duck end price | 35,000 revenue | 52,500 potential revenue | 45,000 terminal value ref; 30–60k sensitivity; not cash sale |
| Feed | 4,500 × invented modifiers, isolated | 20,000/duck core | unavailable until q_feed + p_feed lookup |
| Weed/pest | numeric curves | numeric sandbox shortcuts | descriptive/baseline only; monetary savings unavailable |
| Fertilizer | manure temporal formula + KCl | same mechanism in sandbox | no manure credit; N-P2O5-K2O baseline; Urea+NPK active; KCl excluded |
| Net infra | recap regression | context only | square-equivalent perimeter × local price/lifetime |
| Cage | flat 175k total | context only | per-unit 150–200k; total unavailable without capacity rule |
| Economic output | `Profit_net_cash` | `Net_Cash_Contribution_DSS` | `Margin_core` conditional; `Profit_full_est` only if complete |
| History | schema v2 | schema v3 | **schema v4** |
| Visualization | invented scientific curves | zone curves + wrong financial waterfall | only truthful availability/support/benchmark series; no fake yield/survival curves |

## 3. Current-Master File Audit

Every artifact present on current `master` is classified below. `REWRITE` means its R2-relevant semantics must change. `KEEP` means no model-semantic rewrite is required, though naming/docs may still be updated. `ARCHIVE/INVALIDATE` means keep only as historical evidence, not active implementation guidance.

### 3.1 Root / configuration

| Path | Disposition | Audit result |
|---|---|---|
| `.env.example` | KEEP + HARDEN | Correctly externalizes env values. Keep, but require real JWT secret outside source. |
| `.gitattributes` | KEEP | LF normalization and binary declarations are appropriate. |
| `.gitignore` | KEEP | Correctly ignores env/cache/db/test DB. |
| `CHANGELOG.md` | REWRITE | Current Unreleased and v2 historical records describe invalid mathematical semantics. Preserve history but add R2 migration and explicit invalidation. |
| `README.md` | REWRITE | Currently points to wrong SoT and documents mandatory p_duck_buy, fixed yield, wrong survival/economics/calendar. |
| `requirements.txt` | KEEP / REVIEW | Stack is sufficient for R2; no model change required. |
| `BACKEND_GRAPH_PLAN.md` (baseline-only) | ARCHIVE/REFERENCE | Useful proof of visualization architecture, but graph formulas are invalid. Do not restore as active design. |

### 3.2 Package markers

The following `__init__.py` artifacts are module markers and contain no R2 mathematics; retain unchanged unless packaging changes:

- `app/__init__.py`
- `app/api/__init__.py`
- `app/api/routes/__init__.py`
- `app/core/__init__.py`
- `app/data/__init__.py`
- `app/domain/__init__.py`
- `app/engines/__init__.py`
- `app/repositories/__init__.py`
- `app/schemas/__init__.py`
- `app/services/__init__.py`
- `tests/__init__.py`

### 3.3 API layer

| Path | Disposition | Required R2 action |
|---|---|---|
| `app/api/dependencies.py` | KEEP | Auth dependency pattern remains valid. |
| `app/api/router.py` | KEEP / SCOPE CHECK | Routing pattern valid. Optimizer stays isolated/stub. |
| `app/api/routes/auth.py` | KEEP | No R2 mathematical semantics. |
| `app/api/routes/health.py` | KEEP | No change except app version if desired. |
| `app/api/routes/dss.py` | REWRITE | Update descriptions, request optional-price semantics, response contract, availability fields, visualization semantics. |
| `app/api/routes/optimizer.py` | KEEP STUB / ISOLATE | Do not reintroduce legacy optimizer formulas during R2 migration. It must not contaminate DSS core. |

### 3.4 Core infrastructure

| Path | Disposition | Required R2 action |
|---|---|---|
| `app/core/config.py` | HARDEN | **Remove hardcoded production-default JWT secret.** Require environment value outside tests/development. Model-independent but production-critical. |
| `app/core/database.py` | REWRITE MIGRATION | Add schema v4 fields; never reinterpret v1–v3 rows. Do not alter v3 semantics in-place. |
| `app/core/exceptions.py` | KEEP | Error hierarchy is useful. Add availability errors only if endpoint design requires them; otherwise availability is response state, not HTTP failure. |
| `app/core/security.py` | KEEP + HARDEN | PBKDF2/HMAC mechanics can remain. Config secret must not use checked-in fallback. |

### 3.5 Data/domain

| Path | Disposition | Required R2 action |
|---|---|---|
| `app/data/seed.py` | FULL REWRITE | Remove current Y_base, 109–116 Inpari, 21/65 calendar aliases, sale 52.5k, feed 20k, KCl 9.5k, 6k gabah, invalid metadata tags. Seed only R2-valid registry values. |
| `app/domain/models.py` | FULL REWRITE R2 TYPES | Remove/deprecate fields that imply wrong runtime semantics. Add R2 parameter metadata, availability/status enums or typed strings, history v4 model. |

### 3.6 Engines

| Path | Disposition | Required R2 action |
|---|---|---|
| `app/engines/formula_engine.py` | FULL REWRITE | Implement active R2 deterministic formulas only. No legacy scientific fallback. |
| `app/engines/impact_engine.py` | FULL REWRITE / SPLIT | Remove executable weed/pest/manure/feed legacy formulas. Implement fertilizer baseline, net equivalent cost, and explicit unavailable outputs. Consider rename to `cost_engine.py`/`material_engine.py`. |

### 3.7 Repositories

| Path | Disposition | Required R2 action |
|---|---|---|
| `app/repositories/lookup_repository.py` | REWRITE DATA SOURCE | Repository pattern valid; returned seed/lookup semantics must be R2. |
| `app/repositories/history_repository.py` | REWRITE v4 | Add v4 write/read. v1/v2/v3 remain immutable legacy read-only or hidden. |
| `app/repositories/user_repository.py` | KEEP | No model-semantic change. |

### 3.8 Schemas

| Path | Disposition | Required R2 action |
|---|---|---|
| `app/schemas/auth.py` | KEEP | No model change. |
| `app/schemas/common.py` | KEEP | Error/health envelopes valid. |
| `app/schemas/dss.py` | FULL REWRITE | Request: p_duck_buy optional. Response: nested R2 semantic groups + availability flags + nulls. Remove wrong canonical fields. |
| `app/schemas/optimizer.py` | KEEP STUB / MARK LEGACY | Do not treat optimizer types as DSS R2 types. Its current documentation still references old filenames and legacy concepts; clean comments if touched. |

### 3.9 Services

| Path | Disposition | Required R2 action |
|---|---|---|
| `app/services/auth_service.py` | KEEP | No R2 model change. |
| `app/services/simulation_service.py` | FULL REWRITE ORCHESTRATION | Orchestrate R2 gates; no fixed yield, no 60% overload survival, no auto duck revenue, no fixed feed. |
| `app/services/visualization_service.py` | FULL REWRITE | Never generate a scientific curve from unresolved formulas. Show zones, windows, availability, cost ranges, and waterfall only for available components. |

### 3.10 Application bootstrap

| Path | Disposition | Required R2 action |
|---|---|---|
| `app/main.py` | REWRITE DOC STRINGS | App wiring remains; remove wrong SoT and `Net_Cash_Contribution_DSS` descriptions. Optimizer description must not advertise reuse of legacy formulas as scientifically approved. |

### 3.11 Active docs on master

| Path | Disposition | Reason |
|---|---|---|
| `docs/Model Matematika Data Collection DSS Padi Bebek FINAL.md` | INVALIDATE / REPLACE | It explicitly allows recap-derived parameter calculations and contains wrong R2 runtime. Replace active role with `01_R2_MODEL_SSOT.md`. |
| `docs/NUMERICAL_VALIDATION_DSS_PADI_BEBEK_FINAL_CLEAN.md` | INVALIDATE AS R2 VALIDATION | It calibrates/LOFO-fits yield median from the clean recap. This violates the confirmed comparator-only rule. Preserve only as legacy research history. |
| `docs/tes_skenario.md` | INVALIDATE / REPLACE | Built around old mandatory input and fixed-yield semantics. Replace with `tes_skenario_R2.md`. |

### 3.12 Postman

| Path | Disposition | Required R2 action |
|---|---|---|
| `postman/Rice_Duck_DSS.postman_collection.json` | FULL REWRITE CONTRACT TESTS | Current tests assert Cost_feed=400k, NetCash, Inpari 109–116, required price. All invalid. |
| `postman/Rice_Duck_DSS.postman_environment.json` | KEEP + SANITIZE | Local environment concept valid. Example password should remain non-production. |

### 3.13 Tests

| Path | Disposition | R2 action |
|---|---|---|
| `tests/conftest.py` | KEEP + v4 DB support | Test isolation is valid. |
| `tests/fixtures/historical_replay.json` | REPLACE/EXPAND PROVENANCE | Current 11 fixtures contain imputed age and `0` purchase prices under old semantics; do not use directly as R2 ground truth. |
| `tests/test_api.py` | FULL REWRITE | Current assertions hard-lock wrong master outputs. |
| `tests/test_formula_engine.py` | FULL REWRITE | Current tests explicitly assert 21/65/44, 100%/60% survival, fixed 47.8767507 yield. |
| `tests/test_historical_replay.py` | FULL REWRITE | Current tests compute MAE against fixed recap-derived yield. Invalid for R2. |
| `tests/test_history.py` | REWRITE v4 | Test v4 round-trip and legacy read isolation. |
| `tests/test_scientific_visualizations.py` | FULL REWRITE | Current test asserts 0.60 survival curve and fixed yield benchmark. |
| `tests/test_sot_golden_case.py` | DELETE/REPLACE | Current numeric golden output is a trap: R2 intentionally has unavailable yield/feed/full profit. Golden case should test semantics/invariants, not fabricate full numeric total. |

## 4. Baseline-Only Binary Research Artifacts

The baseline commit contained research files that current master removed:

- `docs/Dataset_Bersih_Rekap_Include_Hasil_Simulasi_Baru.xlsx`
- `docs/Kumpulan_Variabel_Rumus_Data_Artikel_Referensi_Scopus_FINAL.xlsx`
- `docs/Literatur Review Lengkap.xlsx`
- `docs/Recap Data CRS Bebek.xlsx`
- `docs/data_collection_padi_bebek_FINAL.xlsx`

These were cross-checked against the research artifact set used to construct R2. Their role is **not** equal:

- `data_collection_padi_bebek_FINAL.xlsx` → local evidence source.
- reference workbook(s) → literature fallback/audit source.
- recap and simulation workbook(s) → comparator/test only.

Do not re-add all binaries to production repo solely because they existed at `78f46e...`. If retained, place them under an explicit research/archive directory or external research storage and document their role.

## 5. Migration Strategy

### Phase M0 — Branch/working state

1. Preserve current `master` history.
2. Create a dedicated R2 implementation branch from the chosen code baseline.
3. If physically resetting code to `78f46e...`, immediately apply this documentation package before writing scientific code.
4. Never treat passing tests from either `78f46e...` or current master as proof of R2 correctness.

### Phase M1 — Documentation first

- Add this package.
- Mark old model/validation/scenario docs legacy.
- Update README precedence.

### Phase M2 — Domain and schema types

- Implement R2 request/response schemas first.
- Introduce explicit `AvailabilityStatus`, support flags, parameter status tags.
- Introduce `schema_version=4` persistence model.

### Phase M3 — Pure engines

Implement and test in this order:

1. input normalization/default price;
2. age support;
3. density support;
4. calendar windows;
5. survival availability gate;
6. fertilizer baseline;
7. infrastructure net range;
8. unresolved/unavailable component representations;
9. yield lookup interface with **no fallback**;
10. economic ledger conditionality.

### Phase M4 — Service orchestration

- Compose engines.
- No silent defaults beyond approved default purchase price.
- Propagate `null` + availability state.
- Generate warnings/trace metadata.

### Phase M5 — Persistence

- Write new simulations as v4 only.
- Never save R2 values into v3 columns under v3 semantics.
- Legacy rows are read-only and must expose their model version.

### Phase M6 — API/visualization

- Update options/simulate/visualize.
- Visualization must only graph valid quantities.
- A chart may visualize support zones or ranges without inventing continuous biological effects.

### Phase M7 — Tests

- Replace old golden values.
- Add anti-regression tests asserting banned identifiers/values do not control runtime.
- Add availability tests for missing yield/feed lookups.
- Add v4 history tests.

### Phase M8 — Historical validation

Only after the model is frozen and implementation parity tests pass:

- build R2 validation fixtures with provenance flags;
- regenerate predictions fresh;
- follow `06_R2_TEST_VALIDATION_PROTOCOL.md`;
- do not tune model from errors.

## 6. Security/Engineering Hardening Gate

Not a mathematical requirement, but current repo contains a default JWT secret in `app/core/config.py`. Before production deployment:

- remove meaningful secret default;
- fail startup in production if `JWT_SECRET_KEY` is missing/placeholder;
- keep test override in `tests/conftest.py`;
- restrict CORS in production;
- version `APP_VERSION` with R2 migration.

## 7. Do Not Do These During Migration

- Do not resurrect a formula because frontend currently expects its chart.
- Do not use `None -> legacy value` fallbacks.
- Do not turn `UNAVAILABLE` into zero.
- Do not let database `NOT NULL DEFAULT 0` silently convert unknown scientific outputs into measured zero.
- Do not recalculate R2 coefficients from historical replay error.
- Do not equate terminal duck value with realized sale revenue.
- Do not reactivate optimizer legacy formulas as part of DSS core migration.

