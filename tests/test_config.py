
"""
Test configuration loading.
"""
import pytest
import os
from api.app.core.config import Settings


def test_config_loads_with_env_example():
    """Test that config loads with .env.example values."""
    # Set minimal required env vars
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    
    try:
        settings = Settings()
        assert settings.DATABASE_URL is not None
        assert "sqlite" in settings.DATABASE_URL or "postgresql" in settings.DATABASE_URL
        assert settings.REDIS_URL is not None
        assert settings.SECRET_KEY is not None
    except Exception as e:
        pytest.fail(f"Settings failed to load: {e}")


def test_config_gdpr_defaults():
    """Test that GDPR-compliant defaults are set."""
    settings = Settings()
    assert settings.STORE_RESUME_RAW is False, "Raw resume storage should be disabled by default"
    assert settings.ANONYMIZE_JOBS is True, "Job anonymization should be enabled by default"


def test_config_rate_limit():
    """Test rate limit configuration."""
    settings = Settings()
    assert settings.RATE_LIMIT_PER_SECOND > 0
    assert settings.RATE_LIMIT_PER_SECOND <= 10, "Rate limit should be conservative"
