"""Model A status/reference visualization, without numerical survival."""
from app.schemas.dss import AgeZonePoint, DensityZonePoint, DSSSimulationRequest, ReferenceBenchmarks, VisualizationResponse, WaterfallNode
from app.services.simulation_service import dss_service

class VisualizationService:
    def generate_visualization_series(self,payload:DSSSimulationRequest):
        zones=[]
        for n in range(1,101):
            d=n/10; ceiling=4 if payload.planting_system=="jajar_legowo" else 3
            status="UNDER" if d<2 else "RECOMMENDED" if d<=ceiling else "WARNING_ABOVE_RECOMMENDED" if d<=8 else "HIGH_RISK"
            zones.append(DensityZonePoint(density=d,density_status=status,is_recommended_jarwo=2<=d<=4,is_recommended_tegel=2<=d<=3,is_high_risk=d>8))
        ages=[AgeZonePoint(age_days=a,age_status="NOT_RECOMMENDED" if a<21 else "LOCAL_READY" if a<=30 else "OLDER_CONSERVATIVE",zone="below_local_ready" if a<21 else "local_ready" if a<=30 else "older_conservative") for a in range(0,46)]
        result=dss_service.simulate(payload); waterfall=[]
        for name,key,kind in [("Revenue gabah","revenue_gabah","revenue"),("Revenue bebek all-sold scenario","revenue_duck_all_sold_scenario","revenue"),("Cost beli bebek","cost_duck_buy","cost")]:
            value=getattr(result,key)
            if value is not None: waterfall.append(WaterfallNode(name=name,amount=-value if kind=="cost" else value,type=kind))
        if result.cash_contribution_before_optional is not None: waterfall.append(WaterfallNode(name="Cash contribution before optional",amount=result.cash_contribution_before_optional,type="total"))
        return VisualizationResponse(density_zones=zones,age_zones=ages,financial_waterfall=waterfall,reference_benchmarks=ReferenceBenchmarks(),survival_note="No numerical survival curve: HIGH is a risk status only above 8 ducks/are.",yield_note="Xiong literature yield is shown only within 0<d_ha<=600 and 50<=t<=80.")
visualization_service=VisualizationService()
