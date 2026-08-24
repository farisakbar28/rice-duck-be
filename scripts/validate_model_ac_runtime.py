"""Real-HTTP A+C acceptance with an isolated disposable SQLite database."""
import hashlib, json, os, socket, subprocess, sys, time, uuid
from datetime import datetime, timezone
from pathlib import Path
import httpx

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/"docs"/"runtime_evidence_model_ac.json"
MAIN_DB=ROOT/"data"/"rice_duck.db"
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
def free_port():
    sock=socket.socket(); sock.bind(("127.0.0.1",0)); port=sock.getsockname()[1]; sock.close(); return port
def expect(condition,message):
    if not condition: raise AssertionError(message)
def main():
    port=free_port(); runtime_db=ROOT/"data"/f"runtime_model_ac_{uuid.uuid4().hex}.db"; instance=uuid.uuid4().hex
    before=sha(MAIN_DB); env=os.environ.copy(); env.update({"DATABASE_PATH":str(runtime_db),"RUNTIME_INSTANCE_ID":instance,"PYTHONPATH":str(ROOT)})
    command=[sys.executable,"-m","uvicorn","app.main:app","--host","127.0.0.1","--port",str(port)]
    process=subprocess.Popen(command,cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    base=f"http://127.0.0.1:{port}"; evidence={"branch":subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip(),"base_head":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),"working_tree_dirty":bool(subprocess.check_output(["git","status","--porcelain"],cwd=ROOT,text=True).strip()),"captured_at":datetime.now(timezone.utc).isoformat(),"server_url":base,"runtime_instance_id":instance,"backend_start_command":" ".join(command),"runtime_database_path":str(runtime_db),"main_database_before":before}
    try:
        with httpx.Client(timeout=10) as client:
            for _ in range(50):
                try:
                    health=client.get(base+"/health")
                    if health.status_code==200: break
                except httpx.HTTPError: pass
                time.sleep(.1)
            else: raise RuntimeError("Uvicorn health check timed out")
            evidence["health"]=health.json()
            def simulate(data):
                response=client.post(base+"/api/v1/dss/simulate",json=data); expect(response.status_code==200,response.text); return response.json()
            common={"rice_variety":"sertani","planting_system":"jajar_legowo","duck_age_days":21}
            refs=[]
            for name,duration,ducks,expected in [("AC-R01",49,40,None),("AC-R02",50,40,65.0044549762),("AC-R03",80,40,69.7396),("AC-R04",81,40,None),("AC-R05",80,61,None),("AC-R32",32,40,None)]:
                body=simulate({**common,"land_area_are":10,"duck_count":ducks,"literature_duration_days":duration})
                expect(body["yield_are_kg"]==50,"primary changed")
                if expected is None: expect(body["yield_literature_reference_are_kg"] is None and body["literature_reference_status"]=="OUTSIDE_LITERATURE_DOMAIN",name)
                else: expect(abs(body["yield_literature_reference_are_kg"]-expected)<1e-8,name)
                refs.append({"id":name,"response":body})
            evidence["reference_cases"]=refs
            calendar=simulate({**common,"land_area_are":10,"duck_count":40,"planting_date":"2026-01-01"}); expect(calendar["release_date_min"]=="2026-01-22" and calendar["yield_literature_reference_are_kg"] is None,"calendar isolation")
            evidence["calendar"]=calendar
            no_ref=simulate({**common,"land_area_are":10,"duck_count":40}); r50=refs[1]["response"]; r80=refs[2]["response"]
            fields=["yield_are_kg","yield_total_kg","revenue_gabah","revenue_duck_all_sold_scenario","cost_duck_buy","cash_contribution_before_optional","cash_contribution_after_optional"]
            expect(all(no_ref[k]==r50[k]==r80[k] for k in fields),"primary/reference coupling")
            evidence["primary_reference_decoupling_pass"]=True
            holdout=[("H01",3.60,13,"sertani","jajar_legowo",45.83,6000,25000), ("H02",5.10,5,"sertani","jajar_legowo",48.04,6000,25000), ("H03",10,65,"sertani","jajar_legowo",60.50,6000,7539), ("H04",7.26,9,"sertani","jajar_legowo",59.37,7500,22222.22222), ("H05",5.10,10,"inpari","jajar_legowo",21.02,7500,5000), ("H06",14.41,30,"sertani","jajar_legowo",52.43,7500,10000), ("H07",10,32,"sertani","jajar_legowo",53.40,6300,0), ("H08",3.60,15,"sertani","jajar_legowo",40.42,6000,0), ("H09",10,29,"inpari","tegel",38.65,6000,0), ("H10",3,6,"sertani","jajar_legowo",13.50,6000,25000), ("H11",3.77,8,"sertani","jajar_legowo",36.47,6000,25000)]
            rows=[]; errors=[]
            for ident,area,ducks,variety,system,actual,pg,pb in holdout:
                body=simulate({"land_area_are":area,"duck_count":ducks,"rice_variety":variety,"planting_system":system,"duck_age_days":21,"p_gabah":pg,"p_duck_buy":pb,"p_duck_sell":45000})
                expect(body["literature_reference_status"]=="OUTSIDE_LITERATURE_DOMAIN" and body["yield_literature_reference_are_kg"] is None,ident)
                expect(abs(body["cost_duck_buy"]-ducks*pb)<.01,ident); expect(abs(body["cash_contribution_before_optional"]-(50*area*pg+ducks*45000-ducks*pb))<.01,ident)
                errors.append(50-actual); rows.append({"id":ident,"response":body,"actual_yield_are":actual})
            mae=sum(abs(x) for x in errors)/11; rmse=(sum(x*x for x in errors)/11)**.5; ordered=sorted(abs(x) for x in errors); medae=ordered[5]; bias=sum(errors)/11
            evidence["holdout"]=rows; evidence["holdout_metrics"]={"MAE":mae,"RMSE":rmse,"MedAE":medae,"Bias":bias}; evidence["summary"]={"holdout_pass":"11/11","holdout_metrics_pass":abs(mae-11.979)<.01 and abs(rmse-15.990)<.01 and abs(bias-7.307)<.01,"holdout_cost_duck_buy_audit_pass":"11/11","holdout_cash_contribution_audit_pass":"11/11","holdout_reference_abstention_pass":"11/11","reference_cases_pass":"6/6","primary_reference_decoupling_pass":True,"calendar_pass":True}
            register=client.post(base+"/api/v1/auth/register",json={"name":"Runtime User","email":"runtime@example.com","password":"password123"}); expect(register.status_code==201,register.text)
            token=client.post(base+"/api/v1/auth/login",json={"email":"runtime@example.com","password":"password123"}).json()["access_token"]; headers={"Authorization":"Bearer "+token}
            saved=client.post(base+"/api/v1/dss/simulate",json={**common,"land_area_are":10,"duck_count":40,"literature_duration_days":50},headers=headers).json(); listing=client.get(base+"/api/v1/dss/histories",headers=headers).json(); hid=listing["data"][0]["id"]; detail=client.get(base+f"/api/v1/dss/histories/{hid}",headers=headers).json(); expect(listing["data"][0]["schema_version"]==4 and detail==saved,"history v4")
            expect(client.delete(base+f"/api/v1/dss/histories/{hid}",headers=headers).status_code==200,"history delete"); expect(client.get(base+f"/api/v1/dss/histories/{hid}",headers=headers).status_code==404,"history 404")
            evidence["history"]={"schema_version":4,"round_trip":True,"delete_then_404":True}
    finally:
        process.terminate(); process.wait(timeout=10)
        evidence["main_database_after"]=sha(MAIN_DB); evidence["main_database_unchanged"]=before==evidence["main_database_after"]
        EVIDENCE.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")
        if runtime_db.exists(): runtime_db.unlink()
    print(json.dumps(evidence["summary"],indent=2))
if __name__=="__main__": main()
