"""
Application configuration management.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import List, Optional, Any
import os
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database
    DATABASE_URL: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./jobfinder.db"))

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
    API_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5000"

    # Job connector settings
    MOCK_CONNECTORS: bool = False
    ADZUNA_APP_ID: Optional[str] = None
    ADZUNA_APP_KEY: Optional[str] = None
    RAPIDAPI_KEY: Optional[str] = None
    JOOBLE_API_KEY: Optional[str] = None
    INDEED_PUBLISHER_ID: Optional[str] = None

    # Resume Processing
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "docx", "txt"]
    SPACY_MODEL: str = "en_core_web_sm"
    USE_EMBEDDINGS: bool = False
    USE_ADVANCED_MATCHING: bool = True

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

    # Job Caching
    JOB_CACHE_TTL_HOURS: int = 24
    ENABLE_JOB_DEDUPLICATION: bool = True

    # RSS Feed Settings
    RSS_FEED_CACHE_TTL: int = 3600  # 1 hour in seconds
    RSS_MAX_FEEDS_PER_SOURCE: int = 50

    # Web Scraping Settings
    SCRAPING_ENABLED: bool = False
    SCRAPING_USER_AGENT: str = "Mozilla/5.0 (compatible; JobFinderBot/1.0)"
    SCRAPING_DELAY_MIN: float = 2.0  # Minimum delay between requests in seconds
    SCRAPING_DELAY_MAX: float = 5.0  # Maximum delay between requests

    # Job Matching Algorithm
    SIMILARITY_THRESHOLD: float = 0.3  # Minimum similarity score (0-1)
    SKILLS_WEIGHT: float = 0.5
    EXPERIENCE_WEIGHT: float = 0.25
    LOCATION_WEIGHT: float = 0.15
    TITLE_WEIGHT: float = 0.10

    # Vector Database (for embeddings)
    USE_VECTOR_DB: bool = False
    VECTOR_DB_TYPE: str = "faiss"  # Options: faiss, pinecone
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None

    # RSS Feeds Configuration
    RSS_FEEDS: str = ""  # Comma-separated list of RSS feed URLs
    RATE_LIMIT_PER_SECOND: float = 2.0

    # Privacy & Storage
    STORE_RESUME_RAW: bool = False  # GDPR compliance - don't store raw by default
    ANONYMIZE_JOBS: bool = True  # Anonymize job data
    
    # Embedding Backend
    EMBEDDING_BACKEND: str = "tfidf"  # Options: tfidf, sbert
    
    # Alembic
    ALEMBIC_INI: str = "alembic.ini"

    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    @classmethod
    def parse_allowed_extensions(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # If it's a comma-separated string
                return [ext.strip() for ext in v.split(",")]
        return v


# Singleton with error handling
try:
    settings = Settings()
except Exception as e:
    import sys
    print(f"ERROR: Failed to load settings: {e}", file=sys.stderr)
    print("Please check your .env file and ensure all required variables are set.", file=sys.stderr)
    raise