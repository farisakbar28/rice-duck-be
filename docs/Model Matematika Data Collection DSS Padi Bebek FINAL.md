# Economic Differential-Costing Engine untuk Agroekosistem Padi-Bebek

## 1. Ringkasan Eksekutif

Dokumen ini merumuskan secara utuh arsitektur Economic Differential-Costing Engine yang memfasilitasi evaluasi kelayakan finansial mendalam atas penerapan agroekosistem padi-bebek. Berbeda dengan model akuntansi usahatani agrikultur statis pada umumnya, konstruksi pendekatan diferensial (inkremental) di dalam model ini mengisolasi secara eksklusif variabel aliran kas serta intervensi biaya yang berfluktuasi murni akibat hadirnya populasi unggas di area tanam. Biaya-biaya kultivasi tetap, seperti pengolahan traktor basal atau proses semai persemaian yang secara alamiah terbentuk tanpa kehadiran integrasi bebek, dikesampingkan agar matriks evaluasi berfokus mutlak pada analisis impak.

Sistem ini merajut beragam input operasional lapangan yang meliputi total area basah efektif, kepadatan per satuan petak, taksonomi varietas padi, arsitektur jarak tanam spasial, dan profil kronologis umur ternak untuk kemudian disuling melewati kompartemen komputasi independen. Modul-modul ini meliputi Age Engine dan Density Engine yang berfungsi menentukan rasio kerugian gesekan akibat penyimpangan batas alam; Survival Engine yang mengekstrapolasikan proyeksi harapan hidup ternak dari fungsi kepadatan; Yield Engine untuk mentranslasikan intervensi panen; Material Engine untuk kalkulasi substitusi kimiawi; serta Cost Engine guna membukukan arus logistik tunai. Hasil perhitungan direkombinasikan guna menelurkan agregasi $\text{Profit\_net\_cash}$ sebagai cermin langsung daya beli dan likuiditas tunai riil petani.

Seluruh komponen model terpartisi tegas ke dalam dua kelompok fungsional: kelompok Aktif (Included Components) yang membentuk kalkulasi eksekusi utama $\text{Profit\_net\_cash}$, dan kelompok Cadangan (Sandbox/Excluded Components) yang terdiri dari parameter-parameter dengan volatilitas pencatatan tinggi atau standar praktik lapangan yang belum seragam antarpetani. Kelompok kedua ini tetap difinalisasi penuh rumus dan nilai acuannya, sehingga senantiasa siap diaktifkan kembali (_plug-and-play_) ke dalam sirkuit kalkulasi utama tanpa memerlukan rekonstruksi ulang.

---

## 2. Status Klaim dan Parameter Dasar

Metodologi pengambilan dan kalibrasi parameter moneter serta produktivitas dibangun memprioritaskan fungsi agregasi median persentil ke-50, sebuah instrumen matematika yang tangguh (_robust_) dalam menangkal distorsi ekstrim tipikal data observasi empiris. Formulasi juga ditopang oleh triangulasi data yang melibatkan pencatatan rekapitulasi primer, evaluasi kualitatif batas (_boundary validation_) operasional, konsensus ekspertis lapangan, serta validasi silang lintas hierarki sumber (rekapitulasi mentah, rekapitulasi bersih, hasil wawancara terstruktur, dan literatur _peer-reviewed_). Setiap baris data yang teridentifikasi sebagai nilai duplikat, _placeholder_, atau imputasi dieksklusi secara sistematis dari basis kalkulasi median guna mencegah bias sirkular.

| Parameter                      | Nilai               | Status                  | Mengapa                                                                                                                                                                                                                                                                                  |
| ------------------------------ | ------------------- | ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| $Y_0$                          | 47,8767507 kg/are   | Local-validated         | Median empirik produktivitas vegetatif spesifik agroekosistem padi-bebek, terekstraksi dari agregasi lintas-siklus dataset historis lapangan riil, pasca penerapan protokol _masking_ nilai kosong/nol dan eksklusi baris anomali pencatatan.                                            |
| $p_{\text{gabah}}$             | Rp6.000/kg          | Local-validated         | Cerminan moda transaksi aktual pada jaringan distribusi hasil panen, berbasis agregasi pencatatan harga jual komoditas lapangan.                                                                                                                                                         |
| $p_{\text{duck\_sell}}$        | Rp35.000/ekor       | Local-validated         | Valuasi harga apresiasi pasar unggas hidup spesifik wilayah, berbasis agregasi pencatatan primer peternak.                                                                                                                                                                               |
| $p_{\text{duck\_buy}}$         | Rp25.000/ekor       | Local-validated         | Taksiran batas bawah (_lower bound_) konservatif nilai investasi bibit usia 2-3 minggu, diekstraksi dari konsolidasi wawancara operasional lapangan.                                                                                                                                     |
| $HST_{\text{panen}}$ (Sertani) | 114 hari            | Local-validated         | Median siklus panen aktual pematangan fenologi kultivar, diukur berdasarkan agregasi lintas-siklus pada dataset rekapitulasi historis primer, pasca filtrasi baris duplikat/_placeholder_.                                                                                               |
| $HST_{\text{panen}}$ (Inpari)  | 134 hari            | Local-validated         | Median siklus panen aktual pematangan fenologi kultivar, diukur berdasarkan agregasi lintas-siklus pada dataset rekapitulasi historis primer, pasca filtrasi baris duplikat/_placeholder_.                                                                                               |
| $k_{\text{weed\_hire}}$        | Rp26.178/are        | Local-estimate          | Tarif bayangan (_shadow price_) beban penyiangan, diekstraksi dari transaksi primer valid dan independen tercatat pada rekapitulasi mentah lapangan. Komponen biaya terisolasi dari sirkuit agregasi kas tunai utama.                                                                    |
| $C_{\text{pest\_base}}$        | Rp2.135/are         | Local-estimate          | Representasi ekuivalen moneter kontrol hama. Komponen biaya terisolasi dari sirkuit agregasi kas tunai utama.                                                                                                                                                                            |
| $C_{\text{feed\_base}}$        | Rp4.500/ekor/siklus | Local-validated         | Median empiris biaya pakan tambahan non-nol lintas siklus tercatat pada rekapitulasi mentah lapangan.                                                                                                                                                                                    |
| $\kappa_N$                     | 0,049               | Literature-uncalibrated | Faktor kandungan hara referensi untuk Nitrogen, terverifikasi presisi hingga baris ekstraksi numerik primer literatur referensi (Xiong et al., 2014). Status _uncalibrated_ merujuk pada fungsi transformasi temporal yang menaunginya, bukan pada konstanta kandungan hara itu sendiri. |
| $\kappa_P$                     | 0,072               | Literature-uncalibrated | Faktor kandungan hara referensi untuk Fosfor ($\text{P}_2\text{O}_5$), terverifikasi presisi ke ekstraksi numerik primer literatur referensi (Xiong et al., 2014), dengan catatan status yang sama seperti $\kappa_N$.                                                                   |
| $\kappa_K$                     | 0,032               | Literature-uncalibrated | Faktor kandungan hara referensi untuk Kalium ($\text{K}_2\text{O}$), terverifikasi presisi ke ekstraksi numerik primer literatur referensi (Xiong et al., 2014), dengan catatan status yang sama seperti $\kappa_N$.                                                                     |

---

## 3. Input Model

Spesifikasi dimensi operasional dari peranti masuk lapangan menuntut akurasi spasial dan kronologis, membatasi diri eksklusif pada metrik dengan densitas reliabilitas maksimum.

| Nama Masukan      | Simbol                         | Satuan   | Aturan                         | Mengapa                                                                                                                                                                  |
| ----------------- | ------------------------------ | -------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Luas lahan aktif  | $A_{\text{are}}$               | are      | Luasan petak genangan efektif  | Mendefinisikan landasan operasional, skala ekonomi, dan daya dukung spasial awal — didefinisikan sebagai area aktif interaksi bebek, bukan luas total kepemilikan lahan. |
| Populasi unggas   | $J$                            | ekor     | Total biomasa bibit diinjeksi  | Memicu fluktuasi penalti kepadatan, beban pakan sintesis, dan valuasi panen akhir.                                                                                       |
| Sistem tanam      | $S$                            | kategori | Klasifikasi Jarwo / Tegel      | Merekonstruksi matriks toleransi geometri mobilitas ternak ($K_{\text{safe}}$) dan diferensial produktivitas antar sistem tanam ($F_{\text{sys}}$).                      |
| Varietas padi     | $V$                            | kategori | Takson Sertani / Inpari        | Mensinkronisasi ritme kalender agronomi menuju tenggat pemanenan gabah absolut.                                                                                          |
| Tanggal tanam     | $D_{\text{tanam}}$             | tanggal  | Inisiasi transplantasi (semai) | Poros kronologis (_anchor_) kalibrasi panen komoditas utama.                                                                                                             |
| Umur unggas       | $U_{\text{duck}}$              | hari     | Usia kronologis pasca-menetas  | Memicu kalkulasi koefisien mortalitas anatomis serta penentuan daya intersepsi alami.                                                                                    |
| Harga beli (ops.) | $p_{\text{duck\_buy\_manual}}$ | Rp/ekor  | Koreksi instrumen moneter      | Mengakomodasi disparitas harga fluktuatif di luar rezim pasar standar (_override input_).                                                                                |

---

## 4. Mesin Komputasi Matematis

### 4.1 Age Engine (Integrasi Kerentanan Usia)

$$\text{[system-design]} \quad R_{\text{age}} = \begin{cases} 0,35, & \text{jika } U_{\text{duck}} < 14 \\ 0,15, & \text{jika } 14 \le U_{\text{duck}} \le 29 \\ 0,05, & \text{jika } U_{\text{duck}} \ge 30 \end{cases}$$

**Penjelasan Matematis:** Kompartemen ini mengevaluasi kerugian efisiensi (_efficiency drag_) berbasis usia ontogeni ternak. Berlandaskan evaluasi lapangan kualitatif (_boundary validation_) yang divalidasi eksplisit oleh narasumber mitra lapangan, ekuilibrium daya tahan ternak tercapai pada umur 30 hari. Populasi yang terlampau muda ($< 14$ hari) memiliki kapabilitas anatomis yang sangat rentan sehingga dibebani penalti mekanis ekstrim ($0,35$). Umur 14-29 hari diklasifikasi sebagai fase maturasi moderat ($0,15$). Usia $\ge 30$ hari dinilai telah beradaptasi utuh sehingga beroperasi dengan gesekan penalti minimum ($0,05$).

### 4.2 Density Engine (Friksi Spasial)

$$\text{[local-calculated]} \quad d = \frac{J}{A_{\text{are}}}$$

$$\text{[local-estimate]} \quad K_{\text{safe}} = \begin{cases} 4, & \text{untuk Jarwo} \\ 3, & \text{untuk Tegel} \end{cases}$$

**Penjelasan Matematis:** Arsitektur spasial Jajar Legowo terbukti melebarkan ruang jelajah (mobilitas inter-baris), memberikan kapasitas tampung ekologis hingga 4 ekor/are sebelum memicu kerusakan vegetatif. Model Tegel, dengan geometri grid yang rapat, menekan asimtot ruang aman pada 3 ekor/are. Kedua ambang ini murni bersumber dari kesaksian dan validasi pakar mitra lapangan — narasumber secara eksplisit mengonfirmasi bahwa geometri Jajar Legowo memberi ruang gerak dan akses cahaya lebih baik, sementara geometri Tegel yang lebih sempit berisiko diinjak ketika populasi bebek memasuki fase tubuh besar pada saat tanaman masih berumur anakan.

$$\text{[system-design]} \quad P_{\text{over}} = \max\left(0, \min\left(1, \frac{d - K_{\text{safe}}}{8 - K_{\text{safe}}}\right)\right)$$

$$\text{[system-design]} \quad P_{\text{under}} = \max\left(0, \frac{2 - d}{2}\right)$$

**Penjelasan Matematis:** Friksi direpresentasikan secara _piecewise progresif_. Fungsi konvergen mencapai destruksi total manakala kongesti menembus batas saturasi atas (8 ekor/are). Sebaliknya, koefisien $P_{\text{under}}$ merespons ruang kosong akibat kepadatan defisit, mengeskalasi tingkat inefisiensi kegagalan pemangsaan alami. Pola non-linear naik-lalu-menurun akibat kepadatan berlebih ini juga konsisten secara kualitatif dengan pola realisasi panen pada gradien kepadatan bebek yang dilaporkan literatur referensi (Azizi et al., 2023).

### 4.3 Calendar Engine (Kronologi Masa Simbiosis)

$$\text{[local-estimate]} \quad t_{\text{active}} = 65 - 21 = 44 \text{ hari}$$

$$\text{[local-calculated]} \quad D_{\text{panen\_gabah}} = D_{\text{tanam}} + HST_{\text{panen}}$$

**Penjelasan Matematis:** Siklus kehadiran ternak dikonstruksi secara deterministik ke dalam interval absolut selama 44 hari (dari inisiasi masuk pada usia kritis 21 HST hingga ambang penarikan mutlak 65 HST). Ambang penarikan 65 HST diperlakukan sebagai konstanta kalender mutlak, bersumber dari kesepakatan _tacit_ teknisi (_undocumented expert field consensus_) hasil diskusi langsung dengan pakar mitra lapangan, dan beroperasi dominan memveto ketidakselarasan durasi kualitatif lain demi meredam distorsi fluktuasi rekam sekunder.

### 4.4 Survival Engine (Retensi Populasi)

$$\text{[local-validated]} \quad \lambda_{\text{eff}} = 0,78125 \times (1 - 0,50 R_{\text{age}}) \times (1 - 0,45 P_{\text{over}})$$

**Penjelasan Matematis:** Vektor ekspektasi kehidupan dikunci batas puncaknya (_ceiling_) di $0,78125$ — median rasio kelangsungan hidup aktual (populasi terjual dibagi populasi awal diinjeksi) yang dihitung langsung dari rekapitulasi mentah lapangan, pasca eksklusi baris data anomali dan penerapan protokol _masking_ pada baris bernilai nol/kosong. _Ceiling_ empiris ini kemudian didepresiasi lebih lanjut oleh dua koefisien penalti multiplikatif ($0,50$ untuk stres ontogeni dan $0,45$ untuk asfiksiasi kerumunan) yang bekerja simultan, menghasilkan median $\lambda_{\text{eff}}$ populasi sebesar $0,7517$ setelah kedua faktor penalti diterapkan.

$$\text{[local-calculated]} \quad N_{\text{survive}} = \lfloor J \times \lambda_{\text{eff}} \rfloor$$

**Catatan metodologis:** $N_{\text{survive}}$ diasumsikan setara dengan volume unggas yang tercatat terjual pada akhir siklus (bebek yang bertahan hidup dianggap terealisasi sebagai penjualan), konsisten dengan keputusan metodologis bahwa realisasi penjualan merupakan proksi terbaik yang tersedia untuk populasi tersintas pada granularitas data yang ada.

### 4.5 Yield Engine (Koreksi Biomasa Padi)

$$\text{[system-design]} \quad F_{\text{density\_bio}}(d) = 1 + \alpha_{\text{bio}} \left( 1 - \exp\left(-\frac{d}{K_{\text{opt}}}\right) \right) - \beta_{\text{tramp}} \left( \max\left(0, \frac{d - K_{\text{max}}}{K_{\text{max}}}\right) \right)^2$$

**Penjelasan Matematis:** Kurva respons kepadatan diformulasikan sebagai fungsi polinomial agronomis berbasis saturasi eksponensial yang menangkap insentif kesuburan biologis (_agronomic boost_) dari kotoran NPK dan bioturbasi pengadukan lumpur oleh bebek. Struktur saturasi asimtotik $\left(1 - \exp(-d / K_{\text{opt}})\right)$ mengontrol batas penyerapan fisiologis hara tanah seiring bertambahnya populasi ternak, mencegah anomali pertumbuhan linier tanpa batas sesuai prinsip biologi agronomis. Koefisien insentif maksimal $\alpha_{\text{bio}} = 0,15$ ($+15\%$) berjangkar pada sintesis literatur ilmiah mengenai rasio peningkatan hasil panen komoditas terintegrasi terhadap monokultur (Xiong et al., 2014; Azizi et al., 2023). Parameter $K_{\text{opt}} = 4 \text{ ekor/are}$ merepresentasikan kepadatan optimal lokal sesuai batas atas acuan disarankan berdasarkan konsolidasi observasi mitra lapangan. Efek destruksi mekanis masif (_trampling effect_) dikontrol oleh koefisien $\beta_{\text{tramp}} = 0,25$ (Azizi et al., 2023) yang diformulasikan secara kuadratik progresif dan mulai aktif mengurangi hasil panen manakala kepadatan melampaui batas saturasi atas daya dukung sistem Jajar Legowo ($K_{\text{max}} = 8 \text{ ekor/are}$, sesuai acuan observasi lapangan yang dicatat mitra).

$$\text{[system-design]} \quad F_{\text{age}} = 1 - 0,08 R_{\text{age}}$$

Gesekan minor akibat ternak belum stabil meredam laju fotosintetik dalam deviasi maksimum 8% ($0,08$), berjangkar pada basis kualitatif ontogeni usia ternak.

$$\text{[system-design]} \quad F_{\text{sys}} = \begin{cases} 1,00, & \text{untuk Jarwo} \\ 1,211, & \text{untuk Tegel} \end{cases}$$

**Penjelasan Matematis:** Rasio ini merepresentasikan diferensial produktivitas median empiris antar sistem tanam, terekstraksi langsung dari perbandingan median hasil aktual Tegel terhadap median hasil aktual Jarwo pada dataset siklus bersih. Sistem Tegel menunjukkan keunggulan produktivitas median empiris meski didukung volume observasi yang relatif terbatas; koefisien ini karenanya diklasifikasikan sebagai estimasi ahli yang dijangkarkan pada data (_data-anchored local estimate_), bukan derivasi dari koefisien numerik literatur eksternal, mengingat korpus literatur yang tersedia hanya menyediakan pembahasan kualitatif jarak tanam tanpa koefisien pengali hasil per sistem tanam yang eksplisit.

$$\text{[empirical-correction]} \quad F_{\text{var}} = 1,00$$

**Penjelasan Matematis:** Berdasarkan konsolidasi data operasional lapangan mitra, taksonomi varietas Sertani/Seratih dan Inpari beroperasi pada baseline produktivitas dasar yang setara secara massa ($Y_0 = 47,8767507 \text{ kg/are}$). Perbedaan antar varietas berimplikasi murni secara fenologis dan kronologis terhadap tenggat waktu pematangan komoditas ($HST_{\text{panen}}$) serta penjadwalan penarikan ternak dari lahan basah, tanpa adanya pemotongan produktivitas massa gabah dasar.

$$\text{[mixed]} \quad \text{Yield\_are} = Y_0 \times F_{\text{sys}} \times F_{\text{age}} \times F_{\text{density\_bio}}(d) \times F_{\text{var}}$$

### 4.6 Material Engine (Sirkulasi Pupuk Alam)

$$\text{[literature-uncalibrated]} \quad N_{\text{duck}} = \max(0, 0,02 t_{\text{active}} - 0,6) \times \kappa_N \times (J \times \lambda_{\text{eff}})$$

$$\text{[literature-uncalibrated]} \quad P_{\text{duck}} = \max(0, 0,02 t_{\text{active}} - 0,6) \times \kappa_P \times (J \times \lambda_{\text{eff}})$$

$$\text{[literature-uncalibrated]} \quad K_{\text{duck}} = \max(0, 0,02 t_{\text{active}} - 0,6) \times \kappa_K \times (J \times \lambda_{\text{eff}})$$

**Penjelasan Matematis:** Trajektori substitusi mineral feses diformulasikan linear (_slope_ $0,02$). Konstanta interupsi ruang ($-0,6$) diberlakukan ketat demi mengekang perhitungan ilusi deposit nitrogen harian, mengakui batas fisiologis bahwa pembusukan ekskresi membutuhkan inkubasi pasif ($\sim 30$ hari) agar nutrisinya terionisasi untuk serapan akar silika. Konstanta $\kappa_{N/P/K}$ terverifikasi presisi ke titik data numerik kandungan hara kumulatif per ekor pada ambang siklus referensi 80 hari (Xiong et al., 2014); namun studi rujukan tersebut tidak menyediakan fungsi akumulasi harian pada rentang sub-80-hari, sehingga fungsi linearisasi waktu (_slope_ dan intersep) tetap diklasifikasikan sebagai konstruksi internal (_literature-uncalibrated_) yang belum memiliki jejak sitasi kuantitatif langsung.

$$\text{[system-design]} \quad Q_{\text{urea}}, Q_{\text{phonska}}, Q_{\text{kcl}} = \text{least-cost nutrient mapping berbasis substitusi}$$

**Penjelasan Matematis:** Mesin substitusi _least-cost_ di atas beroperasi pada basis kandungan hara pupuk berikut. Pupuk Urea mengandung Nitrogen (N) minimum 46%, sesuai spesifikasi resmi produsen PT Petrokimia Gresik yang berlaku seragam untuk varian bersubsidi maupun non-subsidi (SNI 2801:2010; Petrokimia Gresik, 2024). Pupuk NPK Phonska bersubsidi saat ini mengandung N 15%, $\text{P}_2\text{O}_5$ 10%, $\text{K}_2\text{O}$ 12%, dan S 10% (SNI 2803:2012; Petrokimia Gresik, 2026), menggantikan formulasi terdahulu ($\text{N-P}_2\text{O}_5\text{-K}_2\text{O}$ 15-15-15) yang berlaku hingga awal 2021 (Bisnis.com, 2021). Kandungan oksida $\text{P}_2\text{O}_5$ dan $\text{K}_2\text{O}$ dikonversi ke basis unsur murni menggunakan faktor konversi agronomi standar ($\text{P}_2\text{O}_5 \to \text{P}$: x0,4364; $\text{K}_2\text{O} \to \text{K}$: x0,8301), menghasilkan konstanta elemental Phonska terkini $\text{P}=0,04364$ dan $\text{K}=0,09961$ yang tertanam pada mesin substitusi. Untuk komponen KCl, yang berada di luar skema pupuk bersubsidi resmi, digunakan spesifikasi kandungan pupuk KCl/MOP non-subsidi merek Mahkota ($\text{K}_2\text{O}$ minimum 60%; Gokomodo, 2024), menghasilkan konstanta elemental $\text{K}=0,49806$ pasca konversi oksida-ke-unsur yang identik.

$$\text{[literature-anchored]} \quad N_{\text{need}} = 1,1761; \quad P_{\text{need}} = 0,2745; \quad K_{\text{need}} = 0,2745 \quad \text{(satuan hara oksida per are)}$$

**Penjelasan Matematis:** Baseline kebutuhan hara per luasan ini merepresentasikan target substitusi bagi mesin _least-cost_ di atas. Nilai ini diturunkan dari rata-rata input pupuk aktual petani terintegrasi padi-bebek di Subak Lanyah, Kabupaten Tabanan, Bali -- 196 kg Urea/ha dan 183 kg Phonska/ha -- terverifikasi valid mengacu langsung pada data primer literatur referensi (Vipriyanti et al., 2021). Konversi ke basis are ($196 \text{ kg/ha} \times 0,01 = 1,96 \text{ kg Urea/are}$; $183 \text{ kg/ha} \times 0,01 = 1,83 \text{ kg Phonska/are}$), dikombinasikan dengan kandungan hara Urea (46% N) dan formulasi Phonska bersubsidi yang berlaku pada periode pengumpulan data lapangan artikel tersebut ($\text{N-P}_2\text{O}_5\text{-K}_2\text{O}$ 15-15-15, sebelum revisi formulasi 2021), menghasilkan: $N_{\text{need}} = (1,96 \times 0,46) + (1,83 \times 0,15) = 1,1761$; $P_{\text{need}} = 1,83 \times 0,15 = 0,2745$; $K_{\text{need}} = 1,83 \times 0,15 = 0,2745$ (seluruhnya basis oksida $\text{P}_2\text{O}_5/\text{K}_2\text{O}$, konsisten dengan satuan pelaporan input pupuk pada artikel sumber). Nilai-nilai ini secara metodologis independen dari revisi formulasi Phonska bersubsidi 2021, karena keduanya mengukur kebutuhan hara riil tanaman dalam satuan fisik unsur/oksida murni, bukan takaran produk komersial -- sehingga tetap valid sebagai target substitusi bagi mesin _least-cost_ yang beroperasi di atas basis kandungan hara Phonska terkini (15-10-12).

### 4.7 Cost Engine (Arus Kas dan Penghindaran Biaya)

$$\text{[local-estimate]} \quad C_{\text{duck\_buy}} = J \times p_{\text{duck\_buy}}$$

$$\text{[system-design]} \quad R_{\text{weed}}(d) = 0,93 \times (1 - \exp(-0,35 d))$$

**Penjelasan Matematis:** Intersep populasi gulma diatur konvergen eksponensial dengan pengereman asimtot $0,93$ ($93\%$). Angka ini disarikan dari kemampuan ekuilibrium hewan pada metrik kepadatan gulma (bukan biomassa) — perbandingan perlakuan berbasis bebek terhadap kontrol tanpa bebek dan tanpa herbisida menunjukkan penurunan kepadatan gulma sebesar 93,8% dan 92,0% pada dua metrik pengukuran independen (Du et al., 2025), dengan rata-rata dibulatkan menjadi $0,93$. Gradien percepatan $-0,35$ mendikte perapatan ke arah saturasi tersebut.

$$\text{[system-design]} \quad R_{\text{pest}}(d) = 0,80 \times (1 - \exp(-0,35 d))$$

**Penjelasan Matematis:** Valuasi pelindung infeksi patogen dikunci kuat pada langit saturasi $0,80$ ($80\%$). Formulasi mematuhi batas entomologi agrikultur bahwa intervensi predator non-terbang mustahil mengintervensi ekosistem hama 100%; basis primer klasifikasi ini adalah pernyataan kualitatif eksplisit mengenai penurunan signifikan populasi hama pada sistem terintegrasi bebek (Li et al., 2019), sehingga _ceiling_ numerik $0,80$ tetap diklasifikasikan sebagai estimasi desain sistem (_system-design_). Sebagai sitasi pendukung sekunder, studi terpisah yang secara kuantitatif melaporkan efektivitas kontrol populasi wereng batang hingga 98,47% dan wereng daun hingga 100% pada sistem padi-bebek (Long et al., 2013) turut memperkuat plausibilitas arah dan besaran mekanisme yang direpresentasikan fungsi ini, tanpa menggantikan basis kalibrasi _ceiling_ itu sendiri karena perbedaan cakupan taksonomi hama yang diukur.

---

#### Empirically Uncorrelated Isolated Components (Modul Cadangan / Sandbox)

$$\text{[local-estimate]} \quad \text{Cost\_labor\_weeding} = k_{\text{weed\_hire}} \times A_{\text{are}} \times (1 - R_{\text{weed}}(d))$$

$$\text{[local-estimate]} \quad \text{Cost\_pesticide} = C_{\text{pest\_base}} \times A_{\text{are}} \times (1 - R_{\text{pest}}(d))$$

$$\text{[local-estimate]} \quad \text{Cost\_infra\_net} = 0,5 \times 289.260 \times \sqrt{A_{\text{are}}}$$

**Penjelasan Matematis:** Modul ini merentangkan geometri luasan via fungsi akar kuadrat ($\sqrt{\cdot}$) ke batas dimensi tepi lahan. Konstanta $289.260$ adalah proksi rupiah ekuivalen material jaring per satuan akar-luas, diregresikan langsung (_least-squares_, melalui titik nol) terhadap observasi primer independen lintas petani yang telah melalui filtrasi data sintetis/default, dikurangi separuhnya ($0,5$) untuk mendesimulasikan depresiasi mekanis melewati umur pakai siklus ganda material jaring (2-3 siklus).

$$\text{[local-estimate]} \quad \text{Cost\_infra\_cage} = \text{Rp}175.000/\text{siklus (flat)}$$

**Penjelasan Matematis:** Berbeda dari komponen jaring, tidak ditemukan satu pun observasi primer independen untuk item kandang pada rekapitulasi mentah lapangan yang dapat digunakan sebagai basis regresi terhadap populasi ternak ($J$) — seluruh baris yang memuat item kandang terkonfirmasi sebagai nilai amortisasi seragam yang tidak berelasi dengan skala usaha masing-masing petani, sehingga dieksklusi dari basis kalkulasi. Nilai Rp175.000/siklus merupakan titik tengah (_midpoint_) dari rentang biaya amortisasi kandang yang dilaporkan eksplisit oleh narasumber mitra lapangan (Rp150.000–Rp200.000/siklus, berbasis harga beli unit dibagi masa pakai 3-4 siklus), diperlakukan sebagai biaya tetap per siklus karena data granular jumlah unit kandang per luasan/populasi tidak tersedia untuk mendukung skema proporsional tanpa asumsi tambahan.

$$\text{[system-design]} \quad C_{\text{infra}} = \text{Cost\_infra\_net} + \text{Cost\_infra\_cage}$$

**Penjelasan Matematis:** Struktur penjumlahan langsung ini menggantikan mekanisme _floor barrier_ pada formulasi terdahulu, karena nilai batas bawah tersebut, pada saat ditelusuri kembali ke sumber primernya, terbukti berasal dari agregat baris amortisasi seragam yang non-independen — sehingga kehilangan validitasnya sebagai representasi desil minimum data lapangan riil.

$$\text{[regulatory-locked / market-price]} \quad C_{\text{fert}} = Q_{\text{phonska}} \times 1.840 + Q_{\text{urea}} \times 1.800 + Q_{\text{kcl}} \times 9.500$$

**Penjelasan Matematis:** Harga Urea (Rp1.800/kg) dan NPK Phonska (Rp1.840/kg) bersifat _regulatory-locked_, merujuk langsung pada Harga Eceran Tertinggi (HET) pupuk bersubsidi yang berlaku (Kepmentan RI No. 1117/2025). Harga KCl (Rp9.500/kg) berada di luar skema subsidi pupuk resmi, sehingga diklasifikasikan sebagai _market-price reference_, merujuk pada harga pasar non-subsidi merek termurah yang tersedia di pasaran daring nasional.

$$\text{[local-estimate]} \quad C_{\text{feed}} = J \times 4.500 \times (1 + 0,75 P_{\text{over}} + 0,50 R_{\text{age}})$$

**Penjelasan Matematis:** Komponen biaya pakan tambahan diformulasikan penuh dan siap eksekusi (_plug-and-play_), mengikuti struktur pengali kepadatan ($P_{\text{over}}$) dan usia ($R_{\text{age}}$) yang identik dengan arsitektur komponen Cost Engine aktif lainnya. Konstanta basis Rp4.500/ekor/siklus merupakan median empiris observasi biaya pakan non-nol pada rekapitulasi mentah lapangan. Komponen ini diisolasi dari $\text{Cost\_total\_cash}$ inti karena narasumber mitra lapangan sendiri menegaskan bahwa praktik dan takaran pemberian pakan tambahan belum terstandardisasi secara konsisten antarpetani, sehingga penyertaannya pada kalkulasi kas inti berisiko menimbulkan distorsi sistematis; formula tetap difinalisasi penuh agar dapat diaktifkan kembali segera apabila standardisasi praktik pemberian pakan telah tercapai di masa depan.

---

## 5. Output Akhir Sistem

Tipologi output dirancang membelah dua kutub metrik. Desain asimetris ini mengeksekusi karantina terhadap komponen-komponen transaksi yang bersifat bayangan (_shadow parameters_) atau yang belum memenuhi standar konsistensi pencatatan lapangan, melindungi presisi arus kas berjalan.

### 5.1 Core Validated Output Group

| Kategori           | Output Komponen            | Rumus Ringkas                                                     | Makna Operasional                                                                                                                                                                                                                                |
| ------------------ | -------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Tunai Berjalan** | $\text{Revenue\_gabah}$    | $\text{Yield\_are} \times A_{\text{are}} \times p_{\text{gabah}}$ | Nilai tebusan absolut dari volume komoditas beras terselamatkan.                                                                                                                                                                                 |
| **Tunai Berjalan** | $\text{Revenue\_duck}$     | $N_{\text{survive}} \times p_{\text{duck\_sell}}$                 | Pencairan kapital atas biomasa populasi unggas sintas akhir musim.                                                                                                                                                                               |
| **Kumulasi Kas**   | $\text{Total\_Revenue}$    | $\text{Revenue\_gabah} + \text{Revenue\_duck}$                    | Volume total suntikan modal kotor dari komoditas ganda.                                                                                                                                                                                          |
| **Tunai Berjalan** | $\text{Cost\_duck\_buy}$   | $J \times p_{\text{duck\_buy}}$                                   | Akselerasi pencatatan resapan tunai pengadaan bibit aset hidup.                                                                                                                                                                                  |
| **Kumulasi Kas**   | $\text{Cost\_total\_cash}$ | $\text{Cost\_duck\_buy}$                                          | Konstruksi biaya berjalan riil (_Core Expenses_) berbasis verifikasi, murni terdiri dari pengadaan bibit unggas — komponen pakan diisolasi penuh ke modul cadangan (Bagian 5.2) mengingat volatilitas standar praktik pencatatannya di lapangan. |
| **Agregat Final**  | $\text{Profit\_net\_cash}$ | $\text{Total\_Revenue} - \text{Cost\_total\_cash}$                | Sisa likuiditas tunai nyata berdaya serap (_Pure Absorbed Profit_).                                                                                                                                                                              |

### 5.2 Empirically Uncorrelated Isolated Output Group

Kompartemen logistik berikut — _Weeding_, _Pesticide_, _Infrastructure_, _Fertilizer_, dan _Feed_ — diisolasi sempurna sebagai _Standalone Indicative Outputs_, terlepas secara fungsional dari hierarki $\text{Profit\_net\_cash}$. Kebijakan ini diberlakukan akibat asimetri pembukuan ekstrem (_zero-cash paradigm_) atau standar praktik pencatatan yang belum konsisten pada observasi primer. Evaluasi menunjukkan absennya transaksi moneter sewa asisten penyiangan pada mayoritas observasi, nihilnya pencatatan amortisasi material jaring/kandang secara terpisah dan seragam, eksistensi pembuatan pestisida botani tanpa taksiran finansial, margin perselisihan mencolok antara asumsi takaran hara teoretis dengan daya beli pupuk aktual, serta variasi ekstrem praktik dan takaran pemberian pakan tambahan antarpetani. Seluruh komponen pada kelompok ini tetap difinalisasi penuh rumus dan nilai _hardcode_-nya, sehingga senantiasa siap diaktifkan kembali ke dalam sirkuit kalkulasi utama tanpa memerlukan rekonstruksi ulang apabila standar pencatatan lapangan mencapai tingkat konsistensi yang memadai.

| Output Parameter                    | Matriks Substitusi            | Justifikasi Metodologi Isolasi (Scopus Q1 Standard)                                                                                                                                                                                                                                                                                                      |
| ----------------------------------- | ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| $\text{Cost\_weeding\_isolated}$    | $\text{Cost\_labor\_weeding}$ | Metrik tereduksi sekadar nilai bayangan (_shadow-price_). Verifikasi dataset memvalidasi penyiangan murni bertenaga internal keluarga pada mayoritas observasi; ketiadaan arus kas keluar nyata memaksa pembekuan agregasi metrik ini.                                                                                                                   |
| $\text{Cost\_pesticide\_isolated}$  | $\text{Cost\_pesticide}$      | Basis kalibrasi formula terpaku pada valuta agrokimia sintetis. Praktik empiris membantah dengan substitusi bio-pestisida mandiri tanpa jejak moneter terukur.                                                                                                                                                                                           |
| $\text{Cost\_infra\_isolated}$      | $C_{\text{infra}}$            | Komponen jaring telah dikalibrasi ulang berbasis regresi observasi primer independen; namun komponen kandang tetap merupakan estimasi amortisasi turunan wawancara (bukan observasi kas langsung), sehingga keseluruhan output infrastruktur tetap diperlakukan sebagai indikator _standalone_ hingga tersedia data granular unit fisik per skala usaha. |
| $\text{Cost\_fertilizer\_isolated}$ | $C_{\text{fert}}$             | Rekomendasi takaran pupuk berbasis ekstraksi teoretis referensi belum divalidasi uji laboratorium spektrometri tanah lokal, menghasilkan friksi volume yang lebar dibanding kebutuhan riil. Komponen KCl secara tambahan berada di luar skema harga regulasi resmi, sehingga rentan terhadap fluktuasi harga pasar bebas.                                |
| $\text{Cost\_feed\_isolated}$       | $C_{\text{feed}}$             | Praktik dan takaran pemberian pakan tambahan terbukti belum terstandardisasi secara konsisten antarpetani berdasarkan konfirmasi eksplisit narasumber mitra lapangan, sehingga penyertaannya pada agregasi kas inti berisiko menimbulkan distorsi sistematis pada evaluasi kelayakan finansial.                                                          |

---

## 6. Kamus Variabel Aktif Model

| Variabel                                            | Engine         | Definisi Leksikal                                               | Satuan    | Status Arsitektur Parameter                            |
| --------------------------------------------------- | -------------- | --------------------------------------------------------------- | --------- | ------------------------------------------------------ |
| $A_{\text{are}}$                                    | Input          | Eksposur luasan basah aktif                                     | are       | Terkalibrasi Lokal / Raw Input                         |
| $J$                                                 | Input          | Distribusi unit populasi fauna                                  | ekor      | Terkalibrasi Lokal / Raw Input                         |
| $S$                                                 | Input          | Arsitektur geometris komoditas                                  | kategori  | Estimasi Ekspertis Lokal                               |
| $V$                                                 | Input          | Taksonomi galur vegetatif                                       | kategori  | Estimasi Ekspertis Lokal                               |
| $U_{\text{duck}}$                                   | Input          | Waktu biologi inkubasi awal                                     | hari      | Estimasi Ekspertis Lokal                               |
| $R_{\text{age}}$                                    | Age            | Rasio fluktuasi transisi risiko                                 | rasio     | Sistem Komputasi Artifisial                            |
| $d$                                                 | Density        | Friksi populasi absolut per unit                                | ekor/are  | Derivatif Kalkulasi Lokal                              |
| $P_{\text{over}} / P_{\text{under}}$                | Density        | Simetri gaya tolak destruktif                                   | rasio     | Sistem Komputasi Artifisial                            |
| $\lambda_{\text{eff}}$                              | Survival       | Vektor ekspektasi kehidupan                                     | rasio     | Estimasi Ekspertis Lokal                               |
| $F_{\text{sys}}$                                    | Yield          | Diferensial sistem tanam                                        | rasio     | Estimasi Ekspertis Lokal (_Data-Anchored_)             |
| $F_{\text{density\_bio}}(d)$                        | Yield          | Kurva saturasi biologis & friksi injakan                        | rasio     | Hibrida Empiris Lokal & Literatur Scopus               |
| $K_{\text{opt}} / K_{\text{max}}$                   | Yield          | Ambang kepadatan optimal ($4$) & kapasitas maksimal ($8$)       | ekor/are  | Validasi Acuan Primer Lapangan                         |
| $\alpha_{\text{bio}} / \beta_{\text{tramp}}$        | Yield          | Koefisien insentif biomasa ($+15\%$) & penalti injakan ($0,25$) | koefisien | Teoretis Literatur Scopus (Xiong et al.; Azizi et al.) |
| $\text{Yield\_are}$                                 | Yield          | Produksi massa komoditi puncak                                  | kg/are    | Hibrida Empiris & Literatur                            |
| $N_{\text{duck}}, P_{\text{duck}}, K_{\text{duck}}$ | Material       | Substitusi bio-mineralisasi                                     | unit hara | Teoretis Literatur (_Uncalibrated_)                    |
| $C_{\text{duck\_buy}}$                              | Cost           | Translasi moneter logistik biomasa                              | Rp        | Validasi Primer Historis                               |
| $R_{\text{weed}}, R_{\text{pest}}$                  | Cost           | Kurva asimtot penetralan ancaman                                | rasio     | Sistem Komputasi Artifisial                            |
| $C_{\text{feed}}$                                   | Cost (Sandbox) | Translasi moneter belanja pakan tambahan                        | Rp        | Local-validated / Modul Cadangan (_Excluded_)          |

---

## 7. Batasan Model dan Prospeksi Masa Depan

Kondisi batas (_boundary limits_) memfokuskan mesin eksklusif pada ekuasi ekonomi diferensial mikro. Pembangunan vektor perluasan untuk penaksiran siklus Gas Efek Rumah Kaca ($\text{N}_2\text{O}/\text{CH}_4$) ditangguhkan menunggu injeksi parameter absorpsi dasar (Baseline $\text{CH}_4$) troposferik presisi tinggi dari stasiun riset independen. Komponen-komponen pada modul Sandbox (Bagian 5.2) tersedia penuh sebagai vektor reaktivasi cepat apabila konsistensi pencatatan lapangan untuk komponen-komponen tersebut mencapai standar yang memadai di masa depan.

---

## 8. Daftar Pustaka Metodologis dan Empiris

1. Xiong, D., Fang, K., Luo, Y., & Dai, X. (2014). Modeling of Duck Density and Complex Stocking Time in Rice-Duck Agroecosystems. _Mathematical Problems in Engineering_. DOI: 10.1155/2014/487537.
2. Li, M., Li, R., Zhang, J., Liu, S., Hei, Z., & Qiu, S. (2019). A combination of rice cultivar mixed-cropping and duck co-culture suppressed weeds and pests. _Basic and Applied Ecology_, 40, 67-77.
3. Du, C., Yang, D., Hu, L., et al. (2025). Feeding ducks in ratoon rice field reduces weed competition. _Field Crops Research_, 334, 110147.
4. Long, P., Huang, H., Liao, X., Fu, Z., Zheng, H., Chen, A., & Chen, C. (2013). Mechanism and capacities of reducing ecological cost through rice-duck cultivation. _Journal of the Science of Food and Agriculture_, 93(12), 2881-2891. DOI: 10.1002/jsfa.6223.
5. Azizi, M., Syamsuddin, S., & Basyah, B. (2023). Integration of Rice-Duck on Growth and Yield of Paddy Crops (_Oryza sativa_ L.). _IOP Conference Series: Earth and Environmental Science_, 1183, 012090. DOI: 10.1088/1755-1315/1183/1/012090.
6. Kementerian Pertanian Republik Indonesia. (2025). _Keputusan Menteri Pertanian RI Nomor 1117/Kpts./SR.310/M/10/2025 tentang Perubahan atas Keputusan Menteri Pertanian Nomor 800/KPTS./SR.310/M/09/2025 tentang Jenis, Harga Eceran Tertinggi dan Alokasi Pupuk Bersubsidi Sektor Pertanian Tahun Anggaran 2025_ (berlaku 22 Oktober 2025). Dari [https://www.pertanian.go.id/?show=news&act=view&id=7221](https://www.pertanian.go.id/?show=news&act=view&id=7221).
7. Gokomodo. (2024). _Referensi harga dan kandungan hara pupuk KCl non-subsidi ($\text{K}_2\text{O}$ 60%) pada platform distribusi agrikultur daring nasional, mencakup merek Mahkota, Mentari MOP, dan MOP Meroke_. Dari [https://gokomodo.com/blog/berapasih-harga-pupuk-kcl-50-kg-di-pasaran-mungkin-referensi-ini-bisa-membantu-kamu](https://gokomodo.com/blog/berapasih-harga-pupuk-kcl-50-kg-di-pasaran-mungkin-referensi-ini-bisa-membantu-kamu).
8. Astungkara Way Field Research Team. (2026). _Rekapitulasi Data Siklus Padi-Bebek: Dataset Historis Tervalidasi (2023-2026)_. Observasi dan Kuantifikasi Lapangan Primer.
9. Astungkara Way Field Research Team. (2026). _Konsolidasi Variabel Operasional Lapangan Padi-Bebek: Boundary Validation & Analisis Kualitatif_. Wawancara Ekstensif Lapangan.
10. Petrokimia Gresik. (2024). _Spesifikasi Produk Pupuk Urea: Kadar Nitrogen Minimal 46% (SNI 2801:2010), berlaku seragam untuk varian bersubsidi dan non-subsidi_. Dari [https://petrokimia-gresik.com/product/pupuk-urea](https://petrokimia-gresik.com/product/pupuk-urea).
11. Petrokimia Gresik. (2026). _Spesifikasi Produk Pupuk NPK Phonska Bersubsidi: N 15%, $\text{P}_2\text{O}_5$ 10%, $\text{K}_2\text{O}$ 12%, S 10% (SNI 2803:2012)_. Dari [https://petrokimia-gresik.com/product/phonska](https://petrokimia-gresik.com/product/phonska).
12. Bisnis.com. (2021). _Petrokimia Gresik Rilis Tiga Produk Pupuk Komersial: Penyesuaian Formula Unsur Hara P Pupuk NPK Phonska Bersubsidi dari NPK 15-15-15 Menjadi NPK 15-10-12_. Dari [https://ekonomi.bisnis.com/read/20210712/257/1416835/petrokimia-gresik-rilis-tiga-produk-pupuk-komersial](https://ekonomi.bisnis.com/read/20210712/257/1416835/petrokimia-gresik-rilis-tiga-produk-pupuk-komersial).
13. Vipriyanti, N. U., Lyulianti, S. P., Puspawati, D. A., Handayani, M. E., Tariningsih, D., & Malung, Y. U. (2021). The efficiency of duck rice integrated system for sustainable farming. _IOP Conference Series: Earth and Environmental Science_, 892, 012008. DOI: 10.1088/1755-1315/892/1/012008.
