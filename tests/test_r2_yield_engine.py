from decimal import Decimal

from app.data.seed import F_RD_REFERENCE, YIELD_BASELINES
from app.domain.models import AgeSupportFlag, AvailabilityStatus, DensitySupportFlag, LocalCultivarGroup
from app.engines.r2.normalization import normalize_inputs
from app.engines.r2.yield_engine import RANGE_TYPE, compute_yield
from app.repositories.lookup_repository import lookup_repository

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
