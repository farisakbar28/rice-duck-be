from fastapi import APIRouter

from app.schemas.simulation import (
    SimulationDashboardSummaryResponse,
    SimulationListResponse,
    SimulationPreviewRequest,
    SimulationPreviewResponse,
    SimulationRequest,
    SimulationResponse,
)
from app.services.simulation_service import simulation_service

router = APIRouter()


@router.post("/preview-context", response_model=SimulationPreviewResponse)
def preview_simulation_context(payload: SimulationPreviewRequest) -> SimulationPreviewResponse:
    return simulation_service.preview_context(payload)


@router.post("/evaluate", response_model=SimulationResponse)
def evaluate_simulation(payload: SimulationRequest) -> SimulationResponse:
    return simulation_service.evaluate(payload)


@router.get("", response_model=SimulationListResponse)
def list_simulations() -> SimulationListResponse:
    return SimulationListResponse(data=simulation_service.list_simulations())


@router.get("/{simulation_id}/summary", response_model=SimulationDashboardSummaryResponse)
def get_simulation_summary(simulation_id: str) -> SimulationDashboardSummaryResponse:
    return simulation_service.get_simulation_summary(simulation_id)


@router.get("/{simulation_id}", response_model=SimulationResponse)
def get_simulation_detail(simulation_id: str) -> SimulationResponse:
    return simulation_service.get_simulation_detail(simulation_id)
