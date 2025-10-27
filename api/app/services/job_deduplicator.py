"""
Job deduplication and caching service.
Prevents duplicate jobs from different sources and implements caching.
"""
import hashlib
import json
from typing import List, Dict, Any, Set
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class JobDeduplicator:
    """Deduplicate jobs from multiple sources."""
    
    def __init__(self, cache_ttl_hours: int = 24):
        """
        Initialize job deduplicator.
        
        Args:
            cache_ttl_hours: Time to live for cached job hashes in hours
        """
        self.cache_ttl_hours = cache_ttl_hours
        self.job_hashes: Set[str] = set()
        self.job_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
    
    def generate_job_hash(self, job_data: Dict[str, Any]) -> str:
        """
        Generate unique hash for a job.
        
        Uses title, company, and location for uniqueness.
        """
        title = str(job_data.get("title", "")).lower().strip()
        company = str(job_data.get("company", "")).lower().strip()
        location = str(job_data.get("location", "")).lower().strip()
        
        key_string = f"{title}|{company}|{location}"
        
        key_string = key_string.encode('utf-8', errors='ignore')
        return hashlib.sha256(key_string).hexdigest()[:16]
    
    def is_duplicate(self, job_data: Dict[str, Any]) -> bool:
        """Check if job is a duplicate."""
        job_hash = self.generate_job_hash(job_data)
        return job_hash in self.job_hashes
    
    def add_job(self, job_data: Dict[str, Any]) -> str:
        """
        Add job to deduplication cache.
        
        Returns:
            Job hash
        """
        job_hash = self.generate_job_hash(job_data)
        self.job_hashes.add(job_hash)
        self.job_cache[job_hash] = job_data
        self.cache_timestamps[job_hash] = datetime.now()
        return job_hash
    
    def deduplicate_jobs(
        self,
        jobs: List[Dict[str, Any]],
        keep_source_priority: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Remove duplicate jobs from list.
        
        Args:
            jobs: List of job dictionaries
            keep_source_priority: List of sources in priority order (highest first)
        
        Returns:
            List of unique jobs
        """
        if not jobs:
            return []
        
        unique_jobs = []
        seen_hashes = set()
        hash_to_job = {}
        
        for job in jobs:
            job_hash = self.generate_job_hash(job)
            
            if job_hash not in seen_hashes:
                seen_hashes.add(job_hash)
                hash_to_job[job_hash] = job
                unique_jobs.append(job)
            elif keep_source_priority:
                existing_job = hash_to_job.get(job_hash)
                if existing_job:
                    existing_source = existing_job.get("source", "")
                    new_source = job.get("source", "")
                    
                    try:
                        existing_priority = keep_source_priority.index(existing_source) if existing_source in keep_source_priority else 999
                        new_priority = keep_source_priority.index(new_source) if new_source in keep_source_priority else 999
                        
                        if new_priority < existing_priority:
                            for i, unique_job in enumerate(unique_jobs):
                                if self.generate_job_hash(unique_job) == job_hash:
                                    unique_jobs[i] = job
                                    hash_to_job[job_hash] = job
                                    break
                    except (ValueError, IndexError):
                        pass
        
        logger.info(f"Deduplicated {len(jobs)} jobs to {len(unique_jobs)} unique jobs")
        
        return unique_jobs
    
    def clean_cache(self):
        """Remove expired entries from cache."""
        now = datetime.now()
        ttl = timedelta(hours=self.cache_ttl_hours)
        
        expired_hashes = [
            job_hash for job_hash, timestamp in self.cache_timestamps.items()
            if now - timestamp > ttl
        ]
        
        for job_hash in expired_hashes:
            self.job_hashes.discard(job_hash)
            self.job_cache.pop(job_hash, None)
            self.cache_timestamps.pop(job_hash, None)
        
        if expired_hashes:
            logger.info(f"Cleaned {len(expired_hashes)} expired job entries from cache")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_jobs": len(self.job_hashes),
            "cache_size_mb": len(json.dumps(self.job_cache)) / (1024 * 1024),
            "oldest_entry": min(self.cache_timestamps.values()) if self.cache_timestamps else None,
            "newest_entry": max(self.cache_timestamps.values()) if self.cache_timestamps else None
        }


job_deduplicator = JobDeduplicator()
