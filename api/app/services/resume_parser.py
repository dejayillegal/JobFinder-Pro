"""
Resume parsing service using pdfminer.six, python-docx, and spaCy.
Extracts skills, experience, role, and location preferences from resumes.
"""
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

COMMON_SKILLS = [
    "python", "java", "javascript", "typescript", "react", "angular", "vue",
    "node", "nodejs", "express", "fastapi", "flask", "django",
    "sql", "postgresql", "mysql", "mongodb", "redis",
    "aws", "azure", "gcp", "docker", "kubernetes", "k8s",
    "git", "jenkins", "ci/cd", "devops",
    "machine learning", "ml", "ai", "data science",
    "selenium", "pytest", "jest", "testing", "qa",
    "rest", "api", "graphql", "microservices",
    "html", "css", "tailwind", "bootstrap",
    "agile", "scrum", "jira"
]

SENIORITY_KEYWORDS = {
    "junior": ["junior", "associate", "entry level", "fresher", "0-2 years"],
    "mid": ["mid level", "intermediate", "2-5 years", "3-6 years"],
    "senior": ["senior", "lead", "principal", "staff", "5+ years", "7+ years"],
    "manager": ["manager", "director", "head", "vp", "chief"]
}

INDIAN_CITIES = [
    "bangalore", "bengaluru", "mumbai", "delhi", "pune", "hyderabad",
    "chennai", "kolkata", "ahmedabad", "gurgaon", "noida", "remote"
]


class ResumeParser:
    """Parse resumes to extract structured information."""

    def __init__(self):
        """Initialize parser with optional spaCy model."""
        self.nlp = None
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            logger.warning(f"spaCy model not loaded: {e}. Using rule-based extraction only.")

    def parse_pdf(self, file_path: str) -> str:
        """Extract text from PDF using pdfminer.six."""
        try:
            from pdfminer.high_level import extract_text
            text = extract_text(file_path)
            return text
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise

    def parse_docx(self, file_path: str) -> str:
        """Extract text from DOCX using python-docx."""
        try:
            from docx import Document
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            logger.error(f"Error parsing DOCX: {e}")
            raise

    def parse_txt(self, file_path: str) -> str:
        """Read text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading TXT: {e}")
            raise

    def extract_text(self, file_path: str) -> str:
        """Extract text from resume based on file extension."""
        path = Path(file_path)
        extension = path.suffix.lower()

        if extension == '.pdf':
            return self.parse_pdf(file_path)
        elif extension == '.docx':
            return self.parse_docx(file_path)
        elif extension == '.txt':
            return self.parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {extension}")

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text using keyword matching."""
        text_lower = text.lower()
        found_skills = []

        for skill in COMMON_SKILLS:
            if skill.lower() in text_lower:
                found_skills.append(skill)

        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ["ORG", "PRODUCT"] and len(ent.text.split()) <= 3:
                    skill = ent.text.strip()
                    if skill.lower() not in [s.lower() for s in found_skills]:
                        found_skills.append(skill)

        return list(set(found_skills))[:20]

    def extract_years_experience(self, text: str) -> Optional[int]:
        """Extract years of experience using regex patterns."""
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)[\s\w]*(?:experience|exp)',
            r'experience.*?(\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\+?\s*(?:years?|yrs?)\s+in'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                years = int(match.group(1))
                return min(years, 50)

        return None

    def extract_current_role(self, text: str) -> Optional[str]:
        """Extract current role/title from resume."""
        role_patterns = [
            r'(?:current|present)[\s\w]*:?\s*([^\n]{10,60})',
            r'(?:software|qa|test|quality)\s+(?:engineer|developer|analyst|tester)[^\n]{0,30}'
        ]

        for pattern in role_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                role = match.group(0).strip()
                return role[:100]

        lines = text.split('\n')[:10]
        for line in lines:
            if any(keyword in line.lower() for keyword in ['engineer', 'developer', 'analyst', 'qa', 'tester']):
                return line.strip()[:100]

        return None

    def extract_locations(self, text: str) -> List[str]:
        """Extract location preferences."""
        text_lower = text.lower()
        found_locations = []

        for city in INDIAN_CITIES:
            if city in text_lower:
                found_locations.append(city.title())

        if "remote" in text_lower or "work from home" in text_lower:
            if "Remote" not in found_locations:
                found_locations.append("Remote")

        return found_locations[:5]

    def extract_seniority(self, text: str, years_experience: Optional[int]) -> str:
        """Determine seniority level."""
        text_lower = text.lower()

        for level, keywords in SENIORITY_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                return level

        if years_experience is not None:
            if years_experience < 2:
                return "junior"
            elif years_experience < 5:
                return "mid"
            elif years_experience < 10:
                return "senior"
            else:
                return "senior"

        return "mid"

    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """
        Parse resume file and extract information.

        Args:
            file_path: Path to resume file

        Returns:
            Dictionary with parsed resume data (sanitized for privacy)
        """
        from ..core.config import settings
        from ..utils.privacy import privacy_manager

        try:
            raw_text = self.extract_text(file_path)

            skills = self.extract_skills(raw_text)
            years_experience = self.extract_years_experience(raw_text)
            current_role = self.extract_current_role(raw_text)
            locations_preferred = self.extract_locations(raw_text)
            seniority_level = self.extract_seniority(raw_text, years_experience)

            # Sanitize resume text if raw storage is disabled
            stored_text = raw_text
            if not privacy_manager.should_store_raw(settings):
                stored_text = privacy_manager.sanitize_resume_text(raw_text)

            return {
                "success": True,
                "raw_text": stored_text,
                "skills": skills,
                "years_experience": years_experience,
                "current_role": current_role,
                "locations_preferred": locations_preferred,
                "seniority_level": seniority_level
            }
        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            return {
                "raw_text": "",
                "skills": [],
                "years_experience": None,
                "current_role": None,
                "locations_preferred": [],
                "seniority_level": "mid",
                "education": [],
                "success": False,
                "error": str(e)
            }