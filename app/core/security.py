import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.exceptions import AuthenticationError


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        settings.password_hash_iterations,
    )
    return (
        f"pbkdf2_sha256${settings.password_hash_iterations}$"
        f"{_base64_encode(salt)}${_base64_encode(digest)}"
    )


def verify_password(password: str, encoded_hash: str) -> bool:
    try:
        algorithm, iterations_text, salt_text, digest_text = encoded_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_text)
        salt = _base64_decode(salt_text)
        expected_digest = _base64_decode(digest_text)
    except (TypeError, ValueError):
        return False

    actual_digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
    )
    return hmac.compare_digest(actual_digest, expected_digest)


def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_access_token_minutes)).timestamp()),
    }
    header_segment = _json_segment({"alg": "HS256", "typ": "JWT"})
    payload_segment = _json_segment(payload)
    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    signature = hmac.new(
        settings.jwt_secret_key.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    return f"{header_segment}.{payload_segment}.{_base64_encode(signature)}"


def decode_access_token(token: str) -> str:
    try:
        header_segment, payload_segment, signature_segment = token.split(".")
        signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
        expected_signature = hmac.new(
            settings.jwt_secret_key.encode("utf-8"),
            signing_input,
            hashlib.sha256,
        ).digest()
        if not hmac.compare_digest(
            _base64_decode(signature_segment),
            expected_signature,
        ):
            raise AuthenticationError()

        header = json.loads(_base64_decode(header_segment))
        payload = json.loads(_base64_decode(payload_segment))
        if header.get("alg") != "HS256":
            raise AuthenticationError()
        if int(payload["exp"]) <= int(datetime.now(timezone.utc).timestamp()):
            raise AuthenticationError()
        user_id = payload.get("sub")
        if not isinstance(user_id, str) or not user_id:
            raise AuthenticationError()
        return user_id
    except AuthenticationError:
        raise
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        raise AuthenticationError() from None


def _json_segment(value: dict) -> str:
    raw = json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return _base64_encode(raw)


def _base64_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _base64_decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + ("=" * (-len(value) % 4)))
