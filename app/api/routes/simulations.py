from fastapi import APIRouter, HTTPException, status

from app.schemas.simulation import SimulationRequest, SimulationResponse
from app.services.simulation_service import SimulationInputError, simulation_service

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

