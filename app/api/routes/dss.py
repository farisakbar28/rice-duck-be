"""R2 DSS core routes (docs/03_R2_API_CONTRACT.md).

Seven user concepts (six required inputs + the optional purchase price).
Scientific/economic partial output is valid: unavailable quantities are
serialized as null with explicit availability/status metadata at HTTP 200.
Authenticated simulations persist exactly one schema-v4 snapshot.

The ``/visualize`` endpoint is intentionally NOT registered in Phase 3:
the pre-R2 visualization semantics are invalidated and the canonical R2
visualization contract is implemented in Phase 4. No legacy visualization
output is exposed in the meantime.
"""

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
)
from app.services.simulation_service import dss_service

router = APIRouter(prefix="/dss")


@router.get(
    "/options",
    response_model=DSSOptionsResponse,
    summary="Get R2 DSS input options",
    description=(
        "Mengembalikan opsi input kanonik model R2: jendela panen varietas "
        "(Sertani/Seratih 100-110 HST, Inpari 90-100 HST), rentang densitas "
        "didukung per sistem tanam (jajar_legowo 2-4, tegel 2-3 bebek/are), "
        "dan metadata harga beli bebek opsional (default Rp26.500, rentang "
        "lokal Rp25.000-28.000). Status yield lookup masih PENDING_LOOKUP; "
        "tidak ada multiplier yield yang diekspos."
    ),
)
def get_dss_options() -> DSSOptionsResponse:
    return dss_service.get_options()


@router.post(
    "/simulate",
    response_model=DSSSimulationResponse,
    summary="Run R2 DSS simulation",
    description=(
        "Menjalankan simulasi model R2: enam input wajib ditambah harga beli "
        "bebek opsional (tujuh konsep pengguna). p_duck_buy kosong/null "
        "memakai default registri Rp26.500; nilai yang diberikan harus > 0 "
        "(0 bukan berarti tanpa pembelian). Output ilmiah/ekonomi bersifat "
        "parsial dan itu valid: komponen yang tidak tersedia muncul sebagai "
        "null dengan status/kode alasan eksplisit pada HTTP 200, bukan error. "
        "Simulasi terautentikasi menyimpan satu snapshot history skema v4; "
        "autentikasi tidak mengubah hasil numerik."
    ),
    responses={
        400: {"model": ErrorResponse, "description": "Input numerik/tanggal tidak valid."},
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
    summary="List simulation histories",
    description=(
        "Mengembalikan riwayat milik user: baris R2 (model_version=R2, "
        "schema_version=4, ringkasan indeks) digabung dengan baris pra-R2 "
        "yang tetap terlihat sebagai LEGACY tanpa nilai ilmiah yang "
        "disintesis ulang."
    ),
    responses={401: {"model": ErrorResponse, "description": "Access token diperlukan."}},
)
def list_histories(
    auth: AuthContext = Depends(get_current_user),
) -> HistoryListResponse:
    return dss_service.list_histories(auth.user.id)


@router.get(
    "/histories/{history_id}",
    response_model=DSSSimulationResponse,
    summary="Get stored simulation snapshot",
    description=(
        "Mengembalikan snapshot semantik v4 persis seperti disimpan saat "
        "simulasi; respons tidak dihitung ulang dengan registry saat ini. "
        "Baris legacy (schema_version <= 3) tidak direpresentasikan ulang "
        "sebagai hasil R2 dan mengembalikan 409 legacy_history_semantics."
    ),
    responses={
        401: {"model": ErrorResponse, "description": "Access token diperlukan."},
        404: {"model": ErrorResponse, "description": "History tidak ditemukan."},
        409: {
            "model": ErrorResponse,
            "description": "Baris history legacy tidak dapat direpresentasikan sebagai snapshot R2.",
        },
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
    summary="Delete a simulation history",
    description=(
        "Menghapus history milik user (R2 v4 atau legacy) secara "
        "ownership-scoped; id milik user lain mengembalikan 404."
    ),
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


# PHASE-4 DEFERRAL: POST /dss/visualize is deliberately absent. The previous
# endpoint served invalidated pre-R2 chart semantics (fixed-yield benchmark,
# survival fallback curves); exposing it would violate docs/07. The canonical
# R2 visualization contract is implemented in Phase 4 -- no placeholder or
# fabricated chart payload is provided here (see tests/test_r2_production_path_static.py).
