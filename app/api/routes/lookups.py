from fastapi import APIRouter

from app.schemas.lookups import PlantingSystemListResponse, RiceVarietyListResponse
from app.services.simulation_service import simulation_service

router = APIRouter()


@router.get("/rice-varieties", response_model=RiceVarietyListResponse)
def get_rice_varieties() -> RiceVarietyListResponse:
    return RiceVarietyListResponse(data=simulation_service.list_rice_varieties())


@router.get("/planting-systems", response_model=PlantingSystemListResponse)
def get_planting_systems() -> PlantingSystemListResponse:
    return PlantingSystemListResponse(data=simulation_service.list_planting_systems())

