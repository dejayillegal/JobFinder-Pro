
# JobFinder Pro - Test Suite

This directory contains comprehensive tests for the JobFinder Pro application.

## Test Structure

- `test_matcher.py` - Unit tests for job matching algorithm
- `test_parser.py` - Unit tests for resume parser
- `test_connectors.py` - Unit tests for job connectors
- `test_integration.py` - Integration tests for end-to-end flows
- `conftest.py` - Shared pytest fixtures and configuration
- `validate_setup.py` - Setup validation script
- `run_tests.py` - Test runner with coverage

## Running Tests

### Quick Start

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Validate setup first
make test-validate

# Run everything
make test-all
```

### Detailed Commands

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_integration.py -v

# Run specific test
pytest tests/test_integration.py::TestAuthenticationFlow::test_user_registration -v

# Run with coverage
pytest tests/ --cov=api --cov-report=html

# Run only unit tests
pytest tests/ -m unit

# Run only integration tests
pytest tests/ -m integration
```

## Test Configuration

### Environment Variables

Tests require the following environment variables:

**Required:**
- `DATABASE_URL` - Database connection (uses in-memory SQLite for tests)
- `SECRET_KEY` - JWT secret key
- `REDIS_URL` - Redis connection for Celery

**Optional (for real API tests):**
- `ADZUNA_APP_ID` - Adzuna API credentials
- `ADZUNA_API_KEY` - Adzuna API key
- `MOCK_CONNECTORS=false` - Disable mocks to use real APIs

### Getting Adzuna API Credentials

1. Sign up at https://developer.adzuna.com/
2. Create a new application
3. Copy your App ID and API Key
4. Set environment variables:
   ```bash
   export ADZUNA_APP_ID=your_app_id
   export ADZUNA_API_KEY=your_api_key
   export MOCK_CONNECTORS=false
   ```

## Test Coverage

Our test suite covers:

- ✅ User registration and authentication
- ✅ Token-based authorization (JWT)
- ✅ Resume upload and parsing (PDF, DOCX, TXT)
- ✅ Job connector integration (Adzuna real API + mocks)
- ✅ Job matching algorithm with explainable scores
- ✅ Database models and relationships
- ✅ API endpoints and error handling
- ✅ Integration flows (upload → parse → match → retrieve)

## Writing New Tests

Follow these patterns:

```python
import pytest
from fastapi.testclient import TestClient

class TestYourFeature:
    """Test your feature."""
    
    def test_something(self, client, auth_headers):
        """Test description."""
        response = client.get("/api/endpoint", headers=auth_headers)
        assert response.status_code == 200
```

## Continuous Integration

Tests run automatically on:
- Every push to main branch
- Every pull request
- Using GitHub Actions (see `.github/workflows/ci.yml`)

## Troubleshooting

### Tests failing with "Database not found"
- Check DATABASE_URL is set
- For local testing, ensure PostgreSQL is running

### Tests failing with "Redis connection error"
- Ensure Redis is running locally
- Or set REDIS_URL to valid Redis instance

### Tests timing out
- Some integration tests may be slow with real APIs
- Use `-m unit` to run only fast unit tests

### Mock data vs Real APIs
- By default, connectors use mock data for development
- Set `MOCK_CONNECTORS=false` to use real job APIs
- Only Adzuna has full API support currently
