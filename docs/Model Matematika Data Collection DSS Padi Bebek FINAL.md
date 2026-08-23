# Decision-Support Net Cash Contribution Engine untuk Agroekosistem Padi-Bebek

> **Status:** Source of Truth (SoT) model matematika backend DSS Padi-Bebek  
> **Tanggal SoT:** 22 Agustus 2026  
> Dokumen ini adalah acuan implementasi production backend. Jika implementasi, test, README, Postman, schema, visualization, persistence, atau dokumentasi lain bertentangan dengan dokumen ini, komponen tersebut harus disesuaikan dengan SoT ini.

---

## 1. Tujuan dan Ruang Lingkup

DSS Padi-Bebek adalah model deterministik untuk:

1. mengklasifikasikan kesiapan umur bebek;
2. menghitung kepadatan bebek dan statusnya terhadap batas operasional lokal;
3. menghasilkan kalender masuk, keluar, dan panen berbasis tanggal tanam;
4. mengestimasi jumlah bebek yang tersedia pada akhir integrasi;
5. mengestimasi hasil gabah menggunakan baseline empiris lokal;
6. menghitung nilai gabah dan potensi nilai bebek;
7. menghitung biaya inti pembelian bebek dan pakan; dan
8. menghasilkan `Net_Cash_Contribution_DSS`.

`Net_Cash_Contribution_DSS` adalah **estimasi kontribusi kas parsial**, bukan laba bersih akuntansi, bukan realized historical profit, dan bukan ukuran menyeluruh seluruh biaya usahatani.

Komponen penyiangan, pestisida, pupuk/material, dan infrastruktur berada pada **Research/Sandbox** dan tidak masuk ke kalkulasi Core.

---

## 2. Hierarki Keputusan dan Evidensi

Urutan resolusi konflik informasi lokal:

```text
Expert judgement terbaru
> diskusi lanjutan
> wawancara/data collection awal
```

Data rekap mentah dan dataset bersih digunakan untuk parameter yang dapat dihitung langsung. Literatur peer-reviewed digunakan sebagai supporting evidence, pembatas domain, dan penjelasan mekanisme. Koefisien numerik dari konteks non-Bali tidak boleh dipindahkan langsung menjadi koefisien production lokal tanpa dasar kalibrasi lokal yang memadai.

Prioritas literatur:

```text
Bali > Indonesia > ASEAN > Asia > Global
```

Artikel setelah 2020 diprioritaskan bila tersedia dan relevan. Sumber lebih lama dapat digunakan bila memberikan mekanisme atau formulasi yang tidak tersedia pada sumber lebih baru.

---

## 3. Kontrak Input Production

Production model mempunyai **7 input wajib**.

| Konsep | Field API yang dipertahankan | Aturan |
|---|---|---|
| Luas lahan aktif | `land_area_are` | Wajib; `> 0` are |
| Populasi awal bebek | `duck_count` | Wajib; integer `> 0` |
| Varietas padi | `rice_variety` | Wajib; `sertani` atau `inpari` dengan `inpari` bermakna **generic Inpari** |
| Sistem tanam | `planting_system` | Wajib; `jajar_legowo` atau `tegel`. Nilai `jajar_legowo` pada production model **hanya berarti Jajar Legowo 2:1** |
| Umur bebek | `duck_age_days` | Wajib; dipakai untuk Age Readiness |
| Tanggal tanam | `planting_date` | Wajib; tanggal kalender |
| Harga beli bebek | `p_duck_buy` | Wajib; `>= 0` Rp/ekor |

### 3.1 Parameter backend production, bukan input pengguna

```text
p_gabah     = 6000       # Rp/kg
p_duck_sell = 52500      # Rp/ekor
c_feed      = 20000      # Rp/ekor/siklus
```

`p_duck_buy = 25000` **bukan fallback production**. Rp25.000 hanya reference lokal historis. Backend harus memakai nilai `p_duck_buy` yang dikirim pengguna. Nilai `0` sah bila pada siklus tersebut memang tidak ada current-cycle cash purchase.

---

## 4. Age Readiness Engine

```text
AgeFlag(U_duck) =
    TOO_YOUNG               jika U_duck < 21
    RECOMMENDED             jika 21 <= U_duck <= 30
    ABOVE_RECOMMENDED_AGE   jika U_duck > 30
```

Age Readiness hanya menghasilkan informasi kesiapan/warning.

### Larangan production

Production model tidak boleh menggunakan:

- `R_age = 0.35 / 0.15 / 0.05`;
- `F_age`;
- multiplier/penalty yield berdasarkan umur;
- multiplier/penalty survival berdasarkan umur;
- multiplier feed berdasarkan umur.

---

## 5. Density Engine

```text
d    = duck_count / land_area_are       # ekor/are
d_ha = 100 * d                          # ekor/ha
```

### 5.1 Status kepadatan

```text
d < 2
    -> UNDER_DENSITY

planting_system = jajar_legowo  # semantik: Jajar Legowo 2:1
dan 2 <= d <= 4
    -> RECOMMENDED

planting_system = tegel
dan 2 <= d <= 3
    -> RECOMMENDED

di atas ceiling sistem tetapi d <= 8
    -> ABOVE_RECOMMENDED

d > 8
    -> OVERLOAD_HIGH_RISK
```

Batas `> 8 ekor/are` adalah operational high-risk boundary lokal, bukan universal biological threshold.

Density tidak memberi bonus atau penalti numerik terhadap Yield Engine production. Kompleksitas hubungan density-yield tetap menjadi limitation model. Pada `d > 8`, efek numerik production hanya diterapkan pada Survival Engine.

---

## 6. Calendar Engine

Umur bebek (`duck_age_days`) dan umur tanaman/HST adalah variabel berbeda.

```text
HST_in   = 21
HST_out  = 65
t_active = 65 - 21 = 44 hari
```

Karena `planting_date` wajib:

```text
D_in  = planting_date + 21 hari
D_out = planting_date + 65 hari
```

### 6.1 Panen

Sertani:

```text
HST_panen_min = 100
HST_panen_max = 110

D_panen_min = planting_date + 100 hari
D_panen_max = planting_date + 110 hari
```

Inpari:

```text
HST_panen_min = 109
HST_panen_max = 116

D_panen_min = planting_date + 109 hari
D_panen_max = planting_date + 116 hari
```

Rentang 109–116 HST berasal dari tiga observasi lokal yang memiliki tanggal tanam dan panen langsung (109, 112, dan 116 HST; median deskriptif 112 HST). Karena jumlah observasi masih terbatas dan mencakup kategori Inpari umum serta Inpari 32, rentang ini diperlakukan sebagai **reference window empiris lokal**, bukan klaim fenologis universal seluruh subvarietas Inpari.

Production model tidak boleh membuat `planting_date` fallback, current-date fallback, midpoint tanggal, atau tanggal sintetik.

---

## 7. Survival Engine

```text
N_survive =
    duck_count                       jika d <= 8
    floor(0.60 * duck_count)         jika d > 8
```

Untuk `d <= 8`, model tidak menerapkan mortalitas baseline.

Hal tersebut adalah **modeling assumption**, bukan klaim bahwa mortalitas biologis aktual pasti nol. Penyakit, predator, cuaca, kualitas pemeliharaan, dan faktor husbandry lain berada di luar scope model.

Untuk estimasi ekonomi DSS:

```text
N_sold_DSS := N_survive
```

`N_sold_DSS` adalah jumlah bebek yang diasumsikan tersedia untuk dijual dalam estimasi DSS. Jangan membuat `r_sale`, sell-through ratio, atau rasio penjualan historis pada production model.

---

## 8. Yield Engine

Baseline empiris lokal:

```text
Y_base = 47.8767507 kg/are
```

Production:

```text
F_sys_JARWO_2_1 = 1
F_sys_TEGEL      = 1

F_var_SERTANI       = 1
F_var_INPARI_GENERIC = 1

Yield_are_pred   = 47.8767507
Yield_total_pred = Yield_are_pred * land_area_are
```

### Semantik penting

- Sistem tanam tidak diberi multiplier yield numerik.
- Varietas tidak diberi multiplier yield numerik.
- Umur bebek tidak diberi multiplier yield numerik.
- Density tidak diberi multiplier yield numerik.
- `d > 8` tetap menghasilkan yield baseline; kondisi overload dilaporkan melalui `OVERLOAD_HIGH_RISK`, sedangkan pengaruh numeriknya berada pada Survival Engine.
- Keputusan ini tidak berarti faktor-faktor tersebut tidak memiliki efek agronomis. Artinya coefficient lokal yang stabil belum cukup kuat untuk meningkatkan empirical local prediction bila dipaksakan ke production Yield Engine.

---

## 9. Core Economic Engine

```text
Revenue_gabah =
    Yield_total_pred * 6000

Revenue_duck_potential =
    N_survive * 52500

Cost_duck_buy =
    duck_count * p_duck_buy

Cost_feed =
    duck_count * 20000

Core_Cash_Cost =
    Cost_duck_buy + Cost_feed

Total_Revenue_DSS =
    Revenue_gabah + Revenue_duck_potential

Net_Cash_Contribution_DSS =
    Total_Revenue_DSS - Core_Cash_Cost
```

### Semantik `p_duck_buy = 0`

Jika pengguna mengirim:

```text
p_duck_buy = 0
```

maka:

```text
Cost_duck_buy = 0
```

Ini sah hanya sebagai representasi **tidak adanya current-cycle cash purchase**. Model tidak otomatis memasukkan opportunity cost aset bebek existing.

### Interpretasi final output

`Net_Cash_Contribution_DSS` tidak boleh dilabeli:

- accounting net profit;
- realized farmer profit;
- pure incremental profit.

---

## 10. Research / Sandbox

Sandbox tidak masuk `Net_Cash_Contribution_DSS`.

### 10.1 Weeding

```text
k_weeding = 21000 Rp/are/kegiatan
R_weeding = 0.77

Weeding_residual_per_are_event =
    21000 * (1 - 0.77)
    = 4830

Weeding_avoided_per_are_event =
    21000 - 4830
    = 16170
```

Tidak boleh dikalikan frekuensi per siklus tanpa parameter frekuensi yang telah dikalibrasi.

### 10.2 Pesticide

```text
Pesticide_reduction_upper_bound = 0.80
```

Nilai 80% hanya indikator upper bound nonmoneter. Jangan memasukkannya sebagai penghematan rupiah Core.

### 10.3 Fertilizer / Material

Mekanisme substitusi hara boleh tetap didokumentasikan sebagai Research/Sandbox, tetapi magnitude penghematan production belum dikalibrasi lokal secara memadai. Jangan memasukkan fertilizer saving ke Core.

### 10.4 Infrastructure

Infrastructure hanya context/reference. Tidak ada production cost formula.

---

## 11. Canonical Output Semantics

Backend harus menyediakan informasi semantik berikut, walaupun struktur nesting/casing final dapat disesuaikan dengan schema repository selama tidak mengubah makna.

| Output | Makna |
|---|---|
| `AgeFlag` | `TOO_YOUNG`, `RECOMMENDED`, atau `ABOVE_RECOMMENDED_AGE` |
| `density_are` | `duck_count / land_area_are` |
| `density_ha` | `100 * density_are` |
| `DensityStatus` | `UNDER_DENSITY`, `RECOMMENDED`, `ABOVE_RECOMMENDED`, atau `OVERLOAD_HIGH_RISK` |
| `HST_in` | 21 |
| `HST_out` | 65 |
| `t_active` | 44 |
| `D_in` | `planting_date + 21` |
| `D_out` | `planting_date + 65` |
| `harvest_hst` | Sertani 100–110; Inpari 109–116 |
| `harvest_date` | Diturunkan dari `planting_date` |
| `N_survive` | Survival Engine |
| `Yield_are_pred` | 47.8767507 kg/are |
| `Yield_total_pred` | `Yield_are_pred * land_area_are` |
| `Revenue_gabah` | Estimasi nilai gabah |
| `Revenue_duck_potential` | Potensi nilai bebek |
| `Cost_duck_buy` | Current-cycle cash purchase cost |
| `Cost_feed` | Simplified feed cost |
| `Core_Cash_Cost` | `Cost_duck_buy + Cost_feed` |
| `Total_Revenue_DSS` | `Revenue_gabah + Revenue_duck_potential` |
| `Net_Cash_Contribution_DSS` | Final core output |

### 11.1 Warning minimum yang harus direpresentasikan secara semantik

- `U_duck < 21`: terlalu muda / di bawah rentang readiness.
- `U_duck > 30`: di atas rentang umur yang direkomendasikan.
- `d > 8`: overload/high-risk.
- survival normal: estimation mengasumsikan pemeliharaan memadai; actual mortality dapat berbeda.

Nama literal warning string boleh mengikuti conventions repository, tetapi maknanya tidak boleh berubah.

---

## 12. Production Domain dan Validation Boundary

- Production menerima `land_area_are > 0`.
- Dataset kalibrasi/validasi lokal clean menggunakan `A_are >= 2.5`.
- Karena itu prediction untuk `0 < land_area_are < 2.5` berada di luar domain numerical validation lokal.
- `jajar_legowo` dalam production model hanya mewakili **Jajar Legowo 2:1**.
- Kategori Inpari masih menggabungkan observasi Inpari umum dan Inpari 32; window 109–116 HST karena itu merupakan reference lokal dengan dukungan sampel terbatas, bukan generalisasi seluruh subvarietas.
- Final economic output tidak memiliki historical endpoint yang semantik-identik dengan raw farmer profit.
- `N_sold_actual` tidak boleh dipakai sebagai biological ground truth untuk `N_survive`.

---

## 13. Legacy Semantics yang Dilarang pada Production Path

Semantics berikut tidak boleh lagi mengendalikan output production:

```text
R_age
F_age
lambda_eff = 0.78125
m_safe = 0.10
survival = floor(J * 0.90) untuk d <= 8
P_over / P_under sebagai multiplier yield
F_density_bio
alpha_bio
beta_tramp
F_sys != 1
yield baseline per-variety lama
Y_base_Sertani = 46.9363
Y_base_Inpari = 47.1970
p_duck_buy hardcoded/fallback 25000
planting_date optional
duck_age_days optional/default 21
generic Jarwo yang mencakup rasio selain 2:1
p_duck_sell = 35000
feed = 4500
Cost_feed_isolated
Profit_net_cash sebagai canonical final output
r_sale / sell-through ratio
numerical pesticide saving pada Core
fertilizer saving pada Core
infrastructure cost formula pada Core
```

Nilai atau nama legacy dapat tetap muncul pada historical persistence/migration layer bila diperlukan untuk membaca data lama, tetapi tidak boleh diinterpretasikan sebagai semantics production final.

---

## 14. Implementation Invariants

Implementasi final harus memenuhi seluruh invariants berikut:

1. Semua 7 input production wajib.
2. `p_duck_buy` menerima `0`; tidak ada fallback Rp25.000.
3. `jajar_legowo` hanya bermakna Jajar Legowo 2:1.
4. Age hanya menghasilkan readiness status/warning.
5. Density hanya menghasilkan metric/status dan menjadi input Survival Engine.
6. `d <= 8` menghasilkan `N_survive = J`.
7. `d > 8` menghasilkan `N_survive = floor(0.60J)`.
8. Yield selalu memakai baseline `47.8767507 kg/are`.
9. `planting_date` wajib dan seluruh tanggal kalender diturunkan darinya.
10. Sertani memakai 100–110 HST; Inpari memakai local empirical window 109–116 HST.
11. Feed adalah Core `J * 20000`.
12. Harga jual bebek production adalah Rp52.500/ekor.
13. Final output canonical adalah `Net_Cash_Contribution_DSS`.
14. Sandbox tidak boleh mengubah Core.
15. Test, visualization, history, README, Postman, dan API schema tidak boleh menghidupkan kembali semantics legacy.

---

## 15. Referensi Evidensi Utama

### Internal

- Rekapitulasi observasi primer siklus padi-bebek mitra penelitian di Bali.
- Dataset lokal bersih yang memenuhi kriteria cleaning.
- Wawancara/data collection awal.
- Diskusi lanjutan dan klarifikasi operasional.
- Konsolidasi expert judgement dan boundary validation.
- Korpus ekstraksi variabel, rumus, dan data dari 88 artikel.

### Eksternal

- Alfiansyah, M. L., Rahardja, D. P., & Padjung, R. (2025). *Advantages of introducing maggot-fed ducks into a rice plantation with and without Azolla*. Journal of Water and Land Development, 67, 61–72. https://doi.org/10.24425/jwld.2025.156040.
- Azizi, M., Syamsuddin, S., & Basyah, B. (2023). *Integration of rice-duck on growth and yield of paddy crops (Oryza sativa L.)*. IOP Conference Series: Earth and Environmental Science, 1183, 012090. https://doi.org/10.1088/1755-1315/1183/1/012090.
- Batubara, S. F., & Musfal. (2023). *Study of rice varieties, fertilizer application, and planting system on rice production in irrigated rice*. IOP Conference Series: Earth and Environmental Science, 1246, 012013. https://doi.org/10.1088/1755-1315/1246/1/012013.
- Beding, P. A., Palobo, F., Tiro, B. M. W., Lewaherilla, N. E., & Soplanit, A. (2023). *Rice growth response and yield to different planting systems in Merauke Regency, South Papua*. IOP Conference Series: Earth and Environmental Science, 1287, 012011. https://doi.org/10.1088/1755-1315/1287/1/012011.
- Endriani, Arief, R. W., Diptaningsari, D., Wardani, N., Soraya, & Asnawi, R. (2024). *Application of planting system and organic fertilizer on the yield of Inpari IR Nutri Zinc in Lampung*. IOP Conference Series: Earth and Environmental Science, 1338, 012014. https://doi.org/10.1088/1755-1315/1338/1/012014.
- Long, P., Huang, H., Liao, X., Fu, Z., Zheng, H., Chen, A., & Chen, C. (2013). *Mechanism and capacities of reducing ecological cost through rice-duck cultivation*. Journal of the Science of Food and Agriculture, 93(12), 2881–2891. https://doi.org/10.1002/jsfa.6223.
- Vipriyanti, N. U., Lyulianti, S. P., Puspawati, D. A., Handayani, M. E., Tariningsih, D., & Malung, Y. U. (2021). *The efficiency of duck rice integrated system for sustainable farming*. IOP Conference Series: Earth and Environmental Science, 892, 012008. https://doi.org/10.1088/1755-1315/892/1/012008.
- Xiong, D., Fang, K., Luo, Y., & Dai, X. (2014). *Modeling of duck density and complex stocking time in rice-duck agroecosystems in terms of economic and ecological benefits*. Mathematical Problems in Engineering, 2014, 487537. https://doi.org/10.1155/2014/487537.
