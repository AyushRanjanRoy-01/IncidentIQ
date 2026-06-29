"""Application configuration.

Loads settings from environment variables (and an optional ``.env`` file) using
pydantic-settings. Every field has a sensible default so the application can boot
with **zero configuration** for local development and tests. Production deployments
override these via environment variables / secrets.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings sourced from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------ App
    app_name: str = "IncidentIQ"
    api_title: str = "IncidentIQ — AI-SRE Platform API"
    api_version: str = "0.1.0"
    environment: Literal["local", "test", "staging", "production"] = "local"
    debug: bool = True
    log_level: str = "INFO"
    log_json: bool = True

    # CORS (comma-separated list, or "*")
    cors_origins: str = "*"

    # ------------------------------------------------------------- Database
    # Default to a local SQLite file so the app runs with no external services.
    # Production overrides with e.g. postgresql+asyncpg://user:pass@host:5432/db
    database_url: str = "sqlite+aiosqlite:///./incidentiq.db"
    database_echo: bool = False
    database_pool_size: int = 10

    # ---------------------------------------------------------------- Redis
    # Optional. When unset/unreachable the app degrades to an in-process cache.
    redis_url: str = ""
    redis_cache_ttl: int = 300

    # ----------------------------------------------------------- Security
    # NOTE: override jwt_secret_key in any non-local environment.
    jwt_secret_key: str = "dev-insecure-change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    # Seed demo users on startup (local/dev only). Disable in production.
    seed_demo_users: bool = True

    # Rate limiting (per-client, fixed window)
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 120
    rate_limit_window_seconds: int = 60

    # ----------------------------------------------------------------- LLM
    # Provider for the multi-agent RCA. "auto" uses OpenAI when a key is present,
    # otherwise falls back to the deterministic mock provider (offline-friendly).
    llm_provider: Literal["auto", "openai", "mock"] = "auto"
    openai_api_key: str = ""
    openai_base_url: str = ""  # optional override (Azure / proxy / local)
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 800
    llm_timeout_seconds: int = 30

    # Embeddings: deterministic local hashing embedder by default (no network).
    # Set to "openai" to use OpenAI embeddings when a key is present.
    embedding_provider: Literal["local", "openai"] = "local"
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 256  # used by the local hashing embedder

    # ------------------------------------------------------------- Agents
    rca_auto_propose_threshold: float = 0.6  # min confidence to auto-propose fix
    agent_timeout_seconds: int = 60

    # ------------------------------------------------- External integrations
    # All integrations run in mock mode unless explicitly enabled + configured.
    integrations_mock_mode: bool = True
    prometheus_url: str = "http://localhost:9090"
    kubernetes_enabled: bool = False
    slack_bot_token: str = ""
    pagerduty_api_key: str = ""
    github_token: str = ""

    # ------------------------------------------------------- Observability
    otel_enabled: bool = False
    otel_exporter_otlp_endpoint: str = ""

    @field_validator("cors_origins")
    @classmethod
    def _strip_origins(cls, v: str) -> str:
        return v.strip()

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def openai_ready(self) -> bool:
        return bool(self.openai_api_key.strip())


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()


# Module-level singleton for convenient imports: ``from app.core.config import settings``
settings = get_settings()
