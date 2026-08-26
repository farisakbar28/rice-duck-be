# Phase 6D-R Corrected Publication-Facing Validation Report

> Status: `PHASE_6DR_CORRECTED_EMPIRICAL_VALIDATION_COMPLETE`
> This report separates a validation-harness provenance correction from the frozen R2 scientific model.

## Identity and immutability

- Current repository HEAD: `eda6a8035b89174e225999dec3aac0ec98685510`
- Scientific target SHA: `b10b0a1f83357c5db1d6cdfb9c41eaa84b6727a7`
- Original official Phase-6D run: `20260826T202953Z_b10b0a1`
- Original comparator harness blob SHA: `0eafa61e8ee5e6c62f41a12e86a1a8dadb035c21`
- Corrected validation harness working target: `eda6a8035b89174e225999dec3aac0ec98685510+WORKTREE:324203cf8f08de5c90137590fe26c2ea5927020be2fb6378575366baa7bd1d79`
- Protocol source blob SHA at the scientific target: `7c329403e8b6325760513b7f2f50e93c1d3259f9`
- MODEL_VERSION=`R2`; registry=`R2-2026-08-26.3`; scientific freeze=`R2-FREEZE-2026-08-26.5`.
- No `.6` freeze, `.4` registry, coefficient revision, recalibration, or model rerun was performed.
- Corrected metrics reuse the original frozen Phase-6 runtime predictions.

## Original-run root cause

- `validation/workbook_parser.py::_actual_provenance` assigns `DERIVED_ACTUAL` whenever the raw comparator cell content is a formula (`raw_formula` starts with `=`); `reconstruct_cohorts` applies that result to `actual_yield_kg_per_are`.
- In the original `validation/comparators.py::build_yield_comparator`, the actual value was retained only when `actual_provenance == OBSERVED_VALUE`; every derived actual was replaced with `None` before metric calculation.
- Result: the official source reconstruction was valid, but the yield/revenue comparator became non-evaluable at N=0 due to endpoint provenance-admissibility logic.

## Pre-existing protocol finding

- At the target protocol, clean cohort N=36 is stated in §§3 and 5.1; the component table in §12 states yield comparator availability 36/36; §6 and §22 prescribe yield comparison when executable.
- §4 explicitly includes `DERIVED_ACTUAL` in the comparator provenance vocabulary.
- Finding: the pre-existing protocol did not state that `DERIVED_ACTUAL` yield must be rejected. The original harness exclusion was not a protocol requirement.

## Raw yield formula and precedent audit

- Audited all 36 clean rows before calculating residuals; `metric_calculation_performed`=False; `residuals_used_for_adjudication`=False.
- Formula patterns:
  - `=AA{row}/H{row}`: N=35; class=ACTUAL_HARVESTED_GABAH_KG_DIVIDED_BY_PROGRAM_RICE_AREA_ARE; numerator=actual harvested gabah quantity, directly recorded in the raw workbook as 'Actual gabah yield (kg)'; denominator=active cultivated/program rice area, directly recorded as 'Rice field in program (Are)'; unit=kg / are -> kg/are; constant=None; pure deterministic measurement derivation=True.
  - `=$AA${row}/H{row}`: N=1; class=ACTUAL_HARVESTED_GABAH_KG_DIVIDED_BY_PROGRAM_RICE_AREA_ARE; numerator=actual harvested gabah quantity, directly recorded in the raw workbook as 'Actual gabah yield (kg)'; denominator=active cultivated/program rice area, directly recorded as 'Rice field in program (Are)'; unit=kg / are -> kg/are; constant=None; pure deterministic measurement derivation=True.
- Precedents for every row are recorded in `yield_actual_provenance_adjudication.json`; all formula precedents are direct numeric raw cells: `AA` actual gabah quantity and `H` program rice area. No formula-derived precedent, imputation, legacy model result, prediction, default, or unknown precedent was used.
- Area semantic: `H` is `Rice field in program (Are)`, mapped by the clean workbook to `A_are (Luas Program)` and compatible with R2 active cultivated/program rice interaction area. It is not total land and is not a separate unverified harvested-area construct.
- Harvest quantity semantic: `AA` is directly recorded `Actual gabah yield (kg)`, with separate sale-price and gabah-revenue fields. It is treated as actual harvested gabah quantity, not a sales quantity or legacy prediction.
- Basis limitation: the workbooks say gabah but do not identify GKP, GKG, or moisture percentage; the heterogeneity/unknown basis is disclosed and not silently harmonized.

## Yield admissibility decision

- A `DERIVED_ACTUAL` yield is eligible only when its formula deterministically transforms semantically compatible direct actual observations into kg/are: actual harvested quantity (kg) divided by active cultivated/program rice area (are), with no forbidden model/imputation/fallback semantics.
- Admissible derived-yield N=36; non-admissible N=0.
- Non-admissible yield reason counts: `{}`.
- Yield provenance distribution: `{'OBSERVED_VALUE': 0, 'EXPLICIT_ZERO': 0, 'MISSING_UNKNOWN': 0, 'DERIVED_ACTUAL': 36, 'LEGACY_IMPUTATION': 0}`. Provenance remains `DERIVED_ACTUAL`; admissibility is a separate boolean dimension.
- No row was excluded for residual size, envelope miss, MAPE, or model performance. Row inclusion was fully determined before metric calculation by source semantics and provenance.

## Endpoint-specific policy

- Purchase price strict comparator remains `OBSERVED_VALUE` and positive only; `DERIVED_ACTUAL` purchase price remains excluded.
- Yield comparator accepts `OBSERVED_VALUE` plus semantically verified/admissible `DERIVED_ACTUAL`; non-admissible derived, legacy imputation, missing/unknown, and unverified explicit zero are excluded.
- Paddy price follows the existing approved diagnostic rule: observed positive historical price is metadata for the price-neutral diagnostic only.

## Corrected yield comparator

- N_total_actual_eligible=36; N_predicted=22; prediction coverage=61.111111111111114% (0.6111111111111112).
- MAE=9.183970959818181 kg/are; RMSE=13.421718631571618 kg/are; MedAE=6.162351085000001 kg/are; MBE=2.606386759818184 kg/are; WAPE=20.68403714256823%; supplementary MAPE=46.662702734492015%; diagnostic R²=-0.05747750232820392.
- Evidence envelope: covered N=20; LITERATURE_EVIDENCE_ENVELOPE_COVERAGE=0.9090909090909091 (90.9090909090909%); mean width=47.60574545454545 kg/are; median width=45.6432 kg/are.
- Prediction status counts: scientific unavailable N=14; HTTP execution failure N=0.
- Cluster bootstrap: `{'status': 'EVALUATED', 'reason': None, 'cluster_unit': 'farmer_cluster_id', 'resamples': 2000, 'seed': 20260826, 'percentile': [0.025, 0.975], 'intervals': {'MAE': {'lower': 5.338547626190476, 'upper': 14.255541432705883}, 'RMSE': {'lower': 7.48075664347243, 'upper': 19.285367878437786}, 'MBE': {'lower': -2.391187468095236, 'upper': 8.891407133200001}, 'WAPE': {'lower': 11.282456480039396, 'upper': 36.907197894190645}, 'LITERATURE_EVIDENCE_ENVELOPE_COVERAGE': {'lower': 0.75, 'upper': 1.0}}}` (farmer_cluster_id, 2,000 resamples, seed 20260826, 2.5/97.5 percentile).

### Subgroups

- overall_numeric_prediction_cohort: N_actual_eligible=36; N_predicted=22; coverage=0.6111111111111112; policy=QUANTITATIVE; MAE=9.183970959818181; RMSE=13.421718631571618; WAPE=20.68403714256823; R²=-0.05747750232820392
- strict_supported_domain: N_actual_eligible=17; N_predicted=17; coverage=1.0; policy=QUANTITATIVE; MAE=9.855426004470589; RMSE=14.436931455685956; WAPE=23.478704172402782; R²=-0.13347568973167578
- INPARI_GROUP: N_actual_eligible=5; N_predicted=3; coverage=0.6; policy=QUANTITATIVE; MAE=8.309602693333334; RMSE=10.467747785900904; WAPE=17.60201414199902; R²=-1.2410685761425695
- SERTANI_GROUP: N_actual_eligible=31; N_predicted=19; coverage=0.6129032258064516; policy=QUANTITATIVE; MAE=9.322029107157894; RMSE=13.83058101193071; WAPE=21.206653635894305; R²=-0.016996305821770585; note=LOW_EVIDENCE_TWO_LOCATION_EXTERNAL_RANGE
- Jajar Legowo: N_actual_eligible=32; N_predicted=20; coverage=0.625; policy=QUANTITATIVE; MAE=8.8949165408; RMSE=13.481510495508598; WAPE=19.96657912338301; R²=0.019256868141710348
- Tegel: N_actual_eligible=4; N_predicted=2; coverage=0.5; policy=COUNT_ONLY_SMALL_N; MAE=None; RMSE=None; WAPE=None; R²=None

## Revenue diagnostics

- CURRENT_HPP_OPERATIONAL_VALUE_DIAGNOSTIC: status=EVALUATED; N_total_actual_eligible=36; N_predicted=22; coverage=61.111111111111114%; MAE=311527.7986064933 Rp/cycle; RMSE=420128.394071854 Rp/cycle; MedAE=254786.2200136502 Rp/cycle; MBE=41782.65592655224 Rp/cycle; WAPE=16.576559236396317%; envelope coverage=0.9090909090909091.
- PRICE_NEUTRAL_HISTORICAL_PRICE_DIAGNOSTIC: status=EVALUATED; N_total_actual_eligible=36; N_predicted=22; coverage=61.111111111111114%; MAE=297042.3196077955 Rp/cycle; RMSE=400883.6711827306 Rp/cycle; MedAE=241702.28101260017 Rp/cycle; MBE=30976.365834068216 Rp/cycle; WAPE=15.987950881921265%; envelope coverage=0.9090909090909091.
- Current-HPP diagnostic uses the current regulatory HPP benchmark; price-neutral diagnostic uses observed historical paddy price as comparator metadata only. No profit metric is produced.

## Scientific diff and independent reproduction

- Scientific diff guard pass=True; changed paths=[]; scientific parameter/equation change=False.
- Independent yield/envelope/revenue reproduction: `PASS`; zero meaningful mismatch=True; tolerance={'relative': 1e-12, 'absolute': 1e-08}. Full check is in `independent_metric_reproduction.json`.

## Original-run preservation and QA

- Original run before/after file manifests identical=True; original artifacts remain byte-for-byte preserved.
- Purchase policy result: strict_N=27; derived_actual_context_N=2; no derived purchase price entered the strict comparator.
- No PII is present in correction artifacts; row identity is source row plus anonymous farmer cluster ID only.
- Required tests and compileall results are recorded in `qa_results.json`.

## Correction conclusion

- The original Phase-6D execution was official and targeted the correct frozen science, but its yield/revenue result was rendered non-evaluable by a validation-harness endpoint provenance-admissibility defect. It is not evidence that the model empirically failed at N=0.
- This correction changes validation semantics only; production science remains R2 / registry .3 / freeze .5.

`PHASE_6DR_CORRECTED_EMPIRICAL_VALIDATION_COMPLETE`
