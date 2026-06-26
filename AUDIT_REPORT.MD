# AUDIT_REPORT

## 1. Backend vs Frontend Sync

### 1.1 Ringkasan

Secara umum frontend `C:\My Project\rice-duck` sudah mengikuti kontrak endpoint backend runtime `C:\My Project\rice-duck-be\app` untuk alur utama:
- auth register/login/me
- load opsi DSS
- simulasi DSS
- list/detail/delete history

Namun belum 100% sinkron pada beberapa detail penting: validasi form, pemetaan field rekomendasi, label status, dan sebagian perilaku UI terhadap response backend.

### 1.2 Endpoint dan flow utama

| Area | Backend runtime | Frontend | Status | Bukti file |
|---|---|---|---|---|
| Health | `GET /health` | Tidak dipakai frontend | Tidak masalah | `app/api/routes/health.py` |
| Auth register | `POST /api/v1/auth/register` | Dipakai | Sinkron | `app/api/routes/auth.py`, `src/services/auth.ts` |
| Auth login | `POST /api/v1/auth/login` | Dipakai | Sinkron | `app/api/routes/auth.py`, `src/services/auth.ts` |
| Auth me | `GET /api/v1/auth/me` | Dipakai | Sinkron | `app/api/routes/auth.py`, `src/services/auth.ts`, `src/context/AuthContext.tsx` |
| DSS options | `GET /api/v1/dss/options` | Dipakai | Sinkron | `app/api/routes/dss.py`, `src/services/dss.ts`, `src/pages/SimulasiPage.tsx` |
| DSS simulate | `POST /api/v1/dss/simulate` | Dipakai | Sinkron secara path dan shape dasar | `app/api/routes/dss.py`, `src/services/dss.ts` |
| Histories list | `GET /api/v1/dss/histories` | Dipakai | Sinkron | `app/api/routes/dss.py`, `src/services/dss.ts`, `src/pages/HistoryPage.tsx` |
| History detail | `GET /api/v1/dss/histories/{history_id}` | Dipakai | Sinkron | `app/api/routes/dss.py`, `src/services/dss.ts`, `src/pages/HistoryPage.tsx` |
| History delete | `DELETE /api/v1/dss/histories/{history_id}` | Dipakai | Sinkron | `app/api/routes/dss.py`, `src/services/dss.ts`, `src/pages/HistoryPage.tsx` |

#### Bukti flow sinkron
- Prefix backend berasal dari `app/main.py` dan `app/api/router.py`.
- Frontend menyusun base URL dari `src/config/api.ts` lalu memanggil path yang sama di `src/services/auth.ts` dan `src/services/dss.ts`.
- Simulasi memakai token optional di frontend dan backend juga menerima optional bearer pada `POST /api/v1/dss/simulate`.
- History di frontend hanya dipanggil setelah auth, sesuai backend yang mensyaratkan bearer token.

### 1.3 Payload request

#### 1.3.1 Auth register/login

Backend:
- `app/schemas/auth.py`
- register: `name`, `email`, `password` dengan password minimum 8
- login: `email`, `password`

Frontend:
- `src/components/AuthModal.tsx`
- `src/services/auth.ts`

Status:
- payload auth sinkron secara field
- frontend sudah normalisasi email dengan `trim().toLowerCase()`
- backend juga melakukan normalisasi tambahan

Temuan:

| Lokasi | Masalah | Dampak | Rekomendasi singkat |
|---|---|---|---|
| `src/components/AuthModal.tsx` | Placeholder password register masih menulis `Min. 6 karakter`, padahal frontend validation dan backend schema sama-sama minimum 8 | Pengguna mendapat petunjuk salah | Samakan teks UI dengan kontrak backend |

#### 1.3.2 Payload simulasi DSS

Backend schema `app/schemas/dss.py` menerima:
```json
{
  "duck_count": 28,
  "land_area_are": 7,
  "planting_date": "2026-06-01",
  "rice_variety": "sertani",
  "planting_system": "jajar_legowo",
  "duck_age_days": 30
}
```

Frontend mengirim field yang sama dari `src/pages/SimulasiPage.tsx` melalui `src/services/dss.ts`.

Status:
- Nama field sinkron.
- Contoh default frontend sinkron dengan contoh payload backend.

Temuan:

| Lokasi | Masalah | Dampak | Rekomendasi singkat |
|---|---|---|---|
| `src/pages/SimulasiPage.tsx` vs `app/schemas/dss.py` | Input HTML `land_area_are` memakai `min=0`, backend butuh `gt=0` | User bisa submit `0`, lalu kena HTTP 422 | Samakan constraint UI dengan backend (`min > 0`) |
| `src/pages/SimulasiPage.tsx` vs `app/schemas/dss.py` | Input HTML `duck_age_days` memakai `min=0`, backend butuh `gt=0` | User bisa submit `0`, lalu kena HTTP 422 | Samakan constraint UI dengan backend (`min > 0`) |
| `src/pages/SimulasiPage.tsx` | Validasi lokal fokus pada nilai kosong/null, belum memeriksa batas backend | Error baru diketahui setelah request ke backend | Tambah validasi frontend mengikuti schema backend |

### 1.4 Structure response dan field mapping

#### 1.4.1 Root response simulasi

Backend `app/schemas/dss.py` mengembalikan blok utama:
- `history_id`
- `input`
- `lookup`
- `actual_scenario`
- `optimality_assessment`
- `recommended_scenario`
- `comparison`
- `risk`
- `trace`
- `notes`
- `economics`
- `ecology`
- `environment`
- `validation`
- `data_readiness`

Frontend type `src/types/api.ts` dan render `src/pages/SimulasiPage.tsx` sudah mengikuti shape ini.

Status:
- Sinkron untuk blok utama.
- Null handling dasar juga sudah ada.

#### 1.4.2 Mapping `actual_scenario`

Frontend menampilkan:
- `duck_count`
- `land_area_are`
- `density_are`
- `duration_days`
- `release_date`
- `pull_date`
- `predicted_yield.*`
- `risk_status`
- `penalty_rate`

Backend menyediakan field tersebut.

Status:
- Sinkron.

#### 1.4.3 Mapping `recommended_scenario`

Temuan penting:

| Lokasi | Masalah | Dampak | Rekomendasi singkat |
|---|---|---|---|
| `src/pages/SimulasiPage.tsx` | Komponen kartu skenario selalu membaca `land_area_are` seperti `ActualScenario`, padahal `RecommendedScenario` backend tidak punya field itu | UI rekomendasi menampilkan `undefined are` | Untuk rekomendasi, ambil luas lahan dari `input.land_area_are` atau tambahkan mapping khusus |

Penjelasan:
- Backend `app/schemas/dss.py` untuk `RecommendedScenario` memang berisi `recommended_duck_count`, `recommended_density_are`, `recommended_duration_days`, tanggal rekomendasi, yield, risk, reasoning.
- Frontend mengasumsikan bentuk sama penuh dengan `ActualScenario` pada bagian luas lahan.

### 1.5 Null handling

#### Sudah sinkron
- `src/pages/SimulasiPage.tsx` memakai formatter angka/rupiah yang menampilkan fallback saat nilai null.
- Untuk blok environment, frontend sudah membedakan null biasa vs `formula_available=true` dan `numeric_ready=false`.
- Ini sejalan dengan backend yang mengembalikan formula environment aktif tetapi data numerik bisa belum tersedia.

#### Temuan

| Lokasi | Masalah | Dampak | Rekomendasi singkat |
|---|---|---|---|
| `src/pages/SimulasiPage.tsx` | Error handling simulasi memakai `err?.error?.message`, sedangkan pola auth memakai `apiErr?.message` | Pesan error backend bisa hilang dan jatuh ke pesan generik | Samakan pembacaan objek error dengan helper `ApiError` |

### 1.6 Status, sumber data, environment, trace, notes

#### Status/sumber data
- Backend mengirim banyak status runtime seperti `ready`, `partial`, `estimation_only`, `literature-uncalibrated`, `local-estimate`.
- Frontend punya dua peta label: `STATUS_LABEL` dan `DATA_READINESS_LABEL`.

Temuan:

| Lokasi | Masalah | Dampak | Rekomendasi singkat |
|---|---|---|---|
| `src/pages/SimulasiPage.tsx` atau `src/types/api.ts` | Label frontend punya key `estimation-only`, sedangkan backend mengirim `estimation_only` | Badge status bisa tampil mentah sebagai `estimation_only` | Samakan enum/key status dengan backend runtime |

#### Environment
- Backend `app/services/simulation_service.py` dan engine environment mengembalikan field numerik null jika flux CH4/N2O belum tersedia, tetapi `formula_available=true`.
- Frontend sudah menampilkan ini sebagai “Rumus tersedia, data belum lengkap”.

Status:
- Sinkron secara perilaku.

#### Trace dan notes
- Backend mengembalikan `trace` dan `notes`.
- Frontend menampilkan `notes` dan menampilkan `trace` sebagai JSON mentah di section “Trace Akademik”.

Status:
- Sinkron secara teknis.

Catatan:
- `trace` besar akan membebani UI, tetapi bukan mismatch kontrak.

### 1.7 History

#### Sudah sinkron
- Backend list history: ringkasan item.
- Backend detail history: full `DSSSimulationResponse` dengan re-simulation dari input tersimpan.
- Frontend `src/pages/HistoryPage.tsx` mengikuti pola itu.
- Delete history juga sinkron.

#### Temuan

| Lokasi | Masalah | Dampak | Rekomendasi singkat |
|---|---|---|---|
| `src/pages/HistoryPage.tsx` | Tiga kartu ringkasan history (`Rata-rata Yield`, `Varietas Terpopuler`, `Status Dominan`) masih placeholder `—` | UI terkesan punya insight tambahan padahal belum dihitung | Sembunyikan sampai ada data nyata atau hitung dari history |
| `src/pages/HistoryPage.tsx` | Error detail history menyatukan 401/404/dll menjadi pesan umum | Sulit membedakan masalah auth vs data hilang | Bedakan pesan menurut status backend |

### 1.8 Recommendation dan optimality di UI

#### Sudah sinkron
- Frontend hanya menampilkan rekomendasi jika `!is_optimal && recommended_scenario`.
- Ini cocok dengan backend yang dapat mengembalikan `recommended_scenario: null` saat dianggap optimal.

#### Catatan penting
- Sinkron secara struktur, tetapi makna `is_optimal` dari backend saat ini berbeda dengan sebagian dokumentasi akademik/README. Ini dibahas di Bagian 2.
- Artinya frontend mengikuti backend runtime, tetapi bisa tidak sesuai ekspektasi paper/dokumen.

### 1.9 Dead UI / dead code / route yang tidak relevan dengan backend

| Lokasi | Temuan | Dampak | Rekomendasi singkat |
|---|---|---|---|
| `src/pages/SimulasiPage.tsx` | `comparison` dari backend ada di type tetapi praktis belum dipakai di UI | Data backend tidak termanfaatkan | Putuskan apakah akan ditampilkan atau dihapus dari ekspektasi UI |
| `src/pages/HistoryPage.tsx` | `setPage` diterima tetapi tidak dipakai | Kode mati | Bersihkan saat refactor nanti |
| `src/components/Topbar.tsx` | Handler export PDF tidak aktif karena tombol disable | Fitur tampak setengah jadi | Aktifkan saat siap atau hapus |
| `src/components/Topbar.tsx` | Typo `aia-label` dan ada karakter backtick liar | Aksesibilitas dan tampilan kecil terganggu | Perbaiki label/markup |

### 1.10 Kesimpulan bagian 1

Frontend sudah mengikuti backend runtime untuk alur inti dan struktur response besar. Mismatch utama bukan pada endpoint, melainkan pada detail UX dan pemetaan field:
- validasi form belum seketat backend
- kartu rekomendasi salah memetakan luas lahan
- sebagian status label tidak cocok
- placeholder UI dan beberapa pesan error masih lemah

---

## 2. Backend/System vs Docs Source of Truth

### 2.1 Ringkasan

Backend runtime saat ini adalah source of truth operasional, tetapi belum sepenuhnya konsisten dengan source of truth akademik lokal di folder `docs`:
- `docs/data_collection_padi_bebek.md`
- `docs/Model Matematika Data Collection DSS Padi Bebek Rev 2.md`
- `docs/Kumpulan Variabel, Rumus, dan Data dari Artikel Referensi.md`

Sebagian rumus inti sudah masuk runtime, tetapi ada drift pada:
- nilai parameter
- status klaim data
- narasi note/metadata
- optimality logic
- objective recommendation
- data availability ekonomi dan emisi

### 2.2 Rumus inti yang sudah selaras secara umum

Rumus inti yang benar-benar ada di runtime:
- konversi are ke ha
- kepadatan `density_are`, `density_ha`
- durasi dari `HST_masuk` ke `HST_heading`
- survival `lambda`
- model kotoran bebek per fase
- yield berbasis density dan duration
- penalty ketika density melebihi `K_max`
- risk status
- N/P/K tanah dari skala kotoran
- nilai ekologi parsial
- REY formula bersyarat
- environment formula bersyarat
- optimizer rekomendasi berbasis enumerasi kandidat

Lokasi code utama:
- `app/engines/formula_engine.py`
- `app/engines/impact_engine.py`
- `app/services/simulation_service.py`
- `app/data/seed.py`

Status:
- Ada fondasi rumus akademik di runtime.
- Masalah utama ada pada kalibrasi, nilai default, dan narasi status.

### 2.3 Temuan mismatch utama terhadap docs

#### 2.3.1 `q_feed` fallback tidak konsisten

| Item | Lokasi code | Lokasi/konteks docs | Perbedaan | Dampak ke DSS/paper | Rekomendasi tindak lanjut |
|---|---|---|---|---|---|
| `q_feed` fallback | `app/data/seed.py`, `app/services/simulation_service.py` | `README.md`, `docs/Model Matematika Data Collection DSS Padi Bebek Rev 2.md` | Runtime hitung memakai `0.10`; sebagian note runtime menulis `0.15`; model doc juga memuat rentang `0.12-0.225` | Penjelasan output ekonomi bisa salah walau hitungannya pakai nilai lain | Verifikasi nilai rujukan final, lalu samakan code comment/note/README/paper note |

Penjelasan singkat:
- Ini mismatch paling penting karena bukan hanya beda narasi, tetapi juga bisa membingungkan pembaca audit apakah runtime memakai 0.10, 0.12, atau 0.15.

#### 2.3.2 `K_max` untuk sistem Tegel tidak seragam

| Item | Lokasi code | Lokasi/konteks docs | Perbedaan | Dampak ke DSS/paper | Rekomendasi tindak lanjut |
|---|---|---|---|---|---|
| `K_max_are` Tegel | `app/data/seed.py` | `docs/Model Matematika Data Collection DSS Padi Bebek Rev 2.md`, `docs/data_collection_padi_bebek.md` | Runtime pakai `2.5`; model doc memuat `2`; data collection memuat rentang `2-3` | Risk dan rekomendasi untuk Tegel bisa dinilai berbeda dari dokumen | Tetapkan apakah runtime memakai midpoint desain atau angka lokal final; jelaskan eksplisit di report ilmiah |

#### 2.3.3 Status hara tanah bertentangan dengan runtime

| Item | Lokasi code | Lokasi/konteks docs | Perbedaan | Dampak ke DSS/paper | Rekomendasi tindak lanjut |
|---|---|---|---|---|---|
| N/P/K tanah | `app/data/seed.py`, `app/engines/impact_engine.py`, `app/services/simulation_service.py` | Note/assumption runtime dan konteks docs soal kappa lokal | Runtime punya `kappa_n`, `kappa_p`, `kappa_k` dan menghitung nilai numerik; sebagian note menyatakan hara belum dihitung/null | User dan reviewer bisa mengira sistem tidak menghitung hara padahal output ada | Pisahkan jelas antara “nilai dihitung dari referensi” vs “belum terkalibrasi lokal” |

#### 2.3.4 Metadata pestisida/herbisida bertentangan

| Item | Lokasi code | Lokasi/konteks docs | Perbedaan | Dampak ke DSS/paper | Rekomendasi tindak lanjut |
|---|---|---|---|---|---|
| `V_eco2` / pesticide reduction | `app/engines/impact_engine.py`, metadata di service/lookup | Konteks doc ekologi dan metadata runtime | Runtime menghitung `V_eco2`, tetapi metadata tertentu menyebut tidak dihitung | Trace metodologi jadi membingungkan | Rapikan metadata agar sesuai perilaku runtime |

#### 2.3.5 Logic optimality berbeda dari dokumen

| Item | Lokasi code | Lokasi/konteks docs | Perbedaan | Dampak ke DSS/paper | Rekomendasi tindak lanjut |
|---|---|---|---|---|---|
| `is_optimal` dan threshold optimality | `app/services/simulation_service.py` | `README.md` dan konteks model DSS | Dokumen menjelaskan threshold gap density/yield/profit; runtime saat ini memakai exact match terhadap skenario terbaik | Kesimpulan “optimal” di UI/backend dapat berbeda dari naskah/paper | Perlu verifikasi lanjutan: apakah runtime sengaja diubah atau docs belum diperbarui |

Penjelasan singkat:
- Ini bukan bug kecil. Ini mengubah arti keluaran DSS karena “optimal” dalam dokumen berbasis threshold toleransi, sedangkan runtime sekarang berbasis kecocokan eksak terhadap solusi terbaik hasil search.

#### 2.3.6 Objective recommendation berbeda dari docs

| Item | Lokasi code | Lokasi/konteks docs | Perbedaan | Dampak ke DSS/paper | Rekomendasi tindak lanjut |
|---|---|---|---|---|---|
| Fungsi skor rekomendasi | `app/services/simulation_service.py` | `README.md`, konteks optimizer di docs | Docs menyiratkan ekonomi/ekologi hanya ikut jika data lengkap; runtime hampir selalu memasukkan komponen ekologi jika nilai parsial tersedia | Saran rekomendasi bisa lebih “ecology-driven” dari narasi dokumen | Tegaskan objective runtime final di laporan akademik dan UI |

#### 2.3.7 Batas risk `SAFE` pada tepat `0.8 * K_max`

| Item | Lokasi code | Lokasi/konteks docs | Perbedaan | Dampak ke DSS/paper | Rekomendasi tindak lanjut |
|---|---|---|---|---|---|
| Boundary SAFE/LOW | `app/engines/formula_engine.py` | `README.md` / penjelasan threshold risk | Docs menyatakan `0.8 × K_max` masuk SAFE; runtime memakai `>` sehingga nilai tepat batas masuk LOW | Kasus batas dapat menghasilkan klasifikasi berbeda | Putuskan boundary final dan dokumentasikan konsisten |

#### 2.3.8 Data emisi belum tersedia walau rumus ada

| Item | Lokasi code | Lokasi/konteks docs | Perbedaan | Dampak ke DSS/paper | Rekomendasi tindak lanjut |
|---|---|---|---|---|---|
| CH4/N2O seasonal flux | `app/data/seed.py`, `app/engines/impact_engine.py` | Docs environment/emission | Docs menyiapkan formula; runtime tidak punya angka flux aktif sehingga hasil numerik null | Section environment tampil “rumus tersedia, data belum lengkap” terus-menerus | Pertahankan status apa adanya, tetapi jelaskan jelas bahwa ini belum operasional numerik |

### 2.4 Variabel/parameter yang ada di docs tetapi belum masuk sistem penuh

Contoh yang muncul di docs namun belum menjadi input runtime utama:
- varietas tambahan seperti Cigelis/Cegelis, Ciherang, beras merah
- sistem tanam seperti SRI, double transplant
- kondisi air/topografi
- biaya atau jenis pakan sebagai input eksplisit
- biaya pestisida/herbisida spesifik
- beberapa variabel operasional lapangan lain

Dampak:
- Runtime saat ini menyederhanakan domain masalah ke subset variabel yang lebih sempit.
- Ini sah untuk sistem operasional sementara, tetapi harus dibedakan dari cakupan penuh dokumen akademik.

### 2.5 Satuan dan konversi

Status:
- Runtime konsisten memakai `land_area_are` sebagai input utama.
- `ha` diturunkan dari `are / 100`.
- `density_ha` adalah hasil turunan dari `density_are * 100`.
- `kg_per_are` diturunkan dari `kg_per_ha / 100`.

Kesimpulan:
- Tidak ada mismatch satuan besar yang terlihat pada runtime.
- Yang perlu dijaga adalah penjelasan ke pengguna bahwa density literatur dan density input lapangan adalah turunan konversi, bukan dua input berbeda.

### 2.6 Status klaim data

Runtime memakai beberapa label status penting:
- `ready`
- `partial`
- `estimation_only`
- `literature-uncalibrated`
- `local-estimate`
- placeholder/null untuk data belum ada

Temuan:
- Beberapa klaim status di notes/metadata tidak serapi data runtime nyata.
- Khusus ekonomi, ekologi, hara, dan environment, perlu dibedakan antara:
  1. rumus tersedia
  2. angka referensi tersedia
  3. kalibrasi lokal tersedia
  4. angka final operasional tersedia

### 2.7 Kesimpulan bagian 2

Backend saat ini sudah mengimplementasikan inti DSS, tetapi belum 100% sejalan dengan source of truth akademik lokal. Gap terpenting:
- `q_feed`
- `K_max` Tegel
- status hara tanah
- metadata pestisida/herbisida
- definisi optimality
- objective recommendation
- emisi yang masih formula-only

Sebagian butuh klarifikasi akademik, bukan sekadar perbaikan code.

---

## 3. Dependency Output <- Proses <- Input dan Bagian yang Tidak Berpengaruh

### 3.1 Ringkasan

Bagian ini menelusuri alur sebab-akibat runtime. Fokusnya: output akhir mana dipengaruhi input apa, lewat proses/rumus apa, dan komponen mana yang ada di sistem/docs tetapi belum berdampak nyata.

### 3.2 Predicted yield

Pola dependency:

`predicted_yield <- yield base quadratic + temporal response + density penalty + system factor <- duck_count, land_area_are, rice_variety(HST), planting_system(K_max,f_yield), alpha_local, penalty constants`

Uraian:
- `duck_count` dan `land_area_are` membentuk `density_are` lalu `density_ha`.
- `rice_variety` menentukan `HST_masuk` dan `HST_heading`, lalu menghasilkan `duration_days`.
- `planting_system` memberi `K_max_are` dan `f_yield`.
- `alpha_local` memberi faktor kalibrasi lokal global.
- Jika `density_are > K_max_are`, hasil terkena `penalty_rate`.

Field output yang terdampak:
- `predicted_yield.kg_per_ha`
- `predicted_yield.kg_per_are`
- `predicted_yield.estimated_total_kg`
- `predicted_yield.ton_per_ha`
- `x_base_*`, `x_penalized_*`

Yang tidak berpengaruh ke yield saat ini:
- `duck_age_days`: masuk payload, tetapi tidak masuk formula yield.
- `feed_price_rp_per_kg`: hanya ekonomi.
- `rice_duck_price_rp_per_kg`: hanya ekonomi/REY.
- `soil_nutrients`: output ekologi, bukan input balik ke yield.

Catatan penting:
- `duck_age_days` tampil sebagai input penting di UI, tetapi backend saat ini belum memakai umur bebek untuk mengubah prediksi yield. Dampaknya: jangan menafsirkan output seolah umur bebek sudah mengubah hasil agronomi.

### 3.3 Actual scenario

Pola dependency:

`actual_scenario <- transform input + lookup varietas/sistem + formula agronomi dasar <- payload simulasi + seed lookup + constants`

Komponen utama:
- area: `land_area_are -> land_area_ha`
- density: `duck_count / land_area_are`
- dates: `planting_date + HST_masuk/HST_heading`
- duration: `HST_heading - HST_masuk`
- survival: `duck_count * survival_lambda`
- dung: piecewise menurut `duration_days`
- effective duration: `duration * grazing_hours/baseline_hours`
- yield: bagian 3.2
- risk status: bagian 3.5
- REY: jika parameter ekonomi tersedia

Yang tidak berpengaruh ke `actual_scenario` utama:
- data emisi belum memberi angka numerik
- `limited_test_max_are` hanya metadata opsi
- `recommended_density_max_are` tidak mengubah actual scenario

### 3.4 Recommended scenario

Pola dependency:

`recommended_scenario <- brute-force candidate search + scenario evaluation + scoring <- land_area_are, rice_variety(HST), planting_system(K_max,min density,f_yield), yield engine, risk engine, economics availability, ecology availability`

Uraian:
- Rentang jumlah bebek dibentuk dari `recommended_density_min_are * land_area_are` hingga `K_max_are * land_area_are`.
- Durasi kandidat dari `1` sampai `min(duration varietas, t_max_eff_days)`.
- Tiap kandidat dievaluasi dengan formula yield, risk, ecology, dan ekonomi bila numerik tersedia.
- Skor memakai `normalized_yield - risk_penalty`, lalu menambah profit jika ada, dan menambah ecology bila tersedia.

Yang tidak berpengaruh atau belum penuh:
- `recommended_density_max_are` ada di seed sistem tanam, tetapi pencarian maksimum saat ini memakai `K_max_are`, bukan field ini.
- `limited_test_max_are` tidak membatasi optimizer.
- `duck_age_days` tidak mempengaruhi search.
- profit sering tidak ikut karena `net_profit_rp` null saat data harga belum lengkap.

Dampak:
- Recommendation sangat dipengaruhi yield, risk, dan hampir selalu ecology.
- Batas praktis rekomendasi yang ada di metadata sistem tanam belum benar-benar dipakai penuh.

### 3.5 Risk

Pola dependency:

`risk <- density threshold check + duration threshold check <- duck_count, land_area_are, rice_variety(HST), planting_system(K_max)`

Komponen:
- `density_are`
- `duration_days`
- `K_max_are`
- batas fase maksimum dari varietas atau aturan runtime

Output terdampak:
- `actual_scenario.risk_status`
- `recommended_scenario.risk_status`
- blok `risk`
- penalty dalam optimizer

Yang tidak berpengaruh:
- `duck_age_days`
- harga ekonomi
- parameter emisi

### 3.6 Economics

Pola dependency:

`economics <- rice revenue + duck revenue/cost + feed cost + infrastructure + ecological value <- predicted_yield, surviving_ducks, duck_count, effective_duration_days, q_feed, feed saving, prices/costs, ecology outputs`

Alur lebih rinci:
- `rice_revenue_rp <- predicted_yield.kg_per_are * land_area_are * rice_duck_price_rp_per_kg`
- `duck_revenue_rp <- surviving_ducks * duck_sale_price_rp_per_duck`
- `duck_purchase_cost_rp <- duck_count * duck_buy_price_rp_per_duck`
- `feed_cost_rp <- duck_count * q_feed * effective_duration_days * feed_price * (1 - feed saving)`
- `net_profit_rp <- rice_revenue + duck_net_value + ecological_value - infrastructure - additional_cost`

Parameter yang sekarang memblokir output ekonomi penuh:
- `rice_duck_price_rp_per_kg = None`
- `feed_price_rp_per_kg = None`
- `conventional_yield_kg_per_ha = None`

Akibat ke output:
- `duck_revenue_rp` ada
- `duck_purchase_cost_rp` ada
- `infrastructure` ada
- `feed_cost_rp` null
- `rice_revenue_rp` null
- `net_profit_rp` null
- `REY` null
- `conventional_rice_revenue` null

Yang hanya placeholder atau belum berdampak penuh:
- `maintenance_cost` placeholder `0.0`
- `additional_cost` placeholder `0.0`
- `feed_greedy_kg_per_duck_day` null, sehingga penalty feed tidak aktif

### 3.7 Ecology

Pola dependency:

`ecology <- fertilizer saving + pesticide/herbicide saving + weeding saving + nutrient estimate <- duration_days, density_are, density_ha, land_area_are, land_area_ha, survival_lambda, fertilizer prices, weeding cost, kappa N/P/K, K_max`

Uraian:
- fertilizer saving memakai durasi, density, lambda, area, dan harga pupuk
- pesticide/herbicide saving memakai fungsi sigmoid pada density per ha dan area
- weeding saving memakai rasio `density_are / K_max_are`
- hara tanah memakai skala kotoran dan `kappa_n/p/k`

Yang belum berpengaruh balik ke sistem lain:
- nilai N/P/K tanah saat ini tidak dipakai balik ke yield, risk, atau recommendation kecuali sebagai bagian output ecology/trace

Dampak:
- ecology sudah numerik walau banyak statusnya masih estimasi/literature-uncalibrated
- karena numeric tersedia, komponen ecology ikut mempengaruhi optimizer runtime saat ini

### 3.8 Environment

Pola dependency:

`environment <- CH4/N2O conversion + GWP + GHGI <- seasonal flux constants + predicted_yield`

Syarat numerik:
- butuh `seasonal_ch4_rice_duck_kg_per_ha`
- butuh `seasonal_n2o_kg_per_ha`
- untuk `ch4_reduction_pct` juga butuh flux konvensional

Status saat ini:
- rumus ada
- flags status ada
- data numerik seed belum ada
- hasil numerik tetap null

Dampak:
- Environment belum mempengaruhi keputusan numerik lain secara nyata.
- Lebih tepat disebut formula-ready, data-not-ready.

### 3.9 Data readiness

Pola dependency:

`data_readiness <- rule/status aggregation <- availability input lookup + completeness economics/ecology/environment + calibration status`

Makna:
- ini bukan rumus saintifik langsung, melainkan agregasi status kesiapan data backend

Yang mempengaruhi:
- apakah field ekonomi kritis ada
- apakah environment punya flux numerik
- apakah output masih estimasi/literature-based

Yang tidak mempengaruhi:
- `data_readiness` tidak mengubah yield atau recommendation secara langsung; ia hanya melabeli kualitas kesiapan data

### 3.10 Validation

Pola dependency:

`validation <- schema validation + business-range note <- payload input + lookup ranges + runtime assumptions`

Mempengaruhi:
- note/warning ke user
- bukan hasil hitung utama langsung

Contoh:
- `duck_age_days` dipakai di sini sebagai warning range, bukan sebagai faktor rumus output inti

### 3.11 Trace

Pola dependency:

`trace <- assembled explanation/metadata from formulas and statuses <- computed scenario + lookups + parameter metadata + notes`

Makna:
- trace membantu audit dan pelacakan akademik
- bukan penentu utama output baru

Yang hanya metadata/catatan:
- sebagian `PARAMETER_METADATA`
- note status sumber data
- label ketersediaan data

Catatan:
- beberapa metadata saat ini bertentangan dengan runtime nyata, jadi trace belum selalu bisa dianggap sumber kebenaran final tanpa verifikasi.

### 3.12 Notes

Pola dependency:

`notes <- rule-based explanatory messages <- missing parameter status + estimation status + validation status + recommendation status`

Makna:
- notes menjelaskan konteks
- bukan pengubah angka

Temuan penting:
- notes tertentu masih menyebut `q_feed=0.15`
- notes tertentu menyebut N/P/K belum dihitung walau runtime menghitungnya

Dampak:
- notes bisa tidak sinkron dengan hasil hitung aktual

### 3.13 History output

Pola dependency:

`history output <- saved input + saved snapshot fields + re-simulation detail <- authenticated user + simulate result + history repository`

Uraian:
- Saat simulasi dengan auth, backend menyimpan history.
- List history menampilkan ringkasan item.
- Detail history melakukan re-simulation berdasarkan input tersimpan, bukan sekadar menampilkan blob lama.

Dampak:
- Detail history mengikuti runtime formula terbaru.
- Jika formula berubah di backend, detail history lama bisa berubah hasilnya dibanding saat pertama disimpan.

Perlu verifikasi lanjutan:
- Ini mungkin sengaja agar history selalu mengikuti model terbaru, tetapi untuk kebutuhan audit ilmiah bisa menimbulkan pertanyaan soal reproduksibilitas hasil lama.

### 3.14 Bagian yang ada di sistem/docs tetapi tidak atau belum berpengaruh ke output

| Item | Status | Kenapa tidak berpengaruh | Dampak audit |
|---|---|---|---|
| `duck_age_days` | Ada di payload/input | Saat ini hanya dipakai untuk warning/validasi, belum masuk formula yield/risk/economics/ecology | Jangan framing UI seolah umur bebek mengubah prediksi |
| `minimum_density_are` | Ada di seed | Optimizer memakai `recommended_density_min_are`, bukan konstanta ini | Konstanta tampak aktif padahal tidak menentukan hasil |
| `recommended_density_max_are` | Ada di seed sistem tanam | Optimizer maksimum masih memakai `K_max_are` | Metadata batas rekomendasi belum benar-benar mengikat output |
| `limited_test_max_are` | Ada di lookup | Hanya ditampilkan/tersimpan sebagai metadata | Belum membatasi recommendation atau risk |
| `feed_greedy_kg_per_duck_day` | Ada sebagai field, nilainya null | Formula penalty feed dormant | Belum mengubah economics |
| `maintenance_cost` | Placeholder | Diisi `0.0`, belum mewakili data nyata | Net profit parsial dan optimistis |
| `additional_cost` | Placeholder | Diisi `0.0` | Net profit parsial |
| Banyak `PARAMETER_METADATA` | Metadata | Menjelaskan status/sumber, bukan kalkulasi | Berguna untuk trace, bukan angka |
| Variabel docs seperti topografi/kondisi air | Ada di docs | Belum dimodelkan di runtime | Ruang pengembangan, belum pengaruh hasil |
| Varietas/sistem tanam tambahan di docs | Ada di docs | Belum ada di seed runtime | Cakupan sistem lebih sempit dari dokumen |
| Emission formulas | Ada di code | Data flux belum tersedia | Output environment numerik belum hidup |

### 3.15 Kesimpulan bagian 3

Output agronomi inti sudah punya dependency runtime yang jelas. Bagian yang paling lemah atau belum berdampak penuh:
- `duck_age_days`
- placeholder biaya
- metadata batas rekomendasi yang belum dipakai optimizer
- komponen emisi yang masih formula-only
- sebagian notes/trace yang lebih bersifat naratif daripada sumber kebenaran numerik

---

## 4. Data Availability dan Validitas terhadap Source of Truth

### 4.1 Ringkasan

Status data runtime saat ini campuran antara:
- data input yang sudah operasional
- lookup lokal/estimasi
- parameter literatur
- placeholder biaya
- komponen formula yang siap tetapi data angkanya belum ada

Bagian ini tidak mengubah status sumber data. Bagian ini hanya memetakan apa yang sudah ada, belum ada, placeholder, ada di docs lokal, ada di literatur, atau benar-benar belum tersedia.

### 4.2 Data yang sudah ada di sistem dan dipakai runtime

| Item penting | Status runtime | Lokasi utama | Validitas terhadap source of truth | Catatan audit |
|---|---|---|---|---|
| `duck_count` | Input operasional | `app/schemas/dss.py` | Sesuai sistem dan docs sebagai input dasar | Dipakai langsung ke density, survival, economics |
| `land_area_are` | Input operasional | `app/schemas/dss.py` | Sesuai docs dan runtime | Menjadi basis hampir semua output |
| `planting_date` | Input operasional | `app/schemas/dss.py` | Sesuai docs | Dipakai untuk release/pull date |
| `rice_variety` (`sertani`,`inpari`) | Lookup operasional | `app/data/seed.py` | Ada dasar di docs, tetapi cakupan varietas belum lengkap | Dipakai ke HST dan duration |
| `planting_system` (`jajar_legowo`,`tegel`) | Lookup operasional | `app/data/seed.py` | Sesuai sebagian docs, tetapi cakupan sistem belum lengkap | Dipakai ke K_max dan factor yield |
| `survival_lambda=0.67` | Aktif | `app/data/seed.py` | Sesuai referensi/estimate yang dipakai runtime | Dipakai ke survival, hara, ekonomi |
| `f_yield` | Aktif | `app/data/seed.py` | Sesuai desain runtime, perlu verifikasi akademik lanjutan | Langsung mempengaruhi yield |
| `kappa_n/p/k` | Aktif | `app/data/seed.py` | Ada sebagai koefisien referensi, tetapi klaim note masih kacau | Runtime benar-benar menghitung hara |
| biaya infrastruktur dasar | Aktif | `app/data/seed.py` | Ada dukungan di docs/README, tetapi kualitas lokal perlu dibedakan dari placeholder | Dipakai ke economics |
| `weeding_cost_rp_per_are` | Aktif | `app/data/seed.py` | Sesuai desain runtime | Dipakai ke ecology |
| harga pupuk N/P/K | Aktif | `app/data/seed.py` | Sesuai referensi runtime | Dipakai ke ecology |
| harga bebek beli/jual | Aktif | `app/data/seed.py` | Tersedia di sistem | Dipakai ke economics |

### 4.3 Data yang ada di sistem tetapi masih estimasi / local-estimate / literature-uncalibrated / partial

| Item | Status | Validitas singkat | Catatan audit |
|---|---|---|---|
| Yield DSS | `estimation_only` | Rumus ada, kalibrasi lokal penuh belum terlihat | Layak untuk simulasi eksploratif, bukan klaim presisi final |
| `K_max` Jarwo/Tegel | `local-estimate` | Jarwo relatif konsisten, Tegel perlu verifikasi karena docs tidak seragam | Sangat mempengaruhi risk dan recommendation |
| `f_yield` | `literature-uncalibrated` | Ada sebagai faktor pembeda sistem tanam, belum tampak kalibrasi lokal kuat | Perlu dijaga dalam narasi hasil |
| Ecology saving | campuran estimate/literature | Formula aktif, belum semua berbasis lokal | Saat ini tetap mempengaruhi recommendation |
| Environment | `literature-uncalibrated` pada level formula, tetapi numeric belum siap | Formula ada, data flux belum ada | Jangan disajikan seolah hasil emisi final sudah tersedia |
| Economics | `partial` | Sebagian biaya/harga ada, sebagian kunci belum ada | Net profit dan REY belum final |

### 4.4 Data yang ada di sistem tetapi masih placeholder atau belum lengkap

| Item | Status | Dampak | Catatan audit |
|---|---|---|---|
| `rice_duck_price_rp_per_kg` | `None` | `rice_revenue_rp` null, `REY` null, `net_profit_rp` null | Data kritis belum tersedia di runtime |
| `feed_price_rp_per_kg` | `None` | `feed_cost_rp` null, `duck_net_value` null, `net_profit_rp` null | Membatasi economics |
| `conventional_yield_kg_per_ha` | `None` | Revenue pembanding null | Membatasi analisa komparatif |
| `maintenance_cost_rp` | placeholder `0.0` | Profit bisa terlalu optimistis | Perlu verifikasi lokal |
| `additional_cost` | placeholder `0.0` | Profit parsial | Perlu verifikasi komponen biaya nyata |
| `feed_greedy_kg_per_duck_day` | `None` | Penalty feed tidak aktif | Komponen economics belum penuh |
| flux CH4/N2O | `None` | Environment numerik null | Formula hidup, data mati |

### 4.5 Data yang ada di docs lokal/literatur tetapi belum menjadi runtime aktif penuh

| Item | Ada di docs? | Ada di runtime? | Penjelasan singkat |
|---|---|---|---|
| Varietas tambahan: Cigelis/Cegelis, Ciherang, beras merah | Ya | Tidak | Docs lebih kaya dari seed runtime |
| Sistem tanam tambahan: SRI, double transplant | Ya | Tidak | Belum jadi opsi operasional |
| Rentang `q_feed` lebih kaya | Ya | Parsial | Runtime memilih satu fallback, tetapi narasi sumber belum final |
| Variabel lapangan seperti air/topografi | Ya | Tidak | Belum dimodelkan di DSS runtime |
| Beberapa detail biaya lapangan | Ya/diindikasikan | Parsial | Belum lengkap untuk economics final |

### 4.6 Data yang kemungkinan benar-benar belum tersedia atau perlu verifikasi lanjutan

| Item | Status audit | Alasan |
|---|---|---|
| Flux CH4/N2O lokal operasional | Perlu verifikasi lanjutan | Tidak tampak ada seed/lookup numerik aktif di runtime |
| Harga gabah padi-bebek lokal final | Perlu verifikasi lanjutan | Belum ada nilai runtime aktif meski konsepnya dibutuhkan |
| Yield konvensional lokal pembanding | Perlu verifikasi lanjutan | Belum ada nilai runtime aktif |
| Biaya pakan aktual | Perlu verifikasi lanjutan | Belum ada nilai runtime aktif |
| Kalibrasi lokal penuh untuk `alpha_local`, `q_feed`, ecology, emisi | Perlu verifikasi lanjutan | Ada indikasi kebutuhan di docs, belum tampak final di runtime |

### 4.7 Validitas per area besar

#### Agronomi
- Input inti tersedia dan valid secara operasional.
- Lookup varietas/sistem tanam ada, tetapi cakupannya lebih sempit dari docs.
- Yield bersifat estimasi dan masih perlu dijaga klaimnya.

#### Ekonomi
- Data dasar sebagian tersedia, tetapi tiga blocker utama masih kosong: harga gabah padi-bebek, harga pakan, yield konvensional.
- Maka economics runtime belum layak dibaca sebagai hasil profit final penuh.

#### Ekologi
- Formula dan angka dasar tersedia cukup untuk output parsial.
- Validitas masih dominan estimatif/literature-based.
- Hara tanah numerik ada, tetapi narasi status perlu dibedakan sebagai estimasi, bukan pengukuran lapangan.

#### Emisi/lingkungan
- Status terbaik saat ini: formula tersedia, data numerik belum tersedia.
- Tidak boleh diperlakukan sebagai modul emisi operasional final.

### 4.8 Kesimpulan bagian 4

Data operasional minimal untuk simulasi agronomi sudah ada. Data ekonomi dan emisi belum lengkap. Beberapa data sudah ada tetapi masih status estimasi, local-estimate, literature-uncalibrated, atau placeholder. Source of truth docs lebih kaya dari runtime, sehingga report akhir harus membedakan tegas antara:
- data yang sudah aktif di sistem
- data yang hanya ada di docs/literatur
- data yang sudah ada tapi masih placeholder
- data yang benar-benar belum tersedia

---

## Penutup Singkat

Audit ini menunjukkan backend runtime sudah cukup matang untuk simulasi inti dan frontend sudah mengikuti kontrak utama. Namun untuk kebutuhan akademik, paper, dan sinkronisasi UI, masih ada sejumlah drift penting pada:
- validasi frontend
- mapping field rekomendasi
- narasi status/notes
- optimality/recommendation semantics
- kelengkapan data ekonomi dan emisi

Beberapa temuan murni teknis frontend-backend. Sebagian lain perlu keputusan akademik atau verifikasi sumber data lebih lanjut sebelum dianggap final.
