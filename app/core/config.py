from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Rice Duck DSS Backend"
    app_env: str = "development"
    app_debug: bool = True
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    host: str = "127.0.0.1"
    port: int = 8000
    database_path: str = "data/rice_duck.db"
    cors_allowed_origins: str = "*"
    # Deliberately has no source-controlled default.  Every process must set a
    # deployment-specific secret through JWT_SECRET_KEY or an untracked .env.
    jwt_secret_key: str = Field(min_length=32)
    jwt_access_token_minutes: int = 120
    password_hash_iterations: int = 600_000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("jwt_secret_key")
    @classmethod
    def reject_example_secret(cls, value: str) -> str:
        if "replace-with-" in value.lower() or "example" in value.lower():
            raise ValueError("JWT_SECRET_KEY must be replaced with a private runtime secret.")
        return value

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
