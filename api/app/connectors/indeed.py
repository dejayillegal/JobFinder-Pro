"""
Indeed India connector (Mock implementation with real API structure).
"""
from typing import List, Dict, Any
import logging
from .base import BaseConnector

logger = logging.getLogger(__name__)


class IndeedConnector(BaseConnector):
    """Indeed India job search connector."""
    
    def __init__(self, use_mock: bool = None):
        """Initialize Indeed connector."""
        from ..core.config import settings
        if use_mock is None:
            use_mock = settings.MOCK_CONNECTORS
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
                "title": "Software Test Engineer",
                "company": "Indeed Tech Labs",
                "location": "Bangalore, Karnataka",
                "description": "We are seeking a talented Software Test Engineer to join our QA team. Experience with manual and automated testing required.",
                "excerpt": "Seeking talented Software Test Engineer...",
                "url": "https://www.indeed.co.in/jobs/mock/1",
                "posted_date": "2025-01-22",
                "required_skills": ["manual testing", "selenium", "java", "sql"],
                "seniority_level": "mid"
            },
            {
                "title": "QA Analyst - Mobile Testing",
                "company": "Mobile First Company",
                "location": "Hyderabad, Telangana",
                "description": "Mobile testing specialist needed. Experience with iOS and Android testing frameworks.",
                "excerpt": "Mobile testing specialist needed...",
                "url": "https://www.indeed.co.in/jobs/mock/2",
                "posted_date": "2025-01-21",
                "required_skills": ["mobile testing", "appium", "ios", "android"],
                "seniority_level": "mid"
            },
            {
                "title": "Junior QA Engineer",
                "company": "Startup Labs",
                "location": "Remote",
                "description": "Entry level QA position. We'll train you in modern testing practices.",
                "excerpt": "Entry level QA position...",
                "url": "https://www.indeed.co.in/jobs/mock/3",
                "posted_date": "2025-01-23",
                "required_skills": ["testing", "python", "api testing"],
                "seniority_level": "junior"
            },
            {
                "title": "Test Automation Engineer",
                "company": "Enterprise Solutions Ltd",
                "location": "Pune, Maharashtra",
                "description": "Build and maintain test automation frameworks. Cypress and Selenium experience preferred.",
                "excerpt": "Build and maintain test automation frameworks...",
                "url": "https://www.indeed.co.in/jobs/mock/4",
                "posted_date": "2025-01-19",
                "required_skills": ["cypress", "selenium", "javascript", "ci/cd"],
                "seniority_level": "senior"
            }
        ]
        
        jobs = [self.normalize_job(job) for job in mock_jobs[:max_results]]
        logger.info(f"Indeed (MOCK): Returning {len(jobs)} jobs")
        return jobs
