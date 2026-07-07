"""Golden regression test — locks the SoT example payload to Tabel 2.3 outputs.

This test guards against any future formula drift by asserting the complete
``/api/v1/dss/simulate`` response for the canonical SoT example against the
expected values documented in ``docs/Model_Matematika_..._FINAL_BANGET.md``
(Tabel 2.2 + Tabel 2.3).

Payload (exact copy from SoT Tabel 2.1):
    land_area_are=10, duck_count=50, rice_variety=sertani,
    planting_system=jajar_legowo, planting_date=2026-01-01,
    duck_age_days=14.

Tolerance: Rp1 for currency fields, exact for integer-like fields.
"""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


# Tabel 2.3 SoT — exact expected values for the canonical example.
GOLDEN_PAYLOAD = {
    "land_area_are": 10,
    "duck_count": 50,
    "rice_variety": "sertani",
    "planting_system": "jajar_legowo",
    "planting_date": "2026-01-01",
    "duck_age_days": 14,
}

# Currency tolerance: Rp1 (SoT rounding in displays).
RP1 = 1.0


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def test_golden_full_response_matches_sot_tabel_2_3(client: TestClient) -> None:
    """Lock the entire SoT example response. Any drift from Tabel 2.3 fails."""
    r = client.post("/api/v1/dss/simulate", json=GOLDEN_PAYLOAD)
    assert r.status_code == 200, r.text
    body = r.json()

    # ----- Calendar Engine (Tabel 2.2 + 2.3) -----
    assert body["D_masuk_bebek"] == "2026-01-22"   # D_tanam + 21
    assert body["D_tarik_bebek"] == "2026-03-07"   # D_tanam + 65
    assert body["D_panen_gabah"] == "2026-04-10"   # D_tanam + 99 (Sertani)

    # ----- Density & Age status (Tabel 2.3) -----
    assert body["density_status"] == "WARNING_DENSITY"
    assert body["age_status"] == "AGE_BUY_RANGE"

    # ----- Survival Engine: N_survive = floor(50 * 0.55) = 27 -----
    assert body["N_survive"] == 27.0

    # ----- Yield Engine (Tabel 2.3) -----
    # Yield_are = 48.039 * F_density(0.9375) * F_age(0.988) * F_sys(1.00) * F_var(1.00) ≈ 44.49
    assert body["Yield_are_predict"] == pytest.approx(44.49, abs=RP1)
    # Yield_total = 44.49 * 10 = 444.9 (display rounded)
    assert body["Yield_total_predict"] == pytest.approx(444.9, abs=RP1)

    # ----- Revenue (Tabel 2.3) -----
    # Revenue_gabah = 444.9 * 6000 = 2.669.400
    assert body["Revenue_gabah"] == pytest.approx(2_669_400.0, abs=RP1)
    # Revenue_duck = 27 * 35000 = 945.000
    assert body["Revenue_duck"] == pytest.approx(945_000.0, abs=RP1)
    # Total_Revenue = 2.669.400 + 945.000 = 3.614.400
    assert body["Total_Revenue"] == pytest.approx(3_614_400.0, abs=RP1)

    # ----- Cost detail (Tabel 2.3) -----
    # Cost_duck_buy = 50 * 25000 = 1.250.000
    assert body["Cost_duck_buy"] == pytest.approx(1_250_000.0, abs=RP1)
    # Cost_feed = 50 * 5000 * (1 + 0.75*0.25 + 0.50*0.15) = 315.625
    assert body["Cost_feed"] == pytest.approx(315_625.0, abs=RP1)
    # Cost_labor_base = 47527 * 10 = 475.270
    assert body["Cost_labor_base"] == pytest.approx(475_270.0, abs=RP1)
    # Cost_labor_weed_hired = 30539 * 10 * (1 - 0.7849) ≈ 65.685
    assert body["Cost_labor_weed_hired"] == pytest.approx(65_685.0, abs=RP1)
    # Cost_labor_tending = 0.0 (DEPRECATED, dihapus dari formula)
    # NOT asserted as response field — TIDAK di-expose di API response.
    # Cost_labor_total = 475.270 + 65.685 = 540.955
    assert body["Cost_labor_total"] == pytest.approx(540_955.0, abs=RP1)

    # ----- Infrastructure breakdown (Tabel 2.3) -----
    # Cost_infra_net = 0.5 * 49.435 * sqrt(10) ≈ 78.163
    assert body["Cost_infra_net"] == pytest.approx(78_163.0, abs=RP1)
    # Cost_infra_cage = 0.5 * 8.333 * 50 = 208.325
    assert body["Cost_infra_cage"] == pytest.approx(208_325.0, abs=RP1)
    # Cost_infra = 78.163 + 208.325 = 286.488 (floor tidak aktif)
    assert body["Cost_infra"] == pytest.approx(286_488.0, abs=RP1)
    # Invariant: net + cage == total
    assert (
        body["Cost_infra_net"] + body["Cost_infra_cage"]
        == pytest.approx(body["Cost_infra"], abs=RP1)
    )

    # ----- Fertilizer (Tabel 2.3) -----
    # Cost_fertilizer_total = 161.500 (least-cost mix)
    assert body["Cost_fertilizer_total"] == pytest.approx(161_500.0, abs=RP1)
    assert body["Cost_fert_urea"] == pytest.approx(45_000.0, abs=RP1)
    assert body["Cost_fert_phonska"] == pytest.approx(69_000.0, abs=RP1)
    assert body["Cost_fert_kcl"] == pytest.approx(47_500.0, abs=RP1)
    # Cost_pesticide = 6.440
    assert body["Cost_pesticide"] == pytest.approx(6_440.0, abs=RP1)

    # ----- Cost_total_cash (Tabel 2.3) -----
    # = 1.250.000 + 315.625 + 540.955 + 286.488 + 161.500 + 6.440 = 2.561.008
    assert body["Cost_total_cash"] == pytest.approx(2_561_008.0, abs=RP1)

    # ----- Profit (Tabel 2.3) -----
    # Profit_net_cash = 3.614.400 - 2.561.008 = 1.053.392
    assert body["Profit_net_cash"] == pytest.approx(1_053_392.0, abs=RP1)
    # Valuation_weed_eco = 101.422 (post Finalisasi poin 12)
    assert body["Valuation_weed_eco"] == pytest.approx(101_422.0, abs=RP1)
    # Profit_net_full = 1.053.392 + 101.422 = 1.154.814
    assert body["Profit_net_full"] == pytest.approx(1_154_814.0, abs=RP1)

    # ----- F_sys (Tabel 2.3 additive) -----
    assert body["F_sys"] == pytest.approx(1.0, abs=0.01)


def test_golden_response_excludes_cost_labor_tending(client: TestClient) -> None:
    """Hardening: ``Cost_labor_tending`` MUST NOT be exposed in API response.

    SoT FINAL_BANGET Catatan Finalisasi poin 12: kolom dihapus dari formula
    dan TIDAK di-expose di API response (lihat juga CHANGELOG.md [Unreleased]).
    """
    r = client.post("/api/v1/dss/simulate", json=GOLDEN_PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    assert "Cost_labor_tending" not in body, (
        "Cost_labor_tending leaked into API response — SoT Catatan Finalisasi "
        "poin 12 violation."
    )


def test_golden_invariants_hold(client: TestClient) -> None:
    """Hardening: cross-field invariants documented in SoT.

    These invariants should hold for ANY valid input, not just the golden case.
    Locked here as a regression guard.
    """
    r = client.post("/api/v1/dss/simulate", json=GOLDEN_PAYLOAD)
    assert r.status_code == 200
    body = r.json()

    # Invariant 1: Cost_infra_net + Cost_infra_cage == Cost_infra
    assert (
        body["Cost_infra_net"] + body["Cost_infra_cage"]
        == pytest.approx(body["Cost_infra"], abs=RP1)
    )
    # Invariant 2: Revenue_gabah + Revenue_duck == Total_Revenue
    assert (
        body["Revenue_gabah"] + body["Revenue_duck"]
        == pytest.approx(body["Total_Revenue"], abs=RP1)
    )
    # Invariant 3: Profit_net_cash + Valuation_weed_eco == Profit_net_full
    assert (
        body["Profit_net_cash"] + body["Valuation_weed_eco"]
        == pytest.approx(body["Profit_net_full"], abs=RP1)
    )
    # Invariant 4: Cost_total_cash >= Cost_labor_base
    # (Cost_labor_base alone is a subset of Cost_labor_total ≤ Cost_total_cash)
    assert body["Cost_total_cash"] >= body["Cost_labor_base"]
    # Invariant 5: N_survive is integer-valued (floor)
    assert float(body["N_survive"]) == int(body["N_survive"])
    # Invariant 6: All Cost_* values are non-negative
    for key in (
        "Cost_duck_buy", "Cost_feed", "Cost_labor_base",
        "Cost_labor_weed_hired", "Cost_labor_total",
        "Cost_infra_net", "Cost_infra_cage", "Cost_infra",
        "Cost_fertilizer_total", "Cost_pesticide", "Cost_total_cash",
    ):
        assert body[key] >= 0, f"{key} must be non-negative, got {body[key]}"
