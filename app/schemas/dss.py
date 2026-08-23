"""Schemas for the DSS Core SoT calculator.

Field semantics follow docs/Model Matematika Data Collection DSS Padi Bebek FINAL.md.

SoT §3: 7 mandatory inputs (land_area_are, duck_count, rice_variety, planting_system,
         duck_age_days, planting_date, p_duck_buy)
SoT §11: Canonical output semantics
"""

from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Options endpoint
# ---------------------------------------------------------------------------


class RiceVarietyOption(BaseModel):
    code: str
    label: str
    # SoT §6.1: Sertani 100–110, Inpari 109–116
    hst_panen_min: int
    hst_panen_max: int
    risk_note: str
    status: str


class PlantingSystemOption(BaseModel):
    code: str
    label: str
    # SoT §5.1: recommended density ceiling per system
    recommended_density_max_are: float
    recommended_density_min_are: float
    note: str


class DSSOptionsResponse(BaseModel):
    rice_varieties: list[RiceVarietyOption]
    planting_systems: list[PlantingSystemOption]


# ---------------------------------------------------------------------------
# Input — SoT §3: 7 mandatory inputs
# ---------------------------------------------------------------------------


class DSSSimulationRequest(BaseModel):
    """7 mandatory inputs per SoT §3.

    All fields are required. No silent fallbacks.
    p_duck_buy: mandatory, >= 0. Value 0 is valid (no current-cycle cash purchase).
    duck_age_days: mandatory, >= 0. No default.
    planting_date: mandatory. No date fallback.
    """

    model_config = ConfigDict(
        # JSON permits non-finite numeric tokens in some parsers, but they do
        # not represent valid production measurements and would invalidate
        # Decimal-based density, yield, and economics calculations.
        allow_inf_nan=False,
        json_schema_extra={
            "example": {
                "land_area_are": 10.0,
                "duck_count": 20,
                "rice_variety": "sertani",
                "planting_system": "jajar_legowo",
                "duck_age_days": 21,
                "planting_date": "2024-04-22",
                "p_duck_buy": 15000,
            }
        }
    )

    land_area_are: float = Field(gt=0, description="Luas lahan aktif > 0 are")
    duck_count: int = Field(gt=0, description="Populasi awal bebek > 0")
    rice_variety: str = Field(min_length=1, description="'sertani' atau 'inpari'")
    planting_system: str = Field(
        min_length=1, description="'jajar_legowo' (2:1 only) atau 'tegel'"
    )
    duck_age_days: int = Field(
        ge=0, description="Umur bebek saat masuk sawah (hari). Wajib, tidak ada default."
    )
    planting_date: date = Field(description="Tanggal tanam. Wajib, tidak ada fallback.")
    p_duck_buy: float = Field(
        ge=0,
        description=(
            "Harga beli bebek (Rp/ekor). Wajib, >= 0. "
            "Nilai 0 sah bila tidak ada current-cycle cash purchase."
        ),
    )


# ---------------------------------------------------------------------------
# Output — SoT §11: Canonical Output Semantics
# ---------------------------------------------------------------------------


class SandboxWeeding(BaseModel):
    """SoT §10.1: Weeding Research/Sandbox output (per-event only)."""
    k_weeding_rp_per_are_event: float
    R_weeding: float
    Weeding_residual_per_are_event: float
    Weeding_avoided_per_are_event: float
    Weeding_residual_total_one_event: float
    Weeding_avoided_total_one_event: float
    note: str


class SandboxPesticide(BaseModel):
    """SoT §10.2: Pesticide Research/Sandbox — non-monetary indicator."""
    Pesticide_reduction_upper_bound: float
    note: str


class SandboxFertilizer(BaseModel):
    """SoT §10.3: Fertilizer Research/Sandbox — literature-uncalibrated."""
    Cost_fertilizer_total: float
    Cost_fert_urea: float
    Cost_fert_phonska: float
    Cost_fert_kcl: float
    Q_phonska: float
    Q_urea: float
    Q_kcl: float
    note: str


class SandboxInfrastructure(BaseModel):
    """SoT §10.4: Infrastructure — context/reference only, without a cost formula."""
    note: str


class SandboxOutputs(BaseModel):
    """SoT §10: Research/Sandbox outputs. NOT included in Core_Cash_Cost or Net_Cash_Contribution_DSS."""
    weeding: SandboxWeeding
    pesticide: SandboxPesticide
    fertilizer: SandboxFertilizer
    infrastructure: SandboxInfrastructure


class DSSSimulationResponse(BaseModel):
    """SoT §11: Canonical Output Semantics.

    All Core fields follow SoT §11 naming exactly.
    Sandbox outputs are nested under 'sandbox' and have zero effect on Core.
    """

    # SoT §4: Age Readiness Engine
    age_flag: str                   # TOO_YOUNG | RECOMMENDED | ABOVE_RECOMMENDED_AGE

    # SoT §5: Density Engine
    density_are: float              # duck_count / land_area_are
    density_ha: float               # 100 * density_are
    density_status: str             # UNDER_DENSITY | RECOMMENDED | ABOVE_RECOMMENDED | OVERLOAD_HIGH_RISK

    # SoT §6: Calendar Engine
    HST_in: int                     # 21
    HST_out: int                    # 65
    t_active: int                   # 44
    D_in: date                      # planting_date + 21
    D_out: date                     # planting_date + 65
    harvest_hst_min: int            # Sertani: 100; Inpari: 109
    harvest_hst_max: int            # Sertani: 110; Inpari: 116
    D_panen_min: date               # planting_date + harvest_hst_min
    D_panen_max: date               # planting_date + harvest_hst_max

    # SoT §7: Survival Engine
    N_survive: int                  # J (d<=8) or floor(0.60*J) (d>8)

    # SoT §8: Yield Engine
    Yield_are_pred: float           # 47.8767507 kg/are (constant)
    Yield_total_pred: float         # Yield_are_pred * land_area_are

    # SoT §9: Core Economic Engine
    Revenue_gabah: float            # Yield_total_pred * 6000
    Revenue_duck_potential: float   # N_survive * 52500
    Cost_duck_buy: float            # duck_count * p_duck_buy
    Cost_feed: float                # duck_count * 20000
    Core_Cash_Cost: float           # Cost_duck_buy + Cost_feed
    Total_Revenue_DSS: float        # Revenue_gabah + Revenue_duck_potential
    Net_Cash_Contribution_DSS: float  # Total_Revenue_DSS - Core_Cash_Cost

    # SoT §11.1: Warnings
    warnings: list[str]

    # SoT §10: Research/Sandbox (informational only, does NOT affect Core)
    sandbox: SandboxOutputs


# ---------------------------------------------------------------------------
# History schemas
# ---------------------------------------------------------------------------


class HistorySummary(BaseModel):
    rice_variety: str
    planting_system: str
    duck_count: int
    land_area_are: float
    density_are: float
    d_panen_min: date
    d_panen_max: date
    yield_total_pred: float


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
    # Age
    age_flag: str
    # Density
    density_are: float
    density_ha: float
    density_status: str
    # Calendar
    hst_in: int
    hst_out: int
    t_active: int
    d_in: date
    d_out: date
    harvest_hst_min: int
    harvest_hst_max: int
    d_panen_min: date
    d_panen_max: date
    # Survival
    n_survive: int
    # Yield
    yield_are_pred: float
    yield_total_pred: float
    # Core Economics
    revenue_gabah: float
    revenue_duck_potential: float
    cost_duck_buy: float
    cost_feed: float
    core_cash_cost: float
    total_revenue_dss: float
    net_cash_contribution_dss: float
    # Warnings
    warnings: list[str]


class DeleteHistoryResponse(BaseModel):
    message: str


# ---------------------------------------------------------------------------
# Visualization schemas
# ---------------------------------------------------------------------------


class DensityZonePoint(BaseModel):
    """Density zone visualization point."""
    density: float
    density_status: str             # UNDER_DENSITY | RECOMMENDED | ABOVE_RECOMMENDED | OVERLOAD_HIGH_RISK
    is_recommended_jarwo: bool      # 2 <= d <= 4
    is_recommended_tegel: bool      # 2 <= d <= 3
    is_overload: bool               # d > 8
    survival_rate: float            # 1.0 (d<=8) or 0.60 (d>8)


class AgeZonePoint(BaseModel):
    """Age readiness zone visualization point."""
    age_days: int
    age_flag: str                   # TOO_YOUNG | RECOMMENDED | ABOVE_RECOMMENDED_AGE
    zone: str                       # "below_recommended" | "recommended" | "above_recommended"


class WaterfallNode(BaseModel):
    name: str
    amount: float
    type: str                       # "revenue" | "cost" | "total"


class ReferenceBenchmarks(BaseModel):
    recommended_density_max_jarwo: float = 4.0
    recommended_density_max_tegel: float = 3.0
    overload_threshold: float = 8.0
    yield_baseline_kg_per_are: float = 47.8767507


class VisualizationResponse(BaseModel):
    density_zones: list[DensityZonePoint]
    age_zones: list[AgeZonePoint]
    financial_waterfall: list[WaterfallNode]
    reference_benchmarks: ReferenceBenchmarks
    survival_note: str
    yield_note: str
