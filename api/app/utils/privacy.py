
"""
Privacy and GDPR compliance utilities.
"""
import re
import hashlib
from typing import Dict, Any


class ResumePrivacyManager:
    """Manage resume data privacy and anonymization."""
    
    @staticmethod
    def sanitize_resume_text(text: str, max_length: int = 5000) -> str:
        """
        Sanitize resume text by removing PII.
        
        Args:
            text: Raw resume text
            max_length: Maximum length to store
        
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        
        # Remove phone numbers (various formats)
        text = re.sub(r'\b\d{10}\b', '[PHONE]', text)
        text = re.sub(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '[PHONE]', text)
        text = re.sub(r'\+\d{1,3}[-.\s]?\d{9,10}\b', '[PHONE]', text)
        
        # Remove addresses (basic pattern)
        text = re.sub(r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln)\b', '[ADDRESS]', text)
        
        # Truncate to max length
        if len(text) > max_length:
            text = text[:max_length] + "... [TRUNCATED]"
        
        return text
    
    @staticmethod
    def anonymize_job_data(job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize job data before storage.
        
        Args:
            job: Job dictionary
        
        Returns:
            Anonymized job dictionary
        """
        anonymized = job.copy()
        
        # Remove raw data if anonymization is enabled
        if "raw" in anonymized:
            anonymized.pop("raw")
        
        # Hash the URL to prevent tracking
        if "url" in anonymized and anonymized["url"]:
            url_hash = hashlib.sha256(anonymized["url"].encode()).hexdigest()[:16]
            anonymized["url_hash"] = url_hash
        
        return anonymized
    
    @staticmethod
    def should_store_raw(settings) -> bool:
        """Check if raw data should be stored based on settings."""
        return getattr(settings, "STORE_RESUME_RAW", False)


privacy_manager = ResumePrivacyManager()
