
"""
Test privacy and GDPR compliance.
"""
import pytest
from api.app.utils.privacy import privacy_manager


def test_sanitize_resume_removes_email():
    """Test that email addresses are removed from resume text."""
    text = "Contact me at john.doe@example.com for more info"
    sanitized = privacy_manager.sanitize_resume_text(text)
    assert "john.doe@example.com" not in sanitized
    assert "[EMAIL]" in sanitized


def test_sanitize_resume_removes_phone():
    """Test that phone numbers are removed."""
    text = "Call me at 9876543210 or +91-9876543210"
    sanitized = privacy_manager.sanitize_resume_text(text)
    assert "9876543210" not in sanitized
    assert "[PHONE]" in sanitized


def test_sanitize_resume_truncates_long_text():
    """Test that long text is truncated."""
    text = "A" * 10000
    sanitized = privacy_manager.sanitize_resume_text(text, max_length=100)
    assert len(sanitized) <= 120  # 100 + truncation message
    assert "[TRUNCATED]" in sanitized


def test_anonymize_job_removes_raw_data():
    """Test that raw job data is removed when anonymizing."""
    job = {
        "title": "Software Engineer",
        "company": "Tech Corp",
        "url": "https://example.com/job/123",
        "raw": {"sensitive": "data"}
    }
    anonymized = privacy_manager.anonymize_job_data(job)
    assert "raw" not in anonymized
    assert "url_hash" in anonymized


def test_store_raw_default_false():
    """Test that raw storage is disabled by default."""
    from api.app.core.config import Settings
    settings = Settings()
    assert privacy_manager.should_store_raw(settings) is False
