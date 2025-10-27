
"""
Abstract base class for job scrapers.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, AsyncGenerator
import hashlib
import logging

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for all job scrapers."""
    
    def __init__(self, name: str):
        self.name = name
        self.seen_hashes = set()
    
    def generate_job_hash(self, job: Dict[str, Any]) -> str:
        """Generate unique hash for job deduplication."""
        title = job.get("title", "").lower().strip()
        company = job.get("company", "").lower().strip()
        location = job.get("location", "").lower().strip()
        url = job.get("url", "").lower().strip()
        
        key_string = f"{title}|{company}|{location}|{url}"
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]
    
    def is_duplicate(self, job: Dict[str, Any]) -> bool:
        """Check if job is duplicate."""
        job_hash = self.generate_job_hash(job)
        if job_hash in self.seen_hashes:
            return True
        self.seen_hashes.add(job_hash)
        return False
    
    def normalize_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize job data to standard format."""
        return {
            "source": job.get("source", self.name),
            "title": job.get("title", "").strip(),
            "company": job.get("company", "Unknown").strip(),
            "location": job.get("location", "").strip(),
            "description": job.get("description", "").strip(),
            "excerpt": job.get("excerpt", job.get("description", "")[:200]).strip(),
            "url": job.get("url", "").strip(),
            "posted_at": job.get("posted_at"),
            "required_skills": job.get("required_skills", []),
            "seniority_level": job.get("seniority_level", ""),
            "raw": job.get("raw", {})
        }
    
    @abstractmethod
    async def scrape_jobs(
        self,
        query: str,
        location: str = "India",
        max_results: int = 20
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Scrape jobs from source.
        
        Yields normalized job dictionaries.
        """
        pass
    
    async def collect_jobs(
        self,
        query: str,
        location: str = "India",
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Collect jobs into a list."""
        jobs = []
        async for job in self.scrape_jobs(query, location, max_results):
            if not self.is_duplicate(job):
                jobs.append(job)
                if len(jobs) >= max_results:
                    break
        return jobs
