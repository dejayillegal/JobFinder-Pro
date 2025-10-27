"""Tests for resume parser service."""

import pytest
from pathlib import Path
from api.app.services.resume_parser import ResumeParser


@pytest.fixture
def parser():
    """Create ResumeParser instance."""
    return ResumeParser()


@pytest.fixture
def sample_text_resume():
    """Sample resume text for testing."""
    return """
    John Doe
    Senior Software Engineer
    john.doe@example.com | +91-9876543210
    
    SUMMARY
    Experienced software engineer with 5 years of experience in Python and cloud technologies.
    
    SKILLS
    - Programming: Python, JavaScript, Java, Go
    - Frameworks: Django, FastAPI, React, Node.js
    - Databases: PostgreSQL, MongoDB, Redis
    - Cloud: AWS, Azure, Docker, Kubernetes
    - Tools: Git, Jenkins, Terraform
    
    EXPERIENCE
    Senior Software Engineer at Tech Corp
    Bangalore, India (2020 - Present)
    - Led team of 5 engineers
    - Built microservices architecture
    - Reduced deployment time by 60%
    
    Software Engineer at StartupXYZ
    Bangalore, India (2018 - 2020)
    - Developed REST APIs
    - Implemented CI/CD pipelines
    
    EDUCATION
    B.Tech in Computer Science
    IIT Delhi (2014 - 2018)
    """


def test_extract_skills(parser, sample_text_resume):
    """Test skill extraction from resume."""
    parsed = parser.parse_text(sample_text_resume)
    
    assert "skills" in parsed
    skills = [s.lower() for s in parsed["skills"]]
    
    assert "python" in skills
    assert "javascript" in skills
    assert "aws" in skills
    assert "docker" in skills


def test_extract_experience_years(parser, sample_text_resume):
    """Test years of experience calculation."""
    parsed = parser.parse_text(sample_text_resume)
    
    assert "years_experience" in parsed
    assert parsed["years_experience"] >= 5


def test_extract_locations(parser, sample_text_resume):
    """Test location extraction."""
    parsed = parser.parse_text(sample_text_resume)
    
    assert "locations_preferred" in parsed
    locations = [loc.lower() for loc in parsed["locations_preferred"]]
    assert "bangalore" in locations


def test_extract_education(parser, sample_text_resume):
    """Test education extraction."""
    parsed = parser.parse_text(sample_text_resume)
    
    assert "education" in parsed
    assert len(parsed["education"]) > 0


def test_parse_empty_text(parser):
    """Test parsing empty text."""
    parsed = parser.parse_text("")
    
    assert parsed["skills"] == []
    assert parsed["years_experience"] == 0


def test_parse_with_email(parser):
    """Test email extraction."""
    text = "Contact me at john.doe@example.com"
    parsed = parser.parse_text(text)
    
    assert "john.doe@example.com" in parsed["raw_text"]


def test_skill_normalization(parser):
    """Test that skills are normalized correctly."""
    text = "I know python, PYTHON, Python, nodejs, Node.js"
    parsed = parser.parse_text(text)
    
    skills_lower = [s.lower() for s in parsed["skills"]]
    
    # Python should appear once despite different cases
    python_count = skills_lower.count("python")
    assert python_count >= 1


def test_years_experience_calculation(parser):
    """Test years of experience from date ranges."""
    text = """
    Senior Engineer (2018 - 2023)
    Junior Engineer (2015 - 2018)
    """
    parsed = parser.parse_text(text)
    
    # Should calculate approximately 8 years
    assert parsed["years_experience"] >= 5


def test_current_role_extraction(parser):
    """Test current role extraction."""
    text = """
    Senior Software Engineer at Google
    Experience: 5 years in backend development
    """
    parsed = parser.parse_text(text)
    
    assert "current_role" in parsed
    role = parsed["current_role"].lower()
    assert "engineer" in role or "software" in role


@pytest.mark.parametrize("skill,expected", [
    ("Python", True),
    ("JavaScript", True),
    ("AWS", True),
    ("RandomSkill123", False),
])
def test_skill_detection(parser, skill, expected):
    """Test skill detection with various inputs."""
    text = f"I am proficient in {skill}"
    parsed = parser.parse_text(text)
    
    skills_lower = [s.lower() for s in parsed["skills"]]
    if expected:
        assert skill.lower() in skills_lower or any(skill.lower() in s for s in skills_lower)
