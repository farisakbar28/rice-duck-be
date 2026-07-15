"""Visualization service for generating SoT v2 mathematical chart series data.

Isolated read-only provider for frontend graphing UI.
Does not alter core financial calculation logic.
"""

from decimal import Decimal

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
)
from app.services.simulation_service import dss_service


class VisualizationService:
    def generate_visualization_series(
        self, payload: DSSSimulationRequest
    ) -> VisualizationResponse:
        # 1. Density Curve Series (d: 0.0 to 10.0, step 0.1 for 101 points)
        density_curve: list[DensityPoint] = []
        
        # Bio-density constants (SoT 4.5)
        alpha_bio = Decimal("0.15")
        k_opt = Decimal("4.0")
        beta_tramp = Decimal("0.25")
        k_max = Decimal("8.0")
        
        # System factors (SoT 4.5 / Tabel 2.2)
        f_sys_jarwo = Decimal("1.00")
        f_sys_tegel = Decimal("0.95")
        
        # Fixed baseline age factor (adapted fully, R_age = 0.05 => F_age = 1 - 0.08*0.05 = 0.996)
        r_age_base = Decimal("0.05")
        f_age_base = Decimal("1") - Decimal("0.08") * r_age_base

        step = Decimal("0.1")
        d_current = Decimal("0.0")
        
        while d_current <= Decimal("10.0") + Decimal("0.0001"):
            # F_density_bio computation
            boost = alpha_bio * (Decimal("1") - _dec_exp(-d_current / k_opt))
            trampling = beta_tramp * (
                max(Decimal("0"), (d_current - k_max) / k_max) ** Decimal("2")
            )
            f_density_bio = Decimal("1") + boost - trampling

            # Calculate total yield factor including F_sys
            jarwo_factor = round(float(f_density_bio * f_sys_jarwo * f_age_base), 4)
            tegel_factor = round(float(f_density_bio * f_sys_tegel * f_age_base), 4)
            d_val = round(float(d_current), 1)

            density_curve.append(
                DensityPoint(
                    density=d_val,
                    jarwo_yield_factor=jarwo_factor,
                    tegel_yield_factor=tegel_factor,
                )
            )
            d_current += step

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

            age_vulnerability.append(
                AgePoint(
                    age_days=age,
                    risk_ratio=round(float(r_age_dec), 4),
                    survival_ceiling=round(float(lambda_eff), 4),
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
        
        core_cash = round(sim_res.Cost_total_cash, 2)
        isolated_shadow_sum = round(
            sim_res.Cost_weeding_isolated
            + sim_res.Cost_pesticide_isolated
            + sim_res.Cost_infra_isolated
            + sim_res.Cost_feed_isolated
            + sim_res.Cost_fertilizer_isolated,
            2,
        )

        financial_breakdown = FinancialAbsorptionBreakdown(
            core_validated_liquid_cash=core_cash,
            empirically_uncorrelated_isolated_shadow_costs=isolated_shadow_sum,
        )

        return VisualizationResponse(
            density_curve=density_curve,
            age_vulnerability=age_vulnerability,
            reference_benchmarks=benchmarks,
            financial_absorption=financial_breakdown,
        )


visualization_service = VisualizationService()
