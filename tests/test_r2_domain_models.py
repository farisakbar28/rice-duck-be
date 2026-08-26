"""Phase 1: R2 domain model structures.

Provenance status and execution state are separate, closed vocabularies.
Active lookup types carry no invalidated defaults; legacy v1-v3 history
dataclasses remain byte-compatible but clearly NON-R2.
"""

import dataclasses
from datetime import datetime

import pytest

from app.domain.models import (
    AgeSupportFlag,
    AvailabilityStatus,
    ComponentAvailability,
    CostCompletenessFlag,
    DensitySupportFlag,
    ExecutionState,
    ExtrapolationFlag,
    ParameterMetadata,
    PlantingSystem,
    PriceBenchmarkType,
    ProvenanceStatus,
    PurchasePriceSource,
    RiceVariety,
    SimulationHistory,
)


class TestCanonicalEnums:
    def test_provenance_status_is_exactly_canonical_set(self) -> None:
        assert {s.value for s in ProvenanceStatus} == {
            "local-calibrated",
            "local-estimate",
            "literature-uncalibrated",
            "system-design",
            "regulatory-locked",
            "mixed",
        }

    def test_execution_state_is_exactly_canonical_set(self) -> None:
        assert {s.value for s in ExecutionState} == {
            "ACTIVE",
            "ACTIVE_RANGE",
            "ACTIVE_BASELINE",
            "CONDITIONAL",
            "PENDING_LOOKUP",
            "UNAVAILABLE",
            "DESCRIPTIVE",
            "NON_EXECUTABLE_LEGACY",
        }

    @pytest.mark.parametrize(
        "banned",
        [
            "local-validated",
            "local-calculated",
            "local-empirical-reference",
            "locked",
            "hardware-locked",
            "system-neutral-SoT",
            "estimation",
            "partial",
        ],
    )
    def test_banned_labels_are_not_members(self, banned: str) -> None:
        assert banned not in {s.value for s in ProvenanceStatus}

    def test_support_and_availability_vocabularies(self) -> None:
        assert {f.value for f in AgeSupportFlag} == {
            "CAUTION",
            "SUPPORTED",
            "OUTSIDE_LOCAL_RANGE",
        }
        assert {f.value for f in DensitySupportFlag} == {
            "SUPPORTED",
            "LIMITED_TEST",
            "HIGH_RISK",
            "EXTRAPOLATION",
        }
        assert {a.value for a in AvailabilityStatus} == {"AVAILABLE", "UNAVAILABLE"}
        assert {c.value for c in CostCompletenessFlag} == {"COMPLETE", "INCOMPLETE"}
        assert {e.value for e in ExtrapolationFlag} == {"IN_DOMAIN", "OUT_OF_DOMAIN"}
        assert {p.value for p in PriceBenchmarkType} == {"REGULATORY_HPP"}
        assert {s.value for s in PurchasePriceSource} == {
            "USER_INPUT",
            "LOCAL_DEFAULT_MIDPOINT",
        }
        assert {c.value for c in ComponentAvailability} == {
            "AVAILABLE",
            "AVAILABLE_RANGE",
            "PARTIAL_RANGE_ONLY",
            "BASELINE_RANGE_ONLY",
            "UNAVAILABLE",
        }


class TestRiceVarietyShape:
    EXPECTED_FIELDS = {
        "code",
        "label",
        "harvest_hst_min",
        "harvest_hst_max",
        "calendar_status",
        "yield_lookup_status",
        "note",
        "exact_cultivar_code",
    }

    def test_no_legacy_calendar_alias_fields(self) -> None:
        names = {f.name for f in dataclasses.fields(RiceVariety)}
        assert names == self.EXPECTED_FIELDS
        for banned in (
            "hst_panen",
            "hst_masuk",
            "hst_heading",
            "harvest_age_days",
            "hst_masuk_min",
            "hst_masuk_max",
            "hst_heading_min",
            "hst_heading_max",
        ):
            assert banned not in names

    def test_variety_is_frozen(self) -> None:
        variety = RiceVariety(
            code="sertani",
            label="Sertani / Seratih",
            harvest_hst_min=100,
            harvest_hst_max=110,
            calendar_status=ProvenanceStatus.LOCAL_ESTIMATE,
            yield_lookup_status=ExecutionState.PENDING_LOOKUP,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            variety.harvest_hst_min = 109  # type: ignore[misc]


class TestPlantingSystemShape:
    EXPECTED_FIELDS = {
        "code",
        "label",
        "supported_density_min_are",
        "supported_density_max_are",
        "status",
        "note",
    }

    def test_no_yield_factor_or_penalty_fields(self) -> None:
        names = {f.name for f in dataclasses.fields(PlantingSystem)}
        assert names == self.EXPECTED_FIELDS
        for banned in (
            "f_yield",
            "k_safe_are",
            "k_max_are",
            "penalty_rate",
            "f_yield_status",
            "system_yield_factor",
        ):
            assert banned not in names

    def test_system_is_frozen(self) -> None:
        system = PlantingSystem(
            code="tegel",
            label="Tegel",
            supported_density_min_are=2.0,
            supported_density_max_are=3.0,
            status=ProvenanceStatus.LOCAL_ESTIMATE,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            system.supported_density_max_are = 8.0  # type: ignore[misc]


class TestParameterMetadata:
    def _meta(self, **overrides: object) -> ParameterMetadata:
        kwargs: dict = {
            "key": "k",
            "value": 1.0,
            "unit": "x",
            "status_tag": ProvenanceStatus.LOCAL_ESTIMATE,
            "execution_state": ExecutionState.ACTIVE,
            "source_ids": ("I1",),
            "model_version": "R2",
            "effective_from": "2026-08-26",
        }
        kwargs.update(overrides)
        return ParameterMetadata(**kwargs)  # type: ignore[arg-type]

    def test_pending_lookup_must_not_carry_numeric_value(self) -> None:
        with pytest.raises(ValueError):
            self._meta(execution_state=ExecutionState.PENDING_LOOKUP)

    def test_unavailable_must_not_carry_numeric_value(self) -> None:
        with pytest.raises(ValueError):
            self._meta(execution_state=ExecutionState.UNAVAILABLE)

    def test_pending_lookup_allows_none_value(self) -> None:
        meta = self._meta(
            execution_state=ExecutionState.PENDING_LOOKUP,
            value=None,
        )
        assert meta.value is None

    def test_metadata_is_frozen(self) -> None:
        meta = self._meta()
        with pytest.raises(dataclasses.FrozenInstanceError):
            meta.value = 2.0  # type: ignore[misc]


class TestLegacyHistorySeparation:
    def test_v3_history_model_unchanged_and_non_r2(self) -> None:
        names = {f.name for f in dataclasses.fields(SimulationHistory)}
        # v3 columns preserved for read compatibility...
        for legacy_field in (
            "net_cash_contribution_dss",
            "revenue_duck_potential",
            "cost_feed",
            "yield_are_pred",
            "hst_in",
            "hst_out",
        ):
            assert legacy_field in names
        # ...but the type carries no R2 marker fields that services could mistake
        # for canonical semantics (no availability/provenance members).
        assert "availability" not in names
        assert "provenance" not in names

    def test_user_infrastructure_untouched(self) -> None:
        from app.domain.models import AuthContext, User

        user = User(
            id="u1",
            name="n",
            email="e@example.com",
            password_hash="h",
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1),
        )
        assert AuthContext(user=user).user is user
