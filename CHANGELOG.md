# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Restored cycle-specific `p_duck_buy` values to H01-H11 holdout replay using cleaned source-row mapping, enabling source-level audit of `cost_duck_buy` and scenario cash contribution without changing frozen Model C yield parameters or holdout metrics.
- **Breaking: Model C migration.** The active production formula is frozen C0: 50 kg/are from the farmer-grouped calibration partition. C1/C3/C4 candidate coefficients remain research-only and cannot enter `/api/v1/dss/simulate`.
- The simulation API now has five core inputs, strict finite JSON-number validation, optional calendar/prices/scenario costs, and no Xiong or literature-duration runtime contract.
- Density and age are gates only; numerical survival, the old fixed calendar, legacy yield/revenue fields, and hidden feed costs were removed from Model C responses.
- Calendar recommendations are 21–30 HST release and 56–60 HST withdrawal. Branch-C fallbacks are 6000/25000/45000 with local-calibrated/local-estimate provenance.
- Feed and infrastructure are explicit optional costs, and authenticated current histories use deterministic schema version 4 while v1–v3 remain preserved historical rows.
- Model C tests, OpenAPI descriptions, Postman requests, and real-HTTP holdout/synthetic/history acceptance evidence were updated.

### Notes
- Release 2.0.0 below remains an historical record of the previous v2 model and is superseded by this migration; its formulas and test claims are not the current production contract.

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
