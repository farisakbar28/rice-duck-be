"""R2 economic ledger engine -- availability-aware, conditional.

Ledger rules (SSOT sections 8, 12, 13; registry R2-COST-01, R2-GRAIN-01/02,
R2-DUCKVAL-01, R2-LEDGER-01..06):

    C_duck_buy          = J * p_duck_buy_eff                    (always available)
    Revenue_gabah       = Yield_total * p_gabah_ref             (yield available only)
    V_duck_end          = N_survive * {30k, 45k, 60k}           (survival available only)
    CashRevenue         = Revenue_gabah                         (terminal value is NOT cash)
    GrossEconomicValue  = Revenue_gabah + V_duck_end_ref        (both available only)
    Cost_core_direct    = C_duck_buy + C_net_cycle_ref
    Cost_total_available= sum of numerically AVAILABLE cost components only
                          (duck purchase + net reference + fertilizer baseline);
                          unavailable feed/cage-total are never coerced to zero.
    CostCompletenessFlag= COMPLETE only if every component required by the full
                          configured ledger is available; currently INCOMPLETE
                          because feed amount and cage total remain unavailable.
    Margin_core         = GrossEconomicValue - Cost_core_direct (both available only)
    Profit_full_est     = numeric ONLY if completeness is COMPLETE.

``Margin_core`` is a core margin, never labeled net profit. The terminal duck
value is a livestock asset value, never realized sale revenue.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.domain.models import (
    AvailabilityStatus,
    CostCompletenessFlag,
    PriceBenchmarkType,
)
from app.engines.r2.common import to_decimal
from app.engines.r2.config import R2EngineConfig
from app.engines.r2.fertilizer import FertilizerResult
from app.engines.r2.infrastructure import InfrastructureResult
from app.engines.r2.survival import SurvivalResult
from app.engines.r2.yield_engine import YieldResult

PROFIT_FULL_STATUS_INCOMPLETE = "UNAVAILABLE_INCOMPLETE_COST"


@dataclass(frozen=True)
class EconomicLedgerResult:
    duck_purchase_availability: AvailabilityStatus
    duck_purchase_cost_rp: Decimal

    paddy_price_benchmark_rp_per_kg: Decimal
    paddy_price_semantics: PriceBenchmarkType

    paddy_revenue_rp: Decimal | None
    cash_revenue_rp: Decimal | None

    terminal_value_min_rp: Decimal | None
    terminal_value_ref_rp: Decimal | None
    terminal_value_max_rp: Decimal | None
    terminal_value_is_cash_revenue: bool

    gross_economic_value_rp: Decimal | None

    cost_core_direct_rp: Decimal
    cost_total_available_rp: Decimal
    cost_completeness: CostCompletenessFlag

    margin_core_rp: Decimal | None
    profit_full_est_rp: Decimal | None
    profit_full_status: str | None


def compute_economic_ledger(
    *,
    duck_count: int,
    purchase_price_effective: Decimal | float | int | str,
    yield_result: YieldResult,
    survival_result: SurvivalResult,
    infrastructure_result: InfrastructureResult,
    fertilizer_result: FertilizerResult,
    config: R2EngineConfig,
    feed_amount_rp: Decimal | None = None,
    cage_total_amount_rp: Decimal | None = None,
) -> EconomicLedgerResult:
    price = to_decimal(purchase_price_effective)
    duck_buy = to_decimal(int(duck_count)) * price

    yield_available = (
        yield_result.availability is AvailabilityStatus.AVAILABLE
        and yield_result.yield_total_kg is not None
    )
    survival_available = (
        survival_result.availability is AvailabilityStatus.AVAILABLE
        and survival_result.surviving_ducks is not None
    )

    # Paddy revenue -- regulatory HPP benchmark applied to yield only when
    # the yield engine itself reports availability.
    paddy_revenue: Decimal | None = None
    if yield_available:
        paddy_revenue = (
            to_decimal(yield_result.yield_total_kg) * config.p_gabah_ref_rp_per_kg
        )
    cash_revenue = paddy_revenue

    # Terminal duck value -- asset value with sensitivity band; not cash revenue.
    terminal_min: Decimal | None = None
    terminal_ref: Decimal | None = None
    terminal_max: Decimal | None = None
    if survival_available:
        survivors = to_decimal(survival_result.surviving_ducks)
        terminal_min = survivors * config.duck_terminal_min_rp_per_duck
        terminal_ref = survivors * config.duck_terminal_ref_rp_per_duck
        terminal_max = survivors * config.duck_terminal_max_rp_per_duck

    gross_economic_value: Decimal | None = None
    if paddy_revenue is not None and terminal_ref is not None:
        gross_economic_value = paddy_revenue + terminal_ref

    net_ref_cost = infrastructure_result.net.cost_ref_rp_per_cycle
    fert_cost = fertilizer_result.cost_total_rp

    cost_core_direct = duck_buy + net_ref_cost
    # Availability-aware aggregation: only components that ARE numerically
    # available under the current configuration. Feed and cage total are
    # absent (never zero-filled) so they are excluded by design here.
    cost_total_available = duck_buy + net_ref_cost + fert_cost

    feed_available = feed_amount_rp is not None
    cage_total_available = cage_total_amount_rp is not None
    completeness = (
        CostCompletenessFlag.COMPLETE
        if feed_available and cage_total_available
        else CostCompletenessFlag.INCOMPLETE
    )

    margin_core: Decimal | None = None
    if gross_economic_value is not None:
        margin_core = gross_economic_value - cost_core_direct

    profit_full_est: Decimal | None = None
    profit_full_status: str | None = None
    if completeness is CostCompletenessFlag.INCOMPLETE:
        profit_full_status = PROFIT_FULL_STATUS_INCOMPLETE
    elif gross_economic_value is not None:
        cost_full_est = (
            cost_total_available
            + to_decimal(feed_amount_rp)
            + to_decimal(cage_total_amount_rp)
        )
        profit_full_est = gross_economic_value - cost_full_est

    return EconomicLedgerResult(
        duck_purchase_availability=AvailabilityStatus.AVAILABLE,
        duck_purchase_cost_rp=duck_buy,
        paddy_price_benchmark_rp_per_kg=config.p_gabah_ref_rp_per_kg,
        paddy_price_semantics=PriceBenchmarkType.REGULATORY_HPP,
        paddy_revenue_rp=paddy_revenue,
        cash_revenue_rp=cash_revenue,
        terminal_value_min_rp=terminal_min,
        terminal_value_ref_rp=terminal_ref,
        terminal_value_max_rp=terminal_max,
        terminal_value_is_cash_revenue=False,
        gross_economic_value_rp=gross_economic_value,
        cost_core_direct_rp=cost_core_direct,
        cost_total_available_rp=cost_total_available,
        cost_completeness=completeness,
        margin_core_rp=margin_core,
        profit_full_est_rp=profit_full_est,
        profit_full_status=profit_full_status,
    )
