# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

> **Canonical status:** this Unreleased section describes the active R2
> contract. Releases 1.0.0 and 2.0.0 below are immutable historical records;
> their formulas, response fields, and test claims are superseded and must not
> be used as current implementation guidance.

### Added
- Added `POST /api/v1/dss/visualize`, a side-effect-free view over the canonical
  R2 simulation with complete support-zone partitions, calendar windows,
  calculated infrastructure ranges, fertilizer baseline components,
  availability-aware yield series, and a partial financial waterfall.
- Added fail-fast security configuration validation for required JWT secrets,
  production debug/CORS/placeholder restrictions, and the production PBKDF2
  iteration floor.
- Added active visualization, provenance, configuration, and startup tests plus
  explicit pytest quarantine for `tests/legacy_invalid/`.
- Added Phase-5 freeze governance metadata: `MODEL_FROZEN`, `FREEZE_ID`
  (`R2-FREEZE-2026-08-26.1`), and `FREEZE_EFFECTIVE_FROM` in the seed layer,
  exposed as `model.freeze_id` / `model.frozen = true` in simulation and
  visualization responses. Frozen means *immutable validation target*; it does
  not mean empirically validated, accurate, or complete (docs/11).
- Added `docs/11_R2_FREEZE_MANIFEST.md` describing freeze semantics, distinct
  provenance dimensions, manifest contents, and the official execution gate.
- Added an isolated research-only validation harness (`validation/`,
  `python -m validation`) with source fingerprinting (SHA-256 + sheets),
  provenance policies, canonical-runtime synthetic evidence (B01–B18),
  supported-age invariance checking, docs/06 §19 V1 matrix mapping, calendar
  metric primitives with cluster bootstrap, expert-transfer matrix, and
  deterministic artifact/report generation. Research dependencies are split
  into `requirements-validation.txt`; production code never imports them.
- Added freeze-semantics tests (identity dimensions, Phase-4 parameter
  snapshot guard, availability invariance under freeze) and production/
  research isolation guards (no `app/` import of `validation`, no fitting or
  optimization code paths, no rebinding of canonical registry identifiers).

### Changed
- Simulation/visualization model metadata now sources `frozen` from the freeze
  configuration instead of a hardcoded literal; the response contract gains an
  optional `freeze_id` field.
- Completed the R2 migration across API descriptions, README, Postman assets,
  environment examples, and canonical API/persistence documentation.
- Corrected yield lookup identity: generic input options no longer claim exact
  cultivar resolution; exact cultivar identity and baseline-row availability
  are independent fail-closed conditions.
- Corrected trace metadata so active and conditional formula IDs represent the
  selected and successfully executed branches rather than registry membership.
- Adopted `0.0.0-dev` as the source-checkout application version; deployments
  inject their own release version independently of model version `R2`.
- Preserved schema-v4 snapshot history and isolated pre-R2 compatibility paths
  without recomputation or reinterpretation.

### Security
- Removed the usable in-source JWT signing-secret fallback.
- Production startup now rejects debug mode, wildcard or empty CORS origins,
  placeholder/trivial JWT secrets, and password hashing below 600,000
  iterations. Reduced hashing cost is permitted only in the test environment.

## [2.0.0] - 2026-07-16

### Added
- **Economic Differential-Costing Engine (SoT v2)** — Total migration from legacy linear model to biologically-validated differential costing engine per `docs/Model Matematika Data Collection DSS Padi Bebek FINAL.md`.
- **Yield Engine — Non-linear Bio-density Curve** (`F_density_bio`): Exponential saturation boost (`α=0.15, K_opt=4`) + quadratic trampling penalty (`β=0.25, K_max=8`). Replaces legacy linear `F_density = 1 - 0.12*P_under - 0.25*P_over`.
- **Varietal Coefficient Normalization** (`F_var = 1.00`): Overrides legacy `0.80`; no base yield cut for Sertani/Inpari per empirical correction (Tabel 1 SoT).
- **Two-Tier Circuit Architecture** (Bagian 5 SoT):
  - **Core Validated Output Group (Active Circuit)**: `Cost_duck_buy`, `Cost_total_cash` (= `Cost_duck_buy`), `Profit_net_cash`, revenues, yield, calendar, survival.
  - **Empirically Uncorrelated Isolated Output Group (Sandbox Circuit)**: `Cost_feed_isolated`, `Cost_weeding_isolated`, `Cost_pesticide_isolated`, `Cost_infra_isolated`, `Cost_fertilizer_isolated` + sub-components. These are **fully excluded** from `Cost_total_cash` and `Profit_net_cash` aggregation.
- **High-Precision Numeric Stack**: All engine computations use `decimal.Decimal` (precision=50). Custom Taylor-series `exp()` (100 terms) and Newton-Raphson `sqrt()` (50 iterations). **Zero mid-calculation rounding** — rounding only at JSON serialization boundary.
- **Complete Ecology Engine Removal**: `V_weed_eco`, `Valuation_weed_eco`, `Profit_net_full` deleted from schema, DB, repository, service, and response DTOs. Focus strictly on real cash liquidity (`Profit_net_cash`).

### Changed
- **Age Engine**: Piecewise thresholds clarified — `<14` (0.35), `14–29` (0.15), `≥30` (0.05). Boundary `14` and `30` are inclusive in safe range.
- **Density Engine**: `P_over` capped at `1.0`; `P_under` unbounded at 1.0 but density floor is `>0`. `K_safe` differentiated: `4` (Jarwo) vs `3` (Tegel).
- **Survival Engine**: `λ_eff` ceiling = `0.78125`; depreciation factors `0.50` (R_age) and `0.45` (P_over). `N_survive` uses `floor` (not `round`).
- **Material Engine**: Phonska elemental fractions updated to subsidized 15-10-12 specification (P=0.04364, K=0.09961); KCl non-subsidized 60% K₂O → K=0.49806. HET prices locked: Urea 1800, Phonska 1840, KCl 9500.
- **Infrastructure Cost**: Net = `0.5 * 289260 * sqrt(A_are)`; Cage = flat `175000`.
- **Feed Cost**: `J * 4500 * (1 + 0.75*P_over + 0.50*R_age)`.
- **Weed & Pest Reduction**: Asymptotes 0.93 / 0.80; decay rate 0.35.

### Removed
- Legacy linear `F_density` formula (`1 - 0.12*P_under - 0.25*P_over`).
- Legacy `F_var = 0.80` (varietal base yield penalty).
- `V_weed_eco` constant (13500) and `compute_ecology_weed()` function.
- `Valuation_weed_eco` and `Profit_net_full` fields from API response, DB schema, and history repository.
- `Cost_labor_base`, `Cost_labor_tending`, `Cost_labor_total` — permanently deleted per SoT.
- All mid-calculation rounding (e.g., `floor(yield_are * 100)/100` before revenue multiplication).

### Fixed
- Binary reference files (`*.xlsx`, `*.docx`) preserved on disk; git LFS tracking recommended.
- UTF-8 BOM removed from `formula_engine.py`, `impact_engine.py`, `simulation_service.py`.
- CRLF/LF line-ending warnings suppressed via `.gitattributes`.

### Test Coverage
- **44/44 tests passing** (test_api.py, test_formula_engine.py, test_sot_golden_case.py).
- Golden case validated: `Yield_are_predict=52.36`, `Profit_net_cash=3011883.01` for SoT reference input (10 are, 50 ducks, sertani, jarwo, U=14).
- All 36 integration scenarios from `docs/tes_skenario.md` populated with live backend responses.

### Documentation
- `README.md` fully rewritten: all legacy formulas removed; new `F_density_bio`, `F_var=1.00`, Two-Tier response schema, and golden case documented.
- `docs/tes_skenario.md` fully populated: 36/36 scenarios executed against live backend, outputs recorded verbatim from API responses.

## [1.0.0] - 2026-07-15

### Added
- Initial release aligned with SoT v1 (Model Matematika Data Collection DSS Padi Bebek FINAL.docx).
- DSS Core simulation endpoint with Age, Density, Calendar, Survival, Yield, Material, Cost, Ecology engines.
- SQLite history persistence with explicit column schema (v2).
- Optimizer stub endpoint (`/api/v1/optimizer/recommend`).
- Pytest suite covering formula engines and golden case validation.

---

**Legend:**
- **Added** for new features.
- **Changed** for changes in existing functionality.
- **Removed** for now-deleted features.
- **Fixed** for bug fixes.
- **Test Coverage** for testing improvements.
- **Documentation** for documentation updates.
