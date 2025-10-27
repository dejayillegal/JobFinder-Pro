
"""
TF-IDF based job matching for resume-job similarity.
"""
from typing import Dict, Any, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

logger = logging.getLogger(__name__)


class TFIDFJobMatcher:
    """Job matcher using TF-IDF and cosine similarity."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1
        )
    
    def calculate_match_score(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive match score between resume and job.
        
        Args:
            resume_data: Parsed resume data
            job_data: Job listing data
        
        Returns:
            Dictionary with match scores and factors
        """
        from ..core.config import settings
        
        # Calculate individual component scores
        skills_score = self._calculate_skills_match(resume_data, job_data)
        experience_score = self._calculate_experience_match(resume_data, job_data)
        location_score = self._calculate_location_match(resume_data, job_data)
        title_score = self._calculate_title_match(resume_data, job_data)
        
        # Weighted total score
        total_score = (
            skills_score * settings.SKILLS_WEIGHT +
            experience_score * settings.EXPERIENCE_WEIGHT +
            location_score * settings.LOCATION_WEIGHT +
            title_score * settings.TITLE_WEIGHT
        )
        
        # Normalize to 0-100
        total_score = min(100, int(total_score * 100))
        
        # Determine top matching factors
        factors = {
            "Skills Match": int(skills_score * 100),
            "Experience Level": int(experience_score * 100),
            "Location": int(location_score * 100),
            "Job Title Relevance": int(title_score * 100)
        }
        
        top_factors = sorted(factors.items(), key=lambda x: x[1], reverse=True)[:3]
        top_factors = [f"{name}: {score}%" for name, score in top_factors]
        
        return {
            "match_score": total_score,
            "skills_score": int(skills_score * 100),
            "seniority_score": int(experience_score * 100),
            "location_score": int(location_score * 100),
            "title_score": int(title_score * 100),
            "top_factors": top_factors
        }
    
    def _calculate_skills_match(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> float:
        """Calculate skills match using set intersection and TF-IDF."""
        resume_skills = set([s.lower() for s in resume_data.get("skills", [])])
        job_skills = set([s.lower() for s in job_data.get("required_skills", [])])
        
        if not resume_skills or not job_skills:
            # Fall back to text similarity
            return self._text_similarity(
                " ".join(resume_data.get("skills", [])),
                job_data.get("description", "")
            )
        
        # Calculate Jaccard similarity
        intersection = len(resume_skills.intersection(job_skills))
        union = len(resume_skills.union(job_skills))
        
        if union == 0:
            return 0.0
        
        jaccard = intersection / union
        
        # Bonus for having all required skills
        if job_skills.issubset(resume_skills):
            jaccard = min(1.0, jaccard * 1.2)
        
        return jaccard
    
    def _calculate_experience_match(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> float:
        """Match experience level/seniority."""
        resume_exp = resume_data.get("years_experience", 0)
        job_seniority = job_data.get("seniority_level", "mid").lower()
        
        # Define experience ranges for seniority levels
        seniority_ranges = {
            "junior": (0, 2),
            "entry": (0, 2),
            "mid": (2, 5),
            "intermediate": (2, 5),
            "senior": (5, 100),
            "lead": (7, 100),
            "principal": (10, 100),
            "staff": (10, 100)
        }
        
        exp_range = seniority_ranges.get(job_seniority, (0, 100))
        
        if exp_range[0] <= resume_exp <= exp_range[1]:
            return 1.0
        elif resume_exp < exp_range[0]:
            # Under-qualified
            gap = exp_range[0] - resume_exp
            return max(0.0, 1.0 - (gap * 0.2))
        else:
            # Over-qualified
            gap = resume_exp - exp_range[1]
            return max(0.5, 1.0 - (gap * 0.1))
    
    def _calculate_location_match(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> float:
        """Match location preferences."""
        preferred_locations = [
            loc.lower() for loc in resume_data.get("locations_preferred", [])
        ]
        job_location = job_data.get("location", "").lower()
        
        if not preferred_locations:
            return 0.7  # Neutral score if no preference
        
        # Check for remote
        if "remote" in job_location:
            return 1.0
        
        # Check if job location matches any preferred location
        for pref_loc in preferred_locations:
            if pref_loc in job_location or job_location in pref_loc:
                return 1.0
        
        return 0.3  # Low score if location doesn't match
    
    def _calculate_title_match(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> float:
        """Match job title with current role."""
        current_role = resume_data.get("current_role", "").lower()
        job_title = job_data.get("title", "").lower()
        
        if not current_role or not job_title:
            return 0.5
        
        return self._text_similarity(current_role, job_title)
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts using TF-IDF."""
        if not text1 or not text2:
            return 0.0
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating text similarity: {e}")
            return 0.0


# Singleton instance
tfidf_matcher = TFIDFJobMatcher()
