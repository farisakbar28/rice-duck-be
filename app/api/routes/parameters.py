from fastapi import APIRouter

from app.schemas.parameters import ActiveParameterSetResponse
from app.services.parameter_service import parameter_service

router = APIRouter()


@router.get("/active", response_model=ActiveParameterSetResponse)
def get_active_parameter_set() -> ActiveParameterSetResponse:
    return ActiveParameterSetResponse(data=parameter_service.get_active_parameter_set())

