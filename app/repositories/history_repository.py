"""Versioned persistence: v1-v3 untouched; v4 contains exact Model C payloads."""
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4
from app.core.database import get_connection
@dataclass(frozen=True)
class ModelCHistory: id:str; schema_version:int; created_at:datetime; payload:dict
class HistoryRepository:
 def create_v4(self,user_id,payload,response):
  identifier=str(uuid4()); now=datetime.now(timezone.utc); document={"input":payload.model_dump(mode="json"),"response":response.model_dump(mode="json")}
  with get_connection() as c: c.execute("INSERT INTO dss_simulation_histories (id,user_id,schema_version,created_at,input_json,actual_scenario_json,recommended_scenario_json,comparison_json,risk_json,trace_json,notes_json,economics_json,ecology_json,environment_json,lookup_json,validation_json,data_readiness_json,model_c_payload_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(identifier,user_id,4,now.isoformat(),"{}","{}","{}","{}","{}","{}","[]","{}","{}","{}","{}","{}","{}",json.dumps(document,ensure_ascii=False,sort_keys=True)))
  return identifier
 def _row(self,row): return ModelCHistory(row["id"],4,datetime.fromisoformat(row["created_at"]),json.loads(row["model_c_payload_json"]))
 def list_v4_by_user(self,user_id):
  with get_connection() as c: rows=c.execute("SELECT * FROM dss_simulation_histories WHERE user_id=? AND schema_version=4 ORDER BY created_at DESC",(user_id,)).fetchall()
  return [self._row(x) for x in rows]
 def get_v4(self,hid,user_id):
  with get_connection() as c: row=c.execute("SELECT * FROM dss_simulation_histories WHERE id=? AND user_id=? AND schema_version=4",(hid,user_id)).fetchone()
  return self._row(row) if row else None
 def delete_by_id_and_user(self,hid,user_id):
  with get_connection() as c: return c.execute("DELETE FROM dss_simulation_histories WHERE id=? AND user_id=? AND schema_version=4",(hid,user_id)).rowcount>0
history_repository=HistoryRepository()
