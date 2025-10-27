
"""
RSS/Atom feed job scraper with async support.
"""
from typing import Dict, Any, List, AsyncGenerator
import httpx
import feedparser
from datetime import datetime
from dateutil import parser as date_parser
import re
import logging
from bs4 import BeautifulSoup

from .base import BaseScraper
from ..utils.rate_limiter import AsyncRateLimiter

logger = logging.getLogger(__name__)


class RSSJobScraper(BaseScraper):
    """Scrape jobs from RSS/Atom feeds."""
    
    DEFAULT_FEEDS = {
        "indeed_india": "https://www.indeed.co.in/rss?q={query}&l={location}",
        "monster_india": "https://www.monsterindia.com/srp/results.html?format=rss&query={query}&where={location}",
        "timesjobs": "https://www.timesjobs.com/candidate/rss-feed-jobs.html?searchType=personalizedSearch&txtKeywords={query}",
        "linkedin_rss": "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={query}&location={location}",
        "naukri_rss": "https://www.naukri.com/jobapi/v3/search?noOfResults=20&keywords={query}&location={location}"
    }
    
    def __init__(self, feed_urls: Dict[str, str] = None, rate_limit: float = 2.0):
        super().__init__("RSS_Aggregator")
        self.feed_urls = feed_urls or self.DEFAULT_FEEDS
        self.rate_limiter = AsyncRateLimiter(rate_limit)
        self.cache = {}
    
    def clean_html(self, html_text: str) -> str:
        """Remove HTML tags and clean text."""
        if not html_text:
            return ""
        soup = BeautifulSoup(html_text, "html.parser")
        text = soup.get_text()
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from job description."""
        skills_keywords = [
            "python", "javascript", "java", "react", "node.js", "sql", "aws",
            "docker", "kubernetes", "mongodb", "postgresql", "typescript",
            "angular", "vue.js", "django", "flask", "fastapi", "machine learning",
            "data science", "devops", "ci/cd", "git", "agile", "scrum",
            "golang", "rust", "c++", "c#", "ruby", "php", "spring boot",
            "microservices", "rest api", "graphql", "redis", "elasticsearch"
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in skills_keywords:
            if skill in text_lower:
                found_skills.append(skill)
        
        return list(set(found_skills))
    
    def infer_seniority(self, title: str, description: str) -> str:
        """Infer seniority level from title and description."""
        text = f"{title} {description}".lower()
        
        if any(word in text for word in ["senior", "lead", "principal", "staff", "architect"]):
            return "senior"
        elif any(word in text for word in ["junior", "entry", "graduate", "intern", "trainee"]):
            return "junior"
        elif any(word in text for word in ["mid", "intermediate"]):
            return "mid"
        else:
            return "mid"
    
    async def scrape_jobs(
        self,
        query: str,
        location: str = "India",
        max_results: int = 20
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Scrape jobs from RSS feeds."""
        total_yielded = 0
        
        for feed_name, feed_url_template in self.feed_urls.items():
            if total_yielded >= max_results:
                break
            
            try:
                await self.rate_limiter.acquire()
                
                feed_url = feed_url_template.format(
                    query=query.replace(" ", "+"),
                    location=location.replace(" ", "+")
                )
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(feed_url, follow_redirects=True)
                    response.raise_for_status()
                    
                    feed = feedparser.parse(response.text)
                    
                    for entry in feed.entries:
                        if total_yielded >= max_results:
                            break
                        
                        title = entry.get("title", "Unknown Title")
                        link = entry.get("link", "")
                        description = entry.get("summary", entry.get("description", ""))
                        published = entry.get("published", entry.get("updated", ""))
                        
                        clean_desc = self.clean_html(description)
                        skills = self.extract_skills_from_text(clean_desc)
                        
                        # Extract company
                        company = "Unknown Company"
                        company_match = re.search(r'at\s+([A-Z][a-zA-Z\s&.]+?)(?:\s+[-|]|\s+in\s+|$)', title)
                        if company_match:
                            company = company_match.group(1).strip()
                        
                        # Extract location
                        job_location = location
                        location_match = re.search(r'in\s+([A-Z][a-zA-Z\s,]+?)(?:\s+[-|]|$)', title)
                        if location_match:
                            job_location = location_match.group(1).strip()
                        
                        # Parse date
                        published_at = None
                        if published:
                            try:
                                published_at = date_parser.parse(published)
                            except Exception:
                                pass
                        
                        job = {
                            "source": feed_name,
                            "title": title,
                            "company": company,
                            "location": job_location,
                            "description": clean_desc[:1000],
                            "excerpt": clean_desc[:200] if clean_desc else title,
                            "url": link,
                            "required_skills": skills,
                            "seniority_level": self.infer_seniority(title, clean_desc),
                            "posted_at": published_at,
                            "raw": {"feed_entry": dict(entry)}
                        }
                        
                        normalized_job = self.normalize_job(job)
                        yield normalized_job
                        total_yielded += 1
                
                logger.info(f"RSS {feed_name}: Fetched jobs successfully")
                
            except Exception as e:
                logger.error(f"Error fetching from {feed_name}: {e}")
                continue
