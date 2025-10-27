"""
RapidAPI Job Search Connector.
Integrates with various job search APIs available on RapidAPI.
"""
import httpx
from typing import List, Dict, Any, Optional
import logging
from .base import BaseConnector, retry_with_backoff
from ..core.config import settings

logger = logging.getLogger(__name__)


class RapidAPIConnector(BaseConnector):
    """RapidAPI job search connector using multiple job APIs."""
    
    RAPIDAPI_HOST = "jsearch.p.rapidapi.com"
    RAPIDAPI_BASE_URL = f"https://{RAPIDAPI_HOST}"
    
    def __init__(self, use_mock: bool = None):
        """Initialize RapidAPI connector."""
        if use_mock is None:
            use_mock = settings.MOCK_CONNECTORS or not settings.RAPIDAPI_KEY
        
        super().__init__(use_mock=use_mock)
        self.api_key = settings.RAPIDAPI_KEY
    
    @retry_with_backoff(max_retries=3)
    def search_jobs_real(
        self,
        query: str,
        location: str = "India",
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Search jobs using RapidAPI JSearch API."""
        if not self.api_key:
            logger.warning("RapidAPI key not configured, using mock data")
            return self._get_mock_jobs(max_results)
        
        url = f"{self.RAPIDAPI_BASE_URL}/search"
        
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.RAPIDAPI_HOST
        }
        
        params = {
            "query": f"{query} in {location}",
            "page": "1",
            "num_pages": "1",
            "date_posted": "all"
        }
        
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                jobs = []
                for result in data.get("data", [])[:max_results]:
                    job = self.normalize_job({
                        "title": result.get("job_title", ""),
                        "company": result.get("employer_name", "Unknown"),
                        "location": result.get("job_city", location) + ", " + result.get("job_country", "India"),
                        "description": result.get("job_description", ""),
                        "excerpt": result.get("job_highlights", {}).get("Qualifications", [""])[0][:200],
                        "url": result.get("job_apply_link", result.get("job_google_link", "")),
                        "posted_date": result.get("job_posted_at_datetime_utc"),
                        "required_skills": result.get("job_required_skills", []),
                        "seniority_level": result.get("job_employment_type", "").lower()
                    })
                    jobs.append(job)
                
                logger.info(f"RapidAPI: Found {len(jobs)} jobs for '{query}' in {location}")
                return jobs
                
        except Exception as e:
            logger.error(f"RapidAPI error: {e}")
            return self._get_mock_jobs(max_results)
    
    def search_jobs(
        self,
        query: str,
        location: str = "India",
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Search jobs (use real or mock based on configuration)."""
        if self.use_mock:
            return self._get_mock_jobs(max_results)
        
        return self.search_jobs_real(query, location, max_results)
    
    def _get_mock_jobs(self, max_results: int) -> List[Dict[str, Any]]:
        """Get mock jobs for testing."""
        mock_jobs = [
            {
                "title": "DevOps Engineer",
                "company": "Cloud Services Ltd",
                "location": "Hyderabad, India",
                "description": "Looking for experienced DevOps engineer with AWS, Docker, Kubernetes expertise.",
                "excerpt": "Looking for experienced DevOps engineer...",
                "url": "https://rapidapi.mock/jobs/1",
                "posted_date": "2025-01-20",
                "required_skills": ["aws", "docker", "kubernetes", "terraform", "jenkins"],
                "seniority_level": "senior"
            },
            {
                "title": "Data Scientist",
                "company": "AI Innovations Inc",
                "location": "Bangalore, India",
                "description": "Join our data science team. Python, ML, TensorFlow experience needed.",
                "excerpt": "Join our data science team...",
                "url": "https://rapidapi.mock/jobs/2",
                "posted_date": "2025-01-19",
                "required_skills": ["python", "machine learning", "tensorflow", "pandas", "sql"],
                "seniority_level": "mid"
            }
        ]
        
        jobs = [self.normalize_job(job) for job in mock_jobs[:max_results]]
        logger.info(f"RapidAPI (MOCK): Returning {len(jobs)} jobs")
        return jobs
