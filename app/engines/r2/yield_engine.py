"""Phase-6 R2 yield engine: supported-domain global external reference only."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.data.seed import F_RD_REFERENCE, YIELD_BASELINES
from app.domain.models import AgeSupportFlag, AvailabilityStatus, DensitySupportFlag, LocalCultivarGroup, RiceVariety
from app.engines.r2.common import high_precision, to_decimal
from app.engines.r2.normalization import NormalizedInputs
from app.schemas.dss import ReasonCode

RANGE_TYPE = "LITERATURE_EVIDENCE_ENVELOPE"

@dataclass(frozen=True)
class YieldResult:
    availability: AvailabilityStatus
    cultivar_group_code: LocalCultivarGroup | None
    cultivar_group_resolved: bool
    baseline_ref_kg_per_are: Decimal | None = None
    baseline_low_kg_per_are: Decimal | None = None
    baseline_high_kg_per_are: Decimal | None = None
    rice_duck_response_factor: Decimal | None = None
    yield_ref_kg_per_are: Decimal | None = None
    yield_low_kg_per_are: Decimal | None = None
    yield_high_kg_per_are: Decimal | None = None
    yield_total_ref_kg: Decimal | None = None
    yield_total_low_kg: Decimal | None = None
    yield_total_high_kg: Decimal | None = None
    source_id: str | None = None
    baseline_source_id: str | None = None
    frd_source_id: str | None = None
    evidence_strength: str | None = None
    evidence_warning: str | None = None
    reason_codes: tuple[ReasonCode, ...] = ()

    @property
    def yield_kg_per_are(self): return self.yield_ref_kg_per_are
    @property
    def yield_total_kg(self): return self.yield_total_ref_kg

def compute_yield(*, variety: RiceVariety | None, normalized_inputs: NormalizedInputs,
                  age_support: AgeSupportFlag, density_support: DensitySupportFlag) -> YieldResult:
    group = variety.cultivar_group_code if variety else None
    reasons: list[ReasonCode] = []
    if group is None: reasons.append(ReasonCode.CULTIVAR_GROUP_UNRESOLVED)
    record = YIELD_BASELINES.get(group.value) if group else None
    if record is None: reasons.append(ReasonCode.Y_BASE_GROUP_LOOKUP_MISSING)
    if age_support is not AgeSupportFlag.SUPPORTED: reasons.append(ReasonCode.AGE_OUTSIDE_SUPPORTED_DOMAIN)
    if density_support is not DensitySupportFlag.SUPPORTED: reasons.append(ReasonCode.DENSITY_OUTSIDE_SUPPORTED_DOMAIN)
    if not F_RD_REFERENCE: reasons.append(ReasonCode.FRD_REFERENCE_MISSING)
    if reasons:
        return YieldResult(AvailabilityStatus.UNAVAILABLE, group, group is not None, reason_codes=tuple(reasons))
    factor = to_decimal(F_RD_REFERENCE["factor"])
    ref, low, high = (to_decimal(record[k]) for k in ("ref_kg_per_are", "low_kg_per_are", "high_kg_per_are"))
    with high_precision():
        yr, yl, yh = ref * factor, low * factor, high * factor
        area = to_decimal(normalized_inputs.land_area_are)
        tr, tl, th = yr * area, yl * area, yh * area
    return YieldResult(AvailabilityStatus.AVAILABLE, group, True, ref, low, high, factor, yr, yl, yh, tr, tl, th,
                       record["source_id"], record["source_id"], F_RD_REFERENCE["source_id"],
                       record["evidence_strength"], record["warning"])
