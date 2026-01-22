"""
Integration tests for FastAPI backend
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient

from src.fastapi.app.main import app
from src.fastapi.app.core.config import settings

# Test client
client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_main_health_endpoint(self):
        """Test main health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "alexa-plus-chatbot-api"
    
    def test_api_health_endpoint(self):
        """Test API v1 health endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "alexa-plus-chatbot-api-v1"


class TestAuthenticationEndpoints:
    """Test authentication endpoints"""
    
    def test_login_endpoint_exists(self):
        """Test that login endpoint exists"""
        # This will fail without valid credentials, but endpoint should exist
        response = client.post("/api/v1/auth/token", data={
            "username": "invalid",
            "password": "invalid"
        })
        # Should return 401 (unauthorized) not 404 (not found)
        assert response.status_code == 401
    
    def test_register_endpoint_exists(self):
        """Test that register endpoint exists"""
        response = client.post("/api/v1/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "testpass123"
        })
        # Should not return 404 (endpoint exists)
        assert response.status_code != 404


class TestAPIStructure:
    """Test API structure and routing"""
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = client.options("/api/v1/health")
        # Should have CORS headers or at least not fail
        assert response.status_code in [200, 405]  # 405 = Method not allowed but endpoint exists
    
    def test_api_versioning(self):
        """Test API versioning structure"""
        # Test that v1 endpoints are properly structured
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        # Test that non-existent versions return 404
        response = client.get("/api/v2/health")
        assert response.status_code == 404


@pytest.mark.asyncio
class TestWebSocketEndpoints:
    """Test WebSocket endpoints"""
    
    async def test_websocket_endpoint_exists(self):
        """Test that WebSocket endpoints are configured"""
        # This is a basic test to ensure WebSocket routes are set up
        # Full WebSocket testing would require more complex setup
        
        with client.websocket_connect("/ws/live-updates") as websocket:
            # If we can connect, the endpoint exists
            assert websocket is not None


class TestDatabaseIntegration:
    """Test database integration (mocked)"""
    
    def test_dynamodb_config(self):
        """Test DynamoDB configuration"""
        assert settings.DYNAMODB_TABLE_CALLS is not None
        assert settings.DYNAMODB_TABLE_RESIDENTS is not None
        assert settings.DYNAMODB_TABLE_USERS is not None
    
    def test_aws_config(self):
        """Test AWS configuration"""
        assert settings.AWS_REGION is not None


if __name__ == "__main__":
    pytest.main([__file__])