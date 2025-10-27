
"""
Test job scrapers.
"""
import pytest
from unittest.mock import AsyncMock, patch
from api.app.scrapers.rss_scraper import RSSJobScraper
from api.app.scrapers.base import BaseScraper


def test_base_scraper_generates_hash():
    """Test that base scraper generates consistent hashes."""
    scraper = RSSJobScraper()
    
    job1 = {
        "title": "Software Engineer",
        "company": "Tech Corp",
        "location": "Bangalore",
        "url": "https://example.com/job1"
    }
    
    job2 = {
        "title": "Software Engineer",
        "company": "Tech Corp",
        "location": "Bangalore",
        "url": "https://example.com/job1"
    }
    
    hash1 = scraper.generate_job_hash(job1)
    hash2 = scraper.generate_job_hash(job2)
    
    assert hash1 == hash2


def test_base_scraper_detects_duplicates():
    """Test duplicate detection."""
    scraper = RSSJobScraper()
    
    job = {
        "title": "Software Engineer",
        "company": "Tech Corp",
        "location": "Bangalore",
        "url": "https://example.com/job1"
    }
    
    assert not scraper.is_duplicate(job)
    assert scraper.is_duplicate(job)  # Second time should be duplicate


def test_rss_scraper_extracts_skills():
    """Test skill extraction from text."""
    scraper = RSSJobScraper()
    
    text = "We are looking for a Python developer with React and AWS experience"
    skills = scraper.extract_skills_from_text(text)
    
    assert "python" in skills
    assert "react" in skills
    assert "aws" in skills


def test_rss_scraper_infers_seniority():
    """Test seniority level inference."""
    scraper = RSSJobScraper()
    
    assert scraper.infer_seniority("Senior Software Engineer", "") == "senior"
    assert scraper.infer_seniority("Junior Developer", "") == "junior"
    assert scraper.infer_seniority("Mid-Level Engineer", "") == "mid"
    assert scraper.infer_seniority("Software Engineer", "") == "mid"  # Default


@pytest.mark.asyncio
async def test_rss_scraper_respects_rate_limit():
    """Test that rate limiter is used."""
    import time
    
    scraper = RSSJobScraper(rate_limit=10.0)  # 10 requests per second
    
    start = time.time()
    await scraper.rate_limiter.acquire()
    await scraper.rate_limiter.acquire()
    elapsed = time.time() - start
    
    # Should take at least 0.1 seconds for 2 requests at 10/sec
    assert elapsed >= 0.05
