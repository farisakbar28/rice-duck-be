# R2 Backend Agent Implementation Checklist

> Execute in order. Do not skip to “make tests green” by preserving legacy semantics.

## Phase 0 — Establish Working Baseline

- [ ] Confirm repository is `farisakbar28/rice-duck-be`.
- [ ] Confirm baseline reference commit `78f46ebd8004b8ebfdd7559a1c0648482d3eeeaa` is available.
- [ ] Preserve current `master` history; do not force-push away the three later commits.
- [ ] Create implementation branch for R2.
- [ ] Add this documentation package before scientific code changes.
- [ ] Mark old active SoT/validation/scenario docs as legacy-invalidated.

## Phase 1 — Domain Contract First

- [ ] Rewrite `app/schemas/dss.py` using `03_R2_API_CONTRACT.md`.
- [ ] Make `p_duck_buy` optional nullable; missing/null -> default, supplied value must be >0.
- [ ] Introduce support/availability/completeness fields.
- [ ] Make unavailable numeric fields nullable.
- [ ] Remove canonical `Revenue_duck_potential`, `Net_Cash_Contribution_DSS`, fixed-yield semantics.
- [ ] Ensure response can carry range values, provenance and warnings.

## Phase 2 — Domain Models and Parameter Registry

- [ ] Rewrite `app/domain/models.py` R2 structures.
- [ ] Separate provenance status from execution state.
- [ ] Remove wrong 21/65 aliases from active R2 types.
- [ ] Remove sale-price/feed/yield defaults from active constants.
- [ ] Add immutable parameter registry version.
- [ ] Rewrite `app/data/seed.py` with only approved R2 values.
- [ ] Do not seed `Y_base` or `F_RD_lookup` with legacy values.

## Phase 3 — Pure R2 Engines

### 3A Normalization

- [ ] `A_m2=100*A_are`.
- [ ] `d=J/A_are`.
- [ ] purchase price resolution default=26,500.

### 3B Support engine

- [ ] age flag only.
- [ ] density flag only.
- [ ] no numerical penalty from support flags.

### 3C Calendar

- [ ] harvest Sertani 100–110.
- [ ] harvest Inpari 90–100.
- [ ] release 21–30.
- [ ] pull 56–60.
- [ ] active duration ref=32, interval=28–40.

### 3D Survival

- [ ] lambda 0.90 only when age+density both supported.
- [ ] otherwise unavailable/null.
- [ ] `floor(J*lambda)` only after gate.
- [ ] no sale state.

### 3E Yield

- [ ] implement lookup interface.
- [x] Phase-6 range baseline and global F_RD reference are active.
- [ ] exact approved local cultivar-group normalization only; no fuzzy aliases.
- [x] missing group baseline/F_RD reference -> null, not legacy Y0.
- [ ] no interpolation/extrapolation/nearest-neighbour/cross-system yield lookup.
- [ ] no system/age/density fallback multipliers.

### 3F Fertilizer baseline

- [ ] N-P2O5-K2O consistent basis.
- [ ] baseline needs 1.1761 / 0.2745 / 0.2745 per are.
- [ ] no manure credit formula.
- [ ] Urea 46% N.
- [ ] NPK 15-10-12.
- [ ] HET 1800/1840 versioned.
- [ ] no KCl branch.

### 3G Infrastructure

- [ ] equivalent perimeter formula.
- [ ] return min/ref/max net cost.
- [ ] cage only per-unit range; no total without capacity.

### 3H Feed/weed/pest

- [ ] feed returns unavailable.
- [ ] weeding returns baseline range only; saving unavailable.
- [ ] pest effect descriptive/context-specific; saving unavailable.

### 3I Economics

- [ ] `C_duck_buy` active.
- [ ] terminal duck value not cash revenue.
- [ ] paddy benchmark 6500.
- [ ] `Cost_core_direct=C_duck_buy+C_net_cycle_ref`.
- [ ] margin only if yield+survival available.
- [ ] full profit only if complete.

## Phase 4 — Service Layer

- [ ] Rewrite `simulation_service.py` orchestration in engine order.
- [ ] No silent scientific fallback.
- [ ] Propagate null + reason codes.
- [ ] Preserve trace formula IDs and source IDs.
- [ ] Optional authenticated user only affects persistence, not numeric result.

## Phase 5 — Persistence v4

- [ ] Implement `05_R2_PERSISTENCE_VERSIONING.md`.
- [ ] Create new R2 table or semantically isolated v4 storage.
- [ ] Keep v1-v3 immutable.
- [ ] Save request/response/trace snapshots.
- [ ] Store model + registry + Git commit versions.
- [ ] Never convert scientific null to zero.

## Phase 6 — Routes / OpenAPI

- [ ] Update `/dss/options`.
- [ ] Update `/dss/simulate` descriptions.
- [ ] Update history endpoints for v4.
- [ ] Keep optimizer isolated/stub.
- [ ] Update `app/main.py` title/description/version.

## Phase 7 — Visualization

- [ ] remove fixed yield benchmark.
- [ ] remove survival 1.0/0.60 curve.
- [ ] remove R_age/F_density legacy curves.
- [ ] show support zones and ranges only.
- [ ] waterfall must distinguish terminal value from cash revenue.
- [ ] unavailable components are visible as unavailable, not hidden zero.

## Phase 8 — Test Rewrite

- [ ] delete/replace old numeric golden test.
- [ ] rewrite formula engine tests.
- [ ] rewrite API contract tests.
- [ ] rewrite visualization tests.
- [ ] add v4 history tests.
- [ ] add banned-formula anti-regression tests.
- [ ] add missing != zero tests.
- [ ] add fail-closed lookup tests.
- [ ] do not assert old historical MAE constants.

## Phase 9 — Docs/Postman

- [ ] README points to R2 SSOT.
- [ ] CHANGELOG adds R2 and clearly marks previous models historical invalid for production.
- [ ] Postman collection uses optional price/default branch.
- [ ] Postman asserts null/unavailable yield and full profit while lookup incomplete.
- [ ] replace old scenario guide with `tes_skenario_R2.md`.

## Phase 10 — Security Hardening

- [ ] remove meaningful default JWT secret from source.
- [ ] production startup fails on placeholder/missing secret.
- [ ] restrict CORS for production environment.
- [ ] keep low hash iterations only in tests.

## Phase 11 — Freeze and Validation

- [ ] all computational/invariant tests pass.
- [ ] model + registry version frozen.
- [ ] Git commit recorded.
- [ ] build validation fixtures with provenance.
- [ ] run comparator validation only for semantically compatible outputs.
- [ ] use all-36 + strict-domain-17 when yield becomes executable.
- [ ] run 8 excluded stress cases separately.
- [ ] do not recalibrate from comparator errors.

## Final Acceptance Gates

- [ ] No recap-derived parameter in production R2.
- [ ] No banned legacy formula reachable from `/dss/simulate`.
- [ ] No fabricated numeric value for unresolved component.
- [ ] No `N_survive -> N_sold` alias.
- [ ] No net/full profit overclaim.
- [ ] No v3 semantic reuse for R2 persistence.
- [ ] Every active number/formula has provenance and status.
- [ ] Every unavailable output has a reason code.
- [ ] Backend behavior matches documentation, not the other way around.

## Phase 6C-B / 6D — Approved Phase-6 Candidate Implementation (after docs-first)

- [ ] Keep exactly seven input concepts; create no density, release, or evidence user input.
- [ ] Replace the empty/exact-node yield store with group range records and one `SUPPORTED_DOMAIN_GLOBAL_F_RD` reference record.
- [ ] Implement ref/low/high yield and area scaling only behind resolved-group + supported-age + supported-density + F_RD gates.
- [ ] Preserve `LITERATURE_EVIDENCE_ENVELOPE`, `LITERATURE_UNCALIBRATED`, source IDs, and Sertani low-evidence metadata in response, trace, visualization, and history snapshot.
- [ ] Map existing yield numeric aliases to reference values; add explicit envelope fields and range-aware economic propagation.
- [ ] Keep feed, cage total, monetary savings, manure credit, and full profit unavailable; terminal duck value stays an asset.
- [ ] Add the additive v4-history columns/migration and preserve all R2.2 rows unchanged.
- [ ] Implement the Phase-6 test matrix in docs/06; verify source isolation and no interpolation/extrapolation.
- [ ] Bump registry/freeze to `.3` only with the implementation, full passing tests, and a clean committed target.
- [ ] Only after that freeze, run the comparator and publish pre-registered reference/envelope metrics without recalibration.
