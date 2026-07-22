from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AgroGuard API"
    app_version: str = "0.2.0"
    environment: str = "development"
    debug: bool = False
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./agroguard.db"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    telegram_bot_token: SecretStr | None = None
    telegram_chat_id: str | None = None
    openweather_api_key: SecretStr | None = None
    llm_api_key: SecretStr | None = None
    llm_model: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="AGROGUARD_",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
