# R2 Repository Audit Manifest

> This manifest records the repository artifacts reviewed for the R2 migration.  
> Baseline: `78f46ebd8004b8ebfdd7559a1c0648482d3eeeaa`.  
> Current audited master: `2a4824d97933e662cfe9b7a70e1d442f7fb43ac4`.

## 1. Current Master Artifact Inventory

### Root

- `.env.example` — environment contract; retain/harden.
- `.gitattributes` — line ending/binary policy; retain.
- `.gitignore` — ignored runtime artifacts; retain.
- `CHANGELOG.md` — historical model evolution; update with R2 invalidation.
- `README.md` — currently wrong active-model documentation; rewrite.
- `requirements.txt` — FastAPI/Pydantic/Pytest/httpx stack; retain/review versions independently.

### `app/`

- `app/__init__.py` — package marker.
- `app/main.py` — FastAPI bootstrap, handlers, CORS, OpenAPI; descriptions currently wrong R2 semantics.

### `app/api/`

- `app/api/__init__.py` — package marker.
- `app/api/dependencies.py` — required/optional bearer auth resolution.
- `app/api/router.py` — auth + DSS + optimizer routing.
- `app/api/routes/__init__.py` — package marker.
- `app/api/routes/auth.py` — register/login/me.
- `app/api/routes/dss.py` — options/simulate/history/visualize; rewrite R2 contract.
- `app/api/routes/health.py` — service health.
- `app/api/routes/optimizer.py` — stand-alone optimizer stub; isolate from R2 core.

### `app/core/`

- `app/core/__init__.py` — package marker.
- `app/core/config.py` — settings; contains a meaningful default JWT secret that must be hardened.
- `app/core/database.py` — SQLite init + legacy/v3 columns; add semantically isolated v4 storage.
- `app/core/exceptions.py` — typed application errors.
- `app/core/security.py` — PBKDF2 password hashing + HS256-like JWT implementation.

### `app/data/`

- `app/data/__init__.py` — package marker.
- `app/data/seed.py` — current model parameters/metadata; full R2 rewrite required.

### `app/domain/`

- `app/domain/__init__.py` — package marker.
- `app/domain/models.py` — dataclasses for lookups/users/history; current R2-incompatible history and constants.

### `app/engines/`

- `app/engines/__init__.py` — package marker.
- `app/engines/formula_engine.py` — current age/density/calendar/survival/yield/core economics; scientific rewrite required.
- `app/engines/impact_engine.py` — current weeding/pesticide/fertilizer/infrastructure sandbox; contains still-executable invalid formulas.

### `app/repositories/`

- `app/repositories/__init__.py` — package marker.
- `app/repositories/history_repository.py` — v3 explicit persistence + legacy read; v4 rewrite required.
- `app/repositories/lookup_repository.py` — seed-backed lookup access; retain pattern, replace data.
- `app/repositories/user_repository.py` — SQLite user CRUD; model-independent.

### `app/schemas/`

- `app/schemas/__init__.py` — package marker.
- `app/schemas/auth.py` — auth DTOs/validators.
- `app/schemas/common.py` — health/error envelopes.
- `app/schemas/dss.py` — current wrong DSS request/response/history/visualization DTOs; full rewrite.
- `app/schemas/optimizer.py` — extensive legacy optimizer DTO surface; outside R2 DSS scope.

### `app/services/`

- `app/services/__init__.py` — package marker.
- `app/services/auth_service.py` — auth orchestration.
- `app/services/simulation_service.py` — current wrong DSS orchestration/persistence; full rewrite.
- `app/services/visualization_service.py` — current density/age/waterfall generator; full rewrite.

### `docs/`

- `docs/Model Matematika Data Collection DSS Padi Bebek FINAL.md` — current active SoT but incompatible with confirmed R2; invalidate/replace.
- `docs/NUMERICAL_VALIDATION_DSS_PADI_BEBEK_FINAL_CLEAN.md` — legacy numerical validation that uses recap-derived yield calibration/LOFO; not valid R2 validation.
- `docs/tes_skenario.md` — old runtime replay guide; replace with R2 scenario document.

### `postman/`

- `postman/Rice_Duck_DSS.postman_collection.json` — current assertions lock wrong R2 semantics.
- `postman/Rice_Duck_DSS.postman_environment.json` — local environment template; retain/sanitize.

### `tests/`

- `tests/__init__.py` — package marker.
- `tests/conftest.py` — test DB/env isolation; retain and adapt schema v4.
- `tests/fixtures/historical_replay.json` — 11-row legacy fixture; provenance/semantics must be rebuilt.
- `tests/test_api.py` — locks fixed yield/current economics/calendar; rewrite.
- `tests/test_formula_engine.py` — locks current wrong formulas; rewrite.
- `tests/test_historical_replay.py` — locks historical MAE against fixed Y baseline; invalid R2 validation test.
- `tests/test_history.py` — v3 history round-trip; rewrite v4.
- `tests/test_scientific_visualizations.py` — locks 60% survival and fixed yield visualization; rewrite.
- `tests/test_sot_golden_case.py` — numeric golden response for wrong model; replace with semantic/invariant golden contract.

## 2. Baseline-Only / Removed Artifacts Reviewed

- `BACKEND_GRAPH_PLAN.md` — added visualization architecture around invalid old scientific curves; architectural reference only.
- `docs/Dataset_Bersih_Rekap_Include_Hasil_Simulasi_Baru.xlsx` — old simulation/comparator artifact; comparator/audit only.
- `docs/Kumpulan_Variabel_Rumus_Data_Artikel_Referensi_Scopus_FINAL.xlsx` — curated reference fallback; not calibration data.
- `docs/Literatur Review Lengkap.xlsx` — literature review support.
- `docs/Recap Data CRS Bebek.xlsx` — raw historical recap; comparator only.
- `docs/data_collection_padi_bebek_FINAL.xlsx` — valid local data collection source.
- baseline versions of README/CHANGELOG/model doc/tes_skenario and all changed application/test files were compared against current master.

## 3. Baseline Scientific Behavior Confirmed

At `78f46e...` the core path implemented:

- piecewise `R_age`;
- `P_over/P_under`;
- recap-derived `lambda=0.78125` survival;
- fixed 21→65 calendar;
- recap-derived Y0 plus invented density/age/system modifiers;
- isolated feed/weed/pest/infrastructure/fertilizer formulas;
- paddy 6000 and duck sale 35000;
- `Profit_net_cash` based on incomplete cost circuit;
- visualization curves derived from the same invalid formulas.

This is why `78f46e...` is a **code baseline only**, not a formula baseline.

## 4. Current Master Scientific Behavior Confirmed

Current master replaced several old formulas but still implements:

- all seven inputs mandatory, including `p_duck_buy`;
- fixed release 21, pull 65, duration 44;
- Inpari 109–116;
- `N_survive=J` up to d=8 and 60% above;
- fixed yield 47.8767507 kg/are;
- paddy 6000;
- terminal/sale concept as `Revenue_duck_potential=N_survive*52500`;
- fixed feed cost `J*20000`;
- `Net_Cash_Contribution_DSS` as canonical output;
- v3 persistence for these values;
- visualization/golden tests that hard-lock these semantics;
- sandbox formulas that remain executable even where R2 requires non-execution.

## 5. Repository Architectural Understanding

Current request flow:

```text
FastAPI app
  -> /api/v1 router
     -> DSS route
        -> DSSService.simulate()
           -> lookup_repository / seed
           -> formula_engine
           -> impact_engine
           -> optional history_repository
           -> Pydantic response
```

Visualization flow:

```text
POST /dss/visualize
  -> VisualizationService
     -> generate density/age series
     -> internally invoke DSS simulation for financial values
```

Auth/history flow:

```text
register/login -> users table -> custom JWT
optional bearer on simulate -> persist simulation
required bearer on history list/detail/delete
```

Optimizer flow is separate and currently a stub. It must remain isolated during R2 core migration.

