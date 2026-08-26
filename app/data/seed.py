"""R2 seed data -- approved values only.

Single source for active R2 configuration:
  - ``RICE_VARIETIES``      harvest calendar + yield-lookup state
  - ``PLANTING_SYSTEMS``    supported density ranges
  - ``PARAMETER_REGISTRY``  versioned parameter/config metadata

Rules enforced here (docs/01_R2_MODEL_SSOT.md,
docs/04_R2_PARAMETER_EXECUTION_REGISTRY.md,
docs/10_R2_REFERENCE_PROVENANCE.md):

  * Every entry carries key/unit/status_tag/execution_state/source_ids/
    model_version/effective_from (optional min/max range + note).
  * ``PENDING_LOOKUP`` / ``UNAVAILABLE`` entries have value ``None``
    (guarded by ``ParameterMetadata.__post_init__``). No fabricated numeric
    fallbacks: no fixed recap-derived yield baseline, no fake rice-duck
    response table, no feed shortcut price, no KCl price assumption,
    no duck-sale default, no recap-derived calibration. The banned-value
    blacklist lives in docs/07_R2_LEGACY_INVALIDATION_REGISTER.md and is
    enforced by the Phase-1 static test.
  * Harvest windows live ONLY on ``RiceVariety`` (no duplicated constants).
  * Provenance status and execution state are separate dimensions.
"""

from app.domain.models import (
    ExecutionState,
    LocalCultivarGroup,
    ParameterMetadata,
    PlantingSystem,
    ProvenanceStatus,
    RiceVariety,
)

MODEL_VERSION = "R2"
EFFECTIVE_FROM = "2026-08-26"

# Immutable parameter-registry identifier (docs/05 section 4 recommended
# format "R2-YYYY-MM-DD.N"; date matches EFFECTIVE_FROM). Distinct from
# MODEL_VERSION, APP_VERSION, the history schema version, and any Git SHA.
# Bump the trailing ".N" whenever a regulatory price or an approved lookup
# changes without a structural formula change; MODEL_VERSION stays "R2".
PARAMETER_REGISTRY_VERSION = "R2-2026-08-26.2"

# ---------------------------------------------------------------------------
# Freeze governance metadata (Phase 5; docs/11_R2_FREEZE_MANIFEST.md)
# ---------------------------------------------------------------------------
# Distinct provenance dimensions -- never merge these:
#   * MODEL_VERSION              scientific model generation ("R2")
#   * PARAMETER_REGISTRY_VERSION parameter/formula registry identity
#   * settings.app_version       deployment release version
#   * history schema_version     persistence schema of new simulations (4)
#   * settings.model_commit_sha  build/runtime Git commit (environment-injected;
#                                never a self-referential SHA inside its own commit)
#   * FREEZE_* below             governance state only
#
# frozen=true means "immutable validation target": the model/registry identity
# is fixed for retrospective validation. It does NOT mean empirically
# validated, accurate, or scientifically complete. Yield/feed/cage-total/full-
# profit remain unavailable exactly as before the freeze.
#
# The Phase-5 freeze candidate passed its computational gates on a clean tree
# at Phase-4 baseline 39fd69fbfa207862ce4da5be5d4f75e06eed6bdb with zero
# scientific-coefficient changes (guarded by tests/test_r2_freeze_semantics.py).
MODEL_FROZEN: bool = True
FREEZE_ID: str | None = "R2-FREEZE-2026-08-26.2"
FREEZE_EFFECTIVE_FROM: str | None = "2026-08-26"


# ---------------------------------------------------------------------------
# Rice varieties (SSOT §2; provenance doc §4)
# ---------------------------------------------------------------------------

RICE_VARIETIES: list[RiceVariety] = [
    RiceVariety(
        code="sertani",
        label="Sertani / Seratih",
        harvest_hst_min=100,
        harvest_hst_max=110,
        calendar_status=ProvenanceStatus.LOCAL_ESTIMATE,
        yield_lookup_status=ExecutionState.PENDING_LOOKUP,
        note=(
            "Harvest window is a local estimate (source I1). SERTANI_GROUP is "
            "a local label grouping, not genetic identity; its numeric yield "
            "baseline is not configured."
        ),
        cultivar_group_code=LocalCultivarGroup.SERTANI_GROUP,
    ),
    RiceVariety(
        code="inpari",
        label="Inpari",
        harvest_hst_min=90,
        harvest_hst_max=100,
        calendar_status=ProvenanceStatus.LOCAL_ESTIMATE,
        yield_lookup_status=ExecutionState.PENDING_LOOKUP,
        note=(
            "Harvest window is a local estimate (source I1). INPARI_GROUP is "
            "a local label grouping, not genetic identity; its numeric yield "
            "baseline is not configured."
        ),
        cultivar_group_code=LocalCultivarGroup.INPARI_GROUP,
    ),
]


# ---------------------------------------------------------------------------
# Planting systems (SSOT §4; provenance doc §4)
# ---------------------------------------------------------------------------

PLANTING_SYSTEMS: list[PlantingSystem] = [
    PlantingSystem(
        code="jajar_legowo",
        label="Jajar Legowo",
        supported_density_min_are=2.0,
        supported_density_max_are=4.0,
        status=ProvenanceStatus.LOCAL_ESTIMATE,
        note="Supported density 2-4 duck/are (sources I1/I2). Support metadata only.",
    ),
    PlantingSystem(
        code="tegel",
        label="Tegel",
        supported_density_min_are=2.0,
        supported_density_max_are=3.0,
        status=ProvenanceStatus.LOCAL_ESTIMATE,
        note="Supported density 2-3 duck/are (sources I1/I2). Support metadata only.",
    ),
]


def _param(
    key: str,
    *,
    value: object | None,
    unit: str | None,
    status_tag: ProvenanceStatus,
    execution_state: ExecutionState,
    source_ids: tuple[str, ...],
    note: str = "",
    minimum: float | None = None,
    maximum: float | None = None,
) -> ParameterMetadata:
    return ParameterMetadata(
        key=key,
        value=value,
        unit=unit,
        status_tag=status_tag,
        execution_state=execution_state,
        source_ids=source_ids,
        model_version=MODEL_VERSION,
        effective_from=EFFECTIVE_FROM,
        note=note,
        minimum=minimum,
        maximum=maximum,
    )


# ---------------------------------------------------------------------------
# Parameter registry (docs/04 sections 1-3, docs/10 section 4)
# ---------------------------------------------------------------------------

PARAMETER_REGISTRY: dict[str, ParameterMetadata] = {
    # --- Purchase price ---------------------------------------------------
    "p_duck_buy_default": _param(
        "p_duck_buy_default",
        value=26_500,
        unit="Rp/duck",
        status_tag=ProvenanceStatus.MIXED,
        execution_state=ExecutionState.ACTIVE,
        source_ids=("I1",),
        note=(
            "Midpoint of the local Rp25,000-28,000 range; range selection is "
            "local-estimate, midpoint choice is system-design (registry R2-PRICE-01). "
            "Applied only when the user omits/nulls p_duck_buy."
        ),
    ),
    "p_duck_buy_local_range": _param(
        "p_duck_buy_local_range",
        value=None,
        unit="Rp/duck",
        status_tag=ProvenanceStatus.LOCAL_ESTIMATE,
        execution_state=ExecutionState.ACTIVE_RANGE,
        source_ids=("I1",),
        minimum=25_000,
        maximum=28_000,
    ),
    # --- Calendar windows (harvest windows live on RiceVariety) ------------
    "release_hst_window": _param(
        "release_hst_window",
        value=None,
        unit="HST",
        status_tag=ProvenanceStatus.LOCAL_ESTIMATE,
        execution_state=ExecutionState.ACTIVE_RANGE,
        source_ids=("I1",),
        minimum=21,
        maximum=30,
    ),
    "pull_hst_window": _param(
        "pull_hst_window",
        value=None,
        unit="HST",
        status_tag=ProvenanceStatus.LOCAL_ESTIMATE,
        execution_state=ExecutionState.ACTIVE_RANGE,
        source_ids=("I1",),
        minimum=56,
        maximum=60,
    ),
    "active_duration_ref_days": _param(
        "active_duration_ref_days",
        value=32,
        unit="days",
        status_tag=ProvenanceStatus.LOCAL_ESTIMATE,
        execution_state=ExecutionState.ACTIVE_RANGE,
        source_ids=("I1",),
        minimum=28,
        maximum=40,
        note="Reference 32 days; support interval [28, 40] days (registry R2-CAL-05).",
    ),
    "supported_age_window_days": _param(
        "supported_age_window_days",
        value=None,
        unit="days",
        status_tag=ProvenanceStatus.MIXED,
        execution_state=ExecutionState.ACTIVE,
        source_ids=("I1",),
        minimum=21,
        maximum=30,
        note=(
            "Boundaries are local estimates; support labels are system design "
            "(registry R2-AGE-01). Classifier only -- never a numeric multiplier."
        ),
    ),
    # --- Density support metadata -----------------------------------------
    "density_limited_test_are": _param(
        "density_limited_test_are",
        value=None,
        unit="duck/are",
        status_tag=ProvenanceStatus.LOCAL_ESTIMATE,
        execution_state=ExecutionState.ACTIVE,
        source_ids=("I2",),
        minimum=5,
        maximum=6,
        note="Approximate limited-test band used by the support classifier.",
    ),
    "density_high_risk_threshold_are": _param(
        "density_high_risk_threshold_are",
        value=8,
        unit="duck/are",
        status_tag=ProvenanceStatus.LOCAL_ESTIMATE,
        execution_state=ExecutionState.ACTIVE,
        source_ids=("I2",),
        note="Approximate >=8 duck/are high-risk threshold; classifier metadata only.",
    ),
    # --- Survival (conditional) --------------------------------------------
    "lambda_safe_ref": _param(
        "lambda_safe_ref",
        value=0.90,
        unit="ratio",
        status_tag=ProvenanceStatus.LOCAL_ESTIMATE,
        execution_state=ExecutionState.CONDITIONAL,
        source_ids=("I2",),
        note=(
            "Safe-context working estimate only (registry R2-SURV-01). Numeric use "
            "requires age_support=SUPPORTED AND density_support=SUPPORTED; otherwise "
            "survival is unavailable. Gate logic belongs to the Phase-2 survival engine."
        ),
    ),
    # --- Nutrient baselines (literature-uncalibrated) -----------------------
    "n_need_kg_per_are": _param(
        "n_need_kg_per_are",
        value=1.1761,
        unit="kg N/are",
        status_tag=ProvenanceStatus.LITERATURE_UNCALIBRATED,
        execution_state=ExecutionState.ACTIVE_BASELINE,
        source_ids=("R1", "O3", "O5"),
    ),
    "p2o5_need_kg_per_are": _param(
        "p2o5_need_kg_per_are",
        value=0.2745,
        unit="kg P2O5/are",
        status_tag=ProvenanceStatus.LITERATURE_UNCALIBRATED,
        execution_state=ExecutionState.ACTIVE_BASELINE,
        source_ids=("R1", "O5"),
    ),
    "k2o_need_kg_per_are": _param(
        "k2o_need_kg_per_are",
        value=0.2745,
        unit="kg K2O/are",
        status_tag=ProvenanceStatus.LITERATURE_UNCALIBRATED,
        execution_state=ExecutionState.ACTIVE_BASELINE,
        source_ids=("R1", "O5"),
    ),
    # --- Fertilizer products/prices (regulatory) ---------------------------
    "het_urea_rp_per_kg": _param(
        "het_urea_rp_per_kg",
        value=1_800,
        unit="Rp/kg",
        status_tag=ProvenanceStatus.REGULATORY_LOCKED,
        execution_state=ExecutionState.ACTIVE_BASELINE,
        source_ids=("O2",),
    ),
    "het_npk_rp_per_kg": _param(
        "het_npk_rp_per_kg",
        value=1_840,
        unit="Rp/kg",
        status_tag=ProvenanceStatus.REGULATORY_LOCKED,
        execution_state=ExecutionState.ACTIVE_BASELINE,
        source_ids=("O2",),
    ),
    "urea_n_fraction": _param(
        "urea_n_fraction",
        value=0.46,
        unit="fraction",
        status_tag=ProvenanceStatus.REGULATORY_LOCKED,
        execution_state=ExecutionState.ACTIVE,
        source_ids=("O3",),
    ),
    "npk_n_fraction": _param(
        "npk_n_fraction",
        value=0.15,
        unit="fraction",
        status_tag=ProvenanceStatus.REGULATORY_LOCKED,
        execution_state=ExecutionState.ACTIVE,
        source_ids=("O4",),
        note="NPK Phonska 15-10-12 (N-P2O5-K2O).",
    ),
    "npk_p2o5_fraction": _param(
        "npk_p2o5_fraction",
        value=0.10,
        unit="fraction",
        status_tag=ProvenanceStatus.REGULATORY_LOCKED,
        execution_state=ExecutionState.ACTIVE,
        source_ids=("O4",),
    ),
    "npk_k2o_fraction": _param(
        "npk_k2o_fraction",
        value=0.12,
        unit="fraction",
        status_tag=ProvenanceStatus.REGULATORY_LOCKED,
        execution_state=ExecutionState.ACTIVE,
        source_ids=("O4",),
    ),
    # --- Paddy benchmark ----------------------------------------------------
    "p_gabah_ref_rp_per_kg": _param(
        "p_gabah_ref_rp_per_kg",
        value=6_500,
        unit="Rp/kg",
        status_tag=ProvenanceStatus.REGULATORY_LOCKED,
        execution_state=ExecutionState.ACTIVE,
        source_ids=("O1",),
        note="HPP regulatory benchmark (Inpres No. 4/2026), not a market-price forecast.",
    ),
    # --- Infrastructure local ranges ----------------------------------------
    "net_price_rp_per_m": _param(
        "net_price_rp_per_m",
        value=None,
        unit="Rp/m",
        status_tag=ProvenanceStatus.LOCAL_ESTIMATE,
        execution_state=ExecutionState.ACTIVE_RANGE,
        source_ids=("I1",),
        minimum=6_000,
        maximum=6_750,
        note="Price per meter of net/fence; lifetime handled by net_lifetime_cycles.",
    ),
    "net_lifetime_cycles": _param(
        "net_lifetime_cycles",
        value=None,
        unit="cycles",
        status_tag=ProvenanceStatus.LOCAL_ESTIMATE,
        execution_state=ExecutionState.ACTIVE_RANGE,
        source_ids=("I1",),
        minimum=2,
        maximum=3,
    ),
    "cage_cost_per_unit_cycle_rp": _param(
        "cage_cost_per_unit_cycle_rp",
        value=None,
        unit="Rp/unit/cycle",
        status_tag=ProvenanceStatus.LOCAL_ESTIMATE,
        execution_state=ExecutionState.ACTIVE_RANGE,
        source_ids=("I1",),
        minimum=150_000,
        maximum=200_000,
        note="Per-unit cycle range; reference midpoint Rp175,000. Total cage cost stays unavailable without a capacity rule.",
    ),
    "weeding_baseline_rp_per_are": _param(
        "weeding_baseline_rp_per_are",
        value=None,
        unit="Rp/are",
        status_tag=ProvenanceStatus.LOCAL_ESTIMATE,
        execution_state=ExecutionState.ACTIVE_RANGE,
        source_ids=("I1",),
        minimum=6_000,
        maximum=38_000,
        note="Baseline weeding cost band per are. Monetary saving conversion is unavailable.",
    ),
    # --- Duck terminal value (conditional, NOT cash revenue) -----------------
    "duck_terminal_value_rp_per_duck": _param(
        "duck_terminal_value_rp_per_duck",
        value=45_000,
        unit="Rp/duck",
        status_tag=ProvenanceStatus.LOCAL_ESTIMATE,
        execution_state=ExecutionState.CONDITIONAL,
        source_ids=("I1", "I2"),
        minimum=30_000,
        maximum=60_000,
        note=(
            "Terminal livestock value reference with sensitivity range; requires "
            "N_survive. It is NOT realized duck cash revenue (registry R2-DUCKVAL-01)."
        ),
    ),
    # --- Pending lookups / unavailable branches (value MUST stay None) -------
    "yield_base_by_cultivar_group": _param(
        "yield_base_by_cultivar_group",
        value=None,
        unit="kg/are",
        status_tag=ProvenanceStatus.LITERATURE_UNCALIBRATED,
        execution_state=ExecutionState.PENDING_LOOKUP,
        source_ids=(),
        note=(
            "Local cultivar-group baseline table not configured/approved yet "
            "(registry R2-YLD-LKP-BASE). Missing lookup must yield null output, never a constant."
        ),
    ),
    "f_rd_lookup": _param(
        "f_rd_lookup",
        value=None,
        unit="factor",
        status_tag=ProvenanceStatus.LITERATURE_UNCALIBRATED,
        execution_state=ExecutionState.PENDING_LOOKUP,
        source_ids=(),
        note=(
            "Rice-duck response table/model not encoded/approved yet "
            "(registry R2-YLD-LKP-RD). Candidate literature exists but effect sizes "
            "must not be transplanted (provenance doc section 6)."
        ),
    ),
    "feed_quantity_lookup": _param(
        "feed_quantity_lookup",
        value=None,
        unit="kg/duck/day",
        status_tag=ProvenanceStatus.LITERATURE_UNCALIBRATED,
        execution_state=ExecutionState.UNAVAILABLE,
        source_ids=(),
        note="q_feed(t,U,d) lookup incomplete; no per-duck feed shortcut is permitted (R2-FEED-01).",
    ),
    "feed_price_lookup": _param(
        "feed_price_lookup",
        value=None,
        unit="Rp/kg",
        status_tag=ProvenanceStatus.LITERATURE_UNCALIBRATED,
        execution_state=ExecutionState.UNAVAILABLE,
        source_ids=(),
        note="p_feed(t) lookup incomplete (R2-FEED-01).",
    ),
    "cage_capacity_rule": _param(
        "cage_capacity_rule",
        value=None,
        unit=None,
        status_tag=ProvenanceStatus.SYSTEM_DESIGN,
        execution_state=ExecutionState.UNAVAILABLE,
        source_ids=(),
        note="Cage units-per-area rule absent; total cage cost blocked (R2-CAGE-02).",
    ),
    "manure_nutrient_credit": _param(
        "manure_nutrient_credit",
        value=None,
        unit=None,
        status_tag=ProvenanceStatus.MIXED,
        execution_state=ExecutionState.UNAVAILABLE,
        source_ids=(),
        note=(
            "No supported temporal manure credit; nutrient needs run baseline-no-credit "
            "(registry R2-MANURE-01, SSOT section 7). Not a claim of zero contribution."
        ),
    ),
    "weeding_saving_conversion": _param(
        "weeding_saving_conversion",
        value=None,
        unit=None,
        status_tag=ProvenanceStatus.SYSTEM_DESIGN,
        execution_state=ExecutionState.UNAVAILABLE,
        source_ids=(),
        note="Biological suppression != monetary saving; conversion unsupported (R2-WEED-02).",
    ),
    "pesticide_saving_conversion": _param(
        "pesticide_saving_conversion",
        value=None,
        unit=None,
        status_tag=ProvenanceStatus.SYSTEM_DESIGN,
        execution_state=ExecutionState.UNAVAILABLE,
        source_ids=(),
        note="No valid monetary conversion baseline/function (R2-PEST-02).",
    ),
    "pesticide_effect": _param(
        "pesticide_effect",
        value="CONTEXT_SPECIFIC",
        unit=None,
        status_tag=ProvenanceStatus.LITERATURE_UNCALIBRATED,
        execution_state=ExecutionState.DESCRIPTIVE,
        source_ids=(),
        note="Qualitative context descriptor only; no universal pest-reduction scalar (R2-PEST-01).",
    ),
    "kcl_branch": _param(
        "kcl_branch",
        value=None,
        unit=None,
        status_tag=ProvenanceStatus.SYSTEM_DESIGN,
        execution_state=ExecutionState.UNAVAILABLE,
        source_ids=(),
        note=(
            "KCl excluded from the active product set until a valid exact price/source "
            "is configured (R2-KCL-01); the historical Rp9,500 assumption is invalidated."
        ),
    ),
}


__all__ = [
    "EFFECTIVE_FROM",
    "FREEZE_EFFECTIVE_FROM",
    "FREEZE_ID",
    "MODEL_FROZEN",
    "MODEL_VERSION",
    "PARAMETER_REGISTRY",
    "PARAMETER_REGISTRY_VERSION",
    "PLANTING_SYSTEMS",
    "RICE_VARIETIES",
]
