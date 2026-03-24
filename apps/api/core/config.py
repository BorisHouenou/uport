from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── App ──────────────────────────────────────────────────
    app_name: str = "Uportai API"
    app_version: str = "0.1.0"
    environment: Literal["development", "staging", "production"] = "development"
    secret_key: str = "change-me-in-production"
    allowed_origins: str = "http://localhost:3000"

    # ─── Database ─────────────────────────────────────────────
    database_url: str
    database_url_sync: str
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # ─── Redis ────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # ─── Auth (Clerk) ─────────────────────────────────────────
    clerk_secret_key: str = ""
    clerk_publishable_key: str = ""

    # ─── AI ───────────────────────────────────────────────────
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    voyage_api_key: str = ""
    llm_model: str = "claude-sonnet-4-6"
    llm_temperature: float = 0.0
    embedding_model: str = "voyage-3"
    rag_top_k: int = 8
    confidence_threshold: float = 0.75  # below this → human review queue

    # ─── Payments ─────────────────────────────────────────────
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""

    # ─── Storage ──────────────────────────────────────────────
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "ca-central-1"
    s3_bucket_documents: str = "uportai-documents"

    # ─── Observability ────────────────────────────────────────
    sentry_dsn: str = ""
    log_level: str = "INFO"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
