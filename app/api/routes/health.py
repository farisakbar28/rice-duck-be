from fastapi import APIRouter

from app.schemas.common import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Mengembalikan status layanan dan identitas service backend.",
)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service="rice-duck-dss-backend")

