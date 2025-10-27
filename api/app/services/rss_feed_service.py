
"""
RSS/Atom feed aggregation for job listings.
"""
from typing import List, Dict, Any, Optional
import feedparser
import httpx
from datetime import datetime, timedelta
import hashlib
import logging
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class RSSFeedService:
    """Service for aggregating jobs from RSS/Atom feeds."""
    
    def __init__(self, cache_ttl: int = 3600):
        self.cache_ttl = cache_ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
    
    def clean_html(self, html_text: str) -> str:
        """Remove HTML tags and clean text."""
        if not html_text:
            return ""
        soup = BeautifulSoup(html_text, "html.parser")
        text = soup.get_text()
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract potential skills from job description."""
        skills_keywords = [
            "python", "javascript", "java", "react", "node.js", "sql", "aws",
            "docker", "kubernetes", "mongodb", "postgresql", "typescript",
            "angular", "vue.js", "django", "flask", "fastapi", "machine learning",
            "data science", "devops", "ci/cd", "git", "agile", "scrum"
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in skills_keywords:
            if skill in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    async def fetch_feed(self, feed_url: str, source_name: str) -> List[Dict[str, Any]]:
        """
        Fetch and parse RSS/Atom feed.
        
        Args:
            feed_url: URL of the RSS feed
            source_name: Name of the job source
        
        Returns:
            List of normalized job dictionaries
        """
        # Check cache
        cache_key = hashlib.md5(feed_url.encode()).hexdigest()
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if datetime.now() - cached_data["timestamp"] < timedelta(seconds=self.cache_ttl):
                logger.info(f"Returning cached data for {feed_url}")
                return cached_data["jobs"]
        
        jobs = []
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(feed_url)
                response.raise_for_status()
                
                feed = feedparser.parse(response.text)
                
                for entry in feed.entries:
                    # Extract job data
                    title = entry.get("title", "Unknown Title")
                    link = entry.get("link", "")
                    description = entry.get("summary", entry.get("description", ""))
                    published = entry.get("published", entry.get("updated", ""))
                    
                    # Clean description
                    clean_desc = self.clean_html(description)
                    
                    # Extract skills from description
                    skills = self.extract_skills(clean_desc)
                    
                    # Try to extract company from description or title
                    company = "Unknown Company"
                    company_match = re.search(r'at\s+([A-Z][a-zA-Z\s&]+?)(?:\s+[-|]|\s+in\s+|$)', title)
                    if company_match:
                        company = company_match.group(1).strip()
                    
                    # Extract location
                    location = "Remote"
                    location_match = re.search(r'in\s+([A-Z][a-zA-Z\s,]+?)(?:\s+[-|]|$)', title)
                    if location_match:
                        location = location_match.group(1).strip()
                    
                    # Parse published date
                    published_at = None
                    if published:
                        try:
                            from dateutil import parser as date_parser
                            published_at = date_parser.parse(published)
                        except Exception:
                            pass
                    
                    job = {
                        "source": source_name,
                        "title": title,
                        "company": company,
                        "location": location,
                        "description": clean_desc[:500],  # First 500 chars
                        "excerpt": clean_desc[:200] if clean_desc else title,
                        "url": link,
                        "required_skills": skills,
                        "seniority_level": self._infer_seniority(title, clean_desc),
                        "published_at": published_at
                    }
                    
                    jobs.append(job)
                
                logger.info(f"Fetched {len(jobs)} jobs from {feed_url}")
                
                # Update cache
                self.cache[cache_key] = {
                    "jobs": jobs,
                    "timestamp": datetime.now()
                }
                
        except Exception as e:
            logger.error(f"Error fetching feed {feed_url}: {e}")
        
        return jobs
    
    def _infer_seniority(self, title: str, description: str) -> str:
        """Infer seniority level from title and description."""
        text = f"{title} {description}".lower()
        
        if any(word in text for word in ["senior", "lead", "principal", "staff"]):
            return "senior"
        elif any(word in text for word in ["junior", "entry", "graduate", "intern"]):
            return "junior"
        elif any(word in text for word in ["mid", "intermediate"]):
            return "mid"
        else:
            return "mid"  # Default


# Singleton instance
rss_feed_service = RSSFeedService()
