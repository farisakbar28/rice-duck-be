"""Schemas for the DSS Core SoT calculator.

Field semantics follow ``docs/Model_Matematika_Data_Collection_DSS_Padi_Bebek_FINAL_BANGET.md``
(Tabel 2.1 input, Tabel 2.2 proses, Tabel 2.3 output). Deprecation markers
indicate legacy fields retained for backward compatibility — they MUST stay
synchronised with the new canonical fields (see Fase 4 plan).

The optimizer/recommendation layer is intentionally NOT defined here. It
lives in ``app.schemas.optimizer`` and is served from
``/api/v1/optimizer/recommend``.
"""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


# -----------------------------------------------------------------------------
# Options endpoint
# -----------------------------------------------------------------------------

# Legacy field name; canonical name is ``hst_panen`` (Fase 1). Deprecated.
class RiceVarietyOption(BaseModel):
    code: str
    label: str

    # Canonical (SoT) — Fase 1: HST_panen per varietas (Sertani/Seratih=99, Inpari=112).
    # Catatan Finalisasi poin 8; Tabel 2.2.
    hst_panen: int

    # Deprecated (will be sunset). Retained for backward-compat; values are
    # now expressed as calendar reminders relative to D_tanam (see Tabel 2.3).
    # ``hst_masuk`` legacy = 20; ``hst_heading`` legacy = 65. Do NOT use these
    # for new code paths; call ``D_masuk_bebek``/``D_tarik_bebek`` directly.
    hst_masuk: int
    hst_heading: int

    # Deprecated: ``harvest_age_days`` is the legacy alias of ``hst_panen``.
    # Kept additive (per keputusan #2). Will be sunset.
    harvest_age_days: int

    risk_note: str

    # Deprecated ranges.
    hst_masuk_range: dict[str, int]
    hst_heading_range: dict[str, int]

    status: str


# Legacy field name; canonical name is ``F_sys`` (Fase 2). Deprecated.
class PlantingSystemOption(BaseModel):
    code: str
    label: str

    # Canonical (SoT) — Fase 1+2: K_safe per sistem tanam. Jarwo=4, Tegel=3.
    # Tabel 2.2.
    k_safe_are: float

    # Canonical (SoT) — Fase 2: F_sys per sistem tanam. Jarwo=1.00, Tegel=0.95.
    # Tabel 2.2 (Yield Engine). Tegel receives a PENALTY, not the legacy
    # 1.39 bonus.
    F_sys: float

    note: str

    # Deprecated: legacy names. Retained for backward-compat (keputusan #2).
    k_max_are: float
    f_yield: float

    k_max_range_are: dict[str, float]
    limited_test_max_are: float | None
    k_max_status: str
    f_yield_status: str


class DSSOptionsResponse(BaseModel):
    rice_varieties: list[RiceVarietyOption]
    planting_systems: list[PlantingSystemOption]


# -----------------------------------------------------------------------------
# Input — Tabel 2.1 SoT
# -----------------------------------------------------------------------------


class DSSSimulationRequest(BaseModel):
    """6 input inti + 1 kondisional (``p_duck_buy_manual`` muncul hanya jika
    ``U_duck < 14`` atau ``U_duck > 21``). Tabel 2.1.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "duck_count": 28,
                "land_area_are": 7,
                "planting_date": "2026-06-01",
                "rice_variety": "sertani",
                "planting_system": "jajar_legowo",
                "duck_age_days": 30,
                "duck_buy_price_rp_per_duck": 26500,
            }
        }
    )

    duck_count: int = Field(gt=0)
    land_area_are: float = Field(gt=0)
    planting_date: date
    rice_variety: str = Field(min_length=1)
    planting_system: str = Field(min_length=1)
    duck_age_days: int = Field(gt=0)
    duck_buy_price_rp_per_duck: float | None = Field(default=None, gt=0)


# Internal DTO used by ``simulation_service``.
class DSSInput(BaseModel):
    duck_count: int
    land_area_are: float
    planting_date: date
    rice_variety: str
    planting_system: str
    duck_age_days: int
    duck_buy_price_rp_per_duck: float | None = None


# -----------------------------------------------------------------------------
# Output — Tabel 2.3 SoT
# -----------------------------------------------------------------------------


class DSSSimulationResponse(BaseModel):
    # Evaluasi agronomi & operasional
    density_status: str
    age_status: str
    D_masuk_bebek: date
    D_tarik_bebek: date
    D_panen_gabah: date  # NEW — Fase 1
    N_survive: float

    # Prediksi panen (Yield)
    Yield_are_predict: float
    Yield_total_predict: float

    # Komponen pendapatan (Revenue)
    Revenue_gabah: float
    Revenue_duck: float
    Total_Revenue: float

    # Komponen biaya detail (Cost) — Fase 2 additive breakdown
    Cost_duck_buy: float
    Cost_feed_isolated: float
    Cost_weeding_isolated: float
    Cost_pesticide_isolated: float
    Cost_infra_isolated: float
    Cost_fertilizer_isolated: float
    Cost_infra_net_isolated: float
    Cost_infra_cage_isolated: float
    Cost_fert_urea_isolated: float
    Cost_fert_phonska_isolated: float
    Cost_fert_kcl_isolated: float
    # Core
    Cost_total_cash: float

    # Profit
    Profit_net_cash: float
    # Valuation_weed_eco and Profit_net_full removed per SoT
    # Fase 4 — additive deprecation marker (not a value field).
    # New canonical yield factor name; equals ``planting_systems[].F_sys`` at request time.
    F_sys: float


# -----------------------------------------------------------------------------
# History — Fase 5 explicit columns
# -----------------------------------------------------------------------------


class HistorySummary(BaseModel):
    rice_variety: str
    planting_system: str
    duck_count: int
    land_area_are: float
    actual_density_are: float
    d_panen_gabah: date
    estimated_total_yield_kg: float


class HistoryListItem(BaseModel):
    id: str
    schema_version: int
    created_at: date
    summary: HistorySummary


class HistoryListResponse(BaseModel):
    data: list[HistoryListItem]


class HistoryDetailResponse(BaseModel):
    id: str
    schema_version: int
    created_at: date
    # Agronomi & operasional
    density_status: str
    age_status: str
    d_masuk_bebek: date
    d_tarik_bebek: date
    d_panen_gabah: date
    n_survive: float
    # Yield
    yield_are_predict: float
    yield_total_predict: float
    # Revenue
    revenue_gabah: float
    revenue_duck: float
    total_revenue: float
    # Cost detail
    cost_duck_buy: float
    cost_feed_isolated: float
    cost_weeding_isolated: float
    cost_pesticide_isolated: float
    cost_infra_isolated: float
    cost_fertilizer_isolated: float
    cost_infra_net_isolated: float
    cost_infra_cage_isolated: float
    cost_fert_urea_isolated: float
    cost_fert_phonska_isolated: float
    cost_fert_kcl_isolated: float
    cost_total_cash: float
    # Profit
    profit_net_cash: float


class DeleteHistoryResponse(BaseModel):
    message: str


# -----------------------------------------------------------------------------
# Visualization — Graph Data Contracts
# -----------------------------------------------------------------------------


class DensityPoint(BaseModel):
    density: float
    jarwo_yield_factor: float
    tegel_yield_factor: float
    is_safe_jarwo: bool = True


class AgePoint(BaseModel):
    age_days: int
    risk_ratio: float
    survival_ceiling: float


class WaterfallNode(BaseModel):
    label: str
    value: float
    node_type: str  # "revenue", "cost", "profit"


class ReferenceBenchmarks(BaseModel):
    k_safe_jarwo: float = 4.0
    k_safe_tegel: float = 3.0
    k_max_saturation: float = 8.0


class FinancialAbsorptionBreakdown(BaseModel):
    core_validated_liquid_cash: float
    empirically_uncorrelated_isolated_shadow_costs: float


class VisualizationsObject(BaseModel):
    density_curve: list[DensityPoint]
    age_vulnerability: list[AgePoint]
    financial_waterfall: list[WaterfallNode]


class VisualizationResponse(BaseModel):
    density_curve: list[DensityPoint]
    age_vulnerability: list[AgePoint]
    reference_benchmarks: ReferenceBenchmarks
    financial_absorption: FinancialAbsorptionBreakdown
    visualizations: VisualizationsObject


