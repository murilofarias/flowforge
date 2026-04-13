from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://flowforge:flowforge@postgres:5432/flowforge"
    redis_url: str = "redis://redis:6379/0"
    fixture_mode: bool = True
    api_cors_origins: str = "http://localhost:5173"
    webhook_signing_secret: str = "dev-secret"
    openai_api_key: str = ""
    hubspot_token: str = ""
    salesforce_token: str = ""
    slack_webhook_url: str = ""
    http_allowed_hosts: str = "*"
    secret_key: str = "dev-secret-change-me"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.api_cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
