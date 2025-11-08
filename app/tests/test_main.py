"""
Test FastAPI application initialization.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestAppInitialization:
    """Test basic FastAPI app setup."""
    
    def test_app_exists(self):
        """Test that the FastAPI app instance is created."""
        assert app is not None
        assert hasattr(app, 'routes')
    
    def test_health_endpoint(self):
        """Test that a basic health check endpoint works."""
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()
        assert response.json()["status"] == "healthy"
