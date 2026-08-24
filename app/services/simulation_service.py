"""Model A DSS orchestration; no legacy survival or sandbox computation."""
from app.core.exceptions import InvalidReferenceError, ResourceNotFoundError
from app.engines.formula_engine import (P_DUCK_BUY_FALLBACK, P_DUCK_SELL_FALLBACK, P_GABAH_FALLBACK, compute_age_status, compute_calendar, compute_density, compute_economics, compute_xiong_yield)
from app.repositories.history_repository import history_repository
from app.repositories.lookup_repository import lookup_repository
from app.schemas.dss import (DeleteHistoryResponse, DSSOptionsResponse, DSSSimulationRequest, DSSSimulationResponse, HistoryListItem, HistoryListResponse, HistorySummary, PlantingSystemOption, RiceVarietyOption)

def _number(value): return float(value) if value is not None else None

class DSSService:
    def get_options(self):
        return DSSOptionsResponse(rice_varieties=[RiceVarietyOption(code=x.code,label=x.label,risk_note=x.risk_note,status=x.status) for x in lookup_repository.list_rice_varieties()], planting_systems=[PlantingSystemOption(code=x.code,label=x.label,recommended_density_max_are=x.recommended_density_max_are,recommended_density_min_are=x.recommended_density_min_are,note=x.note) for x in lookup_repository.list_planting_systems()])
    def simulate(self, payload: DSSSimulationRequest, user_id: str | None = None) -> DSSSimulationResponse:
        if payload.rice_variety not in {"sertani", "inpari"}: raise InvalidReferenceError(message="Unknown rice_variety. Valid values: sertani, inpari.",field="rice_variety")
        if payload.planting_system not in {"jajar_legowo", "tegel"}: raise InvalidReferenceError(message="Unknown planting_system. Valid values: jajar_legowo, tegel.",field="planting_system")
        age = compute_age_status(payload.duck_age_days); density = compute_density(payload.duck_count,payload.land_area_are,payload.planting_system); calendar = compute_calendar(payload.planting_date)
        y = compute_xiong_yield(density["density_ha"], payload.literature_duration_days, payload.land_area_are)
        p_gabah, p_buy, p_sell = (payload.p_gabah if payload.p_gabah is not None else P_GABAH_FALLBACK), (payload.p_duck_buy if payload.p_duck_buy is not None else P_DUCK_BUY_FALLBACK), (payload.p_duck_sell if payload.p_duck_sell is not None else P_DUCK_SELL_FALLBACK)
        econ = compute_economics(duck_count=payload.duck_count,density_are=density["density_are"],yield_total_kg=y["yield_total_kg"],p_gabah=p_gabah,p_duck_buy=p_buy,p_duck_sell=p_sell,c_feed_scenario=payload.c_feed_scenario,c_jaring_purchase=payload.c_jaring_purchase,n_jaring_cycles=payload.n_jaring_cycles,c_kandang_purchase=payload.c_kandang_purchase,n_kandang_cycles=payload.n_kandang_cycles)
        warnings = age["warnings"][:]
        if density["density_are"] > 8: warnings.append("Kepadatan di atas 8 ekor/are: survival risk HIGH; revenue bebek all-sold tidak tersedia.")
        if y["reason"]: warnings.append(y["reason"])
        provenance = {"yield":{"source":"Xiong et al. (2014)","status":"literature-uncalibrated","reason":y["reason"]},"prices":{"p_gabah":"runtime" if payload.p_gabah is not None else "local-estimate fallback Rp6000/kg","p_duck_buy":"runtime" if payload.p_duck_buy is not None else "local-estimate fallback Rp25000/ekor","p_duck_sell":"runtime" if payload.p_duck_sell is not None else "local-estimate fallback Rp45000/ekor"},"survival":"HIGH risk status only; no numerical survival prediction" if density["density_are"] > 8 else "No numerical survival claim or correction"}
        response = DSSSimulationResponse(age_status=age["age_status"],density_are=_number(density["density_are"]),density_ha=_number(density["density_ha"]),density_status=density["density_status"],survival_risk="HIGH" if density["density_are"] > 8 else None,yield_status=y["yield_status"],yield_are_kg=_number(y["yield_are_kg"]),yield_total_kg=_number(y["yield_total_kg"]),revenue_gabah=_number(econ["revenue_gabah"]),revenue_duck_all_sold_scenario=_number(econ["revenue_duck_all_sold_scenario"]),cost_duck_buy=_number(econ["cost_duck_buy"]),cost_feed_scenario=_number(econ["cost_feed_scenario"]),cost_infra_cycle=_number(econ["cost_infra_cycle"]),cash_contribution_before_optional=_number(econ["cash_contribution_before_optional"]),cash_contribution_after_optional=_number(econ["cash_contribution_after_optional"]),warnings=warnings,provenance=provenance,**calendar)
        if user_id: history_repository.create_v4(user_id, payload, response)
        return response
    def list_histories(self,user_id):
        return HistoryListResponse(data=[HistoryListItem(id=x.id,schema_version=x.schema_version,created_at=x.created_at,summary=HistorySummary(rice_variety=x.payload["input"]["rice_variety"],planting_system=x.payload["input"]["planting_system"],duck_count=x.payload["input"]["duck_count"],land_area_are=x.payload["input"]["land_area_are"],density_are=x.payload["response"]["density_are"],yield_status=x.payload["response"]["yield_status"])) for x in history_repository.list_v4_by_user(user_id)])
    def get_history(self,history_id,user_id):
        row=history_repository.get_v4(history_id,user_id)
        if row is None: raise ResourceNotFoundError(message=f"History '{history_id}' was not found.",field="history_id")
        return DSSSimulationResponse.model_validate(row.payload["response"])
    def delete_history(self,history_id,user_id):
        if not history_repository.delete_by_id_and_user(history_id,user_id): raise ResourceNotFoundError(message=f"History '{history_id}' was not found.",field="history_id")
        return DeleteHistoryResponse(message="Simulation history deleted successfully")
dss_service=DSSService()
