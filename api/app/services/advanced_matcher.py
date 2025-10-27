"""
Advanced NLP-based job matching engine with TF-IDF and semantic similarity.
Uses spaCy for NER skill extraction and cosine similarity for matching.
"""
from typing import Dict, List, Any, Tuple, Optional
import logging
import re
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
import spacy

logger = logging.getLogger(__name__)


class AdvancedJobMatcher:
    """Advanced job matcher with NLP and semantic analysis."""
    
    WEIGHTS = {
        "semantic_similarity": 0.35,
        "skills_match": 0.35,
        "seniority_match": 0.15,
        "location_match": 0.15
    }
    
    SENIORITY_LEVELS = {
        "intern": 0,
        "entry": 1,
        "junior": 2,
        "mid": 3,
        "senior": 4,
        "lead": 5,
        "principal": 6,
        "manager": 7,
        "director": 8
    }
    
    SKILL_IMPORTANCE_WEIGHTS = {
        "python": 1.5, "java": 1.5, "javascript": 1.4, "typescript": 1.4,
        "react": 1.4, "angular": 1.3, "vue": 1.3, "nodejs": 1.4, "django": 1.3,
        "aws": 1.6, "azure": 1.5, "gcp": 1.5, "kubernetes": 1.5, "docker": 1.4,
        "machine learning": 1.6, "deep learning": 1.5, "tensorflow": 1.4,
        "pytorch": 1.4, "data science": 1.5, "sql": 1.3, "postgresql": 1.3,
        "mongodb": 1.3, "redis": 1.2, "elasticsearch": 1.3,
        "git": 1.1, "ci/cd": 1.3, "agile": 1.1, "scrum": 1.1,
        "rest api": 1.3, "graphql": 1.3, "microservices": 1.4,
        "testing": 1.2, "selenium": 1.2, "pytest": 1.2, "junit": 1.2
    }
    
    def __init__(self, spacy_model: str = "en_core_web_sm"):
        """Initialize advanced matcher with spaCy model."""
        self.spacy_model_name = spacy_model
        self.nlp = None
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 3),
            stop_words='english',
            lowercase=True
        )
        self._load_spacy_model()
    
    def _load_spacy_model(self):
        """Load spaCy model with error handling."""
        try:
            self.nlp = spacy.load(self.spacy_model_name)
            logger.info(f"Loaded spaCy model: {self.spacy_model_name}")
        except Exception as e:
            logger.warning(f"Could not load spaCy model {self.spacy_model_name}: {e}")
            logger.warning("Advanced NLP features will be limited")
            self.nlp = None
    
    def extract_skills_nlp(self, text: str) -> List[str]:
        """Extract skills from text using NLP and pattern matching."""
        if not text:
            return []
        
        skills = set()
        text_lower = text.lower()
        
        for skill_pattern in self.SKILL_IMPORTANCE_WEIGHTS.keys():
            if skill_pattern in text_lower:
                skills.add(skill_pattern)
        
        common_skills = [
            "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "php", "go", "rust",
            "react", "angular", "vue", "svelte", "nextjs", "nodejs", "express", "django", "flask",
            "spring", "laravel", "rails", "asp.net",
            "aws", "azure", "gcp", "heroku", "vercel", "netlify",
            "docker", "kubernetes", "jenkins", "gitlab", "github actions", "terraform", "ansible",
            "mysql", "postgresql", "mongodb", "redis", "cassandra", "dynamodb", "elasticsearch",
            "rest api", "graphql", "grpc", "websockets", "microservices",
            "machine learning", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch",
            "scikit-learn", "pandas", "numpy", "matplotlib", "keras",
            "agile", "scrum", "kanban", "jira", "confluence",
            "git", "svn", "mercurial",
            "linux", "unix", "windows", "macos",
            "selenium", "cypress", "jest", "mocha", "pytest", "junit"
        ]
        
        for skill in common_skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                skills.add(skill)
        
        if self.nlp:
            try:
                doc = self.nlp(text[:10000])
                for ent in doc.ents:
                    if ent.label_ in ["PRODUCT", "ORG", "TECHNOLOGY"]:
                        skill_candidate = ent.text.lower().strip()
                        if len(skill_candidate) > 2 and len(skill_candidate) < 30:
                            skills.add(skill_candidate)
            except Exception as e:
                logger.debug(f"NER extraction error: {e}")
        
        return list(skills)
    
    def calculate_semantic_similarity(
        self,
        resume_text: str,
        job_description: str
    ) -> float:
        """Calculate semantic similarity using TF-IDF and cosine similarity."""
        if not resume_text or not job_description:
            return 0.0
        
        try:
            resume_text_clean = self._clean_text(resume_text)
            job_text_clean = self._clean_text(job_description)
            
            if not resume_text_clean or not job_text_clean:
                return 0.0
            
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([resume_text_clean, job_text_clean])
            
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Semantic similarity calculation error: {e}")
            return 0.0
    
    def _clean_text(self, text: str) -> str:
        """Clean text for TF-IDF processing."""
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def calculate_skills_score_advanced(
        self,
        resume_skills: List[str],
        job_skills: List[str]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate advanced skills match score with importance weighting.
        
        Returns:
            Tuple of (score, details_dict)
        """
        if not resume_skills or not job_skills:
            return 0.0, {"matched": [], "missing": job_skills or []}
        
        resume_skills_norm = {self._normalize_skill(s) for s in resume_skills}
        job_skills_norm = {self._normalize_skill(s) for s in job_skills}
        
        matched_skills = []
        missing_skills = []
        total_weight = 0.0
        matched_weight = 0.0
        
        for job_skill in job_skills_norm:
            skill_weight = self.SKILL_IMPORTANCE_WEIGHTS.get(job_skill, 1.0)
            total_weight += skill_weight
            
            if job_skill in resume_skills_norm:
                matched_skills.append(job_skill)
                matched_weight += skill_weight
            else:
                fuzzy_match = False
                for resume_skill in resume_skills_norm:
                    if fuzz.ratio(job_skill, resume_skill) > 85:
                        matched_skills.append(job_skill)
                        matched_weight += skill_weight * 0.8
                        fuzzy_match = True
                        break
                
                if not fuzzy_match:
                    missing_skills.append(job_skill)
        
        score = (matched_weight / total_weight) if total_weight > 0 else 0.0
        
        details = {
            "matched": matched_skills,
            "missing": missing_skills,
            "match_rate": f"{len(matched_skills)}/{len(job_skills_norm)}"
        }
        
        return min(score, 1.0), details
    
    def _normalize_skill(self, skill: str) -> str:
        """Normalize skill name for comparison."""
        return skill.lower().strip().replace("_", " ").replace("-", " ")
    
    def calculate_seniority_score(
        self,
        resume_seniority: str,
        job_seniority: str
    ) -> float:
        """Calculate seniority match score with partial credit."""
        if not job_seniority:
            return 0.8
        
        resume_level = self.SENIORITY_LEVELS.get(resume_seniority.lower(), 3)
        job_level = self.SENIORITY_LEVELS.get(job_seniority.lower(), 3)
        
        diff = abs(resume_level - job_level)
        
        if diff == 0:
            return 1.0
        elif diff == 1:
            return 0.75
        elif diff == 2:
            return 0.5
        elif diff == 3:
            return 0.3
        else:
            return 0.1
    
    def calculate_location_score(
        self,
        resume_locations: List[str],
        job_location: str
    ) -> float:
        """Calculate location match score."""
        if not job_location:
            return 0.5
        
        job_location_norm = job_location.lower().strip()
        
        if "remote" in job_location_norm:
            return 1.0
        
        if not resume_locations:
            if "bangalore" in job_location_norm or "bengaluru" in job_location_norm:
                return 0.75
            return 0.5
        
        resume_locations_norm = [loc.lower().strip() for loc in resume_locations]
        
        for resume_loc in resume_locations_norm:
            if resume_loc == "remote" and "remote" in job_location_norm:
                return 1.0
            
            if fuzz.partial_ratio(resume_loc, job_location_norm) > 80:
                return 0.95
        
        if "bangalore" in job_location_norm or "bengaluru" in job_location_norm:
            return 0.6
        
        return 0.3
    
    def calculate_match_score(
        self,
        resume_profile: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive match score with all factors.
        
        Args:
            resume_profile: Parsed resume data
            job_data: Job data
        
        Returns:
            Dictionary with scores and explanations
        """
        resume_text = resume_profile.get("raw_text", "")
        job_description = job_data.get("description", "")
        
        semantic_score = self.calculate_semantic_similarity(resume_text, job_description)
        
        resume_skills = resume_profile.get("skills", [])
        job_skills = job_data.get("required_skills", [])
        
        if not job_skills and job_description:
            job_skills = self.extract_skills_nlp(job_description)
        
        skills_score, skills_details = self.calculate_skills_score_advanced(resume_skills, job_skills)
        
        resume_seniority = resume_profile.get("seniority_level", "mid")
        job_seniority = job_data.get("seniority_level", "")
        seniority_score = self.calculate_seniority_score(resume_seniority, job_seniority)
        
        resume_locations = resume_profile.get("locations_preferred", [])
        job_location = job_data.get("location", "")
        location_score = self.calculate_location_score(resume_locations, job_location)
        
        weighted_score = (
            semantic_score * self.WEIGHTS["semantic_similarity"] +
            skills_score * self.WEIGHTS["skills_match"] +
            seniority_score * self.WEIGHTS["seniority_match"] +
            location_score * self.WEIGHTS["location_match"]
        )
        
        match_score = weighted_score * 100
        
        factors = [
            {"name": "Semantic Similarity", "score": semantic_score * 100, "weight": self.WEIGHTS["semantic_similarity"]},
            {"name": "Skills Match", "score": skills_score * 100, "weight": self.WEIGHTS["skills_match"]},
            {"name": "Seniority Match", "score": seniority_score * 100, "weight": self.WEIGHTS["seniority_match"]},
            {"name": "Location Match", "score": location_score * 100, "weight": self.WEIGHTS["location_match"]}
        ]
        
        top_factors = sorted(
            factors,
            key=lambda x: x["score"] * x["weight"],
            reverse=True
        )[:3]
        
        return {
            "match_score": round(match_score, 2),
            "semantic_similarity": round(semantic_score * 100, 2),
            "skills_score": round(skills_score * 100, 2),
            "seniority_score": round(seniority_score * 100, 2),
            "location_score": round(location_score * 100, 2),
            "skills_details": skills_details,
            "top_factors": [
                {"name": f["name"], "score": round(f["score"], 1)}
                for f in top_factors
            ]
        }
    
    def match_jobs(
        self,
        resume_profile: Dict[str, Any],
        jobs: List[Dict[str, Any]],
        min_score: float = 25.0
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
            try:
                match_result = self.calculate_match_score(resume_profile, job)
                
                if match_result["match_score"] >= min_score:
                    match = {
                        **job,
                        **match_result
                    }
                    matches.append(match)
            except Exception as e:
                logger.error(f"Error matching job {job.get('title', 'unknown')}: {e}")
                continue
        
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return matches
