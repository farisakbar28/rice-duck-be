# R2 Backend Documentation Index

> **Project:** Rice-Duck DSS Backend  
> **Repository:** `farisakbar28/rice-duck-be`  
> **Implementation baseline:** commit `78f46ebd8004b8ebfdd7559a1c0648482d3eeeaa`  
> **Audited current master:** commit `2a4824d97933e662cfe9b7a70e1d442f7fb43ac4`  
> **Model generation:** R2 — Economic/Cost Model, 26 August 2026  
> **Status:** implementation specification; not a record of completed R2 runtime results.

## 1. Purpose

Folder ini adalah paket dokumentasi acuan untuk migrasi backend `rice-duck-be` dari model matematika lama menuju **R2**. Dokumen ini mengikat keputusan penelitian yang sudah dikonfirmasi dan mencegah agent backend membawa kembali formula, parameter, atau validation logic yang sudah dinyatakan tidak valid.

Commit `78f46e...` dipakai sebagai **baseline arsitektur/kode sebelum tiga commit migrasi terbaru**, bukan sebagai source of truth matematika. Formula matematika pada commit tersebut juga sudah diaudit dan sebagian besar **tidak valid untuk R2**.

Current `master` juga **bukan** source of truth R2. Ia adalah implementasi generasi sesudah `78f46e...` yang masih membawa model salah/usang pada calendar, survival, yield, ekonomi, sandbox, persistence, visualization, tests, dan dokumentasi.

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
| `tes_skenario_R2.md` | Template evidence runtime dan historical comparator; tidak berisi hasil palsu sebelum code dijalankan. |

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

### current master — do not patch by changing constants only

Current master removed some old pseudo-formulas, tetapi menggantinya dengan model baru yang tetap salah untuk R2: fixed yield, full/60% survival, 109–116 Inpari window, mandatory purchase price, potential duck sale, fixed feed cost, dan `Net_Cash_Contribution_DSS`.

Migrasi R2 harus berupa **semantic migration**, bukan constant replacement.

## 6. Definition of Done for Documentation Sync

Migrasi dokumentasi dianggap sinkron ketika:

- README menunjuk `01_R2_MODEL_SSOT.md` sebagai mathematical source of truth.
- old SoT diberi status `LEGACY_INVALIDATED` atau dipindahkan ke archive; tidak lagi diberi label FINAL aktif.
- old numerical validation diberi status historical invalid-for-R2 karena menggunakan rekap sebagai calibration/LOFO baseline.
- `tes_skenario.md` lama tidak dipakai sebagai R2 evidence.
- Postman, OpenAPI descriptions, tests, seed metadata, DB comments, dan changelog tidak lagi menyebut semantics yang dilarang R2.

