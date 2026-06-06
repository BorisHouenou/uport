from functools import lru_cache
from typing import Literal
from urllib.parse import urlparse, urlunparse

from pydantic import model_validator
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
    # Railway PostgreSQL add-on sets DATABASE_URL as postgresql://...
    # We normalise to asyncpg and derive the sync URL automatically.
    database_url: str
    database_url_sync: str = ""  # auto-derived from database_url if not set
    db_pool_size: int = 10
    db_max_overflow: int = 20

    @model_validator(mode="after")
    def normalise_database_urls(self) -> "Settings":
        url = self.database_url
        # Normalise postgres:// → postgresql:// (Railway uses the short form)
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://") :]
        # Ensure async URL has +asyncpg driver
        if url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        # Railway PostgreSQL requires SSL; asyncpg needs ssl=require not sslmode=require
        url = url.replace("sslmode=require", "ssl=require")
        if "ssl=" not in url and "sslmode=" not in url:
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}ssl=require"
        self.database_url = url
        # Derive sync URL — strip asyncpg driver, convert ssl=require → sslmode=require
        if not self.database_url_sync:
            sync = url.replace("+asyncpg", "").replace("ssl=require", "sslmode=require")
            self.database_url_sync = sync
        return self

    # ─── Redis ────────────────────────────────────────────────
    # Railway's Redis add-on injects REDIS_URL automatically.
    # CELERY_BROKER_URL / CELERY_RESULT_BACKEND are derived from it when not set.
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = ""
    celery_result_backend: str = ""

    @model_validator(mode="after")
    def derive_celery_urls(self) -> "Settings":
        parsed = urlparse(self.redis_url)
        base = urlunparse(parsed._replace(path=""))
        if not self.celery_broker_url:
            self.celery_broker_url = f"{base}/1"
        if not self.celery_result_backend:
            self.celery_result_backend = f"{base}/2"
        return self

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

    # ─── Email (AWS SES) ──────────────────────────────────────
    ses_from_email: str = ""  # e.g. "noreply@uportai.com"
    app_base_url: str = "https://app.uportai.com"

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
