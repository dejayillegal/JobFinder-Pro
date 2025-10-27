"""
Job matching engine with explainable scoring.
Scores based on: skills overlap (60%), seniority match (25%), location match (15%).
"""
from typing import Dict, List, Any, Tuple
import logging
from fuzzywuzzy import fuzz

logger = logging.getLogger(__name__)


class JobMatcher:
    """Match jobs to resume profiles with explainable scores."""
    
    WEIGHTS = {
        "skills": 0.6,
        "seniority": 0.25,
        "location": 0.15
    }
    
    SENIORITY_LEVELS = {
        "junior": 1,
        "mid": 2,
        "senior": 3,
        "manager": 4
    }
    
    def __init__(self):
        """Initialize matcher."""
        pass
    
    def normalize_skill(self, skill: str) -> str:
        """Normalize skill name for comparison."""
        return skill.lower().strip()
    
    def calculate_skills_score(
        self,
        resume_skills: List[str],
        job_skills: List[str]
    ) -> float:
        """
        Calculate skills match score.
        
        Returns:
            Score between 0 and 1
        """
        if not resume_skills or not job_skills:
            return 0.0
        
        resume_skills_norm = [self.normalize_skill(s) for s in resume_skills]
        job_skills_norm = [self.normalize_skill(s) for s in job_skills]
        
        exact_matches = len(set(resume_skills_norm) & set(job_skills_norm))
        
        fuzzy_matches = 0
        for job_skill in job_skills_norm:
            if job_skill in resume_skills_norm:
                continue
            
            for resume_skill in resume_skills_norm:
                if fuzz.ratio(job_skill, resume_skill) > 80:
                    fuzzy_matches += 0.5
                    break
        
        total_matches = exact_matches + fuzzy_matches
        max_possible = max(len(job_skills_norm), len(resume_skills_norm))
        
        score = min(total_matches / max_possible, 1.0) if max_possible > 0 else 0.0
        
        return score
    
    def calculate_seniority_score(
        self,
        resume_seniority: str,
        job_seniority: str
    ) -> float:
        """
        Calculate seniority match score.
        
        Returns:
            Score between 0 and 1
        """
        if not job_seniority:
            return 0.8
        
        resume_level = self.SENIORITY_LEVELS.get(resume_seniority.lower(), 2)
        job_level = self.SENIORITY_LEVELS.get(job_seniority.lower(), 2)
        
        diff = abs(resume_level - job_level)
        
        if diff == 0:
            return 1.0
        elif diff == 1:
            return 0.7
        elif diff == 2:
            return 0.4
        else:
            return 0.2
    
    def calculate_location_score(
        self,
        resume_locations: List[str],
        job_location: str
    ) -> float:
        """
        Calculate location match score with Bangalore priority.
        
        Returns:
            Score between 0 and 1
        """
        if not job_location:
            return 0.5
        
        job_location_norm = job_location.lower().strip()
        
        if not resume_locations:
            if "bangalore" in job_location_norm or "bengaluru" in job_location_norm:
                return 0.8
            return 0.5
        
        resume_locations_norm = [loc.lower().strip() for loc in resume_locations]
        
        if "remote" in job_location_norm:
            return 1.0
        
        for resume_loc in resume_locations_norm:
            if resume_loc == "remote":
                if "remote" in job_location_norm:
                    return 1.0
                continue
            
            if fuzz.partial_ratio(resume_loc, job_location_norm) > 80:
                if "bangalore" in resume_loc or "bengaluru" in resume_loc:
                    return 1.0
                return 0.9
        
        if "bangalore" in job_location_norm or "bengaluru" in job_location_norm:
            return 0.6
        
        if "india" in job_location_norm:
            return 0.5
        
        return 0.3
    
    def calculate_match_score(
        self,
        resume_profile: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate overall match score with component scores.
        
        Args:
            resume_profile: Parsed resume data with skills, seniority, locations
            job_data: Job data with required_skills, seniority_level, location
        
        Returns:
            Dictionary containing:
            - match_score: Overall score (0-100)
            - skills_score: Component score
            - seniority_score: Component score
            - location_score: Component score
            - top_factors: Top 3 contributing factors
        """
        resume_skills = resume_profile.get("skills", [])
        resume_seniority = resume_profile.get("seniority_level", "mid")
        resume_locations = resume_profile.get("locations_preferred", [])
        
        job_skills = job_data.get("required_skills", [])
        job_seniority = job_data.get("seniority_level", "")
        job_location = job_data.get("location", "")
        
        skills_score = self.calculate_skills_score(resume_skills, job_skills)
        seniority_score = self.calculate_seniority_score(resume_seniority, job_seniority)
        location_score = self.calculate_location_score(resume_locations, job_location)
        
        weighted_score = (
            skills_score * self.WEIGHTS["skills"] +
            seniority_score * self.WEIGHTS["seniority"] +
            location_score * self.WEIGHTS["location"]
        )
        
        match_score = weighted_score * 100
        
        factors = [
            {"name": "Skills Match", "weight": skills_score * 100, "contribution": self.WEIGHTS["skills"]},
            {"name": "Seniority Match", "weight": seniority_score * 100, "contribution": self.WEIGHTS["seniority"]},
            {"name": "Location Match", "weight": location_score * 100, "contribution": self.WEIGHTS["location"]}
        ]
        
        top_factors = sorted(
            factors,
            key=lambda x: x["weight"] * x["contribution"],
            reverse=True
        )[:3]
        
        return {
            "match_score": round(match_score, 2),
            "skills_score": round(skills_score * 100, 2),
            "seniority_score": round(seniority_score * 100, 2),
            "location_score": round(location_score * 100, 2),
            "top_factors": [
                {"name": f["name"], "weight": round(f["weight"], 1)}
                for f in top_factors
            ]
        }
    
    def match_jobs(
        self,
        resume_profile: Dict[str, Any],
        jobs: List[Dict[str, Any]],
        min_score: float = 30.0
    ) -> List[Dict[str, Any]]:
        """
        Match multiple jobs to a resume profile.
        
        Args:
            resume_profile: Parsed resume data
            jobs: List of job dictionaries
            min_score: Minimum match score to include
        
        Returns:
            List of matches with scores, sorted by match_score descending
        """
        matches = []
        
        for job in jobs:
            match_result = self.calculate_match_score(resume_profile, job)
            
            if match_result["match_score"] >= min_score:
                match = {
                    **job,
                    **match_result
                }
                matches.append(match)
        
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return matches
