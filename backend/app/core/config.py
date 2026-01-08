"""Application configuration.

Loads environment variables and provides configuration settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # API Configuration
    api_title: str = "AI-SRE Platform"
    api_version: str = "0.1.0"
    debug: bool = False
    
    # Database
    database_url: str = ""
    database_pool_size: int = 10
    
    # Redis
    redis_url: str = ""
    redis_cache_ttl: int = 300
    
    # LLM Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Integrations
    prometheus_url: str = "http://localhost:9090"
    kubernetes_api_url: str = "http://localhost:6443"
    slack_bot_token: Optional[str] = None
    pagerduty_api_key: Optional[str] = None
    github_token: Optional[str] = None
    
    # Vector Store
    pgvector_enabled: bool = True
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Agent Configuration
    max_agent_iterations: int = 10
    agent_timeout_seconds: int = 300
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = False

settings = Settings()
