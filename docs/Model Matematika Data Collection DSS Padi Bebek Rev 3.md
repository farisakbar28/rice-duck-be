MODEL MATEMATIKA DAN DATA COLLECTION

DSS Yield Prediction Padi-Bebek - Revisi 3 Final


Catatan Revisi 3 Final:

- Scope aktif varietas padi hanya Sertani/Seratih dan Inpari berdasarkan data collection lokal final. Varietas lain menjadi limitation/pengembangan lanjutan, bukan lookup aktif DSS Rev 3.
- Scope aktif sistem tanam hanya Jajar Legowo/Jarwo dan Tegel/Konvensional berdasarkan data collection lokal final. SRI, double transplant, dan sistem lain menjadi limitation/pengembangan lanjutan, bukan lookup aktif DSS Rev 3.
- q_feed fallback operasional ditetapkan 0.10 kg/ekor/hari dari artikel referensi A02 dengan status literature-uncalibrated.
- K_max Tegel ditetapkan sebagai rentang 2-3 ekor/are dengan batas maksimum praktis 3 ekor/are.
- Hara N/P/K aktif dihitung dari kappa_N/P/K literatur dengan status literature-uncalibrated / estimation-only.
- V_eco2 tetap aktif sebagai estimasi penghematan pestisida/herbisida dari rumus literatur.
- Optimality memakai exact best optimizer match dengan objective adaptive: yield + ecology - risk penalty; profit masuk hanya jika numeric-ready; environment tidak masuk objective.
- Boundary risk: LOW jika density < 0.8*K_max; SAFE jika 0.8*K_max <= density <= K_max.
- Emisi/lingkungan dan variabel kondisi operasional non-daily-duck dipindahkan menjadi limitation penelitian.
- Label status menggunakan estimation-only secara konsisten.


# 1. Ringkasan Eksekutif

- Data collection lokal tersedia: status local-calibrated atau local-estimate. Data hanya berasal dari artikel referensi: status literature-uncalibrated dan wajib diberi catatan belum dikalibrasi lokal oleh Astungkara Way.

- Backbone model yield, nilai bebek, manfaat pupuk, dan manfaat pestisida/herbisida tetap mengikuti model, tetapi koefisien tersebut diposisikan sebagai baseline literatur sampai ada kalibrasi lokal.

- Modul ekonomi lokal ada melalui V_duck_lokal, C_feed, C_infra, V_gulma, dan Laba_bersih. Semua komponen tetap aktif sebagai perhitungan estimasi; data lokal diprioritaskan, sedangkan data/rumus dari artikel referensi dipakai dengan status literature-uncalibrated atau belum dikalibrasi lokal oleh Astungkara Way.

- Revisi 3 menetapkan modul emisi/lingkungan (CO2e, GHGI, Reduksi_CH4, dan relasi DO-to-CH4) tidak menjadi komponen aktif perhitungan DSS karena data CH4, N2O, baseline emisi konvensional, dan DO tidak tersedia dari mitra. Bagian tersebut dicatat sebagai limitation penelitian, bukan output numerik sistem.

| Keputusan final | Isi keputusan | Dampak ke DSS/paper |
| --- | --- | --- |
| Tidak menghapus data referensi | Semua rumus/angka referensi tetap dicantumkan sesuai relevansi. | Diberi label literature-uncalibrated; tidak overclaim sebagai data Astungkara Way. |
| Area aktif bebek menjadi wajib | A_are yang dipakai dalam kepadatan adalah luas petak aktif bebek. | Total lahan berbeda dari area bebek: risiko bias rekomendasi dapat muncul. |
| Satuan are menjadi utama | d_are untuk DSS/petani/paper lokal; d_lit_ha hanya catatan rumus literatur. | Menghindari kesalahan skala 100 kali pada rumus Xiong tanpa menjadikan hektar sebagai satuan utama. |
| Durasi mengikuti fase padi | HST_masuk + t <= HST_heading. | Menjaga bebek keluar sebelum risiko malai/bulir. |
| V_duck dipisah | V_duck_Xiong untuk referensi; V_duck_lokal untuk rupiah lokal. | Mencegah double counting biaya pakan dan salah konteks mata uang. |
| Emisi menjadi limitation penelitian | CO2e/GHGI/Reduksi_CH4/DO-to-CH4 tidak menjadi komponen aktif perhitungan DSS Rev 3 karena data CH4, N2O, baseline emisi konvensional, dan DO tidak tersedia dari mitra. | Mencegah overclaim; emisi hanya dijelaskan sebagai keterbatasan dan peluang riset lanjutan. |



# 2. Hirarki Sumber Data dan Status Klaim

| Status klaim | Definisi | Contoh parameter/rumus | Cara menulis di paper / sistem |
| --- | --- | --- | --- |
| Local-calibrated | Nilai sudah kuat dari data collection lokal dan cukup konsisten untuk dijadikan default. | C_jaring, C_kandang, p_gabah. | Boleh disebut parameter lokal awal. |
| Local-estimate | Ada data lokal tetapi belum lengkap atau hanya rata-rata. | lambda 0.35-0.67, HST_masuk 21-30, HST_heading sekitar 56-60, C_gulma range. | Sebut sebagai estimasi lokal; simpan range. |
| Literature-uncalibrated | Nilai/rumus dari artikel referensi, belum diuji lokal Astungkara Way. | x(d,t), V_duck_Xiong, V_eco1, V_eco2, kappa_N/P/K, q_feed referensi. | Sebut sebagai baseline referensi belum dikalibrasi lokal. |
| Estimation-only | Output numerik dihitung sebagai estimasi karena memakai rumus/data referensi atau data lokal parsial. | N/P/K_tanah, Dung_total, V_eco1, V_eco2. | Jangan ditulis sebagai data terukur lokal; tulis sebagai estimasi model. |
| System-design | Rumus dibuat untuk aturan DSS, bukan rumus eksplisit jurnal. | P_rate, r_gulma, risk score, status output/objective rule. | Sebut sebagai desain sistem/decision rule. |
| Formula-kept / belum terkalibrasi lokal | Rumus/data tetap dicantumkan dan dihitung hanya untuk komponen yang masih menjadi ruang lingkup DSS Rev 3. | C_feed referensi, N/P/K_tanah, V_eco1, V_eco2. | Tampilkan sebagai estimasi/catatan model dengan label belum dikalibrasi lokal oleh Astungkara Way, bukan angka final lokal. |





# 3. Data Collection: Parameter Lokal dan Referensi

| Parameter | Nilai final / range | Satuan | Sumber | Status | Catatan pemakaian |
| --- | --- | --- | --- | --- | --- |
| A_are | Runtime input | are | Input petani / data collection | Local-calibrated: area aktif jelas | Luas petak aktif bebek. Total lahan berbeda: kepadatan wajib memakai area aktif. |
| J | Runtime input | ekor | Input petani | Local-calibrated | Jumlah bebek ditebar; integer >= 0. |
| V | Sertani/Seratih; Inpari | kategori | Data collection lokal final | Local-estimate lookup | Scope aktif DSS Rev 3 hanya dua kelompok varietas yang paling kuat muncul pada data collection lokal final. Varietas lain menjadi limitation/pengembangan lanjutan. |
| S | Jajar Legowo/Jarwo; Tegel/Konvensional | kategori | Data collection lokal final | Local-estimate lookup | Scope aktif DSS Rev 3 hanya dua sistem tanam yang muncul pada praktik padi-bebek lokal. Sistem lain menjadi limitation/pengembangan lanjutan. |
| TD | Runtime input | tanggal | Input petani | Local-estimate | Jangkar kalender; tidak langsung masuk yield. |
| U_bebek | 14-21 hari umum; 21-30 hari lebih aman lokal | hari | Data collection | Local-estimate | Umur 21 hari kadang masih lemah; 30 hari lebih aman tetapi biaya bisa berbeda. |
| HST_masuk | 21-30; default konservatif 28 untuk contoh Sertani/CRS lambat | HST | Data collection | Local-estimate | Normal bisa 21 HST; pertumbuhan lambat: 28-32 HST. |
| HST_heading | 56-60; range 40-65 | HST | Data collection | Local-estimate | Batas tarik bebek utama; gunakan istilah keluar malai. |
| t_lokal_aktif | Default 32; range praktis 28-40 | hari | Turunan HST_masuk-heading | Local-estimate | Contoh: masuk 28 HST, tarik 60 HST = 32 hari. |
| K_max_are Jarwo | Default aman 4; range acuan 4-8; 5-6 hanya uji terbatas | ekor/are | Data collection + referensi | Local-estimate | Default aman bukan batas maksimum teoritis. |
| K_max_are Tegel | 2-3; K_max praktis 3 | ekor/are | Data collection | Local-estimate | Rentang lokal 2-3 ekor/are. Nilai 3 dipakai sebagai batas maksimum praktis; nilai 2 sebagai batas bawah rekomendasi praktis. |
| Kepadatan rekomendasi umum | 2-4 | ekor/are | Data collection | Local-estimate | 4 ekor/are mulai memberi profit; 5-6 uji terbatas. |
| lambda | 0.35-0.67; default awal 0.67 pada kondisi tidak ada data pasti | rasio 0-1 | Data collection | Local-estimate | 0.67 adalah estimasi atas, bukan rata-rata final. |
| daily_duck_grazing_hours | sekitar 10 | jam/hari | Data collection | Local-estimate | Untuk t_effective; bukan pengganti t model Xiong. |
| baseline_hours | 12 | jam/hari | Model operasional | System-design | Harus konsisten di sistem. |
| p_gabah_konv / p0 | Rp5.600-Rp5.700 | Rp/kg | Data collection | Local-estimate | Pisahkan gabah dan beras; gunakan harga periode yang sama. |
| p_gabah_RD | Belum final; dapat sama atau premium dengan data pendukung | Rp/kg | Data collection | Parsial | Jangan klaim premium pada kondisi harga lokal belum dikunci/didapatkan. |
| rendemen gabah-beras | sekitar 50%; range 46-60 | persen | Data collection | Local-estimate | Khusus perspektif beras. |
| p_duck_buy | Rp25.000-Rp28.000 | Rp/ekor | Data collection | Local-estimate | Umur pembelian memengaruhi risiko adaptasi. |
| p_duck | Rp30.000-Rp60.000; contoh Rp35.000-45.000 | Rp/ekor | Data collection | Local-estimate | Bobot jual belum tersedia; gunakan per ekor. |
| q_feed lokal | Belum tersedia | kg/ekor/hari | Data collection | Input-belum-tersedia-lokal | Data lokal tetap dikumpulkan untuk kalibrasi. Selama lokal belum tersedia, C_feed tetap aktif memakai q_feed fallback operasional 0.10 dengan status literature-uncalibrated. |
| q_feed fallback operasional | 0.10 | kg/ekor/hari | Artikel referensi A02 | Literature-uncalibrated | Dipakai sebagai fallback operasional C_feed saat q_feed lokal belum tersedia. Nilai 0.10 berasal dari angka eksplisit literatur “Average feed consumed per duck per day = 0.1 kg/day”; bukan data lokal Astungkara Way. |
| p_feed | Input/parameter lokal; belum default final | Rp/kg | Data collection | Parsial | Dipakai untuk C_feed. Harga pakan lokal belum final: gunakan nilai referensi/estimasi dengan status sumber data yang eksplisit. |
| C_jaring | Rp1.200.000-Rp1.350.000/200 m | Rp | Data collection | Local-estimate | Angka terbaru Rp1.350.000; amortisasi per siklus. |
| life_jaring | 2-3 | siklus | Data collection | Local-estimate | Amortisasi Rp450.000-Rp675.000/siklus untuk 200m. |
| C_kandang | Rp600.000/unit 2x1m | Rp | Data collection | Local-estimate | Ukuran dan jumlah unit disesuaikan kebutuhan. |
| life_kandang | 3-4 | siklus | Data collection | Local-estimate | Amortisasi Rp150.000-Rp200.000/siklus/unit. |
| P_N/P_P/P_K | Rp2.400-Rp3.000 awal untuk pupuk subsidi; SP-36/KCl perlu dipisah | Rp/kg | Data collection | Parsial | Dipakai pada V_pupuk_lokal dan V_eco1. Harga lokal parsial: gunakan data lokal yang ada dan lengkapi dengan referensi berstatus literature-uncalibrated. |
| C_gulma | Rp6.000-Rp25.000 tipikal; ekstrem Rp70.000-Rp72.000 | Rp/are/siklus | Data collection | Local-estimate | Gunakan tipikal; ekstrem sebagai outlier. |





# 4. Data Referensi yang Tetap Dipakai tetapi Belum Dikalibrasi Lokal

| Komponen | Nilai/rumus referensi | Mengapa tetap dipakai | Catatan wajib |
| --- | --- | --- | --- |
| x(d,t) | (-0.0103*d_lit_ha^2 + 2.6314*d_lit_ha + 7569.4) * exp(-((t-80)^2)/(2*80^2)); x_kg_are = x_kg_ha_note/100 | Backbone yield padi-bebek dari referensi utama dalam workbook. | Literature-uncalibrated; dikalibrasi dengan alpha_local setelah data panen lokal cukup. Output DSS memakai kg/are. |
| V_duck_Xiong | [-0.0096*d_lit_ha^2 + (11.3861 + 14.4*lambda)*d_lit_ha - 0.18*lambda*t*d_lit_ha + 17.0857] * A_ha_note | Model nilai bebek dari referensi padi-bebek. | Koefisien ekonomi bukan rupiah/Bali; jangan dipakai sebagai profit lokal final. d_lit_ha dan A_ha_note hanya catatan rumus literatur. |
| Dung_total 2 fase | t<=50: (t/50)*4; t>50: 4+(t-50)*0.2 | Rumus fase tersedia di referensi dan dibutuhkan untuk mengaktifkan estimasi kotoran serta N/P/K_tanah. | Aktif sebagai literature-uncalibrated; output lokal diberi label estimasi referensi sampai ada uji kotoran lokal. |
| kappa_N/P/K | kappa_N=0.049; kappa_P=0.072; kappa_K=0.032 pada basis 10 kg kotoran | Nilai referensi tersedia dan dibutuhkan untuk mengaktifkan N_tanah, P_tanah, K_tanah, V_pupuk_lokal, dan V_eco1. | Aktif memakai 0.049, 0.072, 0.032 sebagai literature-uncalibrated; tulis setara pupuk, bukan kandungan pasti lokal. |
| V_eco1_Xiong | [0.02*t - 0.6] * [0.107*P_N + 0.424*P_P + 0.058*P_K] * d_are * lambda * A_are | Rumus penghematan pupuk dari model utama. | Gunakan max(0, raw) agar tidak negatif pada durasi lokal pendek. Bentuk ini ekuivalen dengan rumus literatur setelah konversi are-ha. |
| V_eco2 | (400/(1+exp(-0.036626*d_lit_ha)) - 3.327) * A_ha_note | Rumus penghematan pestisida/herbisida dari model utama. | Pastikan operator pembagian, bukan pangkat; belum kalibrasi harga lokal pestisida. Output DSS tetap dikembalikan sebagai estimasi total pada A_are. |
| q_feed | 0.10 kg/ekor/hari | Dibutuhkan untuk C_feed, V_duck_lokal, Laba_bersih, dan DeltaProfit saat q_feed lokal belum tersedia. | Aktif sebagai fallback operasional literature-uncalibrated dari artikel referensi A02. Tidak diklaim sebagai konsumsi pakan lokal Astungkara Way sampai ada data feed_kg_total/feed_cost_total lokal. |
| REY | REY = Σ(Y_i * P_i) / P_rice | Formula REY ditemukan pada artikel integrated farming dan berguna sebagai indikator akademik untuk mengonversi output non-padi menjadi ekuivalen padi/beras. | Aktif sebagai indikator akademik literature-uncalibrated; tidak menjadi tampilan utama petani pada kondisi berpotensi membingungkan. |



# 5. Model Matematika End-to-End

## 5.1 Input dan Konversi Satuan

[local-calculated] A_are = luas area aktif bebek

A_are menjadi satuan utama DSS. Total lahan tanpa area aktif: hasil diberi warning karena kepadatan dapat bias. Catatan hektar disimpan sebagai A_ha_note = A_are / 100 untuk rumus literatur.

[local-calculated] d_aktual_are = J / A_are

Kepadatan yang dipahami petani. Satuan ekor/are.

[local-calculated] d_lit_ha = d_aktual_are * 100

Catatan konversi untuk rumus literatur Xiong. Output DSS tetap dikembalikan ke ekor/are.

[local-calculated] x_final_kg_are = x_final_kg_ha_note / 100

Output utama petani dan paper lokal ditampilkan sebagai kg/are.

[local-calculated] x_final_ton_ha_note = x_final_kg_are / 10

Hanya catatan pembanding ton/ha. Ekonomi Rp/kg memakai x_final_kg_are * A_are.

## 5.2 Lookup Agronomi dan Kalender

[local-estimate] HST_masuk = lookup(V, S)

Default lokal: 21-30 HST; contoh konservatif 28 HST untuk tanaman lambat/CRS.

[local-estimate] HST_heading = lookup(V)

Default lokal sekitar 56-60 HST, range 40-65 HST. Istilah tampilan: keluar malai.

[local-estimate] K_max_are = lookup(S)

Jarwo default aman 4 ekor/are. Tegel memakai rentang lokal 2-3 ekor/are dengan K_max praktis 3 ekor/are. 5-6 ekor/are hanya skenario uji terbatas pada Jarwo dan tidak menjadi default aman.

[local-calculated] K_max_ha_note = K_max_are * 100

Catatan konversi untuk rumus literatur saat diperlukan; keputusan DSS tetap memakai K_max_are.

[literature-uncalibrated] f_yield = lookup(S)

Untuk DSS Rev 3, f_yield hanya dipakai pada sistem aktif: Tegel/Konvensional dan Jajar Legowo/Jarwo. Nilai dari SRI, double transplant, dan sistem lain tidak menjadi lookup aktif karena tidak muncul kuat pada data collection lokal final dan tidak masuk scope DSS saat ini.

[local-calculated] tanggal_lepas = TD + HST_masuk

Output jadwal ke petani.

[local-calculated] tanggal_tarik = TD + min(HST_masuk + t, HST_heading)

Bebek tidak boleh melewati fase keluar malai.

## 5.3 Durasi, Survival, dan Kotoran

[system-design] 0 < t <= min(t_max_eff, HST_heading - HST_masuk)

t adalah durasi aktif kalender bebek di sawah, bukan HST absolut.

[local-estimate] N_d = J * lambda

lambda disimpan sebagai desimal 0-1. Range lokal awal 0.35-0.67.

[system-design] t_effective = t * (daily_duck_grazing_hours / baseline_hours)

daily_duck_grazing_hours sekitar 10 jam/hari; baseline_hours default sistem 12.

[literature-uncalibrated] Dung_total = (t/50) * 4, pada kondisi t <= 50

Kotoran kumulatif per ekor pada fase 1; belum uji lokal.

[literature-uncalibrated] Dung_total = 4 + (t - 50) * 0.2, pada kondisi t > 50

Kotoran kumulatif per ekor pada fase lanjut; belum uji lokal.

[literature-uncalibrated] Dung_are = Dung_total * d_aktual_are * lambda

Estimasi total kotoran per are dari bebek yang bertahan. Catatan hektar: Dung_ha_note = Dung_are * 100.

## 5.4 Hara Tanah dari Kotoran Bebek

[literature-uncalibrated] N_tanah_are = kappa_N * (Dung_total / 10) * d_aktual_are * lambda

kappa_N=0.049 berbasis referensi literatur; output aktif sebagai estimation-only dan belum uji lokal.

[literature-uncalibrated] P_tanah_are = kappa_P * (Dung_total / 10) * d_aktual_are * lambda

kappa_P=0.072 sebagai P2O5 ekuivalen berbasis referensi literatur; output aktif sebagai estimation-only dan belum uji lokal.

[literature-uncalibrated] K_tanah_are = kappa_K * (Dung_total / 10) * d_aktual_are * lambda

kappa_K=0.032 sebagai K2O ekuivalen berbasis referensi literatur; output aktif sebagai estimation-only dan belum uji lokal.

[mixed] V_pupuk_lokal = (N_tanah_are*P_N + P_tanah_are*P_P + K_tanah_are*P_K) * A_are

Output lokal memakai harga pupuk lokal yang tersedia; harga referensi diberi status literature-uncalibrated.

## 5.5 Model Yield Padi

[literature-uncalibrated] x_base_kg_ha_note = (-0.0103*d_lit_ha^2 + 2.6314*d_lit_ha + 7569.4) * exp(-((t - 80)^2)/(2*80^2)); x_base_kg_are = x_base_kg_ha_note / 100

Backbone literatur. Koefisien belum dikalibrasi untuk Bali/Astungkara Way.

[system-design] P_rate = 0, pada kondisi d_aktual_are <= K_max_are

Tidak ada penalti pada kepadatan di bawah atau sama dengan daya dukung lokal.

[system-design] P_rate = min(P_max, gamma * ((d_aktual_are - K_max_are) / K_max_are)), pada kondisi d_aktual_are > K_max_are

gamma default 0.5; P_max default 1.0. Ini desain sistem, bukan rumus eksplisit jurnal.

[system-design] x_penalized_kg_are = x_base_kg_are * (1 - P_rate)

Yield setelah risiko kepadatan.

[mixed] x_final_kg_are = alpha_local * x_penalized_kg_are * f_yield

alpha_local default 1.0 sampai ada kalibrasi 3-5 siklus data lokal.

## 5.6 Ekonomi Padi, Bebek, Infrastruktur, dan Profit

[local-estimate] R_gabah_RD = x_final_kg_are * A_are * p_gabah_RD

Harga Rp/kg: yield utama wajib kg/are dan dikalikan A_are.

[local-estimate] R_gabah_K = x0_kg_are * A_are * p_gabah_konv

Baseline harus lokasi, varietas, sistem tanam, dan musim yang sebanding.

[mixed] DeltaV_rice = R_gabah_RD - R_gabah_K

Nilai tambah produksi padi terhadap baseline konvensional.

[literature-uncalibrated] REY = Σ(Y_i * P_i) / P_rice

Rice Equivalent Yield aktif sebagai indikator akademik internal untuk mengonversi output non-padi menjadi setara padi/beras. Status literature-uncalibrated untuk hasil yang belum dikalibrasi lokal

[local-estimate] C_duck_buy = J * p_duck_buy

Biaya pembelian bibit/anak bebek.

[mixed] C_feed = J * q_feed * t_effective * p_feed * (1 - kappa_feed_save)

q_feed lokal ada: C_feed memakai q_feed lokal. q_feed lokal tidak ada: C_feed memakai q_feed fallback operasional 0.10 kg/ekor/hari dari artikel referensi A02 sebagai estimasi literature-uncalibrated. p_feed tetap wajib tersedia agar C_feed numerik dapat dihitung.

[local-estimate] V_duck_lokal = N_d * p_duck - C_duck_buy - C_feed

Model rupiah lokal. Tetap aktif sebagai estimasi lokal/parsial; komponen yang belum tersedia lokal dapat memakai data referensi dengan status literature-uncalibrated.

[literature-uncalibrated] V_duck_Xiong = [-0.0096*d_lit_ha^2 + (11.3861 + 14.4*lambda)*d_lit_ha - 0.18*lambda*t*d_lit_ha + 17.0857] * A_ha_note

Model referensi net revenue. Jangan dikurangi C_feed lagi; memakai catatan hektar internal dan belum dikalibrasi lokal.

[local-estimate] C_infra = C_jaring/life_jaring + C_kandang/life_kandang + maintenance_infra

maintenance_infra belum tercatat: default 0 dengan catatan.

[mixed] Laba_bersih = R_gabah_RD + V_duck_lokal + V_eco - C_infra - biaya_tambahan_lain

Rumus tetap aktif. Komponen dari data lokal diberi status local-estimate/local-calibrated, sedangkan komponen dari artikel diberi status literature-uncalibrated/belum dikalibrasi lokal. 

## 5.7 Manfaat Ekologis-Finansial

[literature-uncalibrated] V_eco1_raw = (0.02*t - 0.6) * (0.107*P_N + 0.424*P_P + 0.058*P_K) * d_aktual_are * lambda * A_are

Rumus referensi Xiong untuk penghematan pupuk. Durasi lokal pendek dapat membuat nilai raw negatif.

[system-design] V_eco1 = max(0, V_eco1_raw)

Guard agar output DSS tidak menampilkan penghematan pupuk negatif.

[literature-uncalibrated] V_eco2 = (400/(1 + exp(-0.036626*d_lit_ha)) - 3.327) * A_ha_note, pada kondisi d_aktual_are > 3

Pastikan operator adalah pembagian. V_eco2 tetap aktif dihitung dari rumus literatur sebagai estimasi penghematan pestisida/herbisida, tetapi tidak diklaim sebagai data lokal karena data pestisida/herbisida mitra masih kualitatif dan belum memiliki baseline biaya spesifik.

[system-design] V_eco2 = linear_interpolate(0, nilai_d3_are, d_aktual_are/3), pada kondisi d_aktual_are <= 3

Interpolasi rendah untuk menjaga kontinuitas model.

[system-design] r_gulma = min(1, d_aktual_are / K_max_are)

Proporsi konservatif manfaat gulma dari kepadatan.

[local-estimate] V_gulma = C_gulma * A_are * r_gulma

Komponen lokal yang paling siap karena biaya weeding baseline tersedia.

[mixed] V_eco = V_eco1 + V_eco2 + V_gulma

Total manfaat ekologis-finansial. Tampilkan komponen terpisah agar tidak overclaim.

## 5.8 Lingkungan dan Emisi sebagai Limitation Penelitian

Modul emisi/lingkungan tidak menjadi komponen aktif perhitungan DSS Rev 3.

CO2e, GHGI, Reduksi_CH4, dan relasi DO-to-CH4 tidak dihitung sebagai output numerik karena data F_CH4, F_N2O, baseline emisi konvensional, dan DO tidak tersedia dari mitra. Komponen ini dicatat sebagai limitation penelitian, bukan sebagai hasil estimasi sistem.

Rumus berikut hanya disimpan sebagai konteks riset lanjutan, tidak dipakai dalam objective function dan tidak ditampilkan sebagai output utama DSS Rev 3:

- CO2e_are = F_CH4_are * GWP_CH4 + F_N2O_are * GWP_N2O
- GHGI = CO2e_are / x_final_kg_are
- Reduksi_CH4 = (F_CH4_konv - F_CH4_RD) / F_CH4_konv * 100%
- Y_CH4 = -1.5276*X_DO + 14.770

Data yang dibutuhkan untuk mengaktifkan modul ini pada penelitian lanjutan:

| Data | Kegunaan | Status Rev 3 |
| --- | --- | --- |
| F_CH4_RD | Menghitung CO2e padi-bebek | Tidak tersedia dari mitra |
| F_N2O_RD | Menghitung CO2e padi-bebek | Tidak tersedia dari mitra |
| F_CH4_konv | Menghitung Reduksi_CH4 | Tidak tersedia dari mitra |
| F_N2O_konv | Membandingkan CO2e konvensional vs padi-bebek | Tidak tersedia dari mitra |
| X_DO | Mengaktifkan model DO-to-CH4 | Tidak tersedia dari mitra |
| flooded_days / drainage calendar | Menjelaskan konteks emisi musiman | Tidak tersedia dari mitra |

## 5.9 Objective Function dan Mode Rekomendasi

[system-design] Score_safety = I(HST_masuk + t <= HST_heading) * I(d_are <= K_max_are) * I(A_are > 0)

Safety gate wajib sebelum optimasi. Kandidat yang melewati fase keluar malai atau melewati K_max_are tidak dipilih sebagai skenario aman.

[system-design] Score_yield = norm(x_final_kg_are)

Komponen yield selalu masuk objective karena output yield adalah tujuan utama DSS.

[system-design] Score_ecology = norm(V_eco)

Komponen ekologi masuk objective saat nilainya tersedia sebagai estimasi numerik. V_eco terdiri dari V_eco1, V_eco2, dan V_gulma dengan status sumber data masing-masing.

[system-design] Score_economy = norm(Laba_bersih), hanya jika numeric-ready

Profit hanya masuk objective jika Laba_bersih numerik siap dihitung. Jika harga padi-bebek, harga pakan, atau baseline pembanding belum tersedia, profit tidak dipakai sebagai penentu optimality.

[system-design] Score_environment = tidak digunakan pada DSS Rev 3

Environment/emisi tidak masuk objective karena data F_CH4, F_N2O, baseline emisi konvensional, dan DO tidak tersedia dari mitra. Bagian ini menjadi limitation penelitian.

[system-design] F_active(d,t) = w_yield*Score_yield + w_ecology*Score_ecology + w_economy*Score_economy_ready - w_risk*Risk_penalty

Mode aktif Rev 3 saat data ekonomi belum lengkap:

[system-design] F_current(d,t) = w_yield*Score_yield + w_ecology*Score_ecology - w_risk*Risk_penalty

[system-design] is_optimal = true hanya jika skenario aktual identik dengan best_scenario hasil optimizer berdasarkan objective aktif.

Skenario aktual tidak dianggap optimal hanya karena status risiko SAFE. Rekomendasi disembunyikan hanya ketika actual_density_are, actual_duration_days, actual_duck_count, dan objective score aktual sudah identik dengan kandidat terbaik optimizer dalam toleransi numerik kecil.

[local-calculated] J_rekomendasi = round(d_rekomendasi_are * A_are)

Output jumlah bebek rekomendasi harus integer.

# 6. Kamus Variabel Aktif DSS Rev 3

Catatan Rev 3 Final: kamus ini hanya memuat variabel yang menjadi bagian aktif DSS. Variabel emisi dan variabel kondisi operasional non-daily-duck tidak dimasukkan ke kamus aktif karena menjadi limitation penelitian.

| No | Variabel | Kelompok | Makna | Satuan | Status final |
| --- | --- | --- | --- | --- | --- |
| 1 | d | Decision variable | Kepadatan bebek yang dioptimasi | ekor/are; catatan literatur ekor/ha | Literature baseline + local constraint |
| 2 | t | Decision variable | Durasi bebek aktif di sawah | hari | Local-estimate + system constraint |
| 3 | J | Input | Jumlah bebek ditebar | ekor | Local-calibrated/input |
| 4 | A_are | Input | Luas area aktif bebek | are | Local-calibrated/input |
| 5 | TD | Input | Tanggal tanam padi | tanggal | Local input |
| 6 | V | Input | Varietas padi aktif: Sertani/Seratih dan Inpari | kategori | Local-estimate lookup |
| 7 | S | Input | Sistem tanam aktif: Jajar Legowo/Jarwo dan Tegel/Konvensional | kategori | Local-estimate lookup |
| 8 | U_bebek | Input | Umur bebek saat masuk | hari/minggu | Local-estimate |
| 9 | p_gabah_RD / p_beras_RD | Parameter harga | Harga produk padi-bebek | Rp/kg | Local-estimate/parsial |
| 10 | p_duck | Parameter harga | Harga jual bebek hidup | Rp/ekor | Local-estimate |
| 11 | p_gabah_konv / p_beras_konv | Parameter harga | Harga baseline konvensional | Rp/kg | Local-estimate |
| 12 | x0 | Parameter baseline | Yield baseline konvensional setara | kg/are; catatan ton/ha | Local-estimate / reference fallback |
| 13 | P_N | Parameter harga | Harga pupuk N/Urea | Rp/kg | Local-estimate/parsial |
| 14 | P_P | Parameter harga | Harga pupuk fosfat/SP-36 | Rp/kg | Local-estimate/parsial |
| 15 | P_K | Parameter harga | Harga pupuk kalium/KCl | Rp/kg | Local-estimate/parsial |
| 16 | p_feed | Parameter harga | Harga pakan buatan | Rp/kg | Local-estimate / reference fallback |
| 17 | p_duck_buy | Parameter biaya | Harga beli bibit/anak bebek | Rp/ekor | Local-estimate |
| 18 | C_jaring | Parameter biaya | Biaya jaring | Rp/investasi | Local-estimate |
| 19 | C_kandang | Parameter biaya | Biaya kandang/naungan | Rp/investasi | Local-estimate |
| 20 | C_gulma | Parameter biaya | Biaya gulma baseline | Rp/are/siklus | Local-estimate |
| 21 | lambda | Biologis bebek | Survival rate bebek | 0-1 | Local-estimate |
| 22 | kappa_dung | Biologis bebek | Kotoran segar harian | kg/ekor/hari | Literature-uncalibrated |
| 23 | kappa_N | Biologis bebek | Kandungan N ekuivalen | kg/basis | Literature-uncalibrated |
| 24 | kappa_P | Biologis bebek | Kandungan P2O5 ekuivalen | kg/basis | Literature-uncalibrated |
| 25 | kappa_K | Biologis bebek | Kandungan K2O ekuivalen | kg/basis | Literature-uncalibrated |
| 26 | t_phase1 | Biologis bebek | Batas fase muda | hari | Literature-uncalibrated |
| 27 | kappa_dung_p1 | Biologis bebek | Kotoran kumulatif fase 1 | kg/ekor | Literature-uncalibrated |
| 28 | kappa_dung_p2 | Biologis bebek | Laju kotoran fase 2 | kg/ekor/hari | Literature-uncalibrated |
| 29 | kappa_feed_save | Biologis/pakan | Proporsi pakan dari alam | 0-1 | Literature-uncalibrated/local note |
| 30 | t_max_eff | Constraint | Batas efisiensi maksimum | hari | Literature-uncalibrated |
| 31 | HST_masuk | Lookup agronomi | Hari aman bebek dilepas | HST | Local-estimate |
| 32 | HST_heading | Lookup agronomi | Hari keluar malai | HST | Local-estimate |
| 33 | K_max | Lookup agronomi | Daya dukung kepadatan | ekor/are; catatan ekor/ha | Local-estimate |
| 34 | f_yield | Lookup agronomi | Faktor pengali yield untuk sistem tanam aktif Rev 3 | rasio | Literature-uncalibrated; hanya Jarwo/Tegel aktif |
| 35 | daily_duck_grazing_hours | Operasional lokal | Jam aktivitas bebek | jam/hari | Local-estimate |
| 36 | d_aktual | Dependent | Kepadatan aktual | ekor/are; catatan ekor/ha | Calculated |
| 37 | t_aktual | Dependent | Durasi aktual kalender | hari | Calculated |
| 38 | N_d | Dependent | Jumlah bebek hidup akhir | ekor | Calculated/local-estimate |
| 39 | Dung_total | Dependent | Total kotoran per ekor | kg/ekor | Literature-uncalibrated |
| 40 | t_effective | Dependent | Durasi efektif aktivitas | hari efektif | System-design |
| 41 | x_base | Dependent yield | Yield model dasar | kg/are; catatan kg/ha literatur | Literature-uncalibrated |
| 42 | x_penalized | Dependent yield | Yield setelah penalti | kg/are | System-design |
| 43 | x_final | Dependent yield | Yield akhir | kg/are; catatan kg/ha dan ton/ha | Mixed |
| 44 | P_rate | Dependent risk | Laju penalti kepadatan | 0-1 | System-design |
| 45 | DeltaV_rice | Dependent ekonomi | Nilai tambah padi | Rp | Mixed |
| 46 | V_duck | Dependent ekonomi | Nilai ekonomi bebek | Rp atau index | Mixed |
| 47 | V_eco1 | Dependent ekologi | Penghematan pupuk | Rp | Literature + guard |
| 48 | V_eco2 | Dependent ekologi | Penghematan pestisida/herbisida | Rp | Literature-uncalibrated |
| 49 | V_gulma | Dependent ekologi | Penghematan gulma/weeding | Rp | Local-estimate |
| 50 | V_eco | Dependent ekologi | Total manfaat ekologis-finansial | Rp | Mixed |
| 51 | Delta_y | Dependent objective | Nilai komparatif referensi | Rp/index | Mixed |
| 52 | C_infra | Dependent biaya | Biaya infrastruktur per siklus | Rp | Local-estimate |
| 53 | Penalty_yield | Dependent risk | Potongan nilai panen akibat risiko | Rp/kg | System-design |
| 54 | Laba_bersih | Dependent ekonomi | Estimasi laba bersih | Rp | Aktif estimasi/status-based |
| 55 | REY | Dependent akademik | Rice equivalent yield | kg/are | Literature-uncalibrated / aktif akademik |
| 56 | DeltaProfit | Dependent ekonomi | Selisih profit aktual vs rekomendasi | Rp | Parsial/status-based |
| 57 | N_tanah | Dependent hara | Nitrogen setara dari kotoran | kg/are | Literature-uncalibrated |
| 58 | P_tanah | Dependent hara | P2O5 setara dari kotoran | kg/are | Literature-uncalibrated |
| 59 | K_tanah | Dependent hara | K2O setara dari kotoran | kg/are | Literature-uncalibrated |




# 7. Limitation Penelitian dan Variabel Non-Aktif

Bagian ini memuat data, variabel, atau komponen yang ditemukan pada data collection/literatur, tetapi tidak menjadi scope aktif DSS Rev 3. Komponen ini tidak dipakai dalam perhitungan, lookup aktif, objective function, maupun output numerik utama.

| Komponen non-aktif | Status Rev 3 Final | Alasan |
| --- | --- | --- |
| Varietas tambahan seperti Cigelis/Cegelis, Ciherang, beras merah, dan lainnya | Limitation / pengembangan lanjutan | Data collection lokal final paling kuat hanya menyebut Sertani/Seratih dan Inpari sebagai varietas utama. Varietas lain tidak dipakai sebagai lookup aktif agar tidak overclaim. |
| Sistem tanam tambahan seperti SRI, double transplant, dan lainnya | Limitation / pengembangan lanjutan | Data collection lokal final untuk praktik padi-bebek hanya memuat Jajar Legowo/Jarwo dan Tegel/Konvensional. Sistem lain tidak dipakai sebagai lookup aktif DSS Rev 3. |
| A_total_are | Konteks data, bukan parameter aktif | Perhitungan kepadatan, yield, ekonomi, dan rekomendasi hanya memakai A_are sebagai area aktif bebek. Total lahan dapat disimpan sebagai catatan, tetapi bukan fallback perhitungan. |
| water_condition, water_depth_cm, dan drainage_note | Limitation penelitian | Data kondisi air dari mitra tidak konsisten sebagai data kuantitatif dan pengaruhnya ke output DSS belum jelas. Tidak dipakai dalam rumus aktif. |
| topography_level / land_elevation_masl | Limitation penelitian | Data topografi/ketinggian tidak lengkap dan pengaruh kuantitatifnya ke output DSS belum jelas. Tidak dipakai dalam rumus aktif. |
| daily_labor_hours | Limitation penelitian | Jam kerja pengelolaan belum menjadi rumus biaya/produktivitas terukur pada DSS Rev 3. Tidak dipakai dalam profit atau objective. |
| weather_note, predator_note, disease_note, unusual_event | Limitation penelitian / catatan validasi | Faktor ini dapat menjelaskan outlier survival atau hasil lapangan, tetapi tidak menjadi rumus aktif karena tidak tersedia sebagai data numerik konsisten dari mitra. |
| kappa_feed_greedy dan Penalty_feed | Non-aktif pada model Rev 3 | Data fase pakan tambahan tinggi masih bersifat kualitatif. Biaya pakan aktif cukup memakai C_feed dengan q_feed fallback 0.10 dan p_feed ketika tersedia. |
| F_CH4, F_N2O, F_CH4_konv, F_N2O_konv, X_DO, CO2e, GHGI, Reduksi_CH4, GWP_CH4, GWP_N2O, beta_DO, beta_redoks, beta_metan | Limitation penelitian | Data CH4, N2O, baseline emisi konvensional, DO, redoks, dan metanogen tidak tersedia dari mitra. Emisi tidak dihitung sebagai output numerik dan tidak masuk objective function. |
| Bobot bebek jual | Limitation data ekonomi | Data bobot jual belum tersedia rapi. Perhitungan ekonomi bebek memakai harga per ekor, bukan harga berbasis bobot. |
| Data panen lokal bersih per petak aktif | Kebutuhan kalibrasi lanjutan | Data panen padi-bebek sering tercampur antara petak bebek dan non-bebek, sehingga belum cukup sebagai kalibrasi final alpha_local. |
| Harga gabah/beras padi-bebek final dan harga pakan lokal Rp/kg | Kebutuhan kalibrasi lanjutan | Sebagian harga tersedia secara parsial, tetapi belum cukup untuk membuat seluruh output profit numeric-ready pada semua skenario. |
| Uji kotoran bebek lokal | Kebutuhan validasi lanjutan | N/P/K_tanah aktif dihitung dari kappa_N/P/K literatur, tetapi belum menjadi local-calibrated karena uji kotoran lokal belum tersedia. |





# 8. Data Collection Lanjutan untuk Kalibrasi Astungkara Way

| Kelompok | Kolom data yang dikumpulkan | Satuan/format | Prioritas | Tujuan |
| --- | --- | --- | --- | --- |
| Identitas | cycle_id, farmer_id, subak, munduk, plot_id | teks | Wajib | Mencegah data tercampur antarpetak/petani. |
| Lahan | A_active_duck_are; A_total_are opsional sebagai catatan non-aktif | are | Wajib untuk A_active_duck_are | Kepadatan, yield, ekonomi, dan rekomendasi hanya memakai area aktif bebek. |
| Tanam | TD, V, S, tanggal_transplant opsional | tanggal/kategori | Wajib | Membentuk lookup HST dan sistem tanam. |
| Bebek | J, U_bebek, tanggal_lepas, HST_masuk, tanggal_tarik, HST_tarik | ekor/hari/tanggal | Wajib | Validasi t aktual dan batas heading. |
| Survival | duck_initial, duck_final, duck_dead, duck_lost, mortality_reason | ekor/kategori | Wajib | Kalibrasi lambda dan ekonomi bebek. |
| Panen padi | yield_active_duck_kg, yield_unit, harvest_date, moisture_note | kg atau kg/are | Wajib | Harus spesifik petak aktif bebek, bukan gabungan petak. |
| Baseline | yield_baseline_same_location, baseline_variety, baseline_system | kg/are | Sangat disarankan | Pembanding harus lokasi/varietas/sistem setara. |
| Harga | p_gabah_RD, p_gabah_konv, p_beras_RD, p_beras_konv, rendemen | Rp/kg/% | Wajib untuk ekonomi | Pisahkan gabah dan beras. |
| Bebek ekonomi | p_duck_buy, p_duck_sell, duck_weight_optional | Rp/ekor/kg | Wajib untuk V_duck_lokal | Bobot tidak ada: gunakan per ekor. |
| Pakan | feed_kg_total, feed_cost_total | kg/Rp | Prioritas tinggi | Kalibrasi q_feed lokal dan biaya pakan. Jenis pakan tidak menjadi variabel model utama. C_feed tetap aktif memakai fallback q_feed 0.10 sampai data lokal tersedia. |
| Infrastruktur | C_jaring, panjang_jaring, life_jaring, C_kandang, jumlah_kandang, life_kandang, maintenance | Rp/unit/siklus | Wajib untuk profit | Amortisasi per siklus. |
| Gulma | weeding_baseline_cost, weeding_actual_cost, weeding_frequency | Rp/are/frekuensi | Prioritas tinggi | Kalibrasi V_gulma. |
| Pupuk | fertilizer_type, fertilizer_kg_are, fertilizer_cost, timing | kg/are/Rp | Disarankan | Kalibrasi manfaat kotoran/pupuk. N/P/K_tanah tetap aktif memakai kappa_N/P/K referensi sampai uji lokal tersedia. |
| Hama/pestisida | pest_incidence_note, pesticide_cost, herbicide_cost | teks/Rp | Disarankan | Kalibrasi V_eco2. |





# 9. Aturan Implementasi Sistem 

| Aturan | Keputusan final | Alasan |
| --- | --- | --- |
| R-01 Area | A_are/A_active_duck_are wajib dipakai untuk d_aktual. A_total_are tidak dipakai sebagai fallback perhitungan. | Area aktif menentukan risiko sebenarnya; memakai total lahan dapat membuat kepadatan dan rekomendasi bias. |
| R-02 Satuan | Semua proses DSS memakai are. d_lit_ha = d_are*100 hanya dibuat sementara sebelum masuk rumus Xiong. | Rumus literatur memakai ekor/ha, tetapi output DSS kembali ke are. |
| R-03 Durasi | Hard constraint: HST_masuk + t <= HST_heading. | Cegah kerusakan malai/bulir. |
| R-04 Density | Jarwo default aman 4 ekor/are; Tegel memakai rentang 2-3 ekor/are dengan K_max praktis 3 ekor/are. Boundary risk: LOW jika d_are < 0.8*K_max; SAFE jika 0.8*K_max <= d_are <= K_max. | Sesuai validasi lokal dan menghindari boundary tepat 0.8*K_max masuk LOW. |
| R-05 Yield | x_final boleh dihitung sebagai estimasi model dengan alpha_local=1. | Belum kalibrasi lokal penuh. |
| R-06 Profit | Laba_bersih, C_feed, dan DeltaProfit tetap dihitung sebagai estimasi. Data lokal diprioritaskan; data referensi dipakai saat data lokal belum tersedia. | Tidak mematikan output; status klaim membedakan lokal, parsial, dan literature-uncalibrated. |
| R-07 V_duck | Mode V_duck_Xiong: jangan kurangi C_feed lagi. | V_duck_Xiong bersifat net-revenue referensi. |
| R-08 V_eco1 | Gunakan max(0, V_eco1_raw). | Durasi lokal pendek dapat membuat raw negatif. |
| R-09 V_eco2 | Gunakan 400/(1+exp(...)), bukan 400^(...). | Kesalahan operator membuat hasil tidak valid. |
| R-10 Emisi | CO2e/GHGI/Reduksi_CH4/DO-to-CH4 tidak menjadi output numerik DSS Rev 3 dan tidak masuk objective. | Data CH4, N2O, baseline emisi konvensional, dan DO tidak tersedia dari mitra; bagian ini menjadi limitation penelitian. |
| R-11 Data referensi | Data referensi dipakai sebagai fallback aktif dengan flag literature-uncalibrated. | Sesuai catatan penting: tidak dihapus dan tidak dianggap data lokal. |
| R-12 Response | Setiap output memuat status_data, sumber_data, dan catatan_kalibrasi. Label status menggunakan estimation-only secara konsisten. | Transparansi akademik dan mencegah overclaim. |
| R-13 Optimality | Skenario aktual dianggap optimal hanya jika identik dengan best_scenario hasil optimizer berdasarkan objective aktif. | Rekomendasi tidak perlu muncul ketika aktual sudah di titik terbaik, tetapi SAFE saja belum berarti optimal. |





# 10. Skenario Output DSS dan Status Klaim.

## 10.1 Skenario Output Aktual dan Status Klaim

| Output DSS | Rumus perhitungan | Yang dihasilkan | Penjelasan skenario | Status klaim |
| --- | --- | --- | --- | --- |
| A-01 Kepadatan aktual | A_are = area aktif; A_ha_note = A_are/100; d_aktual_are = J/A_are; d_lit_ha = d_aktual_are*100 | Kepadatan aktual utama dalam ekor/are; ekor/ha hanya catatan rumus literatur. | Mengevaluasi jumlah bebek yang benar-benar ditebar petani terhadap luas area aktif bebek. Hanya total lahan tersedia: sistem memberi catatan bias area. | Local-calculated; kuat dengan A_are sebagai area aktif bebek. |
| A-02 Durasi aktual dan timeline | t_aktual = HST_tarik - HST_masuk; fallback = HST_heading - HST_masuk; tanggal_lepas = TD + HST_masuk; tanggal_tarik = TD + min(HST_masuk + t_aktual, HST_heading) | Durasi aktual bebek di sawah, tanggal lepas, dan tanggal tarik. | Mengecek apakah durasi aktual mengikuti fase tanaman padi dan tidak melewati fase keluar malai. | Local-estimate: HST/tanggal belum lengkap; local-calculated: tanggal aktual lengkap. |
| A-03 Status risiko aktual | d_aktual_are <= K_max_are: P_rate = 0; d_aktual_are > K_max_are: P_rate = min(P_max, gamma*((d_aktual_are - K_max_are)/K_max_are)) | Status aman, perlu perhatian, atau berisiko; termasuk tingkat penalti kepadatan. | Membaca apakah rencana petani terlalu padat terhadap daya dukung lahan/pola tanam. Risiko juga mempertimbangkan bebek melewati fase keluar malai. | System-design berbasis validasi lokal; belum menjadi rumus biologis universal. |
| A-04 Prediksi yield aktual | x_base_kg_ha_note = (-0.0103*d_lit_ha^2 + 2.6314*d_lit_ha + 7569.4) * exp(-((t_aktual - 80)^2)/(2*80^2)); x_base_kg_are = x_base_kg_ha_note/100; x_final_kg_are = alpha_local*x_base_kg_are*(1-P_rate)*f_yield | Prediksi hasil panen aktual dalam kg/are; kg/ha dan ton/ha hanya catatan konversi. | Menghasilkan estimasi yield dari input aktual petani setelah penalti kepadatan dan faktor sistem tanam. | Mixed: x_base literature-uncalibrated; P_rate system-design; alpha_local perlu kalibrasi Astungkara Way. |
| A-05 Selisih yield aktual terhadap baseline | Delta_x_are = x_final_kg_are - x0_kg_are; Delta_x_ha_note = Delta_x_are*100 | Kenaikan atau penurunan yield aktual dibanding baseline konvensional. | Dipakai untuk menunjukkan apakah skenario aktual petani lebih baik atau lebih rendah dari pembanding tanpa bebek yang sebanding. | Local-estimate: x0 berasal dari data lokal terbatas; literature-uncalibrated: baseline masih referensi. |
| A-06 Bebek hidup akhir aktual | N_d_aktual = J * lambda | Estimasi jumlah bebek yang bertahan sampai akhir periode. | Mengubah jumlah bebek awal menjadi jumlah bebek yang realistis untuk ekonomi bebek dan kontribusi kotoran. | Local-estimate; lambda lokal masih berupa range dan perlu kalibrasi survival per siklus. |
| A-07 Kotoran dan hara aktual | t<=50: Dung_total=(t/50)*4; t>50: Dung_total=4+(t-50)*0.2; N_tanah_are=kappa_N*(Dung_total/10)*d_aktual_are*lambda; P_tanah_are=kappa_P*(Dung_total/10)*d_aktual_are*lambda; K_tanah_are=kappa_K*(Dung_total/10)*d_aktual_are*lambda | Estimasi kotoran, N, P2O5, dan K2O ekuivalen per are. | Menjelaskan kontribusi biologis bebek terhadap lahan dalam bentuk estimasi setara pupuk, bukan klaim hasil uji laboratorium. | Literature-uncalibrated; belum dikalibrasi lokal karena kotoran dan unsur hara belum diukur lokal. |
| A-08 Nilai tambah padi aktual | R_gabah_RD = x_final_kg_are*A_are*p_gabah_RD; R_gabah_K = x0_kg_are*A_are*p_gabah_konv; DeltaV_rice = R_gabah_RD - R_gabah_K | Nilai ekonomi padi/gabah aktual dibanding baseline. | Membandingkan nilai produksi padi-bebek aktual dengan sistem konvensional. Harga gabah dan beras harus dipisahkan. | Mixed; kuat: harga dan baseline lokal sebanding; parsial: harga/baseline belum lengkap. |
| A-09 Nilai ekonomi bebek aktual | C_duck_buy = J*p_duck_buy; C_feed = J*q_feed*t_effective*p_feed*(1-kappa_feed_save); V_duck_lokal = N_d_aktual*p_duck - C_duck_buy - C_feed; V_duck_Xiong = [-0.0096*d_lit_ha^2 + (11.3861+14.4*lambda)*d_lit_ha - 0.18*lambda*t_aktual*d_lit_ha + 17.0857]*A_ha_note | Estimasi nilai ekonomi bebek lokal dan nilai referensi Xiong. | Membedakan ekonomi bebek berbasis harga lokal dari model referensi. C_feed aktif memakai q_feed lokal atau q_feed fallback operasional 0.10. Mode V_duck_Xiong net revenue: C_feed tidak dikurangkan lagi. | V_duck_lokal aktif estimasi local/reference-mixed; V_duck_Xiong literature-uncalibrated. |
| A-10 Manfaat ekologis-finansial aktual | V_eco1 = max(0, (0.02*t-0.6)*(0.107*P_N+0.424*P_P+0.058*P_K)*d_aktual_are*lambda*A_are); V_eco2 = (400/(1+exp(-0.036626*d_lit_ha))-3.327)*A_ha_note; V_gulma = C_gulma*A_are*r_gulma; V_eco = V_eco1+V_eco2+V_gulma | Estimasi manfaat pupuk, pestisida/herbisida, gulma, dan total manfaat ekologis-finansial. | Menampilkan komponen manfaat ekologis secara terpisah agar sumber manfaat tidak tercampur. | V_gulma local-estimate; V_eco1/V_eco2 literature-uncalibrated; r_gulma system-design. |
| A-11 Biaya dan laba bersih aktual | C_infra = C_jaring/life_jaring + C_kandang/life_kandang + maintenance_infra; Laba_bersih_aktual = R_gabah_RD + V_duck_lokal + V_eco - C_infra - biaya_tambahan_lain | Estimasi biaya infrastruktur dan laba bersih skenario aktual. | Menghasilkan gambaran ekonomi aktual petani. q_feed, baseline, atau biaya lain yang berasal dari referensi tetap dihitung dengan status literature-uncalibrated. | Aktif estimasi/status-based; local-estimate untuk infrastruktur, literature-uncalibrated untuk komponen referensi. |
| A-12 Emisi dan lingkungan aktual | Tidak dihitung sebagai output numerik DSS Rev 3. | Tidak ada CO2e, GHGI, Reduksi_CH4, atau DO-to-CH4 pada output utama. | Data CH4, N2O, baseline emisi konvensional, dan DO tidak tersedia dari mitra. | Limitation penelitian; bukan komponen aktif DSS. |



## 10.2 Skenario Output Rekomendasi dan Status Klaim

| Output DSS | Rumus perhitungan | Yang dihasilkan | Penjelasan skenario | Status klaim |
| --- | --- | --- | --- | --- |
| R-01 Variabel keputusan rekomendasi | (d_are*, t*) = argmax F_active(d,t), dengan 0 < d_are <= K_max_are dan 0 < t <= min(t_max_eff, HST_heading - HST_masuk) | Kepadatan rekomendasi berbasis are dan durasi rekomendasi terbaik menurut DSS. | Sistem mencari kombinasi kepadatan dan durasi terbaik berdasarkan objective aktif: yield + ecology - risk penalty; profit masuk jika numeric-ready; environment tidak masuk. | System-design + literature baseline; nilai akhir perlu validasi lokal. |
| R-02 Jumlah bebek rekomendasi | d_rekomendasi_are = d_are*; J_rekomendasi = round(d_rekomendasi_are*A_are) | Jumlah bebek ideal dalam bilangan bulat dan kepadatan rekomendasi ekor/are. | Mengubah hasil optimasi d* menjadi jumlah bebek yang dapat dipraktikkan pada area aktif bebek milik petani. | Local-calculated dari output optimasi; constraint lokal mengikuti K_max_are. |
| R-03 Timeline rekomendasi | tanggal_lepas_rekomendasi = TD + HST_masuk; tanggal_tarik_rekomendasi = TD + min(HST_masuk + t*, HST_heading) | Tanggal lepas dan tanggal tarik bebek versi rekomendasi. | Memberikan jadwal rekomendasi yang mengikuti kalender padi, varietas, dan batas keluar malai. | Local-estimate: lookup HST masih estimasi; local-calculated: TD dan lookup valid. |
| R-04 Status risiko rekomendasi | P_rate_rekomendasi = 0 pada kondisi d_rekomendasi_are <= K_max_are; selain itu P_rate_rekomendasi = min(P_max, gamma*((d_rekomendasi_are-K_max_are)/K_max_are)) | Status risiko rekomendasi dan penalti kepadatan rekomendasi. | Memastikan rekomendasi tidak sekadar mengejar yield/profit, tetapi tetap menghindari risiko tanaman rusak, malai dimakan, dan biaya pakan meningkat. | System-design berbasis validasi lokal; perlu diuji lapangan. |
| R-05 Prediksi yield rekomendasi | d_lit_ha_rec = d_rekomendasi_are*100; x_base_rec_kg_ha_note = (-0.0103*d_lit_ha_rec^2 + 2.6314*d_lit_ha_rec + 7569.4)*exp(-((t* - 80)^2)/(2*80^2)); x_base_rec_kg_are = x_base_rec_kg_ha_note/100; x_final_rec_kg_are = alpha_local*x_base_rec_kg_are*(1-P_rate_rec)*f_yield | Prediksi hasil panen pada skenario rekomendasi dalam kg/are; kg/ha dan ton/ha hanya catatan konversi. | Menghasilkan estimasi hasil panen pada skenario petani mengikuti jumlah bebek dan durasi rekomendasi. | Mixed; model yield literature-uncalibrated dan perlu alpha_local dari data Astungkara Way. |
| R-06 Perbandingan yield rekomendasi vs aktual | DeltaYield = x_final_rec - x_final_aktual; DeltaYield_% = DeltaYield/x_final_aktual*100% | Selisih yield absolut dan persentase terhadap skenario aktual. | Menunjukkan apakah rekomendasi memberi peningkatan hasil atau hanya memperbaiki risiko tanpa kenaikan besar. | Calculated comparison; klaim peningkatan lokal menunggu validasi panen petak aktif. |
| R-07 Bebek akhir dan kotoran rekomendasi | N_d_rec = J_rekomendasi*lambda; Dung_are_rec = Dung_total(t*)*d_rekomendasi_are*lambda | Estimasi bebek bertahan dan total kotoran per are pada rekomendasi. | Menilai dampak rekomendasi terhadap populasi bebek akhir, kontribusi kotoran, dan kebutuhan pengelolaan. | N_d local-estimate; Dung_are literature-uncalibrated/belum dikalibrasi lokal. |
| R-08 Nilai tambah padi rekomendasi | R_gabah_RD_rec = x_final_rec_kg_are*A_are*p_gabah_RD; DeltaV_rice_rec = R_gabah_RD_rec - R_gabah_K | Nilai produksi padi pada skenario rekomendasi dibanding baseline. | Membandingkan nilai ekonomi padi rekomendasi terhadap baseline yang sama dengan skenario aktual. | Mixed; kuat: harga dan baseline lokal tersedia; parsial: data belum lengkap. |
| R-09 Nilai ekonomi bebek rekomendasi | C_duck_buy_rec = J_rekomendasi*p_duck_buy; C_feed_rec = J_rekomendasi*q_feed*t_effective_rec*p_feed*(1-kappa_feed_save); V_duck_lokal_rec = N_d_rec*p_duck - C_duck_buy_rec - C_feed_rec; V_duck_Xiong_rec = [-0.0096*d_lit_ha_rec^2 + (11.3861+14.4*lambda)*d_lit_ha_rec - 0.18*lambda*t* d_lit_ha_rec + 17.0857]*A_ha_note | Estimasi nilai bebek lokal dan referensi pada skenario rekomendasi. | Menghitung dampak jumlah bebek rekomendasi terhadap biaya beli, biaya pakan, survival, dan nilai jual bebek. q_feed fallback operasional 0.10 dipakai saat q_feed lokal belum tersedia. | V_duck_lokal aktif estimasi local/reference-mixed; V_duck_Xiong literature-uncalibrated. |
| R-10 Manfaat ekologis rekomendasi | V_eco_rec = V_eco1_rec + V_eco2_rec + V_gulma_rec; V_gulma_rec = C_gulma*A_are*min(1, d_rekomendasi_are/K_max_are) | Estimasi manfaat pupuk, pestisida/herbisida, gulma, dan total manfaat ekologis pada rekomendasi. | Menunjukkan potensi manfaat ekologis-finansial saat kepadatan dan durasi disesuaikan oleh DSS. | Mixed; V_gulma local-estimate, V_eco1/V_eco2 literature-uncalibrated. |
| R-11 Laba dan selisih profit | Laba_bersih_rec = R_gabah_RD_rec + V_duck_lokal_rec + V_eco_rec - C_infra_rec - biaya_tambahan_lain; DeltaProfit = Laba_bersih_rec - Laba_bersih_aktual | Estimasi laba rekomendasi dan selisih terhadap skenario aktual. | Memberi ukuran finansial apakah rekomendasi lebih layak daripada input awal petani dengan status sumber data yang eksplisit. | Aktif estimasi/status-based; komponen referensi berstatus literature-uncalibrated. |
| R-12 Emisi dan lingkungan rekomendasi | Tidak dihitung sebagai output numerik DSS Rev 3. | Tidak ada CO2e, GHGI, DeltaGHGI, atau Reduksi_CH4 pada rekomendasi utama. | Data CH4, N2O, baseline emisi konvensional, dan DO tidak tersedia dari mitra. | Limitation penelitian; bukan komponen aktif DSS. |
| R-13 Ringkasan rekomendasi DSS | Ringkasan = fungsi(J_rekomendasi, d_rekomendasi_are, t*, x_final_rec, DeltaYield, DeltaProfit, P_rate_rec, status_kalibrasi) | Narasi rekomendasi: jumlah bebek, jadwal, prediksi yield, manfaat ekologis-finansial, risiko, dan catatan kalibrasi. | Output akhir yang dibaca pengguna. Sistem menampilkan status klaim agar angka lokal, estimasi, dan referensi belum terkalibrasi tidak tercampur. | System-design untuk komunikasi DSS; angka mengikuti status klaim masing-masing komponen. |



# 11. Contoh Perhitungan Ilustratif

| Blok | Variabel | Hasil | Catatan |
| --- | --- | --- | --- |
| Input | A_are | 7 are aktif | Area aktif bebek, bukan total lahan. |
| Input | J | 28 ekor | Jumlah bebek ditebar. |
| Derivasi | d_are | 28/7 = 4 ekor/are | Batas atas default aman Jarwo. |
| Derivasi | d_lit_ha | 4*100 = 400 ekor/ha | Catatan konversi untuk rumus literatur, bukan satuan utama DSS. |
| Lookup | HST_masuk | 28 HST | Contoh konservatif. |
| Lookup | HST_heading | 60 HST | Contoh fase keluar malai. |
| Derivasi | t | 60-28 = 32 hari | Durasi aktif kalender. |
| Asumsi | lambda | 0.67 | Estimasi atas lokal. |
| Kotoran | Dung_total | (32/50)*4 = 2.56 kg/ekor | Literature-uncalibrated. |
| Yield | P_rate | 0 pada K_max_are=4 | Tidak melewati daya dukung default. |
| Output | x_final | Estimasi model | Butuh alpha_local setelah data panen. |
| Hara | N_tanah | 0.049*(2.56/10)*4*0.67 = 0.0336 kg/are | Aktif sebagai estimasi referensi; belum dikalibrasi lokal. Catatan hektar: 3.36 kg/ha. |
| Hara | P_tanah | 0.072*(2.56/10)*4*0.67 = 0.0494 kg/are | Aktif sebagai estimasi referensi; belum dikalibrasi lokal. Catatan hektar: 4.94 kg/ha. |
| Hara | K_tanah | 0.032*(2.56/10)*4*0.67 = 0.0220 kg/are | Aktif sebagai estimasi referensi; belum dikalibrasi lokal. Catatan hektar: 2.20 kg/ha. |
| Output | C_feed | J*0.10*t_effective*p_feed*(1-kappa_feed_save), saat q_feed lokal belum tersedia | Aktif memakai q_feed fallback 0.10 dari A02 dengan status literature-uncalibrated; p_feed tetap wajib tersedia agar biaya pakan numerik dapat dihitung. |
| Limitation | CO2e/GHGI/Reduksi_CH4/DO-to-CH4 | Tidak dihitung sebagai output numerik DSS Rev 3 | Data CH4, N2O, baseline emisi konvensional, dan DO tidak tersedia dari mitra. |
