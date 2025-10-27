"""
Jooble API connector (Mock implementation with real API structure).
"""
from typing import List, Dict, Any
import logging
from .base import BaseConnector

logger = logging.getLogger(__name__)


class JoobleConnector(BaseConnector):
    """Jooble job search connector."""
    
    def __init__(self, use_mock: bool = None):
        """Initialize Jooble connector."""
        import os
        from ..core.config import settings
        
        # Check for API key in environment (optional)
        self.api_key = os.getenv("JOOBLE_API_KEY", "")
        
        if use_mock is None:
            use_mock = settings.MOCK_CONNECTORS or not self.api_key
        super().__init__(use_mock=use_mock)
    
    def search_jobs(
        self,
        query: str,
        location: str = "India",
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Search jobs (mock implementation)."""
        mock_jobs = [
            {
                "title": "Performance Test Engineer",
                "company": "Global Tech Corp",
                "location": "Bangalore, India",
                "description": "Performance testing specialist needed. JMeter, LoadRunner experience required.",
                "excerpt": "Performance testing specialist needed...",
                "url": "https://jooble.org/jobs/mock/1",
                "posted_date": "2025-01-20",
                "required_skills": ["jmeter", "loadrunner", "performance testing"],
                "seniority_level": "senior"
            },
            {
                "title": "API Testing Specialist",
                "company": "Cloud Services Inc",
                "location": "Remote, India",
                "description": "Focus on API testing with Postman and REST Assured. Remote work available.",
                "excerpt": "Focus on API testing...",
                "url": "https://jooble.org/jobs/mock/2",
                "posted_date": "2025-01-21",
                "required_skills": ["api testing", "postman", "rest assured", "python"],
                "seniority_level": "mid"
            },
            {
                "title": "QA Engineer - Fintech",
                "company": "FinTech Innovations",
                "location": "Mumbai, India",
                "description": "Join our fintech team as QA engineer. Banking domain knowledge preferred.",
                "excerpt": "Join our fintech team...",
                "url": "https://jooble.org/jobs/mock/3",
                "posted_date": "2025-01-18",
                "required_skills": ["qa", "fintech", "selenium", "sql"],
                "seniority_level": "mid"
            }
        ]
        
        jobs = [self.normalize_job(job) for job in mock_jobs[:max_results]]
        logger.info(f"Jooble (MOCK): Returning {len(jobs)} jobs")
        return jobs
