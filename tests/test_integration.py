
"""Integration tests for the entire application flow."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import tempfile
import os
from pathlib import Path

from api.main import app
from api.app.core.database import Base, get_db
from api.app.models import User, Resume, Job, JobMatch, ProcessingJob


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """Register a user and return auth headers."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_resume_file():
    """Create a sample resume text file."""
    content = """
    John Doe
    Senior QA Engineer
    john.doe@example.com | +91-9876543210
    
    PROFESSIONAL SUMMARY
    Experienced QA Engineer with 5 years of experience in automation testing,
    Selenium, Python, and API testing. Based in Bangalore, India.
    
    SKILLS
    - Programming: Python, Java, JavaScript
    - Testing: Selenium, Pytest, JUnit, API Testing
    - Tools: Jenkins, Git, JIRA, Postman
    - Databases: PostgreSQL, MySQL
    - Cloud: AWS
    
    EXPERIENCE
    Senior QA Engineer at Tech Corp
    Bangalore, India (2020 - Present)
    - Led automation testing efforts
    - Built CI/CD pipelines
    
    QA Engineer at StartupXYZ
    Bangalore, India (2018 - 2020)
    - Developed test automation framework
    
    EDUCATION
    B.Tech in Computer Science
    IIT Delhi (2014 - 2018)
    """
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_file.write(content)
    temp_file.close()
    
    yield temp_file.name
    
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)


class TestAuthenticationFlow:
    """Test user authentication flows."""
    
    def test_user_registration(self, client):
        """Test user can register successfully."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepass123",
                "full_name": "New User"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_duplicate_registration(self, client, auth_headers):
        """Test duplicate email registration fails."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_user_login(self, client, auth_headers):
        """Test user can login successfully."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_login_wrong_password(self, client, auth_headers):
        """Test login fails with wrong password."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
    
    def test_token_refresh(self, client, auth_headers):
        """Test token refresh works."""
        # First register and get tokens
        reg_response = client.post(
            "/api/auth/register",
            json={
                "email": "refresh@example.com",
                "password": "testpass123"
            }
        )
        refresh_token = reg_response.json()["refresh_token"]
        
        # Refresh the token
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data


class TestResumeUpload:
    """Test resume upload and processing."""
    
    def test_health_check(self, client):
        """Test API health check."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_upload_resume_unauthorized(self, client, sample_resume_file):
        """Test resume upload requires authentication."""
        with open(sample_resume_file, 'rb') as f:
            response = client.post(
                "/api/resume/upload",
                files={"file": ("resume.txt", f, "text/plain")}
            )
        assert response.status_code == 401
    
    def test_upload_resume_success(self, client, auth_headers, sample_resume_file):
        """Test successful resume upload."""
        with open(sample_resume_file, 'rb') as f:
            response = client.post(
                "/api/resume/upload",
                files={"file": ("resume.txt", f, "text/plain")},
                headers=auth_headers
            )
        assert response.status_code == 202
        data = response.json()
        assert "job_id" in data
        assert "resume_id" in data
        assert "message" in data
    
    def test_upload_invalid_file_type(self, client, auth_headers):
        """Test upload rejects invalid file types."""
        content = b"Invalid file content"
        response = client.post(
            "/api/resume/upload",
            files={"file": ("resume.exe", content, "application/x-msdownload")},
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"].lower()


class TestJobMatching:
    """Test job matching functionality."""
    
    def test_get_matches_empty(self, client, auth_headers):
        """Test getting matches when none exist."""
        response = client.get("/api/matches/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["matches"] == []
    
    def test_get_matches_with_filters(self, client, auth_headers):
        """Test getting matches with filters."""
        response = client.get(
            "/api/matches/",
            params={"min_score": 50, "location": "Bangalore"},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "total" in response.json()
        assert "matches" in response.json()


class TestResumeParser:
    """Test resume parsing functionality."""
    
    def test_parse_text_file(self, sample_resume_file):
        """Test parsing text resume."""
        from api.app.services.resume_parser import ResumeParser
        
        parser = ResumeParser()
        result = parser.parse_resume(sample_resume_file)
        
        assert result["success"] is True
        assert "skills" in result
        assert len(result["skills"]) > 0
        assert "python" in [s.lower() for s in result["skills"]]
        assert "selenium" in [s.lower() for s in result["skills"]]
        assert result["years_experience"] >= 5
        assert "locations_preferred" in result
        assert any("bangalore" in loc.lower() for loc in result["locations_preferred"])


class TestJobConnectors:
    """Test job connector functionality with real APIs."""
    
    def test_adzuna_connector_real(self):
        """Test Adzuna connector with real API if credentials available."""
        from api.app.connectors.adzuna import AdzunaConnector
        from api.app.core.config import settings
        
        # Skip if no credentials
        if not settings.ADZUNA_APP_ID or not settings.ADZUNA_APP_KEY:
            pytest.skip("Adzuna API credentials not configured")
        
        connector = AdzunaConnector(use_mock=False)
        jobs = connector.search_jobs(query="QA Engineer", location="Bangalore", max_results=5)
        
        assert len(jobs) > 0
        for job in jobs:
            assert "title" in job
            assert "company" in job
            assert "url" in job
            assert job["url"].startswith("http")
            assert job["source"] == "Adzuna"


class TestMatchingAlgorithm:
    """Test job matching algorithm."""
    
    def test_perfect_skills_match(self):
        """Test matching with perfect skill overlap."""
        from api.app.services.matcher import JobMatcher
        
        matcher = JobMatcher()
        
        resume = {
            "skills": ["Python", "Selenium", "API Testing"],
            "seniority_level": "senior",
            "locations_preferred": ["Bangalore"]
        }
        
        job = {
            "title": "Senior QA Engineer",
            "required_skills": ["Python", "Selenium", "API Testing"],
            "seniority_level": "senior",
            "location": "Bangalore"
        }
        
        result = matcher.calculate_match_score(resume, job)
        
        assert result["match_score"] > 80
        assert result["skills_score"] > 90
        assert result["seniority_score"] == 100
        assert result["location_score"] > 90
    
    def test_partial_skills_match(self):
        """Test matching with partial skill overlap."""
        from api.app.services.matcher import JobMatcher
        
        matcher = JobMatcher()
        
        resume = {
            "skills": ["Python", "Java"],
            "seniority_level": "mid",
            "locations_preferred": ["Bangalore"]
        }
        
        job = {
            "title": "Software Engineer",
            "required_skills": ["Python", "JavaScript", "React", "Node.js"],
            "seniority_level": "mid",
            "location": "Bangalore"
        }
        
        result = matcher.calculate_match_score(resume, job)
        
        assert 20 < result["match_score"] < 80
        assert result["skills_score"] < 50
    
    def test_location_scoring_bangalore(self):
        """Test Bangalore location gets priority."""
        from api.app.services.matcher import JobMatcher
        
        matcher = JobMatcher()
        
        resume = {
            "skills": ["Python"],
            "seniority_level": "mid",
            "locations_preferred": ["Bangalore"]
        }
        
        job = {
            "title": "Engineer",
            "required_skills": ["Python"],
            "seniority_level": "mid",
            "location": "Bangalore, India"
        }
        
        result = matcher.calculate_match_score(resume, job)
        assert result["location_score"] >= 90


class TestDatabaseModels:
    """Test database models and relationships."""
    
    def test_user_creation(self, db_session):
        """Test creating a user."""
        from api.app.core.security import get_password_hash
        
        user = User(
            email="dbtest@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="DB Test User"
        )
        db_session.add(user)
        db_session.commit()
        
        retrieved = db_session.query(User).filter(User.email == "dbtest@example.com").first()
        assert retrieved is not None
        assert retrieved.email == "dbtest@example.com"
        assert retrieved.full_name == "DB Test User"
    
    def test_resume_relationship(self, db_session):
        """Test user-resume relationship."""
        from api.app.core.security import get_password_hash
        
        user = User(
            email="resume@example.com",
            hashed_password=get_password_hash("password123")
        )
        db_session.add(user)
        db_session.commit()
        
        resume = Resume(
            user_id=user.id,
            filename="test.txt",
            file_path="/tmp/test.txt",
            skills=["Python", "Java"],
            years_experience=5
        )
        db_session.add(resume)
        db_session.commit()
        
        assert len(user.resumes) == 1
        assert user.resumes[0].filename == "test.txt"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
