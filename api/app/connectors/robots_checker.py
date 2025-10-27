"""
Robots.txt checker utility for ethical web scraping.
"""
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class RobotsChecker:
    """Check robots.txt compliance before scraping."""
    
    def __init__(self):
        """Initialize robots.txt parsers cache."""
        self.parsers = {}
    
    def can_fetch(self, url: str, user_agent: str = "*") -> bool:
        """
        Check if URL can be fetched according to robots.txt.
        
        Args:
            url: URL to check
            user_agent: User agent string
        
        Returns:
            True if allowed, False otherwise
        """
        try:
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            if robots_url not in self.parsers:
                parser = RobotFileParser()
                parser.set_url(robots_url)
                try:
                    parser.read()
                    self.parsers[robots_url] = parser
                except Exception as e:
                    logger.warning(f"Could not read robots.txt from {robots_url}: {e}")
                    return True
            
            parser = self.parsers[robots_url]
            allowed = parser.can_fetch(user_agent, url)
            
            if not allowed:
                logger.warning(f"Robots.txt prohibits scraping {url}")
            
            return allowed
        except Exception as e:
            logger.error(f"Error checking robots.txt: {e}")
            return True


robots_checker = RobotsChecker()
