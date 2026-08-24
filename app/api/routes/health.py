from fastapi import APIRouter

from app.schemas.common import HealthResponse
from app.core.config import settings

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Mengembalikan status layanan dan identitas service backend.",
)
def health_check() -> HealthResponse:
    return HealthResponse(runtime_instance_id=settings.runtime_instance_id)
