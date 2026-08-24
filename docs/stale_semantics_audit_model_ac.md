# A+C stale semantics audit

Checked active Python, docs, tests, Postman, and scripts for: `47.8767507`, `Y_BASE`, `N_survive`, `survival_rate`, `compute_surviving_ducks`, `0.60`, `52500`, `Cost_feed`, `Net_Cash_Contribution_DSS`, `HST_OUT`, `T_ACTIVE`, `109`, `116`, `FINAL_BANGET`, `Yield_are_pred`, `Revenue_duck_potential`, `average`, `weighted`, `ensemble`, `blend`, `w_A`, `w_C`, `alpha_bio`, `F_density_bio`, `F_sys`, `F_var`, `A_STRICT_SEPARATION`, and `C_FARMER_GROUPED_LOCAL`.

| Classification | Result |
| --- | --- |
| Active production path | No old yield, survival, feed, calendar, or fusion semantics remain. Production uses only `compute_primary_yield` and `compute_economics_from_primary`. |
| Historical documentation | Previous release notes retain historical terminology only. |
| Research provenance | Candidate C1/C3/C4 and Xiong source remain described in the SoT, never invoked as production modifiers. |
| Negative tests | `tests/test_model_ac.py` asserts reference/economics invariance, strict input, high-risk abstention, and no visualization survival rate. |
| Legacy persistence | v1-v3 table columns stay physically available; current route queries schema version 4 only. |
