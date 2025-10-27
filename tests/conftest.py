
"""Pytest configuration and shared fixtures."""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set test environment variables
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["SESSION_SECRET"] = "test-session-secret"
os.environ["DEV_MODE"] = "true"
os.environ["MOCK_CONNECTORS"] = "false"

# Import after setting environment
import pytest
from fastapi.testclient import TestClient


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
