
"""
Job scrapers package with pluggable architecture.
"""
from .base import BaseScraper
from .rss_scraper import RSSJobScraper
from .playwright_scraper import PlaywrightJobScraper

__all__ = ["BaseScraper", "RSSJobScraper", "PlaywrightJobScraper"]
