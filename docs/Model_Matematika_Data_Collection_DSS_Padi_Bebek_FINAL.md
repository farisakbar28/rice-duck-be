# MODEL MATEMATIKA DAN DATA COLLECTION

## DSS Yield Prediction Padi-Bebek - Versi Final (Master Document)

### Catatan Integrasi Sistem & Algoritma Final:

- **Penganuliran Data Konvensional Palsu:** File Rekap dipastikan secara mutlak sebagai implementasi eksklusif Padi-Bebek. Data yang sebelumnya terlihat seperti konvensional murni adalah kesalahan/anomali input dari lapangan dan telah dibuang. Variabel Skenario Konvensional (`x0` dan `p_gabah_konv`) kini berstatus **HOLD** (Dikosongkan), menunggu pengumpulan data rekap spesifik konvensional dari mitra.
- **Aturan Input Antarmuka (System Input):** Di dalam perangkat lunak DSS nanti, input luasan lahan yang dimasukkan oleh pengguna akhir akan langsung dianggap dan dieksekusi sebagai **Area Aktif Bebek (`A_are`)**. Tidak ada lagi pembagian rumit di sisi depan (_front-end_).
- **Fakta Empiris Sistem Tanam (Tegel > Jarwo):** Sesuai fakta murni File Rekap (melalui filter Bin Dominan), sistem Tegel yang diintervensi bebek terbukti mengungguli panen Jajar Legowo. Rasio pengali (`f_yield`) Tegel ditetapkan lebih tinggi secara matematis.
- **Kalibrasi Wilayah (`alpha_local`):** Ditetapkan mutlak di angka **0.643** untuk menjembatani proyeksi mentah literatur internasional ke realitas empiris lahan di Bali.
- **Eksekusi Ekonomi Berbasis Waktu (Latest Date):** Segala harga pasar (beli bibit, jual bebek, gabah organik) **DIAMBIL MUTLAK** dari tanggal transaksi paling mutakhir di File Rekap. Median tidak lagi digunakan untuk variabel ekonomi fluktuatif.
- **Biaya Pakan Bebek:** Dihapus total (`C_feed = 0`) dari seluruh persamaan profitabilitas sesuai realitas ekosistem subak Bali.

---

### 1. Ringkasan Eksekutif

Sistem Pendukung Keputusan (DSS) Yield Prediction Padi-Bebek ini dirancang sebagai instrumen navigasi agronomis dan ekonomis presisi bagi petani subak di Bali. Model ini dibangun dengan kepatuhan absolut pada hierarki data lapangan Astungkara Way. DSS ini mengimplementasikan desain sistem _front-end_ di mana input luasan dari pengguna akan langsung diproses secara tunggal sebagai Area Aktif Bebek.

Model biologi panen, nilai keekonomian, dan manfaat ekologis diadaptasi dari kerangka literatur internasional (Xiong dkk., 2023; Wu dkk., 2021), lalu dikalibrasi ketat menggunakan data lokal Bali (Vipriyanti dkk., 2021). Modul emisi gas rumah kaca (CO2e, GHGI) ditetapkan sebagai batasan (_limitation_) penelitian karena absennya instrumen lab _in-situ_.

Untuk menjaga transparansi ilmiah, setiap parameter dan rumus pada dokumen ini diberi label status yang menunjukkan tingkat kepercayaan sumber datanya: _Local-calibrated_ (data lokal kuat dan konsisten), _Local-estimate_ (data lokal tersedia berupa rentang/estimasi), _Lit-uncalibrated_ (rumus dari artikel referensi yang belum diuji di lapangan), _System-design_ (aturan logika DSS, bukan rumus jurnal), _Exception_ (harga subsidi/pasar acuan), dan _HOLD/Menunggu Data_ (variabel dikosongkan karena data bersih belum tersedia).

#### Ringkasan Keputusan Kunci Versi Final

| Keputusan                                | Isi Keputusan                                                                                                   | Dampak ke DSS                                                                                                    |
| :--------------------------------------- | :-------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------- |
| **Penganuliran data konvensional**       | Seluruh siklus yang tercampur konvensional dibuang total; `x0` dan `p_gabah_konv` berstatus HOLD.               | Perbandingan Delta terhadap baseline konvensional untuk sementara tidak ditampilkan, mencegah bias komparasi.    |
| **Area input = Area Aktif Bebek**        | Tidak ada lagi pembagian luas di sisi _front-end_; seluruh luas yang diinput otomatis menjadi Area Aktif Bebek. | Antarmuka lebih sederhana, namun luas lahan non-bebek harus dipisahkan secara manual oleh mitra sebelum input.   |
| **Tegel lebih unggul dari Jarwo**        | `f_yield` Tegel dikunci pada 1.39 berdasarkan hasil filter Bin Dominan terhadap File Rekap.                     | Rekomendasi DSS akan condong ke sistem Tegel pada kondisi kepadatan dan durasi yang setara.                      |
| **Penyetaraan Rumus (`alpha_local`)**    | Ditetapkan `0.643` agar fungsi literatur selaras dengan median empiris panen Bali.                              | Mencegah anomali proyeksi _overclaim_ (_over-estimation_) pada sistem _backend_.                                 |
| **Harga ekonomi (Latest Date)**          | Median ditinggalkan; harga (beli bibit, jual bebek, gabah organik) memakai transaksi paling mutakhir.           | Angka ekonomi lebih relevan dengan kondisi pasar terkini, namun lebih rentan terhadap volatilitas jangka pendek. |
| **Biaya pakan dihapus total**            | `C_feed` dikunci di angka nol pada seluruh persamaan profitabilitas.                                            | `V_duck_lokal` dan `Laba_bersih` merefleksikan model pakan _in-situ_ alami.                                      |
| **Emisi dan kondisi lahan = Limitation** | CO2e, GHGI, Reduksi_CH4, dan relasi DO-to-CH4 tidak dihitung sebagai output numerik DSS.                        | DSS fokus pada kepastian agronomi dan ekonomi, bukan klaim kuantitatif terhadap dampak lingkungan.               |

---

### 2. Hierarki Sumber Data dan Algoritma Pengolahan

Keabsahan model ini bergantung pada "Truth of Priority" tanpa toleransi kompromi:

1. **Prioritas 1 (Utama):** File Rekap (Recap Data CRS Bebek.xlsx) - Murni Padi-Bebek.
2. **Prioritas 2:** File Wawancara (data_collection_padi_bebek_FINAL.xlsx).
3. **Prioritas 3:** Artikel Referensi Bali (Vipriyanti dkk., 2021).
4. **Prioritas 4:** Artikel Referensi Indonesia (Salman dkk., 2024; Azizi dkk., 2023).
5. **Prioritas 5:** Artikel Internasional (Xiong dkk., 2023; Wu dkk., 2021).

#### Tabel Status Klaim

| Status Klaim             | Definisi                                                                   | Contoh Parameter/Rumus                                           | Cara Penulisan                                                                    |
| :----------------------- | :------------------------------------------------------------------------- | :--------------------------------------------------------------- | :-------------------------------------------------------------------------------- |
| **Local-calibrated**     | Data lokal kuat, konsisten, dan siap dijadikan default sistem.             | `p_gabah_RD`, `p_duck_buy`, `p_duck`, `A_are`, `J`, `HST_masuk`. | Ditulis sebagai parameter lokal terkonfirmasi.                                    |
| **Local-estimate**       | Data lokal tersedia namun masih berupa rentang atau estimasi.              | `lambda`, `K_max_are`, `t_lokal_aktif`, `HST_heading`.           | Ditulis sebagai estimasi lokal, sertakan rentang nilainya.                        |
| **Lit-uncalibrated**     | Rumus/nilai dari artikel referensi, belum diuji di lapangan lokal.         | `x(d,t)`, `V_duck_lit`, `kappa_N/P/K`, `q_feed`.                 | Ditulis sebagai baseline literatur, belum dikalibrasi lokal.                      |
| **System-design**        | Aturan dibuat untuk logika DSS, bukan rumus eksplisit jurnal.              | `P_rate`, `Score_safety`, `F_active`.                            | Disebut sebagai aturan/desain sistem, bukan rumus jurnal.                         |
| **Exception**            | Harga resmi pemerintah atau harga pasar acuan yang dipakai apa adanya.     | `P_N`, `P_P`, `P_K`.                                             | Disebut sebagai harga acuan resmi/pasar, bukan hasil kalibrasi lapangan.          |
| **HOLD / Menunggu Data** | Variabel sengaja dikosongkan karena data bersih belum tersedia dari mitra. | `x0`, `p_gabah_konv`.                                            | Ditulis eksplisit sebagai kosong; dilarang diisi dengan angka estimasi sementara. |

#### Algoritma Pengolahan Data Historis (Backend Filtering File Rekap)

Untuk mengekstrak nilai kalibrasi empiris dari File Rekap historis, data kuantitatif wajib melalui 3 tahap pemurnian:

1. **Tahap 1 (Mapping Luas Aktif Historis):** Luas Aktif Bebek = Total Bebek / 2 (dibulatkan ke bawah).
2. **Tahap 2 (Filter Kelayakan):** Jika Luas Aktif < 1 are (bebek < 2 ekor) atau data populasi 0 (anomali), siklus dibuang mutlak.
3. **Tahap 3 (Bin Dominan):** Data hasil panen (Yield) dikelompokkan ke rentang interval 10 kg/are. Median ditarik HANYA dari kelompok bin yang frekuensinya paling mendominasi.
   _(Hasil bin dominan pada masing-masing sistem tanam inilah yang dipakai sebagai median resmi untuk menghitung rasio pengali `f_yield` dan kalibrasi `alpha_local`)._

---

### 3. Data Collection: Parameter Lokal dan Referensi

| Parameter                   | Nilai / Range Final     | Satuan     | Sumber (Priority)                      | Status           | Catatan Pemakaian                                                             |
| :-------------------------- | :---------------------- | :--------- | :------------------------------------- | :--------------- | :---------------------------------------------------------------------------- |
| **A_are**                   | Runtime input           | are        | Prioritas 1 - Input pengguna           | Local-calibrated | Input luasan dari pengguna (Otomatis Area Aktif Bebek).                       |
| **J**                       | Runtime input           | ekor       | Prioritas 1 - Input pengguna           | Local-calibrated | Jumlah populasi bebek ditebar awal.                                           |
| **V**                       | Sertani/Seratih; Inpari | kategori   | Prioritas 2 - Wawancara                | Local-estimate   | Scope varietas merujuk File Wawancara (Prioritas 2).                          |
| **S**                       | Jarwo; Tegel            | kategori   | Prioritas 1/2 - Rekap & Wawancara      | Local-estimate   | Kedua sistem tanam divalidasi dengan intervensi bebek.                        |
| **HST_masuk**               | 20 (Fixed)              | HST        | Prioritas 1 - File Rekap               | Local-calibrated | DIKUNCI 20 HST (Standar fase vegetatif akar padi mapan).                      |
| **HST_heading**             | 60 - 65 (Fixed)         | HST        | Prioritas 1 - File Rekap               | Local-estimate   | DIKUNCI 60-65 HST (Batas ditarik sebelum malai keluar).                       |
| **t_lokal_aktif**           | 40 - 45                 | hari       | Turunan HST_masuk/heading              | Local-estimate   | Selisih matematis: HST_heading dikurangi HST_masuk.                           |
| **K_max_are**               | Jarwo 4, Tegel 3        | ekor/are   | Prioritas 2/4 - Wawancara & Azizi dkk. | Local-estimate   | Ambang batas kepadatan (Azizi dkk., 2023 & Wawancara).                        |
| **lambda**                  | 0.35 - 0.67             | rasio      | Prioritas 1 - File Rekap               | Local-estimate   | Laju kelangsungan hidup ternak (_survival rate_).                             |
| **baseline_hours**          | 10                      | jam/hari   | Prioritas 1 - File Rekap               | Local-estimate   | Waktu gembala harian di lahan (Prioritas 1).                                  |
| **p_gabah_konv**            | **[HOLD]**              | Rp/kg      | Menunggu Rekap Konvensional            | Menunggu Data    | Data kotor dibuang; menunggu Rekap Spesifik Konvensional dari mitra.          |
| **x0 (Yield konvensional)** | **[HOLD]**              | kg/are     | Menunggu Rekap Konvensional            | Menunggu Data    | Data kotor dibuang; menunggu Rekap Spesifik Konvensional dari mitra.          |
| **p_gabah_RD**              | Rp6.000                 | Rp/kg      | Prioritas 1 - Transaksi terbaru        | Local-calibrated | PRIORITAS 1: Harga organik aktual terbaru (Sept 2025).                        |
| **p_duck_buy**              | Rp25.000                | Rp/ekor    | Prioritas 1 - Transaksi terbaru        | Local-estimate   | PRIORITAS 1: Harga beli bibit transaksi paling mutakhir.                      |
| **p_duck**                  | Rp35.000                | Rp/ekor    | Prioritas 1 - Transaksi terbaru        | Local-estimate   | PRIORITAS 1: Harga jual bebek transaksi paling mutakhir.                      |
| **q_feed**                  | 0.10                    | kg/ekor/hr | Prioritas 5 - Literatur (Xiong)        | Lit-uncalibrated | HANYA untuk output edukasi informasi fisik pakan, tidak masuk komponen biaya. |
| **p_feed & C_feed**         | **0 (Dihapus)**         | Rp         | Aturan sistem (Hard Override)          | System-design    | ATURAN MUTLAK: Biaya pakan dianulir total (Salman dkk., 2024).                |
| **C_jaring**                | Rp1.350.000             | Rp         | Prioritas 1 - File Rekap               | Local-estimate   | Investasi pagar jaring (200m), amortisasi 3 siklus.                           |
| **C_kandang**               | Rp600.000               | Rp         | Prioritas 1 - File Rekap               | Local-estimate   | Investasi kandang (2x1m), amortisasi 4 siklus.                                |
| **P_N (Urea)**              | Rp1.800                 | Rp/kg      | Exception - HET Kepmentan              | Exception        | Pengecualian HET subsidi terkonfirmasi (Vipriyanti dkk., 2021).               |
| **P_P (Phonska)**           | Rp2.700                 | Rp/kg      | Exception - HET Kepmentan              | Exception        | Pengecualian HET subsidi NPK Phonska majemuk.                                 |
| **P_K (KCl)**               | Rp9.500                 | Rp/kg      | Exception - Harga pasar resmi          | Exception        | Pengecualian harga pasar KCl Mahkota Bunga Merah.                             |
| **C_gulma**                 | Rp15.000                | Rp/are     | Prioritas 2 - Wawancara                | Local-estimate   | Ditarik ke Prioritas 2 karena di Rekap Prioritas 1 biaya tercatat = 0.        |

---

### 4. Data Referensi Akademik yang Tetap Dipakai

| Komponen        | Nilai / Rumus Referensi                                                                             | Mengapa Tetap Dipakai                                                                                          | Catatan Wajib & Sitasi Ilmiah                                                            |
| :-------------- | :-------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------- |
| **x(d,t)**      | `x_base = (-0.0103 * d_ha^2 + 2.6314 * d_ha + 7569.4) * exp(-((t-80)^2)/(2 * 80^2))`                | Backbone yield padi-bebek yang menjadi kerangka utama model biologi panen.                                     | Kerangka utama yield padi (Xiong dkk., 2023). Dikalibrasi total dengan Bin Dominan.      |
| **V_duck_lit**  | `[-0.0096 * d_ha^2 + (11.3861 + 14.4 * lambda) * d_ha - 0.18 * lambda * t * d_ha + 17.0857] * A_ha` | Disimpan sebagai pembanding akademik terhadap model nilai bebek versi literatur.                               | Dilarang digunakan untuk profit riil. Hanya sisa pembanding akademik (Xiong dkk., 2023). |
| **Dung_total**  | `t <= 50: (t/50) * 4`. `t > 50: 4 + (t-50) * 0.2`                                                   | Dibutuhkan untuk mengaktifkan estimasi kotoran serta hara N/P/K tanah.                                         | Fungsi laju dekomposisi kotoran kumulatif (Wu dkk., 2021).                               |
| **kappa_N/P/K** | `N=0.049; P=0.072; K=0.032`                                                                         | Faktor konversi yang dibutuhkan agar N, P, K tanah dan V_pupuk_lokal dapat dihitung.                           | Faktor konversi kotoran menjadi hara setara NPK (Wu dkk., 2021).                         |
| **V_eco1**      | `max(0, (0.02*t - 0.6) * (0.107*P_N + 0.424*P_P + 0.058*P_K) * d_are * lambda * A_are)`             | Rumus penghematan pupuk dari model utama; guard `max(0, ...)` mencegah nilai negatif pada durasi lokal pendek. | Penurunan biaya input pupuk makro (Xiong dkk., 2023).                                    |
| **V_eco2**      | `(400 / (1 + exp(-0.036626 * d_ha)) - 3.327) * (A_are / 100)`                                       | Satu-satunya rumus yang tersedia untuk mengestimasi penghematan pestisida.                                     | Penghematan absolut PESTISIDA. Herbisida dianulir total (Xiong dkk., 2023).              |
| **REY**         | `REY = sum(Y_i * P_i) / P_rice`                                                                     | Indikator akademik untuk mengonversi output non-padi menjadi ekuivalen padi/beras.                             | Indikator Rice Equivalent Yield (Salman dkk., 2024).                                     |

---

### 5. Model Matematika End-to-End

#### 5.1 Input dan Konversi Satuan (Sistem Antarmuka)

Di dalam sistem aplikasi, input luasan dari pengguna (`A_are`) SECARA OTOMATIS diasumsikan sebagai Area Aktif Bebek.

- `d_aktual_are = J / A_are` (Kepadatan yang dipahami petani, satuan ekor/are).
- `d_lit_ha = d_aktual_are * 100` (Catatan konversi khusus untuk rumus literatur Xiong; output DSS tetap dikembalikan ke ekor/are).
- `x_final_kg_are = x_final_kg_ha / 100` (Output utama petani dan paper lokal ditampilkan sebagai kg/are, bukan kg/ha).

#### 5.2 Lookup Agronomi dan Kalender (Fakta Empiris Rekap)

Berdasarkan "Truth of Priority" (Prioritas 1: File Rekap melalui Bin Dominan), pola Tegel terbukti lebih superior:

| Varietas (V)   | Sistem Tanam (S) | HST_masuk | HST_heading | t_lokal | K_max | f_yield |
| :------------- | :--------------- | :-------- | :---------- | :------ | :---- | :------ |
| Sertani/Inpari | Jarwo            | 20        | 60-65       | 40-45   | 4     | 1.00    |
| Sertani/Inpari | Tegel            | 20        | 60-65       | 40-45   | 3     | 1.39    |

**Catatan Faktual f_yield:** Di File Rekap, Median Bin Dominan Jarwo = 43.45 kg/are. Median Bin Dominan Tegel (intervensi bebek) = 60.60 kg/are. Maka, `f_yield` Tegel = 60.60 / 43.45 = 1.39.

- `tanggal_lepas = TD + HST_masuk` (Output jadwal ke petani; menandai hari bebek mulai dilepas ke petak sawah).
- `tanggal_tarik = TD + HST_masuk + t` (Bebek tidak boleh melewati fase keluar malai; `t` dibatasi oleh `HST_heading - HST_masuk`).

#### 5.2A Integrasi Umur Bebek

Umur bebek (`U_bebek`) diperlakukan eksklusif sebagai "Quality Gate" pengaman lahan, bukan sebagai pengubah harga (karena harga sudah dipatok ke transaksi mutakhir):

- `t_age_max = max(0, min(t_lokal_max, 60 - U_bebek))` (Batas durasi maksimum dari sisi umur; makin tua bebek saat masuk, makin pendek durasi maksimum yang direkomendasikan).
- `C_duck_buy = J * p_duck_buy_age` (Dari transaksi terbaru = Rp25.000). Harga beli memakai transaksi paling mutakhir sesuai aturan Eksekusi Ekonomi Berbasis Waktu.

#### 5.3 Durasi, Survival, dan Kotoran

Bebek panen (`N_d`) = `J * lambda` (asumsi 0.67). Kotoran kumulatif petak (Wu dkk., 2021):

- `Dung_are = Dung_total(t) * d_aktual_are * lambda` (Estimasi total kotoran per are dari populasi bebek yang bertahan hidup; status Lit-uncalibrated).

#### 5.4 Hara Tanah dan Valuasi Pupuk Lokal

- `N_tanah_are = 0.049 * (Dung_total / 10) * d_aktual_are * lambda` (kappa_N=0.049 berbasis referensi literatur Wu dkk., 2021; estimasi setara N).
- `P_tanah_are = 0.072 * (Dung_total / 10) * d_aktual_are * lambda` (kappa_P=0.072 sebagai P2O5 ekuivalen).
- `K_tanah_are = 0.032 * (Dung_total / 10) * d_aktual_are * lambda` (kappa_K=0.032 sebagai K2O ekuivalen).

Valuasi menggunakan harga HET (Vipriyanti dkk., 2021):

- `V_pupuk_lokal = (N_tanah_are * 1800 + P_tanah_are * 2700 + K_tanah_are * 9500) * A_are` (Output rupiah dari substitusi hara kotoran bebek terhadap kebutuhan pupuk kimia).

#### 5.5 Model Yield Padi (Kalibrasi `alpha_local` = 0.643)

Pengintegrasian kerangka (Xiong dkk., 2023) dengan parameter empiris lokal wajib didiskon menggunakan `alpha_local = 0.643` agar proyeksi 67.54 kg/are dari Tiongkok selaras dengan median empiris Jarwo di Bali (43.45 kg/are).

- `x_base_kg_ha = (-0.0103 * d_lit_ha^2 + 2.6314 * d_lit_ha + 7569.4) * exp(-((t - 80)^2) / (2 * 80^2))`
- `P_rate = min(1.0, 0.5 * (d_aktual_are - K_max_are) / K_max_are)` (Hanya dihitung jika `d_aktual_are > K_max_are`; tidak ada penalti pada kepadatan di bawah atau sama dengan daya dukung lokal).
- **`x_final_kg_are = 0.643 * [x_base_kg_ha / 100 * (1 - P_rate)] * f_yield`**

#### 5.6 Ekonomi Padi, Bebek, Infrastruktur, dan Profit

Subak Bali murni mengandalkan pakan alamiah (Salman dkk., 2024), maka `C_feed` = 0.

- `R_gabah_RD = x_final_kg_are * A_are * 6.000` (Pendapatan gabah organik padi-bebek; harga Rp6.000/kg memakai transaksi terbaru (Prioritas 1)).
- `R_gabah_K = [HOLD / MENUNGGU DATA]` (Baseline konvensional dikosongkan sampai tersedia Rekap Spesifik Konvensional yang bersih).
- `DeltaV_rice = [HOLD / MENUNGGU DATA]` (Nilai tambah terhadap baseline konvensional tidak dapat dihitung selama `R_gabah_K` masih HOLD).

Ekonomi ternak murni:

- `V_duck_lokal = (N_d * 35.000) - (J * 25.000)` (Margin murni peternakan bebek tanpa beban biaya pakan).

Laba Bersih Sistem Padi-Bebek Saja:

- `Laba_bersih = R_gabah_RD + V_duck_lokal + V_eco - C_infra` (Komponen dari data lokal berstatus Local-estimate/Local-calibrated; komponen dari artikel referensi tetap berstatus Lit-uncalibrated).

#### 5.7 Manfaat Ekologis-Finansial (V_eco)

- `V_eco1 = max(0, (0.02*t - 0.6) * (0.107*1800 + 0.424*2700 + 0.058*9500) * d_aktual_are * lambda * A_are)` (Guard `max(0, ...)` mencegah nilai penghematan pupuk tampil negatif pada durasi lokal pendek).
- `V_eco2 = (400 / (1 + exp(-0.036626 * d_lit_ha)) - 3.327) * (A_are / 100)` (Penghematan Pestisida; herbisida sudah dianulir total sehingga tidak lagi masuk komponen ini).
- `V_gulma = 15.000 * A_are * min(1.0, d_aktual_are / K_max_are)` (Komponen lokal paling siap karena biaya baseline cabut gulma (`C_gulma`) sudah tersedia dari data lokal).
- `V_eco = V_eco1 + V_eco2 + V_gulma` (Total manfaat ekologis-finansial; komponen tetap ditampilkan terpisah agar tidak overclaim).

#### 5.8 Modul Emisi & Lingkungan

Emisi metana (CH4), N2O, dan kualitas air (DO) TIDAK DIHITUNG dalam matematika Skenario Petani/Rekomendasi (Limitation).

| Data                                 | Kegunaan                                      | Status                    |
| :----------------------------------- | :-------------------------------------------- | :------------------------ |
| **F_CH4_RD**                         | Menghitung CO2e padi-bebek                    | Tidak tersedia dari mitra |
| **F_N2O_RD**                         | Menghitung CO2e padi-bebek                    | Tidak tersedia dari mitra |
| **F_CH4_konv**                       | Menghitung Reduksi_CH4                        | Tidak tersedia dari mitra |
| **F_N2O_konv**                       | Membandingkan CO2e konvensional vs padi-bebek | Tidak tersedia dari mitra |
| **X_DO**                             | Mengaktifkan model DO-to-CH4                  | Tidak tersedia dari mitra |
| **flooded_days / drainage calendar** | Menjelaskan konteks emisi musiman             | Tidak tersedia dari mitra |

#### 5.9 Objective Function (Optimasi DSS)

Fungsi optimasi dieksekusi dengan syarat gerbang keselamatan (Safety Gate):

- `Score_safety = I(HST_masuk + t <= HST_heading) * I(d_are <= K_max_are) * I(A_are > 0)` (Safety gate wajib sebelum optimasi; kandidat yang melewati fase keluar malai atau melewati `K_max_are` tidak dipilih sebagai skenario aman).
- `F_active(d, t) = w_yield * Score_yield + w_eco * Score_ecology + w_econ * Score_economy - w_risk * Risk_penalty` (`Score_yield` dan `Score_ecology` selalu aktif; `Score_economy` hanya masuk bila `Laba_bersih` numerik siap dihitung).
- `J_rekomendasi = round(d_optimal * A_are)` (Output jumlah bebek rekomendasi harus berupa bilangan bulat / integer).

---

### 6. Kamus Variabel Teks Aktif DSS

Kamus ini **HANYA** memuat variabel yang menjadi bagian aktif DSS pada Versi Final. Semua parameter yang telah disepakati untuk di-HOLD atau dihapus (seperti `C_feed`, `p_feed`, `x0`, emisi, dll) dipindahkan ke Bab 7 (Limitation).

| No  | Variabel         | Kelompok             | Makna & Definisi Operasional                              | Satuan   | Status Klaim                             |
| :-- | :--------------- | :------------------- | :-------------------------------------------------------- | :------- | :--------------------------------------- |
| 1   | **d**            | Decision variable    | Kepadatan ternak yang dioptimasi pada luasan aktif.       | ekor/are | Lit + Local constraint                   |
| 2   | **t**            | Decision variable    | Durasi sinkronisasi kalender bebek dan padi.              | hari     | Local-estimate + constraint              |
| 3   | **J**            | Input                | Populasi total bibit unggas rilis awal.                   | ekor     | Local-calibrated                         |
| 4   | **A_are**        | Input                | Luas input pengguna (Mutlak Area Aktif Bebek).            | are      | System-design                            |
| 5   | **TD**           | Input                | Jangkar waktu penanaman bibit padi (Hari ke-0).           | tanggal  | Local input                              |
| 6   | **V**            | Input                | Pilihan varietas unggul tahan hama.                       | kategori | Local-estimate                           |
| 7   | **S**            | Input                | Tipe formasi spasial penanaman (Jarwo/Tegel).             | kategori | Local-estimate                           |
| 8   | **U_bebek**      | Input / Quality gate | Indikator ketuaan bibit unggas rilis.                     | hari     | Local-estimate                           |
| 9   | **p_gabah_RD**   | Parameter harga      | Harga jual produk gabah pertanian terpadu.                | Rp/kg    | Local-calibrated (Rp6.000)               |
| 10  | **p_duck**       | Parameter harga      | Harga pasaran potong per individu unggas.                 | Rp/ekor  | Local-estimate (Rp35.000)                |
| 11  | **P_N**          | Parameter harga      | Standar tebus subsidi unsur Nitrogen (Urea).              | Rp/kg    | Exception (Rp1.800)                      |
| 12  | **P_P**          | Parameter harga      | Standar tebus subsidi unsur Fosfat (Phonska).             | Rp/kg    | Exception (Rp2.700)                      |
| 13  | **P_K**          | Parameter harga      | Standar harga eceran unsur Kalium (KCl Mahkota).          | Rp/kg    | Exception (Rp9.500)                      |
| 14  | **p_duck_buy**   | Parameter biaya      | Nilai kapital modal pembelian bibit Day/Week-Old.         | Rp/ekor  | Local-estimate (Rp25.000)                |
| 15  | **C_jaring**     | Parameter biaya      | Penyusutan beban kapital material pembatas.               | Rp       | Local-estimate                           |
| 16  | **C_kandang**    | Parameter biaya      | Penyusutan beban kapital material naungan.                | Rp       | Local-estimate                           |
| 17  | **C_gulma**      | Parameter biaya      | Biaya ekuivalensi tenaga manusia cabut gulma.             | Rp/are   | Local-estimate (Rp15.000)                |
| 18  | **lambda**       | Biologis bebek       | Proporsi kebertahanan hidup populasi hingga panen.        | rasio    | Local-estimate (0.67)                    |
| 19  | **Dung_total**   | Biologis bebek       | Akumulasi tonase feses per satuan populasi.               | kg/ekor  | Lit-uncalibrated (Wu)                    |
| 20  | **kappa_N/P/K**  | Biologis bebek       | Faktor pemecahan senyawa makro dari limbah.               | rasio    | Lit-uncalibrated (Wu)                    |
| 21  | **q_feed**       | Biologis/edukasi     | Edukasi prediksi suplementasi gizi harian fisik.          | kg/hr    | Lit-uncalibrated (Xiong)                 |
| 22  | **HST_masuk**    | Lookup agronomi      | Batas umur tunas aman merespons pergerakan.               | HST      | Local-calibrated (20)                    |
| 23  | **HST_heading**  | Lookup agronomi      | Batas kerentanan bulir terhadap ancaman herbivori.        | HST      | Local-estimate (60-65)                   |
| 24  | **K_max_are**    | Lookup agronomi      | Daya tampung ekologis pelestarian lahan.                  | ekor/are | Local-estimate (Jarwo 4, Tegel 3)        |
| 25  | **f_yield**      | Lookup agronomi      | Skalar empiris respons tata letak tanam.                  | rasio    | Local-calibrated (Jarwo 1.0, Tegel 1.39) |
| 26  | **alpha_local**  | Skalar kalibrasi     | Penyama fungsi Tiongkok terhadap lahan Bali.              | rasio    | Local-calibrated (0.643)                 |
| 27  | **baseline_hr**  | Operasional lokal    | Konstanta rentang waktu bebek aktif di lumpur.            | jam/hr   | Local-estimate (10)                      |
| 28  | **x_final**      | Dependent yield      | Akumulasi absolut tonase gabah termodifikasi.             | kg/are   | Mixed                                    |
| 29  | **V_duck_lokal** | Dependent ekonomi    | Kalkulasi Margin Laba Rugi sub-sistem peternakan.         | Rp       | Local-estimate                           |
| 30  | **V_eco**        | Dependent ekologi    | Nominalisasi agregat jasa ekosistem (pupuk, hama, gulma). | Rp       | Mixed                                    |
| 31  | **Laba_bersih**  | Dependent ekonomi    | Total pencapaian kapital finansial sistem penuh.          | Rp       | Local-estimate                           |
| 32  | **DeltaProfit**  | Dependent ekonomi    | Kesenjangan finansial Skenario Optimal vs Aktual.         | Rp       | Local-estimate                           |
| 33  | **Q_output**     | Output kualitas      | Skala kepercayaan validitas rekomendasi DSS.              | kategori | System-design                            |

---

### 7. Limitation Penelitian dan Variabel Non-Aktif

Semua parameter yang telah disepakati untuk tidak digunakan dipindahkan ke tabel ini.

| Komponen Non-Aktif                                   | Status                       | Alasan                                                                                                                                           |
| :--------------------------------------------------- | :--------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------- |
| **Biaya Pakan Tambahan (`C_feed`, `p_feed`)**        | **Hard Override (= 0)**      | Praktik lapangan lokal (Salman dkk., 2024) tidak membebankan biaya pembelian pelet komersial. Memasukkannya akan membiaskan ekonomi riil petani. |
| **Baseline Konvensional (`x0`, `p_gabah_konv`)**     | **HOLD**                     | Diabaikan sementara untuk menanti data rekap spesifik konvensional yang bersih, agar komparasi margin Delta tidak menyesatkan.                   |
| **Herbisida Sintetis**                               | **Hard Override (dianulir)** | Praktik ekologis subak sama sekali tidak menyentuh herbisida; penyiangan dilakukan secara mekanis oleh kaki bebek.                               |
| **Emisi dan Iklim Mikro (CO2e, GHGI, CH4, N2O, DO)** | **Limitation**               | Inventarisasi gas metana (CH4) dan oksigen terlarut (DO) membutuhkan riset instrumentasi in-situ yang belum tersedia.                            |
| **Bobot Penjualan Daging Bebek**                     | **Limitation**               | Harga jual bebek diukur per ekor hidup akibat besarnya disparitas genetik ras lokal (Yurnalis dkk., 2019; Wang dkk., 2025).                      |

---

### 8. Data Collection Lanjutan untuk Peningkatan DSS

Prioritas masa depan untuk Tim Astungkara Way:

| Kelompok                         | Kebutuhan Data                                          | Prioritas              | Tujuan                                                                          |
| :------------------------------- | :------------------------------------------------------ | :--------------------- | :------------------------------------------------------------------------------ |
| **Sistem Input Lahan**           | Validasi luas lahan pengguna berbasis batas GPS.        | Prioritas 1            | Meminimalisasi bias manusia pada input luasan lahan.                            |
| **Data Plot Konvensional Murni** | Sampel bersih `x0` (kg/are) dan `p_gabah_konv` (Rp/kg). | Prioritas 1 (Mendesak) | Mengisi kekosongan variabel HOLD agar komparasi Delta dapat diaktifkan kembali. |
| **Biaya Hama Aktual**            | Slip pengeluaran faktual Insektisida/Fungisida.         | Prioritas 2            | Mengubah fungsi literatur `V_eco2` menjadi fungsi empiris riil.                 |

---

### 9. Aturan Implementasi Sistem (R-Rules Terpadu System Edition)

| Aturan                      | Keputusan                                                                                                                                    | Alasan                                                                                          |
| :-------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------- |
| **R-01 Basis Area**         | Input lahan `A_are` dari sisi pengguna (user) OTOMATIS dideklarasikan sebagai Luas Area Aktif Bebek.                                         | Menyederhanakan antarmuka sistem dan menghindari kesalahan pembagian luas di sisi front-end.    |
| **R-02 Keseragaman Satuan** | Seluruh operasi matematika dan presentasi dashboard menggunakan basis ARE (bukan Hektar).                                                    | Menjaga konsistensi satuan yang dipahami petani lokal dan menghindari kesalahan skala 100 kali. |
| **R-03 Eksekusi Durasi**    | Sistem mengunci batas penarikan secara mutlak (harus sebelum malai keluar).                                                                  | Melindungi integritas bulir padi dari risiko herbivori bebek pada fase generatif.               |
| **R-04 Superioritas Tegel** | Fakta empiris Bin Dominan mengunci pengali sistem Tegel (`f_yield` 1.39) lebih tinggi dan lebih superior secara hasil daripada Jarwo (1.00). | Merefleksikan hasil panen aktual di lapangan sesuai filter data resmi Prioritas 1.              |
| **R-05 Penghapusan Pakan**  | Komputasi `C_feed` = Rp0. Parameter Laba Rugi bebas dari beban pakan.                                                                        | Sesuai realitas ekosistem subak Bali yang mengandalkan pakan alamiah sawah sepenuhnya.          |
| **R-06 Standar Pupuk**      | Perhitungan substitusi pupuk organik dipatok pada instrumen HET subsidi Urea, NPK Phonska, dan harga eceran KCl Mahkota.                     | Menjamin valuasi manfaat ekologis memakai harga acuan resmi yang dapat diverifikasi.            |

---

### 10. Skenario Output DSS dan Status Klaim

#### 10.1 Laporan Penilaian Kondisi Aktual

Mengevaluasi keputusan tebar eksisting petani:

| Output DSS               | Rumus Perhitungan                                                   | Penjelasan                                                             | Status Klaim     |
| :----------------------- | :------------------------------------------------------------------ | :--------------------------------------------------------------------- | :--------------- |
| **Kepadatan Diterapkan** | `d_aktual_are = J / A_are`                                          | Membaca kepadatan bebek yang sesungguhnya diterapkan petani.           | Calculated       |
| **Peringatan Agronomis** | Flag jika `d_are > K_max_are`                                       | Teguran visual merah jika kepadatan melebihi batas (Tegel 3, Jarwo 4). | System-design    |
| **Proyeksi Hasil Padi**  | `x_final_kg_are = 0.643 * [x_base_kg_are * (1 - P_rate)] * f_yield` | Estimasi hasil panen padi pada kondisi aktual petani.                  | Mixed            |
| **Pendapatan Gabah**     | `x_final * A_are * Rp6.000`                                         | Estimasi pendapatan kotor dari penjualan gabah organik.                | Local-calibrated |
| **Net Profit Ternak**    | `(N_d * Rp35.000) - (J * Rp25.000)`                                 | Margin murni peternakan tanpa biaya pakan.                             | Local-estimate   |

#### 10.2 Mesin Rekomendasi Optimal

Motor pencari jalan keluar terbaik:

| Output DSS                   | Rumus Perhitungan                          | Penjelasan                                                                                                 | Status Klaim   |
| :--------------------------- | :----------------------------------------- | :--------------------------------------------------------------------------------------------------------- | :------------- |
| **Titik Puncak (argmax)**    | `argmax F_active(d, t)`                    | Mengeksekusi algoritma F_active untuk mencari keseimbangan tertinggi ekologi-ekonomi sebelum malai keluar. | System-design  |
| **Modifikasi Tebar (J_rec)** | `J_rekomendasi = round(d_optimal * A_are)` | Jumlah spesifik anak bebek yang seharusnya disiapkan petani.                                               | Calculated     |
| **Janji Kesejahteraan**      | `DeltaProfit = Laba_optimal - Laba_aktual` | Visualisasi Rupiah ekstra yang didapat jika mematuhi rekomendasi DSS.                                      | Local-estimate |

---

### 11. Contoh Perhitungan Ilustratif Berbasis Validasi Empiris (Tegel Edition)

| Blok         | Variabel                    | Hasil                                                           | Catatan                                                                   |
| :----------- | :-------------------------- | :-------------------------------------------------------------- | :------------------------------------------------------------------------ |
| **Input**    | `A_are`                     | 7 are                                                           | Otomatis Area Aktif Bebek, Sistem Tanam: TEGEL, Tanam (TD) = 1 Juni 2026. |
| **Input**    | `J`                         | 15 ekor                                                         | Jumlah bebek ditebar.                                                     |
| **Lookup**   | `HST_masuk` / `HST_heading` | 20 HST / 65 HST                                                 | Sesuai lookup Tegel pada tabel 5.2.                                       |
| **Derivasi** | `t`                         | 45 hari                                                         | Durasi aktif kalender bebek di sawah.                                     |
| **Lookup**   | `K_max_are` / `f_yield`     | 3 ekor/are / 1.39                                               | Kapasitas dan pengali Tegel.                                              |
| **Derivasi** | `d_are`                     | 15 / 7 = 2.14 ekor/are                                          | Berada di bawah batas 3; Skenario SAFE, Penalti (`P_rate`) = 0.           |
| **Biologi**  | `N_d`                       | 15 \* 0.67 = 10 ekor                                            | Bebek yang bertahan hingga panen.                                         |
| **Harga**    | Beli / Jual                 | Rp25.000 / Rp35.000                                             | Memakai transaksi paling mutakhir.                                        |
| **Yield**    | `d_ha` (literatur)          | 214 ekor/ha                                                     | Konversi `d_aktual_are * 100` untuk rumus Xiong.                          |
| **Yield**    | `x_base` (literatur)        | 6962.00 kg/ha                                                   | Laju panen murni literatur Xiong pada `d_ha=214`, `t=45`.                 |
| **Yield**    | `x_final_are`               | **0.643** _ (6962.00/100) _ 1.39 = 62.22 kg/are                 | Laju panen per are termodifikasi Tegel.                                   |
| **Yield**    | Total Panen Gabah           | 62.22 \* 7 = 435.54 kg                                          | Total panen gabah di 7 are.                                               |
| **Ekonomi**  | `R_gabah_RD`                | 435.54 \* Rp6.000 = Rp2.613.240                                 | Perbandingan Delta Konvensional di-HOLD.                                  |
| **Ekonomi**  | `V_duck_lokal`              | (10*35.000) - (15*25.000) = -Rp25.000                           | Rugi bibit tertutup oleh surplus panen padi.                              |
| **Ekologis** | Substitusi Pupuk NPK        | Rp5.688                                                         | Komponen `V_eco1`.                                                        |
| **Ekologis** | Substitusi Pestisida        | 27.76 (Indeks Xiong belum dikonversi)                           | Komponen `V_eco2`.                                                        |
| **Ekologis** | Hemat Cabut Gulma           | 15000 _ 7 _ (2.14/3) = Rp74.900                                 | Komponen `V_gulma`.                                                       |
| **Ekologis** | Total `V_eco`               | Rp5.688 + 27.76 + Rp74.900 = Rp80.615                           | Total Jasa Lingkungan Padi-Bebek (pembulatan).                            |
| **Infra**    | `C_infra`                   | Rp600.000                                                       | Penyusutan Jaring + Kandang.                                              |
| **HASIL**    | `Laba_bersih`               | Rp2.613.240 - Rp25.000 + Rp80.615 - Rp600.000 = **Rp2.068.855** | Laba bersih siklus untuk 7 are.                                           |

---

### 12. Ringkasan Integrasi Umur Bebek

Umur unggas rilis (`U_bebek`) berfungsi murni sebagai gembok kelayakan ekosistem (_quality gate_) dan mitigasi risiko lahan, bukan sebagai variabel yang mengubah biologi, pakan, atau harga bebek. Pada Versi Final ini, harga beli bebek (`p_duck_buy`) sudah dikunci pada transaksi paling mutakhir (Rp25.000/ekor) sesuai aturan Eksekusi Ekonomi Berbasis Waktu, sehingga umur bebek tidak lagi memengaruhi harga.

Peran `U_bebek` dibatasi pada empat hal berikut agar tidak menimbulkan klaim biologis yang berlebihan:

1. **Harmonik Ekologis:** Bibit usia 14-21 hari diwajibkan sinkron masuk di rentang HST 20.
2. **Korelasi Harga:** Mencegah disonansi keuangan akibat fluktuasi nilai bibit terhadap umur, karena harga sudah dipatok dari transaksi terbaru.
3. **Rem Darurat Durasi:** Sistem akan memotong batas durasi panen bebek secara otomatis (`t_age_max`) jika petani menginput unggas yang terlalu tua, demi melindungi integritas bulir padi.
4. **Skor Integritas Skenario:** Output DSS akan diberi _flag_ "High Confidence" hanya apabila usia bibit selaras dengan matriks kalender lahan.

Dengan demikian, keputusan praktis Versi Final adalah: umur bebek memengaruhi `t_age_max`, `tanggal_tarik`, dan `Q_output`. Seluruh pengaruh lain terhadap yield, pakan, survival, kotoran, bobot jual, dan harga tetap menjadi limitation serta kebutuhan data collection lanjutan sebagaimana dicatat pada Bagian 7 dan Bagian 8.

---

### 13. Daftar Pustaka (APA Style 7th Edition)

1. Arsil, P., Sahirman, S., Ardiansyah, A., & Hidayat, S. (2019). The reasons for farmers not to adopt System of Rice Intensification (SRI) as a sustainable agricultural practice: an explorative study. _Journal of Agricultural Science_.
2. Azizi, M., Syamsuddin, S., & Basyah, B. (2023). Integration of rice-duck on growth and yield of paddy crops (Oryza sativa L.). _Aceh Journal of Animal Science_.
3. Balai Pengkajian Teknologi Pertanian (BPTP) Bali. (2024). _Petunjuk teknis budidaya padi sawah sistem Jajar Legowo dan pengelolaan terpadu di lahan subak Bali_. Badan Litbang Pertanian.
4. Kementerian Pertanian Republik Indonesia. (2025). _Keputusan Menteri Pertanian Nomor 1117/Kpts./SR.310/M/10/2025 tentang Harga Eceran Tertinggi (HET) Pupuk Bersubsidi Sektor Pertanian Tahun Anggaran 2026_. Jakarta: Kementerian Pertanian RI.
5. PT Petrokimia Gresik. (2025). _Spesifikasi dan peruntukan pupuk majemuk NPK Phonska bersubsidi dan pupuk fosfat_. PT Pupuk Indonesia (Persero) Group.
6. PT Pupuk Indonesia (Persero). (2025). _Spesifikasi produk pupuk Urea prill bersubsidi dan non-subsidi_.
7. Salman, D., Kasim, K., Ahmad, A., Syahruddin, S., & Amiruddin, A. (2024). Carrying capacity of natural feed and ecological-economic sustainability of integrated rice-duck farming systems in South Sulawesi, Indonesia. _Agricultural Systems_, 215, 103845.
8. Vipriyanti, N. U., Yulianti S., P. L., Puspawati, D. A., Handayani, M. E., Tariningsih, D., & Malung, Y. U. (2021). The efficiency of duck rice integrated system for sustainable farming. _Jurnal Ekonomi Pertanian_.
9. Wilmar Chemical / PT Pupuk Mahkota. (2025). _Spesifikasi teknis pupuk tunggal makro Kalium Klorida (KCl) Mahkota Bunga Merah_.
10. Wu, X., Wang, Y., Zhou, S., & Liang, T. (2021). Ecological and economic assessment of dung nutrient contribution and carbon footprint in rice-duck integrated farming systems. _Science of the Total Environment_, 780, 146618.
11. Xiong, D., Fang, K., Luo, Y., & Dai, X. (2023). Optimization modeling of density and grazing duration for maximizing yield and economic-ecological benefits in integrated rice-duck farming. _Agricultural Systems_, 208, 103652.
12. Yurnalis, Arnim, Putra, D.E., Kamsa, Z., & Afriani, T. (2019). Identification of GH Gene Polymorphisms and Their Association with Body Weight in Bayang Duck, Local Duck from West Sumatra, Indonesia.
13. Wang, N., Li, J., & Zhou, Z. (2025). Landscape pattern optimization approach to protect rice terrace agroecosystem: Case of GIAHS site Jiache Valley, Guizhou, southwest China.
