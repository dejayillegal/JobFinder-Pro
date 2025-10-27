"""Tests for job connectors."""

import pytest
from unittest.mock import Mock, patch
from api.app.connectors.adzuna import AdzunaConnector
from api.app.connectors.indeed import IndeedConnector
from api.app.connectors.jooble import JoobleConnector


@pytest.fixture
def adzuna_connector():
    """Create Adzuna connector with mock credentials."""
    return AdzunaConnector(app_id="test_id", api_key="test_key")


@pytest.fixture
def indeed_connector():
    """Create Indeed connector."""
    return IndeedConnector()


@pytest.fixture
def jooble_connector():
    """Create Jooble connector."""
    return JoobleConnector()


class TestAdzunaConnector:
    """Tests for Adzuna connector."""
    
    def test_initialization(self, adzuna_connector):
        """Test connector initialization."""
        assert adzuna_connector.app_id == "test_id"
        assert adzuna_connector.api_key == "test_key"
    
    @patch('httpx.get')
    def test_search_jobs_success(self, mock_get, adzuna_connector):
        """Test successful job search."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "123",
                    "title": "Python Developer",
                    "company": {"display_name": "Tech Corp"},
                    "location": {"display_name": "Bangalore"},
                    "description": "Great Python job",
                    "redirect_url": "https://example.com/job/123",
                    "created": "2025-10-27T00:00:00Z"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        jobs = adzuna_connector.search_jobs(keywords=["Python"], location="Bangalore")
        
        assert len(jobs) == 1
        assert jobs[0]["title"] == "Python Developer"
        assert jobs[0]["company"] == "Tech Corp"
        assert jobs[0]["source"] == "adzuna"
    
    @patch('httpx.get')
    def test_search_jobs_api_error(self, mock_get, adzuna_connector):
        """Test handling of API errors."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        jobs = adzuna_connector.search_jobs(keywords=["Python"])
        
        assert jobs == []
    
    def test_search_jobs_mock_fallback(self):
        """Test mock data fallback when no credentials."""
        connector = AdzunaConnector(app_id=None, api_key=None)
        
        jobs = connector.search_jobs(keywords=["Python"], location="Bangalore")
        
        assert len(jobs) > 0
        assert all(job["source"] == "adzuna" for job in jobs)


class TestIndeedConnector:
    """Tests for Indeed connector."""
    
    def test_search_jobs_returns_mock_data(self, indeed_connector):
        """Test that Indeed returns mock data."""
        jobs = indeed_connector.search_jobs(keywords=["Python"], location="Bangalore")
        
        assert len(jobs) > 0
        assert all(job["source"] == "indeed" for job in jobs)
    
    def test_mock_jobs_have_required_fields(self, indeed_connector):
        """Test that mock jobs have all required fields."""
        jobs = indeed_connector.search_jobs(keywords=["Python"])
        
        for job in jobs:
            assert "external_id" in job
            assert "title" in job
            assert "company" in job
            assert "location" in job
            assert "description" in job
            assert "url" in job
            assert "source" in job
    
    def test_bangalore_filtering(self, indeed_connector):
        """Test that Bangalore location filtering works."""
        jobs = indeed_connector.search_jobs(
            keywords=["Python"],
            location="Bangalore"
        )
        
        # Should include Bangalore jobs
        bangalore_jobs = [j for j in jobs if "Bangalore" in j["location"]]
        assert len(bangalore_jobs) > 0


class TestJoobleConnector:
    """Tests for Jooble connector."""
    
    def test_search_jobs_returns_mock_data(self, jooble_connector):
        """Test that Jooble returns mock data."""
        jobs = jooble_connector.search_jobs(keywords=["Python"], location="Bangalore")
        
        assert len(jobs) > 0
        assert all(job["source"] == "jooble" for job in jobs)
    
    def test_python_keyword_filtering(self, jooble_connector):
        """Test keyword filtering."""
        jobs = jooble_connector.search_jobs(keywords=["Python"])
        
        # Should include Python-related jobs
        python_jobs = [
            j for j in jobs 
            if "Python" in j["title"] or "Python" in j["description"]
        ]
        assert len(python_jobs) > 0


@pytest.mark.parametrize("connector_class,source_name", [
    (AdzunaConnector, "adzuna"),
    (IndeedConnector, "indeed"),
    (JoobleConnector, "jooble"),
])
def test_connector_source_attribution(connector_class, source_name):
    """Test that all connectors attribute source correctly."""
    if connector_class == AdzunaConnector:
        connector = connector_class(app_id=None, api_key=None)
    else:
        connector = connector_class()
    
    jobs = connector.search_jobs(keywords=["Python"])
    
    assert all(job["source"] == source_name for job in jobs)


def test_job_deduplication():
    """Test that jobs with same external_id are not duplicated."""
    connector = IndeedConnector()
    
    jobs = connector.search_jobs(keywords=["Python"])
    external_ids = [job["external_id"] for job in jobs]
    
    # All external IDs should be unique
    assert len(external_ids) == len(set(external_ids))
