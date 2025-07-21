"""
Simple integration test for API health check
"""

import pytest
from fastapi.testclient import TestClient

# Import the FastAPI app directly
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from breakout_screener.main import app


def test_health_check():
    """Test API health check endpoint"""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


def test_api_docs():
    """Test that API documentation is accessible"""
    with TestClient(app) as client:
        response = client.get("/docs")
        assert response.status_code == 200


def test_api_root():
    """Test API root endpoint"""
    with TestClient(app) as client:
        response = client.get("/")
        # Should either redirect to docs or return some response
        assert response.status_code in [200, 307]


if __name__ == "__main__":
    # Run the tests directly
    test_health_check()
    test_api_docs()
    test_api_root()
    print("All simple integration tests passed!")