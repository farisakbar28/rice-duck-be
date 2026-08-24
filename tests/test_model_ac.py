import json
import pytest
from fastapi.testclient import TestClient
from app.main import create_app

@pytest.fixture
def client(): return TestClient(create_app())
def payload(**changes):
    value={"land_area_are":10,"duck_count":40,"rice_variety":"sertani","planting_system":"jajar_legowo","duck_age_days":21}
    value.update(changes); return value

@pytest.mark.parametrize(("age","status"),[(20,"NOT_RECOMMENDED"),(21,"LOCAL_READY"),(30,"LOCAL_READY"),(31,"OLDER_CONSERVATIVE")])
def test_age_gate_never_changes_primary(client,age,status):
    body=client.post("/api/v1/dss/simulate",json=payload(duck_age_days=age)).json()
    assert (body["age_status"],body["yield_are_kg"]) == (status,50.0)

@pytest.mark.parametrize(("system","ducks","status"),[("jajar_legowo",19,"UNDER"),("jajar_legowo",20,"RECOMMENDED"),("jajar_legowo",40,"RECOMMENDED"),("jajar_legowo",41,"WARNING_ABOVE_RECOMMENDED"),("jajar_legowo",80,"WARNING_ABOVE_RECOMMENDED"),("jajar_legowo",81,"HIGH_RISK"),("tegel",30,"RECOMMENDED"),("tegel",31,"WARNING_ABOVE_RECOMMENDED")])
def test_density_gate_and_high_risk(client,system,ducks,status):
    body=client.post("/api/v1/dss/simulate",json=payload(planting_system=system,duck_count=ducks)).json()
    assert body["density_status"] == status and body["yield_are_kg"] == 50
    if ducks==81: assert body["survival_risk"]=="HIGH" and body["revenue_duck_all_sold_scenario"] is None and body["cash_contribution_before_optional"] is None

@pytest.mark.parametrize(("duration","expected"),[(None,None),(32,None),(49,None),(50,65.0044549762),(80,69.7396),(81,None)])
def test_xiong_domain_and_golden_values(client,duration,expected):
    body=client.post("/api/v1/dss/simulate",json=payload(literature_duration_days=duration) if duration is not None else payload()).json()
    assert body["yield_are_kg"]==50
    if expected is None: assert body["literature_reference_status"]=="OUTSIDE_LITERATURE_DOMAIN" and body["yield_literature_reference_are_kg"] is None
    else: assert body["literature_reference_status"]=="VALID_DOMAIN" and body["yield_literature_reference_are_kg"]==pytest.approx(expected)

def test_reference_never_routes_into_primary_economics(client):
    fields=["yield_are_kg","yield_total_kg","revenue_gabah","revenue_duck_all_sold_scenario","cost_duck_buy","cash_contribution_before_optional","cash_contribution_after_optional"]
    bodies=[client.post("/api/v1/dss/simulate",json=payload(**item)).json() for item in ({},{"literature_duration_days":50},{"literature_duration_days":80})]
    assert all({key: body[key] for key in fields}=={key:bodies[0][key] for key in fields} for body in bodies)
    assert bodies[1]["revenue_gabah"]==3000000 and bodies[1]["cash_contribution_before_optional"]==3800000

def test_defaults_zero_optional_costs_and_calendar(client):
    body=client.post("/api/v1/dss/simulate",json=payload(duck_count=20,planting_date="2026-01-01",p_duck_buy=0,c_feed_scenario=1000,c_jaring_purchase=10000,n_jaring_cycles=10)).json()
    assert body["cost_duck_buy"]==0 and body["cost_feed_scenario"]==1000 and body["cost_infra_cycle"]==1000 and body["cash_contribution_after_optional"]==body["cash_contribution_before_optional"]-2000
    assert body["release_date_min"]=="2026-01-22" and body["withdraw_date_max"]=="2026-03-02"

@pytest.mark.parametrize(("field","value"),[("land_area_are","10"),("duck_count",40.0),("duck_age_days",True),("p_gabah",True),("literature_duration_days","50")])
def test_strict_numbers(client,field,value):
    response=client.post("/api/v1/dss/simulate",json=payload(**{field:value}))
    assert response.status_code==400

def test_j_zero_and_unknown_exact_code(client):
    assert client.post("/api/v1/dss/simulate",json=payload(duck_count=0)).json()["revenue_duck_all_sold_scenario"]==0
    response=client.post("/api/v1/dss/simulate",json=payload(rice_variety="SERTANI")); assert response.status_code==422

def test_history_v4_round_trip(client):
    register=client.post("/api/v1/auth/register",json={"name":"History User","email":"history@example.com","password":"password123"}); assert register.status_code==201
    token=client.post("/api/v1/auth/login",json={"email":"history@example.com","password":"password123"}).json()["access_token"]; headers={"Authorization":f"Bearer {token}"}
    simulated=client.post("/api/v1/dss/simulate",json=payload(literature_duration_days=50),headers=headers); assert simulated.status_code==200
    row=client.get("/api/v1/dss/histories",headers=headers).json()["data"][0]; assert row["schema_version"]==4
    assert client.get(f"/api/v1/dss/histories/{row['id']}",headers=headers).json()==simulated.json()
    assert client.delete(f"/api/v1/dss/histories/{row['id']}",headers=headers).status_code==200

def test_legacy_rows_are_physically_preserved_but_hidden(client):
    from app.core.database import get_connection
    register=client.post("/api/v1/auth/register",json={"name":"Legacy User","email":"legacy@example.com","password":"password123"}); assert register.status_code==201
    token=client.post("/api/v1/auth/login",json={"email":"legacy@example.com","password":"password123"}).json()["access_token"]
    from app.repositories.user_repository import user_repository
    user=user_repository.get_by_email("legacy@example.com")
    with get_connection() as connection:
        connection.execute("INSERT INTO dss_simulation_histories (id,user_id,schema_version,created_at,input_json,actual_scenario_json,recommended_scenario_json,comparison_json,risk_json,trace_json,notes_json,economics_json,ecology_json,environment_json,lookup_json,validation_json,data_readiness_json) VALUES ('legacy-v3',?,3,'2026-01-01T00:00:00+00:00','{}','{}','{}','{}','{}','{}','[]','{}','{}','{}','{}','{}','{}')",(user.id,))
    response=client.get("/api/v1/dss/histories",headers={"Authorization":f"Bearer {token}"}); assert response.json()=={"data":[]}
    headers={"Authorization":f"Bearer {token}"}
    assert client.get("/api/v1/dss/histories/legacy-v3",headers=headers).status_code==404
    assert client.delete("/api/v1/dss/histories/legacy-v3",headers=headers).status_code==404
    with get_connection() as connection: assert connection.execute("SELECT COUNT(*) FROM dss_simulation_histories WHERE id='legacy-v3'").fetchone()[0]==1

def test_openapi_and_visualization(client):
    schema=client.get("/openapi.json").json(); assert "literature_duration_days" in schema["components"]["schemas"]["DSSSimulationRequest"]["properties"]
    assert "VALID_DOMAIN" in str(schema) and "/api/v1/optimizer/recommend" not in schema["paths"]
    result=client.post("/api/v1/dss/visualize",json=payload()).json(); assert "survival_rate" not in result["density_zones"][0] and "PRIMARY" in result["yield_note"]
