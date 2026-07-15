"""Visualization service for generating SoT v2 mathematical chart series data.

Isolated read-only provider for frontend graphing UI.
Does not alter core financial calculation logic.
"""

from decimal import Decimal, getcontext

from app.engines.formula_engine import (
    _dec_exp,
    compute_duck_age_status,
    compute_surviving_ducks,
)
from app.schemas.dss import (
    AgePoint,
    DensityPoint,
    FinancialAbsorptionBreakdown,
    ReferenceBenchmarks,
    DSSSimulationRequest,
    VisualizationResponse,
    VisualizationsObject,
    WaterfallNode,
)
from app.services.simulation_service import dss_service


class VisualizationService:
    def generate_visualization_series(
        self, payload: DSSSimulationRequest
    ) -> VisualizationResponse:
        # High precision calculation layer
        getcontext().prec = 50

        # 1. Density Curve Series (100 points, interval step 0.1: 0.1 to 10.0)
        density_curve: list[DensityPoint] = []

        # Bio-density constants (SoT 4.5)
        alpha_bio = Decimal("0.15")
        k_opt = Decimal("4.0")
        beta_tramp = Decimal("0.25")
        k_max = Decimal("8.0")

        # System factors (SoT 4.5 / Tabel 2.2)
        f_sys_jarwo = Decimal("1.00")
        f_sys_tegel = Decimal("1.211")

        k_safe_jarwo = Decimal("4.0")
        k_safe_tegel = Decimal("3.0")

        step = Decimal("0.1")

        for i in range(1, 101):
            d_current = Decimal(i) * step

            # F_density_bio computation
            boost = alpha_bio * (Decimal("1") - _dec_exp(-d_current / k_opt))
            trampling = beta_tramp * (
                max(Decimal("0"), (d_current - k_max) / k_max) ** Decimal("2")
            )
            f_density_bio = Decimal("1") + boost - trampling

            # Calculate yield factors
            jarwo_factor = round(float(f_density_bio * f_sys_jarwo), 6)
            tegel_factor = round(float(f_density_bio * f_sys_tegel), 6)
            d_val = round(float(d_current), 6)

            is_safe_jarwo = d_current <= k_safe_jarwo
            is_safe_tegel = d_current <= k_safe_tegel
            is_over_density = d_current > k_max

            density_curve.append(
                DensityPoint(
                    density=d_val,
                    yield_factor_jarwo=jarwo_factor,
                    yield_factor_tegel=tegel_factor,
                    is_safe_jarwo=is_safe_jarwo,
                    is_safe_tegel=is_safe_tegel,
                    is_over_density=is_over_density,
                )
            )

        # 2. Age Vulnerability Series (age_days: 1 to 45)
        age_vulnerability: list[AgePoint] = []
        base_duck_count = 10000

        for age in range(1, 46):
            age_status = compute_duck_age_status(age)
            r_age_dec = age_status["R_age"]

            # lambda_eff calculation via compute_surviving_ducks with p_over = 0
            surviving_dec = compute_surviving_ducks(
                duck_count=base_duck_count,
                r_age=float(r_age_dec),
                p_over=0.0,
            )
            lambda_eff = surviving_dec / Decimal(base_duck_count)

            if age < 14:
                zone = "red"
            elif age <= 29:
                zone = "yellow"
            else:
                zone = "green"

            age_vulnerability.append(
                AgePoint(
                    age_days=age,
                    risk_ratio=round(float(r_age_dec), 6),
                    survival_ceiling=round(float(lambda_eff), 6),
                    zone=zone,
                )
            )

        # 3. Reference Benchmarks
        benchmarks = ReferenceBenchmarks(
            k_safe_jarwo=4.0,
            k_safe_tegel=3.0,
            k_max_saturation=8.0,
        )

        # 4. Financial Absorption Two-Tier Breakdown
        sim_res = dss_service.simulate(payload, user_id=None)

        core_cash = round(float(sim_res.Cost_total_cash), 6)
        isolated_shadow_sum = round(
            float(
                sim_res.Cost_weeding_isolated
                + sim_res.Cost_pesticide_isolated
                + sim_res.Cost_infra_isolated
                + sim_res.Cost_feed_isolated
                + sim_res.Cost_fertilizer_isolated
            ),
            6,
        )

        financial_breakdown = FinancialAbsorptionBreakdown(
            core_validated_liquid_cash=core_cash,
            empirically_uncorrelated_isolated_shadow_costs=isolated_shadow_sum,
        )

        # 5. Waterfall Series (Gross Grain Revenue, Gross Duck Revenue, Duckling Acquisition Cost, Pure Absorbed Net Cash)
        financial_waterfall: list[WaterfallNode] = [
            WaterfallNode(
                name="Gross Grain Revenue",
                amount=round(float(sim_res.Revenue_gabah), 6),
                type="revenue",
            ),
            WaterfallNode(
                name="Gross Duck Revenue",
                amount=round(float(sim_res.Revenue_duck), 6),
                type="revenue",
            ),
            WaterfallNode(
                name="Duckling Acquisition Cost",
                amount=-round(float(sim_res.Cost_duck_buy), 6),
                type="cost",
            ),
            WaterfallNode(
                name="Pure Absorbed Net Cash",
                amount=round(float(sim_res.Profit_net_cash), 6),
                type="total",
            ),
        ]

        visualizations = VisualizationsObject(
            density_curve=density_curve,
            age_vulnerability=age_vulnerability,
            financial_waterfall=financial_waterfall,
            benchmarks=benchmarks,
        )

        return VisualizationResponse(
            density_curve=density_curve,
            age_vulnerability=age_vulnerability,
            reference_benchmarks=benchmarks,
            financial_absorption=financial_breakdown,
            visualizations=visualizations,
        )


visualization_service = VisualizationService()


