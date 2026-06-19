from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.domain.models import AuthContext
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    UserResponse,
)
from app.schemas.common import ErrorResponse
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth")


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=201,
    responses={
        409: {"model": ErrorResponse, "description": "Email sudah terdaftar."},
        422: {"model": ErrorResponse, "description": "Request tidak valid."},
    },
)
def register(payload: RegisterRequest) -> RegisterResponse:
    return auth_service.register(payload)


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={401: {"model": ErrorResponse, "description": "Email atau password salah."}},
)
def login(payload: LoginRequest) -> LoginResponse:
    return auth_service.login(payload)


@router.get(
    "/me",
    response_model=UserResponse,
    responses={401: {"model": ErrorResponse, "description": "Access token tidak valid."}},
)
def get_me(auth: AuthContext = Depends(get_current_user)) -> UserResponse:
    return auth_service.to_user_response(auth.user)
