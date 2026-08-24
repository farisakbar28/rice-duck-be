"""Model C visual aids: gates, C0 benchmark, and only available finances."""
from decimal import Decimal
from app.schemas.dss import *
from app.services.simulation_service import dss_service
class VisualizationService:
 def generate_visualization_series(self,payload):
  zones=[]
  for i in range(1,101):
   d=Decimal(i)/10; s="HIGH_RISK" if d>8 else "UNDER" if d<2 else "RECOMMENDED" if d <= (4 if payload.planting_system=="jajar_legowo" else 3) else "WARNING_ABOVE_RECOMMENDED"
   zones.append(DensityZonePoint(density=float(d),density_status=s,is_recommended_jarwo=2<=d<=4,is_recommended_tegel=2<=d<=3,is_high_risk=d>8))
  ages=[AgeZonePoint(age_days=x,age_status="NOT_RECOMMENDED" if x<21 else "LOCAL_READY" if x<=30 else "OLDER_CONSERVATIVE",zone="below_recommended" if x<21 else "recommended" if x<=30 else "above_recommended") for x in range(1,46)]
  r=dss_service.simulate(payload); wf=[WaterfallNode(name="Revenue Gabah",amount=r.revenue_gabah,type="revenue"),WaterfallNode(name="Revenue Bebek (all-sold scenario)",amount=r.revenue_duck_all_sold_scenario,type="revenue"),WaterfallNode(name="Biaya Beli Bebek",amount=-r.cost_duck_buy,type="cost"),WaterfallNode(name="Cash contribution before optional",amount=r.cash_contribution_before_optional,type="total")]
  return VisualizationResponse(density_zones=zones,age_zones=ages,financial_waterfall=wf,reference_benchmarks=ReferenceBenchmarks(),survival_note="Numerical survival is not modeled; HIGH is shown only above 8 ducks/are.",yield_note="Frozen farmer-grouped C0 benchmark: 50 kg/are.")
visualization_service=VisualizationService()
