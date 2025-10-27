
"""
Robots.txt checker for ethical scraping.
"""
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, urljoin
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class RobotsChecker:
    """Check robots.txt compliance."""
    
    def __init__(self, user_agent: str = "JobFinderBot/1.0"):
        self.user_agent = user_agent
        self.parsers: Dict[str, RobotFileParser] = {}
    
    def can_fetch(self, url: str) -> bool:
        """Check if URL can be fetched according to robots.txt."""
        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            if base_url not in self.parsers:
                parser = RobotFileParser()
                robots_url = urljoin(base_url, "/robots.txt")
                parser.set_url(robots_url)
                try:
                    parser.read()
                    self.parsers[base_url] = parser
                except Exception as e:
                    logger.warning(f"Could not read robots.txt for {base_url}: {e}")
                    # If can't read robots.txt, assume allowed
                    return True
            
            return self.parsers[base_url].can_fetch(self.user_agent, url)
        except Exception as e:
            logger.error(f"Error checking robots.txt: {e}")
            return False
