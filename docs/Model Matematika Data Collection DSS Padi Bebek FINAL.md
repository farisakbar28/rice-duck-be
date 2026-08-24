# MODEL MATEMATIKA EKONOMI DSS PADI-BEBEK

## Versi A - Strict Separation + Evidence Reset

> **STATUS IMPLEMENTASI:** Source of Truth (SoT) untuk backend branch **A — Strict Separation + Evidence Reset**.  
> **Sumber model akademik:** `Model Matematika Ekonomi DSS Padi Bebek - Versi A Final.docx` (versi **non-revisi/pure** yang dipilih untuk implementasi).  
> Dokumen `.docx ... Revisi` hanya arsip dan **bukan** acuan implementasi branch ini.  
> Jika kode, schema, test, README, persistence, visualization, atau dokumentasi lama bertentangan dengan dokumen ini, implementasi harus mengikuti dokumen ini.

---

Catatan Finalisasi:

- Recap Data CRS Bebek dan seluruh dataset turunannya hanya berfungsi sebagai test/validation evidence. Tidak ada angka dari 36 siklus bersih yang boleh membentuk parameter production model.
- Formula hasil konversi kualitatif-ke-numerik pada model ekonomi lama dihapus dari production path. Formula hanya dipertahankan jika merupakan arithmetic/system rule yang transparan atau persamaan referensi yang benar-benar eksplisit.
- Yield backbone yang disetujui adalah persamaan Xiong et al. (2014) dengan status literature-uncalibrated dan validity guard. Model tidak mengekstrapolasi persamaan tersebut secara diam-diam ke rentang lokal yang berada di luar domain artikel.
- Mortalitas biologis tidak dimodelkan secara numerik. Hanya ketika d_are > 8, sistem mengaktifkan survival-risk/status tanpa menetapkan persentase survival.
- Output ekonomi menggunakan istilah kontribusi kas/estimasi skenario, bukan laba bersih final, karena penjualan bebek, pakan, infrastruktur, dan biaya lain tidak seluruhnya memiliki pencatatan yang konsisten.
## 1. Ringkasan Eksekutif

Versi A adalah cabang metodologis paling ketat. Data rekap historis Astungkara Way tidak digunakan untuk fitting, kalibrasi, pemilihan koefisien, atau tuning setelah hasil test terlihat. Konsekuensinya, sejumlah formula lama yang sebelumnya terlihat lokal harus dihapus. Model final berfungsi sebagai DSS berbasis rule lokal untuk density, kalender, umur, dan survival-risk gate; sedangkan yield numerik hanya boleh dihitung ketika input berada di domain persamaan literatur yang dipakai.

Hasil audit menunjukkan incompatibility yang substantif: persamaan Xiong menetapkan 50 <= t <= 80 hari dan 0 < d <= 600 ducks/ha, sedangkan data collection Astungkara Way menempatkan durasi lokal bebek aktif sekitar 28-40 hari. Karena itu, untuk skenario lokal tipikal model harus mengembalikan status OUTSIDE_LITERATURE_DOMAIN, bukan memaksakan angka yield. Ini merupakan konsekuensi langsung pilihan strict separation + evidence reset, bukan kegagalan komputasi.

## 2. Status Klaim dan Prinsip Metodologi


| Status tag | Definisi pemakaian Versi A |
| --- | --- |
| local-calibrated | Tidak digunakan untuk parameter yang berasal dari Recap pada Versi A. Hanya boleh dipakai bila ada data lokal independen yang memang menjadi calibration source. |
| local-estimate | Boundary/range dari data collection atau expert judgement yang belum menjadi pengukuran numerik lengkap. |
| literature-uncalibrated | Persamaan/angka artikel Scopus yang dipertahankan tetapi belum dikalibrasi terhadap kondisi Astungkara Way. |
| system-design | Arithmetic, gate, status rule, atau keputusan DSS yang dibuat eksplisit dan tidak diklaim sebagai hukum biologis. |
| regulatory-locked | Tidak ada parameter aktif pada versi ini. |
| mixed | Output yang menggabungkan runtime input, local-estimate, dan/atau formula berstatus berbeda. |


Rule anti-leakage: I3 (Dataset Actual Bersih) baru boleh dibuka untuk evaluasi setelah struktur dan parameter Versi A dibekukan. Hasil test tidak digunakan untuk mengubah formula atau parameter pada cabang ini.

## 3. Input Model


| Nama masukan | Simbol | Satuan | Status input | Catatan |
| --- | --- | --- | --- | --- |
| Luas area aktif bebek | A_are | are | Wajib | Luas petak yang benar-benar diakses bebek; bukan total kepemilikan lahan. Sumber I1 No.24. |
| Jumlah bebek ditebar | J | ekor | Wajib | Bilangan bulat >=0. |
| Sistem tanam | S | kategori | Wajib | Scope aktif: Jajar Legowo/Jarwo atau Tegel/Konvensional. |
| Varietas padi | V | kategori | Wajib | Scope aktif: Sertani/Seratih atau Inpari. |
| Tanggal tanam | TD | tanggal | Wajib jika output kalender | Jangkar kalender; tidak langsung mengubah yield. |
| Umur bebek saat masuk | U_bebek | hari | Wajib | Dipakai sebagai quality/status gate; tidak menjadi multiplier yield/survival/feed. |
| Harga gabah | p_gabah | Rp/kg | Runtime / fallback | Harga periode aktual diprioritaskan. Fallback referensi lokal hanya jika eksplisit diberi label. |
| Harga beli bebek | p_duck_buy | Rp/ekor | Runtime / fallback | Harga aktual diprioritaskan; fallback lokal Rp25.000/ekor berada dalam range I1 No.39. |
| Harga jual bebek | p_duck_sell | Rp/ekor | Runtime / scenario | Jika tidak tersedia, Rp45.000/ekor hanya local-estimate berbasis expert judgement, bukan harga universal. |


## 4. Mesin Komputasi Matematis

### 4.1 Age/Readiness Gate

**Formula:** `[system-design] age_status = NOT_RECOMMENDED jika U_bebek < 21; LOCAL_READY jika 21 <= U_bebek <= 30; OLDER_CONSERVATIVE jika U_bebek > 30`

Threshold 21-30 hari berasal dari data collection lokal (I1 No.25). Status ini tidak mengubah yield, survival, feed, atau profit secara numerik.

Formula R_age = 0,35/0,15/0,05 dan F_age = 1 - 0,08*R_age dari model lama dikeluarkan dari production path karena magnitude penalti tersebut tidak memiliki kalibrasi numerik lokal yang memadai (audit I4 Bagian 4.1 dan 4.5).

### 4.2 Density Engine

**Formula:** `[system-design] d_are = J / A_are`

Rumus arithmetic langsung. A_are wajib > 0 dan d_are menggunakan area aktif bebek (I1 No.24).

**Formula:** `[system-design] d_ha = 100 * d_are`

Konversi hanya untuk kompatibilitas dengan persamaan literatur yang memakai ducks/ha.

**Formula:** `[mixed] density_status = UNDER jika d_are < 2; RECOMMENDED jika Jarwo: 2<=d_are<=4 atau Tegel: 2<=d_are<=3; WARNING_ABOVE_RECOMMENDED jika di atas rentang sistem sampai 8; HIGH_RISK jika d_are > 8`

Range rekomendasi berasal dari I1 No.20-22 dan expert judgement I2 Bagian 4.1. Bentuk status merupakan system-design; tidak dikonversi menjadi probabilitas kerusakan.

P_over dan P_under kontinu dari model lama dihapus. Batas lokal dipertahankan sebagai classification/risk gate, bukan sebagai probabilitas biologis.

### 4.3 Calendar Engine

**Formula:** `[local-estimate] HST_release_rec in [21,30]`

Data collection I1 No.12; 14 HST tidak dijadikan default lokal.

**Formula:** `[local-estimate] HST_withdraw_rec mengikuti fase heading/berbunga; acuan lokal sekitar 56-60 HST`

Data collection I1 No.13 dan No.26. Fase tanaman lebih penting daripada hard-code tanggal tunggal.

**Formula:** `[system-design] t_local = HST_withdraw - HST_release`

Durasi lokal yang terkumpul sekitar 28-40 hari; contoh praktis 60-28 = 32 hari (I1 No.27).

**Formula:** `[system-design] D_release = TD + HST_release; D_withdraw = TD + HST_withdraw`

Transformasi kalender saja; TD bukan penyebab langsung perubahan yield.

Hard constant t_active=44 (65-21) dari model lama tidak dipertahankan. Sistem menyimpan window/range dan fase heading sebagai trigger penarikan.

### 4.4 Survival Risk Gate

**Formula:** `[system-design] survival_risk = HIGH jika d_are > 8`

Expert judgement menempatkan >8 ekor/are sebagai zona risiko jauh lebih serius, tetapi tidak menetapkan fungsi atau persentase mortalitas final (I2 Bagian 4.1). Pada d_are <= 8 tidak ada koreksi survival dalam model karena mortalitas diperlakukan sebagai faktor pengelolaan petani di luar scope.

Model tidak memprediksi N_survive maupun N_sold. Expert judgement menyatakan bebek hidup tidak selalu dijual (I2 Bagian 4.2). Karena itu, revenue penjualan bebek hanya boleh dibaca sebagai skenario all-sold atau menggunakan angka penjualan aktual jika tersedia.

### 4.5 Yield Engine - Literature Backbone dengan Validity Guard

**Formula:** `[literature-uncalibrated] x_kg_ha(d,t) = (-0.0103*d_ha^2 + 2.6314*d_ha + 7569.4) * exp(-((t-80)^2)/(2*80^2))`

Persamaan eksplisit Xiong et al. (2014), E1/I5. d menggunakan ducks/ha dan x menghasilkan kg/ha.

**Formula:** `[system-design] x_kg_are = x_kg_ha / 100`

Konversi satuan dari kg/ha menjadi kg/are.

**Formula:** `[system-design] yield_valid = TRUE hanya jika 0 < d_ha <= 600 dan 50 <= t <= 80; selain itu yield_status = OUTSIDE_LITERATURE_DOMAIN`

Validity guard mengikuti domain yang dinyatakan eksplisit oleh Xiong. Sistem tidak melakukan clamp atau extrapolation sebagai output production.

Konsekuensi lokal: t_local Astungkara Way sekitar 28-40 hari tidak overlap dengan 50-80 hari pada E1. Maka skenario lokal tipikal tidak memperoleh angka yield production dari Versi A. Nilai hasil extrapolation boleh dihitung hanya sebagai diagnostic sensitivity dan wajib diberi label out-of-domain.

### 4.6 Economic Differential-Costing Engine

**Formula:** `[mixed] Revenue_gabah = x_kg_are * A_are * p_gabah`

Hanya dihitung bila yield_valid=TRUE. p_gabah runtime diprioritaskan.

**Formula:** `[system-design] C_duck_buy = J * p_duck_buy`

Arithmetic costing; tidak memodelkan mortalitas.

**Formula:** `[mixed] Revenue_duck_all_sold_scenario = J * p_duck_sell`

Skenario maksimum sederhana, bukan prediksi jumlah terjual. Field ini dinonaktifkan jika d_are > 8 karena survival berada pada zona risiko tinggi dan tidak dimodelkan secara numerik.

**Formula:** `[mixed] CashContribution_before_optional = Revenue_gabah + Revenue_duck_all_sold_scenario - C_duck_buy`

Disebut kontribusi kas skenario, bukan laba bersih.

**Formula:** `[system-design] C_infra_cycle = C_jaring_purchase/n_jaring_cycles + C_kandang_purchase/n_kandang_cycles`

Hanya aktif jika nilai aktual/default scenario dipilih. I1 No.48-55 memberi range lokal, bukan biaya universal per are.

**Formula:** `[mixed] CashContribution_after_optional = CashContribution_before_optional - C_feed_scenario - C_infra_cycle`

C_feed_scenario dan infrastruktur ditampilkan sebagai komponen terpisah; jika tidak tersedia, output tidak menyamarkan nilainya sebagai nol terukur.

Fallback economic evidence: p_duck_buy sekitar Rp25.000-Rp28.000/ekor (I1 No.39); expert judgement menilai harga jual normal minimal sekitar Rp45.000/ekor dan mixed-feed sekitar Rp20.000/ekor/siklus sebagai lower-bound scenario (I2 Bagian 4.5-4.6). Nilai feed tersebut tidak menjadi hidden default production karena I1 No.43-47 menunjukkan variasi dan ketiadaan standar lokal yang stabil.

## 5. Parameter Final Versi A


| Parameter | Nilai | Satuan | Status | Evidence/catatan |
| --- | --- | --- | --- | --- |
| A_are | runtime | are | system-design | Area aktif bebek; I1 No.24. |
| J | runtime | ekor | system-design | Jumlah bebek ditebar. |
| U_bebek | runtime | hari | local-estimate | Quality gate 21-30 hari; I1 No.25. |
| d_rec_low | 2 | ekor/are | local-estimate | Batas bawah rekomendasi umum; I1 No.22. |
| d_rec_high_Jarwo | 4 | ekor/are | local-estimate | Batas atas rekomendasi konservatif Jarwo; I1 No.22 + I2 4.1. |
| d_rec_high_Tegel | 3 | ekor/are | local-estimate | I1 No.20 + I2 4.1. |
| d_high_risk | 8 | ekor/are | local-estimate | Boundary expert; bukan probabilitas mortalitas. |
| HST_release_low | 21 | HST | local-estimate | I1 No.12. |
| HST_release_high | 30 | HST | local-estimate | I1 No.12. |
| HST_heading_low | 56 | HST | local-estimate | I1 No.13. |
| HST_heading_high | 60 | HST | local-estimate | I1 No.13; observasi lebih luas tetap dicatat sebagai uncertainty. |
| t_local_low | 28 | hari | local-estimate | I1 No.27. |
| t_local_high | 40 | hari | local-estimate | I1 No.27. |
| p_gabah_fallback | Rp6.000 | Rp/kg | local-estimate | Diterima sebagai realistis pada expert judgement; runtime price tetap prioritas. |
| p_duck_buy_fallback | Rp25.000 | Rp/ekor | local-estimate | Lower bound range lokal Rp25-28 ribu; I1 No.39. |
| p_duck_sell_scenario | Rp45.000 | Rp/ekor | local-estimate | Minimum normal menurut expert judgement; runtime market price prioritas. |
| C_feed_expert_scenario | Rp20.000 | Rp/ekor/siklus | local-estimate | Optional sensitivity/lower-bound mixed-feed; tidak hidden default. |
| Xiong a2 | -0.0103 | coefficient | literature-uncalibrated | E1/I5. |
| Xiong a1 | 2.6314 | coefficient | literature-uncalibrated | E1/I5. |
| Xiong a0 | 7569.4 | kg/ha intercept | literature-uncalibrated | E1/I5. |
| Xiong t_center | 80 | hari | literature-uncalibrated | E1/I5. |


## 6. Evaluasi Test-Only Versi A

Dataset test tetap 36 siklus. Sebanyak 33/36 siklus berada dalam domain density Xiong (<=600 ducks/ha), sedangkan 3/36 berada di atas domain tersebut. Tidak ada (0/36) skenario lokal dengan t=32 hari yang berada pada domain t Xiong 50-80 hari. Karena itu, primary local validation metric untuk formula Xiong tidak didefinisikan pada Versi A.


| Evaluasi | MAE kg/are | RMSE | MedAE | Bias | Interpretasi |
| --- | --- | --- | --- | --- | --- |
| Primary test | Tidak dihitung | - | - | - | Semua t lokal berada di luar domain artikel; menghitung error sebagai validation akan menyesatkan. |
| Diagnostic sensitivity: t=32 (out-of-domain), 33 density-valid cycles | 17.012 | 21.689 | 15.225 | 16.427 | Hanya diagnostic extrapolation; bukan validation production. |
| Literature lower bound: t=50, 33 density-valid cycles | 23.810 | 27.656 | 22.462 | 23.689 | Valid terhadap batas t artikel, tetapi tidak merepresentasikan local duration 28-40 hari. |


Diagnostic t=32 menunjukkan bias positif sekitar 16,43 kg/are pada subset density-valid. Angka ini memperkuat alasan untuk tidak menyebut extrapolation sebagai prediksi lokal terkalibrasi. Hasil test tidak dipakai kembali untuk memperbaiki koefisien Versi A.

## 7. Formula Lama yang Dikeluarkan dari Production Path


| Formula/parameter lama | Status final | Alasan |
| --- | --- | --- |
| R_age = 0,35/0,15/0,05 | Removed | Magnitude penalti berasal dari konversi kualitatif. Diganti status gate. |
| P_over dan P_under kontinu | Removed | Boundary lokal dipertahankan sebagai status, bukan probabilitas. |
| lambda_eff = 0,78125*(...) | Removed | Ceiling berasal dari recap dan sold count tidak identik dengan survival. |
| F_age = 1 - 0,08*R_age | Removed | Tidak ada kalibrasi pengaruh umur ke yield. |
| F_density_bio dengan alpha=0,15; beta=0,25 | Removed | Bentuk fungsi baru internal; tidak dipakai pada evidence-reset branch. |
| F_sys=1,211 dan F_var=1 empiris | Removed | Berasal dari dataset recap yang sekarang test-only. |
| Material temporal max(0,0,02*t-0,6) | Sandbox | Interpolasi internal tidak menjadi active economic output. |
| R_weed(d), R_pest(d) | Sandbox | Mekanisme didukung, kurva numerik density tidak memiliki kalibrasi lokal. |
| C_feed=J*4500*(1+...) | Removed | Rp4.500 berasal dari recap dan multipliers constructed. |
| Regression infrastructure coefficient | Removed | Berasal dari recap; diganti arithmetic amortization transparan. |


## 8. Output DSS Final Versi A


| Output | Format | Kondisi | Status |
| --- | --- | --- | --- |
| d_are | angka | Selalu jika A_are>0 | system-design |
| density_status | UNDER/RECOMMENDED/WARNING/HIGH_RISK | Selalu | mixed |
| age_status | NOT_RECOMMENDED/LOCAL_READY/OLDER_CONSERVATIVE | Selalu | system-design |
| HST_release/HST_withdraw | range/tanggal | Jika varietas dan TD tersedia | mixed |
| survival_risk | HIGH | Hanya jika d_are>8 | system-design |
| yield_status | VALID/OUTSIDE_LITERATURE_DOMAIN | Selalu | system-design |
| x_kg_are | kg/are | Hanya yield_valid=TRUE | literature-uncalibrated |
| Revenue_gabah | Rp | Hanya yield_valid dan price tersedia | mixed |
| Revenue_duck_all_sold_scenario | Rp | Harga jual tersedia; dinonaktifkan jika d_are>8 | mixed |
| C_duck_buy | Rp | Jika harga beli tersedia | system-design |
| C_feed_scenario | Rp | Opsional; nilai aktual/sensitivity | mixed |
| C_infra_cycle | Rp/siklus | Opsional | mixed |
| CashContribution_before_optional | Rp | Jika komponen prerequisite tersedia | mixed |
| CashContribution_after_optional | Rp | Jika feed/infrastruktur dipilih | mixed |


## 9. Keterbatasan Final Versi A

- Tidak ada overlap antara rentang durasi lokal 28-40 hari dan domain Xiong 50-80 hari. Ini adalah limitation utama numerical yield prediction pada cabang A.
- Mortalitas tidak dimodelkan secara numerik pada density sampai 8 ekor/are; hanya density >8 yang memicu survival-risk gate. Boundary ini bukan estimasi persentase mortalitas.
- Model tidak memprediksi jumlah bebek yang dijual. All-sold revenue adalah scenario ceiling sederhana.
- Feed, pupuk, weeding, pestisida/herbisida, dan manfaat hara tidak menjadi active numeric benefit tanpa data yang lebih kuat.
- Tidak ada optimal d* atau t* berbasis continuous optimization pada production path. Model memberi recommended range dan risk gate karena formula objective lama dibersihkan.
- Jika penelitian membutuhkan angka yield lokal aktif untuk durasi 28-40 hari, diperlukan persamaan jurnal yang valid pada domain tersebut atau dataset calibration independen yang tidak menggunakan test set Versi A.
## 10. Traceability Keputusan Final


| Keputusan | Pilihan | Implementasi |
| --- | --- | --- |
| Decision 1 | A - Strict separation | I3 hanya test/validation; semua recap-derived production parameters dicabut. |
| Decision 2 | 2A - Evidence reset | Formula kualitatif-ke-numerik dihapus atau dikembalikan menjadi status/range. |
| P1 | Approved | Xiong active numerical backbone hanya dengan validity guard. |
| P2 | Approved with scope rule | Tidak ada koreksi survival numerik sampai boundary 8; d_are>8 memicu survival risk/status tanpa persentase. |
| P3 | Approved | Output ekonomi disebut cash contribution/scenario estimate, bukan net profit final. |
| P4 | Tidak berlaku ke A | Split calibration/holdout hanya untuk Versi C. |


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
| E1 | Xiong, D.; Fang, K.; Luo, Y.; Dai, X. (2014). Modeling of Duck Density and Complex Stocking Time in Rice-Duck Agroecosystems in Terms of Economic and Ecological Benefits. Mathematical Problems in Engineering, 2014, 487537. DOI: 10.1155/2014/487537. | Fallback formula yield; domain 0<d<=600 ducks/ha dan 50<=t<=80 hari. | SCImago journal record: https://www.scimagojr.com/journalsearch.php?q=13082&tip=sid . Journal memiliki rekam Scopus historis; source kemudian discontinued, sehingga tidak diperlakukan sebagai sumber baru >2020. |
| E2 | Khumairoh, U.; Lantinga, E.A.; Handriyadi, I.; Schulte, R.P.O.; Groot, J.C.J. (2021). Agro-ecological mechanisms for weed and pest suppression and nutrient recycling in high yielding complex rice systems. Agriculture, Ecosystems & Environment, 313, 107385. DOI: 10.1016/j.agee.2021.107385. | Indonesia; mendukung mekanisme duck-foraging, weed/pest suppression, nutrient cycling, dan perlunya kehati-hatian memindahkan mekanisme menjadi koefisien lokal. | Scopus dikonfirmasi pada halaman Elsevier Journal Insights: https://www.sciencedirect.com/journal/agriculture-ecosystems-and-environment/about/insights . |
| E3 | Li, Y. et al. (2023). Developing integrated rice-animal farming based on climate and farmers choices. Agricultural Systems, 204, 103554. DOI: 10.1016/j.agsy.2022.103554. | Asia/global review; mendukung kebutuhan adaptasi IRF terhadap kondisi geografis, iklim, dan konteks lokal. | SCImago: https://www.scimagojr.com/journalsearch.php?q=15061&tip=sid ; metrics based on Scopus data. |
| E4 | Alfiansyah, M.L.; Rahardja, D.P.; Padjung, R. (2025). Advantages of introducing maggot-fed ducks into a rice plantation with and without Azolla. Journal of Water and Land Development, 67, 61-72. DOI: 10.24425/jwld.2025.156040. | Indonesia (Sulawesi Selatan); recent empirical context bahwa timing dan stocking density berpengaruh, tetapi density eksperimen tidak ditransfer ke Bali. | Publisher indexing page secara eksplisit mencantumkan SCOPUS: https://journals.pan.pl/jwld . |



---


## Kontrak Implementasi Backend — Branch A — Strict Separation + Evidence Reset

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

`/optimizer/recommend` pada master adalah stub dan berada di luar SoT. Endpoint tersebut tidak dipasang pada API riset Model A; **dilarang** menghidupkan kembali formula legacy melalui optimizer lalu mencampurkannya ke `/dss/simulate`.

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

Field Core:

| Field API | Tipe | Aturan |
|---|---|---|
| `land_area_are` | number | wajib; `>0` |
| `duck_count` | integer | wajib; `>=0` |
| `rice_variety` | enum | wajib; `sertani` / `inpari` |
| `planting_system` | enum | wajib; `jajar_legowo` / `tegel` |
| `duck_age_days` | integer | wajib; `>=0` |
| `planting_date` | date/null | opsional; hanya untuk mengubah HST menjadi tanggal kalender |
| `p_gabah` | number/null | opsional; runtime aktual prioritas, fallback `6000` hanya dengan metadata `local-estimate` |
| `p_duck_buy` | number/null | opsional; runtime aktual prioritas, fallback `25000` hanya dengan metadata `local-estimate` |
| `p_duck_sell` | number/null | opsional; runtime aktual prioritas, fallback skenario `45000` dengan metadata `local-estimate` |
| `literature_duration_days` | number/null | **conditional technical input** untuk mencoba Yield Xiong; jika tidak diberikan, Core lokal tidak membuat angka yield Xiong |
| `c_feed_scenario` | number/null | opsional; biaya total skenario feed per siklus, tanpa hidden default |
| `c_jaring_purchase` | number/null | opsional |
| `n_jaring_cycles` | number/null | wajib `>0` jika `c_jaring_purchase` diberikan |
| `c_kandang_purchase` | number/null | opsional |
| `n_kandang_cycles` | number/null | wajib `>0` jika `c_kandang_purchase` diberikan |

`literature_duration_days` bukan local-calibrated parameter. Ia hanya membuka jalur evaluasi persamaan Xiong bila caller memang mempunyai/ingin menguji nilai `t`. Tanpa nilai tersebut, local operational window `28–40` hari sendiri sudah menunjukkan bahwa numerical literature yield tidak layak dipaksakan.

### Output canonical branch A

| Field | Semantik |
|---|---|
| `model_variant` | `A_STRICT_SEPARATION` |
| `age_status` | `NOT_RECOMMENDED`, `LOCAL_READY`, `OLDER_CONSERVATIVE` |
| `density_are`, `density_ha` | hasil aritmetika |
| `density_status` | `UNDER`, `RECOMMENDED`, `WARNING_ABOVE_RECOMMENDED`, `HIGH_RISK` |
| `release_hst_min/max` | `21/30` |
| `withdraw_hst_min/max` | `56/60` |
| `release_date_min/max`, `withdraw_date_min/max` | tanggal atau `null` bila `planting_date` tidak ada |
| `survival_risk` | `HIGH` hanya jika `d_are>8`; selain itu `null` |
| `yield_status` | `VALID` atau `OUTSIDE_LITERATURE_DOMAIN` |
| `yield_are_kg`, `yield_total_kg` | angka hanya bila Xiong domain valid; selain itu `null` |
| `revenue_gabah` | hanya bila yield numeric tersedia |
| `revenue_duck_all_sold_scenario` | `J*p_duck_sell`; `null` jika `d_are>8` |
| `cost_duck_buy` | `J*p_duck_buy` |
| `cash_contribution_before_optional` | hanya bila prerequisite revenue tersedia |
| `cost_feed_scenario`, `cost_infra_cycle` | child component opsional |
| `cash_contribution_after_optional` | hanya jika optional-cost scenario memang dipilih |
| `warnings`, `provenance` | wajib menjelaskan fallback, domain mismatch, dan high-risk |

**Field yang harus hilang dari response A:** `N_survive`, `survival_rate`, `Revenue_duck_potential` berbasis survivor, `Cost_feed` hidden/default, `Net_Cash_Contribution_DSS` legacy, dan numerical sandbox yang seolah production.

### Implementasi Yield Xiong

Gunakan `Decimal`/precision tinggi sebagaimana pola repository sekarang; pembulatan hanya di DTO boundary.

```text
d_ha = 100 * d_are

x_kg_ha = (-0.0103*d_ha^2 + 2.6314*d_ha + 7569.4)
          * exp(-((t-80)^2)/(2*80^2))

valid iff: 0 < d_ha <= 600 and 50 <= t <= 80
x_kg_are = x_kg_ha / 100
```

Tidak boleh clamp `t`, mengganti `t` dengan 50 secara diam-diam, atau menghitung extrapolation sebagai production result.

### Perubahan file minimum dari master

| Path | Perubahan wajib |
|---|---|
| `app/engines/formula_engine.py` | hapus constant yield dan numerical survival; implement age/density/calendar range, survival-risk gate, Xiong + validity guard, economic scenario |
| `app/engines/impact_engine.py` | keluarkan dari Core; bila dipertahankan, label research-only dan jangan dipanggil otomatis |
| `app/services/simulation_service.py` | conditional yield/economics; tidak membuat `N_survive`; tidak memberi universal survival warning pada kondisi normal |
| `app/schemas/dss.py` | request optional price/date/duration/optional costs; response nullable untuk unavailable output |
| `app/data/seed.py` | hapus `47.8767507`, `52500`, fixed feed `20000`, fixed HST 21/65 sebagai production constants; simpan range/default branch A |
| `app/services/visualization_service.py` | hapus numerical survival curve; visualisasikan density/age gates dan Xiong domain/reference hanya jika valid |
| `app/domain/models.py`, repository/history | schema v4; persistence mengikuti nullable field A |
| `tests/*` | rebuild sesuai `docs/tes_skenario.md` A |
