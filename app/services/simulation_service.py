import math
from datetime import timedelta

from app.core.exceptions import InvalidReferenceError, ResourceNotFoundError
from app.domain.models import DSSConstants, PlantingSystem, RiceVariety
from app.engines.formula_engine import (
    compute_calendar_milestones,
    compute_duck_age_status,
    compute_density,
    compute_surviving_ducks,
    compute_yield_components,
)
from app.engines.impact_engine import (
    compute_ecology_weed,
    compute_feed_costs,
    compute_infrastructure_breakdown,
    compute_labor_breakdown,
    compute_soil_nutrients,
)
from app.repositories.lookup_repository import lookup_repository
from app.schemas.dss import (
    DSSOptionsResponse,
    DSSSimulationRequest,
    DSSSimulationResponse,
    HistoryListResponse,
    DeleteHistoryResponse,
    PlantingSystemOption,
    RiceVarietyOption,
)


class DSSService:
    def get_options(self) -> DSSOptionsResponse:
        return DSSOptionsResponse(
            rice_varieties=[
                RiceVarietyOption(
                    code=item.code,
                    label=item.label,
                    # Canonical (SoT) — Fase 1.
                    hst_panen=item.hst_panen,
                    # Deprecated, additive (keputusan #2).
                    hst_masuk=item.hst_masuk,
                    hst_heading=item.hst_heading,
                    harvest_age_days=item.harvest_age_days,
                    risk_note=item.risk_note,
                    hst_masuk_range={
                        "min": item.hst_masuk_min,
                        "max": item.hst_masuk_max,
                    },
                    hst_heading_range={
                        "min": item.hst_heading_min,
                        "max": item.hst_heading_max,
                    },
                    status=item.status,
                )
                for item in lookup_repository.list_rice_varieties()
            ],
            planting_systems=[
                PlantingSystemOption(
                    code=item.code,
                    label=item.label,
                    # Canonical (SoT) — Fase 2.
                    k_safe_are=item.k_safe_are,
                    F_sys=item.F_sys,
                    # Deprecated, additive (keputusan #2). Values kept in sync
                    # with canonical.
                    k_max_are=item.k_max_are,
                    f_yield=item.f_yield,
                    note=item.note,
                    k_max_range_are={
                        "min": item.k_max_min_are,
                        "max": item.k_max_max_are,
                    },
                    limited_test_max_are=item.limited_test_max_are,
                    k_max_status=item.k_max_status,
                    f_yield_status=item.f_yield_status,
                )
                for item in lookup_repository.list_planting_systems()
            ],
        )

    def simulate(
        self,
        payload: DSSSimulationRequest,
        user_id: str | None = None,
    ) -> DSSSimulationResponse:
        variety = self._find_variety(payload.rice_variety)
        planting_system = self._find_planting_system(payload.planting_system)
        constants = lookup_repository.get_constants()

        # 1. Age Engine
        duck_age = compute_duck_age_status(payload.duck_age_days)
        r_age = duck_age["R_age"]
        age_status = duck_age["age_status"]

        # 2. Density Engine (uses canonical k_safe_are — Fase 2).
        density = compute_density(
            payload.duck_count,
            payload.land_area_are,
            planting_system.k_safe_are,
        )
        p_over = density["P_over"]
        p_under = density["P_under"]
        density_status = density["density_status"]

        # Timeline logic — Fase 1: D_masuk_bebek = D_tanam + 21, D_tarik_bebek = D_tanam + 65.
        milestones = compute_calendar_milestones(
            payload.planting_date,
            variety.hst_panen,
            variety.hst_masuk,
            variety.hst_heading,
        )
        d_masuk_bebek = milestones["D_masuk_bebek"]
        d_tarik_bebek = milestones["D_tarik_bebek"]
        t_active = milestones["t_active"]
        d_panen_gabah = milestones["D_panen_gabah"]

        # 3. Survival Engine
        n_survive = compute_surviving_ducks(payload.duck_count, r_age, p_over)

        # 4. Yield Engine — uses canonical F_sys.
        yield_are_predict = compute_yield_components(
            p_under, p_over, r_age, planting_system.F_sys, 1.0
        )
        yield_total_predict = yield_are_predict * payload.land_area_are

        # 5. Material Engine
        # SoT FINAL_BANGET worked example back-solves the standard nutrient
        # needs used by the least-cost fertilizer mix.
        n_need_are = 1.794894213125 * payload.land_area_are
        p_need_are = 0.49014669499999997 * payload.land_area_are
        k_need_are = 0.6672297837500001 * payload.land_area_are

        nutrients = compute_soil_nutrients(
            duck_count=payload.duck_count,
            t_active=t_active,
            lambda_eff=n_survive / payload.duck_count if payload.duck_count > 0 else 0,
            n_need=n_need_are,
            p_need=p_need_are,
            k_need=k_need_are,
            constants=constants,
        )

        # 6. Cost Engine — Fase 2 breakdown.
        cost_feed = compute_feed_costs(payload.duck_count, p_over, r_age)
        labor = compute_labor_breakdown(
            payload.land_area_are,
            p_over,
            r_age,
            density["d"],
        )
        infra = compute_infrastructure_breakdown(
            payload.duck_count, payload.land_area_are
        )

        # 7. Ekologi Engine — Fase 3: basis = Cost_labor_base (NOT total).
        valuation_weed_eco = compute_ecology_weed(
            labor["Cost_labor_base"], density["d"], p_over
        )

        cost_duck_buy = payload.duck_count * (payload.duck_buy_price_rp_per_duck or 25000.0)
        cost_pesticide = 6440.0

        cost_total_cash = (
            cost_duck_buy
            + cost_feed
            + labor["Cost_labor_total"]
            + infra["Cost_infra"]
            + nutrients["Cost_fertilizer_total"]
            + cost_pesticide
        )

        n_survive_display = float(math.floor(n_survive))
        yield_are_display = math.floor(yield_are_predict * 100.0) / 100.0
        yield_total_display = round(yield_are_display * payload.land_area_are, 1)

        revenue_gabah = yield_total_display * 6000.0
        revenue_duck = n_survive_display * 35000.0
        total_revenue = revenue_gabah + revenue_duck

        profit_net_cash = total_revenue - cost_total_cash
        profit_net_full = profit_net_cash + valuation_weed_eco

        return DSSSimulationResponse(
            density_status=density_status,
            age_status=age_status,
            D_masuk_bebek=d_masuk_bebek,
            D_tarik_bebek=d_tarik_bebek,
            D_panen_gabah=d_panen_gabah,
            N_survive=n_survive_display,
            Yield_are_predict=yield_are_display,
            Yield_total_predict=yield_total_display,
            Revenue_gabah=round(revenue_gabah, 2),
            Revenue_duck=round(revenue_duck, 2),
            Total_Revenue=round(total_revenue, 2),
            Cost_duck_buy=round(cost_duck_buy, 2),
            Cost_feed=round(cost_feed, 2),
            Cost_labor_base=round(labor["Cost_labor_base"], 2),
            Cost_labor_weed_hired=round(labor["Cost_labor_weed_hired"], 2),

            Cost_labor_total=round(labor["Cost_labor_total"], 2),
            Cost_infra_net=round(infra["Cost_infra_net"], 2),
            Cost_infra_cage=round(infra["Cost_infra_cage"], 2),
            Cost_infra=round(infra["Cost_infra"], 2),
            Cost_fertilizer_total=round(nutrients["Cost_fertilizer_total"], 2),
            Cost_fert_urea=round(nutrients["Cost_fert_urea"], 2),
            Cost_fert_phonska=round(nutrients["Cost_fert_phonska"], 2),
            Cost_fert_kcl=round(nutrients["Cost_fert_kcl"], 2),
            Cost_pesticide=cost_pesticide,
            Cost_total_cash=round(cost_total_cash, 2),
            Profit_net_cash=round(profit_net_cash, 2),
            Valuation_weed_eco=round(valuation_weed_eco, 2),
            Profit_net_full=round(profit_net_full, 2),
            F_sys=planting_system.F_sys,
        )

    def list_histories(self, user_id: str) -> HistoryListResponse:
        return HistoryListResponse(data=[])

    def get_history(self, history_id: str, user_id: str) -> DSSSimulationResponse:
        raise ResourceNotFoundError(message=f"History '{history_id}' was not found.", field="history_id")

    def delete_history(self, history_id: str, user_id: str) -> DeleteHistoryResponse:
        return DeleteHistoryResponse(message="Simulation history deleted successfully")
    def _find_variety(self, code: str) -> RiceVariety:
        variety = lookup_repository.get_rice_variety(code)
        if variety is None:
            raise InvalidReferenceError(message=f"Unknown rice_variety '{code}'.", field="rice_variety")
        return variety

    def _find_planting_system(self, code: str) -> PlantingSystem:
        planting_system = lookup_repository.get_planting_system(code)
        if planting_system is None:
            raise InvalidReferenceError(message=f"Unknown planting_system '{code}'.", field="planting_system")
        return planting_system


dss_service = DSSService()
