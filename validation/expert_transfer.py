"""Expert-evidence transfer matrix (task §35; docs/06 section 18).

Each R2 parameter/formula receives exactly one label:
  DIRECT  -- exact concept/parameter was judged by the domain expert.
  PARTIAL -- same concept, mathematical form changed or only a boundary judged.
  NONE    -- the R2 formula was not expert-evaluated.

Rules encoded here:
  * The historical ~45.84 kg/are scenario plausibility is a historical
    snapshot; it is NOT transferred to R2 yield.
  * The expert's ~80% working confidence is NEVER converted into a
    statistical acceptance threshold.
  * There is no global "expert accuracy" score.
"""

EXPERT_TRANSFER_MATRIX: list[dict] = [
    {
        "parameter": "age_support (R2-AGE-01)",
        "transfer": "DIRECT",
        "evidence_reference": "I2 (expert documentation); docs/10 section 4",
        "scope": "support classification boundaries only (21-30 days)",
        "note": "Age is a classifier; no numeric age multiplier exists in R2.",
    },
    {
        "parameter": "density_supported_boundaries (R2-DEN-02)",
        "transfer": "DIRECT",
        "evidence_reference": "I1/I2",
        "scope": "Jarwo 2-4 and Tegel 2-3 duck/are support ranges",
        "note": "Boundary judgment transferred; metadata-only, never a penalty.",
    },
    {
        "parameter": "high_risk_density_threshold (~>=8/are)",
        "transfer": "PARTIAL",
        "evidence_reference": "I2",
        "scope": "approximate qualitative threshold, not an exact constant",
        "note": "Approximation acknowledged in registry note.",
    },
    {
        "parameter": "survival lambda_safe_ref=0.90 (R2-SURV-01)",
        "transfer": "PARTIAL",
        "evidence_reference": "I2 safe-context estimate",
        "scope": "value judged for safe context; availability gate is R2 design",
        "note": "Not a universal biological rate; conditional on SUPPORTED age+density.",
    },
    {
        "parameter": "N_survive != N_sold state separation (R2-SURV-03)",
        "transfer": "DIRECT",
        "evidence_reference": "I2",
        "scope": "biological state vs sales state separation",
        "note": "Sold ducks are never used as survival ground truth.",
    },
    {
        "parameter": "terminal duck reference price 45k [30k,60k] (R2-DUCKVAL-01)",
        "transfer": "PARTIAL",
        "evidence_reference": "I1/I2 local price evidence",
        "scope": "price level + sensitivity band; NOT a sale-revenue assumption",
        "note": "V_duck_end is livestock asset value, never realized cash revenue.",
    },
    {
        "parameter": "feed cost state (R2-FEED-01)",
        "transfer": "NONE",
        "evidence_reference": "-",
        "scope": "no expert numeric feed judgment encoded",
        "note": "Runtime stays UNAVAILABLE until sourced q_feed/p_feed lookups exist.",
    },
    {
        "parameter": "weed suppression effect (R2-WEED-01/02)",
        "transfer": "PARTIAL",
        "evidence_reference": "I2 qualitative acknowledgment",
        "scope": "concept-level suppression recognized; monetary conversion NONE",
        "note": "C_weeding_saved stays UNAVAILABLE; baseline range only.",
    },
    {
        "parameter": "pest effect (R2-PEST-01/02)",
        "transfer": "NONE",
        "evidence_reference": "-",
        "scope": "heterogeneous evidence; no universal scalar judged",
        "note": "CONTEXT_SPECIFIC descriptor only.",
    },
    {
        "parameter": "manure nutrient credit decision (R2-MANURE-01/R2-NUT-04)",
        "transfer": "PARTIAL",
        "evidence_reference": "I2 contribution concept; temporal linearization rejected",
        "scope": "decision: baseline-no-credit executable state",
        "note": "Not a claim of zero manure contribution.",
    },
    {
        "parameter": "yield lookup Y_base(V_exact)*F_RD_lookup (R2-YLD-01)",
        "transfer": "NONE",
        "evidence_reference": "-",
        "scope": "new formula not expert-reviewed",
        "note": (
            "Historical 45.84 kg/are scenario plausibility is a historical "
            "snapshot ONLY; it does not validate or parameterize R2 yield."
        ),
    },
    {
        "parameter": "economics semantics (ledger conditionality R2-LEDGER-*)",
        "transfer": "PARTIAL",
        "evidence_reference": "I2 state-separation review",
        "scope": "state separation reviewed; ledger algebra is system-design",
        "note": "Margin_core is never labeled net profit; full profit gated on COMPLETE.",
    },
]

GLOBAL_NOTES = [
    "Expert ~80% working confidence is not a statistical pass/fail threshold.",
    "No aggregate 'expert accuracy' score is defined anywhere in this harness.",
]
