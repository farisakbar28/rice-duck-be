import sqlite3

from app.core.exceptions import AuthenticationError, ConflictError
from app.core.security import create_access_token, hash_password, verify_password
from app.domain.models import User
from app.repositories.user_repository import user_repository
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    UserResponse,
)


class AuthService:
    def register(self, payload: RegisterRequest) -> RegisterResponse:
        if user_repository.get_by_email(payload.email) is not None:
            raise ConflictError(message="Email is already registered.", field="email")
        try:
            user = user_repository.create(
                name=payload.name,
                email=payload.email,
                password_hash=hash_password(payload.password),
            )
        except sqlite3.IntegrityError:
            raise ConflictError(
                message="Email is already registered.",
                field="email",
            ) from None
        return RegisterResponse(
            message="User registered successfully",
            user=self.to_user_response(user),
        )

    def login(self, payload: LoginRequest) -> LoginResponse:
        user = user_repository.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise AuthenticationError(message="Invalid email or password.")
        return LoginResponse(
            access_token=create_access_token(user.id),
            token_type="Bearer",
            user=self.to_user_response(user),
        )

    def to_user_response(self, user: User) -> UserResponse:
        return UserResponse(id=user.id, name=user.name, email=user.email)


auth_service = AuthService()
