"""Application configuration using pydantic-settings."""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Central configuration for the AI Negotiation Arena backend."""

    # Application
    APP_NAME: str = "AI Negotiation Arena"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/negotiation_arena"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/negotiation_arena"

    # Simulation defaults
    DEFAULT_AGENT_COUNT: int = 20
    DEFAULT_ROUND_COUNT: int = 100
    DEFAULT_TICK_INTERVAL_MS: int = 500
    MAX_SPEED_MULTIPLIER: float = 10.0

    # Redis (optional)
    REDIS_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()