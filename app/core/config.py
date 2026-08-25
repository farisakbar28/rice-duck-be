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
    # Git commit that produced a response (docs/05 section 4). Injected by
    # the deployment environment; never discovered via subprocess per
    # request. Null is valid -- the v4 column is nullable.
    model_commit_sha: str | None = None
    cors_allowed_origins: str = "*"
    jwt_secret_key: str = "mSXdI785UBtEkxe1ejL5AqYnt5uD2jEeSDmrD60I3Jw"
    jwt_access_token_minutes: int = 120
    password_hash_iterations: int = 600_000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

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
