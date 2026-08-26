from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


JWT_SECRET_PLACEHOLDER = "replace-with-a-long-random-secret"
LOCAL_APP_VERSION = "0.0.0-dev"
MIN_PASSWORD_HASH_ITERATIONS = 600_000
_TRIVIAL_PRODUCTION_SECRETS = {
    JWT_SECRET_PLACEHOLDER,
    "change-me",
    "changeme",
}


class Settings(BaseSettings):
    app_name: str = "Rice Duck DSS Backend"
    app_env: str = "development"
    app_debug: bool = True
    # Deployment automation supplies a release version. Source checkouts use
    # an explicit development marker and never imply an invented release.
    app_version: str = LOCAL_APP_VERSION
    api_v1_prefix: str = "/api/v1"
    host: str = "127.0.0.1"
    port: int = 8000
    database_path: str = "data/rice_duck.db"
    # Git commit that produced a response (docs/05 section 4). Injected by
    # the deployment environment; never discovered via subprocess per
    # request. Null is valid -- the v4 column is nullable.
    model_commit_sha: str | None = None
    cors_allowed_origins: str = "*"
    jwt_secret_key: str = ""
    jwt_access_token_minutes: int = Field(default=120, gt=0)
    password_hash_iterations: int = Field(default=MIN_PASSWORD_HASH_ITERATIONS, gt=0)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_security_policy(self) -> Self:
        environment = self.app_env.strip().lower()
        object.__setattr__(self, "app_env", environment)
        secret = self.jwt_secret_key.strip()
        if not secret:
            raise ValueError(
                "JWT_SECRET_KEY is required. Set an explicit secret in the environment; "
                "the application will not generate or use a built-in fallback."
            )

        if (
            environment != "test"
            and self.password_hash_iterations < MIN_PASSWORD_HASH_ITERATIONS
        ):
            raise ValueError(
                "PASSWORD_HASH_ITERATIONS must be at least 600000 outside APP_ENV=test."
            )

        if environment == "production":
            if self.app_debug:
                raise ValueError("APP_DEBUG must be false in APP_ENV=production.")
            origins = self.cors_allowed_origins_list
            if not origins or "*" in origins:
                raise ValueError(
                    "CORS_ALLOWED_ORIGINS must list explicit origins in production; "
                    "wildcard and empty values are forbidden."
                )
            if secret.lower() in _TRIVIAL_PRODUCTION_SECRETS:
                raise ValueError(
                    "JWT_SECRET_KEY must not use a placeholder or trivial value in production."
                )
        return self

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        if self.cors_allowed_origins.strip() == "*":
            return ["*"]
        return [
            origin.strip()
            for origin in self.cors_allowed_origins.split(",")
            if origin.strip()
        ]


settings = Settings()
