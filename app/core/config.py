from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Rice Duck DSS Backend"
    app_env: str = "development"
    app_debug: bool = True
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    host: str = "127.0.0.1"
    port: int = 8000
    de_random_seed: int = 42

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

