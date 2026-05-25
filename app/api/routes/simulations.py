from fastapi import APIRouter, HTTPException, status

from app.schemas.simulation import SimulationListResponse, SimulationRequest, SimulationResponse
from app.services.simulation_service import (
    SimulationInputError,
    SimulationNotFoundError,
    simulation_service,
)

router = APIRouter()


@router.post("/evaluate", response_model=SimulationResponse)
def evaluate_simulation(payload: SimulationRequest) -> SimulationResponse:
    try:
        return simulation_service.evaluate(payload)
    except SimulationInputError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get("", response_model=SimulationListResponse)
def list_simulations() -> SimulationListResponse:
    return SimulationListResponse(data=simulation_service.list_simulations())


@router.get("/{simulation_id}", response_model=SimulationResponse)
def get_simulation_detail(simulation_id: str) -> SimulationResponse:
    try:
        return simulation_service.get_simulation_detail(simulation_id)
    except SimulationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
