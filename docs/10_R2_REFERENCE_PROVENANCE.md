# R2 Reference and Provenance Registry

> **Purpose:** prevent backend constants from losing their research provenance.  
> This is an implementation registry, not a substitute for the final academic reference list.

## 1. Internal Research Sources

| ID | Source | Role |
|---|---|---|
| `I1` | `data_collection_padi_bebek_FINAL.xlsx` | Primary local data collection for calendar, density, prices, infrastructure, local cost ranges. |
| `I2` | `Dokumentasi Expert DSS Padi-Bebek.docx` | Expert evidence for structural separation, safe-context survival, density boundaries, duck value, evidence transfer. |
| `I3` | `Model Matematika Data Collection DSS Padi Bebek.docx` | Domain-wide documentation/format/provenance reference. |
| `I4` | legacy economic model DOCX | Audit target; not R2 source of truth. |
| `I5` | `Kumpulan_Variabel_Rumus_Data_Artikel_Referensi_Scopus_FINAL.xlsx` | Curated literature fallback only. |
| `V1` | `Recap Data CRS Bebek.xlsx` | Raw historical comparator only. |
| `V2` | `DSS_Padi_Bebek_Rekap_Bersih_v10.xlsx` | Clean comparator cohort only. |
| `V3` | `Dataset Bersih Rekap Include Hasil Simulasi Baru.xlsx` | Legacy simulation audit only. |

## 2. External Scientific References

| ID | Citation / DOI | Year | Geography | R2 role | Scopus verification status |
|---|---|---:|---|---|---|
| `R1` | Vipriyanti, N.U. et al., *The efficiency of duck rice integrated system for sustainable farming*, DOI `10.1088/1755-1315/892/1/012008` | 2021 | Bali, Indonesia | Bali RDIS fertilizer/input baseline context | IOP EES series Scopus coverage verified during R2 audit |
| `R2` | Nallasamy, T. et al., *Rice-duck integrated system (RDIS) sustains organic rice production in India*, DOI `10.1007/s13165-025-00508-6` | 2025 | Tamil Nadu, India | design/mechanism reference only; supplementary evidence does not provide the complete transferable yield table required for executable F_RD | Organic Agriculture Scopus active during R2 audit |
| `R3` | Alfiansyah, L.M.; Rahardja, D.P.; Padjung, R., DOI `10.24425/jwld.2025.156040` | 2025 | South Sulawesi, Indonesia | feed intake/FCR/economic mechanism; not direct local effect-size calibration | direct Scopus publication record `105033853270` noted during audit |
| `R4` | Du, C. et al., DOI `10.1016/j.fcr.2025.110147` | 2025 | Central China | weed suppression biological evidence only | Field Crops Research Scopus coverage verified |
| `R5` | Qian, P. et al., DOI `10.1080/09583157.2022.2044016` | 2022 | Zhejiang, China | evidence that pest response is heterogeneous/not universally beneficial | journal Scopus indexing verified |
| `R6` | Zhou, Y. et al., DOI `10.3390/agriculture16111172` | 2026 | Jianghan Plain, China | external context for survival/management and state separation | Agriculture Scopus indexing verified |
| `R7` | Xiong, D. et al., DOI `10.1155/2014/487537` | 2014 | China | historical fallback/reference only | retained from internal Scopus reference workbook; non-executable by default |

## 3. Official / Regulatory Sources

| ID | Source | R2 parameter |
|---|---|---|
| `O1` | Instruksi Presiden No. 4 Tahun 2026 / Badan Pangan Nasional | `p_gabah_ref=6500 Rp/kg` HPP benchmark |
| `O2` | Kepmentan No.1117/Kpts./SR.310/M/10/2025 | HET Urea `1800 Rp/kg`; NPK `1840 Rp/kg` |
| `O3` | Official Urea producer specification | Urea N fraction `0.46` |
| `O4` | Official NPK Phonska registration/specification | NPK 15-10-12 (`N=0.15`, `P2O5=0.10`, `K2O=0.12`) |
| `O5` | 2021 official soil-research annual documentation | historical Phonska 15-15-15 context used only for reconstructing the 2021 Bali nutrient baseline |

## 4. Parameter Provenance Map

| Parameter | Value / state | Source IDs | Status |
|---|---|---|---|
| harvest Sertani/Seratih | 100–110 HST | I1 | `local-estimate` |
| harvest Inpari | 90–100 HST | I1 | `local-estimate` |
| release | 21–30 HST | I1 | `local-estimate` |
| pull/heading | 56–60 HST | I1 | `local-estimate` |
| active duration | ref 32, interval 28–40 | I1 | `local-estimate` |
| supported duck age | 21–30 days | I1 | `local-estimate` |
| Jarwo density | 2–4/are | I1/I2 | `local-estimate` |
| Tegel density | 2–3/are | I1/I2 | `local-estimate` |
| high-risk density | approx >=8/are | I2 | `local-estimate` |
| safe survival reference | 0.90 | I2 | `local-estimate` |
| duck buy range | 25k–28k | I1 | `local-estimate` |
| duck buy default | 26.5k | I1 + system midpoint | `mixed` |
| duck terminal ref | 45k; range 30–60k | I1/I2 | `local-estimate` |
| paddy benchmark | 6500/kg | O1 | `regulatory-locked` |
| N need | 1.1761 kg/are | R1/O3/O5 | `literature-uncalibrated` |
| P2O5 need | 0.2745 kg/are | R1/O5 | `literature-uncalibrated` |
| K2O need | 0.2745 kg/are | R1/O5 | `literature-uncalibrated` |
| Urea composition | 46% N | O3 | `regulatory-locked` |
| NPK composition | 15-10-12 | O4 | `regulatory-locked` |
| Urea HET | 1800/kg | O2 | `regulatory-locked` |
| NPK HET | 1840/kg | O2 | `regulatory-locked` |
| net price | 6000–6750/m | I1 | `local-estimate` |
| net lifetime | 2–3 cycles | I1 | `local-estimate` |
| cage per-unit amortization | 150–200k/cycle | I1 | `local-estimate` |
| weeding baseline | 6–38k/are | I1 | `local-estimate` |
| local cultivar grouping | `SERTANI_GROUP` / `INPARI_GROUP`, approved aliases only | V1/V2 label audit | `system-design` / structure ready; not genetic identity |
| Y_base local cultivar group | unresolved/null | future approved source | `literature-uncalibrated` / `PENDING_LOOKUP` |
| F_RD response | unresolved/null exact-node lookup | R2 design context + future approved evidence | `literature-uncalibrated` / `PENDING_LOOKUP` |
| feed cost | unresolved | I1/R3 candidate mechanism | `UNAVAILABLE` |
| KCl price | unresolved | none accepted | `UNAVAILABLE` |

## 5. Engineering Rule for Sources

Do not reduce provenance to a comment like `# local validated`.

Each versioned parameter should retain:

```text
source_id(s)
status_tag
execution_state
value/range
unit
effective date/version
note
```

Regulatory values must be replaceable/versioned without editing scientific formula code.

## 6. No Transplant Rule

A Scopus article can justify a mechanism without authorizing direct transplantation of its effect size to Bali.

Examples:

- South Sulawesi feed/density studies may support model structure but have densities far above Astungkara's 2–4/are domain.
- China weed/pest evidence does not create a universal Bali monetary saving coefficient.
- Xiong 2014 closed-form formulas do not authorize reuse of its survival definition or time response where local semantics differ.

Runtime values remain `literature-uncalibrated` until local calibration is legitimately possible or the research design explicitly accepts an uncalibrated literature lookup.

Nallasamy is non-executable design context under the current evidence package.
Vipriyanti supplies nutrient/input context only, and Alfiansyah supplies
feed/economic mechanism context only. `V1`, `V2`, and `V3` comparator
workbooks are never parameter sources; `V3` remains legacy-audit-only.
