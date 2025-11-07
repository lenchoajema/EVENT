import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

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
