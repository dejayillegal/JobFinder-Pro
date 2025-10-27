"""
Naukri connector (Mock with Playwright structure for future implementation).
"""
from typing import List, Dict, Any
import logging
from .base import BaseConnector
from .robots_checker import robots_checker

logger = logging.getLogger(__name__)


class NaukriConnector(BaseConnector):
    """Naukri job search connector with robots.txt compliance."""
    
    def __init__(self, use_mock: bool = True):
        """Initialize Naukri connector."""
        super().__init__(use_mock=True)
    
    def can_scrape(self) -> bool:
        """Check if scraping is allowed per robots.txt."""
        test_url = "https://www.naukri.com/qa-jobs"
        allowed = robots_checker.can_fetch(test_url, "JobFinderBot")
        
        if not allowed:
            logger.warning("Naukri robots.txt prohibits scraping. Using mock data only.")
        
        return allowed
    
    def search_jobs(
        self,
        query: str,
        location: str = "India",
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search jobs (mock implementation).
        
        Note: Real Playwright implementation would go here when enabled in staging.
        Must check robots.txt compliance first using self.can_scrape().
        """
        if not self.can_scrape():
            logger.info("Using mock data due to robots.txt restrictions")
        
        mock_jobs = [
            {
                "title": "QA Test Engineer",
                "company": "Naukri Learning",
                "location": "Noida, Uttar Pradesh",
                "description": "Manual and automation testing role. 3-5 years experience required.",
                "excerpt": "Manual and automation testing role...",
                "url": "https://www.naukri.com/jobs/mock/1",
                "posted_date": "2025-01-22",
                "required_skills": ["selenium", "manual testing", "jira", "sql"],
                "seniority_level": "mid"
            },
            {
                "title": "Automation Test Lead",
                "company": "InfoEdge India",
                "location": "Bangalore, Karnataka",
                "description": "Lead automation testing initiatives. Selenium WebDriver expertise required.",
                "excerpt": "Lead automation testing initiatives...",
                "url": "https://www.naukri.com/jobs/mock/2",
                "posted_date": "2025-01-21",
                "required_skills": ["selenium", "java", "test automation", "leadership"],
                "seniority_level": "senior"
            },
            {
                "title": "Software Tester",
                "company": "Tech Mahindra",
                "location": "Pune, Maharashtra",
                "description": "Software testing position in banking domain. Manual and automated testing.",
                "excerpt": "Software testing in banking domain...",
                "url": "https://www.naukri.com/jobs/mock/3",
                "posted_date": "2025-01-20",
                "required_skills": ["manual testing", "selenium", "banking domain"],
                "seniority_level": "mid"
            }
        ]
        
        jobs = [self.normalize_job(job) for job in mock_jobs[:max_results]]
        logger.info(f"Naukri (MOCK): Returning {len(jobs)} jobs")
        return jobs
