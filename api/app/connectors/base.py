"""
Base connector class with retry logic and circuit breaker pattern.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator for retry with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Max retries reached for {func.__name__}: {e}")
                        raise
                    
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay}s: {e}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator


class BaseConnector(ABC):
    """Base class for job board connectors."""
    
    def __init__(self, use_mock: bool = True):
        """
        Initialize connector.
        
        Args:
            use_mock: If True, use mock data instead of real API calls
        """
        self.use_mock = use_mock
        self.name = self.__class__.__name__.replace("Connector", "")
    
    @abstractmethod
    def search_jobs(
        self,
        query: str,
        location: str = "India",
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for jobs.
        
        Args:
            query: Search query (e.g., "QA Engineer", "Python Developer")
            location: Location filter
            max_results: Maximum number of results to return
        
        Returns:
            List of job dictionaries with standardized fields:
            - title
            - company
            - location
            - description
            - url
            - posted_date
            - required_skills
            - seniority_level
        """
        pass
    
    def normalize_job(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize job data to standard format.
        
        Args:
            raw_job: Raw job data from API/scraper
        
        Returns:
            Normalized job dictionary
        """
        return {
            "title": raw_job.get("title", ""),
            "company": raw_job.get("company", ""),
            "location": raw_job.get("location", ""),
            "description": raw_job.get("description", ""),
            "excerpt": raw_job.get("excerpt", "")[:200] if raw_job.get("excerpt") else "",
            "url": raw_job.get("url", ""),
            "posted_date": raw_job.get("posted_date"),
            "required_skills": raw_job.get("required_skills", []),
            "seniority_level": raw_job.get("seniority_level", ""),
            "source": self.name
        }
