"""A+C orchestration: primary C0 always precedes optional Xiong reference."""
from app.core.exceptions import InvalidReferenceError, ResourceNotFoundError
from app.engines.formula_engine import (P_DUCK_BUY_DEFAULT, P_DUCK_SELL_DEFAULT, P_GABAH_DEFAULT, compute_age_status, compute_calendar, compute_density, compute_economics_from_primary, compute_literature_reference, compute_primary_yield)
from app.repositories.history_repository import history_repository
from app.repositories.lookup_repository import lookup_repository
from app.schemas.dss import (DeleteHistoryResponse, DSSOptionsResponse, DSSSimulationRequest, DSSSimulationResponse, HistoryListItem, HistoryListResponse, HistorySummary, PlantingSystemOption, RiceVarietyOption)

def _number(value): return float(value) if value is not None else None

class DSSService:
    def get_options(self):
        return DSSOptionsResponse(rice_varieties=[RiceVarietyOption(code=x.code,label=x.label,risk_note=x.risk_note,status=x.status) for x in lookup_repository.list_rice_varieties()], planting_systems=[PlantingSystemOption(code=x.code,label=x.label,recommended_density_max_are=x.recommended_density_max_are,recommended_density_min_are=x.recommended_density_min_are,note=x.note) for x in lookup_repository.list_planting_systems()])
    def simulate(self, payload: DSSSimulationRequest, user_id: str | None = None) -> DSSSimulationResponse:
        if lookup_repository.get_rice_variety(payload.rice_variety) is None: raise InvalidReferenceError(message="Unknown rice_variety. Valid values: sertani, inpari.", field="rice_variety")
        if lookup_repository.get_planting_system(payload.planting_system) is None: raise InvalidReferenceError(message="Unknown planting_system. Valid values: jajar_legowo, tegel.", field="planting_system")
        age = compute_age_status(payload.duck_age_days)
        density = compute_density(payload.duck_count, payload.land_area_are, payload.planting_system)
        calendar = compute_calendar(payload.planting_date)
        primary = compute_primary_yield(payload.land_area_are)  # Unconditional C0 primary.
        reference = compute_literature_reference(density["density_ha"], payload.literature_duration_days, payload.land_area_are)
        p_gabah = payload.p_gabah if payload.p_gabah is not None else P_GABAH_DEFAULT
        p_buy = payload.p_duck_buy if payload.p_duck_buy is not None else P_DUCK_BUY_DEFAULT
        p_sell = payload.p_duck_sell if payload.p_duck_sell is not None else P_DUCK_SELL_DEFAULT
        economics = compute_economics_from_primary(primary_total_kg=primary["yield_total_kg"], duck_count=payload.duck_count, density_are=density["density_are"], p_gabah=p_gabah, p_duck_buy=p_buy, p_duck_sell=p_sell, c_feed_scenario=payload.c_feed_scenario, c_jaring_purchase=payload.c_jaring_purchase, n_jaring_cycles=payload.n_jaring_cycles, c_kandang_purchase=payload.c_kandang_purchase, n_kandang_cycles=payload.n_kandang_cycles)
        warnings = age["warnings"][:]
        if density["density_are"] > 8: warnings.append("Kepadatan di atas 8 ekor/are: survival risk HIGH; skenario seluruh bebek terjual tidak tersedia.")
        if reference["reason"]: warnings.append(reference["reason"])
        provenance = {"primary_local":{"Y0_C":50.0,"source":"25 calibration cycles / 13 farmers","status":"local-calibrated","selection":"farmer-grouped LOFO; one-standard-error rule","parameter_uncertainty_95pct":"descriptive baseline-parameter uncertainty; not an individual field prediction interval"},"validation":{"untouched_holdout_cycles":11,"untouched_holdout_farmers":6,"MAE":11.979,"RMSE":15.990,"MedAE":9.583,"Bias":7.307,"limitation":"limited holdout performance"},"literature_reference":{"source":"Xiong et al. (2014)","status":"literature-uncalibrated","domain":"0 < density_ha <= 600 and 50 <= literature_duration_days <= 80","availability":reference["status"],"reason":reference["reason"]},"prices":{"p_gabah":{"value":_number(p_gabah),"source":"runtime" if payload.p_gabah is not None else "fallback","status":"runtime" if payload.p_gabah is not None else "local-calibrated"},"p_duck_buy":{"value":_number(p_buy),"source":"runtime" if payload.p_duck_buy is not None else "fallback","status":"runtime" if payload.p_duck_buy is not None else "local-calibrated"},"p_duck_sell":{"value":_number(p_sell),"source":"runtime" if payload.p_duck_sell is not None else "fallback","status":"runtime" if payload.p_duck_sell is not None else "local-estimate"}},"survival":{"note":"numerical survival not modeled"}}
        response = DSSSimulationResponse(yield_are_kg=_number(primary["yield_are_kg"]),yield_total_kg=_number(primary["yield_total_kg"]),parameter_uncertainty_y0_95pct=[42.81,55.78],literature_reference_status=reference["status"],yield_literature_reference_are_kg=_number(reference["yield_are_kg"]),yield_literature_reference_total_kg=_number(reference["yield_total_kg"]),literature_gap_kg_are=_number(reference["yield_are_kg"]-primary["yield_are_kg"]) if reference["yield_are_kg"] is not None else None,age_status=age["age_status"],density_are=_number(density["density_are"]),density_ha=_number(density["density_ha"]),density_status=density["density_status"],survival_risk="HIGH" if density["density_are"]>8 else None,revenue_gabah=_number(economics["revenue_gabah"]),revenue_duck_all_sold_scenario=_number(economics["revenue_duck_all_sold_scenario"]),cost_duck_buy=_number(economics["cost_duck_buy"]),cost_feed_scenario=_number(economics["cost_feed_scenario"]),cost_infra_cycle=_number(economics["cost_infra_cycle"]),cash_contribution_before_optional=_number(economics["cash_contribution_before_optional"]),cash_contribution_after_optional=_number(economics["cash_contribution_after_optional"]),warnings=warnings,provenance=provenance,**calendar)
        if user_id is not None: history_repository.create_v4(user_id,payload,response)
        return response
    def list_histories(self,user_id: str) -> HistoryListResponse:
        return HistoryListResponse(data=[HistoryListItem(id=row.id,schema_version=4,created_at=row.created_at,summary=HistorySummary(rice_variety=row.payload["input"]["rice_variety"],planting_system=row.payload["input"]["planting_system"],duck_count=row.payload["input"]["duck_count"],land_area_are=float(row.payload["input"]["land_area_are"]),density_are=row.payload["response"]["density_are"],yield_are_kg=row.payload["response"]["yield_are_kg"])) for row in history_repository.list_v4_by_user(user_id)])
    def get_history(self,history_id: str,user_id: str) -> DSSSimulationResponse:
        row=history_repository.get_v4(history_id,user_id)
        if row is None: raise ResourceNotFoundError(message=f"History '{history_id}' was not found.",field="history_id")
        return DSSSimulationResponse.model_validate(row.payload["response"])
    def delete_history(self,history_id: str,user_id: str) -> DeleteHistoryResponse:
        if not history_repository.delete_by_id_and_user(history_id,user_id): raise ResourceNotFoundError(message=f"History '{history_id}' was not found.",field="history_id")
        return DeleteHistoryResponse(message="Simulation history deleted successfully")
dss_service=DSSService()
