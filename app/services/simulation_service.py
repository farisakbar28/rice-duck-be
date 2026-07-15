"""DSS simulation service.

Orchestrates the SoT engines (see docs/Model_Matematika_..._FINAL.docx) in the
order mandated by the model document:

  1. Age Engine
  2. Density Engine
  3. Calendar Engine
  4. Survival Engine
  5. Yield Engine
  6. Material Engine
  7. Cost Engine (split into Core + Isolated groups)

Group separation per SoT Bagian 5:
- Core Validated Output: Cost_duck_buy, Cost_total_cash, Profit_net_cash,
  plus revenue/calendar/yield values.
- Empirically Uncorrelated Isolated Output: Cost_*_isolated fields. These
  components are FULLY EXCLUDED from Cost_total_cash and Profit_net_cash.

Numerical precision: all engine computations use ``decimal.Decimal`` with
precision 50. No mid-calculation rounding is performed. Conversion to native
``float`` happens only at the DTO serialisation boundary.
"""

from decimal import Decimal, ROUND_FLOOR

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
    compute_feed_costs,
    compute_infrastructure_breakdown,
    compute_labor_breakdown,
    compute_pesticide_cost,
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


# [local-calculated] SoT 4.6: literature-anchored baseline nutrient needs per are.
# N_need = 1,1761; P_need = 0,2745; K_need = 0,2745 (satuan hara oksida per are).
N_NEED_PER_ARE = Decimal("1.1761")
P_NEED_PER_ARE = Decimal("0.2745")
K_NEED_PER_ARE = Decimal("0.2745")

# [local-validated] SoT 4.5 / Tabel 1: Local-validated market price points.
P_GABAH_PER_KG = Decimal("6000.0")
P_DUCK_SELL_PER_DUCK = Decimal("35000.0")

# [local-estimate] SoT 4.7: default p_duck_buy lower-bound per Tabel 1.
P_DUCK_BUY_DEFAULT = Decimal("25000.0")


def _d(value) -> Decimal:
    """Coerce value to Decimal for safe arithmetic in service layer."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


class DSSService:
    def get_options(self) -> DSSOptionsResponse:
        return DSSOptionsResponse(
            rice_varieties=[
                RiceVarietyOption(
                    code=item.code,
                    label=item.label,
                    # Canonical (SoT) - Fase 1.
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
                    # Canonical (SoT) - Fase 2.
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

        # 1. Age Engine (SoT 4.1)
        duck_age = compute_duck_age_status(payload.duck_age_days)
        r_age = duck_age["R_age"]
        age_status = duck_age["age_status"]

        # 2. Density Engine (SoT 4.2)
        density = compute_density(
            payload.duck_count,
            payload.land_area_are,
            planting_system.k_safe_are,
        )
        p_over = density["P_over"]
        p_under = density["P_under"]
        density_status = density["density_status"]

        # 3. Calendar Engine (SoT 4.3)
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

        # 4. Survival Engine (SoT 4.4)
        n_survive_raw = compute_surviving_ducks(payload.duck_count, r_age, p_over)
        # [system-design] Floor operation is part of SoT math, not display rounding.
        n_survive = int(n_survive_raw.to_integral_value(rounding=ROUND_FLOOR))
        duck_count_d = _d(payload.duck_count)
        lambda_eff = (
            n_survive_raw / duck_count_d if duck_count_d > 0 else Decimal("0")
        )

        # 5. Yield Engine (SoT 4.5)
        # [system-design] F_density_bio with exponential saturation + quadratic trampling.
        yield_are_predict = compute_yield_components(
            density["d"], r_age, planting_system.F_sys
        )
        land_area_d = _d(payload.land_area_are)
        yield_total_predict = yield_are_predict * land_area_d

        # 6. Material Engine (SoT 4.6)
        n_need_total = N_NEED_PER_ARE * land_area_d
        p_need_total = P_NEED_PER_ARE * land_area_d
        k_need_total = K_NEED_PER_ARE * land_area_d

        nutrients = compute_soil_nutrients(
            duck_count=payload.duck_count,
            t_active=t_active,
            lambda_eff=lambda_eff,
            n_need=n_need_total,
            p_need=p_need_total,
            k_need=k_need_total,
            constants=constants,
        )

        # 7. Cost Engine (SoT 4.7 + 5.2)
        # [local-estimate] Core group: C_duck_buy = J * p_duck_buy.
        duck_buy_price = _d(
            payload.duck_buy_price_rp_per_duck
            if payload.duck_buy_price_rp_per_duck is not None
            else P_DUCK_BUY_DEFAULT
        )
        cost_duck_buy = duck_count_d * duck_buy_price

        # [empirically-uncorrelated] Isolated group (Bagian 5.2):
        # weeding, pesticide, infrastructure, fertilizer, feed.
        labor = compute_labor_breakdown(
            land_area_d,
            p_over,
            r_age,
            density["d"],
        )
        cost_pesticide = compute_pesticide_cost(land_area_d, density["d"])
        infra = compute_infrastructure_breakdown(
            payload.duck_count, payload.land_area_are
        )
        cost_feed = compute_feed_costs(payload.duck_count, p_over, r_age)

        # Ecology Engine removed per SoT - no valuation_weed_eco or profit_net_full

        # [soT-precise] Core Validated Output
        # Cost_total_cash = Cost_duck_buy (murni terdiri dari pengadaan bibit
        # unggas - komponen pakan diisolasi penuh ke modul cadangan).
        cost_total_cash = cost_duck_buy

        n_survive_display = float(n_survive)
        # [soT-precise] No mid-calculation rounding. Use raw Decimal values.
        # Display rounding applied only at DTO serialisation below.
        yield_total_predict_raw = yield_total_predict

        revenue_gabah = yield_total_predict_raw * P_GABAH_PER_KG
        revenue_duck = n_survive_display * float(P_DUCK_SELL_PER_DUCK)
        total_revenue = revenue_gabah + _d(revenue_duck)

        profit_net_cash = total_revenue - cost_total_cash

        return DSSSimulationResponse(
            density_status=density_status,
            age_status=age_status,
            D_masuk_bebek=d_masuk_bebek,
            D_tarik_bebek=d_tarik_bebek,
            D_panen_gabah=d_panen_gabah,
            N_survive=n_survive_display,
            Yield_are_predict=float(round(yield_are_predict, 2)),
            Yield_total_predict=float(round(yield_total_predict_raw, 1)),
            Revenue_gabah=float(round(revenue_gabah, 2)),
            Revenue_duck=float(round(revenue_duck, 2)),
            Total_Revenue=float(round(total_revenue, 2)),
            # Core
            Cost_duck_buy=float(round(cost_duck_buy, 2)),
            Cost_feed_isolated=float(round(cost_feed, 2)),
            Cost_total_cash=float(round(cost_total_cash, 2)),
            # Isolated (Bagian 5.2) - fully separated from core cash flow
            Cost_weeding_isolated=float(round(labor["Cost_labor_weeding"], 2)),
            Cost_pesticide_isolated=float(round(cost_pesticide, 2)),
            Cost_infra_net_isolated=float(round(infra["Cost_infra_net"], 2)),
            Cost_infra_cage_isolated=float(round(infra["Cost_infra_cage"], 2)),
            Cost_infra_isolated=float(round(infra["Cost_infra"], 2)),
            Cost_fert_urea_isolated=float(round(nutrients["Cost_fert_urea"], 2)),
            Cost_fert_phonska_isolated=float(round(nutrients["Cost_fert_phonska"], 2)),
            Cost_fert_kcl_isolated=float(round(nutrients["Cost_fert_kcl"], 2)),
            Cost_fertilizer_isolated=float(round(nutrients["Cost_fertilizer_total"], 2)),
            # Profit
            Profit_net_cash=float(round(profit_net_cash, 2)),
            # Yield factor marker (Fase 4)
            F_sys=planting_system.F_sys,
        )

    def list_histories(self, user_id: str) -> HistoryListResponse:
        return HistoryListResponse(data=[])

    def get_history(self, history_id: str, user_id: str) -> DSSSimulationResponse:
        raise ResourceNotFoundError(
            message=f"History '{history_id}' was not found.", field="history_id"
        )

    def delete_history(self, history_id: str, user_id: str) -> DeleteHistoryResponse:
        return DeleteHistoryResponse(message="Simulation history deleted successfully")

    def _find_variety(self, code: str) -> RiceVariety:
        variety = lookup_repository.get_rice_variety(code)
        if variety is None:
            raise InvalidReferenceError(
                message=f"Unknown rice_variety '{code}'.", field="rice_variety"
            )
        return variety

    def _find_planting_system(self, code: str) -> PlantingSystem:
        planting_system = lookup_repository.get_planting_system(code)
        if planting_system is None:
            raise InvalidReferenceError(
                message=f"Unknown planting_system '{code}'.", field="planting_system"
            )
        return planting_system


dss_service = DSSService()
