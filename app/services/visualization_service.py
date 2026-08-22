"""Visualization service — SoT FINAL.

Generates informational zone charts and financial waterfall.
Does NOT use R_age, F_age, lambda_eff, F_density_bio, alpha_bio, beta_tramp, or
any other legacy coefficient banned by SoT §13.

Density curve: shows zone boundaries (UNDER/RECOMMENDED/ABOVE/OVERLOAD) per system.
Age chart: shows readiness zones (TOO_YOUNG/RECOMMENDED/ABOVE_RECOMMENDED_AGE).
Financial waterfall: uses SoT §9 Core Economics with new prices.
"""

from decimal import Decimal, ROUND_FLOOR

from app.engines.formula_engine import Y_BASE
from app.schemas.dss import (
    AgeZonePoint,
    DensityZonePoint,
    DSSSimulationRequest,
    ReferenceBenchmarks,
    VisualizationResponse,
    WaterfallNode,
)
from app.services.simulation_service import dss_service


class VisualizationService:
    def generate_visualization_series(
        self, payload: DSSSimulationRequest
    ) -> VisualizationResponse:

        # 1. Density Zone Series (100 points, 0.1 to 10.0)
        density_zones: list[DensityZonePoint] = []
        step = Decimal("0.1")

        for i in range(1, 101):
            d_val = Decimal(i) * step
            d_float = float(d_val)

            # Density status per SoT §5.1
            if d_val > Decimal("8"):
                ds = "OVERLOAD_HIGH_RISK"
                survival_rate = 0.60
            elif d_val < Decimal("2"):
                ds = "UNDER_DENSITY"
                survival_rate = 1.0
            else:
                # check both systems
                ds = "ABOVE_RECOMMENDED"
                survival_rate = 1.0

            is_recommended_jarwo = Decimal("2") <= d_val <= Decimal("4")
            is_recommended_tegel = Decimal("2") <= d_val <= Decimal("3")
            is_overload = d_val > Decimal("8")

            # Use jarwo status for the curve (planting_system context from payload)
            sys = payload.planting_system.strip().lower()
            ceiling = Decimal("4") if sys == "jajar_legowo" else Decimal("3")
            if d_val > Decimal("8"):
                ds = "OVERLOAD_HIGH_RISK"
            elif d_val < Decimal("2"):
                ds = "UNDER_DENSITY"
            elif d_val <= ceiling:
                ds = "RECOMMENDED"
            else:
                ds = "ABOVE_RECOMMENDED"

            density_zones.append(
                DensityZonePoint(
                    density=round(d_float, 1),
                    density_status=ds,
                    is_recommended_jarwo=bool(is_recommended_jarwo),
                    is_recommended_tegel=bool(is_recommended_tegel),
                    is_overload=bool(is_overload),
                    survival_rate=survival_rate,
                )
            )

        # 2. Age Zone Series (age 1 to 45)
        age_zones: list[AgeZonePoint] = []
        for age in range(1, 46):
            if age < 21:
                flag = "TOO_YOUNG"
                zone = "below_recommended"
            elif age <= 30:
                flag = "RECOMMENDED"
                zone = "recommended"
            else:
                flag = "ABOVE_RECOMMENDED_AGE"
                zone = "above_recommended"
            age_zones.append(
                AgeZonePoint(age_days=age, age_flag=flag, zone=zone)
            )

        # 3. Financial Waterfall — run Core simulation
        sim_res = dss_service.simulate(payload, user_id=None)

        financial_waterfall: list[WaterfallNode] = [
            WaterfallNode(
                name="Revenue Gabah",
                amount=round(sim_res.Revenue_gabah, 2),
                type="revenue",
            ),
            WaterfallNode(
                name="Revenue Potensial Bebek",
                amount=round(sim_res.Revenue_duck_potential, 2),
                type="revenue",
            ),
            WaterfallNode(
                name="Biaya Beli Bebek",
                amount=-round(sim_res.Cost_duck_buy, 2),
                type="cost",
            ),
            WaterfallNode(
                name="Biaya Pakan",
                amount=-round(sim_res.Cost_feed, 2),
                type="cost",
            ),
            WaterfallNode(
                name="Net_Cash_Contribution_DSS",
                amount=round(sim_res.Net_Cash_Contribution_DSS, 2),
                type="total",
            ),
        ]

        benchmarks = ReferenceBenchmarks(
            recommended_density_max_jarwo=4.0,
            recommended_density_max_tegel=3.0,
            overload_threshold=8.0,
            yield_baseline_kg_per_are=float(Y_BASE),
        )

        return VisualizationResponse(
            density_zones=density_zones,
            age_zones=age_zones,
            financial_waterfall=financial_waterfall,
            reference_benchmarks=benchmarks,
            survival_note=(
                "Survival model: d<=8 → N_survive=J (full); d>8 → N_survive=floor(0.60*J). "
                "Estimasi mengasumsikan pemeliharaan memadai."
            ),
            yield_note=(
                f"Yield baseline: {float(Y_BASE)} kg/are (system-neutral, variety-neutral, density-neutral). "
                "Tidak ada multiplier density/age/system/variety pada Yield Engine."
            ),
        )


visualization_service = VisualizationService()
