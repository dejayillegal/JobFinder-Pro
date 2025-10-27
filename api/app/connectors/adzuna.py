"""
Adzuna API connector with real API integration and mock fallback.
"""
from typing import List, Dict, Any
import httpx
import logging
from datetime import datetime
from .base import BaseConnector, retry_with_backoff
from ..core.config import settings

logger = logging.getLogger(__name__)


class AdzunaConnector(BaseConnector):
    """Adzuna job search API connector."""
    
    BASE_URL = "https://api.adzuna.com/v1/api/jobs"
    
    def __init__(self, use_mock: bool = None):
        """Initialize Adzuna connector."""
        if use_mock is None:
            use_mock = settings.MOCK_CONNECTORS or not (settings.ADZUNA_APP_ID and settings.ADZUNA_APP_KEY)
        
        super().__init__(use_mock=use_mock)
        self.app_id = settings.ADZUNA_APP_ID
        self.app_key = settings.ADZUNA_APP_KEY
    
    @retry_with_backoff(max_retries=3)
    def search_jobs_real(
        self,
        query: str,
        location: str = "India",
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Search jobs using real Adzuna API."""
        country = "in"
        url = f"{self.BASE_URL}/{country}/search/1"
        
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "what": query,
            "where": location,
            "results_per_page": min(max_results, 50),
            "content-type": "application/json"
        }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                jobs = []
                for result in data.get("results", [])[:max_results]:
                    job = self.normalize_job({
                        "title": result.get("title", ""),
                        "company": result.get("company", {}).get("display_name", "Unknown"),
                        "location": result.get("location", {}).get("display_name", location),
                        "description": result.get("description", ""),
                        "excerpt": result.get("description", "")[:200],
                        "url": result.get("redirect_url", ""),
                        "posted_date": result.get("created"),
                        "required_skills": [],
                        "seniority_level": ""
                    })
                    jobs.append(job)
                
                logger.info(f"Adzuna: Found {len(jobs)} jobs for '{query}' in {location}")
                return jobs
        except Exception as e:
            logger.error(f"Adzuna API error: {e}")
            raise
    
    def search_jobs_mock(
        self,
        query: str,
        location: str = "India",
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Return mock Adzuna job data for development."""
        mock_jobs = [
            {
                "title": "Senior QA Engineer",
                "company": "Tech Solutions Pvt Ltd",
                "location": "Bangalore, India",
                "description": "Looking for experienced QA engineer with automation skills. 5+ years experience required.",
                "excerpt": "Looking for experienced QA engineer with automation skills...",
                "url": "https://www.adzuna.in/jobs/mock/1",
                "posted_date": "2025-01-15",
                "required_skills": ["selenium", "python", "pytest", "api testing"],
                "seniority_level": "senior"
            },
            {
                "title": "QA Automation Engineer",
                "company": "Startup India Inc",
                "location": "Remote, India",
                "description": "Remote QA position with focus on test automation and CI/CD integration.",
                "excerpt": "Remote QA position with focus on test automation...",
                "url": "https://www.adzuna.in/jobs/mock/2",
                "posted_date": "2025-01-18",
                "required_skills": ["selenium", "jenkins", "python", "agile"],
                "seniority_level": "mid"
            },
            {
                "title": "Quality Assurance Lead",
                "company": "Big Corp Software",
                "location": "Pune, India",
                "description": "Lead QA engineer to manage testing team and automation strategy.",
                "excerpt": "Lead QA engineer to manage testing team...",
                "url": "https://www.adzuna.in/jobs/mock/3",
                "posted_date": "2025-01-20",
                "required_skills": ["leadership", "selenium", "test strategy", "agile"],
                "seniority_level": "senior"
            }
        ]
        
        jobs = [self.normalize_job(job) for job in mock_jobs[:max_results]]
        logger.info(f"Adzuna (MOCK): Returning {len(jobs)} jobs")
        return jobs
    
    def search_jobs(
        self,
        query: str,
        location: str = "India",
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Search jobs with automatic fallback to mock mode."""
        if self.use_mock:
            return self.search_jobs_mock(query, location, max_results)
        else:
            try:
                return self.search_jobs_real(query, location, max_results)
            except Exception as e:
                logger.warning(f"Falling back to mock mode due to error: {e}")
                self.use_mock = True
                return self.search_jobs_mock(query, location, max_results)
