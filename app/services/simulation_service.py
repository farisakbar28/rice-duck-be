"""DSS simulation service — SoT FINAL.

Orchestrates engines per docs/Model Matematika Data Collection DSS Padi Bebek FINAL.md:

  §4  Age Readiness Engine   -> compute_age_flag()
  §5  Density Engine         -> compute_density()
  §6  Calendar Engine        -> compute_calendar()
  §7  Survival Engine        -> compute_surviving_ducks()
  §8  Yield Engine           -> compute_yield()
  §9  Core Economic Engine   -> compute_core_economics()
  §10 Sandbox Engines        -> compute_sandbox_*() [NOT in Core]

SoT §13 banned: R_age, F_age, lambda_eff, P_over/P_under, F_density_bio,
alpha_bio, beta_tramp, F_sys!=1, feed=4500, p_duck_sell=35000, Profit_net_cash
as canonical, Cost_feed_isolated, p_duck_buy fallback/default.
"""

import json
from datetime import date as date_type

from app.core.exceptions import InvalidReferenceError, ResourceNotFoundError
from app.domain.models import PlantingSystem, RiceVariety
from app.engines.formula_engine import (
    compute_age_flag,
    compute_calendar,
    compute_core_economics,
    compute_density,
    compute_surviving_ducks,
    compute_yield,
)
from app.engines.impact_engine import (
    compute_sandbox_fertilizer,
    compute_sandbox_infrastructure,
    compute_sandbox_pesticide,
    compute_sandbox_weeding,
)
from app.repositories.lookup_repository import lookup_repository
from app.schemas.dss import (
    DeleteHistoryResponse,
    DSSOptionsResponse,
    DSSSimulationRequest,
    DSSSimulationResponse,
    HistoryListResponse,
    PlantingSystemOption,
    RiceVarietyOption,
    SandboxFertilizer,
    SandboxInfrastructure,
    SandboxOutputs,
    SandboxPesticide,
    SandboxWeeding,
)


class DSSService:
    def get_options(self) -> DSSOptionsResponse:
        return DSSOptionsResponse(
            rice_varieties=[
                RiceVarietyOption(
                    code=item.code,
                    label=item.label,
                    hst_panen_min=item.hst_panen_min,
                    hst_panen_max=item.hst_panen_max,
                    risk_note=item.risk_note,
                    status=item.status,
                )
                for item in lookup_repository.list_rice_varieties()
            ],
            planting_systems=[
                PlantingSystemOption(
                    code=item.code,
                    label=item.label,
                    recommended_density_max_are=item.recommended_density_max_are,
                    recommended_density_min_are=item.recommended_density_min_are,
                    note=item.note,
                )
                for item in lookup_repository.list_planting_systems()
            ],
        )

    def simulate(
        self,
        payload: DSSSimulationRequest,
        user_id: str | None = None,
    ) -> DSSSimulationResponse:
        # Lookup validation
        variety = self._find_variety(payload.rice_variety)
        planting_system = self._find_planting_system(payload.planting_system)
        constants = lookup_repository.get_constants()

        warnings: list[str] = []

        if payload.land_area_are < 2.5:
            warnings.append(
                "Luas lahan di bawah 2,5 are berada di luar domain numerical validation lokal; "
                "prediksi tetap dihitung sesuai model production."
            )

        # SoT §4: Age Readiness Engine — status/warning only, no yield/survival multiplier
        age_result = compute_age_flag(payload.duck_age_days)
        age_flag = age_result["age_flag"]
        warnings.extend(age_result["warnings"])

        # SoT §5: Density Engine — status only, no yield multiplier
        density_result = compute_density(
            payload.duck_count,
            payload.land_area_are,
            payload.planting_system,
        )
        d = density_result["d"]
        d_ha = density_result["d_ha"]
        density_status = density_result["density_status"]
        warnings.extend(density_result["warnings"])

        # SoT §6: Calendar Engine
        calendar_result = compute_calendar(payload.planting_date, payload.rice_variety)
        warnings.extend(calendar_result["warnings"])

        # SoT §7: Survival Engine — only d > 8 triggers floor(0.60*J)
        n_survive = compute_surviving_ducks(payload.duck_count, d)

        # SoT §11.1: survival assumption warning (always)
        warnings.append(
            "Estimasi survival mengasumsikan pemeliharaan memadai; actual mortality dapat berbeda "
            "akibat penyakit, predator, cuaca, atau faktor husbandry lain."
        )

        # SoT §8: Yield Engine — constant baseline, system/variety/density neutral
        yield_result = compute_yield(payload.land_area_are)
        yield_total_pred = yield_result["Yield_total_pred"]

        # SoT §9: Core Economic Engine
        econ = compute_core_economics(
            yield_total_pred=yield_total_pred,
            n_survive=n_survive,
            duck_count=payload.duck_count,
            p_duck_buy=payload.p_duck_buy,
        )

        # SoT §10: Sandbox (fully separated, does NOT affect Core)
        sandbox_weeding = compute_sandbox_weeding(payload.land_area_are)
        sandbox_pesticide = compute_sandbox_pesticide()
        sandbox_fertilizer = compute_sandbox_fertilizer(
            duck_count=payload.duck_count,
            t_active=calendar_result["t_active"],
            n_survive=n_survive,
            land_area_are=payload.land_area_are,
            constants=constants,
        )
        sandbox_infra = compute_sandbox_infrastructure()

        # Persist history if user authenticated
        if user_id is not None:
            self._save_history(
                user_id=user_id,
                payload=payload,
                age_flag=age_flag,
                density_result=density_result,
                calendar_result=calendar_result,
                n_survive=n_survive,
                yield_result=yield_result,
                econ=econ,
                warnings=warnings,
            )

        return DSSSimulationResponse(
            # Age
            age_flag=age_flag,
            # Density
            density_are=float(round(d, 7)),
            density_ha=float(round(d_ha, 5)),
            density_status=density_status,
            # Calendar
            HST_in=calendar_result["HST_in"],
            HST_out=calendar_result["HST_out"],
            t_active=calendar_result["t_active"],
            D_in=calendar_result["D_in"],
            D_out=calendar_result["D_out"],
            harvest_hst_min=calendar_result["harvest_hst_min"],
            harvest_hst_max=calendar_result["harvest_hst_max"],
            D_panen_min=calendar_result["D_panen_min"],
            D_panen_max=calendar_result["D_panen_max"],
            # Survival
            N_survive=n_survive,
            # Yield
            Yield_are_pred=float(round(yield_result["Yield_are_pred"], 7)),
            Yield_total_pred=float(round(yield_total_pred, 4)),
            # Economics
            Revenue_gabah=float(round(econ["Revenue_gabah"], 2)),
            Revenue_duck_potential=float(round(econ["Revenue_duck_potential"], 2)),
            Cost_duck_buy=float(round(econ["Cost_duck_buy"], 2)),
            Cost_feed=float(round(econ["Cost_feed"], 2)),
            Core_Cash_Cost=float(round(econ["Core_Cash_Cost"], 2)),
            Total_Revenue_DSS=float(round(econ["Total_Revenue_DSS"], 2)),
            Net_Cash_Contribution_DSS=float(round(econ["Net_Cash_Contribution_DSS"], 2)),
            # Warnings
            warnings=warnings,
            # Sandbox
            sandbox=SandboxOutputs(
                weeding=SandboxWeeding(**sandbox_weeding),
                pesticide=SandboxPesticide(**sandbox_pesticide),
                fertilizer=SandboxFertilizer(**sandbox_fertilizer),
                infrastructure=SandboxInfrastructure(**sandbox_infra),
            ),
        )

    def list_histories(self, user_id: str) -> HistoryListResponse:
        from app.repositories.history_repository import history_repository
        from app.schemas.dss import HistoryListItem, HistorySummary

        histories = history_repository.list_by_user(user_id)
        items = []
        for h in histories:
            if hasattr(h, "net_cash_contribution_dss"):
                # v3
                items.append(
                    HistoryListItem(
                        id=h.id,
                        schema_version=h.schema_version,
                        created_at=h.created_at.date(),
                        summary=HistorySummary(
                            rice_variety=h.rice_variety,
                            planting_system=h.planting_system,
                            duck_count=h.duck_count,
                            land_area_are=h.land_area_are,
                            density_are=h.density_are,
                            d_panen_min=date_type.fromisoformat(h.d_panen_min),
                            d_panen_max=date_type.fromisoformat(h.d_panen_max),
                            yield_total_pred=h.yield_total_pred,
                        ),
                    )
                )
        return HistoryListResponse(data=items)

    def get_history(self, history_id: str, user_id: str) -> DSSSimulationResponse:
        from app.repositories.history_repository import history_repository

        history = history_repository.get_by_id_and_user(history_id, user_id)
        if history is None or not hasattr(history, "net_cash_contribution_dss"):
            raise ResourceNotFoundError(
                message=f"History '{history_id}' was not found.", field="history_id"
            )

        warnings = json.loads(history.warnings_json)
        constants = lookup_repository.get_constants()
        sandbox = SandboxOutputs(
            weeding=SandboxWeeding(**compute_sandbox_weeding(history.land_area_are)),
            pesticide=SandboxPesticide(**compute_sandbox_pesticide()),
            fertilizer=SandboxFertilizer(
                **compute_sandbox_fertilizer(
                    duck_count=history.duck_count,
                    t_active=history.t_active,
                    n_survive=history.n_survive,
                    land_area_are=history.land_area_are,
                    constants=constants,
                )
            ),
            infrastructure=SandboxInfrastructure(**compute_sandbox_infrastructure()),
        )
        return DSSSimulationResponse(
            age_flag=history.age_flag,
            density_are=history.density_are,
            density_ha=history.density_ha,
            density_status=history.density_status,
            HST_in=history.hst_in,
            HST_out=history.hst_out,
            t_active=history.t_active,
            D_in=date_type.fromisoformat(history.d_in),
            D_out=date_type.fromisoformat(history.d_out),
            harvest_hst_min=history.harvest_hst_min,
            harvest_hst_max=history.harvest_hst_max,
            D_panen_min=date_type.fromisoformat(history.d_panen_min),
            D_panen_max=date_type.fromisoformat(history.d_panen_max),
            N_survive=history.n_survive,
            Yield_are_pred=history.yield_are_pred,
            Yield_total_pred=history.yield_total_pred,
            Revenue_gabah=history.revenue_gabah,
            Revenue_duck_potential=history.revenue_duck_potential,
            Cost_duck_buy=history.cost_duck_buy,
            Cost_feed=history.cost_feed,
            Core_Cash_Cost=history.core_cash_cost,
            Total_Revenue_DSS=history.total_revenue_dss,
            Net_Cash_Contribution_DSS=history.net_cash_contribution_dss,
            warnings=warnings,
            sandbox=sandbox,
        )

    def delete_history(self, history_id: str, user_id: str) -> DeleteHistoryResponse:
        from app.repositories.history_repository import history_repository

        deleted = history_repository.delete_by_id_and_user(history_id, user_id)
        if not deleted:
            raise ResourceNotFoundError(
                message=f"History '{history_id}' was not found.", field="history_id"
            )
        return DeleteHistoryResponse(message="Simulation history deleted successfully")

    def _find_variety(self, code: str) -> RiceVariety:
        variety = lookup_repository.get_rice_variety(code)
        if variety is None:
            raise InvalidReferenceError(
                message=f"Unknown rice_variety '{code}'. Valid values: 'sertani', 'inpari'.",
                field="rice_variety",
            )
        return variety

    def _find_planting_system(self, code: str) -> PlantingSystem:
        ps = lookup_repository.get_planting_system(code)
        if ps is None:
            raise InvalidReferenceError(
                message=(
                    f"Unknown planting_system '{code}'. "
                    "Valid values: 'jajar_legowo' (Jajar Legowo 2:1 only), 'tegel'."
                ),
                field="planting_system",
            )
        return ps

    def _save_history(
        self,
        user_id: str,
        payload: DSSSimulationRequest,
        age_flag: str,
        density_result: dict,
        calendar_result: dict,
        n_survive: int,
        yield_result: dict,
        econ: dict,
        warnings: list[str],
    ) -> None:
        from app.repositories.history_repository import history_repository
        from app.domain.models import SimulationHistory

        history = SimulationHistory(
            id=history_repository.new_id(),
            user_id=user_id,
            schema_version=3,
            land_area_are=payload.land_area_are,
            duck_count=payload.duck_count,
            rice_variety=payload.rice_variety,
            planting_system=payload.planting_system,
            duck_age_days=payload.duck_age_days,
            planting_date=payload.planting_date.isoformat(),
            p_duck_buy=payload.p_duck_buy,
            age_flag=age_flag,
            density_are=float(round(density_result["d"], 7)),
            density_ha=float(round(density_result["d_ha"], 5)),
            density_status=density_result["density_status"],
            hst_in=calendar_result["HST_in"],
            hst_out=calendar_result["HST_out"],
            t_active=calendar_result["t_active"],
            d_in=calendar_result["D_in"].isoformat(),
            d_out=calendar_result["D_out"].isoformat(),
            harvest_hst_min=calendar_result["harvest_hst_min"],
            harvest_hst_max=calendar_result["harvest_hst_max"],
            d_panen_min=calendar_result["D_panen_min"].isoformat(),
            d_panen_max=calendar_result["D_panen_max"].isoformat(),
            n_survive=n_survive,
            yield_are_pred=float(round(yield_result["Yield_are_pred"], 7)),
            yield_total_pred=float(round(yield_result["Yield_total_pred"], 4)),
            revenue_gabah=float(round(econ["Revenue_gabah"], 2)),
            revenue_duck_potential=float(round(econ["Revenue_duck_potential"], 2)),
            cost_duck_buy=float(round(econ["Cost_duck_buy"], 2)),
            cost_feed=float(round(econ["Cost_feed"], 2)),
            core_cash_cost=float(round(econ["Core_Cash_Cost"], 2)),
            total_revenue_dss=float(round(econ["Total_Revenue_DSS"], 2)),
            net_cash_contribution_dss=float(round(econ["Net_Cash_Contribution_DSS"], 2)),
            warnings_json=json.dumps(warnings, ensure_ascii=False),
            created_at=history_repository.now(),
        )
        history_repository.create_v3(user_id=user_id, history=history)


dss_service = DSSService()
