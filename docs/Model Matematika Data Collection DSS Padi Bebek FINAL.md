# MODEL MATEMATIKA EKONOMI DSS PADI-BEBEK

## Versi C - Farmer-Grouped Calibration/Validation Split + Retain and Calibrate

> **STATUS IMPLEMENTASI:** Source of Truth (SoT) untuk backend branch **C — Farmer-Grouped Calibration/Validation Split**.  
> **Sumber model akademik:** `Model Matematika Ekonomi DSS Padi Bebek - Versi C Final.docx` (versi **non-revisi/pure** yang dipilih untuk implementasi).  
> Dokumen `.docx ... Revisi` hanya arsip dan **bukan** acuan implementasi branch ini.  
> Jika kode, schema, test, README, persistence, visualization, atau dokumentasi lama bertentangan dengan dokumen ini, implementasi harus mengikuti dokumen ini.

---

Catatan Finalisasi:

- 36 clean cycles dibagi pada level petani menjadi 25 calibration/development cycles dari 13 petani dan 11 untouched holdout cycles dari 6 petani. Tidak ada petani yang muncul pada kedua partition.
- Model selection dilakukan hanya di calibration partition menggunakan Leave-One-Farmer-Out (LOFO). Untouched holdout dibuka setelah formula dan model selection freeze.
- Formula lama boleh dipertahankan sebagai candidate jika endpoint-nya identifiable. Jika data tidak mengandung target/variation yang diperlukan, formula tidak dipaksakan menghasilkan coefficient.
- Hasil model selection memilih C0 (constant local baseline 50 kg/are) melalui one-standard-error rule. Candidate density/system/variety tidak memperoleh bukti cukup untuk dipromosikan ke production model.
- Output ekonomi tetap partial/scenario cash contribution. Survival biologis tidak di-fit dari duck-sale records karena jumlah terjual tidak identik dengan jumlah hidup.
## 1. Ringkasan Eksekutif

Versi C mempertahankan kemungkinan local calibration, tetapi memisahkan development dan final validation secara ketat pada level petani. Cabang ini menguji apakah bentuk nonlinear density yang sebelumnya dibuat internal benar-benar memberi nilai prediktif setelah dicegah dari farmer leakage. Hasilnya: C3 memiliki LOFO macro-MAE terendah, tetapi improvement-nya berada dalam uncertainty satu standard error; karena seluruh kandidat termasuk C0 masih berada dalam one-SE threshold, model paling sederhana C0 dipilih sebelum holdout dibuka.

Production Yield Engine Versi C akhirnya tidak menggunakan density, sistem tanam, varietas, umur, atau durasi sebagai multiplier yield numerik. Parameter aktif adalah Y0_C = 50 kg/are, hasil median/calibration objective pada 25 calibration cycles. Density dan kalender tetap penting sebagai DSS risk/recommendation gates, bukan sebagai coefficient yield yang tidak didukung data.

## 2. Metodologi Split dan Anti-Leakage

**Formula:** `[system-design] Partition = 13 farmer calibration/development + 6 farmer untouched holdout`

Unit split adalah identitas petani, bukan baris, sehingga cycle dari petani yang sama tidak bocor ke kedua sisi.

Untouched holdout farmers: I Gusti Ngurah Putu Suka Nada; I Ketut Alit Sudarsana; I Made Arsania; I Made Suardika; I Nyoman Ranes; I Wayan Sadia.

Calibration/development terdiri dari 25 cycles; holdout 11 cycles (30,6% dari 36 clean cycles). Assignment disetujui sebelum fitting dan tidak diubah berdasarkan yield/error.

**Formula:** `[system-design] Inner validation = Leave-One-Farmer-Out pada 13 calibration farmers`

Satu petani beserta seluruh cycle miliknya ditahan pada setiap inner fold.

**Formula:** `[system-design] Model selection = one-standard-error rule; pilih model paling sederhana dengan LOFO macro-MAE <= best_MAE + SE_best`

Rule ditetapkan sebelum holdout final dibuka; holdout tidak digunakan memilih model.

## 3. Input Model


| Nama masukan | Simbol | Satuan | Status input | Catatan |
| --- | --- | --- | --- | --- |
| Luas area aktif bebek | A_are | are | Wajib | Area interaksi bebek. |
| Jumlah bebek | J | ekor | Wajib | Integer >=0. |
| Sistem tanam | S | kategori | Wajib | Jarwo/Tegel untuk risk lookup; candidate yield factor diuji tetapi tidak dipromosikan. |
| Varietas | V | kategori | Wajib | Sertani/Seratih atau Inpari; candidate factor diuji tetapi tidak dipromosikan. |
| Tanggal tanam | TD | tanggal | Wajib jika kalender | Tidak langsung mengubah yield. |
| Umur bebek | U_bebek | hari | Wajib | Quality gate; tidak dapat dikalibrasi terhadap clean dataset karena nilai 21 adalah imputasi. |
| Harga gabah | p_gabah | Rp/kg | Runtime / default | Default C=Rp6.000/kg dari median 25 calibration cycles; runtime aktual prioritas. |
| Harga beli bebek | p_duck_buy | Rp/ekor | Runtime / default | Default C=Rp25.000 dari median 21 positive calibration records; runtime aktual prioritas. |
| Harga jual bebek | p_duck_sell | Rp/ekor | Runtime / scenario | Tidak dapat dikalibrasi dari sale revenue karena N_sold tidak tersedia; expert scenario Rp45.000. |


## 4. Candidate Yield Models yang Diuji

**Formula:** `[local-calibrated candidate C0] Y_hat = Y0`

Baseline constant/intercept-only. Y0 diestimasi dari calibration partition.

**Formula:** `[local-calibrated candidate C1] Y_hat = Y0 * (1 + alpha*(1-exp(-d_are/4)))`

K_opt=4 fixed sebagai local boundary; Y0 dan alpha di-fit. alpha>=0.

**Formula:** `[system-design candidate C2] Y_hat = C1 - beta*(max(0,(d_are-8)/8))^2`

Tidak di-fit: hanya 1 calibration cycle memiliki d_are>8, sehingga beta tidak identifiable secara defensible.

**Formula:** `[local-calibrated candidate C3] Y_hat = C1 * F_sys; F_sys=1 untuk Jarwo dan F_Tegel untuk Tegel`

F_Tegel di-fit hanya menggunakan rows dengan sistem tanam eksplisit; Null(default Jarwo) tidak dipakai sebagai evidence numerik F_sys.

**Formula:** `[local-calibrated candidate C4] Y_hat = C3 * F_var; F_var=1 untuk Sertani dan F_Inpari untuk Inpari`

F_Inpari di-fit pada explicit-system fitting subset; jumlah Inpari kecil sehingga complexity penalty penting.

R_age/F_age tidak diuji karena U_bebek pada clean workbook adalah estimasi 21 hari, bukan variation observasi. Efek t juga tidak di-fit karena t_duck=45 adalah estimasi kualitatif. Survival tidak di-fit karena N_sold tidak identik dengan N_survive (I2 Bagian 4.2).

## 5. Hasil Inner LOFO dan Model Selection


| Candidate | Final calibration params | n fit | LOFO macro MAE | SE | LOFO pooled MAE | Holdout MAE* |
| --- | --- | --- | --- | --- | --- | --- |
| C0 baseline | 50.0000 | 25 | 11.852 | 2.770 | 9.644 | 11.979 |
| C1 density | 37.8797, 0.4794 | 25 | 11.128 | 2.636 | 9.666 | 11.687 |
| C3 density+system | 35.1289, 0.5845, 1.4112 | 19 | 10.441 | 2.613 | 9.580 | 13.298 |
| C4 density+system+variety | 35.1289, 0.5845, 1.4112, 1.1102 | 19 | 11.321 | 2.663 | 10.816 | 14.377 |


*Kolom holdout hanya dilaporkan setelah freeze dan tidak digunakan untuk model selection.

**Formula:** `[system-design] best inner model by macro-MAE = C3; one-SE threshold = 13.055 kg/are`

C3 memiliki macro-MAE terendah, tetapi bukan otomatis production winner.

**Formula:** `[system-design] selected production model = C0`

C0 adalah model paling sederhana yang masih berada di bawah one-SE threshold. Pemilihan ini menolak complexity yang tidak memperoleh improvement stabil.

## 6. Production Yield Engine Versi C

**Formula:** `[local-calibrated] Y0_C = 50.0 kg/are`

Median/MAE-compatible local baseline dari 25 calibration cycles setelah farmer-grouped split.

**Formula:** `[local-calibrated] Yield_are = Y0_C`

Production yield tidak memakai alpha, F_sys, F_var, R_age, atau t multiplier.

**Formula:** `[system-design] Yield_total_kg = Yield_are * A_are`

Konversi dari per-are ke total area aktif.

Farmer-cluster bootstrap pada calibration partition memberi interval deskriptif 95% untuk Y0 sekitar 42.81 sampai 55.78 kg/are (median bootstrap 50.00). Interval ini adalah uncertainty parameter baseline, bukan prediction interval individual untuk satu petak.

## 7. Density, Calendar, Age, dan Survival Gates

**Formula:** `[system-design] d_are = J / A_are`

Area aktif bebek wajib >0.

**Formula:** `[mixed] density_status = UNDER jika d_are<2; RECOMMENDED jika Jarwo 2-4 atau Tegel 2-3; WARNING sampai 8; HIGH_RISK jika >8`

Boundary lokal I1/I2. Tidak memodifikasi Yield_are production C0.

**Formula:** `[system-design] age_status = NOT_RECOMMENDED jika U_bebek<21; LOCAL_READY jika 21<=U_bebek<=30; OLDER_CONSERVATIVE jika >30`

Tidak masuk yield/profit multiplier.

**Formula:** `[local-estimate] HST_release_rec in [21,30]; HST_withdraw mengikuti heading sekitar 56-60 HST`

I1 No.12-13,26. t lokal sekitar 28-40 hari.

**Formula:** `[system-design] survival_risk = HIGH jika d_are > 8`

Boundary expert untuk kondisi berisiko tinggi. Pada d_are <= 8 tidak ada koreksi survival dalam model; jumlah bebek terjual tetap tidak diprediksi.

## 8. Economic Differential-Costing Engine Versi C

**Formula:** `[local-calibrated] p_gabah_default_C = Rp6.000/kg`

Median seluruh 25 calibration price records; runtime price aktual tetap prioritas.

**Formula:** `[local-calibrated] p_duck_buy_default_C = Rp25.000/ekor`

Median 21 positive calibration records; actual purchase price dapat override.

**Formula:** `[local-estimate] p_duck_sell_scenario = Rp45.000/ekor`

Tidak di-fit dari duck sale revenue karena jumlah yang terjual tidak tersedia; expert judgement menolak Rp35.000 sebagai nilai normal.

**Formula:** `[mixed] Revenue_gabah = Yield_are * A_are * p_gabah`

Yield_are production C0; runtime p_gabah diprioritaskan.

**Formula:** `[system-design] C_duck_buy = J * p_duck_buy`

Arithmetic cash cost.

**Formula:** `[mixed] Revenue_duck_all_sold_scenario = J * p_duck_sell`

Potential scenario, bukan predicted realized sale. Dinonaktifkan jika d_are>8 karena survival tidak dimodelkan secara numerik pada zona high-risk.

**Formula:** `[mixed] CashContribution_before_optional = Revenue_gabah + Revenue_duck_all_sold_scenario - C_duck_buy`

Tidak disebut net profit final.

**Formula:** `[system-design] C_infra_cycle = C_jaring_purchase/n_jaring_cycles + C_kandang_purchase/n_kandang_cycles`

Aktif bila data infrastruktur tersedia/dipilih.

**Formula:** `[mixed] CashContribution_after_optional = CashContribution_before_optional - C_feed_scenario - C_infra_cycle`

Feed dan infra selalu tampil sebagai child component; missing tidak disamarkan sebagai measured zero.

Calibration diagnostic feed: median positive recorded feed/J adalah sekitar Rp4.464/ekor/siklus (n=16; IQR Rp1.929-Rp8.500). Nilai ini TIDAK dipromosikan sebagai production default karena pencatatan feed tidak konsisten dan expert judgement memberi lower-bound mixed-feed sekitar Rp20.000/ekor/siklus. Dengan demikian feed tetap scenario/runtime input.

## 9. Untouched Holdout Evaluation

Setelah C0 dipilih dan parameter freeze, 11 cycles dari 6 holdout farmers dibuka. Hasil final: MAE 11.979 kg/are; RMSE 15.990 kg/are; MedAE 9.583 kg/are; bias 7.307 kg/are. Bias positif berarti baseline 50 kg/are cenderung over-predict pada holdout secara rata-rata.


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


Holdout memuat beberapa observasi aktual sangat rendah; baris tersebut tidak dihapus setelah melihat error. Ini menjaga untouched holdout tetap konsisten dengan protokol yang disetujui.

## 10. Parameter Final Versi C


| Parameter | Nilai | Satuan | Status | Evidence/catatan |
| --- | --- | --- | --- | --- |
| Y0_C | 50,0 | kg/are | local-calibrated | 25 calibration cycles; selected C0. |
| Y0_C bootstrap 95% | 42,81-55,78 | kg/are | local-calibrated | Cluster bootstrap by farmer; descriptive parameter uncertainty. |
| d_rec_low | 2 | ekor/are | local-estimate | I1 No.22. |
| d_rec_high_Jarwo | 4 | ekor/are | local-estimate | I1/I2. |
| d_rec_high_Tegel | 3 | ekor/are | local-estimate | I1/I2. |
| d_high_risk | 8 | ekor/are | local-estimate | Expert boundary. |
| HST_release_low | 21 | HST | local-estimate | I1 No.12. |
| HST_release_high | 30 | HST | local-estimate | I1 No.12. |
| HST_heading_low | 56 | HST | local-estimate | I1 No.13. |
| HST_heading_high | 60 | HST | local-estimate | I1 No.13. |
| t_local_low | 28 | hari | local-estimate | I1 No.27. |
| t_local_high | 40 | hari | local-estimate | I1 No.27. |
| p_gabah_default_C | Rp6.000 | Rp/kg | local-calibrated | Median 25 calibration rows. |
| p_duck_buy_default_C | Rp25.000 | Rp/ekor | local-calibrated | Median 21 positive calibration rows. |
| p_duck_sell_scenario | Rp45.000 | Rp/ekor | local-estimate | Expert judgement; not calibrated from sale records. |
| C_feed_recorded_median | Rp4.464 | Rp/ekor/siklus | local-estimate | Diagnostic only, not production default. |
| C_feed_expert_scenario | Rp20.000 | Rp/ekor/siklus | local-estimate | Optional mixed-feed sensitivity. |


## 11. Candidate yang Tidak Dipromosikan


| Candidate | Status | Alasan |
| --- | --- | --- |
| C1 density | Retained as research candidate | Alpha fitted, tetapi improvement tidak cukup untuk mengalahkan simpler C0 via one-SE selection. |
| C2 trampling beta | Non-identifiable | Hanya 1 calibration cycle d_are>8. Tidak ada basis untuk stable beta. |
| C3 density+system | Best mean inner MAE, rejected for production complexity | LOFO macro-MAE terbaik, tetapi masih dalam one-SE band; holdout dibuka setelah rejection. |
| C4 +variety | Rejected | Inpari representation terlalu kecil dan inner performance memburuk. |
| R_age/F_age | Non-identifiable | U_bebek=21 di clean dataset adalah imputasi, bukan observasi variable. |
| t effect | Non-identifiable | t_duck=45 di clean dataset adalah imputasi kualitatif. |
| lambda_eff from sale records | Invalid target | N_sold tidak sama dengan N_survive. |
| Weed/pesticide/fertilizer curves | Insufficient endpoint coverage | Weeding 0/36, fertilizer 1/36, pesticide 4/36 non-zero pada audit I2. |
| Feed age/density multipliers | Not promoted | Feed records sparse/inconsistent dan age tidak variable. |


## 12. Output DSS Final Versi C


| Output | Rumus/format | Kondisi | Status |
| --- | --- | --- | --- |
| Yield_are | 50 kg/are | Selalu selama input area valid | local-calibrated |
| Yield_total_kg | 50*A_are | Selalu | mixed |
| d_are | J/A_are | Selalu | system-design |
| density_status | status | Selalu | mixed |
| age_status | status | Selalu | system-design |
| timeline | HST/tanggal | Jika TD/lookup tersedia | mixed |
| survival_risk | HIGH | Hanya jika d_are>8 | system-design |
| Revenue_gabah | Rp | Harga tersedia | mixed |
| Revenue_duck_all_sold_scenario | Rp | Harga jual tersedia; dinonaktifkan jika d_are>8 | mixed |
| C_duck_buy | Rp | Harga beli tersedia | system-design |
| C_feed_scenario | Rp | Opsional | mixed |
| C_infra_cycle | Rp | Opsional | mixed |
| CashContribution_before_optional | Rp | Prerequisite tersedia | mixed |
| CashContribution_after_optional | Rp | Optional costs tersedia | mixed |
| model_validation_status | LOCAL_CALIBRATED_WITH_LIMITED_HOLDOUT_PERFORMANCE | Selalu | system-design |


## 13. Keterbatasan Final Versi C

- Jumlah observasi tetap kecil: 25 calibration cycles dari 13 petani dan 11 holdout cycles dari 6 petani.
- Hanya 3 calibration observations merupakan Inpari dan 3 explicit Tegel; candidate factors karena itu tidak stabil untuk production.
- Default/imputed Jarwo tidak dipakai sebagai evidence numerik F_sys, sehingga jumlah fitting rows candidate C3/C4 hanya 19.
- U_bebek dan t_duck pada clean workbook tidak merupakan raw observation, sehingga efek umur/durasi tidak dapat dikalibrasi secara sah.
- Holdout MAE sekitar 11,98 kg/are menunjukkan predictive uncertainty masih material. C0 adalah baseline lokal defensible, bukan high-precision predictor.
- Economic output tetap scenario contribution karena duck sale count, feed standard, dan optional cost coverage belum memadai untuk net profit final.
- Setelah holdout dibuka, tidak ada retuning. Jika penelitian mengembangkan model berikutnya, diperlukan dataset baru agar validation set baru tetap independen.
## 14. Traceability Keputusan Final


| Keputusan | Pilihan | Implementasi |
| --- | --- | --- |
| Decision 1 | C - formal calibration/validation split | 25/11 cycles, 13/6 farmers, farmer-grouped. |
| Decision 2 | 2B - retain and calibrate | Formula candidate diuji; non-identifiable candidate tidak dipaksakan. |
| P1 | Versi A only | Tidak mengatur C production yield. |
| P2 | Approved scope rule | Tidak ada koreksi survival numerik sampai boundary 8; d_are>8 memicu risk/status. |
| P3 | Approved | Cash contribution/scenario estimate, bukan final net profit. |
| P4 | Approved | 13 farmer development + 6 farmer untouched holdout; inner LOFO. |


### Sumber Internal yang Menjadi Evidence


| Kode | File | Lokasi | Peran |
| --- | --- | --- | --- |
| I1 | data_collection_padi_bebek_FINAL(3).xlsx | Sheet Data Collection Final; khususnya No. 9-29, 35-55, 58-84. | Data collection lokal hasil konsolidasi. |
| I2 | Dokumentasi Expert DSS Padi-Bebek(1).docx | Bagian 4.1-4.11 dan Bagian 5 audit konsistensi. | Expert judgement dan koreksi parameter. |
| I3 | DSS_Padi_Bebek_Rekap_Bersih_v10(1).xlsx | Sheet Dataset Actual Bersih, 36 siklus. | Versi A: test-only. Versi C: split calibration/holdout. |
| I4 | Model Matematika Data Collection DSS Padi Bebek Ekonomi(3).docx | Bagian 2-5 dan tabel parameter/formula. | Model ekonomi sebelum finalisasi; sumber formula yang diaudit. |
| I5 | Kumpulan_Variabel_Rumus_Data_Artikel_Referensi_Scopus_FINAL.xlsx | Daftar Artikel B4A02; Rumus Model baris B4A02; Data B4A02. | Jejak formula Xiong dan source mapping internal. |
| I6 | Notulensi Semi Wawancara Validasi Variabel(1).pdf | Bagian kepadatan, durasi, pola tanam, harga, biologis bebek. | Boundary validation awal Astungkara Way. |


## Referensi Ilmiah dan Status Scopus

Prioritas pencarian diterapkan Bali > Indonesia > ASEAN > Asia > Global dan tahun >2020. Sumber yang tidak memenuhi aturan jurnal Scopus tidak dipromosikan menjadi dasar formula. Xiong et al. (2014) dipertahankan hanya sebagai fallback karena menyediakan closed-form equation density x stocking-time yang tidak ditemukan pada sumber jurnal >2020 yang ditelusuri untuk finalisasi ini.


| Kode | Referensi | Pemakaian dalam model | Verifikasi Scopus |
| --- | --- | --- | --- |
| E2 | Khumairoh, U.; Lantinga, E.A.; Handriyadi, I.; Schulte, R.P.O.; Groot, J.C.J. (2021). Agro-ecological mechanisms for weed and pest suppression and nutrient recycling in high yielding complex rice systems. Agriculture, Ecosystems & Environment, 313, 107385. DOI: 10.1016/j.agee.2021.107385. | Indonesia; mendukung mekanisme duck-foraging, weed/pest suppression, nutrient cycling, dan perlunya kehati-hatian memindahkan mekanisme menjadi koefisien lokal. | Scopus dikonfirmasi pada halaman Elsevier Journal Insights: https://www.sciencedirect.com/journal/agriculture-ecosystems-and-environment/about/insights . |
| E3 | Li, Y. et al. (2023). Developing integrated rice-animal farming based on climate and farmers choices. Agricultural Systems, 204, 103554. DOI: 10.1016/j.agsy.2022.103554. | Asia/global review; mendukung kebutuhan adaptasi IRF terhadap kondisi geografis, iklim, dan konteks lokal. | SCImago: https://www.scimagojr.com/journalsearch.php?q=15061&tip=sid ; metrics based on Scopus data. |
| E4 | Alfiansyah, M.L.; Rahardja, D.P.; Padjung, R. (2025). Advantages of introducing maggot-fed ducks into a rice plantation with and without Azolla. Journal of Water and Land Development, 67, 61-72. DOI: 10.24425/jwld.2025.156040. | Indonesia (Sulawesi Selatan); recent empirical context bahwa timing dan stocking density berpengaruh, tetapi density eksperimen tidak ditransfer ke Bali. | Publisher indexing page secara eksplisit mencantumkan SCOPUS: https://journals.pan.pl/jwld . |



---


## Kontrak Implementasi Backend — Branch C — Farmer-Grouped Calibration/Validation Split

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

| Field API | Tipe | Aturan |
|---|---|---|
| `land_area_are` | number | wajib; `>0` |
| `duck_count` | integer | wajib; `>=0` |
| `rice_variety` | enum | wajib; `sertani` / `inpari` |
| `planting_system` | enum | wajib; `jajar_legowo` / `tegel` |
| `duck_age_days` | integer | wajib; `>=0`; gate saja |
| `planting_date` | date/null | opsional; hanya untuk calendar dates |
| `p_gabah` | number/null | opsional; default branch C `6000`, runtime aktual prioritas |
| `p_duck_buy` | number/null | opsional; default branch C `25000`, runtime aktual prioritas |
| `p_duck_sell` | number/null | opsional; default scenario `45000`, runtime aktual prioritas |
| `c_feed_scenario` | number/null | opsional; tidak ada hidden production default |
| `c_jaring_purchase`, `n_jaring_cycles` | number/null | optional pair; cycles `>0` bila biaya diberikan |
| `c_kandang_purchase`, `n_kandang_cycles` | number/null | optional pair; cycles `>0` bila biaya diberikan |

Tidak ada `duck_duration_days` untuk production yield C0 karena duration effect **tidak identifiable** dan tidak dipromosikan.

### Output canonical branch C

| Field | Semantik |
|---|---|
| `model_variant` | `C_FARMER_GROUPED_LOCAL` |
| `yield_are_kg` | `50.0` |
| `yield_total_kg` | `50*A_are` |
| `model_validation_status` | `LOCAL_CALIBRATED_WITH_LIMITED_HOLDOUT_PERFORMANCE` |
| `parameter_uncertainty_y0_95pct` | `[42.81,55.78]`; deskriptif, bukan prediction interval individual |
| `age_status` | readiness gate |
| `density_are`, `density_status` | density/risk gate |
| `release_hst_min/max`, `withdraw_hst_min/max` | `21–30`, `56–60` |
| `survival_risk` | `HIGH` hanya jika `d_are>8`; selain itu `null` |
| `revenue_gabah` | `Yield_are*A_are*p_gabah` |
| `revenue_duck_all_sold_scenario` | `J*p_duck_sell`; `null` jika `d_are>8` |
| `cost_duck_buy` | `J*p_duck_buy` |
| `cash_contribution_before_optional` | scenario contribution, bukan net profit |
| optional cost/output | hanya jika caller menyediakan nilai |
| `warnings`, `provenance` | source/default dan limitation |

**Field yang harus hilang dari response C:** `N_survive`, `survival_rate`, old baseline `47.8767507`, fixed `Cost_feed`, `Revenue_duck_potential` berbasis survivor, old harvest windows, dan `Net_Cash_Contribution_DSS` legacy.

### Production Yield Engine

```text
Y0_C = 50.0 kg/are
Yield_are = 50.0
Yield_total_kg = 50.0 * land_area_are
```

Jangan mengaktifkan C1/C3/C4 hanya karena coefficient-nya tersedia di dokumentasi penelitian. Coefficient tersebut adalah audit candidate, **bukan production formula**.

### Perubahan file minimum dari master

| Path | Perubahan wajib |
|---|---|
| `app/engines/formula_engine.py` | `Y_BASE` menjadi 50; hapus numerical survival; kalender jadi range; economics jadi scenario contribution |
| `app/engines/impact_engine.py` | keluarkan dari Core; tidak boleh mempengaruhi economic primary |
| `app/services/simulation_service.py` | output C0 + gates; no `N_survive`; optional economics; provenance validation C |
| `app/schemas/dss.py` | update request/default/nullable output, hapus survival number dan legacy cash fields |
| `app/data/seed.py` | Y0=50; default p_gabah=6000, p_buy=25000, p_sell=45000; hapus feed hidden default dan harvest fixed legacy |
| `app/services/visualization_service.py` | benchmark yield 50; density/age zone only; no survival-rate curve |
| `app/domain/models.py`, repository/history | schema v4; record `model_variant=C_FARMER_GROUPED_LOCAL` |
| `tests/*` | untouched holdout replay + boundary tests sesuai `tes_skenario.md` C |

