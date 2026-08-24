# Stale-semantics audit — A+C evidence freeze

Generated after the A+C cleanup with a repository-wide text search (source, tests, scripts, docs, tracked configuration, and Postman paths; Git object history excluded). Search terms included legacy yield/survival/calendar/economics symbols, numerical fusion words, optimizer labels, and prior model constants.

| Retained occurrence | Classification | Why it is unambiguous |
| --- | --- | --- |
| `app/core/database.py` v1-v3 columns such as `hst_out`, `t_active`, `n_survive`, legacy yield/economics fields | **Legacy physical persistence only** | The comments state v1-v3 are historical physical storage; current repository reads, lists, details, and deletes only `schema_version=4`. Live HTTP evidence seeds v1/v2/v3 and proves hidden/list-detail-delete behavior while rows persist. |
| `docs/Model Matematika Data Collection DSS Padi Bebek FINAL.md` legacy terms/numbers | **Authoritative rejection and historical rationale** | The SoT explicitly identifies them as rejected/obsolete and specifies C0 primary plus separate Xiong reference. It is not executable and is not contradicted by runtime. |
| `CHANGELOG.md` optimizer references | **Historical/removal record** | It says the legacy optimizer was removed and is absent from router/OpenAPI. |
| `README.md` words such as average/ensemble/optimizer | **Negative current-contract statements** | They explicitly prohibit fusion and state that no optimizer endpoint is exposed. |
| `tests/test_model_ac.py` / `scripts/validate_model_ac_runtime.py` `cost_feed_scenario`, optimizer-path, and survival-rate checks | **Current negative/optional-cost tests** | These verify optional scenario cost only, optimizer absence, and absence of numerical survival; they are not legacy model arithmetic. |
| `app/schemas/dss.py`, `app/services/simulation_service.py`, `app/engines/formula_engine.py`, `app/services/visualization_service.py` optional feed/all-sold fields and non-fused language | **Current A+C contract** | Optional costs are runtime scenario inputs; C0 remains the only economics yield. HIGH risk abstains from all-sold revenue without calculating survival. |
| `docs/runtime_evidence_model_ac.json` `cost_feed_scenario: null` | **Generated current runtime evidence** | It records the current optional field as null when omitted, not a legacy Core-feed default. |
| This audit document | **Audit vocabulary** | Terms are retained solely to classify search findings. |

## Confirmed removals from current-model exposure

- No `DSSConstants` class, instantiation, or lookup endpoint remains.
- No current domain type contains old harvest windows, fixed 21/65/44 semantics, numerical survival, `N_survive`, or old predicted-yield/economic DTOs.
- `impact_engine.py` is an archive notice only and is not imported by DSS Core.
- Optimizer router/schema are deleted; OpenAPI exposes no optimizer tag/path.
- No tracked operational JWT secret exists; `.env.example` has a placeholder only.
- Runtime status uses only `VALID_DOMAIN` or `OUTSIDE_LITERATURE_DOMAIN`.

The retained legacy strings above are all either physical v1-v3 compatibility, explicit historical/rejection evidence, negative tests, or current optional-field names. None can route into the current A+C scientific output.
