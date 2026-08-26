"""Canonical R2 visualization as a side-effect-free simulation view.

The service performs no scientific calculation. Request-specific values come
from ``DSSService.simulate(..., user_id=None)`` and support zones come from
the same R2 interval definitions used by the classifiers.
"""

from __future__ import annotations

from app.domain.models import AvailabilityStatus
from app.engines.r2 import (
    age_support_intervals,
    density_support_intervals,
    load_default_config,
)
from app.schemas.dss import (
    AgeSupportZone,
    DensitySupportZone,
    DSSSimulationRequest,
    FertilizerVisualization,
    FertilizerVisualizationComponent,
    FinancialVisualization,
    FinancialVisualizationKind,
    FinancialVisualizationNode,
    InfrastructureVisualization,
    VisualizationResponse,
    VisualizationSelectedInput,
    YieldVisualization,
)
from app.services.simulation_service import dss_service


def _availability(amount: float | None) -> AvailabilityStatus:
    return (
        AvailabilityStatus.AVAILABLE
        if amount is not None
        else AvailabilityStatus.UNAVAILABLE
    )


class VisualizationService:
    def generate(self, payload: DSSSimulationRequest) -> VisualizationResponse:
        # Explicitly anonymous: visualization must never persist history,
        # even when the HTTP request happens to carry an Authorization header.
        simulation = dss_service.simulate(payload, user_id=None)
        config = load_default_config()
        system = dss_service._find_planting_system(simulation.input.planting_system)

        selected_density = simulation.operational.density_are
        if selected_density is None:
            raise RuntimeError("Canonical simulation did not produce density_are.")

        density_zones = [
            DensitySupportZone(
                key=interval.key,
                label=interval.label,
                min=float(interval.minimum) if interval.minimum is not None else None,
                max=float(interval.maximum) if interval.maximum is not None else None,
                min_inclusive=interval.min_inclusive,
                max_inclusive=interval.max_inclusive,
                status=interval.status,
                selected_value_in_zone=interval.contains(selected_density),
            )
            for interval in density_support_intervals(system, config)
        ]
        age_zones = [
            AgeSupportZone(
                key=interval.key,
                label=interval.label,
                min_days=int(interval.minimum) if interval.minimum is not None else None,
                max_days=int(interval.maximum) if interval.maximum is not None else None,
                min_inclusive=interval.min_inclusive,
                max_inclusive=interval.max_inclusive,
                status=interval.status,
                selected_value_in_zone=interval.contains(simulation.input.duck_age_days),
            )
            for interval in age_support_intervals(config)
        ]

        net = simulation.costs.net_infrastructure
        fertilizer = simulation.fertilizer_baseline

        return VisualizationResponse(
            model=simulation.model,
            selected_input=VisualizationSelectedInput(
                land_area_are=simulation.input.land_area_are,
                duck_count=simulation.input.duck_count,
                planting_date=simulation.input.planting_date,
                planting_system=simulation.input.planting_system,
                rice_variety=simulation.input.rice_variety,
                duck_age_days=simulation.input.duck_age_days,
                p_duck_buy_manual=simulation.input.p_duck_buy_manual,
                p_duck_buy_effective=simulation.input.p_duck_buy_effective,
                p_duck_buy_source=simulation.input.p_duck_buy_source,
                density_are=selected_density,
            ),
            density_zones=density_zones,
            age_zones=age_zones,
            calendar=simulation.calendar,
            infrastructure=InfrastructureVisualization(
                availability="AVAILABLE_RANGE",
                area_are=simulation.input.land_area_are,
                equivalent_perimeter_m=net.equivalent_perimeter_m,
                cost_min_rp_per_cycle=net.cost_min_rp_per_cycle,
                cost_ref_rp_per_cycle=net.cost_ref_rp_per_cycle,
                cost_max_rp_per_cycle=net.cost_max_rp_per_cycle,
                geometry_assumption=net.geometry_assumption,
                series_semantics="CALCULATED_REQUEST_RANGE",
            ),
            fertilizer=FertilizerVisualization(
                availability="AVAILABLE",
                baseline_label="BASELINE-NO-CREDIT",
                nutrient_basis=fertilizer.nutrient_basis,
                manure_credit_applied=False,
                components=[
                    FertilizerVisualizationComponent(
                        key="NPK_PHONSKA",
                        label="NPK Phonska",
                        quantity_kg=fertilizer.q_npk_kg,
                        cost_rp=fertilizer.cost_npk_rp,
                    ),
                    FertilizerVisualizationComponent(
                        key="UREA",
                        label="Urea",
                        quantity_kg=fertilizer.q_urea_kg,
                        cost_rp=fertilizer.cost_urea_rp,
                    ),
                ],
                total_cost_rp=fertilizer.cost_total_rp,
            ),
            yield_series=YieldVisualization(
                availability=simulation.crop_yield.availability,
                points=[],
                reason_codes=list(simulation.crop_yield.reason_codes),
            ),
            financial_waterfall=self._financial_view(simulation),
            warnings=list(simulation.warnings),
        )

    @staticmethod
    def _financial_view(simulation) -> FinancialVisualization:
        economics = simulation.economics
        costs = simulation.costs
        terminal_value = simulation.duck.terminal_value_ref_rp
        return FinancialVisualization(
            availability="PARTIAL",
            cost_completeness=costs.cost_completeness,
            nodes=[
                FinancialVisualizationNode(
                    key="paddy_cash_revenue",
                    label="Paddy cash revenue",
                    kind=FinancialVisualizationKind.CASH_REVENUE,
                    availability=_availability(economics.cash_revenue_rp),
                    amount_rp=economics.cash_revenue_rp,
                    affects_cash_total=True,
                    note="Available only when the R2 yield output is available.",
                ),
                FinancialVisualizationNode(
                    key="terminal_duck_value_ref",
                    label="Terminal duck livestock value (reference)",
                    kind=FinancialVisualizationKind.ASSET_VALUE,
                    availability=_availability(terminal_value),
                    amount_rp=terminal_value,
                    affects_cash_total=False,
                    note="Livestock asset value; not realized cash revenue.",
                ),
                FinancialVisualizationNode(
                    key="duck_purchase_cost",
                    label="Duck purchase cost",
                    kind=FinancialVisualizationKind.COST,
                    availability=_availability(costs.duck_purchase.amount_rp),
                    amount_rp=costs.duck_purchase.amount_rp,
                    affects_cash_total=True,
                ),
                FinancialVisualizationNode(
                    key="net_infrastructure_ref_cost",
                    label="Net infrastructure reference cost",
                    kind=FinancialVisualizationKind.COST,
                    availability=_availability(costs.net_infrastructure.cost_ref_rp_per_cycle),
                    amount_rp=costs.net_infrastructure.cost_ref_rp_per_cycle,
                    affects_cash_total=True,
                    note="Square-equivalent request-area estimate.",
                ),
                FinancialVisualizationNode(
                    key="fertilizer_baseline_cost",
                    label="Fertilizer baseline cost",
                    kind=FinancialVisualizationKind.COST,
                    availability=_availability(simulation.fertilizer_baseline.cost_total_rp),
                    amount_rp=simulation.fertilizer_baseline.cost_total_rp,
                    affects_cash_total=True,
                    note="BASELINE-NO-CREDIT; not a zero-manure-contribution claim.",
                ),
                FinancialVisualizationNode(
                    key="feed_cost",
                    label="Feed cost",
                    kind=FinancialVisualizationKind.COST,
                    availability=_availability(costs.feed.amount_rp),
                    amount_rp=costs.feed.amount_rp,
                    affects_cash_total=True,
                    note="Unavailable until quantity and price lookups are configured.",
                ),
                FinancialVisualizationNode(
                    key="cage_total_cost",
                    label="Cage total cost",
                    kind=FinancialVisualizationKind.COST,
                    availability=_availability(costs.cage.total_amount_rp),
                    amount_rp=costs.cage.total_amount_rp,
                    affects_cash_total=True,
                    note="Unavailable until a sourced cage-capacity rule exists.",
                ),
                FinancialVisualizationNode(
                    key="available_cost_subtotal",
                    label="Available cost subtotal",
                    kind=FinancialVisualizationKind.AVAILABLE_COST_SUBTOTAL,
                    availability=_availability(costs.cost_total_available_rp),
                    amount_rp=costs.cost_total_available_rp,
                    affects_cash_total=False,
                    note="Subtotal of available components only; not full cost.",
                ),
                FinancialVisualizationNode(
                    key="full_profit",
                    label="Full profit estimate",
                    kind=FinancialVisualizationKind.FULL_PROFIT,
                    availability=_availability(economics.profit_full_est_rp),
                    amount_rp=economics.profit_full_est_rp,
                    affects_cash_total=False,
                    note="Unavailable while the configured cost ledger is incomplete.",
                ),
            ],
        )


visualization_service = VisualizationService()
