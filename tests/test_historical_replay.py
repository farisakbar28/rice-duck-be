import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "historical_replay.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("scenario", FIXTURE, ids=[item["id"] for item in FIXTURE])
def test_historical_replay_contract(scenario: dict) -> None:
    client = TestClient(create_app())
    request = {key: value for key, value in scenario.items() if key not in {"id", "actual_yield_are"}}
    response = client.post("/api/v1/dss/simulate", json=request)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["density_are"] == pytest.approx(scenario["duck_count"] / scenario["land_area_are"], abs=1e-7)
    assert body["Yield_are_pred"] == pytest.approx(47.8767507)
    assert body["Yield_total_pred"] == pytest.approx(47.8767507 * scenario["land_area_are"], abs=1e-4)
    assert body["Revenue_gabah"] == pytest.approx(47.8767507 * scenario["land_area_are"] * 6000, abs=0.01)
    assert body["Cost_duck_buy"] == pytest.approx(scenario["duck_count"] * scenario["p_duck_buy"])
    if scenario["rice_variety"] == "inpari":
        assert body["harvest_hst_min"] == body["harvest_hst_max"] == 134
    else:
        assert (body["harvest_hst_min"], body["harvest_hst_max"]) == (100, 110)
