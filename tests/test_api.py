"""
Integration tests for API endpoints.
"""

import pytest
import sys
import os
from fastapi.testclient import TestClient

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from services.api.app.main import app
    from services.api.app.auth import get_current_user
    from services.api.app.auth_models import User
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False
    pytest.skip("API module not available", allow_module_level=True)

client = TestClient(app)

# Bypass auth for tests
def mock_get_current_user():
    return User(id="test_user", username="tester", is_active=True)

app.dependency_overrides[get_current_user] = mock_get_current_user


@pytest.mark.skipif(not API_AVAILABLE, reason="API not available")
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.skipif(not API_AVAILABLE, reason="API not available")
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.skipif(not API_AVAILABLE, reason="API not available")
def test_create_alert():
    alert_data = {
        "alert_type": "fire",
        "severity": "high",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "description": "Test fire alert"
    }
    response = client.post("/api/alerts", json=alert_data)
    assert response.status_code == 200
    data = response.json()
    assert data["alert_type"] == "fire"
    assert data["severity"] == "high"

def test_get_alerts():
    response = client.get("/api/alerts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_uav():
    uav_data = {
        "name": "Test-UAV-1",
        "current_latitude": 37.7749,
        "current_longitude": -122.4194
    }
    response = client.post("/api/uavs", json=uav_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test-UAV-1"
    assert data["status"] == "idle"

def test_get_uavs():
    response = client.get("/api/uavs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_detection():
    detection_data = {
        "uav_id": 1,
        "object_class": "fire",
        "confidence": 0.95,
        "latitude": 37.7749,
        "longitude": -122.4194
    }
    response = client.post("/api/detections", json=detection_data)
    assert response.status_code == 200
    data = response.json()
    assert data["object_class"] == "fire"
    assert data["confidence"] == 0.95


def test_metrics_endpoint():
    response = client.get("/metrics")
    # Prometheus text format should be returned
    assert response.status_code == 200
    content_type = response.headers.get("content-type", "")
    assert "text/plain" in content_type
