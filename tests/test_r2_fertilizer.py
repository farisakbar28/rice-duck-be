"""Phase 2: fertilizer baseline engine -- independently computed expectations.

Reference case A=7 are (values derived by hand from the SSOT coefficients,
NOT by calling the engine):
    N_need    = 1.1761 * 7 = 8.2327
    P2O5_need = 0.2745 * 7 = 1.9215
    K2O_need  = 0.2745 * 7 = 1.9215
    Q_npk     = max(1.9215/0.10, 1.9215/0.12) = max(19.215, 16.0125) = 19.215
    Q_urea    = max(0, (8.2327 - 0.15*19.215)/0.46)
              = 5.35045/0.46 = 11.631413043478...
    C_npk     = 19.215 * 1840 = 35,355.60
    C_urea    = 11.631413043... * 1800 = 20,936.543478...
    C_total   = 56,292.143478...
"""

from decimal import Decimal

import pytest

from app.domain.models import AvailabilityStatus
from app.engines.r2.config import load_default_config
from app.engines.r2.fertilizer import NUTRIENT_BASIS, compute_fertilizer_baseline


@pytest.fixture(scope="module")
def config():
    return load_default_config()


def fert(area, config):
    return compute_fertilizer_baseline(area, config)


class TestBaselineNeeds:
    def test_area_seven_independent_literals(self, config) -> None:
        result = fert(7, config)
        assert result.n_need_kg == Decimal("8.2327")
        assert result.p2o5_need_kg == Decimal("1.9215")
        assert result.k2o_need_kg == Decimal("1.9215")

    def test_area_one(self, config) -> None:
        result = fert(1, config)
        assert result.n_need_kg == Decimal("1.1761")
        assert result.p2o5_need_kg == Decimal("0.2745")
        assert result.k2o_need_kg == Decimal("0.2745")

    def test_area_half_are(self, config) -> None:
        result = fert("0.5", config)
        assert result.n_need_kg == Decimal("0.58805")


class TestOptimumQuantities:
    def test_q_npk_is_p_binding_for_default_coefficients(self, config) -> None:
        # P branch: 1.9215/0.10 = 19.215 > K branch: 1.9215/0.12 = 16.0125.
        result = fert(7, config)
        assert result.q_npk_kg == Decimal("19.215")

    def test_q_urea_matches_hand_computation(self, config) -> None:
        result = fert(7, config)
        expected = Decimal("11.631413043478260869565217391304347826086956521739")
        assert abs(result.q_urea_kg - expected) < Decimal("1e-40")
        # Task-stated approximation with looser tolerance as a second guard.
        assert abs(result.q_urea_kg - Decimal("11.6314130435")) < Decimal("1e-10")

    def test_q_urea_never_negative_when_n_small(self, config) -> None:
        """max(0, ...) clamp is structurally present; tiny areas stay >= 0."""
        result = fert(Decimal("0.001"), config)
        assert result.q_urea_kg >= 0


class TestCosts:
    def test_area_seven_costs(self, config) -> None:
        result = fert(7, config)
        assert result.cost_npk_rp == Decimal("19.215") * Decimal("1840")
        assert abs(result.cost_urea_rp - Decimal("20936.54347826087")) < Decimal("1e-8")
        assert abs(result.cost_total_rp - Decimal("56292.14347826087")) < Decimal("1e-8")
        assert abs(result.cost_total_rp - Decimal("56292.14")) < Decimal("0.01")

    def test_cost_identity_components_sum(self, config) -> None:
        result = fert(7, config)
        assert result.cost_total_rp == result.cost_npk_rp + result.cost_urea_rp


class TestConstraintSatisfaction:
    def test_solver_constraints_hold_exactly(self, config) -> None:
        result = fert(7, config)
        n_covered = (
            Decimal("0.46") * result.q_urea_kg + Decimal("0.15") * result.q_npk_kg
        )
        assert n_covered >= result.n_need_kg
        assert Decimal("0.10") * result.q_npk_kg >= result.p2o5_need_kg
        assert Decimal("0.12") * result.q_npk_kg >= result.k2o_need_kg


class TestExplicitSemantics:
    def test_no_manure_credit_flagged(self, config) -> None:
        result = fert(7, config)
        assert result.manure_credit_applied is False

    def test_nutrient_basis_literal(self, config) -> None:
        result = fert(7, config)
        assert result.nutrient_basis == "N-P2O5-K2O"
        assert NUTRIENT_BASIS == "N-P2O5-K2O"

    def test_availability_available(self, config) -> None:
        assert fert(7, config).availability is AvailabilityStatus.AVAILABLE

    def test_result_has_no_potassium_product_branch(self, config) -> None:
        """Active products are Urea + NPK only; no KCl quantity/cost fields."""
        import dataclasses

        names = {f.name for f in dataclasses.fields(type(fert(7, config)))}
        assert not any("kcl" in name or "kcl" in name.lower() for name in names)
        assert {"q_npk_kg", "q_urea_kg", "cost_total_rp"} <= names
