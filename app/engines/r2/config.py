"""Immutable R2 engine configuration built from the canonical registry.

Parameter-access design (approved plan section 6):
  * Every scientific/economic constant used by the pure engines is carried
    by this frozen dataclass. Engines receive it as an argument; they never
    read module-level mutable state.
  * ``R2EngineConfig.from_registry`` validates presence, execution state,
    and numeric availability of every required entry and fails closed
    (ValueError listing all offenders) at construction time.
  * Reference values that the SSOT derives from ranges are computed here
    once (cage per-unit midpoint; net lifetime midpoint) instead of being
    duplicated as magic numbers across engine modules.
  * ``load_default_config()`` wires the production seed registry
    (``app.data.seed``). Pure unit tests construct configs directly or via
    ``from_registry`` on explicit mappings -- no global mutable state.

Sources: docs/01_R2_MODEL_SSOT.md, docs/04_R2_PARAMETER_EXECUTION_REGISTRY.md,
docs/10_R2_REFERENCE_PROVENANCE.md.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from decimal import Decimal

from app.data.seed import PARAMETER_REGISTRY, PLANTING_SYSTEMS
from app.domain.models import ExecutionState, ParameterMetadata, PlantingSystem
from app.engines.r2.common import to_decimal

# Deterministic unit conversion: 1 are = 100 m^2 (registry R2-NORM-01).
# This is a definitional identity, not a scientific estimate.
ARE_TO_M2 = Decimal("100")


@dataclass(frozen=True)
class R2EngineConfig:
    """All runtime constants required by the R2 pure engines."""

    # --- normalization / pricing -----------------------------------------
    area_m2_per_are: Decimal            # definitional (ARE_TO_M2)
    p_duck_buy_default: Decimal         # registry p_duck_buy_default (26,500)

    # --- age support bounds ------------------------------------------------
    age_supported_min_days: int         # 21
    age_supported_max_days: int         # 30

    # --- density support metadata ------------------------------------------
    density_high_risk_min_are: Decimal  # >= 8 -> HIGH_RISK
    density_limited_test_min_are: Decimal  # limited-test band lower bound (5)
    density_limited_test_max_are: Decimal  # limited-test band upper bound (6)
    supported_density_by_system: Mapping[str, tuple[Decimal, Decimal]]

    # --- calendar windows ----------------------------------------------------
    release_hst_min: int                # 21
    release_hst_max: int                # 30
    pull_hst_min: int                   # 56
    pull_hst_max: int                   # 60
    active_duration_ref_days: int       # 32
    active_duration_support_min_days: int  # 28
    active_duration_support_max_days: int  # 40
    f_rd_release_ref_hst: int           # release reference for response lookup (= release max, 30)

    # --- survival (conditional; gate enforced by the survival engine) --------
    lambda_safe_ref: Decimal            # 0.90

    # --- fertilizer baseline -------------------------------------------------
    n_need_kg_per_are: Decimal          # 1.1761
    p2o5_need_kg_per_are: Decimal       # 0.2745
    k2o_need_kg_per_are: Decimal        # 0.2745
    urea_n_fraction: Decimal            # 0.46
    npk_n_fraction: Decimal             # 0.15
    npk_p2o5_fraction: Decimal          # 0.10
    npk_k2o_fraction: Decimal           # 0.12
    het_urea_rp_per_kg: Decimal         # 1800
    het_npk_rp_per_kg: Decimal          # 1840

    # --- infrastructure -------------------------------------------------------
    net_price_min_rp_per_m: Decimal     # 6000
    net_price_max_rp_per_m: Decimal     # 6750
    net_lifetime_min_cycles: Decimal    # 2
    net_lifetime_max_cycles: Decimal    # 3
    net_lifetime_mid_cycles: Decimal    # derived midpoint (2.5)
    cage_unit_min_rp_per_cycle: Decimal   # 150000
    cage_unit_max_rp_per_cycle: Decimal   # 200000
    cage_unit_ref_rp_per_cycle: Decimal   # derived midpoint (175000)

    # --- weeding / pest --------------------------------------------------------
    weeding_baseline_min_rp_per_are: Decimal  # 6000
    weeding_baseline_max_rp_per_are: Decimal  # 38000
    pesticide_effect: str                     # "CONTEXT_SPECIFIC"

    # --- economics ---------------------------------------------------------------
    p_gabah_ref_rp_per_kg: Decimal      # 6500 (regulatory benchmark)
    duck_terminal_min_rp_per_duck: Decimal  # 30000
    duck_terminal_ref_rp_per_duck: Decimal  # 45000
    duck_terminal_max_rp_per_duck: Decimal  # 60000

    @classmethod
    def from_registry(
        cls,
        registry: Mapping[str, ParameterMetadata],
        systems: Iterable[PlantingSystem],
    ) -> "R2EngineConfig":
        """Build a config from a parameter registry + planting systems.

        Fails closed: any missing key, wrong execution state, missing numeric
        value, or missing range aborts construction with a single ValueError
        describing every problem found.
        """
        errors: list[str] = []

        def entry(key: str) -> ParameterMetadata | None:
            item = registry.get(key)
            if item is None:
                errors.append(f"missing registry parameter '{key}'")
            return item

        def num(key: str, expected: ExecutionState) -> Decimal:
            item = entry(key)
            if item is None:
                return Decimal(0)
            if item.execution_state is not expected:
                errors.append(
                    f"'{key}' execution_state={item.execution_state.value}, "
                    f"expected {expected.value}"
                )
            value = item.value
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                errors.append(f"'{key}' carries no numeric value")
                return Decimal(0)
            return to_decimal(value)

        def span(key: str, expected: ExecutionState) -> tuple[Decimal, Decimal]:
            item = entry(key)
            if item is None:
                return (Decimal(0), Decimal(0))
            if item.execution_state is not expected:
                errors.append(
                    f"'{key}' execution_state={item.execution_state.value}, "
                    f"expected {expected.value}"
                )
            if item.minimum is None or item.maximum is None:
                errors.append(f"'{key}' lacks a minimum/maximum range")
                return (Decimal(0), Decimal(0))
            return (to_decimal(item.minimum), to_decimal(item.maximum))

        def as_int(value: float | int | Decimal, label: str) -> int:
            if isinstance(value, bool):
                errors.append(f"{label} is not integer-coercible")
                return 0
            if isinstance(value, Decimal):
                candidate = value
            elif isinstance(value, (int, float)):
                candidate = to_decimal(value)
            else:
                errors.append(f"{label} is not integer-coercible")
                return 0
            if candidate != candidate.to_integral_value():
                errors.append(f"{label} must be integral, got {value}")
                return 0
            return int(candidate)

        supported_density = build_density_map(systems, errors)
        if not supported_density:
            errors.append("no planting-system density ranges provided")

        p_default = num("p_duck_buy_default", ExecutionState.ACTIVE)

        age_lo, age_hi = span("supported_age_window_days", ExecutionState.ACTIVE)
        high_risk = num("density_high_risk_threshold_are", ExecutionState.ACTIVE)
        limited_lo, limited_hi = span("density_limited_test_are", ExecutionState.ACTIVE)

        release_lo, release_hi = span("release_hst_window", ExecutionState.ACTIVE_RANGE)
        pull_lo, pull_hi = span("pull_hst_window", ExecutionState.ACTIVE_RANGE)
        duration_value = num("active_duration_ref_days", ExecutionState.ACTIVE_RANGE)
        duration_lo, duration_hi = span(
            "active_duration_ref_days", ExecutionState.ACTIVE_RANGE
        )

        lam = num("lambda_safe_ref", ExecutionState.CONDITIONAL)

        n_need = num("n_need_kg_per_are", ExecutionState.ACTIVE_BASELINE)
        p_need = num("p2o5_need_kg_per_are", ExecutionState.ACTIVE_BASELINE)
        k_need = num("k2o_need_kg_per_are", ExecutionState.ACTIVE_BASELINE)
        urea_frac = num("urea_n_fraction", ExecutionState.ACTIVE)
        npk_n = num("npk_n_fraction", ExecutionState.ACTIVE)
        npk_p = num("npk_p2o5_fraction", ExecutionState.ACTIVE)
        npk_k = num("npk_k2o_fraction", ExecutionState.ACTIVE)
        het_urea = num("het_urea_rp_per_kg", ExecutionState.ACTIVE_BASELINE)
        het_npk = num("het_npk_rp_per_kg", ExecutionState.ACTIVE_BASELINE)

        price_lo, price_hi = span("net_price_rp_per_m", ExecutionState.ACTIVE_RANGE)
        life_lo, life_hi = span("net_lifetime_cycles", ExecutionState.ACTIVE_RANGE)
        cage_lo, cage_hi = span(
            "cage_cost_per_unit_cycle_rp", ExecutionState.ACTIVE_RANGE
        )

        weed_lo, weed_hi = span(
            "weeding_baseline_rp_per_are", ExecutionState.ACTIVE_RANGE
        )
        pest_item = entry("pesticide_effect")
        pest_effect = ""
        if pest_item is not None:
            if pest_item.execution_state is not ExecutionState.DESCRIPTIVE:
                errors.append(
                    f"'pesticide_effect' execution_state="
                    f"{pest_item.execution_state.value}, expected DESCRIPTIVE"
                )
            if not isinstance(pest_item.value, str):
                errors.append("'pesticide_effect' carries no descriptive value")
            else:
                pest_effect = pest_item.value

        gabah = num("p_gabah_ref_rp_per_kg", ExecutionState.ACTIVE)
        terminal_ref = num(
            "duck_terminal_value_rp_per_duck", ExecutionState.CONDITIONAL
        )
        terminal_lo, terminal_hi = span(
            "duck_terminal_value_rp_per_duck", ExecutionState.CONDITIONAL
        )

        # Integer coercions MUST happen before the fail-closed gate below so
        # that any non-integral registry range aborts construction instead of
        # silently producing zero-valued calendar/age bounds.
        age_min = as_int(age_lo, "supported_age_window min")
        age_max = as_int(age_hi, "supported_age_window max")
        release_min = as_int(release_lo, "release window min")
        release_max = as_int(release_hi, "release window max")
        pull_min = as_int(pull_lo, "pull window min")
        pull_max = as_int(pull_hi, "pull window max")
        duration_ref = as_int(duration_value, "active duration ref")
        duration_min = as_int(duration_lo, "active duration min")
        duration_max = as_int(duration_hi, "active duration max")

        if errors:
            raise ValueError(
                "R2 engine configuration failed closed:\n- " + "\n- ".join(errors)
            )

        lifetime_mid = (life_lo + life_hi) / 2

        return cls(
            area_m2_per_are=ARE_TO_M2,
            p_duck_buy_default=p_default,
            age_supported_min_days=age_min,
            age_supported_max_days=age_max,
            density_high_risk_min_are=high_risk,
            density_limited_test_min_are=limited_lo,
            density_limited_test_max_are=limited_hi,
            supported_density_by_system=supported_density,
            release_hst_min=release_min,
            release_hst_max=release_max,
            pull_hst_min=pull_min,
            pull_hst_max=pull_max,
            active_duration_ref_days=duration_ref,
            active_duration_support_min_days=duration_min,
            active_duration_support_max_days=duration_max,
            # SSOT: F_RD response is evaluated at the reference release edge.
            f_rd_release_ref_hst=release_max,
            lambda_safe_ref=lam,
            n_need_kg_per_are=n_need,
            p2o5_need_kg_per_are=p_need,
            k2o_need_kg_per_are=k_need,
            urea_n_fraction=urea_frac,
            npk_n_fraction=npk_n,
            npk_p2o5_fraction=npk_p,
            npk_k2o_fraction=npk_k,
            het_urea_rp_per_kg=het_urea,
            het_npk_rp_per_kg=het_npk,
            net_price_min_rp_per_m=price_lo,
            net_price_max_rp_per_m=price_hi,
            net_lifetime_min_cycles=life_lo,
            net_lifetime_max_cycles=life_hi,
            net_lifetime_mid_cycles=lifetime_mid,
            cage_unit_min_rp_per_cycle=cage_lo,
            cage_unit_max_rp_per_cycle=cage_hi,
            cage_unit_ref_rp_per_cycle=(cage_lo + cage_hi) / 2,
            weeding_baseline_min_rp_per_are=weed_lo,
            weeding_baseline_max_rp_per_are=weed_hi,
            pesticide_effect=pest_effect,
            p_gabah_ref_rp_per_kg=gabah,
            duck_terminal_min_rp_per_duck=terminal_lo,
            duck_terminal_ref_rp_per_duck=terminal_ref,
            duck_terminal_max_rp_per_duck=terminal_hi,
        )


def build_density_map(
    systems: Iterable[PlantingSystem],
    errors: list[str],
) -> dict[str, tuple[Decimal, Decimal]]:
    mapping: dict[str, tuple[Decimal, Decimal]] = {}
    for system in systems:
        low = system.supported_density_min_are
        high = system.supported_density_max_are
        if low is None or high is None:
            errors.append(f"planting system '{system.code}' lacks density range")
            continue
        lo = to_decimal(low)
        hi = to_decimal(high)
        if lo > hi:
            errors.append(
                f"planting system '{system.code}' has inverted density range"
            )
        mapping[system.code] = (lo, hi)
    return mapping


def load_default_config() -> R2EngineConfig:
    """Production wiring: canonical seed registry + planting systems."""
    return R2EngineConfig.from_registry(PARAMETER_REGISTRY, PLANTING_SYSTEMS)
