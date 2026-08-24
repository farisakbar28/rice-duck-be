# MODEL MATEMATIKA EKONOMI DSS PADI-BEBEK

## Versi Kombinasi A+C - Dual-Evidence Local Production + Literature Transferability

> **STATUS IMPLEMENTASI:** Source of Truth (SoT) untuk backend branch **A+C — Dual-Evidence Architecture**.  
> **Sumber model akademik:** `Model Matematika Ekonomi DSS Padi Bebek - Versi Kombinasi A+C Final.docx` (versi **non-revisi/pure** yang dipilih untuk implementasi).  
> Dokumen `.docx ... Revisi` hanya arsip dan **bukan** acuan implementasi branch ini.  
> Jika kode, schema, test, README, persistence, visualization, atau dokumentasi lama bertentangan dengan dokumen ini, implementasi harus mengikuti dokumen ini.

---

Catatan Finalisasi Kombinasi:

- Versi kombinasi tidak melakukan averaging, weighted ensemble, atau fusion numerik antara Versi A dan Versi C. Kombinasi dilakukan pada level evidence architecture: Versi C menjadi production/local prediction layer, sedangkan Versi A menjadi literature-transfer/reference layer.
- Production yield menggunakan model lokal parsimonious C0 = 50 kg/are yang dipilih sebelum untouched holdout dibuka melalui farmer-grouped LOFO dan one-standard-error rule. Holdout final hanya digunakan untuk evaluasi, bukan retuning.
- Persamaan Xiong et al. (2014) tetap dipertahankan sebagai literature-uncalibrated reference dengan validity guard. Jika input berada di luar domain artikel, sistem mengembalikan OUTSIDE_LITERATURE_DOMAIN dan tidak memaksakan nilai referensi.
- Density, age, calendar, dan survival dipakai sebagai decision/risk gates. Formula kualitatif-ke-numerik yang tidak identifiable tidak kembali dimasukkan melalui jalur kombinasi.
- Economic output tetap berupa partial/scenario cash contribution. Tidak ada klaim laba bersih final selama realisasi penjualan bebek, feed, dan biaya opsional belum tercatat konsisten.
## 1. Ringkasan Eksekutif

Versi Kombinasi A+C menyatukan dua fungsi ilmiah yang berbeda tanpa mencampurkan koefisiennya. Branch C menjawab pertanyaan "model lokal apa yang paling defensible setelah farmer-level calibration dan independent holdout?". Hasilnya adalah baseline lokal parsimonious 50 kg/are. Branch A menjawab pertanyaan "seberapa transferable formula literatur rice-duck yang eksplisit ke kondisi operasional Astungkara Way?". Hasilnya menunjukkan domain mismatch pada durasi, sehingga formula literatur tidak boleh diperlakukan sebagai local production predictor.

Arsitektur ini sengaja menghindari false sophistication. Model lokal yang lebih kompleks diuji, bukan diasumsikan benar; ketika improvement tidak stabil, complexity ditolak. Formula literatur tetap dipertahankan sebagai external benchmark/reference, tetapi tidak dipaksa bekerja di luar domainnya. Dengan demikian, kontribusi ilmiah utama model adalah governance evidence, anti-leakage validation, explicit abstention, dan decision support yang membedakan local-calibrated output dari literature reference.

**Formula:** `[mixed] Yield_primary = Yield_C0 = 50 kg/are`

Output yield utama untuk local DSS. Status local-calibrated dengan limited holdout performance; bukan high-precision mechanistic predictor.

**Formula:** `[mixed] Yield_literature_reference = Xiong(d_ha,t) jika domain valid; selain itu NA dengan status OUTSIDE_LITERATURE_DOMAIN`

Reference layer hanya untuk transferability/robustness. Tidak dirata-ratakan dengan Yield_primary.

**Formula:** `[system-design] Yield_combination_policy = PRIMARY_LOCAL + OPTIONAL_LITERATURE_REFERENCE; no numeric fusion`

Kata "kombinasi" mengacu pada arsitektur bukti ganda, bukan ensemble numerik.

## 2. Governance Model, Status Klaim, dan Anti-Leakage


| Status tag | Definisi pemakaian |
| --- | --- |
| local-calibrated | Nilai diestimasi hanya dari 25 calibration cycles / 13 farmers pada Branch C sebelum untouched holdout dibuka. |
| local-estimate | Evidence lokal tersedia tetapi berupa range, expert boundary, atau data parsial yang tidak layak disebut terukur universal. |
| literature-uncalibrated | Persamaan/parameter jurnal dipertahankan tanpa klaim kalibrasi lokal Astungkara Way. |
| system-design | Arithmetic, routing, gate, status, atau aturan DSS transparan yang tidak diklaim sebagai hukum biologis. |
| regulatory-locked | Tidak ada parameter aktif pada versi kombinasi ini. |
| mixed | Output menggabungkan runtime input dengan komponen yang mempunyai provenance/status berbeda. |



| Lapisan | Aturan data | Peran final |
| --- | --- | --- |
| Branch A - Literature Transferability | Tidak menggunakan I3 untuk fitting. Semua 36 cycles boleh dipakai untuk domain-compatibility/diagnostic setelah formula reference ditetapkan. | Menilai portability formula eksternal; tidak menjadi primary local yield. |
| Branch C - Local Production | 25 cycles/13 farmers untuk development; 11 cycles/6 farmers untouched holdout. | Menentukan production local baseline dan melaporkan out-of-sample performance. |
| Combined DSS | Tidak ada retuning setelah holdout C dibuka; tidak ada averaging A+C. | Local output tetap C0; A hanya reference jika valid. |


Konsekuensi penting: setelah untouched holdout Branch C telah dibuka pada finalisasi ini, 11 holdout cycles tersebut tidak boleh dipakai lagi untuk memilih model versi berikutnya. Pengembangan selanjutnya memerlukan validation data baru agar klaim independensi tetap valid.

## 3. Input Model


| Nama masukan | Simbol | Satuan | Status input | Catatan |
| --- | --- | --- | --- | --- |
| Luas area aktif bebek | A_are | are | Wajib | Area yang benar-benar diakses bebek; A_are > 0. |
| Jumlah bebek | J | ekor | Wajib | Integer >=0. |
| Sistem tanam | S | kategori | Wajib | Scope aktif Jarwo/Tegel untuk risk lookup; bukan multiplier yield production. |
| Varietas padi | V | kategori | Wajib | Scope aktif Sertani/Seratih atau Inpari; bukan multiplier yield production. |
| Tanggal tanam | TD | tanggal | Wajib jika kalender | Jangkar timeline; tidak langsung mengubah yield. |
| Umur bebek | U_bebek | hari | Wajib | Readiness gate; tidak menjadi multiplier yield/survival/feed. |
| Harga gabah | p_gabah | Rp/kg | Runtime/default | Runtime aktual prioritas; fallback C Rp6.000/kg dari calibration partition. |
| Harga beli bebek | p_duck_buy | Rp/ekor | Runtime/default | Runtime aktual prioritas; fallback C Rp25.000/ekor. |
| Harga jual bebek | p_duck_sell | Rp/ekor | Runtime/scenario | Jika tidak tersedia, Rp45.000/ekor hanya local-estimate expert scenario. |
| Biaya pakan scenario | C_feed_scenario | Rp/siklus | Opsional | Tidak hidden-default; user/mitra dapat memberi nilai scenario. |
| Biaya jaring/kandang | C_jaring_purchase, C_kandang_purchase | Rp | Opsional | Diamortisasi per siklus bila masa pakai tersedia. |


## 4. Shared Decision-Support Gates

### 4.1 Age/Readiness Gate

**Formula:** `[system-design] age_status = NOT_RECOMMENDED jika U_bebek < 21; LOCAL_READY jika 21 <= U_bebek <= 30; OLDER_CONSERVATIVE jika U_bebek > 30`

Threshold lokal dari I1; tidak mengubah yield/profit secara numerik.

R_age dan F_age dari model ekonomi lama tetap dikeluarkan. Clean dataset tidak memiliki variasi umur aktual karena U_bebek=21 merupakan estimasi/imputasi, sehingga coefficient umur tidak identifiable.

### 4.2 Density Gate

**Formula:** `[system-design] d_are = J / A_are`

Kepadatan utama untuk DSS lokal.

**Formula:** `[system-design] d_ha = 100 * d_are`

Konversi khusus kebutuhan reference formula yang memakai ducks/ha.

**Formula:** `[mixed] density_status = UNDER jika d_are < 2; RECOMMENDED jika Jarwo 2-4 atau Tegel 2-3; WARNING_ABOVE_RECOMMENDED jika di atas rentang sistem sampai 8; HIGH_RISK jika d_are > 8`

Boundary berasal dari data collection dan expert judgement; bukan probabilitas mortalitas atau kerusakan.

P_over/P_under kontinu tidak digunakan sebagai production probability. Candidate density response hanya diuji pada Branch C dan tidak dipromosikan ke production yield.

### 4.3 Calendar Gate

**Formula:** `[local-estimate] HST_release_rec in [21,30]`

Local evidence I1.

**Formula:** `[local-estimate] HST_withdraw mengikuti heading; acuan sekitar 56-60 HST`

Fase heading/keluar malai menjadi trigger utama, bukan hard-code 65 HST universal.

**Formula:** `[system-design] t_local = HST_withdraw - HST_release`

Rentang praktis lokal sekitar 28-40 hari; digunakan untuk timeline dan pengecekan domain literature reference.

**Formula:** `[system-design] D_release = TD + HST_release; D_withdraw = TD + HST_withdraw`

Transformasi kalender.

### 4.4 Survival Risk Gate

**Formula:** `[system-design] survival_risk = HIGH jika d_are > 8`

Expert judgement menempatkan >8 ekor/are sebagai zona risiko lebih serius tanpa menetapkan persentase mortalitas. Pada d_are <= 8 tidak ada koreksi survival dalam model karena mortalitas diperlakukan sebagai faktor pengelolaan petani di luar scope.

Model tidak memprediksi N_survive maupun N_sold. Revenue bebek all-sold tetap hanya scenario ceiling, bukan prediksi penjualan aktual.

## 5. Dual-Evidence Yield Architecture

### 5.1 Branch C - Primary Local Production Layer

**Formula:** `[local-calibrated] Y0_C = 50.0 kg/are`

Dipilih dari 25 calibration cycles / 13 farmers menggunakan farmer-grouped model-selection protocol.

**Formula:** `[local-calibrated] Yield_primary_are = Y0_C`

Production model adalah parsimonious local baseline C0. Tidak menggunakan alpha, F_sys, F_var, R_age, atau t multiplier.

**Formula:** `[system-design] Yield_primary_total_kg = Yield_primary_are * A_are`

Konversi ke total area aktif.

Farmer-cluster bootstrap pada calibration partition menghasilkan interval deskriptif 95% untuk parameter Y0_C sekitar 42.81-55.78 kg/are (median bootstrap 50.00). Interval ini adalah uncertainty parameter baseline, bukan prediction interval individual.

### 5.2 Branch A - Literature Transferability / Reference Layer

**Formula:** `[literature-uncalibrated] Yield_A_kg_ha = (-0.0103*d_ha^2 + 2.6314*d_ha + 7569.4) * exp(-((t-80)^2)/(2*80^2))`

Persamaan eksplisit Xiong et al. (2014), E1/I5. Tidak dikalibrasi dengan I3.

**Formula:** `[system-design] Yield_A_kg_are = Yield_A_kg_ha / 100`

Konversi kg/ha menjadi kg/are.

**Formula:** `[system-design] A_reference_valid = TRUE hanya jika 0 < d_ha <= 600 dan 50 <= t <= 80`

Jika FALSE: Yield_literature_reference = NA dan status OUTSIDE_LITERATURE_DOMAIN.

Local duration evidence sekitar 28-40 hari tidak overlap dengan domain 50-80 hari pada E1. Oleh karena itu, reference layer pada skenario lokal tipikal akan abstain. Ini adalah explicit domain guard, bukan computational failure.

### 5.3 Combined Routing Policy


| Kondisi | Output yield | Interpretasi DSS |
| --- | --- | --- |
| Local scenario, input valid | Yield_primary = 50 kg/are | Selalu primary local estimate; tampilkan density/age/calendar risk gates. |
| A_reference_valid = TRUE | Tampilkan Yield_literature_reference di samping primary | Reference/robustness only; tidak mengubah Yield_primary. |
| A_reference_valid = FALSE | Yield_literature_reference = NA; OUTSIDE_LITERATURE_DOMAIN | Tidak clamp, tidak extrapolate sebagai production. |
| d_are > 8 | Yield_primary tetap baseline tetapi survival_risk=HIGH dan duck all-sold revenue dinonaktifkan | Output decision harus menandai scenario high-risk; tidak ada survival percentage. |


Branch C tetap menjadi output yield utama. Branch A, ketika valid, ditampilkan sebagai field referensi terpisah. Tidak ada bobot w_A/w_C atau numerical ensemble karena tidak ada basis kalibrasi bobot dan domain A tidak cocok dengan durasi lokal.

**Formula:** `[system-design] literature_gap = Yield_literature_reference - Yield_primary hanya jika A_reference_valid`

Diagnostic comparison only; bukan correction term.

## 6. Branch C Model Selection dan Untouched Validation

Model selection dilakukan hanya pada calibration partition. Candidate structure yang lebih kompleks dipertahankan hanya sebagai hipotesis yang harus mengalahkan baseline secara stabil, bukan sebagai formula yang diasumsikan benar.


| Candidate | Final calibration params | n fit | LOFO macro MAE | SE | LOFO pooled MAE | Holdout MAE* |
| --- | --- | --- | --- | --- | --- | --- |
| C0 | 50.0000 | 25 | 11.852 | 2.770 | 9.644 | 11.979 |
| C1 | 37.8797, 0.4794 | 25 | 11.128 | 2.636 | 9.666 | 11.687 |
| C3 | 35.1289, 0.5845, 1.4112 | 19 | 10.441 | 2.613 | 9.580 | 13.298 |
| C4 | 35.1289, 0.5845, 1.4112, 1.1102 | 19 | 11.321 | 2.663 | 10.816 | 14.377 |


Best mean inner model adalah C3 dengan one-SE threshold 13.055 kg/are. Model C0 dipilih karena merupakan kandidat paling sederhana yang masih berada di dalam one-SE band. Pemilihan terjadi sebelum holdout dibuka.

Untouched holdout C0: MAE 11.979 kg/are; RMSE 15.990; MedAE 9.583; bias 7.307. Setelah freeze, C1 kebetulan memiliki holdout MAE 11.687, lebih rendah 0.292 kg/are dari C0. C0 tetap tidak diganti karena melakukan switching setelah melihat holdout akan mengubah holdout menjadi tuning evidence dan merusak independensi evaluasi.


| Farmer | A are | J | d/are | Varietas | Sistem | Actual | Pred | Error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I Made Arsania | 3.60 | 13 | 3.611 | Sertani | DefaultJarwo | 45.83 | 50.00 | 4.17 |
| I Nyoman Ranes | 5.10 | 5 | 0.980 | Sertani | DefaultJarwo | 48.04 | 50.00 | 1.96 |
| I Ketut Alit Sudarsana | 10.00 | 65 | 6.500 | Sertani | DefaultJarwo | 60.50 | 50.00 | -10.50 |
| I Wayan Sadia | 7.26 | 9 | 1.240 | Sertani | DefaultJarwo | 59.37 | 50.00 | -9.37 |
| I Nyoman Ranes | 5.10 | 10 | 1.961 | Inpari | Jarwo | 21.02 | 50.00 | 28.98 |
| I Ketut Alit Sudarsana | 14.41 | 30 | 2.082 | Sertani | Jarwo | 52.43 | 50.00 | -2.43 |
| I Ketut Alit Sudarsana | 10.00 | 32 | 3.200 | Sertani | Jarwo | 53.40 | 50.00 | -3.40 |
| I Made Arsania | 3.60 | 15 | 4.167 | Sertani | Jarwo | 40.42 | 50.00 | 9.58 |
| I Ketut Alit Sudarsana | 10.00 | 29 | 2.900 | Inpari | Tegel | 38.65 | 50.00 | 11.35 |
| I Gusti Ngurah Putu Suka Nada | 3.00 | 6 | 2.000 | Sertani | Jarwo | 13.50 | 50.00 | 36.50 |
| I Made Suardika | 3.77 | 8 | 2.122 | Sertani | Jarwo | 36.47 | 50.00 | 13.53 |


Holdout memuat observasi aktual yang sangat rendah; tidak ada baris yang dihapus setelah melihat error. Ini mempertahankan protokol untouched validation yang sudah disetujui.

## 7. Branch A Domain-Transfer Diagnostic

Dari 36 clean cycles, 33/36 berada dalam domain density Xiong (<=600 ducks/ha) dan 3/36 berada di atasnya. Dengan t_local default diagnostik 32 hari, 0/36 berada dalam domain duration 50-80 hari. Karena itu, primary local performance metric untuk Branch A tidak didefinisikan.

Sebagai diagnostic out-of-domain saja, extrapolation pada t=32 terhadap density-valid subset menghasilkan MAE 17.012 kg/are, RMSE 21.689, MedAE 15.225, dan bias +16.427 kg/are. Pada t=50 (batas bawah domain artikel), diagnostic MAE 23.810 kg/are dan bias +23.689. Angka tersebut bukan local validation score dan tidak dipakai untuk calibration.

**Formula:** `[system-design] Branch_A_validation_status = DOMAIN_MISMATCH_FOR_LOCAL_T`

Output ini merupakan hasil ilmiah: literature formula tidak memiliki overlap durasi dengan local operational window yang terkumpul.

## 8. Economic Differential-Costing Engine

**Formula:** `[local-calibrated] p_gabah_default_C = Rp6.000/kg`

Median 25 calibration records; runtime actual price tetap prioritas.

**Formula:** `[local-calibrated] p_duck_buy_default_C = Rp25.000/ekor`

Median 21 positive calibration records; runtime actual price dapat override.

**Formula:** `[local-estimate] p_duck_sell_scenario = Rp45.000/ekor`

Expert judgement; tidak di-fit dari sale revenue karena N_sold tidak tersedia.

**Formula:** `[mixed] Revenue_gabah_primary = Yield_primary_are * A_are * p_gabah`

Ekonomi production menggunakan local primary yield, bukan literature reference.

**Formula:** `[system-design] C_duck_buy = J * p_duck_buy`

Arithmetic cost.

**Formula:** `[mixed] Revenue_duck_all_sold_scenario = J * p_duck_sell`

Scenario ceiling; bukan predicted realized sale. Field ini dinonaktifkan jika d_are>8 karena survival berada pada zona high-risk dan tidak dimodelkan secara numerik.

**Formula:** `[mixed] CashContribution_before_optional = Revenue_gabah_primary + Revenue_duck_all_sold_scenario - C_duck_buy`

Terminologi kontribusi kas skenario, bukan net profit final.

**Formula:** `[system-design] C_infra_cycle = C_jaring_purchase/n_jaring_cycles + C_kandang_purchase/n_kandang_cycles`

Aktif bila nilai dan masa pakai tersedia.

**Formula:** `[mixed] CashContribution_after_optional = CashContribution_before_optional - C_feed_scenario - C_infra_cycle`

Optional costs selalu menjadi child components; missing tidak dianggap measured zero.

Diagnostic calibration feed/J memiliki median positive record sekitar Rp4.464/ekor/siklus (n=16; IQR Rp1.929-Rp8.500), tetapi nilai ini tidak menjadi production default karena recording tidak konsisten. Expert mixed-feed scenario sekitar Rp20.000/ekor/siklus tetap hanya sensitivity/runtime scenario.

Economic literature-reference diagnostic hanya dapat ditampilkan jika A_reference_valid; nilainya tidak dipakai sebagai keputusan utama dan tidak mengubah CashContribution_primary.

## 9. Parameter Final Versi Kombinasi


| Parameter | Nilai | Satuan | Status | Evidence/catatan |
| --- | --- | --- | --- | --- |
| Y0_C | 50,0 | kg/are | local-calibrated | Primary local production baseline; 25 calibration cycles. |
| Y0_C bootstrap 95% | 42,81-55,78 | kg/are | local-calibrated | Parameter uncertainty by farmer-cluster bootstrap; bukan individual prediction interval. |
| Xiong a2 | -0,0103 | formula | literature-uncalibrated | Koefisien d_ha^2 pada Branch A. |
| Xiong a1 | 2,6314 | formula | literature-uncalibrated | Koefisien d_ha pada Branch A. |
| Xiong intercept | 7569,4 | kg/ha | literature-uncalibrated | Intercept formula E1. |
| Xiong t center | 80 | hari | literature-uncalibrated | Center exponential term E1. |
| Xiong density domain | 0 < d_ha <= 600 | ekor/ha | literature-uncalibrated | Validity guard Branch A. |
| Xiong duration domain | 50-80 | hari | literature-uncalibrated | Validity guard Branch A. |
| d_rec_low | 2 | ekor/are | local-estimate | I1/I2. |
| d_rec_high_Jarwo | 4 | ekor/are | local-estimate | I1/I2. |
| d_rec_high_Tegel | 3 | ekor/are | local-estimate | I1/I2. |
| d_high_risk | 8 | ekor/are | local-estimate | Expert boundary; bukan fitted mortality threshold. |
| HST_release_low/high | 21-30 | HST | local-estimate | I1. |
| HST_heading_low/high | 56-60 | HST | local-estimate | I1. |
| t_local practical | 28-40 | hari | local-estimate | I1. |
| p_gabah_default_C | Rp6.000 | Rp/kg | local-calibrated | Median calibration records; runtime price prioritas. |
| p_duck_buy_default_C | Rp25.000 | Rp/ekor | local-calibrated | Median positive calibration records. |
| p_duck_sell_scenario | Rp45.000 | Rp/ekor | local-estimate | Expert scenario; runtime market price prioritas. |
| C_feed_expert_scenario | Rp20.000 | Rp/ekor/siklus | local-estimate | Optional sensitivity; bukan hidden default. |


## 10. Formula/Candidate yang Tidak Dipromosikan


| Formula/candidate | Status | Alasan |
| --- | --- | --- |
| R_age = 0,35/0,15/0,05 | Excluded production | Magnitude berasal dari konstruksi kualitatif-ke-numerik; U_bebek clean dataset juga imputasi. |
| F_age = 1-0,08R_age | Excluded production | Tidak ada kalibrasi numerik lokal. |
| P_over/P_under kontinu | Excluded production | Local boundary dipertahankan sebagai status, bukan probability. |
| C1 density | Research candidate only | Fitted alpha tidak memberi improvement cukup stabil untuk mengalahkan simpler C0 via one-SE rule. |
| C2 trampling beta | Non-identifiable | Hanya 1 calibration cycle d_are>8. |
| C3 density+system | Best mean inner MAE; not production | Masih dalam one-SE band; complexity ditolak sebelum holdout. |
| C4 +variety | Rejected | Representation Inpari kecil dan inner performance memburuk. |
| t-dependent local yield | Non-identifiable | t_duck clean dataset adalah estimasi, bukan raw variation. |
| lambda_eff dari sale records | Invalid target | N_sold != N_survive menurut expert judgement. |
| R_weed(d), R_pest(d) | Excluded production | Kurva density internal tidak mempunyai calibration endpoint memadai. |
| N/P/K temporal linearization | Research/sandbox only | Transformasi temporal internal tidak dipromosikan sebagai local measured benefit. |
| Feed age/density multiplier | Excluded production | Feed sparse/inconsistent; age tidak variable. |
| Numerical A+C weighted ensemble | Rejected by design | Tidak ada basis bobot dan Branch A mengalami duration domain mismatch. |


## 11. Output DSS Final Versi Kombinasi


| Output | Rumus/format | Kondisi | Status |
| --- | --- | --- | --- |
| Yield_primary_are | 50 kg/are | Input area valid | local-calibrated |
| Yield_primary_total_kg | 50*A_are | Input area valid | mixed |
| Yield_literature_reference | Xiong/100 atau NA | Hanya jika domain Xiong valid | literature-uncalibrated |
| literature_reference_status | VALID_DOMAIN / OUTSIDE_LITERATURE_DOMAIN | Selalu | system-design |
| literature_gap | Yield_reference - Yield_primary | Jika reference valid | system-design diagnostic |
| d_are | J/A_are | Selalu | system-design |
| density_status | UNDER/RECOMMENDED/WARNING/HIGH_RISK | Selalu | mixed |
| age_status | status readiness | Selalu | system-design |
| timeline | HST/tanggal | Jika TD/lookup tersedia | mixed |
| survival_risk | HIGH | Hanya jika d_are>8 | system-design |
| Revenue_gabah_primary | Rp | Harga tersedia | mixed |
| Revenue_duck_all_sold_scenario | Rp atau NA | Harga tersedia; dinonaktifkan jika d_are>8 | mixed |
| C_duck_buy | Rp | Harga tersedia | system-design |
| C_feed_scenario | Rp | Opsional | mixed |
| C_infra_cycle | Rp | Opsional | mixed |
| CashContribution_before_optional | Rp | Prerequisite tersedia | mixed |
| CashContribution_after_optional | Rp | Optional cost tersedia | mixed |
| model_status | LOCAL_PRIMARY_WITH_LITERATURE_REFERENCE_LAYER | Selalu | system-design |
| validation_status | LOCAL_HOLDOUT_EVALUATED; LITERATURE_TRANSFER_DOMAIN_MISMATCH | Selalu | system-design |


## 12. Interpretasi Ilmiah Versi Kombinasi


| Temuan | Evidence | Konsekuensi klaim |
| --- | --- | --- |
| Literature transferability | Formula Xiong mempunyai struktur density x stocking-time eksplisit, tetapi local duration 28-40 hari tidak overlap dengan domain 50-80 hari. | External formula tidak boleh diklaim locally valid hanya karena berasal dari jurnal. |
| Local complexity | C3 memperoleh mean inner MAE terbaik, tetapi improvement tidak cukup stabil di bawah one-SE selection. | Data tidak mendukung klaim bahwa density/system factor meningkatkan production prediction secara konsisten. |
| Parsimony | C0 dipilih sebelum final holdout. | Model sederhana lebih defensible daripada coefficient kompleks yang tidak stabil. |
| Holdout | C0 holdout MAE 11,979 kg/are; bias +7,307. | Model adalah local baseline dengan uncertainty material, bukan high-precision yield predictor. |
| Expert judgement | Dipakai untuk boundary/risk dan plausibility, bukan dikonversi otomatis menjadi magnitude coefficient. | Menghindari pseudo-quantification. |
| Economic layer | Menggunakan primary local yield dan explicit scenario costs. | Output disebut cash contribution/scenario estimate, bukan net profit final. |


## 13. Keterbatasan Final

- Dataset lokal tetap kecil: 36 clean cycles dari 19 farmers; Branch C menggunakan 25 cycles untuk development dan 11 cycles untuk final holdout.
- Inpari dan explicit Tegel mempunyai representasi rendah; system/variety effects tidak cukup stabil untuk production coefficient.
- U_bebek dan t_duck pada clean workbook bukan raw observations, sehingga age/duration effects tidak dapat local-calibrate secara sah.
- Branch A mengalami duration domain mismatch; reference formula tidak boleh digunakan sebagai local primary predictor pada window 28-40 hari.
- Branch C C0 tidak sensitif terhadap density, system, variety, age, atau duration. Variabel tersebut tetap berfungsi sebagai risk/decision gates, bukan yield multipliers.
- Holdout MAE sekitar 11,98 kg/are menunjukkan uncertainty prediksi individual masih material. Parameter bootstrap Y0 bukan prediction interval individual.
- Mortalitas tidak dimodelkan secara numerik sampai boundary 8 ekor/are; hanya density >8 yang memicu survival-risk gate. Boundary ini bukan estimasi persentase mortalitas.
- Jumlah bebek terjual tidak diprediksi. All-sold duck revenue hanya scenario ceiling.
- Feed, fertilizer, weeding, pesticide/herbicide, dan nutrient benefits tidak dipromosikan sebagai active numeric savings tanpa endpoint lokal yang lebih kuat.
- Setelah holdout dibuka, pengembangan/retuning baru membutuhkan dataset validasi baru. Holdout lama tidak dapat disebut untouched lagi untuk model generasi berikutnya.
- Versi kombinasi meningkatkan rigor evidence architecture, tetapi tidak mengubah keterbatasan sample size menjadi kecanggihan prediktif yang tidak didukung data.
## 14. Traceability Keputusan Final


| Keputusan | Pilihan | Implementasi |
| --- | --- | --- |
| Decision 1 - Branch A | A: strict separation | I3 tidak membentuk Branch A; digunakan untuk domain-transfer diagnostic setelah reference formula freeze. |
| Decision 2 - Branch A | 2A: evidence reset | Formula kualitatif-ke-numerik yang tidak defensible dikeluarkan dari production path. |
| Decision 1 - Branch C | C: formal farmer-grouped split | 25 calibration cycles/13 farmers + 11 untouched holdout cycles/6 farmers. |
| Decision 2 - Branch C | 2B: retain and calibrate | Candidate diuji; non-identifiable formula tidak dipaksakan. |
| P1 | Approved | Xiong aktif sebagai literature reference dengan validity guard; bukan local primary. |
| P2 | Approved with scope rule | Tidak ada koreksi survival numerik sampai boundary 8; d_are>8 memicu survival risk/status tanpa persentase. |
| P3 | Approved | Economic output = cash contribution/scenario estimate, bukan final net profit. |
| P4 | Approved | Farmer-grouped calibration/holdout; inner LOFO; model freeze sebelum holdout. |
| Final combined decision | A+C dual-evidence architecture | Branch C = primary local production; Branch A = optional literature-transfer/reference; no numerical fusion. |


### Sumber Internal yang Menjadi Evidence


| Kode | File | Lokasi | Peran |
| --- | --- | --- | --- |
| I1 | data_collection_padi_bebek_FINAL(3).xlsx | Sheet Data Collection Final; terutama No. 9-29, 35-55, 58-84. | Data collection lokal hasil konsolidasi; boundary agronomi, harga, biaya, dan kondisi operasional. |
| I2 | Dokumentasi Expert DSS Padi-Bebek(1).docx | Bagian 4.1-4.11 dan Bagian 5 audit konsistensi. | Expert judgement; koreksi survival, harga jual bebek, pakan, density, dan metode validasi. |
| I3 | DSS_Padi_Bebek_Rekap_Bersih_v10(1).xlsx | Sheet Dataset Actual Bersih, 36 siklus. | Branch A: tidak membentuk formula. Branch C: 25 calibration + 11 untouched holdout, farmer-grouped. |
| I4 | Model Matematika Data Collection DSS Padi Bebek Ekonomi(3).docx | Bagian parameter dan Mesin Komputasi Matematis. | Model ekonomi pra-finalisasi; sumber formula yang diaudit/dihapus/dijadikan kandidat. |
| I5 | Kumpulan_Variabel_Rumus_Data_Artikel_Referensi_Scopus_FINAL.xlsx | Daftar Artikel, Rumus Model, dan Data untuk Xiong serta referensi lain. | Jejak formula literatur dan mapping artikel internal. |
| I6 | Notulensi Semi Wawancara Validasi Variabel(1).pdf | Bagian kepadatan, durasi, pola tanam, harga, biologis bebek. | Boundary validation awal Astungkara Way. |
| I7 | Model Matematika Ekonomi DSS Padi Bebek - Versi A Final.docx | Seluruh bagian. | Cabang strict separation/evidence reset yang menjadi literature-transfer layer. |
| I8 | Model Matematika Ekonomi DSS Padi Bebek - Versi C Final.docx | Seluruh bagian. | Cabang local calibration/holdout yang menjadi production layer. |


## Referensi Ilmiah dan Status Scopus

Strategi referensi mengikuti prioritas Bali > Indonesia > ASEAN > Asia > Global dan tahun >2020. Penelusuran menemukan publikasi rice-duck dari Bali pada prosiding konferensi, tetapi tidak dipromosikan sebagai referensi ilmiah model karena aturan final penelitian mensyaratkan jurnal yang terindeks Scopus. Karena tidak ditemukan jurnal Scopus Bali >2020 yang memenuhi kebutuhan formula/justifikasi inti, prioritas berikutnya adalah Indonesia. Xiong et al. (2014) dipertahankan hanya sebagai fallback formula historis karena menyediakan closed-form density x stocking-time yang tidak ditemukan dalam jurnal >2020 yang ditelusuri.


| Kode | Referensi | Pemakaian dalam model | Verifikasi Scopus |
| --- | --- | --- | --- |
| E1 | Xiong, D.; Fang, K.; Luo, Y.; Dai, X. (2014). Modeling of Duck Density and Complex Stocking Time in Rice-Duck Agroecosystems in Terms of Economic and Ecological Benefits. Mathematical Problems in Engineering, 2014, 487537. DOI: 10.1155/2014/487537. | Fallback closed-form yield reference untuk Branch A; tidak dikalibrasi lokal dan hanya digunakan dengan validity guard. | Scopus historical coverage; jurnal ceased publishing 2024. SCImago/Scopus historical record; status diperlakukan sebagai fallback, bukan sumber baru >2020. |
| E2 | Khumairoh, U.; Lantinga, E.A.; Handriyadi, I.; Schulte, R.P.O.; Groot, J.C.J. (2021). Agro-ecological mechanisms for weed and pest suppression and nutrient recycling in high yielding complex rice systems. Agriculture, Ecosystems & Environment, 313, 107385. DOI: 10.1016/j.agee.2021.107385. | Indonesia; on-farm evidence bahwa ducks berperan pada weed/pest suppression, nutrient cycling, dan kompleksitas sistem berkaitan dengan yield. Tidak digunakan untuk mengarang koefisien Bali. | Scopus confirmed pada Elsevier Journal Insights; Scopus metrics 2024 menempatkan jurnal Q1. |
| E3 | Li, Y.; Wu, T.; Wang, S.; Ku, X.; Zhong, Z.; Liu, H.; Li, J. (2023). Developing integrated rice-animal farming based on climate and farmers choices. Agricultural Systems, 204, 103554. DOI: 10.1016/j.agsy.2022.103554. | Asia/global review; mendukung bahwa transfer IRF harus mempertimbangkan geografi, iklim, pilihan petani, dan ecological adaptability. | Scopus confirmed pada Elsevier Journal Insights; SCImago 2024 Q1. |
| E4 | Cui, J.; Liu, H.; Wang, H.; Wu, S.; Bashir, M.A.; Reis, S.; Sun, Q.; Xu, J.; Gu, B. (2023). Rice-Animal Co-Culture Systems Benefit Global Sustainable Intensification. Earth's Future, 11(2), e2022EF002984. DOI: 10.1029/2022EF002984. | Global meta-analysis; mendukung plausibility manfaat yield, input reduction, dan net income pada rice-animal co-culture. Effect size global tidak dipakai sebagai multiplier lokal. | Scopus confirmed; Scopus metrics 2024 menempatkan Earth's Future Q1. |
| E5 | Alfiansyah, M.L.; Rahardja, D.P.; Padjung, R. (2025). Advantages of introducing maggot-fed ducks into a rice plantation with and without Azolla. Journal of Water and Land Development, 67, 61-72. DOI: 10.24425/jwld.2025.156040. | Indonesia (Sulawesi Selatan); recent empirical rice-duck context dengan density dan timing; digunakan sebagai contextual plausibility, bukan transfer coefficient ke Bali. | Publisher indexing page mencantumkan SCOPUS; SCImago 2024 Q2. |


### Sumber Verifikasi Indeksasi


| Jurnal | Sumber pengecekan | Status yang dipakai |
| --- | --- | --- |
| Agriculture, Ecosystems & Environment | Elsevier Journal Insights: https://www.sciencedirect.com/journal/agriculture-ecosystems-and-environment/about/insights | Scopus listed; 2024 metrics Q1. |
| Agricultural Systems | Elsevier Journal Insights: https://www.sciencedirect.com/journal/agricultural-systems/about/insights ; SCImago journal record | Scopus listed; SCImago 2024 Q1. |
| Earth's Future | SCImago/WUR Scopus Journal Metrics record | Scopus metrics 2024 Q1. |
| Journal of Water and Land Development | Publisher Abstracting & Indexing: https://journals.pan.pl/jwld ; SCImago 2024 ranking | SCOPUS listed; SCImago 2024 Q2. |
| Mathematical Problems in Engineering | Wiley journal page + historical Scopus/SCImago record | Journal ceased publishing in 2024; historical source only. |



---


## Kontrak Implementasi Backend — Branch A+C — Dual-Evidence Architecture

### Audit kondisi `master` sebelum migrasi

Repository `rice-duck-be` saat ini sudah berupa backend FastAPI terstruktur (`app/api`, `app/engines`, `app/services`, `app/schemas`, `app/repositories`, `tests`), tetapi DSS Core masih merepresentasikan SoT lama. Endpoint utama dapat tetap menggunakan `POST /api/v1/dss/simulate`; yang harus diganti adalah semantics engine, request/response contract, persistence, visualization, dan test.

Perilaku `master` yang **tidak boleh dibawa mentah-mentah** ke branch baru:

- `Y_BASE = 47.8767507 kg/are` sebagai production yield;
- kalender fixed `HST_IN=21`, `HST_OUT=65`, `T_ACTIVE=44`;
- `N_survive = J` untuk `d<=8` dan `floor(0.60*J)` untuk `d>8`;
- `Revenue_duck_potential = N_survive * 52.500`;
- feed wajib `J * 20.000` di Core;
- output canonical `Net_Cash_Contribution_DSS` versi lama;
- harvest window lama Sertani `100–110` dan Inpari `109–116` sebagai output Core;
- visualization `survival_rate=1.0/0.60`;
- sandbox fertilizer/weeding/pesticide yang dipanggil otomatis pada setiap simulasi Core;
- history `schema_version=3` yang memakai field SoT lama.

`/optimizer/recommend` pada master adalah stub dan berada di luar SoT. Branch baru boleh mempertahankannya sebagai stub, tetapi **dilarang** menghidupkan kembali formula legacy melalui optimizer lalu mencampurkannya ke `/dss/simulate`.

### Aturan perubahan repository

1. `app/engines/formula_engine.py` harus menjadi implementasi 1:1 terhadap formula/gate branch ini.
2. `app/services/simulation_service.py` hanya boleh mengorkestrasi output yang ada pada SoT branch ini; jangan mempertahankan field legacy demi kompatibilitas bila maknanya sudah salah.
3. `app/schemas/dss.py` harus diperbarui agar nullable/optional field merepresentasikan **ketidaktersediaan ilmiah**, bukan diisi angka nol palsu.
4. `app/data/seed.py` harus menghapus konstanta obsolete dan menyimpan hanya default/reference yang memang aktif pada branch ini.
5. `app/services/visualization_service.py` tidak boleh menampilkan survival percentage atau kurva numerik yang tidak ada di SoT.
6. History baru harus memakai `schema_version=4`; record v1–v3 tetap historical/legacy dan tidak boleh direinterpretasi sebagai output model baru.
7. Test unit/API/golden case harus ditulis ulang terhadap `tes_skenario.md` branch ini.
8. `docs/NUMERICAL_VALIDATION_DSS_PADI_BEBEK_FINAL_CLEAN.md` lama **hapus dari branch**. Isinya menguji model obsolete `47.8767507 kg/are` pada seluruh 36 siklus dan bertentangan dengan desain validasi terbaru. Hasil/metode validasi yang sah sudah diikat langsung pada SoT ini dan `tes_skenario.md`.
9. README branch harus menunjuk ke file SoT ini dan tidak lagi mendokumentasikan `N_survive`, feed Core Rp20.000, atau output lama bila tidak ada pada branch.


### Kontrak request yang direkomendasikan

Kontrak mengikuti branch C untuk primary local model dan menambah satu technical input opsional untuk Branch A reference.

| Field API | Tipe | Aturan |
|---|---|---|
| `land_area_are` | number | wajib; `>0` |
| `duck_count` | integer | wajib; `>=0` |
| `rice_variety` | enum | wajib; `sertani` / `inpari` |
| `planting_system` | enum | wajib; `jajar_legowo` / `tegel` |
| `duck_age_days` | integer | wajib; `>=0` |
| `planting_date` | date/null | opsional |
| `p_gabah` | number/null | default `6000`, runtime aktual prioritas |
| `p_duck_buy` | number/null | default `25000`, runtime aktual prioritas |
| `p_duck_sell` | number/null | default scenario `45000`, runtime aktual prioritas |
| `literature_duration_days` | number/null | opsional; hanya untuk reference Xiong, tidak mengubah primary yield/economics |
| `c_feed_scenario` | number/null | opsional |
| infrastructure fields | number/null | opsional dengan cycle count `>0` |

### Output canonical branch kombinasi

| Field | Semantik |
|---|---|
| `model_variant` | `AC_DUAL_EVIDENCE` |
| `yield_primary_are` | `50 kg/are` |
| `yield_primary_total_kg` | `50*A_are` |
| `yield_literature_reference_are` | Xiong/100 atau `null` |
| `literature_reference_status` | `VALID_DOMAIN` / `OUTSIDE_LITERATURE_DOMAIN` |
| `literature_gap` | reference-primary hanya bila reference valid |
| `model_status` | `LOCAL_PRIMARY_WITH_LITERATURE_REFERENCE_LAYER` |
| `validation_status` | local holdout evaluated + literature transfer domain mismatch |
| age/density/calendar/survival gates | sama dengan C/A |
| `revenue_gabah_primary` | selalu memakai primary C0, **bukan** literature reference |
| `revenue_duck_all_sold_scenario` | `J*p_duck_sell`; `null` jika `d_are>8` |
| cash contribution fields | primary economy; tidak diubah oleh Xiong reference |

**Larangan:** jangan rata-ratakan `yield_primary` dan `yield_literature_reference`; jangan membuat weight/ensemble; jangan memakai literature output untuk mengganti primary economic decision.

### Perubahan file minimum dari master

| Path | Perubahan wajib |
|---|---|
| `app/engines/formula_engine.py` | implement C0 primary + Xiong reference guard sebagai dua jalur terpisah; hapus numerical survival |
| `app/engines/impact_engine.py` | tidak dipanggil otomatis dari Core |
| `app/services/simulation_service.py` | primary output selalu C0; reference conditional; economics selalu primary |
| `app/schemas/dss.py` | dual-yield response + literature status/gap; nullable reference |
| `app/data/seed.py` | C defaults + Xiong coefficients/domain metadata; no obsolete 47.8767507/52500/feed20000 Core |
| `app/services/visualization_service.py` | tampilkan primary vs reference hanya saat reference valid; no survival-rate curve |
| `app/domain/models.py`, repository/history | schema v4; simpan kedua evidence layers secara terpisah |
| `tests/*` | holdout C primary + domain-transfer A + boundary tests sesuai `tes_skenario.md` kombinasi |

