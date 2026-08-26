# R2 Backend Documentation Index

> **Project:** Rice-Duck DSS Backend  
> **Repository:** `farisakbar28/rice-duck-be`  
> **Implementation baseline:** commit `78f46ebd8004b8ebfdd7559a1c0648482d3eeeaa`  
> **Current release checkout:** branch `master`, HEAD `186ebf9f4542cd056f69d6b7639f9870c5372959`
> **Scientific target:** `b10b0a1f83357c5db1d6cdfb9c41eaa84b6727a7`
> **Model generation:** R2 — Economic/Cost Model, 26 August 2026  
> **Status:** current authoritative index for `R2_PHASE6_TECHNICAL_EMPIRICAL_RELEASE_CLOSED_WITH_LIMITATIONS`.

## 1. Purpose

Folder ini adalah paket dokumentasi acuan untuk migrasi backend `rice-duck-be` dari model matematika lama menuju **R2**. Dokumen ini mengikat keputusan penelitian yang sudah dikonfirmasi dan mencegah agent backend membawa kembali formula, parameter, atau validation logic yang sudah dinyatakan tidak valid.

Commit `78f46e...` dipakai sebagai **baseline arsitektur/kode sebelum tiga commit migrasi terbaru**, bukan sebagai source of truth matematika. Formula matematika pada commit tersebut juga sudah diaudit dan sebagian besar **tidak valid untuk R2**.

The pre-R2 `master` snapshot audited during migration was not the R2 source of
truth. That historical audit identified stale calendar, survival, yield,
economic, sandbox, persistence, visualization, test, and documentation
semantics; the current release checkout is governed by the canonical documents
and the final Phase-6 evidence below.

## 2. Absolute Evidence Rules

1. Data wawancara/data collection lokal boleh menjadi sumber kalibrasi/estimasi lokal.
2. `Recap Data CRS Bebek.xlsx`, dataset bersih, dan turunannya **hanya comparator validasi**. Dilarang menggunakannya untuk fitting, median parameter, baseline yield, multiplier, atau calibration R2.
3. Formula/angka tanpa sumber valid tidak boleh dieksekusi.
4. Formula lama yang tidak valid tidak dihapus dari sejarah penelitian; ia masuk **Legacy/Unresolved Register** dan dinonaktifkan dari runtime.
5. Literatur prioritas: Bali > Indonesia > ASEAN > Asia > global; >2020 diprioritaskan; sumber Scopus wajib untuk dasar ilmiah kecuali data resmi pemerintah/produsen.
6. Output yang belum memiliki evidence numerik cukup harus menjadi `UNAVAILABLE`, `PENDING_LOOKUP`, atau `INCOMPLETE`; jangan mengganti dengan angka buatan.
7. Historical replay tidak boleh mengubah parameter R2 setelah residual/error dilihat.

## 3. Document Precedence

Jika ada konflik, urutan berikut berlaku:

1. `01_R2_MODEL_SSOT.md`
2. `03_R2_API_CONTRACT.md`
3. `04_R2_PARAMETER_EXECUTION_REGISTRY.md`
4. `05_R2_PERSISTENCE_VERSIONING.md`
5. `07_R2_LEGACY_INVALIDATION_REGISTER.md`
6. `02_R2_BACKEND_MIGRATION_PLAN.md`
7. `08_R2_IMPLEMENTATION_CHECKLIST.md`
8. `06_R2_TEST_VALIDATION_PROTOCOL.md`
9. `tes_skenario_R2.md`
10. README/CHANGELOG/Postman/tests setelah semuanya disinkronkan.

For current release status and publication-source mapping, use
`docs/14_R2_FINAL_RELEASE_CLOSURE.md` and its `docs/export/` package. For
scientific equations and parameter values, the precedence above remains in
force; release closure does not override the SSOT.

Dokumen lama berikut **tidak boleh lagi mengalahkan R2**:

- `docs/Model Matematika Data Collection DSS Padi Bebek FINAL.md`
- `docs/NUMERICAL_VALIDATION_DSS_PADI_BEBEK_FINAL_CLEAN.md`
- `docs/tes_skenario.md`
- runtime/golden tests pada `master` sebelum migrasi R2.

## 4. Files in This Package

| File | Function |
|---|---|
| `00_R2_BACKEND_DOCUMENTATION_INDEX.md` | Peta dokumen dan precedence. |
| `01_R2_MODEL_SSOT.md` | Source of Truth matematika/ekonomi R2 yang boleh diimplementasikan. |
| `02_R2_BACKEND_MIGRATION_PLAN.md` | Audit repo, delta `78f46e -> master`, file-by-file disposition, dan migration sequence. |
| `03_R2_API_CONTRACT.md` | Kontrak request/response API R2, availability semantics, error contract, visualization contract. |
| `04_R2_PARAMETER_EXECUTION_REGISTRY.md` | Registry parameter/formula, status tag, execution state, provenance, dan unresolved items. |
| `05_R2_PERSISTENCE_VERSIONING.md` | Schema history R2 (`schema_version=4`), migration dan legacy read-only policy. |
| `06_R2_TEST_VALIDATION_PROTOCOL.md` | Unit/contract/integration/validation methodology yang sudah dikonfirmasi. |
| `07_R2_LEGACY_INVALIDATION_REGISTER.md` | Daftar literal formula/field/constant yang dilarang kembali ke production path. |
| `08_R2_IMPLEMENTATION_CHECKLIST.md` | Urutan pekerjaan agent backend dan acceptance gates. |
| `09_R2_REPO_AUDIT_MANIFEST.md` | Historical pre-R2 repository audit and artifact disposition. |
| `10_R2_REFERENCE_PROVENANCE.md` | Current source/provenance registry for R2 parameters and external evidence. |
| `11_R2_FREEZE_MANIFEST.md` | Semantik freeze (frozen = immutable validation target), dimensi identitas, isi manifest, official execution gate, anti-kalibrasi. |
| `12_R2_TECHNICAL_VALIDATION_SIGNOFF.md` | Historical Phase-5C `.2` technical validation evidence. |
| `13_R2_PHASE6_TECHNICAL_EMPIRICAL_SIGNOFF.md` | Independent Phase-6 technical-empirical signoff, corrected comparator evidence, limitations, and no-change disposition. |
| `14_R2_FINAL_RELEASE_CLOSURE.md` | Current R2 release-level closure, evidence-status matrix, documentation-role matrix, correction register, and publication source map. |
| `export/R2_FINAL_MATHEMATICAL_MODEL_SOURCE.md` | Authoritative source for later mathematical-model DOCX generation; not a DOCX. |
| `export/R2_FINAL_VALIDATION_METHODOLOGY_SOURCE.md` | Authoritative source for later validation-methodology DOCX generation; not a DOCX. |
| `export/R2_IJOST_MANUSCRIPT_FACT_PACKAGE.md` | Publication-safe factual source package; not the manuscript. |
| `export/R2_EXPORT_SOURCE_AUDIT.md` | Cross-source identity, numeric, claim, and expert-status consistency audit. |
| `tes_skenario_R2.md` | Scenario/provenance guidance for runtime and historical comparator evidence; not a substitute for committed results. |

## Current Phase-6 release amendment

The Phase-6 configuration is active in the current R2 runtime under registry
`R2-2026-08-26.3` and freeze `R2-FREEZE-2026-08-26.5`. Corrected retrospective
yield and revenue diagnostics are authoritative in the Phase-6D-R evidence and
independently approved by Phase 6E. The earlier R2.2 `.2` sign-off and the
intermediate `.3`/`.4` freeze candidates remain historical audit lineage only.
Older statements that yield was empty or that the comparator was pending are
historical statements when explicitly labelled and do not describe this
release.

## 5. Baseline Interpretation

### `78f46e...` — retain only as architectural reference

Yang masih berguna dari baseline:

- FastAPI layering: routes → service → engine/repository → schema.
- `Decimal` precision and no mid-calculation rounding philosophy.
- Optional authentication and history ownership pattern.
- Dedicated read-only visualization endpoint pattern.
- Clear separation between endpoint contract and internal computation.

Yang **tidak boleh dipertahankan sebagai scientific semantics**:

- `R_age`, `P_over`, `P_under`.
- `lambda_eff=0.78125*(...)`.
- custom `F_density_bio` and `F_age`.
- `F_sys(Tegel)=1.211`.
- `Y0=47.8767507`.
- 21→65/44-day fixed calendar.
- feed/weed/pest/manure/infrastructure formulas yang telah dibatalkan R2.
- implicit `N_survive -> Revenue_duck`.
- `Profit_net_cash` semantics.

The following current-master comparison is retained as an implementation-history
record from the pre-R2 audit. It does not describe the current release checkout.

### historical pre-R2 master — do not treat as current release state

The pre-R2 audited master removed some old pseudo-formulas, tetapi menggantinya dengan model baru yang tetap salah untuk R2: fixed yield, full/60% survival, 109–116 Inpari window, mandatory purchase price, potential duck sale, fixed feed cost, dan `Net_Cash_Contribution_DSS`.

Migrasi R2 harus berupa **semantic migration**, bukan constant replacement.

## 6. Definition of Done for Documentation Sync

Migrasi dokumentasi dianggap sinkron ketika:

- README menunjuk `01_R2_MODEL_SSOT.md` sebagai mathematical source of truth.
- old SoT diberi status `LEGACY_INVALIDATED` atau dipindahkan ke archive; tidak lagi diberi label FINAL aktif.
- old numerical validation diberi status historical invalid-for-R2 karena menggunakan rekap sebagai calibration/LOFO baseline.
- `tes_skenario.md` lama tidak dipakai sebagai R2 evidence.
- Postman, OpenAPI descriptions, tests, seed metadata, DB comments, dan changelog tidak lagi menyebut semantics yang dilarang R2.

The final Phase-6 documentation closure additionally requires the release
closure and export-source package to agree with the committed corrected
evidence, while `EXPERT_FINAL_REVIEW=PENDING_NON_BLOCKING_EVIDENCE_STREAM`.
