from app.core.exceptions import InvalidReferenceError, ResourceNotFoundError
from app.engines.formula_engine import P_BUY,P_GABAH,P_SELL,compute_age_status,compute_calendar,compute_density,compute_economics,compute_yield
from app.repositories.history_repository import history_repository
from app.repositories.lookup_repository import lookup_repository
from app.schemas.dss import *
class DSSService:
 def get_options(self):
  return DSSOptionsResponse(rice_varieties=[RiceVarietyOption(code=x.code,label=x.label,risk_note=x.risk_note,status=x.status) for x in lookup_repository.list_rice_varieties()],planting_systems=[PlantingSystemOption(code=x.code,label=x.label,recommended_density_max_are=x.recommended_density_max_are,recommended_density_min_are=x.recommended_density_min_are,note=x.note) for x in lookup_repository.list_planting_systems()])
 def simulate(self,payload,user_id=None):
  if lookup_repository.get_rice_variety(payload.rice_variety) is None: raise InvalidReferenceError(message="Unknown rice_variety.",field="rice_variety")
  if lookup_repository.get_planting_system(payload.planting_system) is None: raise InvalidReferenceError(message="Unknown planting_system.",field="planting_system")
  d,dh,status=compute_density(payload.duck_count,payload.land_area_are,payload.planting_system); dates=compute_calendar(payload.planting_date); ya,yt=compute_yield(payload.land_area_are)
  pg=payload.p_gabah if payload.p_gabah is not None else P_GABAH; pb=payload.p_duck_buy if payload.p_duck_buy is not None else P_BUY; ps=payload.p_duck_sell if payload.p_duck_sell is not None else P_SELL
  rice,duck,buy,feed,infra,before,after=compute_economics(total=yt,ducks=payload.duck_count,density=d,p_gabah=pg,p_buy=pb,p_sell=ps,feed=payload.c_feed_scenario,jaring=payload.c_jaring_purchase,nj=payload.n_jaring_cycles,kandang=payload.c_kandang_purchase,nk=payload.n_kandang_cycles)
  warnings=[]
  if d>8: warnings.append("Kepadatan di atas 8 ekor/are: skenario seluruh bebek terjual tidak tersedia; survival numerik tidak dimodelkan.")
  if payload.duck_age_days<21: warnings.append("Umur bebek belum direkomendasikan secara lokal.")
  response=DSSSimulationResponse(yield_are_kg=float(ya),yield_total_kg=float(yt),parameter_uncertainty_y0_95pct=[42.81,55.78],age_status=compute_age_status(payload.duck_age_days),density_are=float(d),density_ha=float(dh),density_status=status,release_hst_min=21,release_hst_max=30,withdraw_hst_min=56,withdraw_hst_max=60,release_date_min=dates[0],release_date_max=dates[1],withdraw_date_min=dates[2],withdraw_date_max=dates[3],survival_risk="HIGH" if d>8 else None,revenue_gabah=float(rice),revenue_duck_all_sold_scenario=float(duck) if duck is not None else None,cost_duck_buy=float(buy),cost_feed_scenario=float(feed) if feed is not None else None,cost_infra_cycle=float(infra) if infra is not None else None,cash_contribution_before_optional=float(before) if before is not None else None,cash_contribution_after_optional=float(after) if after is not None else None,warnings=warnings,provenance={"yield":{"source":"farmer-grouped calibration","status":"local-calibrated","Y0_C":50,"calibration_cycles":25,"calibration_farmers":13,"selection":"one-standard-error rule","parameter_uncertainty":"descriptive; not individual prediction interval"},"validation":{"untouched_holdout_cycles":11,"untouched_holdout_farmers":6,"MAE":11.979,"RMSE":15.990,"MedAE":9.583,"Bias":7.307,"limitation":"limited holdout performance"},"prices":{"p_gabah":{"value":float(pg),"source":"runtime" if payload.p_gabah is not None else "branch-C default","status":"runtime" if payload.p_gabah is not None else "local-calibrated"},"p_duck_buy":{"value":float(pb),"source":"runtime" if payload.p_duck_buy is not None else "branch-C default","status":"runtime" if payload.p_duck_buy is not None else "local-calibrated"},"p_duck_sell":{"value":float(ps),"source":"runtime" if payload.p_duck_sell is not None else "branch-C default","status":"runtime" if payload.p_duck_sell is not None else "local-estimate"}},"survival":{"note":"numerical survival not modeled"}})
  if user_id: history_repository.create_v4(user_id,payload,response)
  return response
 def list_histories(self,user_id):
  return HistoryListResponse(data=[HistoryListItem(id=x.id,schema_version=4,created_at=x.created_at,summary=HistorySummary(rice_variety=x.payload["input"]["rice_variety"],planting_system=x.payload["input"]["planting_system"],duck_count=x.payload["input"]["duck_count"],land_area_are=float(x.payload["input"]["land_area_are"]),density_are=x.payload["response"]["density_are"],yield_are_kg=50)) for x in history_repository.list_v4_by_user(user_id)])
 def get_history(self,hid,user_id):
  x=history_repository.get_v4(hid,user_id)
  if not x: raise ResourceNotFoundError(message=f"History '{hid}' was not found.",field="history_id")
  return DSSSimulationResponse.model_validate(x.payload["response"])
 def delete_history(self,hid,user_id):
  if not history_repository.delete_by_id_and_user(hid,user_id): raise ResourceNotFoundError(message=f"History '{hid}' was not found.",field="history_id")
  return DeleteHistoryResponse(message="Simulation history deleted successfully")
dss_service=DSSService()
