"""
Advanced RSS Feed Aggregator for job boards.
Aggregates job listings from multiple RSS feeds with deduplication.
"""
import httpx
import feedparser
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib
import logging
from .base import BaseConnector, retry_with_backoff

logger = logging.getLogger(__name__)


class RSSAggregator(BaseConnector):
    """Aggregate jobs from multiple RSS feeds."""
    
    RSS_FEEDS = {
        "indeed_india": {
            "url": "https://www.indeed.co.in/rss",
            "params_template": {"q": "{query}", "l": "{location}"}
        },
        "monster_india": {
            "url": "https://www.monsterindia.com/srp/results.html",
            "rss_suffix": "?format=rss",
            "params_template": {"query": "{query}", "where": "{location}"}
        },
        "timesjobs": {
            "url": "https://www.timesjobs.com/candidate/rss-feed-jobs.html",
            "params_template": {"searchType": "personalizedSearch", "txtKeywords": "{query}"}
        }
    }
    
    def __init__(self, use_mock: bool = False):
        """Initialize RSS aggregator."""
        super().__init__(use_mock=use_mock)
        self.seen_job_hashes = set()
    
    def generate_job_hash(self, job_data: Dict[str, Any]) -> str:
        """Generate unique hash for job deduplication."""
        key_string = f"{job_data.get('title', '')}{job_data.get('company', '')}{job_data.get('location', '')}"
        return hashlib.md5(key_string.lower().encode()).hexdigest()
    
    @retry_with_backoff(max_retries=3)
    def fetch_rss_feed(self, feed_url: str, params: Dict[str, str]) -> List[Dict[str, Any]]:
        """Fetch and parse RSS feed."""
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(feed_url, params=params, follow_redirects=True)
                response.raise_for_status()
                
                feed = feedparser.parse(response.content)
                jobs = []
                
                for entry in feed.entries:
                    try:
                        job = self.parse_rss_entry(entry)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        logger.warning(f"Failed to parse RSS entry: {e}")
                        continue
                
                return jobs
        except Exception as e:
            logger.error(f"Failed to fetch RSS feed {feed_url}: {e}")
            return []
    
    def parse_rss_entry(self, entry) -> Optional[Dict[str, Any]]:
        """Parse individual RSS entry into job data."""
        title = entry.get("title", "")
        link = entry.get("link", "")
        description = entry.get("summary", entry.get("description", ""))
        pub_date = entry.get("published", entry.get("pubDate", None))
        
        if not title or not link:
            return None
        
        parts = title.split(" - ")
        job_title = parts[0].strip() if len(parts) > 0 else title
        company = parts[1].strip() if len(parts) > 1 else "Unknown"
        location = parts[2].strip() if len(parts) > 2 else "India"
        
        job_data = {
            "title": job_title,
            "company": company,
            "location": location,
            "description": description,
            "excerpt": description[:200] if description else "",
            "url": link,
            "posted_date": pub_date,
            "required_skills": [],
            "seniority_level": ""
        }
        
        return job_data
    
    def deduplicate_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate jobs based on hash."""
        unique_jobs = []
        
        for job in jobs:
            job_hash = self.generate_job_hash(job)
            if job_hash not in self.seen_job_hashes:
                self.seen_job_hashes.add(job_hash)
                unique_jobs.append(job)
        
        return unique_jobs
    
    @retry_with_backoff(max_retries=3)
    def search_jobs_real(
        self,
        query: str,
        location: str = "India",
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Search jobs from multiple RSS feeds."""
        all_jobs = []
        
        for feed_name, feed_config in self.RSS_FEEDS.items():
            try:
                feed_url = feed_config["url"]
                params_template = feed_config.get("params_template", {})
                
                params = {}
                for key, value in params_template.items():
                    params[key] = value.format(query=query, location=location)
                
                if "rss_suffix" in feed_config:
                    feed_url += feed_config["rss_suffix"]
                
                jobs = self.fetch_rss_feed(feed_url, params)
                
                for job in jobs:
                    job["source"] = feed_name
                    all_jobs.append(self.normalize_job(job))
                
                logger.info(f"RSS {feed_name}: Fetched {len(jobs)} jobs")
                
            except Exception as e:
                logger.error(f"Error fetching from {feed_name}: {e}")
                continue
        
        unique_jobs = self.deduplicate_jobs(all_jobs)
        
        logger.info(f"RSS Aggregator: Found {len(unique_jobs)} unique jobs from {len(all_jobs)} total")
        
        return unique_jobs[:max_results]
    
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
        """Get mock RSS feed jobs for testing."""
        mock_jobs = [
            {
                "title": "Full Stack Developer",
                "company": "Tech Startup India",
                "location": "Bangalore, Karnataka",
                "description": "Join our growing team as a full stack developer. React, Node.js, MongoDB experience required.",
                "excerpt": "Join our growing team...",
                "url": "https://rss.example.com/jobs/1",
                "posted_date": "2025-01-22",
                "required_skills": ["react", "nodejs", "mongodb", "javascript"],
                "seniority_level": "mid"
            },
            {
                "title": "Python Backend Developer",
                "company": "E-commerce Giant",
                "location": "Remote, India",
                "description": "Build scalable backend systems with Python, Django, PostgreSQL. Remote-first company.",
                "excerpt": "Build scalable backend systems...",
                "url": "https://rss.example.com/jobs/2",
                "posted_date": "2025-01-21",
                "required_skills": ["python", "django", "postgresql", "rest api"],
                "seniority_level": "senior"
            }
        ]
        
        jobs = [self.normalize_job(job) for job in mock_jobs[:max_results]]
        logger.info(f"RSS Aggregator (MOCK): Returning {len(jobs)} jobs")
        return jobs
