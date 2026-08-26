from decimal import Decimal

import pytest

from app.data.seed import F_RD_REFERENCE, YIELD_BASELINES
from app.domain.models import AgeSupportFlag, AvailabilityStatus, DensitySupportFlag, ExecutionState, LocalCultivarGroup, ProvenanceStatus, RiceVariety
from app.engines.r2.normalization import normalize_inputs
from app.engines.r2.yield_engine import RANGE_TYPE, compute_yield
from app.repositories.lookup_repository import lookup_repository
from app.services.simulation_service import dss_service
from app.schemas.dss import DSSSimulationRequest, ReasonCode

def _result(variety="inpari", age=21, count=20, area=10, system="jajar_legowo"):
    return compute_yield(variety=lookup_repository.get_rice_variety(variety),
        normalized_inputs=normalize_inputs(land_area_are=area, duck_count=count, p_duck_buy_manual=None,
        config=__import__('app.engines.r2', fromlist=['load_default_config']).load_default_config()),
        age_support=AgeSupportFlag.SUPPORTED if 21 <= age <= 30 else AgeSupportFlag.CAUTION,
        density_support=DensitySupportFlag.SUPPORTED if (system == "jajar_legowo" and 2 <= count/area <= 4) or (system == "tegel" and 2 <= count/area <= 3) else DensitySupportFlag.EXTRAPOLATION)

def test_phase6_inpari_arithmetic_and_metadata():
    r = _result("inpari")
    assert r.availability is AvailabilityStatus.AVAILABLE
    assert (r.yield_ref_kg_per_are, r.yield_low_kg_per_are, r.yield_high_kg_per_are) == (Decimal("54.998"), Decimal("20.560"), Decimal("80.5952"))
    assert r.source_id == "YB-INPARI-SULAEMAN-2024" and RANGE_TYPE == "LITERATURE_EVIDENCE_ENVELOPE"

def test_phase6_sertani_arithmetic_and_low_evidence_warning():
    r = _result("sertani")
    assert (r.yield_ref_kg_per_are, r.yield_low_kg_per_are, r.yield_high_kg_per_are) == (Decimal("45.746"), Decimal("22.9244"), Decimal("68.5676"))
    assert r.evidence_warning == "LOW_EVIDENCE_TWO_LOCATION_EXTERNAL_RANGE"

def test_phase6_area_scaling_and_fail_closed_boundaries():
    r = _result("inpari", area=7, count=14)
    assert r.yield_total_ref_kg == Decimal("384.986")
    for args in (("inpari",20,20,10,"jajar_legowo"),("inpari",31,20,10,"jajar_legowo"),("inpari",21,41,10,"jajar_legowo"),("sertani",21,31,10,"tegel")):
        assert _result(*args).availability is AvailabilityStatus.UNAVAILABLE

def test_phase6_records_are_approved_external_parameters():
    assert F_RD_REFERENCE["factor"] == 1.028
    assert YIELD_BASELINES["INPARI_GROUP"]["ref_kg_per_are"] == 53.5


def _service_yield(*, system="jajar_legowo", age=21, density=2, variety="inpari"):
    response = dss_service.simulate(DSSSimulationRequest(
        land_area_are=10, duck_count=int(10 * density), planting_date="2026-01-01",
        planting_system=system, rice_variety=variety, duck_age_days=age,
    ))
    return response.crop_yield


@pytest.mark.parametrize("system,density", [
    ("jajar_legowo", 2), ("jajar_legowo", 4), ("tegel", 2), ("tegel", 3),
])
def test_supported_density_boundaries_execute_through_service(system, density):
    assert _service_yield(system=system, density=density).availability is AvailabilityStatus.AVAILABLE


@pytest.mark.parametrize("system,density", [
    ("jajar_legowo", 1.9), ("jajar_legowo", 4.1), ("tegel", 1.9), ("tegel", 3.1),
])
def test_unsupported_density_boundaries_fail_closed_through_service(system, density):
    result = _service_yield(system=system, density=density)
    assert result.availability is AvailabilityStatus.UNAVAILABLE
    assert ReasonCode.DENSITY_OUTSIDE_SUPPORTED_DOMAIN in result.reason_codes


@pytest.mark.parametrize("age,available", [(20, False), (21, True), (30, True), (31, False)])
def test_age_boundaries_use_production_classifier_and_gate(age, available):
    result = _service_yield(age=age)
    assert (result.availability is AvailabilityStatus.AVAILABLE) is available


@pytest.mark.parametrize("density", [5, 8, 9])
def test_limited_high_risk_and_extrapolation_all_fail_closed(density):
    result = _service_yield(density=density)
    assert result.availability is AvailabilityStatus.UNAVAILABLE
    assert ReasonCode.DENSITY_OUTSIDE_SUPPORTED_DOMAIN in result.reason_codes


def test_unsupported_yield_has_null_reference_range_and_aliases():
    result = _service_yield(age=20)
    assert (result.yield_ref_kg_per_are, result.yield_low_kg_per_are,
            result.yield_high_kg_per_are, result.yield_kg_per_are) == (None, None, None, None)


def test_both_phase6_sources_are_exposed():
    result = _service_yield(variety="sertani")
    assert result.yield_baseline_source_id == "YB-SERTANI-SULAEMAN-2022"
    assert result.yield_frd_source_id == "FRD-FENG-2024"


def test_missing_baseline_fails_closed(monkeypatch):
    monkeypatch.delitem(YIELD_BASELINES, "INPARI_GROUP")
    result = _service_yield()
    assert result.availability is AvailabilityStatus.UNAVAILABLE
    assert ReasonCode.Y_BASE_GROUP_LOOKUP_MISSING in result.reason_codes


def test_missing_frd_reference_fails_closed(monkeypatch):
    monkeypatch.setattr("app.engines.r2.yield_engine.F_RD_REFERENCE", {})
    result = _service_yield()
    assert result.availability is AvailabilityStatus.UNAVAILABLE
    assert ReasonCode.FRD_REFERENCE_MISSING in result.reason_codes


def test_unresolved_cultivar_group_fails_closed():
    variety = RiceVariety(code="unknown", label="Unknown", harvest_hst_min=1, harvest_hst_max=2,
        calendar_status=ProvenanceStatus.LOCAL_ESTIMATE, yield_lookup_status=ExecutionState.ACTIVE_RANGE,
        cultivar_group_code=None)
    normalized = normalize_inputs(land_area_are=10, duck_count=20, p_duck_buy_manual=None,
        config=__import__('app.engines.r2', fromlist=['load_default_config']).load_default_config())
    result = compute_yield(variety=variety, normalized_inputs=normalized,
        age_support=AgeSupportFlag.SUPPORTED, density_support=DensitySupportFlag.SUPPORTED)
    assert result.availability is AvailabilityStatus.UNAVAILABLE
    assert ReasonCode.CULTIVAR_GROUP_UNRESOLVED in result.reason_codes
