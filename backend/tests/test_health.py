"""Test Health Check Endpoint"""
import pytest
from fastapi.testclient import TestClient
from src.main import app


client = TestClient(app)


def test_health_check():
    """Test health check endpoint returns 200 with correct format"""
    response = client.get("/health")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "success"
    assert "data" in data
    assert data["data"]["status"] == "healthy"
    assert "timestamp" in data["data"]
    assert data["data"]["version"] == "1.0.0"


def test_health_check_data_structure():
    """Test health check response data structure"""
    response = client.get("/health")
    data = response.json()
    
    # Check data keys
    assert set(data.keys()) == {"code", "message", "data"}
    assert set(data["data"].keys()) == {"status", "timestamp", "version"}
