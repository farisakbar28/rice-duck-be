"""Phase 1: R2 seed / parameter registry content.

Locks the approved R2 values (docs/01 SSOT, docs/04 registry,
docs/10 provenance map) and the fail-closed representation of unresolved
quantities: PENDING_LOOKUP / UNAVAILABLE entries carry value None.
"""

import dataclasses

import pytest

from app.data.seed import (
    EFFECTIVE_FROM,
    MODEL_VERSION,
    PARAMETER_REGISTRY,
    PLANTING_SYSTEMS,
    RICE_VARIETIES,
)
from app.domain.models import ExecutionState, ParameterMetadata, ProvenanceStatus


def variety(code: str):
    return next(v for v in RICE_VARIETIES if v.code == code)


def system(code: str):
    return next(s for s in PLANTING_SYSTEMS if s.code == code)


class TestVarietySeed:
    def test_exactly_two_varieties(self) -> None:
        assert {v.code for v in RICE_VARIETIES} == {"sertani", "inpari"}

    def test_sertani_window(self) -> None:
        v = variety("sertani")
        assert (v.harvest_hst_min, v.harvest_hst_max) == (100, 110)
        assert v.calendar_status is ProvenanceStatus.LOCAL_ESTIMATE
        assert v.yield_lookup_status is ExecutionState.PENDING_LOOKUP

    def test_inpari_window_is_90_100_not_109_116(self) -> None:
        v = variety("inpari")
        assert (v.harvest_hst_min, v.harvest_hst_max) == (90, 100)
        assert (109, 116) != (v.harvest_hst_min, v.harvest_hst_max)
        assert v.calendar_status is ProvenanceStatus.LOCAL_ESTIMATE
        assert v.yield_lookup_status is ExecutionState.PENDING_LOOKUP

    def test_no_numeric_yield_baseline_attached(self) -> None:
        for v in RICE_VARIETIES:
            names = {f.name for f in dataclasses.fields(v)}
            assert not any("baseline" in n or "yield_base" in n for n in names)


class TestPlantingSystemSeed:
    def test_jarwo_supported_density_2_4(self) -> None:
        s = system("jajar_legowo")
        assert (s.supported_density_min_are, s.supported_density_max_are) == (2.0, 4.0)
        assert s.status is ProvenanceStatus.LOCAL_ESTIMATE

    def test_tegel_supported_density_2_3(self) -> None:
        s = system("tegel")
        assert (s.supported_density_min_are, s.supported_density_max_are) == (2.0, 3.0)
        assert s.status is ProvenanceStatus.LOCAL_ESTIMATE


class TestRegistryApprovedValues:
    def test_purchase_default_26500_mixed_active(self) -> None:
        p = PARAMETER_REGISTRY["p_duck_buy_default"]
        assert p.value == 26500
        assert p.unit == "Rp/duck"
        assert p.status_tag is ProvenanceStatus.MIXED
        assert p.execution_state is ExecutionState.ACTIVE
        assert p.source_ids == ("I1",)

    def test_purchase_local_range_25000_28000(self) -> None:
        p = PARAMETER_REGISTRY["p_duck_buy_local_range"]
        assert p.value is None
        assert (p.minimum, p.maximum) == (25000, 28000)
        assert p.execution_state is ExecutionState.ACTIVE_RANGE

    def test_release_pull_windows(self) -> None:
        release = PARAMETER_REGISTRY["release_hst_window"]
        pull = PARAMETER_REGISTRY["pull_hst_window"]
        assert (release.minimum, release.maximum) == (21, 30)
        assert (pull.minimum, pull.maximum) == (56, 60)

    def test_active_duration_ref_32_support_28_40(self) -> None:
        p = PARAMETER_REGISTRY["active_duration_ref_days"]
        assert p.value == 32
        assert (p.minimum, p.maximum) == (28, 40)
        assert p.execution_state is ExecutionState.ACTIVE_RANGE

    def test_survival_reference_conditional_never_unconditional(self) -> None:
        p = PARAMETER_REGISTRY["lambda_safe_ref"]
        assert p.value == 0.90
        assert p.execution_state is ExecutionState.CONDITIONAL
        assert p.status_tag is ProvenanceStatus.LOCAL_ESTIMATE

    def test_grain_hpp_6500_regulatory_locked(self) -> None:
        p = PARAMETER_REGISTRY["p_gabah_ref_rp_per_kg"]
        assert p.value == 6500
        assert p.status_tag is ProvenanceStatus.REGULATORY_LOCKED
        assert p.execution_state is ExecutionState.ACTIVE

    def test_nutrient_baseline_coefficients(self) -> None:
        assert PARAMETER_REGISTRY["n_need_kg_per_are"].value == pytest.approx(1.1761)
        assert PARAMETER_REGISTRY["p2o5_need_kg_per_are"].value == pytest.approx(0.2745)
        assert PARAMETER_REGISTRY["k2o_need_kg_per_are"].value == pytest.approx(0.2745)
        for key in ("n_need_kg_per_are", "p2o5_need_kg_per_are", "k2o_need_kg_per_are"):
            entry = PARAMETER_REGISTRY[key]
            assert entry.status_tag is ProvenanceStatus.LITERATURE_UNCALIBRATED
            assert entry.execution_state is ExecutionState.ACTIVE_BASELINE

    def test_fertilizer_hets_and_compositions(self) -> None:
        urea = PARAMETER_REGISTRY["het_urea_rp_per_kg"]
        npk = PARAMETER_REGISTRY["het_npk_rp_per_kg"]
        assert urea.value == 1800 and npk.value == 1840
        for entry in (urea, npk):
            assert entry.status_tag is ProvenanceStatus.REGULATORY_LOCKED
            assert entry.source_ids == ("O2",)
        assert PARAMETER_REGISTRY["urea_n_fraction"].value == pytest.approx(0.46)
        assert PARAMETER_REGISTRY["npk_n_fraction"].value == pytest.approx(0.15)
        assert PARAMETER_REGISTRY["npk_p2o5_fraction"].value == pytest.approx(0.10)
        assert PARAMETER_REGISTRY["npk_k2o_fraction"].value == pytest.approx(0.12)

    def test_terminal_duck_value_is_conditional_and_flagged_non_cash(self) -> None:
        p = PARAMETER_REGISTRY["duck_terminal_value_rp_per_duck"]
        assert p.value == 45000
        assert (p.minimum, p.maximum) == (30000, 60000)
        assert p.execution_state is ExecutionState.CONDITIONAL


class TestFailClosedPendingEntries:
    @pytest.mark.parametrize(
        "key",
        [
            "yield_base_by_cultivar_group",
            "f_rd_lookup",
        ],
    )
    def test_pending_lookups_have_no_numeric_fallback(self, key: str) -> None:
        p = PARAMETER_REGISTRY[key]
        assert p.value is None
        assert p.execution_state is ExecutionState.PENDING_LOOKUP

    @pytest.mark.parametrize(
        "key",
        [
            "feed_quantity_lookup",
            "feed_price_lookup",
            "cage_capacity_rule",
            "manure_nutrient_credit",
            "weeding_saving_conversion",
            "pesticide_saving_conversion",
            "kcl_branch",
        ],
    )
    def test_unavailable_entries_have_no_numeric_fallback(self, key: str) -> None:
        p = PARAMETER_REGISTRY[key]
        assert p.value is None
        assert p.execution_state is ExecutionState.UNAVAILABLE

    def test_feed_has_no_fixed_active_value(self) -> None:
        """No active/active-range feed cost parameter may exist."""
        offenders = [
            k
            for k, p in PARAMETER_REGISTRY.items()
            if "feed" in k
            and p.value is not None
            and p.execution_state
            in (
                ExecutionState.ACTIVE,
                ExecutionState.ACTIVE_RANGE,
                ExecutionState.ACTIVE_BASELINE,
            )
        ]
        assert offenders == []

    def test_kcl_not_regulatory_locked_9500(self) -> None:
        p = PARAMETER_REGISTRY["kcl_branch"]
        assert p.value is None
        assert p.status_tag is not ProvenanceStatus.REGULATORY_LOCKED


class TestRegistryIntegrity:
    def test_every_entry_has_full_metadata(self) -> None:
        assert PARAMETER_REGISTRY, "registry must not be empty"
        for key, p in PARAMETER_REGISTRY.items():
            assert isinstance(p, ParameterMetadata)
            assert p.key == key
            assert isinstance(p.status_tag, ProvenanceStatus)
            assert isinstance(p.execution_state, ExecutionState)
            assert isinstance(p.source_ids, tuple)
            assert p.model_version == MODEL_VERSION == "R2"
            assert p.effective_from == EFFECTIVE_FROM

    def test_provenance_values_within_canonical_enum(self) -> None:
        canonical = {s.value for s in ProvenanceStatus}
        assert all(p.status_tag.value in canonical for p in PARAMETER_REGISTRY.values())

    def test_execution_states_within_canonical_enum(self) -> None:
        canonical = {s.value for s in ExecutionState}
        assert all(
            p.execution_state.value in canonical for p in PARAMETER_REGISTRY.values()
        )

    def test_no_legacy_status_labels_anywhere(self) -> None:
        banned = {
            "local-validated",
            "local-calculated",
            "local-empirical-reference",
            "locked",
            "hardware-locked",
            "system-neutral-SoT",
            "estimation",
            "partial",
        }
        for key, p in PARAMETER_REGISTRY.items():
            assert p.status_tag.value not in banned
            # notes may mention banned historical labels only as invalidation context;
            # they must never be the status itself.
            assert p.status_tag is not None
