"""Phase 4: configuration fails closed before an unsafe app can start."""

import pytest
from pydantic import ValidationError

from app.core.config import (
    JWT_SECRET_PLACEHOLDER,
    LOCAL_APP_VERSION,
    MIN_PASSWORD_HASH_ITERATIONS,
    Settings,
)
from app.core.security import create_access_token, decode_access_token


def _settings(**overrides) -> Settings:
    values = {
        "app_env": "test",
        "app_debug": True,
        "jwt_secret_key": "explicit-test-secret",
        "cors_allowed_origins": "*",
        "password_hash_iterations": 1000,
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


@pytest.mark.parametrize("environment", ["development", "test", "production"])
def test_missing_or_blank_secret_is_rejected_in_every_environment(environment: str) -> None:
    with pytest.raises(ValidationError, match="JWT_SECRET_KEY is required"):
        _settings(app_env=environment, jwt_secret_key="   ")


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"app_debug": True}, "APP_DEBUG must be false"),
        ({"app_debug": False, "cors_allowed_origins": "*"}, "explicit origins"),
        ({"app_debug": False, "cors_allowed_origins": ""}, "explicit origins"),
        ({"app_debug": False, "cors_allowed_origins": "https://example.com", "jwt_secret_key": JWT_SECRET_PLACEHOLDER}, "placeholder"),
    ],
)
def test_production_rejects_unsafe_settings(overrides: dict, message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        _settings(
            app_env="production",
            password_hash_iterations=MIN_PASSWORD_HASH_ITERATIONS,
            **overrides,
        )


def test_non_test_environment_rejects_weakened_password_hashing() -> None:
    with pytest.raises(ValidationError, match="at least 600000"):
        _settings(app_env="development", password_hash_iterations=1000)


def test_valid_production_configuration_can_create_app(monkeypatch) -> None:
    production = _settings(
        app_env="production",
        app_debug=False,
        jwt_secret_key="a-unique-production-secret-value-for-this-test",
        cors_allowed_origins="https://app.example.com,https://admin.example.com",
        password_hash_iterations=MIN_PASSWORD_HASH_ITERATIONS,
        database_path="tests/rice_duck_test.db",
        app_version="2026.08.26",
    )
    import app.core.database as database_module
    import app.main as main_module

    monkeypatch.setattr(database_module, "settings", production)
    monkeypatch.setattr(main_module, "settings", production)
    created = main_module.create_app()
    assert created.version == "2026.08.26"
    assert production.cors_allowed_origins_list == [
        "https://app.example.com",
        "https://admin.example.com",
    ]


def test_local_version_marker_and_token_semantics() -> None:
    assert LOCAL_APP_VERSION == "0.0.0-dev"
    token = create_access_token("user-123")
    assert decode_access_token(token) == "user-123"
