"""R2 fertilizer baseline engine (registry R2-NUT-01..04, R2-FERT-01..03).

Nutrient basis is consistently N-P2O5-K2O. Baseline needs per are:
    N    = 1.1761 kg
    P2O5 = 0.2745 kg
    K2O  = 0.2745 kg

Duck manure credit is NOT executable: net need equals baseline need. This is
a BASELINE-NO-CREDIT state; it is not a claim that manure contributes zero.

Active products only: Urea (46% N) and NPK Phonska (15-10-12). KCl has no
valid sourced price and is excluded -- there is no KCl branch here.
Optimum quantities:
    Q_npk  = max(P2O5_net/0.10, K2O_net/0.12)
    Q_urea = max(0, (N_net - 0.15*Q_npk)/0.46)
Cost:
    C_fert = HET_npk * Q_npk + HET_urea * Q_urea
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.domain.models import AvailabilityStatus
from app.engines.r2.common import high_precision, to_decimal
from app.engines.r2.config import R2EngineConfig

NUTRIENT_BASIS = "N-P2O5-K2O"


@dataclass(frozen=True)
class FertilizerResult:
    availability: AvailabilityStatus
    nutrient_basis: str
    manure_credit_applied: bool
    n_need_kg: Decimal
    p2o5_need_kg: Decimal
    k2o_need_kg: Decimal
    q_npk_kg: Decimal
    q_urea_kg: Decimal
    cost_npk_rp: Decimal
    cost_urea_rp: Decimal
    cost_total_rp: Decimal


def compute_fertilizer_baseline(
    land_area_are: Decimal | float | int | str,
    config: R2EngineConfig,
) -> FertilizerResult:
    a = to_decimal(land_area_are)

    n_need = config.n_need_kg_per_are * a
    p2o5_need = config.p2o5_need_kg_per_are * a
    k2o_need = config.k2o_need_kg_per_are * a

    # Baseline-no-credit: net need == baseline need (manure credit unavailable).
    n_net = n_need
    p2o5_net = p2o5_need
    k2o_net = k2o_need

    with high_precision():
        q_npk = max(p2o5_net / config.npk_p2o5_fraction, k2o_net / config.npk_k2o_fraction)
        q_urea = max(
            Decimal(0),
            (n_net - config.npk_n_fraction * q_npk) / config.urea_n_fraction,
        )
        cost_npk = q_npk * config.het_npk_rp_per_kg
        cost_urea = q_urea * config.het_urea_rp_per_kg

    return FertilizerResult(
        availability=AvailabilityStatus.AVAILABLE,
        nutrient_basis=NUTRIENT_BASIS,
        manure_credit_applied=False,
        n_need_kg=n_need,
        p2o5_need_kg=p2o5_need,
        k2o_need_kg=k2o_need,
        q_npk_kg=q_npk,
        q_urea_kg=q_urea,
        cost_npk_rp=cost_npk,
        cost_urea_rp=cost_urea,
        cost_total_rp=cost_npk + cost_urea,
    )
