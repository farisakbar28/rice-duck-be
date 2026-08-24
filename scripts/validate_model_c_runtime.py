"""Run Model C acceptance against a real, isolated uvicorn process."""
import hashlib,json,os,socket,sqlite3,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
from secrets import token_urlsafe
from urllib.error import HTTPError
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'docs/runtime_evidence_model_c.json'
H=[
 {'id':'H01','raw_row':8,'area':3.60,'J':13,'variety':'sertani','planting_system':'jajar_legowo','actual_yield':45.83,'p_gabah':6000,'p_duck_buy':25000},
 {'id':'H02','raw_row':9,'area':5.10,'J':5,'variety':'sertani','planting_system':'jajar_legowo','actual_yield':48.04,'p_gabah':6000,'p_duck_buy':25000},
 {'id':'H03','raw_row':11,'area':10,'J':65,'variety':'sertani','planting_system':'jajar_legowo','actual_yield':60.50,'p_gabah':6000,'p_duck_buy':7539},
 {'id':'H04','raw_row':14,'area':7.26,'J':9,'variety':'sertani','planting_system':'jajar_legowo','actual_yield':59.37,'p_gabah':7500,'p_duck_buy':22222.22222},
 {'id':'H05','raw_row':23,'area':5.10,'J':10,'variety':'inpari','planting_system':'jajar_legowo','actual_yield':21.02,'p_gabah':7500,'p_duck_buy':5000},
 {'id':'H06','raw_row':25,'area':14.41,'J':30,'variety':'sertani','planting_system':'jajar_legowo','actual_yield':52.43,'p_gabah':7500,'p_duck_buy':10000},
 {'id':'H07','raw_row':38,'area':10,'J':32,'variety':'sertani','planting_system':'jajar_legowo','actual_yield':53.40,'p_gabah':6300,'p_duck_buy':0,'planting_date':'2024-04-22'},
 {'id':'H08','raw_row':43,'area':3.60,'J':15,'variety':'sertani','planting_system':'jajar_legowo','actual_yield':40.42,'p_gabah':6000,'p_duck_buy':0,'planting_date':'2024-10-01'},
 {'id':'H09','raw_row':44,'area':10,'J':29,'variety':'inpari','planting_system':'tegel','actual_yield':38.65,'p_gabah':6000,'p_duck_buy':0,'planting_date':'2024-09-28'},
 {'id':'H10','raw_row':47,'area':3,'J':6,'variety':'sertani','planting_system':'jajar_legowo','actual_yield':13.50,'p_gabah':6000,'p_duck_buy':25000},
 {'id':'H11','raw_row':62,'area':3.77,'J':8,'variety':'sertani','planting_system':'jajar_legowo','actual_yield':36.47,'p_gabah':6000,'p_duck_buy':25000},
]
HOLDOUT_P_DUCK_BUY_SOURCE={'file':'DSS_Padi_Bebek_Rekap_Bersih_v10(1).xlsx','sheet':'Dataset Actual Bersih','join_key':'Excel Row (Sumber)','field':'Buy Price Duck (Rp/ekor)'}
HOLDOUT_PLANTING_DATE_SOURCE={'file':'DSS_Padi_Bebek_Rekap_Bersih_v10(1).xlsx','sheet':'Dataset Actual Bersih','join_key':'Excel Row (Sumber)','field':'Tanggal Tanam (Sumber)'}
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
 env=os.environ|{'DATABASE_PATH':str(db),'RUNTIME_INSTANCE_ID':nonce,'JWT_SECRET_KEY':token_urlsafe(48)}; p=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port',str(n)],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); base=f'http://127.0.0.1:{n}'
 try:
  health=None
  for _ in range(100):
   try:
    health=call(base,'/health');
    if health['http_status']==200: break
   except OSError: time.sleep(.1)
  assert health and health['response'].get('runtime_instance_id')==nonce
  rows=[]
  for row in H:
   ident,raw_row,a,j,v,s,actual,pg,pb=(row[key] for key in ('id','raw_row','area','J','variety','planting_system','actual_yield','p_gabah','p_duck_buy'))
   request={'land_area_are':a,'duck_count':j,'rice_variety':v,'planting_system':s,'duck_age_days':21,'p_gabah':pg,'p_duck_buy':pb,'p_duck_sell':45000}
   planting_date=row.get('planting_date')
   if planting_date is not None: request['planting_date']=planting_date
   e=call(base,'/api/v1/dss/simulate',request); b=e['response']; err=b['yield_are_kg']-actual; expected_revenue=50*a*pg; expected_cost=j*pb; expected_cash=expected_revenue+j*45000-expected_cost; revenue_ok=abs(b['revenue_gabah']-expected_revenue)<0.001; cost_ok=abs(b['cost_duck_buy']-expected_cost)<=.01; cash_ok=abs(b['cash_contribution_before_optional']-expected_cash)<=.01; price_runtime=b['provenance']['prices']['p_duck_buy']['source']=='runtime' and b['provenance']['prices']['p_duck_buy']['status']=='runtime'; calendar_ok=(all(b[key] is None for key in ('release_date_min','release_date_max','withdraw_date_min','withdraw_date_max')) if planting_date is None else all(b[key] is not None for key in ('release_date_min','release_date_max','withdraw_date_min','withdraw_date_max'))); e.update({'id':ident,'raw_row':raw_row,'source_planting_date':planting_date,'actual_yield':actual,'backend_yield':b['yield_are_kg'],'error':err,'density_expected':j/a,'density_returned':b['density_are'],'density_status':b['density_status'],'revenue_expected':expected_revenue,'revenue_returned':b['revenue_gabah'],'revenue_check':revenue_ok,'p_duck_buy_source':pb,'cost_duck_buy_expected':expected_cost,'cost_duck_buy_backend':b['cost_duck_buy'],'cost_duck_buy_check':cost_ok,'cash_contribution_expected':expected_cash,'cash_contribution_backend':b['cash_contribution_before_optional'],'cash_contribution_check':cash_ok,'p_duck_buy_provenance_runtime':price_runtime,'calendar_window':{key:b[key] for key in ('release_date_min','release_date_max','withdraw_date_min','withdraw_date_max')},'calendar_check':calendar_ok,'pass':e['http_status']==200 and b['yield_are_kg']==50 and abs(b['density_are']-j/a)<1e-9 and revenue_ok and cost_ok and cash_ok and price_runtime and calendar_ok}); rows.append(e)
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
  after=snap(main_db); cost_pass=sum(x['cost_duck_buy_check'] for x in rows); cash_pass=sum(x['cash_contribution_check'] for x in rows); calendar_holdout_pass=sum(x['calendar_check'] for x in rows); evidence={'branch':branch,'base_head':base_head,'working_tree_dirty':working_tree_dirty,'captured_at':datetime.now(timezone.utc).isoformat(),'server_url':base,'runtime_instance_id':nonce,'backend_start_command':'python -m uvicorn app.main:app','runtime_database_path':str(db),'main_database_before':before,'main_database_after':after,'main_database_unchanged':before==after,'health':health,'holdout_p_duck_buy_source':HOLDOUT_P_DUCK_BUY_SOURCE,'holdout_planting_date_source':HOLDOUT_PLANTING_DATE_SOURCE,'holdout':rows,'holdout_metrics':metrics,'frozen_holdout_metrics':frozen_metrics,'synthetic':synt,'calendar':cal,'history':history,'summary':{'holdout_pass':sum(x['pass'] for x in rows),'holdout_total':11,'holdout_metrics_pass':metrics_pass,'holdout_cost_duck_buy_audit_pass':cost_pass,'holdout_cost_duck_buy_audit_total':11,'holdout_cash_contribution_audit_pass':cash_pass,'holdout_cash_contribution_audit_total':11,'holdout_calendar_audit_pass':calendar_holdout_pass,'holdout_calendar_audit_total':11,'synthetic_pass':sum(x['pass'] for x in synt),'synthetic_total':12,'calendar_pass':cal['pass'],'history_pass':history['pass']}}
  OUT.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)); print(json.dumps(evidence['summary'])); return 0 if evidence['summary']['holdout_pass']==11 and metrics_pass and cost_pass==11 and cash_pass==11 and calendar_holdout_pass==11 and evidence['summary']['synthetic_pass']==12 and cal['pass'] and history['pass'] else 1
 finally:
  p.terminate(); p.wait(timeout=10)
if __name__=='__main__': raise SystemExit(main())
