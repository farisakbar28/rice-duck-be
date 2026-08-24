from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_optional_current_user
from app.domain.models import AuthContext
from app.schemas.common import ErrorResponse
from app.schemas.dss import (
    DeleteHistoryResponse,
    DSSOptionsResponse,
    DSSSimulationRequest,
    DSSSimulationResponse,
    HistoryListResponse,
    VisualizationResponse,
)
from app.services.simulation_service import dss_service
from app.services.visualization_service import visualization_service

router = APIRouter(prefix="/dss")


@router.get(
    "/options",
    response_model=DSSOptionsResponse,
    summary="Get DSS dropdown options",
    description=(
        "Mengembalikan dropdown varietas padi dan sistem tanam. "
        "jajar_legowo hanya mewakili Jajar Legowo 2:1 (SoT §3)."
    ),
)
def get_dss_options() -> DSSOptionsResponse:
    return dss_service.get_options()


@router.post(
    "/simulate",
    response_model=DSSSimulationResponse,
    summary="Run DSS simulation",
    description=(
        "Menjalankan model matematika deterministik padi-bebek per SoT FINAL. "
        "Model C frozen C0 dengan 5 input inti; harga, kalender, dan biaya adalah opsional. "
        "Output adalah scenario cash contribution, bukan net profit."
    ),
    responses={
        400: {"model": ErrorResponse, "description": "Input tidak valid."},
        401: {"model": ErrorResponse, "description": "Bearer token tidak valid."},
        422: {
            "model": ErrorResponse,
            "description": "Referensi varietas atau sistem tanam tidak ditemukan.",
        },
    },
)
def simulate_dss(
    payload: DSSSimulationRequest,
    auth: AuthContext | None = Depends(get_optional_current_user),
) -> DSSSimulationResponse:
    return dss_service.simulate(
        payload,
        user_id=auth.user.id if auth is not None else None,
    )


@router.get(
    "/histories",
    response_model=HistoryListResponse,
    responses={401: {"model": ErrorResponse, "description": "Access token diperlukan."}},
)
def list_histories(
    auth: AuthContext = Depends(get_current_user),
) -> HistoryListResponse:
    return dss_service.list_histories(auth.user.id)


@router.get(
    "/histories/{history_id}",
    response_model=DSSSimulationResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Access token diperlukan."},
        404: {"model": ErrorResponse, "description": "History tidak ditemukan."},
    },
)
def get_history(
    history_id: str,
    auth: AuthContext = Depends(get_current_user),
) -> DSSSimulationResponse:
    return dss_service.get_history(history_id, auth.user.id)


@router.delete(
    "/histories/{history_id}",
    response_model=DeleteHistoryResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Access token diperlukan."},
        404: {"model": ErrorResponse, "description": "History tidak ditemukan."},
    },
)
def delete_history(
    history_id: str,
    auth: AuthContext = Depends(get_current_user),
) -> DeleteHistoryResponse:
    return dss_service.delete_history(history_id, auth.user.id)


@router.post(
    "/visualize",
    response_model=VisualizationResponse,
    summary="Get visualization zone series",
    description=(
        "Menghasilkan data visualisasi grafik zona density, zona umur bebek, "
        "dan financial waterfall berdasarkan SoT FINAL. "
        "Tidak menggunakan multiplier produksi atau survival numerik."
    ),
    responses={
        422: {"model": ErrorResponse, "description": "Request tidak valid."},
    },
)
def visualize_dss(
    payload: DSSSimulationRequest,
) -> VisualizationResponse:
    return visualization_service.generate_visualization_series(payload)
