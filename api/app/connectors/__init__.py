"""Job board connectors."""
from .base import BaseConnector
from .adzuna import AdzunaConnector
from .indeed import IndeedConnector
from .jooble import JoobleConnector
from .linkedin import LinkedInConnector
from .naukri import NaukriConnector

__all__ = [
    "BaseConnector",
    "AdzunaConnector",
    "IndeedConnector",
    "JoobleConnector",
    "LinkedInConnector",
    "NaukriConnector"
]
