"""Domain models for the R2 rice-duck DSS backend.

Layout (keep sections separate; do not let R2 runtime code consume the
NON-R2 legacy section):

  1. Canonical R2 enumerations.
     Provenance status and execution state are SEPARATE dimensions
     (docs/04_R2_PARAMETER_EXECUTION_REGISTRY.md section 1,
     docs/07_R2_LEGACY_INVALIDATION_REGISTER.md section 3).
     Only the values below are canonical; the ad-hoc current-master status
     labels banned by docs/07 section 3 must never be reintroduced here.

  2. Active R2 lookup/configuration structures (frozen).
     No fixed calendar points (21/65/44), no yield baseline, no duck-sale
     default, no feed default, no KCl assumption. Unresolved scientific
     quantities are represented by registry entries whose value is ``None``
     plus an explicit execution state -- never a placeholder number.

  3. NON-R2 legacy history models (schema_version <= 3).
     Retained ONLY so historical rows stay readable. Byte-compatible with
     the pre-R2 definitions on purpose. Never import these from R2 engines,
     services, or schemas.

  4. Auth/user infrastructure (model-independent, unchanged).

References:
  docs/01_R2_MODEL_SSOT.md          - canonical values/flags
  docs/03_R2_API_CONTRACT.md        - response semantics
  docs/04_R2_PARAMETER_EXECUTION_REGISTRY.md - registry contract
  docs/10_R2_REFERENCE_PROVENANCE.md - source IDs (I1..I5, R1..R7, O1..O5)
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# 1. Canonical R2 enumerations
# ---------------------------------------------------------------------------


class ProvenanceStatus(str, Enum):
    """Scientific/economic provenance tag of a value or formula (R2 §15)."""

    LOCAL_CALIBRATED = "local-calibrated"
    LOCAL_ESTIMATE = "local-estimate"
    LITERATURE_UNCALIBRATED = "literature-uncalibrated"
    SYSTEM_DESIGN = "system-design"
    REGULATORY_LOCKED = "regulatory-locked"
    MIXED = "mixed"


class ExecutionState(str, Enum):
    """Whether/how a value or formula may execute at runtime (registry §1)."""

    ACTIVE = "ACTIVE"
    ACTIVE_RANGE = "ACTIVE_RANGE"
    ACTIVE_BASELINE = "ACTIVE_BASELINE"
    CONDITIONAL = "CONDITIONAL"
    PENDING_LOOKUP = "PENDING_LOOKUP"
    UNAVAILABLE = "UNAVAILABLE"
    DESCRIPTIVE = "DESCRIPTIVE"
    NON_EXECUTABLE_LEGACY = "NON_EXECUTABLE_LEGACY"


class AgeSupportFlag(str, Enum):
    """Age is a support/applicability classifier only (R2 §3)."""

    CAUTION = "CAUTION"
    SUPPORTED = "SUPPORTED"
    OUTSIDE_LOCAL_RANGE = "OUTSIDE_LOCAL_RANGE"


class DensitySupportFlag(str, Enum):
    """Density support classification; metadata/warning only, never a penalty coefficient (R2 §4)."""

    SUPPORTED = "SUPPORTED"
    LIMITED_TEST = "LIMITED_TEST"
    HIGH_RISK = "HIGH_RISK"
    EXTRAPOLATION = "EXTRAPOLATION"


class AvailabilityStatus(str, Enum):
    """Canonical availability for scientific outputs (SSOT §14)."""

    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class CostCompletenessFlag(str, Enum):
    """Ledger completeness gate for full-profit emission (R2 §13)."""

    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"


class PriceBenchmarkType(str, Enum):
    """Paddy price semantics: regulatory HPP benchmark, not a forecast (R2 §12)."""

    REGULATORY_HPP = "REGULATORY_HPP"


class ExtrapolationFlag(str, Enum):
    """In/out-of-domain marker for literature-backed lookups (SSOT §14)."""

    IN_DOMAIN = "IN_DOMAIN"
    OUT_OF_DOMAIN = "OUT_OF_DOMAIN"


class PurchasePriceSource(str, Enum):
    """How the effective duck purchase price was resolved (contract §3.2)."""

    USER_INPUT = "USER_INPUT"
    LOCAL_DEFAULT_MIDPOINT = "LOCAL_DEFAULT_MIDPOINT"


class LocalCultivarGroup(str, Enum):
    """Evidence-bounded local label groups; these are not genetic identities."""

    SERTANI_GROUP = "SERTANI_GROUP"
    INPARI_GROUP = "INPARI_GROUP"


class ComponentAvailability(str, Enum):
    """Availability vocabulary for cost components that can be range-valued.

    Defined by docs/03_R2_API_CONTRACT.md section 4 response shape:
    net infrastructure is AVAILABLE_RANGE, cage PARTIAL_RANGE_ONLY,
    weeding BASELINE_RANGE_ONLY, fully blocked components UNAVAILABLE.
    """

    AVAILABLE = "AVAILABLE"
    AVAILABLE_RANGE = "AVAILABLE_RANGE"
    PARTIAL_RANGE_ONLY = "PARTIAL_RANGE_ONLY"
    BASELINE_RANGE_ONLY = "BASELINE_RANGE_ONLY"
    UNAVAILABLE = "UNAVAILABLE"


# ---------------------------------------------------------------------------
# 2. Active R2 lookup/configuration structures (frozen)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RiceVariety:
    """R2 rice variety lookup entry.

    Harvest windows are local estimates (Sertani/Seratih 100-110,
    Inpari 90-100 HST). Yield resolution is PENDING_LOOKUP until an approved
    local-group baseline table exists; no numeric yield baseline may be
    attached to this type. ``cultivar_group_code`` is a historical-label
    grouping for lookup only and must never be described as genetic identity.
    """

    code: str
    label: str
    harvest_hst_min: int
    harvest_hst_max: int
    calendar_status: ProvenanceStatus
    yield_lookup_status: ExecutionState
    note: str = ""
    cultivar_group_code: LocalCultivarGroup | None = None


@dataclass(frozen=True)
class PlantingSystem:
    """R2 planting-system lookup entry.

    Supported density ranges only (Jarwo 2-4, Tegel 2-3 duck/are).
    Deliberately carries NO F_sys / f_yield / penalty fields: density and
    system are support metadata, never yield multipliers (R2 §4).
    """

    code: str
    label: str
    supported_density_min_are: float
    supported_density_max_are: float
    status: ProvenanceStatus
    note: str = ""


@dataclass(frozen=True)
class ParameterMetadata:
    """Versioned parameter/config record (registry §5, provenance doc §5).

    ``value`` is ``None`` whenever ``execution_state`` is ``PENDING_LOOKUP``
    or ``UNAVAILABLE``; a numeric value in those states would be a fabricated
    fallback. ``source_ids`` reference docs/10 (I*/R*/O* identifiers).
    """

    key: str
    value: Any | None
    unit: str | None
    status_tag: ProvenanceStatus
    execution_state: ExecutionState
    source_ids: tuple[str, ...]
    model_version: str
    effective_from: str
    note: str = ""
    minimum: float | None = None
    maximum: float | None = None

    def __post_init__(self) -> None:
        if self.execution_state in (
            ExecutionState.PENDING_LOOKUP,
            ExecutionState.UNAVAILABLE,
        ) and isinstance(self.value, (int, float)):
            raise ValueError(
                f"Parameter '{self.key}': execution_state={self.execution_state.value} "
                "must not carry a numeric value (fail-closed rule, registry §6)."
            )
        if self.source_ids and not all(isinstance(s, str) for s in self.source_ids):
            raise ValueError(f"Parameter '{self.key}': source_ids must be strings.")


# ---------------------------------------------------------------------------
# 3. R2 persistence v4 snapshot row (docs/05_R2_PERSISTENCE_VERSIONING.md)
# ---------------------------------------------------------------------------
# Semantic storage model for ``dss_simulation_histories_r2``. The JSON
# snapshots (request/response/trace) are the canonical semantic record; the
# remaining fields are indexed list/filter columns. Scientific unknowns stay
# None -- they must never be written as numeric zero. This type is fully
# isolated from the NON-R2 v1-v3 dataclasses below.


@dataclass(frozen=True)
class R2HistorySnapshot:
    """One schema_version=4 row of the R2 history table."""

    id: str
    user_id: str
    schema_version: int
    model_version: str
    parameter_registry_version: str
    model_commit_sha: str | None
    created_at: datetime

    request_json: str
    response_json: str
    trace_json: str

    # Indexed summary columns (list view only)
    land_area_are: float
    duck_count: int
    rice_variety: str
    planting_system: str
    duck_age_days: int
    planting_date: str
    p_duck_buy_manual: float | None
    p_duck_buy_effective: float

    density_are: float
    age_support: str
    density_support: str
    extrapolation_status: str
    yield_availability: str
    survival_availability: str
    cost_completeness: str

    # Unknown scientific outputs remain SQL NULL / Python None.
    yield_total_kg: float | None
    margin_core_rp: float | None
    profit_full_est_rp: float | None


# ---------------------------------------------------------------------------
# 4. NON-R2 legacy history models (read-only compatibility, v1-v3)
# ---------------------------------------------------------------------------
# The two dataclasses below are intentionally byte-compatible with the
# pre-R2 master definitions so existing rows in ``dss_simulation_histories``
# remain readable. They encode invalidated pre-R2 semantics (fixed-yield
# columns, survivor-monetized revenue, the old net-contribution aggregate,
# point-calendar columns -- see docs/07 register) and therefore MUST NOT be
# imported by any R2 engine/service/schema. Persistence v4 uses
# ``R2HistorySnapshot`` above (docs/05_R2_PERSISTENCE_VERSIONING.md).


@dataclass(frozen=True)
class SimulationHistoryLegacy:
    """NON-R2. Legacy schema (schema_version <= 2). Read-only for audit."""

    id: str
    user_id: str
    input_data: dict
    actual_scenario: dict
    recommended_scenario: dict
    comparison: dict
    risk: dict
    trace: dict
    notes: list[str]
    economics: dict
    ecology: dict
    environment: dict
    lookup: dict
    validation: dict
    data_readiness: dict
    created_at: datetime
    schema_version: int = 1


@dataclass(frozen=True)
class SimulationHistory:
    """NON-R2. v3 schema row of the invalidated pre-R2 model. Read-only."""

    id: str
    user_id: str
    schema_version: int
    # Input snapshot
    land_area_are: float
    duck_count: int
    rice_variety: str
    planting_system: str
    duck_age_days: int
    planting_date: str
    p_duck_buy: float
    # Age Engine
    age_flag: str
    # Density Engine
    density_are: float
    density_ha: float
    density_status: str
    # Calendar Engine
    hst_in: int
    hst_out: int
    t_active: int
    d_in: str
    d_out: str
    harvest_hst_min: int
    harvest_hst_max: int
    d_panen_min: str
    d_panen_max: str
    # Survival Engine
    n_survive: int
    # Yield Engine
    yield_are_pred: float
    yield_total_pred: float
    # Core Economics (pre-R2 ledger; NOT canonical R2 outputs)
    revenue_gabah: float
    revenue_duck_potential: float
    cost_duck_buy: float
    cost_feed: float
    core_cash_cost: float
    total_revenue_dss: float
    net_cash_contribution_dss: float
    # Warnings (JSON string)
    warnings_json: str
    created_at: datetime


# ---------------------------------------------------------------------------
# 5. Auth/user infrastructure (unchanged)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class User:
    id: str
    name: str
    email: str
    password_hash: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class AuthContext:
    user: User
