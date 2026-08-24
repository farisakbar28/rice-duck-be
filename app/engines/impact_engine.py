"""SoT §10 Research/Sandbox engines — docs/Model Matematika Data Collection DSS Padi Bebek FINAL.md

These helpers are archived research-only code and are not imported by the
A+C simulation or primary-economics paths.

SoT §10.1 Weeding:
    k_weeding = 21000 Rp/are/kegiatan
    R_weeding = 0.77
    Weeding_residual_per_are_event = 21000 * (1 - 0.77) = 4830
    Weeding_avoided_per_are_event  = 21000 - 4830 = 16170
    NOTE: Must NOT be multiplied by frequency without calibrated frequency parameter.

SoT §10.2 Pesticide:
    Pesticide_reduction_upper_bound = 0.80
    Non-monetary indicator only. No Rp cost formula.

SoT §10.3 Fertilizer/Material:
    Research/sandbox only. Magnitude not calibrated locally for Core.

SoT §10.4 Infrastructure:
    Context/reference only. No production cost formula.

SoT §13: feed=4500, Cost_feed_isolated are BANNED from production path.
"""

from decimal import Decimal

from app.domain.models import DSSConstants


# ---------------------------------------------------------------------------
# SoT §10.1 Weeding sandbox constants
# ---------------------------------------------------------------------------
K_WEEDING_RP_PER_ARE_EVENT = Decimal("21000")
R_WEEDING = Decimal("0.77")
WEEDING_RESIDUAL_PER_ARE_EVENT = K_WEEDING_RP_PER_ARE_EVENT * (Decimal("1") - R_WEEDING)   # 4830
WEEDING_AVOIDED_PER_ARE_EVENT = K_WEEDING_RP_PER_ARE_EVENT - WEEDING_RESIDUAL_PER_ARE_EVENT  # 16170

# ---------------------------------------------------------------------------
# SoT §10.2 Pesticide upper bound indicator (non-monetary)
# ---------------------------------------------------------------------------
PESTICIDE_REDUCTION_UPPER_BOUND = Decimal("0.80")


def _d(value) -> Decimal:
    """Coerce to Decimal."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


# ---------------------------------------------------------------------------
# SoT §10.1: Weeding sandbox
# ---------------------------------------------------------------------------


def compute_sandbox_weeding(land_area_are: float) -> dict:
    """SoT §10.1: Weeding Research/Sandbox output.

    Returns per-event estimates for ONE weeding event.
    Must NOT be multiplied by cycle frequency without a calibrated frequency parameter.

    Weeding_residual_per_are_event = 21000 * (1 - 0.77) = 4830 Rp/are/event
    Weeding_avoided_per_are_event  = 21000 - 4830 = 16170 Rp/are/event
    """
    a = _d(land_area_are)
    residual_total = WEEDING_RESIDUAL_PER_ARE_EVENT * a
    avoided_total = WEEDING_AVOIDED_PER_ARE_EVENT * a
    return {
        "k_weeding_rp_per_are_event": float(K_WEEDING_RP_PER_ARE_EVENT),
        "R_weeding": float(R_WEEDING),
        "Weeding_residual_per_are_event": float(WEEDING_RESIDUAL_PER_ARE_EVENT),
        "Weeding_avoided_per_are_event": float(WEEDING_AVOIDED_PER_ARE_EVENT),
        "Weeding_residual_total_one_event": float(residual_total),
        "Weeding_avoided_total_one_event": float(avoided_total),
        "note": "Per-siklus total tidak dihitung karena frekuensi kegiatan penyiangan belum dikalibrasi lokal.",
    }


# ---------------------------------------------------------------------------
# SoT §10.2: Pesticide sandbox
# ---------------------------------------------------------------------------


def compute_sandbox_pesticide() -> dict:
    """SoT §10.2: Pesticide Research/Sandbox output.

    Pesticide_reduction_upper_bound = 0.80 (non-monetary indicator only).
    No Rp cost formula. Not included in Core.
    """
    return {
        "Pesticide_reduction_upper_bound": float(PESTICIDE_REDUCTION_UPPER_BOUND),
        "note": "Nilai 80% adalah indikator upper bound non-moneter. Tidak ada formula biaya Rp yang dikalibrasi lokal.",
    }


# ---------------------------------------------------------------------------
# SoT §10.3: Fertilizer/Material sandbox (research reference)
# ---------------------------------------------------------------------------

# Soil nutrient kappa constants (literature-uncalibrated, Xiong et al. 2014)
KAPPA_N = Decimal("0.049")
KAPPA_P = Decimal("0.072")
KAPPA_K = Decimal("0.032")

# Elemental fractions
PHONSKA_N_FRACTION = Decimal("0.15")
PHONSKA_P_FRACTION = Decimal("0.04364")
PHONSKA_K_FRACTION = Decimal("0.09961")
UREA_N_FRACTION = Decimal("0.46")
KCL_K_FRACTION = Decimal("0.49806")


def compute_sandbox_fertilizer(
    duck_count: int,
    t_active: int,
    n_survive: int,
    land_area_are: float,
    constants: DSSConstants,
) -> dict:
    """SoT §10.3: Fertilizer Research/Sandbox output.

    Literature-uncalibrated mechanism. Not included in Core_Cash_Cost.
    N_need = 1.1761 * A_are; P_need = 0.2745 * A_are; K_need = 0.2745 * A_are
    """
    a = _d(land_area_are)
    t_d = Decimal(t_active)
    sub_base = max(Decimal("0"), Decimal("0.02") * t_d - Decimal("0.6"))

    survivors = Decimal(n_survive)
    n_duck = sub_base * KAPPA_N * survivors
    p_duck = sub_base * KAPPA_P * survivors
    k_duck = sub_base * KAPPA_K * survivors

    n_need = Decimal("1.1761") * a
    p_need = Decimal("0.2745") * a
    k_need = Decimal("0.2745") * a

    n_rem = max(Decimal("0"), n_need - n_duck)
    p_rem = max(Decimal("0"), p_need - p_duck)
    k_rem = max(Decimal("0"), k_need - k_duck)

    q_phonska = p_rem / PHONSKA_P_FRACTION if p_rem > 0 else Decimal("0")
    q_urea = max(Decimal("0"), n_rem - (q_phonska * PHONSKA_N_FRACTION)) / UREA_N_FRACTION
    q_kcl = max(Decimal("0"), k_rem - (q_phonska * PHONSKA_K_FRACTION)) / KCL_K_FRACTION

    het_phonska = _d(constants.HET_phonska)
    het_urea = _d(constants.HET_urea)
    het_kcl = _d(constants.HET_kcl)

    cost_fert_phonska = q_phonska * het_phonska
    cost_fert_urea = q_urea * het_urea
    cost_fert_kcl = q_kcl * het_kcl
    cost_fertilizer_total = cost_fert_phonska + cost_fert_urea + cost_fert_kcl

    return {
        "Cost_fertilizer_total": float(round(cost_fertilizer_total, 2)),
        "Cost_fert_urea": float(round(cost_fert_urea, 2)),
        "Cost_fert_phonska": float(round(cost_fert_phonska, 2)),
        "Cost_fert_kcl": float(round(cost_fert_kcl, 2)),
        "Q_phonska": float(round(q_phonska, 6)),
        "Q_urea": float(round(q_urea, 6)),
        "Q_kcl": float(round(q_kcl, 6)),
        "note": "Sandbox/research reference only. Tidak termasuk Core_Cash_Cost.",
    }


# ---------------------------------------------------------------------------
# SoT §10.4: Infrastructure sandbox (context/reference only)
# ---------------------------------------------------------------------------

def compute_sandbox_infrastructure() -> dict:
    """SoT §10.4: Infrastructure Research/Sandbox — context/reference only.

    No production cost formula or monetary estimate. Not included in Core.
    """
    return {
        "note": (
            "Infrastructure hanya context/reference. Tidak ada formula biaya atau "
            "estimasi moneter production, dan tidak termasuk Core_Cash_Cost."
        ),
    }
