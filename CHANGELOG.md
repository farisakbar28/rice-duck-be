# CHANGELOG — Migrasi DSS Padi-Bebek ke Model FINAL_BANGET

Semua perubahan mengikuti **source-of-truth tunggal**:
`docs/Model_Matematika_Data_Collection_DSS_Padi_Bebek_FINAL_BANGET.md` (selanjutnya "`_BANGET`").
File `Model_Matematika_..._FINAL_terbaru.md` (sebelumnya) dan versi lama bersifat **DEPRECATED** untuk
logika bisnis kalkulator DSS.

Konvensi referensi: `[GAP-XX]` = nomor item di Gap Analysis scan awal.

---

## [Unreleased]

### Removed

- `Cost_labor_tending` dihapus permanen dari formula Cost Engine dan dari response API (`DSSSimulationResponse`
  tidak mengekspos field ini).
- `Cost_labor_tending` dihapus permanen dari Cost Engine (tidak ada sumber kalibrasi, uji regresi
  37 baris rekap bersih menunjukkan J tidak signifikan terhadap Total Labor Cost).

### Fixed

- Bug `AttributeError` pada `SimulationHistory` saat menyimpan history v2 (field `cost_labor_tending`
  kini ada di dataclass, default 0.0, deprecated).

### Changed

- `Cost_labor_total` SoT example: Rp610.955 → Rp540.955.
- `Valuation_weed_eco` SoT example: Rp116.360 → Rp101.422.
- Basis `V_weed_eco` disederhanakan dari `Cost_labor_base_tending` menjadi `Cost_labor_base` murni.
- Dokumentasi: README.md kini merujuk ke `FINAL_BANGET.md` sebagai source-of-truth aktif.
- Dokumentasi: `FINAL_terbaru.md` ditandai DEPRECATED dengan banner peringatan.

### Added

- **Status final golden case FINAL_BANGET** (`A_are=10, J=50, Sertani, Jarwo, U_duck=14`):
  `Cost_labor_total=540.955`, `Cost_total_cash=2.561.008`, `Profit_net_cash=1.053.392`,
  `Valuation_weed_eco=101.422`, `Profit_net_full=1.154.814`, `N_survive=27`.
- **Kolom `cost_labor_tending` di DB schema dipertahankan sebagai DEPRECATED** (bukan di-drop). 
  Alasan: SoT FINAL_BANGET.md Catatan Finalisasi poin 12 hanya mewajibkan penghapusan dari **formula Cost Engine**, 
  bukan dari DB schema. Kolom diperlukan untuk backward compatibility historical records. 
  Nilai selalu 0.0, TIDAK di-expose di API response. Detail di `app/core/database.py` dan `app/domain/models.py`.
  Tidak ada migrasi/drop kolom untuk revisi final ini.
- **Dokumen `docs/AUDIT_ERRATA.md`** — Koreksi resmi temuan "Critical #2" pada audit independen 
  sebelumnya: klaim "Tabel 2.2 SoT menyebut 27.5014" adalah **TIDAK VALID** (angka tersebut tidak 
  ada di SoT manapun). SoT konsisten: proses `J·λ_eff = 27.5`, output final `N_survive = 27 Ekor` (floor). 
  Kode/API sudah benar (`N_survive: 27.0`), tidak ada perubahan formula diperlukan.
- **File `AUDIT_REPORT.md` tidak pernah ada di git history** — sudah diverifikasi via `git log --all`. 
  Kemungkinan besar file tersebut tidak pernah dibuat atau dihapus sebelum commit. CHANGELOG.md berperan 
  sebagai pengganti catatan perubahan & audit trail.

---

## Ringkasan per Fase

| Fase | Judul | Risiko | Status |
|---:|---|---|---|
| 0 | Isolasi optimizer | Tinggi | Selesai |
| 1 | Calendar engine | Tinggi | Selesai |
| 2 | Cost engine (paling kritis) | Kritis | Selesai |
| 3 | Ekologi engine | Tinggi | Selesai |
| 4 | API additive + deprecation | Sedang | Selesai |
| 5 | DB history (kolom eksplisit) | Tinggi | Selesai |
| 6 | Cleanup artefak Generasi A | Tinggi | Selesai |
| 7 | Test suite deterministik | Tinggi | Selesai |
| 8 | Dokumentasi & rilis | Sedang | Selesai |

---

## Fase 0 — Isolasi Optimizer

**Rujukan SoT:** Catatan Finalisasi poin 2 (kalkulator 6-input manual, tanpa
optimizer).

**Perubahan kode:**
- `app/schemas/optimizer.py` (baru) — semua kelas dormant optimizer
  (`RecommendedScenario`, `OptimalityAssessment`, `EnvironmentSummary`,
  `ActualScenario`, `EconomicsSummary`, `EcologySummary`, `ComparisonSummary`,
  `RiskSummary`, `SoilNutrients`, `ValidationSummary`, `DataReadinessSummary`,
  `ScenarioEconomics`, `ScenarioEcology`, `ScenarioEnvironment`,
  `InfrastructureOutput`, `PredictedYield`, `QualityOutput`,
  `DurationConstraintSummary`, `DuckAgeAssessment`, `ProfitDataPurity`).
- `app/api/routes/optimizer.py` (baru) — endpoint
  `POST /api/v1/optimizer/recommend` (stub, fitur produk mandiri).
- `app/schemas/dss.py` — kelas optimizer dihapus total dari schema DSS core.
- `app/api/router.py` — mount router optimizer dengan tag "optimizer".
- `app/main.py` — deskripsi app dan OpenAPI tag memisahkan DSS Core (SoT) vs
  Optimizer (luar cakupan).

**DoD tercapai:**
- `grep -E "Score_safety|F_active|argmax|J_rekomendasi|DeltaProfit|REY|RecommendedScenario|OptimalityAssessment|EnvironmentSummary|ActualScenario|EconomicsSummary|EcologySummary|ComparisonSummary|RiskSummary|SoilNutrients|ValidationSummary|DataReadinessSummary|ScenarioEconomics|ScenarioEcology|ScenarioEnvironment|InfrastructureOutput|PredictedYield|QualityOutput|DurationConstraintSummary|DuckAgeAssessment|ProfitDataPurity|x_base|d_lit_ha"` di
  `app/schemas/dss.py` & `app/services/simulation_service.py` → 0 hit
  (kecuali komentar dokumentasi).

**Hubungi Gap:** #1, #18.

---

## Fase 1 — Calendar Engine

**Rujukan SoT:** Catatan Finalisasi poin 8; Tabel 2.2 Calendar Engine;
Tabel 2.3.

**Perubahan kode:**
- `app/data/seed.py` — `RiceVariety.hst_panen`: Sertani/Seratih=**99**,
  Inpari=**112** (sebelumnya 105 / 95).
- `app/engines/formula_engine.py` — fungsi baru
  `compute_calendar_milestones(...)`. `D_masuk_bebek = D_tanam + 21` (sebelumnya
  `+20`), `D_tarik_bebek = D_tanam + 65`, `t_active = 44`. Output baru
  `D_panen_gabah = D_tanam + HST_panen`.
- `app/services/simulation_service.py` — integrasi milestones baru.
- `app/schemas/dss.py` — field response baru `D_panen_gabah`.

**DoD tercapai:**
- Contoh SoT `2026-01-01 + 99 hari = 2026-04-10` (Sertani) dan
  `2026-01-01 + 112 hari = 2026-04-23` (Inpari) cocok persis di test
  `test_calendar_d_panen_sertani_99` dan `test_inpari_d_panen_gabah_112`.
- `D_masuk_bebek` di-set ke `D_tanam + 21` (test
  `test_calendar_d_masuk_21_d_tarik_65`).

**Hubungi Gap:** #3, #4, #5.

**Open question (butuh konfirmasi):**
- Perubahan `D_masuk_bebek` dari `+20` ke `+21` adalah **breaking** untuk
  reminder user-facing. Konfirmasi product owner sebelum merge ke production
  jika sudah ada user aktif.

---

## Fase 2 — Cost Engine (PALING KRITIS)

> **[SUPERSEDED]** Section di bawah ini mendeskripsikan skema versi sebelum penghapusan `Cost_labor_tending` (lihat Catatan Finalisasi poin 12, `FINAL_BANGET.md`). Field `Cost_labor_tending` dan `Cost_labor_base_tending` sudah tidak ada di formula/API sejak revisi final.

**Rujukan SoT:** Catatan Finalisasi poin 9, 10, 11; Tabel 2.2 Cost Engine.

**Perubahan kode:**
- `app/engines/impact_engine.py`:
  - `compute_weed_reduction(d) = 0.95 * (1 - exp(-0.35*d))` (baru).
  - `compute_weed_hired_cost(A, d) = 30539 * A * (1 - R_weed(d))` (baru).
  - `compute_labor_breakdown(...)` (baru) — mengembalikan
    `Cost_labor_base`, `Cost_labor_tending`, `Cost_labor_weed_hired`,
    `Cost_labor_base_tending`, `Cost_labor_total`.
  - `compute_infrastructure_breakdown(...)` (baru) — mengembalikan
    `Cost_infra_net`, `Cost_infra_cage`, `Cost_infra` dengan floor
    proporsional (`max(58333, raw_net + raw_cage)` dan scaling
    `58333 / raw_sum` saat raw_sum < floor dan > 0).
- `app/data/seed.py` — `PlantingSystem.F_sys` Tegel = **0.95**
  (sebelumnya `f_yield=1.39`). Field deprecated `f_yield` di-sync.
- `app/services/simulation_service.py` — menggunakan helper breakdown.

**Guardrail (tidak dilanggar):**
- `Cost_feed = J * 5000 * (1 + 0.75*P_over + 0.50*R_age)` — formula
  identik dengan sebelumnya. Test `test_feed_unchanged_scale` &
  `test_cost_feed_invariant` mengunci invariannya.
- `Cost_infra total` formula identik dengan versi lama
  (`max(58333, raw_net + raw_cage)`). Test
  `test_cost_infra_total_matches_legacy_formula` mengunci 286488 untuk
  contoh SoT.
- Invariant: `Cost_infra_net + Cost_infra_cage == Cost_infra` (test
  `test_infra_floor_split_invariant_many_cases`).

**DoD tercapai:**
- Contoh SoT `A=10, J=50, U=14, Jarwo`:
  - `Cost_labor_weed_hired ≈ 65685` ✓
  - `Cost_labor_total ≈ 610955` ✓
  - `Cost_infra_net ≈ 78163`, `Cost_infra_cage ≈ 208325`,
    `Cost_infra = 286488` ✓
  - `Cost_feed = 315625` ✓
- Tegel: yield turun (F_sys=0.95), bukan naik
  (test `test_yield_tegel_penalty_not_bonus`).

**Hubungi Gap:** #6, #8, #9, #10, #12, #13, #14, #15.

**Open question (butuh konfirmasi):**
- Edge case `raw_net + raw_cage == 0` (A=J=0) — saat ini split 50/50 dari
  floor. **Perlu dikonfirmasi tim riset** apakah preferensinya berbeda
  (mis. hanya salah satu komponen yang menanggung floor). SoT sendiri tidak
  eksplisit membahas kasus ini.

---

## Fase 3 — Ekologi Engine

> **[SUPERSEDED]** Section di bawah ini mendeskripsikan basis Ekologi Engine sebelum Catatan Finalisasi poin 12 `FINAL_BANGET.md`. Basis final saat ini adalah `Cost_labor_base` murni, bukan `C_labor_base_tending`.

**Rujukan SoT:** Catatan Finalisasi poin 10; Tabel 2.2 Ekologi Engine.

**Perubahan kode:**
- `app/engines/impact_engine.py` — `compute_ecology_weed(c_labor_base_tending, d, p_over)`.
  Basis berganti dari `Cost_labor_total` (SALAH) menjadi
  `C_labor_base_tending` (BENAR, tanpa `C_weed_hired`).
- `app/services/simulation_service.py` — panggil dengan
  `labor["Cost_labor_base_tending"]`.

**DoD tercapai:**
- Test `test_valuation_weed_eco_basis_excludes_weed_hired` —
  `V_weed_eco` dihitung hanya dari base+tending.
- Test `test_valuation_weed_eco_ignores_extra_weed_hired` — konfirmasi
  salah-basis akan memberi hasil lebih tinggi; dengan basis benar, hasil
  identik terlepas dari `C_weed_hired`.

**Hubungi Gap:** #11.

---

## Fase 4 — API Additive + Deprecation

**Rujukan SoT:** keputusan #2 (additive, deprecate jangan breaking).

**Perubahan kode:**
- `app/schemas/dss.py` — response `/dss/simulate` ditambah field:
  `D_panen_gabah`, `Cost_labor_base`, `Cost_labor_weed_hired`,
  `Cost_labor_tending`, `Cost_infra_net`, `Cost_infra_cage`, `F_sys`.
- Options response: `RiceVarietyOption` punya field baru `hst_panen`
  (canonical) dan deprecated `hst_masuk`/`hst_heading`/`harvest_age_days`.
- `PlantingSystemOption` punya field baru `k_safe_are`, `F_sys` (canonical)
  dan deprecated `k_max_are`, `f_yield` (sinkron dengan canonical).
- `app/api/routes/dss.py` — deskripsi endpoint tidak lagi menyebut "grid
  search rekomendasi".
- `app/main.py` — deskripsi app memisahkan DSS Core (SoT) vs Optimizer
  (luar cakupan).

**DoD tercapai:**
- OpenAPI diff: field baru muncul, field lama deprecated masih ada.
- Test `test_options_include_deprecated_aliases` — deprecated alias
  `f_yield`, `hst_masuk`, `harvest_age_days`, `k_max_are` tetap sinkron
  dengan canonical.
- Test `test_dss_simulate_response_has_no_optimizer_fields` — tidak ada
  field optimizer yang bocor ke `/dss/simulate`.

**Hubungi Gap:** #2, #7, #19.

---

## Fase 5 — DB History (Kolom Eksplisit)

**Rujukan SoT:** keputusan #3 (kolom eksplisit sesuai Tabel 2.3; legacy
dipertahankan dengan `schema_version`).

**Perubahan kode:**
- `app/core/database.py` — `HISTORY_V2_COLUMNS` (27 kolom eksplisit)
  ditambahkan via `ALTER TABLE` saat `initialize_database()`. Kolom
  `schema_version INTEGER NOT NULL DEFAULT 1`.
- `app/domain/models.py`:
  - `SimulationHistory` (v2) — dataclass dengan field eksplisit untuk
    semua kategori output Tabel 2.3 (agronomi, yield, revenue, cost
    detail, profit).
  - `SimulationHistoryLegacy` (v1) — dataclass lama untuk read-only audit.
- `app/repositories/history_repository.py`:
  - `create_v2(...)` — INSERT eksplisit ke kolom baru dengan
    `schema_version=2`.
  - `_to_model(row)` — mengembalikan `SimulationHistory` (v2) atau
    `SimulationHistoryLegacy` (v1) tergantung `schema_version`.
- `app/schemas/dss.py` — `HistoryListItem` dan `HistoryDetailResponse`
  (baru) memakai field eksplisit.

**DoD tercapai:**
- Baris baru ditulis ke kolom eksplisit dengan `schema_version=2`.
- Baris lama tetap terbaca sebagai legacy (read-only).
- `test_no_alpha_local_in_DSSConstants` & `test_no_alpha_local_in_seed_constants`
  mengunci Fase 6.

**Hubungi Gap:** #17.

---

## Fase 6 — Cleanup Artefak Generasi A

**Rujukan SoT:** Bagian 1.4 prompt scan (DEPRECATED — HAPUS PENUH).

**Perubahan kode:**
- `app/domain/models.py`:
  - Hapus field `alpha_local`, `kappa_n`, `kappa_p`, `kappa_k`,
    `phosphate_price_rp_per_kg`, `conventional_rice_price_rp_per_kg`,
    `conventional_yield_kg_per_ha` dari `DSSConstants`.
- `app/data/seed.py`:
  - Hapus nilai `alpha_local=0.643`, `kappa_n/p/k=0.049/0.072/0.032`,
    `phosphate_price_rp_per_kg=2700` dari `DSS_CONSTANTS`.
  - Tandai `kappa_n/p/k_reference`, `conventional_rice_price`, `conventional_yield`
    ParameterMetadata sebagai `status="deprecated"`.
  - Ganti `alpha_local` metadata dengan `alpha_local_legacy` deprecated.
- `x0`, `p_gabah_konv` — grep scan: tidak ditemukan di codebase aktif.
  Tidak ada perubahan.

**DoD tercapai:**
- `grep -E "alpha_local|0\.643|kappa_n|kappa_p|kappa_k|0\.049|0\.072|0\.032|phosphate_price|conventional_"` di codepath DSS-core → 0 hit (kecuali komentar deprecated).

**Hubungi Gap:** #19.

---

## Fase 7 — Test Suite Deterministik

**Perubahan kode:**
- `tests/test_formula_engine.py` — 35 test deterministik baru.
- `tests/test_api.py` — 9 test API end-to-end.
- `tests/test_penalty_rate.py` — 7 test edge case (floor infra, density
  extremes, dll).
- `tests/conftest.py` — tidak diubah.

**DoD tercapai:** 50/50 test passed.

Cakupan minimum:
- Age piecewise (3 test)
- Density over/under/cap (4 test)
- `lambda_eff` (2 test)
- **Tegel penalti 0.95** (2 test — formula + API)
- `HST_panen` 99/112 + `D_panen_gabah` (3 test)
- `C_weed_hired` formula + breakdown (3 test)
- `V_weed_eco` basis (regresi non-double-count) (2 test)
- Floor infra proporsional (aktif & tidak aktif & 50/50) (4 test)
- HET pupuk (1 test)
- Guardrail `Cost_feed`/`Cost_infra` total (2 test)
- Endpoint optimizer terisolasi (2 test)
- Field deprecated tetap ada & additive (1 test)
- Fase 0/6 cleanup (4 test)

**Hubungi Gap:** #21.

---

## Fase 8 — Dokumentasi & Rilis

**Perubahan kode:**
- `README.md` — pointer eksplisit ke `_terbaru` sebagai rujukan tunggal;
  optimizer dipisah sebagai fitur produk mandiri di luar SoT.
- `CHANGELOG.md` (file ini) — pemetaan tiap fase ke Gap Analysis.
- `postman/*` — perlu update manual oleh owner (di luar scope auto).

---

## Daftar Open Questions (masih menunggu konfirmasi manusia)

1. **Edge case floor infra `raw_net + raw_cage == 0`** (A=J=0). Default
   sementara: split 50/50 dari floor. **Konfirmasi tim riset** apakah
   preferensinya berbeda.
2. **Perubahan `D_masuk_bebek` dari `+20` ke `+21`** mengubah tanggal
   reminder user-facing. **Konfirmasi product owner** sebelum merge ke
   production jika sudah ada user aktif.
3. **Requiredness `p_duck_buy_manual`** — saat ini selalu optional. SoT
   mensyaratkan required hanya jika `U_duck < 14` atau `> 21`. **Konfirmasi
   product owner** sebelum menegakkan validator kondisional, karena
   ada/dependensi UI/consumer lain.
4. **Strategi API versioning** — saat ini additive di v1. Apakah perlu
   v2 endpoint terpisah?
5. **DB history shape** — saat ini `SimulationHistory` (v2) belum
   dipanggil oleh service `simulate()`. Apakah perlu auto-persist di
   setiap call (butuh refactor service) atau biarkan eksplisit via
   endpoint terpisah?
6. **Postman collection** — belum diupdate otomatis ke field baru
   (deprecated). Butuh regenerasi manual.
7. **Optimizer stub `/recommend`** — saat ini mengembalikan data dummy.
   Butuh implementasi legacy grid-search atau di-nonaktifkan?

---

## Risiko Breaking Change untuk Consumer API/Frontend

| Risiko | Tipe | Mitigasi |
|---|---|---|
| Field baru `D_panen_gabah`, `Cost_labor_*`, `Cost_infra_net/cage`, `F_sys` muncul | Additive (aman) | Frontend boleh abaikan field baru |
| `Tegel` yield turun (F_sys 1.39→0.95) | **Breaking behavior** | Butuh komunikasi ke product |
| `HST_panen` Sertani/Inpari berubah | **Breaking behavior** | Reminder tanggal bergeser |
| `D_masuk_bebek` dari `+20` ke `+21` | **Breaking behavior** | Konfirmasi product owner |
| Field lama `f_yield`, `hst_masuk`, `hst_heading` deprecated | Additive (aman) | Sunset di rilis vNext |
| `Cost_infra` total tidak berubah | Stabil | Guardrail test |
| `Cost_feed` formula tidak berubah | Stabil | Guardrail test |
| Endpoint optimizer pindah ke `/api/v1/optimizer/recommend` | **Breaking route** | Dokumentasi perlu diumumkan |
| `DSSSimulationResponse` kehilangan `k_max_are`, `f_yield` (jika frontend pernah membaca) | **Breaking schema** | Tinggalkan sebagai alias deprecated di `PlantingSystemOption` |
