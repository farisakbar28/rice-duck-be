import pytest
from fastapi.testclient import TestClient
from app.main import create_app

@pytest.fixture
def client(): return TestClient(create_app())
def payload(**overrides):
    result={"land_area_are":10,"duck_count":40,"rice_variety":"sertani","planting_system":"jajar_legowo","duck_age_days":21}
    result.update(overrides); return result

def test_missing_duration_abstains_and_has_no_legacy_fields(client):
    body=client.post("/api/v1/dss/simulate",json=payload()).json()
    assert body["yield_status"]=="OUTSIDE_LITERATURE_DOMAIN" and body["yield_are_kg"] is None
    assert not {"N_survive","survival_rate","Yield_are_pred","Net_Cash_Contribution_DSS","Cost_feed"}&body.keys()

@pytest.mark.parametrize("age,status",[(20,"NOT_RECOMMENDED"),(21,"LOCAL_READY"),(30,"LOCAL_READY"),(31,"OLDER_CONSERVATIVE")])
def test_age_boundaries(client,age,status): assert client.post("/api/v1/dss/simulate",json=payload(duck_age_days=age)).json()["age_status"]==status

@pytest.mark.parametrize("system,count,status",[("jajar_legowo",19,"UNDER"),("jajar_legowo",20,"RECOMMENDED"),("jajar_legowo",40,"RECOMMENDED"),("jajar_legowo",41,"WARNING_ABOVE_RECOMMENDED"),("jajar_legowo",80,"WARNING_ABOVE_RECOMMENDED"),("jajar_legowo",81,"HIGH_RISK"),("tegel",20,"RECOMMENDED"),("tegel",30,"RECOMMENDED"),("tegel",31,"WARNING_ABOVE_RECOMMENDED")])
def test_density_boundaries(client,system,count,status): assert client.post("/api/v1/dss/simulate",json=payload(planting_system=system,duck_count=count)).json()["density_status"]==status

@pytest.mark.parametrize("t,valid",[(49,False),(50,True),(80,True),(81,False)])
def test_xiong_duration_guard(client,t,valid):
    body=client.post("/api/v1/dss/simulate",json=payload(literature_duration_days=t)).json(); assert (body["yield_status"]=="VALID") is valid

def test_xiong_density_domain_boundary(client):
    valid=client.post("/api/v1/dss/simulate",json=payload(duck_count=60,literature_duration_days=80)).json()
    outside=client.post("/api/v1/dss/simulate",json=payload(duck_count=61,literature_duration_days=80)).json()
    assert valid["density_ha"]==600 and valid["yield_status"]=="VALID"
    assert outside["density_ha"]==610 and outside["yield_status"]=="OUTSIDE_LITERATURE_DOMAIN"

def test_s_a14_golden_economics(client):
    body=client.post("/api/v1/dss/simulate",json=payload(literature_duration_days=50,p_gabah=6000,p_duck_buy=25000,p_duck_sell=45000)).json()
    assert body["yield_are_kg"] == pytest.approx(65.0044549762,abs=1e-8)
    assert body["cash_contribution_before_optional"] == pytest.approx(4700267.30,abs=.02)

def test_high_risk_disables_duck_revenue(client):
    body=client.post("/api/v1/dss/simulate",json=payload(duck_count=81,literature_duration_days=50)).json()
    assert body["survival_risk"]=="HIGH" and body["revenue_duck_all_sold_scenario"] is None

def test_j_zero_and_optional_calendar(client):
    body=client.post("/api/v1/dss/simulate",json=payload(duck_count=0)).json()
    assert body["density_are"]==0 and body["density_status"]=="UNDER" and body["release_date_min"] is None

def test_calendar_date_ranges(client):
    body=client.post("/api/v1/dss/simulate",json=payload(planting_date="2026-01-01")).json()
    assert (body["release_hst_min"],body["release_hst_max"],body["withdraw_hst_min"],body["withdraw_hst_max"])==(21,30,56,60)
    assert (body["release_date_min"],body["release_date_max"],body["withdraw_date_min"],body["withdraw_date_max"])==("2026-01-22","2026-01-31","2026-02-26","2026-03-02")

def test_optional_costs_and_pair_validation(client):
    body=client.post("/api/v1/dss/simulate",json=payload(literature_duration_days=50,c_feed_scenario=50,c_jaring_purchase=100,n_jaring_cycles=2,c_kandang_purchase=100,n_kandang_cycles=4)).json()
    assert body["cost_feed_scenario"]==50 and body["cost_infra_cycle"]==75
    assert body["cash_contribution_after_optional"] == pytest.approx(body["cash_contribution_before_optional"]-125)
    assert client.post("/api/v1/dss/simulate",json=payload(c_jaring_purchase=1)).status_code==400
    assert client.post("/api/v1/dss/simulate",json=payload(c_kandang_purchase=1)).status_code==400

def test_finite_and_reference_validation(client):
    assert client.post("/api/v1/dss/simulate",json=payload(planting_system="unknown")).status_code==422
    assert client.post("/api/v1/dss/simulate",json=payload(land_area_are=-1)).status_code==400
    assert client.post("/api/v1/dss/simulate",content='{"land_area_are":NaN}',headers={"content-type":"application/json"}).status_code==400
    assert client.post("/api/v1/dss/simulate",content='{"land_area_are":10,"duck_count":1,"rice_variety":"sertani","planting_system":"jajar_legowo","duck_age_days":21,"p_gabah":Infinity}',headers={"content-type":"application/json"}).status_code==400

@pytest.mark.parametrize("field,value",[("duck_count",40.0),("duck_count","40"),("duck_age_days",21.0),("duck_age_days","21")])
def test_integer_contract_rejects_coercion(client,field,value):
    assert client.post("/api/v1/dss/simulate",json=payload(**{field:value})).status_code==400

@pytest.mark.parametrize("field,value",[("land_area_are","10"),("p_gabah","6000"),("p_duck_buy","25000"),("p_duck_sell","45000"),("literature_duration_days","50"),("c_feed_scenario","10"),("c_jaring_purchase","10"),("n_jaring_cycles","2"),("c_kandang_purchase","10"),("n_kandang_cycles","2")])
def test_decimal_contract_rejects_string_coercion(client,field,value):
    assert client.post("/api/v1/dss/simulate",json=payload(**{field:value})).status_code==400

def test_openapi_documents_all_scenario_cost_inputs(client):
    schema=create_app().openapi()["components"]["schemas"]["DSSSimulationRequest"]["properties"]
    for field in ("c_feed_scenario","c_jaring_purchase","n_jaring_cycles","c_kandang_purchase","n_kandang_cycles"):
        assert schema[field]["description"]

def test_openapi_numeric_contract_does_not_advertise_string_inputs(client):
    schema=create_app().openapi()["components"]["schemas"]["DSSSimulationRequest"]["properties"]
    for field in ("land_area_are","p_gabah","p_duck_buy","p_duck_sell","literature_duration_days","c_feed_scenario","c_jaring_purchase","n_jaring_cycles","c_kandang_purchase","n_kandang_cycles"):
        assert "string" not in str(schema[field])

def test_openapi_numeric_constraints_use_standard_keywords(client):
    schema=create_app().openapi()["components"]["schemas"]["DSSSimulationRequest"]["properties"]
    assert schema["land_area_are"]["exclusiveMinimum"]==0
    assert schema["p_gabah"]["anyOf"][0]["minimum"]==0
    assert schema["n_jaring_cycles"]["anyOf"][0]["exclusiveMinimum"]==0

def test_openapi_response_documents_every_model_a_field_and_example(client):
    schema=create_app().openapi()["components"]["schemas"]["DSSSimulationResponse"]
    assert schema["example"]["model_variant"]=="A_STRICT_SEPARATION"
    assert schema["example"]["yield_are_kg"] is None
    assert all(field.get("description") for field in schema["properties"].values())

def test_runtime_evidence_acceptance_includes_database_isolation():
    from scripts.validate_model_a_runtime import acceptance_passes
    summary={"health_pass":True,"historical_pass":36,"historical_total":36,"synthetic_pass":19,"synthetic_total":19,"calendar_pass":True,"history_pass":True}
    metadata={"branch":"focus-model-a","runtime_database_changed":True,"main_database_unchanged":True}
    assert acceptance_passes(summary,metadata)
    assert not acceptance_passes(summary,metadata|{"main_database_unchanged":False})
    assert not acceptance_passes(summary,metadata|{"branch":"other-branch"})

def test_runtime_validator_requires_model_a_branch():
    from scripts.validate_model_a_runtime import require_model_a_branch
    require_model_a_branch("focus-model-a")
    with pytest.raises(RuntimeError,match="focus-model-a"):
        require_model_a_branch("other-branch")

def test_runtime_validator_snapshots_main_database_before_launch():
    from pathlib import Path
    source=Path("scripts/validate_model_a_runtime.py").read_text(encoding="utf-8")
    assert source.index("main_database_before = file_snapshot(MAIN_DATABASE_PATH)") < source.index("process = subprocess.Popen(")

def test_runtime_evidence_start_command_includes_isolation_environment():
    from pathlib import Path
    from scripts.validate_model_a_runtime import powershell_start_command
    workspace_path=Path("C:/workspace")
    database_path=Path("C:/runtime.db")
    command=powershell_start_command(["C:/Python/python.exe","-m","uvicorn","app.main:app"],workspace_path,database_path,"nonce-123")
    assert f"Set-Location '{workspace_path}'" in command
    assert f"DATABASE_PATH='{database_path}'" in command
    assert "RUNTIME_INSTANCE_ID='nonce-123'" in command
    assert "& 'C:/Python/python.exe' -m uvicorn app.main:app" in command

def test_health_exposes_runtime_nonce_only_when_configured(client,monkeypatch):
    assert client.get("/health").json()=={"status":"ok","service":"rice-duck-dss-backend"}
    monkeypatch.setenv("RUNTIME_INSTANCE_ID","audit-instance")
    assert client.get("/health").json()=={"status":"ok","service":"rice-duck-dss-backend","runtime_instance_id":"audit-instance"}

@pytest.mark.parametrize("field,value",[("rice_variety","SERTANI"),("rice_variety"," sertani "),("planting_system","JAJAR_LEGOWO"),("planting_system"," jajar_legowo ")])
def test_reference_codes_are_canonical_and_not_silently_normalized(client,field,value):
    response=client.post("/api/v1/dss/simulate",json=payload(**{field:value}))
    assert response.status_code==422

def test_runtime_price_provenance_and_no_hidden_feed(client):
    fallback=client.post("/api/v1/dss/simulate",json=payload(literature_duration_days=50)).json()
    runtime=client.post("/api/v1/dss/simulate",json=payload(literature_duration_days=50,p_gabah=7000,p_duck_buy=1,p_duck_sell=2)).json()
    assert "local-estimate fallback" in fallback["provenance"]["prices"]["p_gabah"]
    assert runtime["provenance"]["prices"]=={"p_gabah":"runtime","p_duck_buy":"runtime","p_duck_sell":"runtime"}
    assert fallback["cost_feed_scenario"] is None and fallback["cash_contribution_after_optional"] is None
    assert fallback["revenue_duck_all_sold_scenario"] == 1800000
    assert fallback["cost_duck_buy"] == 1000000

def test_v4_history_round_trip(client):
    reg=client.post("/api/v1/auth/register",json={"name":"A","email":"a@example.com","password":"password123"}); assert reg.status_code==201
    token=client.post("/api/v1/auth/login",json={"email":"a@example.com","password":"password123"}).json()["access_token"]; headers={"Authorization":f"Bearer {token}"}
    simulated=client.post("/api/v1/dss/simulate",json=payload(literature_duration_days=50),headers=headers); histories=client.get("/api/v1/dss/histories",headers=headers).json()["data"]
    assert histories[0]["schema_version"]==4
    ident=histories[0]["id"]; assert client.get(f"/api/v1/dss/histories/{ident}",headers=headers).json()==simulated.json()
    assert client.delete(f"/api/v1/dss/histories/{ident}",headers=headers).status_code==200

@pytest.mark.parametrize("schema_version",[1,2,3])
def test_legacy_history_is_not_reinterpreted_as_model_a(client,schema_version):
    from app.core.database import get_connection
    reg=client.post("/api/v1/auth/register",json={"name":"Legacy","email":"legacy@example.com","password":"password123"})
    token=client.post("/api/v1/auth/login",json={"email":"legacy@example.com","password":"password123"}).json()["access_token"]
    user_id=client.get("/api/v1/auth/me",headers={"Authorization":f"Bearer {token}"}).json()["id"]
    with get_connection() as connection:
        connection.execute("INSERT INTO dss_simulation_histories (id,user_id,schema_version,created_at,input_json,actual_scenario_json,recommended_scenario_json,comparison_json,risk_json,trace_json,notes_json,economics_json,ecology_json,environment_json,lookup_json,validation_json,data_readiness_json) VALUES (?, ?, ?, '2026-01-01T00:00:00+00:00','{}','{}','{}','{}','{}','{}','[]','{}','{}','{}','{}','{}','{}')",(f"legacy-v{schema_version}",user_id,schema_version))
    headers={"Authorization":f"Bearer {token}"}
    assert client.get("/api/v1/dss/histories",headers=headers).json()["data"]==[]
    assert client.get(f"/api/v1/dss/histories/legacy-v{schema_version}",headers=headers).status_code==404
    assert client.delete(f"/api/v1/dss/histories/legacy-v{schema_version}",headers=headers).status_code==404
    with get_connection() as connection:
        assert connection.execute("SELECT 1 FROM dss_simulation_histories WHERE id=?",(f"legacy-v{schema_version}",)).fetchone() is not None

def test_visualization_has_no_numerical_survival(client):
    body=client.post("/api/v1/dss/visualize",json=payload()).json()
    assert "survival_rate" not in str(body) and body["density_zones"][-1]["is_high_risk"] is True
