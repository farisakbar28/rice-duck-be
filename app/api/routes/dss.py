from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_user, get_optional_current_user
from app.domain.models import AuthContext
from app.schemas.common import ErrorResponse
from app.schemas.dss import DeleteHistoryResponse, DSSOptionsResponse, DSSSimulationRequest, DSSSimulationResponse, HistoryListResponse, VisualizationResponse
from app.services.simulation_service import dss_service
from app.services.visualization_service import visualization_service
router=APIRouter(prefix="/dss")
@router.get("/options",response_model=DSSOptionsResponse,summary="Get DSS dropdown options")
def get_dss_options(): return dss_service.get_options()
@router.post("/simulate",response_model=DSSSimulationResponse,summary="Run A+C dual-evidence simulation",description="C0 local production is primary. Xiong is an optional literature reference only; there is no numerical fusion.",responses={400:{"model":ErrorResponse},401:{"model":ErrorResponse},422:{"model":ErrorResponse}})
def simulate_dss(payload:DSSSimulationRequest,auth:AuthContext|None=Depends(get_optional_current_user)): return dss_service.simulate(payload,user_id=auth.user.id if auth else None)
@router.get("/histories",response_model=HistoryListResponse)
def list_histories(auth:AuthContext=Depends(get_current_user)): return dss_service.list_histories(auth.user.id)
@router.get("/histories/{history_id}",response_model=DSSSimulationResponse)
def get_history(history_id:str,auth:AuthContext=Depends(get_current_user)): return dss_service.get_history(history_id,auth.user.id)
@router.delete("/histories/{history_id}",response_model=DeleteHistoryResponse)
def delete_history(history_id:str,auth:AuthContext=Depends(get_current_user)): return dss_service.delete_history(history_id,auth.user.id)
@router.post("/visualize",response_model=VisualizationResponse,summary="Visualize A+C gates and primary economics",description="Uses primary C0 economics. An unavailable literature reference is never plotted as zero.")
def visualize_dss(payload:DSSSimulationRequest): return visualization_service.generate_visualization_series(payload)
