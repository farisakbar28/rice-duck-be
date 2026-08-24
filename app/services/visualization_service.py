"""A+C visual aids show C0 as primary and never plot unavailable reference as zero."""
from decimal import Decimal
from app.schemas.dss import *
from app.services.simulation_service import dss_service

class VisualizationService:
    def generate_visualization_series(self,payload):
        zones=[]
        for i in range(1,101):
            density=Decimal(i)/10; ceiling=Decimal("4") if payload.planting_system=="jajar_legowo" else Decimal("3")
            status="HIGH_RISK" if density>8 else "UNDER" if density<2 else "RECOMMENDED" if density<=ceiling else "WARNING_ABOVE_RECOMMENDED"
            zones.append(DensityZonePoint(density=float(density),density_status=status,is_recommended_jarwo=Decimal("2")<=density<=Decimal("4"),is_recommended_tegel=Decimal("2")<=density<=Decimal("3"),is_high_risk=density>8))
        ages=[AgeZonePoint(age_days=age,age_status="NOT_RECOMMENDED" if age<21 else "LOCAL_READY" if age<=30 else "OLDER_CONSERVATIVE",zone="below_recommended" if age<21 else "recommended" if age<=30 else "above_recommended") for age in range(1,46)]
        result=dss_service.simulate(payload)
        waterfall=[WaterfallNode(name="PRIMARY local revenue gabah",amount=result.revenue_gabah,type="revenue"),WaterfallNode(name="Revenue bebek (all-sold scenario)",amount=result.revenue_duck_all_sold_scenario,type="revenue"),WaterfallNode(name="Biaya beli bebek",amount=-result.cost_duck_buy,type="cost"),WaterfallNode(name="Cash contribution before optional",amount=result.cash_contribution_before_optional,type="total")]
        return VisualizationResponse(density_zones=zones,age_zones=ages,financial_waterfall=waterfall,reference_benchmarks=ReferenceBenchmarks(),survival_note="Numerical survival is not modeled; HIGH is shown only above 8 ducks/are.",yield_note="PRIMARY local C0 is 50 kg/are. Xiong is an optional unblended literature reference and is omitted when unavailable.")
visualization_service=VisualizationService()
