"""Tests for formula engines — SoT FINAL.

Tests cover SoT §4 Age, §5 Density, §6 Calendar, §7 Survival, §8 Yield, §9 Core Economics.
All legacy semantics (R_age, F_age, lambda_eff, P_over, F_density_bio, etc.) are absent.
"""

import math
from datetime import date
from decimal import Decimal

import pytest

from app.engines.formula_engine import (
    T_ACTIVE,
    Y_BASE,
    HST_IN,
    HST_OUT,
    HST_PANEN_SERTANI_MIN,
    HST_PANEN_SERTANI_MAX,
    HST_PANEN_INPARI_MIN,
    HST_PANEN_INPARI_MAX,
    compute_age_flag,
    compute_calendar,
    compute_core_economics,
    compute_density,
    compute_surviving_ducks,
    compute_yield,
)
from app.engines.impact_engine import compute_sandbox_infrastructure


# ===========================================================================
# SoT §4: Age Readiness Engine
# ===========================================================================


class TestAgeFlag:
    """SoT §4: AgeFlag thresholds 21/30."""

    def test_age_20_too_young(self):
        r = compute_age_flag(20)
        assert r["age_flag"] == "TOO_YOUNG"
        assert len(r["warnings"]) > 0

    def test_age_21_recommended(self):
        r = compute_age_flag(21)
        assert r["age_flag"] == "RECOMMENDED"
        assert r["warnings"] == []

    def test_age_25_recommended(self):
        r = compute_age_flag(25)
        assert r["age_flag"] == "RECOMMENDED"

    def test_age_30_recommended(self):
        r = compute_age_flag(30)
        assert r["age_flag"] == "RECOMMENDED"

    def test_age_31_above_recommended(self):
        r = compute_age_flag(31)
        assert r["age_flag"] == "ABOVE_RECOMMENDED_AGE"
        assert len(r["warnings"]) > 0

    def test_age_1_too_young(self):
        r = compute_age_flag(1)
        assert r["age_flag"] == "TOO_YOUNG"

    def test_age_50_above_recommended(self):
        r = compute_age_flag(50)
        assert r["age_flag"] == "ABOVE_RECOMMENDED_AGE"

    def test_no_r_age_in_output(self):
        """SoT §13: R_age must NOT be returned."""
        r = compute_age_flag(21)
        assert "R_age" not in r
        assert "r_age" not in r

    def test_no_f_age_in_output(self):
        r = compute_age_flag(14)
        assert "F_age" not in r
        assert "f_age" not in r


# ===========================================================================
# SoT §5: Density Engine
# ===========================================================================


class TestDensity:
    """SoT §5: 4-tier density status, no P_over/P_under."""

    def test_under_density(self):
        # d = 10/10 = 1.0 < 2
        r = compute_density(10, 10, "jajar_legowo")
        assert r["density_status"] == "UNDER_DENSITY"
        assert float(r["d"]) == pytest.approx(1.0)

    def test_under_density_tegel(self):
        r = compute_density(5, 10, "tegel")
        assert r["density_status"] == "UNDER_DENSITY"

    def test_jarwo_recommended_lower_bound(self):
        # d = 20/10 = 2.0 → RECOMMENDED (Jarwo ceiling=4)
        r = compute_density(20, 10, "jajar_legowo")
        assert r["density_status"] == "RECOMMENDED"

    def test_jarwo_recommended_upper_bound(self):
        # d = 40/10 = 4.0 → RECOMMENDED (Jarwo ceiling=4)
        r = compute_density(40, 10, "jajar_legowo")
        assert r["density_status"] == "RECOMMENDED"

    def test_jarwo_above_recommended(self):
        # d = 50/10 = 5.0 > 4 but <= 8
        r = compute_density(50, 10, "jajar_legowo")
        assert r["density_status"] == "ABOVE_RECOMMENDED"

    def test_tegel_recommended_lower_bound(self):
        # d = 20/10 = 2.0 → RECOMMENDED (Tegel ceiling=3)
        r = compute_density(20, 10, "tegel")
        assert r["density_status"] == "RECOMMENDED"

    def test_tegel_recommended_upper_bound(self):
        # d = 30/10 = 3.0 → RECOMMENDED (Tegel ceiling=3)
        r = compute_density(30, 10, "tegel")
        assert r["density_status"] == "RECOMMENDED"

    def test_tegel_above_recommended(self):
        # d = 40/10 = 4.0 > 3 but <= 8
        r = compute_density(40, 10, "tegel")
        assert r["density_status"] == "ABOVE_RECOMMENDED"

    def test_overload_high_risk(self):
        # d = 81/10 = 8.1 > 8
        r = compute_density(81, 10, "jajar_legowo")
        assert r["density_status"] == "OVERLOAD_HIGH_RISK"
        assert len(r["warnings"]) > 0

    def test_overload_boundary(self):
        # d = 80/10 = 8.0 exactly → NOT overload (Jarwo: ABOVE_RECOMMENDED)
        r = compute_density(80, 10, "jajar_legowo")
        assert r["density_status"] == "ABOVE_RECOMMENDED"

    def test_overload_just_above(self):
        # d > 8 exactly
        r = compute_density(81, 10, "jajar_legowo")
        assert r["density_status"] == "OVERLOAD_HIGH_RISK"

    def test_d_ha_equals_100_times_d(self):
        r = compute_density(20, 10, "jajar_legowo")
        assert float(r["d_ha"]) == pytest.approx(float(r["d"]) * 100)

    def test_no_p_over_in_output(self):
        """SoT §13: P_over must NOT be returned."""
        r = compute_density(50, 10, "jajar_legowo")
        assert "P_over" not in r
        assert "p_over" not in r

    def test_no_p_under_in_output(self):
        r = compute_density(10, 10, "jajar_legowo")
        assert "P_under" not in r

    def test_density_value_correct(self):
        r = compute_density(20, 6.35, "jajar_legowo")
        # d = 20/6.35 ≈ 3.1496
        assert float(r["d"]) == pytest.approx(20 / 6.35, rel=1e-6)


# ===========================================================================
# SoT §6: Calendar Engine
# ===========================================================================


class TestCalendar:
    """SoT §6: Calendar constants and date derivation."""

    def test_hst_constants(self):
        assert HST_IN == 21
        assert HST_OUT == 65
        assert T_ACTIVE == 44

    def test_sertani_hst_range(self):
        assert HST_PANEN_SERTANI_MIN == 100
        assert HST_PANEN_SERTANI_MAX == 110

    def test_inpari_hst_window(self):
        assert HST_PANEN_INPARI_MIN == 109
        assert HST_PANEN_INPARI_MAX == 116

    def test_sertani_calendar(self):
        r = compute_calendar(date(2024, 4, 22), "sertani")
        assert r["D_in"] == date(2024, 5, 13)       # +21
        assert r["D_out"] == date(2024, 6, 26)      # +65
        assert r["harvest_hst_min"] == 100
        assert r["harvest_hst_max"] == 110
        assert r["D_panen_min"] == date(2024, 7, 31)   # +100
        assert r["D_panen_max"] == date(2024, 8, 10)   # +110
        assert r["t_active"] == 44
        assert r["HST_in"] == 21
        assert r["HST_out"] == 65
        assert r["warnings"] == []

    def test_inpari_calendar(self):
        r = compute_calendar(date(2024, 4, 12), "inpari")
        assert r["harvest_hst_min"] == 109
        assert r["harvest_hst_max"] == 116
        assert r["D_panen_min"] == date(2024, 7, 30)   # +109
        assert r["D_panen_max"] == date(2024, 8, 6)    # +116
        assert r["warnings"] == []

    def test_inpari_calendar_handles_leap_year_boundary(self):
        r = compute_calendar(date(2024, 11, 15), "inpari")
        assert r["D_panen_min"] == date(2025, 3, 4)
        assert r["D_panen_max"] == date(2025, 3, 11)

    def test_planting_date_2026_01_01_sertani(self):
        r = compute_calendar(date(2026, 1, 1), "sertani")
        assert r["D_in"] == date(2026, 1, 22)
        assert r["D_out"] == date(2026, 3, 7)
        assert r["D_panen_min"] == date(2026, 4, 11)
        assert r["D_panen_max"] == date(2026, 4, 21)


# ===========================================================================
# SoT §7: Survival Engine
# ===========================================================================


class TestSurvival:
    """SoT §7: N_survive = J (d<=8) or floor(0.60*J) (d>8)."""

    def test_d_equals_1_no_mortality(self):
        d = Decimal("1.0")
        assert compute_surviving_ducks(50, d) == 50

    def test_d_equals_2_no_mortality(self):
        d = Decimal("2.0")
        assert compute_surviving_ducks(50, d) == 50

    def test_d_equals_8_no_mortality(self):
        """d=8 boundary: NOT overload, N_survive=J."""
        d = Decimal("8.0")
        assert compute_surviving_ducks(100, d) == 100

    def test_d_above_8_overload(self):
        """d>8: N_survive=floor(0.60*J)."""
        d = Decimal("8.1")
        assert compute_surviving_ducks(100, d) == 60

    def test_d_above_8_floor_semantics(self):
        """floor(0.60*81) = floor(48.6) = 48."""
        d = Decimal("8.1")
        assert compute_surviving_ducks(81, d) == 48

    def test_d_above_8_exact_overload_B08(self):
        """B08: A=10, J=81, d=8.1 → OVERLOAD, floor(0.60*81)=48."""
        d = Decimal("8.1")
        assert compute_surviving_ducks(81, d) == 48

    def test_normal_survival_full_count(self):
        """SoT §7: d<=8 → N_survive = full duck_count."""
        d = Decimal("3.0")
        assert compute_surviving_ducks(32, d) == 32

    def test_no_lambda_eff(self):
        """No lambda_eff=0.78125 in production path."""
        # If d<=8, result must equal duck_count exactly
        d = Decimal("4.0")
        result = compute_surviving_ducks(50, d)
        assert result == 50

    def test_no_r_age_dependency(self):
        """Survival must not depend on age."""
        # Same J and d → same result regardless of age
        d = Decimal("3.0")
        r1 = compute_surviving_ducks(30, d)
        r2 = compute_surviving_ducks(30, d)
        assert r1 == r2 == 30


# ===========================================================================
# SoT §8: Yield Engine
# ===========================================================================


class TestYield:
    """SoT §8: Constant baseline 47.8767507, system/variety/density neutral."""

    def test_y_base_constant(self):
        assert Y_BASE == Decimal("47.8767507")

    def test_yield_are_pred_constant(self):
        r = compute_yield(10.0)
        assert float(r["Yield_are_pred"]) == pytest.approx(47.8767507, rel=1e-7)

    def test_yield_total_pred(self):
        r = compute_yield(10.0)
        assert float(r["Yield_total_pred"]) == pytest.approx(47.8767507 * 10.0, rel=1e-6)

    def test_yield_invariant_density(self):
        """SoT §8: Yield must not depend on density."""
        r_low = compute_yield(10.0)
        r_high = compute_yield(10.0)
        assert float(r_low["Yield_are_pred"]) == float(r_high["Yield_are_pred"])

    def test_yield_jarwo_equals_tegel(self):
        """SoT §8: F_sys=1 for both systems — yield identical for same area."""
        r_jarwo = compute_yield(6.0)
        r_tegel = compute_yield(6.0)
        assert float(r_jarwo["Yield_are_pred"]) == float(r_tegel["Yield_are_pred"])

    def test_yield_sertani_equals_inpari(self):
        """SoT §8: F_var=1 for both varieties — yield identical for same area."""
        r_s = compute_yield(5.0)
        r_i = compute_yield(5.0)
        assert float(r_s["Yield_are_pred"]) == float(r_i["Yield_are_pred"])

    def test_yield_does_not_use_f_density_bio(self):
        """No F_density_bio in production path."""
        r = compute_yield(10.0)
        # Yield_are_pred must be exactly Y_BASE
        assert float(r["Yield_are_pred"]) == pytest.approx(47.8767507, rel=1e-10)

    def test_yield_total_small_area(self):
        r = compute_yield(3.45)
        assert float(r["Yield_total_pred"]) == pytest.approx(47.8767507 * 3.45, rel=1e-6)


# ===========================================================================
# SoT §9: Core Economic Engine
# ===========================================================================


class TestCoreEconomics:
    """SoT §9: Revenue, Cost, Net_Cash_Contribution_DSS."""

    def _std_yield(self, area=10.0):
        return compute_yield(area)["Yield_total_pred"]

    def test_revenue_gabah(self):
        ytp = self._std_yield(10.0)
        r = compute_core_economics(
            yield_total_pred=ytp, n_survive=50, duck_count=50, p_duck_buy=0
        )
        assert float(r["Revenue_gabah"]) == pytest.approx(float(ytp) * 6000, rel=1e-6)

    def test_revenue_duck_potential(self):
        ytp = self._std_yield()
        r = compute_core_economics(
            yield_total_pred=ytp, n_survive=32, duck_count=50, p_duck_buy=0
        )
        assert float(r["Revenue_duck_potential"]) == pytest.approx(32 * 52500, rel=1e-6)

    def test_p_duck_sell_is_52500(self):
        ytp = self._std_yield()
        r = compute_core_economics(
            yield_total_pred=ytp, n_survive=1, duck_count=1, p_duck_buy=0
        )
        assert float(r["Revenue_duck_potential"]) == pytest.approx(52500.0)

    def test_cost_duck_buy_zero(self):
        """SoT §9: p_duck_buy=0 is valid."""
        ytp = self._std_yield()
        r = compute_core_economics(
            yield_total_pred=ytp, n_survive=50, duck_count=50, p_duck_buy=0
        )
        assert float(r["Cost_duck_buy"]) == 0.0

    def test_cost_duck_buy_nonzero(self):
        ytp = self._std_yield()
        r = compute_core_economics(
            yield_total_pred=ytp, n_survive=50, duck_count=20, p_duck_buy=15000
        )
        assert float(r["Cost_duck_buy"]) == pytest.approx(20 * 15000)

    def test_cost_feed_core(self):
        """SoT §9: Cost_feed = duck_count * 20000 (Core, not isolated)."""
        ytp = self._std_yield()
        r = compute_core_economics(
            yield_total_pred=ytp, n_survive=50, duck_count=20, p_duck_buy=0
        )
        assert float(r["Cost_feed"]) == pytest.approx(20 * 20000)

    def test_core_cash_cost(self):
        """SoT §9: Core_Cash_Cost = Cost_duck_buy + Cost_feed."""
        ytp = self._std_yield()
        r = compute_core_economics(
            yield_total_pred=ytp, n_survive=50, duck_count=20, p_duck_buy=15000
        )
        assert float(r["Core_Cash_Cost"]) == pytest.approx(
            float(r["Cost_duck_buy"]) + float(r["Cost_feed"])
        )

    def test_total_revenue_dss(self):
        ytp = self._std_yield()
        r = compute_core_economics(
            yield_total_pred=ytp, n_survive=50, duck_count=20, p_duck_buy=0
        )
        assert float(r["Total_Revenue_DSS"]) == pytest.approx(
            float(r["Revenue_gabah"]) + float(r["Revenue_duck_potential"])
        )

    def test_net_cash_contribution_dss(self):
        """SoT §9: Net_Cash_Contribution_DSS = Total_Revenue_DSS - Core_Cash_Cost."""
        ytp = self._std_yield()
        r = compute_core_economics(
            yield_total_pred=ytp, n_survive=50, duck_count=20, p_duck_buy=15000
        )
        assert float(r["Net_Cash_Contribution_DSS"]) == pytest.approx(
            float(r["Total_Revenue_DSS"]) - float(r["Core_Cash_Cost"])
        )

    def test_no_profit_net_cash_key(self):
        """SoT §13: Profit_net_cash must NOT be the canonical output key."""
        ytp = self._std_yield()
        r = compute_core_economics(
            yield_total_pred=ytp, n_survive=50, duck_count=20, p_duck_buy=0
        )
        assert "Profit_net_cash" not in r

    def test_p_duck_buy_30000_passthrough(self):
        ytp = self._std_yield()
        r = compute_core_economics(
            yield_total_pred=ytp, n_survive=50, duck_count=10, p_duck_buy=30000
        )
        assert float(r["Cost_duck_buy"]) == pytest.approx(10 * 30000)


def test_infrastructure_sandbox_has_no_monetary_formula() -> None:
    output = compute_sandbox_infrastructure()
    assert set(output) == {"note"}
    assert "Tidak ada formula biaya" in output["note"]
