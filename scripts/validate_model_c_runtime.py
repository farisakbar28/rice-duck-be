"""Run Model C acceptance against a real, isolated uvicorn process."""
import hashlib,json,os,socket,sqlite3,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
from secrets import token_urlsafe
from urllib.error import HTTPError
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'docs/runtime_evidence_model_c.json'
H=[('H01',3.60,13,'sertani','jajar_legowo',45.83,6000),('H02',5.10,5,'sertani','jajar_legowo',48.04,6000),('H03',10,65,'sertani','jajar_legowo',60.50,6000),('H04',7.26,9,'sertani','jajar_legowo',59.37,7500),('H05',5.10,10,'inpari','jajar_legowo',21.02,7500),('H06',14.41,30,'sertani','jajar_legowo',52.43,7500),('H07',10,32,'sertani','jajar_legowo',53.40,6300),('H08',3.60,15,'sertani','jajar_legowo',40.42,6000),('H09',10,29,'inpari','tegel',38.65,6000),('H10',3,6,'sertani','jajar_legowo',13.50,6000),('H11',3.77,8,'sertani','jajar_legowo',36.47,6000)]
def snap(p): return None if not p.exists() else {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def call(base,path,body=None,token=None,method=None):
 data=None if body is None else json.dumps(body).encode(); headers={'Content-Type':'application/json'} if data else {}
 if token: headers['Authorization']='Bearer '+token
 try:
  with urlopen(Request(base+path,data=data,headers=headers,method=method or ('POST' if body is not None else 'GET')),timeout=10) as x: status,raw=x.status,x.read().decode()
 except HTTPError as x: status,raw=x.code,x.read().decode()
 return {'timestamp':datetime.now(timezone.utc).isoformat(),'request':body,'http_status':status,'raw_response':raw,'response':json.loads(raw)}
def verify_legacy_history_over_http(base,database_path,user_id,token):
 legacy_ids=[f'legacy-runtime-v{version}' for version in (1,2,3)]
 with sqlite3.connect(database_path) as connection:
  for identifier,version in zip(legacy_ids,(1,2,3)):
   connection.execute('INSERT INTO dss_simulation_histories (id,user_id,schema_version,created_at) VALUES (?,?,?,?)',(identifier,user_id,version,'2026-01-01T00:00:00+00:00'))
 listing=call(base,'/api/v1/dss/histories',None,token)
 checks=[]
 for identifier in legacy_ids:
  detail=call(base,f'/api/v1/dss/histories/{identifier}',None,token)
  deletion=call(base,f'/api/v1/dss/histories/{identifier}',None,token,'DELETE')
  checks.append({'id':identifier,'detail':detail,'delete':deletion,'pass':detail['http_status']==404 and deletion['http_status']==404})
 with sqlite3.connect(database_path) as connection:
  preserved=connection.execute('SELECT id FROM dss_simulation_histories WHERE id IN (?,?,?)',legacy_ids).fetchall()
 physical_preserved=sorted(row[0] for row in preserved)==legacy_ids
 return {'seeded_ids':legacy_ids,'list':listing,'checks':checks,'physical_preserved':physical_preserved,'pass':listing['http_status']==200 and listing['response']['data']==[] and all(item['pass'] for item in checks) and physical_preserved}
def main():
 branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
 if branch!='focus-model-c': raise SystemExit('required branch focus-model-c')
 base_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 working_tree_dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip())
 port=socket.socket(); port.bind(('127.0.0.1',0)); n=port.getsockname()[1]; port.close(); nonce=token_urlsafe(18); db=ROOT/'data'/f'model_c_runtime_{nonce}.db'; main_db=ROOT/'data/rice_duck.db'; before=snap(main_db)
 env=os.environ|{'DATABASE_PATH':str(db),'RUNTIME_INSTANCE_ID':nonce}; p=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port',str(n)],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); base=f'http://127.0.0.1:{n}'
 try:
  health=None
  for _ in range(100):
   try:
    health=call(base,'/health');
    if health['http_status']==200: break
   except OSError: time.sleep(.1)
  assert health and health['response'].get('runtime_instance_id')==nonce
  rows=[]
  for ident,a,j,v,s,actual,pg in H:
   e=call(base,'/api/v1/dss/simulate',{'land_area_are':a,'duck_count':j,'rice_variety':v,'planting_system':s,'duck_age_days':21,'p_gabah':pg,'p_duck_sell':45000}); b=e['response']; err=b['yield_are_kg']-actual; expected_revenue=50*a*pg; revenue_ok=abs(b['revenue_gabah']-expected_revenue)<0.001; e.update({'id':ident,'actual_yield':actual,'backend_yield':b['yield_are_kg'],'error':err,'density_expected':j/a,'density_returned':b['density_are'],'revenue_expected':expected_revenue,'revenue_returned':b['revenue_gabah'],'revenue_check':revenue_ok,'pass':e['http_status']==200 and b['yield_are_kg']==50 and abs(b['density_are']-j/a)<1e-9 and revenue_ok}); rows.append(e)
  es=[x['error'] for x in rows]; metrics={'MAE':sum(abs(x) for x in es)/11,'RMSE':(sum(x*x for x in es)/11)**.5,'MedAE':sorted(abs(x) for x in es)[5],'Bias':sum(es)/11}
  frozen_metrics={'MAE':11.979,'RMSE':15.990,'MedAE':9.583,'Bias':7.307}
  metrics_pass=all(abs(metrics[key]-expected)<=0.005 for key,expected in frozen_metrics.items())
  cases=[('S-C01',{'duck_count':20},'RECOMMENDED'),('S-C02',{'duck_count':40},'RECOMMENDED'),('S-C03',{'duck_count':41},'WARNING_ABOVE_RECOMMENDED'),('S-C04',{'duck_count':80},'WARNING_ABOVE_RECOMMENDED'),('S-C05',{'duck_count':81},'HIGH_RISK'),('S-C06',{'duck_count':30,'planting_system':'tegel'},'RECOMMENDED'),('S-C07',{'duck_count':31,'planting_system':'tegel'},'WARNING_ABOVE_RECOMMENDED'),('S-C08',{'duck_count':20,'duck_age_days':20},'NOT_RECOMMENDED'),('S-C09',{'duck_count':20},'RECOMMENDED'),('S-C10',{'duck_count':20},'RECOMMENDED'),('S-C11',{'duck_count':0},'UNDER')]
  synt=[]
  for i,o,expect in cases:
   e=call(base,'/api/v1/dss/simulate',{'land_area_are':10,'rice_variety':'sertani','planting_system':'jajar_legowo','duck_age_days':21}|o); b=e['response']; actual=b['age_status'] if i=='S-C08' else b['density_status']; ok=e['http_status']==200 and actual==expect and b['yield_are_kg']==50
   if i=='S-C04': ok=ok and b['survival_risk'] is None and 'N_survive' not in b
   if i=='S-C05': ok=ok and b['survival_risk']=='HIGH' and b['revenue_duck_all_sold_scenario'] is None and b['cash_contribution_before_optional'] is None and b['cash_contribution_after_optional'] is None
   if i=='S-C09': ok=ok and [b['yield_total_kg'],b['revenue_gabah'],b['revenue_duck_all_sold_scenario'],b['cost_duck_buy'],b['cash_contribution_before_optional']]==[500,3000000,900000,500000,3400000]
   if i=='S-C10': ok=ok and b['cost_feed_scenario'] is None and b['cost_infra_cycle'] is None and b['cash_contribution_after_optional'] is None
   if i=='S-C11': ok=ok and b['revenue_duck_all_sold_scenario']==0 and b['cost_duck_buy']==0
   if i=='S-C08':
    age_results=[]
    for age,expected in [(20,'NOT_RECOMMENDED'),(21,'LOCAL_READY'),(30,'LOCAL_READY'),(31,'OLDER_CONSERVATIVE')]:
     age_entry=call(base,'/api/v1/dss/simulate',{'land_area_are':10,'duck_count':20,'rice_variety':'sertani','planting_system':'jajar_legowo','duck_age_days':age})
     age_results.append({'age_days':age,'expected':expected,'actual':age_entry['response'].get('age_status'),'pass':age_entry['http_status']==200 and age_entry['response'].get('age_status')==expected})
    e['age_boundary_checks']=age_results; ok=ok and all(item['pass'] for item in age_results)
   e.update({'id':i,'pass':ok}); synt.append(e)
  e=call(base,'/api/v1/dss/simulate',{'land_area_are':0,'duck_count':1,'rice_variety':'sertani','planting_system':'jajar_legowo','duck_age_days':21}); e.update({'id':'S-C12','pass':e['http_status']==400}); synt.append(e)
  cal=call(base,'/api/v1/dss/simulate',{'land_area_are':10,'duck_count':20,'rice_variety':'sertani','planting_system':'jajar_legowo','duck_age_days':21,'planting_date':'2026-01-01'}); cal_unanchored=call(base,'/api/v1/dss/simulate',{'land_area_are':10,'duck_count':20,'rice_variety':'sertani','planting_system':'jajar_legowo','duck_age_days':21}); cal['unanchored']=cal_unanchored; cal['pass']=cal['http_status']==200 and [cal['response'][key] for key in ('release_hst_min','release_hst_max','withdraw_hst_min','withdraw_hst_max')]==[21,30,56,60] and [cal['response'][key] for key in ('release_date_min','release_date_max','withdraw_date_min','withdraw_date_max')]==['2026-01-22','2026-01-31','2026-02-26','2026-03-02'] and cal_unanchored['http_status']==200 and [cal_unanchored['response'][key] for key in ('release_hst_min','release_hst_max','withdraw_hst_min','withdraw_hst_max')]==[21,30,56,60] and all(cal_unanchored['response'][key] is None for key in ('release_date_min','release_date_max','withdraw_date_min','withdraw_date_max'))
  suffix=str(int(time.time()*1000000)); email=f'model-c-{suffix}@example.com'; register=call(base,'/api/v1/auth/register',{'name':'Model C Runtime','email':email,'password':'password123'}); login=call(base,'/api/v1/auth/login',{'email':email,'password':'password123'}); token=login['response'].get('access_token') if login['http_status']==200 else None; hp={'land_area_are':10,'duck_count':20,'rice_variety':'sertani','planting_system':'jajar_legowo','duck_age_days':21}; sim=call(base,'/api/v1/dss/simulate',hp,token); listing=call(base,'/api/v1/dss/histories',None,token); hid=listing['response']['data'][0]['id'] if listing['http_status']==200 and listing['response']['data'] else ''; detail=call(base,f'/api/v1/dss/histories/{hid}',None,token); deletion=call(base,f'/api/v1/dss/histories/{hid}',None,token,'DELETE'); gone=call(base,f'/api/v1/dss/histories/{hid}',None,token); register['request']['password']='[REDACTED]'; login['request']['password']='[REDACTED]'; login['response']['access_token']='[REDACTED]'; login['raw_response']='[REDACTED: contains access token]'; history={'steps':[register,login,sim,listing,detail,deletion,gone],'pass':[x['http_status'] for x in [register,login,sim,listing,detail,deletion,gone]]==[201,200,200,200,200,200,404] and listing['response']['data'][0]['schema_version']==4 and detail['response']==sim['response']}
  legacy=verify_legacy_history_over_http(base,db,register['response']['user']['id'],token); history['legacy']=legacy; history['pass']=history['pass'] and legacy['pass']
  after=snap(main_db); evidence={'branch':branch,'base_head':base_head,'working_tree_dirty':working_tree_dirty,'captured_at':datetime.now(timezone.utc).isoformat(),'server_url':base,'runtime_instance_id':nonce,'backend_start_command':'python -m uvicorn app.main:app','runtime_database_path':str(db),'main_database_before':before,'main_database_after':after,'main_database_unchanged':before==after,'health':health,'holdout':rows,'holdout_metrics':metrics,'frozen_holdout_metrics':frozen_metrics,'synthetic':synt,'calendar':cal,'history':history,'summary':{'holdout_pass':sum(x['pass'] for x in rows),'holdout_total':11,'holdout_metrics_pass':metrics_pass,'synthetic_pass':sum(x['pass'] for x in synt),'synthetic_total':12,'calendar_pass':cal['pass'],'history_pass':history['pass']}}
  evidence['holdout_input_limitations']=['p_duck_buy source values are not present for H01-H11 in docs/tes_skenario.md; branch-C fallback was used and source-price arithmetic is not auditable']
  OUT.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)); print(json.dumps(evidence['summary'])); return 0 if evidence['summary']['holdout_pass']==11 and metrics_pass and evidence['summary']['synthetic_pass']==12 and cal['pass'] and history['pass'] else 1
 finally:
  p.terminate(); p.wait(timeout=10)
if __name__=='__main__': raise SystemExit(main())
