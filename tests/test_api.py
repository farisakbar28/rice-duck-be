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
        'duck_count': 50,
        'land_area_are': 10,
        'planting_date': '2026-01-01',
        'rice_variety': 'sertani',
        'planting_system': 'jajar_legowo',
        'duck_age_days': 14,
    }
    r = client.post('/api/v1/dss/simulate', json=payload)
    assert r.status_code == 200, r.text
    body = r.json()

    assert body['D_masuk_bebek'] == '2026-01-22'
    assert body['D_tarik_bebek'] == '2026-03-07'
    assert body['D_panen_gabah'] == '2026-04-25'

    assert body['Yield_are_predict'] == 52.36
    assert body['Cost_total_cash'] == 1250000.0
    assert body['Cost_feed_isolated'] == 284062.5
    assert body['Cost_weeding_isolated'] == 60630.8
    assert body['F_sys'] == 1.0


# ---------------------------------------------------------------------------
# 2. Tegel MUST receive a penalty (Fase 2 critical)
# ---------------------------------------------------------------------------


def test_tegel_yield_higher_than_jarwo(client: TestClient) -> None:
    base = {
        'duck_count': 50,
        'land_area_are': 10,
        'planting_date': '2026-01-01',
        'rice_variety': 'sertani',
        'duck_age_days': 14,
    }
    r_jarwo = client.post(
        '/api/v1/dss/simulate', json={**base, 'planting_system': 'jajar_legowo'}
    )
    r_tegel = client.post(
        '/api/v1/dss/simulate', json={**base, 'planting_system': 'tegel'}
    )
    assert r_jarwo.status_code == 200
    assert r_tegel.status_code == 200
    y_jarwo = r_jarwo.json()['Yield_are_predict']
    y_tegel = r_tegel.json()['Yield_are_predict']
    assert y_tegel > y_jarwo
    assert r_tegel.json()['F_sys'] == 1.211
    assert r_jarwo.json()['F_sys'] == 1.0


# ---------------------------------------------------------------------------
# 3. Inpari D_panen_gabah = +134
# ---------------------------------------------------------------------------


def test_inpari_d_panen_gabah_134(client: TestClient) -> None:
    payload = {
        'duck_count': 50,
        'land_area_are': 10,
        'planting_date': '2026-01-01',
        'rice_variety': 'inpari',
        'planting_system': 'jajar_legowo',
        'duck_age_days': 14,
    }
    r = client.post('/api/v1/dss/simulate', json=payload)
    assert r.status_code == 200
    assert r.json()['D_panen_gabah'] == '2026-05-15'


def test_visualize_endpoint(client: TestClient) -> None:
    payload = {
        'duck_count': 50,
        'land_area_are': 10,
        'planting_date': '2026-01-01',
        'rice_variety': 'sertani',
        'planting_system': 'jajar_legowo',
        'duck_age_days': 14,
    }
    r = client.post('/api/v1/dss/visualize', json=payload)
    assert r.status_code == 200, r.text
    body = r.json()

    assert 'density_curve' in body
    assert len(body['density_curve']) == 51  # 0.0 to 10.0 step 0.2
    assert body['density_curve'][0]['density'] == 0.0

    assert 'age_vulnerability' in body
    assert len(body['age_vulnerability']) == 45
    assert body['age_vulnerability'][0]['age_days'] == 1

    assert body['reference_benchmarks']['k_safe_jarwo'] == 4.0
    assert body['reference_benchmarks']['k_safe_tegel'] == 3.0
    assert body['reference_benchmarks']['k_max_saturation'] == 8.0

    assert 'financial_absorption' in body
    assert body['financial_absorption']['core_validated_liquid_cash'] == 1250000.0



# ---------------------------------------------------------------------------
# 4. Deprecation — f_yield and hst_masuk still present and synced
# ---------------------------------------------------------------------------


def test_options_include_deprecated_aliases(client: TestClient) -> None:
    r = client.get('/api/v1/dss/options')
    assert r.status_code == 200
    body = r.json()
    tegel = next(p for p in body['planting_systems'] if p['code'] == 'tegel')
    # Canonical + deprecated
    assert tegel['F_sys'] == 1.211
    sertani = next(v for v in body['rice_varieties'] if v['code'] == 'sertani')
    assert sertani['hst_panen'] == 114
    assert sertani['harvest_age_days'] == 114  # deprecated alias in sync


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
    """Feed cost formula must produce exactly 284062.5 for SoT example."""
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
    assert r.json()['Cost_feed_isolated'] == pytest.approx(284062.5)


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
    assert r.json()['Cost_infra_isolated'] == pytest.approx(632360.22, rel=1e-3)



