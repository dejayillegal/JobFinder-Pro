
"""
Indeed India connector using RSS feeds (legal alternative to scraping).
"""
from typing import List, Dict, Any
import httpx
import logging
from datetime import datetime
from xml.etree import ElementTree as ET
from .base import BaseConnector, retry_with_backoff

logger = logging.getLogger(__name__)


class IndeedConnector(BaseConnector):
    """Indeed India job search connector using RSS feeds."""
    
    RSS_BASE_URL = "https://www.indeed.co.in/rss"
    
    def __init__(self, use_mock: bool = None):
        """Initialize Indeed connector."""
        import os
        from ..core.config import settings
        
        # Check for API key in environment (optional)
        self.api_key = os.getenv("INDEED_API_KEY", "")
        
        if use_mock is None:
            use_mock = settings.MOCK_CONNECTORS or not self.api_key
        super().__init__(use_mock=use_mock)
    
    @retry_with_backoff(max_retries=3)
    def search_jobs_real(
        self,
        query: str,
        location: str = "India",
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Search jobs using Indeed RSS feeds."""
        params = {
            "q": query,
            "l": location,
            "limit": min(max_results, 50)
        }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(self.RSS_BASE_URL, params=params)
                response.raise_for_status()
                
                # Parse RSS XML
                root = ET.fromstring(response.content)
                jobs = []
                
                for item in root.findall(".//item")[:max_results]:
                    title = item.find("title").text if item.find("title") is not None else ""
                    link = item.find("link").text if item.find("link") is not None else ""
                    description = item.find("description").text if item.find("description") is not None else ""
                    pub_date = item.find("pubDate").text if item.find("pubDate") is not None else None
                    
                    # Extract company and location from title (format: "Job Title - Company - Location")
                    parts = title.split(" - ")
                    job_title = parts[0] if len(parts) > 0 else title
                    company = parts[1] if len(parts) > 1 else "Unknown"
                    job_location = parts[2] if len(parts) > 2 else location
                    
                    job = self.normalize_job({
                        "title": job_title,
                        "company": company,
                        "location": job_location,
                        "description": description,
                        "excerpt": description[:200] if description else "",
                        "url": link,
                        "posted_date": pub_date,
                        "required_skills": [],
                        "seniority_level": ""
                    })
                    jobs.append(job)
                
                logger.info(f"Indeed RSS: Found {len(jobs)} jobs for '{query}' in {location}")
                return jobs
        except Exception as e:
            logger.error(f"Indeed RSS error: {e}")
            raise
    
    def search_jobs_mock(
        self,
        query: str,
        location: str = "India",
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Return mock Indeed job data for development."""
        mock_jobs = [
            {
                "title": f"{query} - Software Test Engineer",
                "company": "Indeed Tech Labs",
                "location": "Bangalore, Karnataka",
                "description": f"We are seeking a talented {query} to join our QA team. Experience with manual and automated testing required.",
                "excerpt": f"Seeking talented {query}...",
                "url": "https://www.indeed.co.in/jobs/mock/1",
                "posted_date": "2025-01-22",
                "required_skills": ["manual testing", "selenium", "java", "sql"],
                "seniority_level": "mid"
            },
            {
                "title": f"{query} - QA Analyst",
                "company": "Mobile First Company",
                "location": "Hyderabad, Telangana",
                "description": f"{query} specialist needed. Experience with testing frameworks.",
                "excerpt": f"{query} specialist needed...",
                "url": "https://www.indeed.co.in/jobs/mock/2",
                "posted_date": "2025-01-21",
                "required_skills": ["mobile testing", "appium", "ios", "android"],
                "seniority_level": "mid"
            }
        ]
        
        jobs = [self.normalize_job(job) for job in mock_jobs[:max_results]]
        logger.info(f"Indeed (MOCK): Returning {len(jobs)} jobs")
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
