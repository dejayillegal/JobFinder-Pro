"""Tests for job matching algorithm."""

import pytest
from api.app.services.matcher import JobMatcher


@pytest.fixture
def matcher():
    """Create JobMatcher instance."""
    return JobMatcher()


@pytest.fixture
def sample_resume():
    """Sample resume data for testing."""
    return {
        "skills": ["Python", "Django", "PostgreSQL", "AWS", "Docker"],
        "years_experience": 5,
        "current_role": "Senior Software Engineer",
        "locations_preferred": ["Bangalore", "Remote"]
    }


@pytest.fixture
def sample_job():
    """Sample job data for testing."""
    return {
        "title": "Senior Backend Engineer",
        "company": "Tech Corp",
        "location": "Bangalore",
        "description": "We need a Python expert with Django experience",
        "required_skills": ["Python", "Django", "PostgreSQL", "AWS"],
        "seniority_level": "Senior"
    }


def test_perfect_match(matcher, sample_resume, sample_job):
    """Test matching with perfect skill overlap."""
    result = matcher.calculate_match(sample_resume, sample_job)
    
    assert result["score"] > 80.0
    assert "skills_score" in result
    assert "seniority_score" in result
    assert "location_score" in result


def test_partial_skill_match(matcher, sample_resume):
    """Test matching with partial skill overlap."""
    job = {
        "title": "Full Stack Developer",
        "company": "StartupXYZ",
        "location": "Bangalore",
        "description": "React and Node.js developer needed",
        "required_skills": ["Python", "React", "Node.js", "MongoDB"],
        "seniority_level": "Mid-Level"
    }
    
    result = matcher.calculate_match(sample_resume, job)
    
    assert 0 < result["score"] < 100
    assert result["skills_score"] < 100


def test_no_skill_match(matcher, sample_resume):
    """Test matching with no skill overlap."""
    job = {
        "title": "iOS Developer",
        "company": "Mobile Inc",
        "location": "Mumbai",
        "description": "Swift and Objective-C required",
        "required_skills": ["Swift", "Objective-C", "iOS", "Xcode"],
        "seniority_level": "Senior"
    }
    
    result = matcher.calculate_match(sample_resume, job)
    
    assert result["score"] < 50.0


def test_location_scoring_bangalore(matcher, sample_resume, sample_job):
    """Test location scoring for Bangalore."""
    result = matcher.calculate_match(sample_resume, sample_job)
    
    assert result["location_score"] == 100.0


def test_location_scoring_remote(matcher, sample_resume):
    """Test location scoring for Remote positions."""
    job = {
        "title": "Remote Engineer",
        "company": "Remote Co",
        "location": "Remote",
        "description": "Work from anywhere",
        "required_skills": ["Python"],
        "seniority_level": "Senior"
    }
    
    result = matcher.calculate_match(sample_resume, job)
    
    assert result["location_score"] == 100.0


def test_location_scoring_other_city(matcher, sample_resume):
    """Test location scoring for non-preferred city."""
    job = {
        "title": "Engineer",
        "company": "Delhi Tech",
        "location": "Delhi",
        "description": "On-site position",
        "required_skills": ["Python"],
        "seniority_level": "Senior"
    }
    
    result = matcher.calculate_match(sample_resume, job)
    
    assert result["location_score"] < 100.0


def test_seniority_exact_match(matcher, sample_resume, sample_job):
    """Test seniority scoring with exact match."""
    result = matcher.calculate_match(sample_resume, sample_job)
    
    assert result["seniority_score"] == 100.0


def test_seniority_mismatch(matcher, sample_resume):
    """Test seniority scoring with mismatched levels."""
    job = {
        "title": "Junior Developer",
        "company": "Startup",
        "location": "Bangalore",
        "description": "Entry level position",
        "required_skills": ["Python"],
        "seniority_level": "Entry"
    }
    
    result = matcher.calculate_match(sample_resume, job)
    
    assert result["seniority_score"] < 100.0


def test_match_explanation(matcher, sample_resume, sample_job):
    """Test that match includes explanation factors."""
    result = matcher.calculate_match(sample_resume, sample_job)
    
    assert "top_factors" in result
    assert len(result["top_factors"]) > 0
    
    # Should have factor explanations
    for factor in result["top_factors"]:
        assert "factor" in factor
        assert "impact" in factor


def test_weighted_scoring(matcher):
    """Test that scoring weights are applied correctly."""
    resume = {
        "skills": ["Python"],
        "years_experience": 5,
        "current_role": "Senior Engineer",
        "locations_preferred": ["Bangalore"]
    }
    
    job = {
        "title": "Senior Engineer",
        "company": "Test",
        "location": "Bangalore",
        "description": "Test job",
        "required_skills": ["Python"],
        "seniority_level": "Senior"
    }
    
    result = matcher.calculate_match(resume, job)
    
    # Perfect match should give high score
    assert result["score"] >= 90.0


def test_case_insensitive_skills(matcher):
    """Test that skill matching is case-insensitive."""
    resume = {
        "skills": ["python", "django"],
        "years_experience": 3,
        "current_role": "Developer",
        "locations_preferred": ["Bangalore"]
    }
    
    job = {
        "title": "Developer",
        "company": "Test",
        "location": "Bangalore",
        "description": "Test",
        "required_skills": ["Python", "Django"],
        "seniority_level": "Mid-Level"
    }
    
    result = matcher.calculate_match(resume, job)
    
    assert result["skills_score"] == 100.0


@pytest.mark.parametrize("resume_skills,job_skills,expected_min_score", [
    (["Python", "Django"], ["Python", "Django"], 90),
    (["Python"], ["Python", "Django", "React"], 30),
    (["Python", "Django", "React"], ["Python"], 30),
    ([], ["Python"], 0),
])
def test_skill_scoring_variations(matcher, resume_skills, job_skills, expected_min_score):
    """Test skill scoring with various combinations."""
    resume = {
        "skills": resume_skills,
        "years_experience": 3,
        "current_role": "Developer",
        "locations_preferred": ["Bangalore"]
    }
    
    job = {
        "title": "Developer",
        "company": "Test",
        "location": "Bangalore",
        "description": "Test",
        "required_skills": job_skills,
        "seniority_level": "Mid-Level"
    }
    
    result = matcher.calculate_match(resume, job)
    
    assert result["skills_score"] >= expected_min_score
