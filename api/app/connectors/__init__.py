"""Job board connectors."""
from .base import BaseConnector
from .adzuna import AdzunaConnector
from .indeed import IndeedConnector
from .jooble import JoobleConnector
from .linkedin import LinkedInConnector
from .naukri import NaukriConnector
from .rss_aggregator import RSSAggregator
from .rapidapi_connector import RapidAPIConnector

__all__ = [
    "BaseConnector",
    "AdzunaConnector",
    "IndeedConnector",
    "JoobleConnector",
    "LinkedInConnector",
    "NaukriConnector",
    "RSSAggregator",
    "RapidAPIConnector"
]
