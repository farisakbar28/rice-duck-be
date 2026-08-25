# tests/legacy_invalid — NON-R2 audit copies

Files in this directory are **historical copies** of the pre-R2 test suite
(current-master generation). They are preserved verbatim as research/audit
evidence and are intentionally NOT collected by pytest (filenames do not
start with `test_`).

They assert semantics that are **invalidated for R2** by:

- `docs/07_R2_LEGACY_INVALIDATION_REGISTER.md` (banned formulas, constants,
  canonical aggregates, provenance labels), and
- `docs/01_R2_MODEL_SSOT.md` / `docs/03_R2_API_CONTRACT.md`.

Examples of locked-in invalid semantics: mandatory `p_duck_buy` with `0`
meaning "no purchase", fixed yield `47.8767507`, Inpari 109–116,
HST 21/65/44 point calendar, `N_survive=J` / `floor(0.60*J)` survival,
duck sale revenue at 52500, feed cost `J*20000`,
`Net_Cash_Contribution_DSS` as canonical output, historical MAE constants.

Disposition per Phase 1 of the R2 migration (`docs/08_R2_IMPLEMENTATION_CHECKLIST.md`
Phase 8): these modules are quarantined, not rewritten. Their reusable shapes
(HTTP error envelope checks, round-trip/delete flows, non-finite rejection)
must be re-derived against R2 contracts in later phases. Do not run them, do
not "fix" their expected numbers, and never import them from production code.
