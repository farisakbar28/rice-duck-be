"""Phase 2: infrastructure engine -- perimeter and net/cage cost ranges.

Reference case A=7 are, computed by hand:
    L     = 4 * sqrt(700) = 105.8300524425836236200717...
    min   = L * 6000/3    = 211,660.10488516724724012926029114083405682
    ref   = L * 6750/2.5  = 285,741.14159497578377417450139304012597671
    max   = L * 6750/2    = 357,176.42699371972971771812674130015747088
"""

from decimal import Decimal

import pytest

from app.domain.models import ComponentAvailability
from app.engines.r2.config import load_default_config
from app.engines.r2.infrastructure import GEOMETRY_ASSUMPTION, compute_infrastructure
from app.schemas.dss import ReasonCode


@pytest.fixture(scope="module")
def config():
    return load_default_config()


def infra(area, config):
    return compute_infrastructure(area, config)


class TestEquivalentPerimeter:
    def test_area_seven(self, config) -> None:
        # 4*sqrt(700) = 40*sqrt(7); digits independently verifiable.
        result = infra(7, config)
        expected = Decimal("105.83005244258362362006463014557041702841036732")
        assert abs(result.net.equivalent_perimeter_m - expected) < Decimal("1e-41")

    def test_area_one(self, config) -> None:
        # 4 * sqrt(100) = 40 exactly.
        assert infra(1, config).net.equivalent_perimeter_m == Decimal("40")


class TestNetCostRange:
    def test_area_seven_independent_literals(self, config) -> None:
        net = infra(7, config).net
        assert abs(net.cost_min_rp_per_cycle - Decimal("211660.104885167247")) < Decimal("1e-9")
        assert abs(net.cost_ref_rp_per_cycle - Decimal("285741.141594975784")) < Decimal("1e-9")
        assert abs(net.cost_max_rp_per_cycle - Decimal("357176.426993719730")) < Decimal("1e-9")

    def test_reference_uses_max_price_over_lifetime_midpoint(self, config) -> None:
        """Independent recomputation via a different arithmetic route."""
        net = infra(7, config).net
        l_net = net.equivalent_perimeter_m
        expected_ref = (l_net * Decimal("6750")) / Decimal("2.5")
        assert abs(net.cost_ref_rp_per_cycle - expected_ref) < Decimal("1e-23")

    def test_monotonic_range_across_areas(self, config) -> None:
        for area in ("0.5", "1", "7", "13.37", "50", "100"):
            net = infra(area, config).net
            assert net.cost_min_rp_per_cycle <= net.cost_ref_rp_per_cycle
            assert net.cost_ref_rp_per_cycle <= net.cost_max_rp_per_cycle

    def test_geometry_assumption_label(self, config) -> None:
        net = infra(7, config).net
        assert net.geometry_assumption == "SQUARE_EQUIVALENT"
        assert GEOMETRY_ASSUMPTION == "SQUARE_EQUIVALENT"


class TestCagePartialAvailability:
    def test_per_unit_range_and_derived_reference(self, config) -> None:
        cage = infra(7, config).cage
        assert cage.availability is ComponentAvailability.PARTIAL_RANGE_ONLY
        assert cage.cost_per_unit_min_rp_per_cycle == Decimal("150000")
        assert cage.cost_per_unit_ref_rp_per_cycle == Decimal("175000")
        assert cage.cost_per_unit_max_rp_per_cycle == Decimal("200000")

    def test_total_is_none_with_capacity_reason(self, config) -> None:
        cage = infra(7, config).cage
        assert cage.total_amount_rp is None
        assert cage.reason_codes == (ReasonCode.CAGE_CAPACITY_RULE_MISSING,)

    def test_total_never_scales_with_area(self, config) -> None:
        """No inferred unit count: total stays None for any area."""
        for area in ("1", "7", "100"):
            assert infra(area, config).cage.total_amount_rp is None


class TestResultStructure:
    def test_wrapper_groups(self, config) -> None:
        result = infra(7, config)
        assert hasattr(result, "net") and hasattr(result, "cage")
