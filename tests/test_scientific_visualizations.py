"""Unit test for Scientific Visualization API blueprint and anti-empty guard validation.
"""

from fastapi.testclient import TestClient
from app.main import app


def test_scientific_visualizations_contract() -> None:
    client = TestClient(app)
    payload = {
        "duck_count": 50,
        "land_area_are": 10,
        "planting_date": "2026-01-01",
        "rice_variety": "sertani",
        "planting_system": "jajar_legowo",
        "duck_age_days": 14,
    }
    r = client.post("/api/v1/dss/visualize", json=payload)
    assert r.status_code == 200, r.text
    body = r.json()

    # 1. Anti-Empty Guard & Core Schema Checks
    assert "visualizations" in body
    viz = body["visualizations"]
    assert viz is not None

    # 2. Density Curve Validation (Exactly 100 points, d=0.1..10.0)
    density_curve = viz.get("density_curve")
    assert isinstance(density_curve, list)
    assert len(density_curve) == 100

    first_point = density_curve[0]
    assert first_point["density"] == 0.1
    assert "yield_factor_jarwo" in first_point
    assert "yield_factor_tegel" in first_point
    assert "is_safe_jarwo" in first_point
    assert "is_safe_tegel" in first_point
    assert "is_over_density" in first_point
    assert isinstance(first_point["yield_factor_jarwo"], float)

    # Check boundaries and boolean safety flags
    safe_pt = next(p for p in density_curve if p["density"] == 4.0)
    assert safe_pt["is_safe_jarwo"] is True
    assert safe_pt["is_safe_tegel"] is False

    over_pt = density_curve[-1]  # density 10.0
    assert over_pt["is_over_density"] is True

    # 3. Age Vulnerability Validation (Exactly 45 points, age=1..45)
    age_vulnerability = viz.get("age_vulnerability")
    assert isinstance(age_vulnerability, list)
    assert len(age_vulnerability) == 45

    age_pt_1 = age_vulnerability[0]
    assert age_pt_1["age_days"] == 1
    assert age_pt_1["zone"] == "red"

    age_pt_14 = age_vulnerability[13]
    assert age_pt_14["age_days"] == 14
    assert age_pt_14["zone"] == "yellow"

    age_pt_30 = age_vulnerability[29]
    assert age_pt_30["age_days"] == 30
    assert age_pt_30["zone"] == "green"

    # 4. Financial Waterfall Validation
    financial_waterfall = viz.get("financial_waterfall")
    assert isinstance(financial_waterfall, list)
    assert len(financial_waterfall) == 4

    labels = [node["name"] for node in financial_waterfall]
    assert labels == [
        "Gross Grain Revenue",
        "Gross Duck Revenue",
        "Duckling Acquisition Cost",
        "Pure Absorbed Net Cash",
    ]

    # Verify nodes have exact float types and valid amounts
    for node in financial_waterfall:
        assert isinstance(node["amount"], float)
        assert node["type"] in ("revenue", "cost", "total")

    # 5. Benchmarks Validation inside Visualizations Block
    benchmarks = viz.get("benchmarks")
    assert benchmarks["k_safe_jarwo"] == 4.0
    assert benchmarks["k_safe_tegel"] == 3.0
    assert benchmarks["k_max_saturation"] == 8.0
