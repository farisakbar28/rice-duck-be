# R2 Persistence and Versioning

> **Canonical history schema for new R2 simulations:** `schema_version = 4`  
> **Legacy v1/v2/v3:** immutable/read-only historical semantics.  
> **Do not overwrite v3 semantics in-place.**

## 1. Why v4 Is Mandatory

Current v3 persistence stores fields whose meanings are invalid under R2:

- `hst_in=21`, `hst_out=65`, `t_active=44` point semantics;
- numeric `n_survive` based on 100%/60% branch;
- fixed `yield_are_pred` and `yield_total_pred`;
- `revenue_duck_potential`;
- numeric fixed `cost_feed`;
- `core_cash_cost`, `total_revenue_dss`, `net_cash_contribution_dss`.

Reusing v3 columns would cause semantic corruption: a field with the same name would mean something materially different after migration.

## 2. Preferred Storage Strategy

Create a new table rather than continuing to append model-specific columns to the legacy table.

Suggested table:

```sql
CREATE TABLE IF NOT EXISTS dss_simulation_histories_r2 (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    schema_version INTEGER NOT NULL DEFAULT 4,
    model_version TEXT NOT NULL,
    parameter_registry_version TEXT NOT NULL,
    model_commit_sha TEXT,
    created_at TEXT NOT NULL,

    request_json TEXT NOT NULL,
    response_json TEXT NOT NULL,
    trace_json TEXT NOT NULL,

    -- list-view/index fields only; semantic snapshot remains response_json
    land_area_are REAL NOT NULL,
    duck_count INTEGER NOT NULL,
    rice_variety TEXT NOT NULL,
    planting_system TEXT NOT NULL,
    duck_age_days INTEGER NOT NULL,
    planting_date TEXT NOT NULL,
    p_duck_buy_manual REAL,
    p_duck_buy_effective REAL NOT NULL,

    density_are REAL NOT NULL,
    age_support TEXT NOT NULL,
    density_support TEXT NOT NULL,
    extrapolation_status TEXT NOT NULL,
    yield_availability TEXT NOT NULL,
    survival_availability TEXT NOT NULL,
    cost_completeness TEXT NOT NULL,

    yield_total_kg REAL,
    margin_core_rp REAL,
    profit_full_est_rp REAL,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_dss_r2_user_created
ON dss_simulation_histories_r2(user_id, created_at DESC);
```

### Why JSON snapshot is canonical

R2 intentionally has:

- nullable scientific values;
- ranges;
- availability flags;
- provenance trace;
- future versioned lookups.

A stored response snapshot preserves exactly what the user saw. It prevents future code/parameter changes from silently rewriting history semantics.

Selected explicit columns exist only for list/search efficiency.

## 3. Snapshot Policy

When an authenticated user calls `/api/v1/dss/simulate`:

1. resolve and validate request;
2. run R2 engines;
3. construct final `DSSSimulationResponseR2`;
4. serialize the **effective input** and final response;
5. save `request_json`, `response_json`, and `trace_json` atomically;
6. save indexed summary fields;
7. return the exact semantic response that was saved.

## 4. Required Version Metadata

Every v4 row must store:

```text
schema_version = 4
model_version = "R2"
parameter_registry_version = explicit immutable identifier
model_commit_sha = Git commit that produced the response, if available
created_at = UTC timestamp
```

Recommended registry version format:

```text
R2-2026-08-26.2
```

If regulatory prices or approved lookup tables later change without changing structural formulas, increment the registry version even if `model_version` remains R2.

## 5. Trace Snapshot

`trace_json` should include at least:

```json
{
  "active_formula_ids": [],
  "conditional_formula_ids": [],
  "disabled_legacy_formula_ids": [],
  "parameter_sources": {},
  "lookup_versions": {},
  "regulation_versions": {},
  "defaulted_inputs": [],
  "availability_reasons": {}
}
```

`active_formula_ids` records rules that were actually evaluated for the
request, including only the selected calendar branch. `conditional_formula_ids`
records conditional value-producing branches only when their availability gate
succeeded. Registry membership alone is not execution: pending or unavailable
yield, revenue, gross-value, and full-profit formulas must not appear in either
list. `disabled_legacy_formula_ids` remains non-executable invalidation
metadata.

Example default record:

```json
{
  "defaulted_inputs": [
    {
      "field": "p_duck_buy",
      "resolved_value": 26500,
      "source": "I1",
      "status": "mixed"
    }
  ]
}
```

## 6. Null Semantics

Database null has scientific meaning: value unavailable/not computed.

Rules:

- `yield_total_kg = NULL` when yield unavailable.
- `margin_core_rp = NULL` when yield or survival unavailable.
- `profit_full_est_rp = NULL` when cost completeness is incomplete.
- never write `0` to stand in for unknown.

Avoid `NOT NULL DEFAULT 0` for scientific/economic output columns.

## 7. History Read Policy

### v4

`GET /histories/{id}` returns the stored `response_json` snapshot, subject only to JSON-schema compatibility adapters that do not recalculate values.

### v1/v2/v3

Legacy rows remain historical records. They must not be converted on read into R2 values.

Recommended API behavior:

- list endpoint may expose them with `model_version="LEGACY"` and `schema_version`;
- detail endpoint may either:
  1. return a dedicated `LegacyHistoryResponse`, or
  2. return `409/422 legacy_history_semantics` with an audit endpoint/link.

Do **not** run current R2 engine with old inputs and call the result the original history.

## 8. Migration of Existing DB

Do not destructively alter existing table values.

Migration steps:

1. keep `users` table;
2. keep `dss_simulation_histories` for v1-v3;
3. create `dss_simulation_histories_r2`;
4. update repository to write v4 to new table;
5. update list service to merge rows only if product UX needs unified history;
6. ensure each item exposes model/schema version;
7. test delete ownership across both legacy and R2 storage.

## 9. Repository Interface

Suggested interface:

```python
class HistoryRepository:
    def create_r2(self, user_id: str, snapshot: R2HistorySnapshot) -> R2HistorySnapshot: ...
    def list_r2_by_user(self, user_id: str) -> list[R2HistorySummary]: ...
    def get_r2_by_id_and_user(self, history_id: str, user_id: str) -> R2HistorySnapshot | None: ...
    def delete_r2_by_id_and_user(self, history_id: str, user_id: str) -> bool: ...

    # legacy read-only
    def get_legacy_by_id_and_user(...): ...
```

Do not name the new method `create_v3` or reuse `SimulationHistory` v3 dataclass.

## 10. History Tests Required

1. v4 simulation round-trip response equality.
2. nullable yield survives persistence as null.
3. omitted purchase price persists both `manual=null` and effective `26500`.
4. v4 history retains parameter/model versions.
5. stored response is not recomputed after seed/config changes in a test.
6. v3 row remains readable only as legacy; not interpreted as R2.
7. ownership isolation (`user A` cannot read/delete `user B`).
8. deletion works for v4.

## 11. Phase-6 Candidate Persistence Amendment (R2.3)

The canonical `response_json` and `trace_json` snapshot must preserve every
Phase-6 yield semantic: reference, low, and high per-are and total yields;
`yield_range_type=LITERATURE_EVIDENCE_ENVELOPE`; evidence status, strength and
warning; source IDs; registry version; and freeze ID. Thus a future R2.3
snapshot remains self-interpretable even if a later registry changes.

For list/search efficiency, add nullable R2-table summary columns for
`yield_ref_kg_per_are`, `yield_low_kg_per_are`, `yield_high_kg_per_are`,
`yield_total_ref_kg`, `yield_total_low_kg`, `yield_total_high_kg`,
`yield_range_type`, and `yield_evidence_status`. Keep `yield_total_kg` as a
backward-compatible reference alias. This is an additive, idempotent schema
migration: existing schema-v4 R2.2 rows retain their original null yield and
R2.2 registry/freeze semantics; they are neither rewritten nor reinterpreted.

Required Phase-6 tests include migration from an existing v4 database,
reference/envelope round-trip equality and serialization precision, frozen
snapshot immutability after later registry changes, and legacy/v4 R2.2 read
compatibility.
