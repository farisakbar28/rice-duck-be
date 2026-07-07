"""Fase 7 — end-to-end API tests for /api/v1/dss/simulate.

These exercise the full simulate() path with SoT-aligned inputs.
"""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


# ---------------------------------------------------------------------------
# 1. SoT example (Tabel 2.2): A=10, J=50, V=Sertani, S=Jarwo, U=14
# ---------------------------------------------------------------------------


def test_sot_example_jarwo(client: TestClient) -> None:
    payload = {
        "duck_count": 50,
        "land_area_are": 10,
        "planting_date": "2026-01-01",
        "rice_variety": "sertani",
        "planting_system": "jajar_legowo",
        "duck_age_days": 14,
    }
    r = client.post("/api/v1/dss/simulate", json=payload)
    assert r.status_code == 200, r.text
    body = r.json()

    # Calendar (Fase 1)
    assert body["D_masuk_bebek"] == "2026-01-22"   # +21
    assert body["D_tarik_bebek"] == "2026-03-07"   # +65
    assert body["D_panen_gabah"] == "2026-04-10"   # +99 (Sertani)

    # Yield Engine: F_sys=1.00 (Jarwo)
    # Yield_are ≈ 48.039 * 1 * (1-0.08*0.15) * 1 * 1 = 47.4625
    # But SoT example evaluates with p_over=0.25 → F_density = 1-0.25*0.25 = 0.9375
    # yield_are = 48.039 * 0.9375 * 0.988 * 1 * 1 ≈ 44.49
    assert 44.0 < body["Yield_are_predict"] < 45.0

    # Cost breakdown (Fase 2)
    assert body["Cost_labor_base"] == pytest.approx(475270.0)
    assert "Cost_labor_tending" not in body
    assert body["Cost_labor_weed_hired"] == pytest.approx(65685.0, rel=1e-3)
    assert body["Cost_labor_total"] == pytest.approx(540955.0, rel=1e-3)
    assert body["Cost_total_cash"] == pytest.approx(2561008.0, rel=1e-3)
    assert body["Profit_net_cash"] == pytest.approx(1053392.0, rel=1e-3)
    assert body["Valuation_weed_eco"] == pytest.approx(101422.0, rel=1e-3)
    assert body["Profit_net_full"] == pytest.approx(1154814.0, rel=1e-3)

    # Infra
    assert body["Cost_infra_net"] == pytest.approx(78163.0, rel=1e-3)
    assert body["Cost_infra_cage"] == pytest.approx(208325.0, rel=1e-3)
    assert body["Cost_infra"] == pytest.approx(286488.0, rel=1e-3)
    assert (
        body["Cost_infra_net"] + body["Cost_infra_cage"]
        == pytest.approx(body["Cost_infra"], rel=1e-3)
    )

    # Feed unchanged
    assert body["Cost_feed"] == pytest.approx(315625.0)

    # F_sys present
    assert body["F_sys"] == 1.0


# ---------------------------------------------------------------------------
# 2. Tegel MUST receive a penalty (Fase 2 critical)
# ---------------------------------------------------------------------------


def test_tegel_yield_lower_than_jarwo(client: TestClient) -> None:
    base = {
        "duck_count": 50,
        "land_area_are": 10,
        "planting_date": "2026-01-01",
        "rice_variety": "sertani",
        "duck_age_days": 14,
    }
    r_jarwo = client.post(
        "/api/v1/dss/simulate", json={**base, "planting_system": "jajar_legowo"}
    )
    r_tegel = client.post(
        "/api/v1/dss/simulate", json={**base, "planting_system": "tegel"}
    )
    assert r_jarwo.status_code == 200
    assert r_tegel.status_code == 200
    y_jarwo = r_jarwo.json()["Yield_are_predict"]
    y_tegel = r_tegel.json()["Yield_are_predict"]
    # Tegel K_safe=3 (vs Jarwo=4), so d=5 gives Tegel P_over=0.4 vs Jarwo=0.25.
    # Combined: F_sys(0.95) * F_density(0.9) for Tegel vs F_density(0.9375) for Jarwo.
    # Tegel is strictly lower. NOT 0.95 ratio — it's lower.
    assert y_tegel < y_jarwo
    # F_sys confirmed via response
    assert r_tegel.json()["F_sys"] == 0.95
    assert r_jarwo.json()["F_sys"] == 1.0


# ---------------------------------------------------------------------------
# 3. Inpari D_panen_gabah = +112
# ---------------------------------------------------------------------------


def test_inpari_d_panen_gabah_112(client: TestClient) -> None:
    payload = {
        "duck_count": 50,
        "land_area_are": 10,
        "planting_date": "2026-01-01",
        "rice_variety": "inpari",
        "planting_system": "jajar_legowo",
        "duck_age_days": 14,
    }
    r = client.post("/api/v1/dss/simulate", json=payload)
    assert r.status_code == 200
    assert r.json()["D_panen_gabah"] == "2026-04-23"


# ---------------------------------------------------------------------------
# 4. Deprecation — f_yield and hst_masuk still present and synced
# ---------------------------------------------------------------------------


def test_options_include_deprecated_aliases(client: TestClient) -> None:
    r = client.get("/api/v1/dss/options")
    assert r.status_code == 200
    body = r.json()
    tegel = next(p for p in body["planting_systems"] if p["code"] == "tegel")
    # Canonical + deprecated
    assert tegel["F_sys"] == 0.95
    assert tegel["f_yield"] == 0.95  # deprecated alias in sync
    assert tegel["k_safe_are"] == 3.0
    assert tegel["k_max_are"] == 3.0  # deprecated alias in sync

    sertani = next(v for v in body["rice_varieties"] if v["code"] == "sertani")
    assert sertani["hst_panen"] == 99
    assert sertani["harvest_age_days"] == 99  # deprecated alias in sync


# ---------------------------------------------------------------------------
# 5. Fase 0 — optimizer endpoint exists and is isolated
# ---------------------------------------------------------------------------


def test_optimizer_endpoint_responds(client: TestClient) -> None:
    payload = {
        "duck_count": 50,
        "land_area_are": 10,
        "planting_date": "2026-01-01",
        "rice_variety": "sertani",
        "planting_system": "jajar_legowo",
        "duck_age_days": 14,
    }
    r = client.post("/api/v1/optimizer/recommend", json=payload)
    assert r.status_code == 200
    body = r.json()
    # Optimizer output is marked as out-of-scope of SoT
    assert "scope_notice" in body
    assert "FINAL_BANGET" in body["scope_notice"]


def test_dss_simulate_response_has_no_optimizer_fields(client: TestClient) -> None:
    """Fase 0 DoD: /dss/simulate must not leak optimizer fields."""
    payload = {
        "duck_count": 50,
        "land_area_are": 10,
        "planting_date": "2026-01-01",
        "rice_variety": "sertani",
        "planting_system": "jajar_legowo",
        "duck_age_days": 14,
    }
    r = client.post("/api/v1/dss/simulate", json=payload)
    assert r.status_code == 200
    body = r.json()
    forbidden = {
        "Score_safety", "F_active", "J_rekomendasi", "DeltaProfit", "REY",
        "actual_scenario", "recommended_scenario", "comparison", "optimality",
        "validation", "data_readiness", "x_base", "d_lit_ha",
    }
    leak = forbidden & set(body.keys())
    assert not leak, f"Optimizer fields leaked into /dss/simulate: {leak}"


# ---------------------------------------------------------------------------
# 6. Guardrail: Cost_feed unchanged regardless of Fase 2 refactor
# ---------------------------------------------------------------------------


def test_cost_feed_invariant(client: TestClient) -> None:
    """Feed cost formula must produce exactly 315625 for SoT example."""
    payload = {
        "duck_count": 50,
        "land_area_are": 10,
        "planting_date": "2026-01-01",
        "rice_variety": "sertani",
        "planting_system": "jajar_legowo",
        "duck_age_days": 14,
    }
    r = client.post("/api/v1/dss/simulate", json=payload)
    assert r.status_code == 200
    assert r.json()["Cost_feed"] == pytest.approx(315625.0)


# ---------------------------------------------------------------------------
# 7. Guardrail: Cost_infra total scale unchanged
# ---------------------------------------------------------------------------


def test_cost_infra_total_matches_legacy_formula(client: TestClient) -> None:
    """Cost_infra = max(58333, raw_net + raw_cage). SoT example 286488."""
    payload = {
        "duck_count": 50,
        "land_area_are": 10,
        "planting_date": "2026-01-01",
        "rice_variety": "sertani",
        "planting_system": "jajar_legowo",
        "duck_age_days": 14,
    }
    r = client.post("/api/v1/dss/simulate", json=payload)
    assert r.status_code == 200
    assert r.json()["Cost_infra"] == pytest.approx(286488.0, rel=1e-3)


# ---------------------------------------------------------------------------
# 8. Fase 3 regression: V_weed_eco unchanged by adding C_weed_hired
# ---------------------------------------------------------------------------


def test_valuation_weed_eco_independent_of_weed_hired(client: TestClient) -> None:
    """If V_weed_eco basis were Cost_labor_total (wrong), it would change
    when weed_hired varies. SoT basis = Cost_labor_base murni, which is
    independent of the extra weed_hired component.
    """
    base = {
        "land_area_are": 10,
        "planting_date": "2026-01-01",
        "rice_variety": "sertani",
        "planting_system": "jajar_legowo",
        "duck_age_days": 14,
    }
    r1 = client.post(
        "/api/v1/dss/simulate", json={**base, "duck_count": 50}
    )
    r2 = client.post(
        "/api/v1/dss/simulate", json={**base, "duck_count": 100}
    )
    # This endpoint-level test keeps the assertion lightweight; the exact basis
    # behaviour is covered in the formula-engine unit tests.
    # That's already tested in test_formula_engine.test_valuation_weed_eco_basis.
    # Here we just assert the response contains the field and it's positive.
    assert r1.json()["Valuation_weed_eco"] > 0
    assert r2.json()["Valuation_weed_eco"] > 0
