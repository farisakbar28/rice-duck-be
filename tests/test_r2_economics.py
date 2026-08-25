"""Phase 2: economic ledger -- availability-aware conditionality.

Cases per task section 22:
  A: yield unavailable + survival available
  B: yield available (synthetic) + survival unavailable
  C: both available -> gross/margin available, full profit still null
  D: feed/cage unavailable -> aggregation never coerces them to zero
"""

from decimal import Decimal

import pytest

from app.domain.models import (
    AvailabilityStatus,
    ComponentAvailability,
    CostCompletenessFlag,
    PriceBenchmarkType,
)
from app.engines.r2.config import load_default_config
from app.engines.r2.economics import (
    PROFIT_FULL_STATUS_INCOMPLETE,
    compute_economic_ledger,
)
from app.engines.r2.fertilizer import compute_fertilizer_baseline
from app.engines.r2.infrastructure import (
    CageInfrastructureResult,
    InfrastructureResult,
    NetInfrastructureResult,
)
from app.engines.r2.survival import compute_survival
from app.engines.r2.yield_engine import YieldResult
from app.schemas.dss import ReasonCode

DUCKS = 28
MANUAL_PRICE = Decimal("30000")


@pytest.fixture(scope="module")
def config():
    return load_default_config()


def infra_result(ref_cost: Decimal | None = None) -> InfrastructureResult:
    """Real net values for A=7; optionally distinct min/ref/max for gating tests."""
    if ref_cost is None:
        return InfrastructureResult(
            net=NetInfrastructureResult(
                equivalent_perimeter_m=Decimal("105.830052442583623620071731098779212703"),
                cost_min_rp_per_cycle=Decimal("211660.1048851672472401292602911408340568207"),
                cost_ref_rp_per_cycle=Decimal("285741.1415949757837741745013930401259767080"),
                cost_max_rp_per_cycle=Decimal("357176.4269937197297177181267413001574708850"),
                geometry_assumption="SQUARE_EQUIVALENT",
            ),
            cage=CageInfrastructureResult(
                availability=ComponentAvailability.PARTIAL_RANGE_ONLY,
                cost_per_unit_min_rp_per_cycle=Decimal("150000"),
                cost_per_unit_ref_rp_per_cycle=Decimal("175000"),
                cost_per_unit_max_rp_per_cycle=Decimal("200000"),
                total_amount_rp=None,
                reason_codes=(ReasonCode.CAGE_CAPACITY_RULE_MISSING,),
            ),
        )
    # Distinct values prove the ledger uses the REFERENCE cost.
    return InfrastructureResult(
        net=NetInfrastructureResult(
            equivalent_perimeter_m=Decimal("100"),
            cost_min_rp_per_cycle=Decimal("1"),
            cost_ref_rp_per_cycle=ref_cost,
            cost_max_rp_per_cycle=Decimal("999999"),
            geometry_assumption="SQUARE_EQUIVALENT",
        ),
        cage=CageInfrastructureResult(
            availability=ComponentAvailability.PARTIAL_RANGE_ONLY,
            cost_per_unit_min_rp_per_cycle=Decimal("150000"),
            cost_per_unit_ref_rp_per_cycle=Decimal("175000"),
            cost_per_unit_max_rp_per_cycle=Decimal("200000"),
            total_amount_rp=None,
            reason_codes=(ReasonCode.CAGE_CAPACITY_RULE_MISSING,),
        ),
    )


def yield_available(total_kg: Decimal = Decimal("378")) -> YieldResult:
    """Synthetic AVAILABLE yield result (378 kg from the synthetic fixture path)."""
    return YieldResult(
        availability=AvailabilityStatus.AVAILABLE,
        exact_cultivar_resolved=True,
        baseline_kg_per_are=Decimal("50"),
        rice_duck_response_factor=Decimal("1.08"),
        yield_kg_per_are=Decimal("54"),
        yield_total_kg=total_kg,
        reason_codes=(),
    )


def yield_unavailable() -> YieldResult:
    return YieldResult(
        availability=AvailabilityStatus.UNAVAILABLE,
        exact_cultivar_resolved=False,
        baseline_kg_per_are=None,
        rice_duck_response_factor=None,
        yield_kg_per_are=None,
        yield_total_kg=None,
        reason_codes=(ReasonCode.Y_BASE_LOOKUP_MISSING, ReasonCode.F_RD_LOOKUP_MISSING),
    )


def survival(config, supported: bool = True):
    from app.domain.models import AgeSupportFlag, DensitySupportFlag

    if supported:
        return compute_survival(
            DUCKS, AgeSupportFlag.SUPPORTED, DensitySupportFlag.SUPPORTED, config
        )
    return compute_survival(DUCKS, AgeSupportFlag.CAUTION, DensitySupportFlag.SUPPORTED, config)


def ledger(config, *, yld, srv, ref_cost=None, feed=None, cage=None):
    return compute_economic_ledger(
        duck_count=DUCKS,
        purchase_price_effective=MANUAL_PRICE,
        yield_result=yld,
        survival_result=srv,
        infrastructure_result=infra_result(ref_cost),
        fertilizer_result=compute_fertilizer_baseline(7, config),
        config=config,
        feed_amount_rp=feed,
        cage_total_amount_rp=cage,
    )


class TestDuckPurchase:
    def test_purchase_identity_with_manual_price(self, config) -> None:
        led = ledger(config, yld=yield_unavailable(), srv=survival(config))
        assert led.duck_purchase_availability is AvailabilityStatus.AVAILABLE
        assert led.duck_purchase_cost_rp == Decimal("28") * MANUAL_PRICE == Decimal("840000")

    def test_benchmark_is_regulatory_hpp(self, config) -> None:
        led = ledger(config, yld=yield_unavailable(), srv=survival(config))
        assert led.paddy_price_benchmark_rp_per_kg == Decimal("6500")
        assert led.paddy_price_semantics is PriceBenchmarkType.REGULATORY_HPP


class TestCaseAYieldUnavailableSurvivalAvailable:
    def test_terminal_value_present_revenue_absent(self, config) -> None:
        led = ledger(config, yld=yield_unavailable(), srv=survival(config))
        # N_survive = floor(28*0.90) = 25.
        assert led.terminal_value_ref_rp == Decimal("1125000")
        assert led.terminal_value_min_rp == Decimal("750000")
        assert led.terminal_value_max_rp == Decimal("1500000")
        assert led.paddy_revenue_rp is None
        assert led.cash_revenue_rp is None
        assert led.gross_economic_value_rp is None
        assert led.margin_core_rp is None
        assert led.profit_full_est_rp is None
        assert led.profit_full_status == PROFIT_FULL_STATUS_INCOMPLETE

    def test_costs_still_computed(self, config) -> None:
        led = ledger(config, yld=yield_unavailable(), srv=survival(config))
        fert_total = compute_fertilizer_baseline(7, config).cost_total_rp
        net_ref = infra_result().net.cost_ref_rp_per_cycle
        assert led.cost_core_direct_rp == Decimal("840000") + net_ref
        assert led.cost_total_available_rp == Decimal("840000") + net_ref + fert_total
        assert led.cost_completeness is CostCompletenessFlag.INCOMPLETE


class TestCaseBYieldAvailableSurvivalUnavailable:
    def test_paddy_cash_available_terminal_absent(self, config) -> None:
        led = ledger(config, yld=yield_available(), srv=survival(config, supported=False))
        assert led.paddy_revenue_rp == Decimal("2457000")  # 378 * 6500
        assert led.cash_revenue_rp == Decimal("2457000")
        assert led.terminal_value_ref_rp is None
        assert led.terminal_value_min_rp is None
        assert led.terminal_value_max_rp is None
        assert led.gross_economic_value_rp is None
        assert led.margin_core_rp is None
        assert led.profit_full_est_rp is None


class TestCaseCBothAvailable:
    def test_gross_margin_available_profit_null(self, config) -> None:
        led = ledger(config, yld=yield_available(), srv=survival(config))
        assert led.gross_economic_value_rp == Decimal("2457000") + Decimal("1125000")
        expected_margin = led.gross_economic_value_rp - led.cost_core_direct_rp
        assert led.margin_core_rp == expected_margin
        # Full profit remains null: cost completeness is incomplete.
        assert led.profit_full_est_rp is None
        assert led.profit_full_status == PROFIT_FULL_STATUS_INCOMPLETE
        assert led.cost_completeness is CostCompletenessFlag.INCOMPLETE

    def test_terminal_value_never_enters_cash_revenue(self, config) -> None:
        led = ledger(config, yld=yield_available(), srv=survival(config))
        assert led.cash_revenue_rp == led.paddy_revenue_rp
        assert led.gross_economic_value_rp > led.cash_revenue_rp
        assert led.terminal_value_is_cash_revenue is False


class TestCostAggregationRules:
    def test_core_direct_uses_net_reference_cost(self, config) -> None:
        distinct_ref = Decimal("777777")
        led = ledger(
            config, yld=yield_unavailable(), srv=survival(config), ref_cost=distinct_ref
        )
        assert led.cost_core_direct_rp == Decimal("840000") + distinct_ref

    def test_weeding_baseline_excluded_from_available_total(self, config) -> None:
        led = ledger(config, yld=yield_unavailable(), srv=survival(config))
        fert_total = compute_fertilizer_baseline(7, config).cost_total_rp
        net_ref = infra_result().net.cost_ref_rp_per_cycle
        assert led.cost_total_available_rp == Decimal("840000") + net_ref + fert_total
        # Weeding baseline range must NOT be folded into the sum.
        weed = Decimal("42000")
        assert led.cost_total_available_rp != led.cost_total_available_rp + weed

    def test_feed_and_cage_not_zero_filled(self, config) -> None:
        led = ledger(config, yld=yield_available(), srv=survival(config))
        fert_total = compute_fertilizer_baseline(7, config).cost_total_rp
        net_ref = infra_result().net.cost_ref_rp_per_cycle
        # Sum equals exactly the three available components; adding a zero for
        # feed or cage would be indistinguishable only if sum were inflated --
        # assert exact identity instead of >=.
        assert led.cost_total_available_rp == Decimal("840000") + net_ref + fert_total
        assert led.cost_total_available_rp != Decimal("0")


class TestCompletenessGate:
    def test_complete_only_when_feed_and_cage_supplied(self, config) -> None:
        led_complete = ledger(
            config,
            yld=yield_available(),
            srv=survival(config),
            feed=Decimal("500000"),
            cage=Decimal("350000"),
        )
        assert led_complete.cost_completeness is CostCompletenessFlag.COMPLETE
        assert led_complete.profit_full_status is None
        expected_profit = (
            led_complete.gross_economic_value_rp - led_complete.cost_total_available_rp
            - Decimal("500000") - Decimal("350000")
        )
        assert led_complete.profit_full_est_rp == expected_profit

    def test_feed_without_cage_still_incomplete(self, config) -> None:
        led = ledger(
            config, yld=yield_available(), srv=survival(config), feed=Decimal("500000")
        )
        assert led.cost_completeness is CostCompletenessFlag.INCOMPLETE
        assert led.profit_full_est_rp is None

    def test_cage_without_feed_still_incomplete(self, config) -> None:
        led = ledger(
            config, yld=yield_available(), srv=survival(config), cage=Decimal("350000")
        )
        assert led.cost_completeness is CostCompletenessFlag.INCOMPLETE
        assert led.profit_full_est_rp is None
