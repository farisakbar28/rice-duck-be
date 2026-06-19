from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import AuthenticationError
from app.core.security import decode_access_token
from app.domain.models import AuthContext
from app.repositories.user_repository import user_repository

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthContext:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthenticationError(message="Bearer access token is required.")
    user = user_repository.get_by_id(decode_access_token(credentials.credentials))
    if user is None:
        raise AuthenticationError()
    return AuthContext(user=user)


def get_optional_current_user(
    authorization: Annotated[str | None, Header()] = None,
) -> AuthContext | None:
    if authorization is None:
        return None
    scheme, separator, token = authorization.partition(" ")
    if separator != " " or scheme.lower() != "bearer" or not token:
        raise AuthenticationError(message="Bearer access token is invalid.")
    user = user_repository.get_by_id(decode_access_token(token))
    if user is None:
        raise AuthenticationError()
    return AuthContext(user=user)
