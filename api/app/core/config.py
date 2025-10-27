"""
Application configuration management.
"""
from pydantic_settings import BaseSettings, Field
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./jobfinder.db")

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # JWT Security
    SECRET_KEY: str = "dev_secret_key_change_in_production"
    JWT_SECRET_KEY: str = "dev_jwt_secret_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 5000
    FRONTEND_URL: str = "http://localhost:3000"

    # Job connector settings
    MOCK_CONNECTORS: bool = Field(default=False, env="MOCK_CONNECTORS")
    ADZUNA_APP_ID: Optional[str] = Field(default=None, env="ADZUNA_APP_ID")
    ADZUNA_APP_KEY: Optional[str] = Field(default=None, env="ADZUNA_APP_KEY")
    JOOBLE_API_KEY: str = ""
    INDEED_PUBLISHER_ID: str = ""

    # Resume Processing
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "docx", "txt"]
    SPACY_MODEL: str = "en_core_web_sm"
    USE_EMBEDDINGS: bool = False

    # Location Defaults
    DEFAULT_COUNTRY: str = "India"
    PRIORITY_LOCATIONS: str = "Bangalore,Remote"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"
    ENABLE_METRICS: bool = True

    # Development
    DEV_MODE: bool = True
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()