# Rice-Duck DSS Backend

FastAPI backend for the canonical R2 rice-duck decision-support model. The
canonical documentation starts at
[`docs/00_R2_BACKEND_DOCUMENTATION_INDEX.md`](docs/00_R2_BACKEND_DOCUMENTATION_INDEX.md)
and [`docs/01_R2_MODEL_SSOT.md`](docs/01_R2_MODEL_SSOT.md); the remaining
numbered R2 documents define its API, registry, persistence, and provenance.

R2 is availability-aware: a valid simulation can return HTTP 200 with some
scientific or economic values set to `null`. Missing yield, feed, cage-total,
or full-profit evidence is reported explicitly and is never replaced with a
legacy constant, zero, or synthetic curve.

## Run locally

1. Copy `.env.example` to `.env` and replace `JWT_SECRET_KEY` with an explicit
   local secret.
2. Install dependencies: `python -m pip install -r requirements.txt`.
3. Start the API:

   ```bash
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

Swagger UI is available at `http://127.0.0.1:8000/docs`.

## API

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/health` | No | Service health |
| POST | `/api/v1/auth/register` | No | Register a history owner |
| POST | `/api/v1/auth/login` | No | Create a bearer token |
| GET | `/api/v1/dss/options` | No | Canonical R2 input options |
| POST | `/api/v1/dss/simulate` | Optional | Run R2; bearer auth persists one v4 snapshot |
| POST | `/api/v1/dss/visualize` | No | Side-effect-free visualization view of R2 |
| GET | `/api/v1/dss/histories` | Bearer | List the caller's R2 and labeled legacy rows |
| GET | `/api/v1/dss/histories/{id}` | Bearer | Read a stored R2 semantic snapshot |
| DELETE | `/api/v1/dss/histories/{id}` | Bearer | Delete an owned history row |

The optimizer route is an isolated product stub and is not part of the R2
scientific model.

## Simulation request

Six fields are required; `p_duck_buy` is optional. Omitting it or sending
`null` selects the registry default. A supplied price must be greater than
zero.

```json
{
  "land_area_are": 7,
  "duck_count": 28,
  "planting_date": "2026-06-01",
  "planting_system": "jajar_legowo",
  "rice_variety": "sertani",
  "duck_age_days": 30,
  "p_duck_buy": null
}
```

`land_area_are`, `duck_count`, and `duck_age_days` must be positive. Supported
reference codes are returned by `/dss/options`. Schema validation uses HTTP
400; an unknown variety or planting-system reference uses HTTP 422.

## R2 output semantics

Current, scientifically intentional limitations are explicit: Phase-6 yield is
available only inside the resolved cultivar-group, supported-age, and supported-
density evidence domain; feed cost, cage total, and full profit remain
`UNAVAILABLE`. Terminal duck value is not realized cash revenue. These states
prevent unsupported numeric claims.

- Calendar values are windows, including release, pull, harvest, and active
  duration support ranges.
- Age and density values are applicability flags. They gate survival
  availability; they are not yield multipliers or penalties.
- Yield is available only after an approved cultivar-group baseline, supported
  age and density, and the pooled rice-duck reference all resolve. Unknown or
  out-of-domain requests remain `UNAVAILABLE`; the active group baselines are
  external literature ranges, not exact local-cultivar or Bali calibration.
- Fertilizer is an available `BASELINE-NO-CREDIT` estimate. It does not claim
  that manure contributes zero nutrients.
- Net infrastructure is a calculated request-area range. Cage unit cost is a
  partial range; total cage cost remains unavailable without a capacity rule.
- Terminal duck value is a livestock asset value, not cash revenue.
- `cost_total_available_rp` is only the subtotal of numeric components.
  `profit_full_est_rp` stays unavailable while the configured ledger is
  incomplete.
- Trace metadata distinguishes formulas that ran from conditional formulas
  whose value-producing branch actually succeeded.

## Visualization contract

`POST /api/v1/dss/visualize` accepts the simulation request and returns a
presentation-only view over the same canonical result:

- complete age and planting-system-specific density support zones, with
  exactly one selected zone for valid input;
- the same calendar window returned by `/dss/simulate`;
- the calculated infrastructure range for the request area;
- NPK and urea fertilizer baseline components;
- the selected Phase-6 yield reference/evidence envelope, or an explicitly
  unavailable series outside the supported domain;
- a partial financial waterfall that separates cash revenue, livestock asset
  value, costs, available-cost subtotal, and unavailable full profit.

The endpoint always calls simulation anonymously. It never writes history,
even if a bearer token is included.

## Freeze and Phase-6 release status

R2 is **frozen for validation**: `model.frozen = true`,
`freeze_id = R2-FREEZE-2026-08-26.5`, with registry
`R2-2026-08-26.3`. Frozen means the model/registry identity
is an immutable validation target — it does **not** mean empirically validated,
accurate, or complete. Phase 6E approved technical-empirical validation with
limitations; corrected Phase-6D-R evidence reports yield and revenue
diagnostics. The final expert assessment remains
`PENDING_NON_BLOCKING_EVIDENCE_STREAM` and is not a release blocker. See
[`docs/11_R2_FREEZE_MANIFEST.md`](docs/11_R2_FREEZE_MANIFEST.md) and the
research-only harness under [`validation/`](validation/) (dependencies:
[`requirements-validation.txt`](requirements-validation.txt); never imported by
production code). The release map is
[`docs/14_R2_FINAL_RELEASE_CLOSURE.md`](docs/14_R2_FINAL_RELEASE_CLOSURE.md).

## History and versioning

Authenticated simulations store schema-v4 request, response, and trace JSON as
an immutable semantic snapshot. Detail reads the stored response instead of
recomputing it under a newer registry. Pre-R2 rows remain isolated: list output
labels them `LEGACY`, while detail returns the documented semantic-conflict
error rather than translating old values into R2.

The scientific model version (`R2`), parameter-registry version, history
schema version, deployment application version, and optional
`MODEL_COMMIT_SHA` are independent provenance dimensions. A source checkout
uses `APP_VERSION=0.0.0-dev`; deployment automation should inject the release
version instead of editing source.

## Security configuration

`JWT_SECRET_KEY` is required in every environment; the application has no
built-in or generated fallback. In production the application also refuses to
start with debug mode enabled, wildcard/empty CORS origins, a placeholder
secret, or fewer than 600,000 PBKDF2 iterations. Lower iteration counts are
permitted only when `APP_ENV=test` to keep automated tests fast.

## Tests

```bash
python -m pytest -q
```

`pytest.ini` collects only active `tests/test_*.py` files and excludes
`tests/legacy_invalid/`. That directory is retained solely as historical
evidence for invalidated contracts and is not an active regression oracle.

The Postman assets in [`postman/`](postman/) exercise options, anonymous and
authenticated simulation, visualization semantics, history round-trip, and
negative validation/reference cases.

## Phase-6 final export sources

The active Phase-6 yield branch is literature-uncalibrated and range-aware:
Inpari 53.5/20.0/78.4 kg/are, Sertani 44.5/22.3/66.7 kg/are (explicit low
evidence), and pooled `F_RD_ref=1.028`. It executes only for resolved cultivar
groups within the supported age/density domain, returning a
`LITERATURE_EVIDENCE_ENVELOPE`, never a confidence or prediction interval.
The authoritative later-generation sources are:

- [`docs/export/R2_FINAL_MATHEMATICAL_MODEL_SOURCE.md`](docs/export/R2_FINAL_MATHEMATICAL_MODEL_SOURCE.md)
- [`docs/export/R2_FINAL_VALIDATION_METHODOLOGY_SOURCE.md`](docs/export/R2_FINAL_VALIDATION_METHODOLOGY_SOURCE.md)
- [`docs/export/R2_IJOST_MANUSCRIPT_FACT_PACKAGE.md`](docs/export/R2_IJOST_MANUSCRIPT_FACT_PACKAGE.md)
- [`docs/export/R2_EXPORT_SOURCE_AUDIT.md`](docs/export/R2_EXPORT_SOURCE_AUDIT.md)

Comparator workbooks remain validation evidence only and were not used for
parameter fitting or recalibration.
