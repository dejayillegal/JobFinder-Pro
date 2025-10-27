
"""
Enhanced job deduplication using multiple strategies.
"""
from typing import List, Dict, Any, Set
import hashlib
from difflib import SequenceMatcher
import re


class EnhancedJobDeduplicator:
    """Advanced job deduplication with fuzzy matching."""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        if not text:
            return ""
        # Convert to lowercase, remove extra spaces and special chars
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def generate_hash(self, title: str, company: str, location: str = "") -> str:
        """Generate hash for exact duplicate detection."""
        normalized = f"{self.normalize_text(title)}|{self.normalize_text(company)}|{self.normalize_text(location)}"
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        norm1 = self.normalize_text(text1)
        norm2 = self.normalize_text(text2)
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def is_duplicate(self, job1: Dict[str, Any], job2: Dict[str, Any]) -> bool:
        """Check if two jobs are duplicates using multiple criteria."""
        # Check exact hash match
        hash1 = self.generate_hash(
            job1.get("title", ""),
            job1.get("company", ""),
            job1.get("location", "")
        )
        hash2 = self.generate_hash(
            job2.get("title", ""),
            job2.get("company", ""),
            job2.get("location", "")
        )
        
        if hash1 == hash2:
            return True
        
        # Check URL match
        url1 = job1.get("url", "")
        url2 = job2.get("url", "")
        if url1 and url2 and url1 == url2:
            return True
        
        # Fuzzy matching on title and company
        title_similarity = self.calculate_similarity(
            job1.get("title", ""),
            job2.get("title", "")
        )
        company_similarity = self.calculate_similarity(
            job1.get("company", ""),
            job2.get("company", "")
        )
        
        # If both title and company are very similar, it's likely a duplicate
        if title_similarity >= self.similarity_threshold and company_similarity >= 0.9:
            return True
        
        return False
    
    def deduplicate_jobs(
        self,
        jobs: List[Dict[str, Any]],
        keep_source_priority: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Remove duplicate jobs, keeping highest priority source.
        
        Args:
            jobs: List of job dictionaries
            keep_source_priority: List of source names in priority order
        
        Returns:
            Deduplicated list of jobs
        """
        if not jobs:
            return []
        
        unique_jobs = []
        seen_hashes: Set[str] = set()
        
        # Sort by source priority if provided
        if keep_source_priority:
            source_priority_map = {src: idx for idx, src in enumerate(keep_source_priority)}
            jobs = sorted(
                jobs,
                key=lambda j: source_priority_map.get(j.get("source", ""), 999)
            )
        
        for job in jobs:
            # Generate hash
            job_hash = self.generate_hash(
                job.get("title", ""),
                job.get("company", ""),
                job.get("location", "")
            )
            
            # Check if we've seen this hash
            if job_hash in seen_hashes:
                continue
            
            # Check for fuzzy duplicates
            is_dup = False
            for existing_job in unique_jobs:
                if self.is_duplicate(job, existing_job):
                    is_dup = True
                    break
            
            if not is_dup:
                unique_jobs.append(job)
                seen_hashes.add(job_hash)
        
        return unique_jobs


# Singleton instance
enhanced_deduplicator = EnhancedJobDeduplicator()
