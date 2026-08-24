# Research Evidence Manifest — Frozen Model C

## Dataset identity and split

- Clean source workbook: `DSS_Padi_Bebek_Rekap_Bersih_v10(1).xlsx`.
- Sheet: `Dataset Actual Bersih`.
- Source-row identity: `Excel Row (Sumber)`; it is the immutable join key for
  replay provenance, rather than farmer name.
- Clean dataset: 36 cycles from 19 farmers.
- Farmer-grouped calibration partition: 25 cycles from 13 farmers.
- Farmer-grouped holdout partition: 11 cycles from 6 farmers.
- There is no farmer overlap between calibration and holdout partitions.
- Exact holdout raw rows: 8, 9, 11, 14, 23, 25, 38, 43, 44, 47, and 62
  (respectively H01–H11).

## Frozen model and price provenance

- Production model is C0 only: `Y0_C` is the calibration median, 50 kg/are.
- `p_gabah` calibration median is Rp6,000/kg.
- Positive `p_duck_buy` calibration records: n=21; median Rp25,000/duck.
- Bootstrap interval `[42.81, 55.78]` describes parameter uncertainty only;
  it is not an individual-prediction interval.
- `duck_age_days=21` is an explicitly imputed/estimated required replay input.
- `DefaultJarwo` is an explicitly imputed clean-dataset planting-system value,
  not an observed raw system label.

## Holdout governance and source replay

- Holdout rows were not used for model selection. C1/C3/C4 are not selected,
  and Model C is not recalibrated after holdout opening.
- Holdout is now opened. It must not be described as untouched for any future
  model generation, selection, or tuning.
- Runtime replay uses source `p_gabah` and source `p_duck_buy` by exact raw
  row. A recorded zero purchase price remains an explicit runtime zero.
- Source planting date field: `Tanggal Tanam (Sumber)`. Only H07/raw row 38
  (`2024-04-22`), H08/raw row 43 (`2024-10-01`), and H09/raw row 44
  (`2024-09-28`) are sent in holdout HTTP requests. Missing source dates are
  omitted; no date is constructed.

The live evidence file is `docs/runtime_evidence_model_c.json`; the readable
audit is `docs/tes_skenario.md`.
