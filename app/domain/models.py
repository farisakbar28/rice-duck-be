from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class RiceVariety:
    code: str
    label: str
    hst_panen: int  # Canonical (SoT) — Fase 1: Tabel 2.2 Calendar Engine
    # Deprecated: legacy fields retained for backward-compat. New code paths
    # must use ``D_masuk_bebek``/``D_tarik_bebek`` (Tabel 2.3).
    hst_masuk: int
    hst_heading: int
    harvest_age_days: int
    risk_note: str
    hst_masuk_min: int
    hst_masuk_max: int
    hst_heading_min: int
    hst_heading_max: int
    status: str


@dataclass(frozen=True)
class PlantingSystem:
    code: str
    label: str
    # Canonical (SoT) — Fase 2: K_safe & F_sys. Tabel 2.2.
    k_safe_are: float
    F_sys: float
    # Deprecated aliases retained for backward-compat (keputusan #2).
    k_max_are: float
    f_yield: float
    note: str = ""
    k_safe_min_are: float = 0
    k_safe_max_are: float = 0
    # Deprecated ranges.
    k_max_min_are: float = 0
    k_max_max_are: float = 0
    limited_test_max_are: float | None = None
    k_max_status: str = "estimation"
    f_yield_status: str = "estimation"



    recommended_density_min_are: float = 2.0
    recommended_density_max_are: float = 4.0


@dataclass(frozen=True)
class DSSConstants:
    survival_lambda: float
    t_max_eff_days: int
    t_phase_1_days: int
    local_feed_warning_phase_days: int
    dung_phase_1_total_kg: float
    dung_phase_2_daily_kg: float
    minimum_density_are: float
    p_max: float
    penalty_gamma: float
    # Fase 6 cleanup: ``alpha_local`` is a deprecated Generasi-A artifact
    # (Xiong-style calibration in FINAL.md). SoT ``_terbaru`` uses the
    # ``48.039 * F_density * F_age * F_sys * F_var`` formula and does not
    # require ``alpha_local``. The field is removed from active contracts.
    daily_duck_grazing_hours: float
    baseline_grazing_hours: float
    feed_requirement_kg_per_duck_day: float | None
    feed_natural_saving_rate: float | None
    feed_greedy_kg_per_duck_day: float | None
    rice_duck_price_rp_per_kg: float | None
    duck_sale_price_rp_per_duck: float
    duck_buy_price_rp_per_duck: float
    duck_target_out_max_days: int
    duck_buy_price_fallback_min_rp: float
    duck_buy_price_fallback_max_rp: float
    duck_buy_price_fallback_mid_rp: float
    feed_price_rp_per_kg: float | None
    # Fase 6 cleanup: HET only; legacy ``phosphate_price_rp_per_kg=2700``
    # was stale and never used by active engine.
    nitrogen_price_rp_per_kg: float
    potassium_price_rp_per_kg: float
    weeding_cost_rp_per_are: float
    # True-cost interview artifacts — dokumentasi kualitatif, bukan output
    # model aktif. Disimpan sebagai catatan saja, tidak dipakai Cost Engine.
    net_cost_rp: float
    net_lifetime_seasons: int
    shelter_cost_rp: float
    shelter_lifetime_seasons: int
    infrastructure_maintenance_rp_per_season: float
    additional_cost_rp_per_season: float
    # Fase 6 cleanup: kappa_n/p/k (0.049/0.072/0.032) adalah Generasi-A
    # literature-uncalibrated. SoT ``_terbaru`` Material Engine memakai
    # koefisien 0.107/0.424/0.058 (lihat Tabel 2.2). Field dihapus.
    gwp_ch4: float
    gwp_n2o: float
    seasonal_ch4_rice_duck_kg_per_ha: float | None
    seasonal_ch4_conventional_kg_per_ha: float | None
    seasonal_n2o_kg_per_ha: float | None
    calibration_note: str

    HET_urea: float = 1800.0
    HET_phonska: float = 1840.0
    HET_kcl: float = 9500.0

    valid_period_conventional_rice_price: str = "Maret 2026"




    feed_requirement_kg_per_duck_day_reference: float = 0.10



    feed_natural_saving_rate_reference: float = 0.66


@dataclass(frozen=True)
class ParameterMetadata:
    value: Any
    unit: str
    source: str
    status: str
    note: str
    minimum: float | int | None = None
    maximum: float | int | None = None


@dataclass(frozen=True)
class User:
    id: str
    name: str
    email: str
    password_hash: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class SimulationHistoryLegacy:
    """Legacy schema (schema_version=1). Read-only for audit."""
    id: str
    user_id: str
    input_data: dict
    actual_scenario: dict
    recommended_scenario: dict
    comparison: dict
    risk: dict
    trace: dict
    notes: list[str]
    economics: dict
    ecology: dict
    environment: dict
    lookup: dict
    validation: dict
    data_readiness: dict
    created_at: datetime
    schema_version: int = 1


@dataclass(frozen=True)
class SimulationHistory:
    """New explicit-column row (schema_version=2)."""
    id: str
    user_id: str
    schema_version: int
    # Agronomi & operasional
    density_status: str
    age_status: str
    d_masuk_bebek: str
    d_tarik_bebek: str
    d_panen_gabah: str
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
    cost_feed: float
    cost_labor_base: float
    cost_labor_weed_hired: float
    cost_labor_total: float
    cost_infra_net: float
    cost_infra_cage: float
    cost_infra_total: float
    cost_fert_urea: float
    cost_fert_phonska: float
    cost_fert_kcl: float
    cost_fertilizer_total: float
    cost_pesticide: float
    cost_total_cash: float
    # Profit
    profit_net_cash: float
    valuation_weed_eco: float
    profit_net_full: float
    created_at: datetime
    cost_labor_tending: float = 0.0  # DEPRECATED (lihat FINAL_BANGET.md Catatan Finalisasi poin 12):
                                      # dihapus dari formula Cost Engine sejak 2026-07-07.
                                      # Field dipertahankan di DB untuk backward compatibility
                                      # historical records, nilai selalu 0.0,
                                      # TIDAK di-expose di API response.


@dataclass(frozen=True)
class AuthContext:
    user: User

