from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_user, get_optional_current_user
from app.domain.models import AuthContext
from app.schemas.common import ErrorResponse
from app.schemas.dss import DeleteHistoryResponse, DSSOptionsResponse, DSSSimulationRequest, DSSSimulationResponse, HistoryListResponse, VisualizationResponse
from app.services.simulation_service import dss_service
from app.services.visualization_service import visualization_service
router=APIRouter(prefix="/dss")
@router.get("/options",response_model=DSSOptionsResponse,summary="Model A reference options",description="Canonical rice-variety and planting-system reference codes; these references do not alter the Xiong equation.")
def get_dss_options(): return dss_service.get_options()
@router.post("/simulate",response_model=DSSSimulationResponse,summary="Run Model A strict-separation simulation",description="Xiong yield is conditional on an explicit literature-duration input and valid domain.",responses={400:{"model":ErrorResponse},401:{"model":ErrorResponse},422:{"model":ErrorResponse}})
def simulate_dss(payload:DSSSimulationRequest,auth:AuthContext|None=Depends(get_optional_current_user)): return dss_service.simulate(payload,auth.user.id if auth else None)
@router.get("/histories",response_model=HistoryListResponse,summary="List Model A v4 histories",description="Lists only version-4 Model A records for the authenticated user. v1-v3 remain historical and are not reinterpreted.")
def list_histories(auth:AuthContext=Depends(get_current_user)): return dss_service.list_histories(auth.user.id)
@router.get("/histories/{history_id}",response_model=DSSSimulationResponse,summary="Get exact Model A v4 history",description="Returns the typed Model A response persisted with a v4 history record; non-v4 records are not exposed as Model A.")
def get_history(history_id:str,auth:AuthContext=Depends(get_current_user)): return dss_service.get_history(history_id,auth.user.id)
@router.delete("/histories/{history_id}",response_model=DeleteHistoryResponse,summary="Delete Model A v4 history",description="Deletes only the authenticated user's v4 Model A record. Historical v1-v3 rows are preserved.")
def delete_history(history_id:str,auth:AuthContext=Depends(get_current_user)): return dss_service.delete_history(history_id,auth.user.id)
@router.post("/visualize",response_model=VisualizationResponse,summary="Model A reference visualization",description="Shows Model A density/readiness zones and conditional scenario economics without a numerical survival curve or fabricated unavailable values.")
def visualize_dss(payload:DSSSimulationRequest): return visualization_service.generate_visualization_series(payload)
