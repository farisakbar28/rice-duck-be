# Manifest Evidence Riset — Model A

## Dataset test-only

| Item | Nilai |
|---|---|
| Source dataset | `DSS_Padi_Bebek_Rekap_Bersih_v10(1).xlsx` |
| Sheet | `Dataset Actual Bersih` |
| Row identity | `Excel Row (Sumber)` |
| Clean rows | 36 |
| Excluded rows | 8 |
| Repository treatment | Workbook tidak disalin ke Git; replay memakai transkripsi provenance input yang dapat diaudit di `docs/tes_skenario.md`. |

## Status evidence dan batas interpretasi

- `U_bebek=21` adalah input **imputed/estimated**, bukan observasi umur biologis mentah.
- `t_duck=45` adalah **imputed/estimated** dan tidak dikirim sebagai
  `literature_duration_days`.
- Durasi Xiong individual mentah untuk historical replay tidak tersedia.
- 33 dari 36 row berada dalam rentang density Xiong (`0 < density_ha <= 600`);
  3 dari 36 berada di luar rentang tersebut.
- Bukti durasi lokal 28–40 hari tidak overlap dengan domain Xiong 50–80 hari.
  Karena itu tidak ada numerical local yield Xiong pada historical suite.
- Historical actual yield adalah context/transferability evidence saja; tidak ada
  MAE atau RMSE production lokal yang diklaim untuk Xiong.
- Harga gabah sumber tersedia 36/36. `p_duck_buy=0` yang eksplisit dipertahankan
  sebagai input runtime nol; nilai yang benar-benar missing dihilangkan dari
  request agar fallback backend dapat dilihat pada provenance.
- `p_duck_sell=45000` adalah nilai skenario all-sold, bukan harga jual aktual
  sumber. Cash contribution tidak dibandingkan dengan raw farmer profit dan
  skenario all-sold tidak dibandingkan dengan `Duck Sale Revenue` historis.

## Reproduksibilitas runtime

`scripts/validate_model_a_runtime.py` menjalankan HTTP acceptance A01–A36,
S-A01–S-A19, calendar, dan authenticated v4 history terhadap Uvicorn pada
database SQLite terisolasi. Evidence mentah dicatat di
`docs/runtime_evidence_model_a.json`, termasuk branch, exact tested HEAD,
status clean worktree saat server mulai, timestamp, URL, nonce, database hash
sebelum/sesudah, serta raw request/response (credential disunting).
