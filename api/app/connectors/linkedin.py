"""
LinkedIn connector (Mock only - scraping LinkedIn violates their ToS).
"""
from typing import List, Dict, Any
import logging
from .base import BaseConnector

logger = logging.getLogger(__name__)


class LinkedInConnector(BaseConnector):
    """LinkedIn job search connector (Mock only for legal reasons)."""
    
    def __init__(self, use_mock: bool = None):
        """Initialize LinkedIn connector."""
        from ..core.config import settings
        if use_mock is None:
            use_mock = settings.MOCK_CONNECTORS
        super().__init__(use_mock=use_mock)
        if not use_mock:
            logger.warning("LinkedIn connector uses mock data only. Scraping LinkedIn may violate their Terms of Service.")
    
    def search_jobs(
        self,
        query: str,
        location: str = "India",
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Search jobs (mock data only)."""
        mock_jobs = [
            {
                "title": "Senior SDET",
                "company": "LinkedIn",
                "location": "Bangalore, Karnataka, India",
                "description": "Software Development Engineer in Test role. Build testing infrastructure at scale.",
                "excerpt": "SDET role. Build testing infrastructure...",
                "url": "https://www.linkedin.com/jobs/mock/1",
                "posted_date": "2025-01-19",
                "required_skills": ["python", "java", "kubernetes", "ci/cd", "testing"],
                "seniority_level": "senior"
            },
            {
                "title": "Quality Engineering Manager",
                "company": "Microsoft India",
                "location": "Hyderabad, Telangana, India",
                "description": "Lead quality engineering teams. Drive testing strategy and automation initiatives.",
                "excerpt": "Lead quality engineering teams...",
                "url": "https://www.linkedin.com/jobs/mock/2",
                "posted_date": "2025-01-17",
                "required_skills": ["leadership", "automation", "agile", "test strategy"],
                "seniority_level": "manager"
            },
            {
                "title": "QA Engineer - Cloud Platform",
                "company": "Amazon",
                "location": "Bangalore, Karnataka, India",
                "description": "Test cloud platform services. AWS experience required.",
                "excerpt": "Test cloud platform services...",
                "url": "https://www.linkedin.com/jobs/mock/3",
                "posted_date": "2025-01-16",
                "required_skills": ["aws", "python", "testing", "api"],
                "seniority_level": "mid"
            }
        ]
        
        jobs = [self.normalize_job(job) for job in mock_jobs[:max_results]]
        logger.info(f"LinkedIn (MOCK): Returning {len(jobs)} jobs")
        return jobs
