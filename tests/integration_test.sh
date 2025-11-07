#!/bin/bash

# Integration test script
# This script tests the full system workflow

set -e

API_URL="http://localhost:8000"
DASHBOARD_URL="http://localhost:3000"

echo "Starting integration tests..."

# Test 1: Check API health
echo "Test 1: Checking API health..."
response=$(curl -s -o /dev/null -w "%{http_code}" $API_URL/health)
if [ $response -eq 200 ]; then
    echo "✓ API health check passed"
else
    echo "✗ API health check failed (HTTP $response)"
    exit 1
fi

# Test 2: Create a UAV
echo "Test 2: Creating a UAV..."
response=$(curl -s -X POST $API_URL/api/uavs \
    -H "Content-Type: application/json" \
    -d '{"name": "Test-UAV", "current_latitude": 37.7749, "current_longitude": -122.4194}')
uav_id=$(echo $response | grep -o '"id":[0-9]*' | grep -o '[0-9]*' | head -1)
if [ ! -z "$uav_id" ]; then
    echo "✓ UAV created with ID: $uav_id"
else
    echo "✗ Failed to create UAV"
    exit 1
fi

# Test 3: Create an alert
echo "Test 3: Creating a satellite alert..."
response=$(curl -s -X POST $API_URL/api/alerts \
    -H "Content-Type: application/json" \
    -d '{"alert_type": "fire", "severity": "high", "latitude": 37.7849, "longitude": -122.4294, "description": "Test alert"}')
alert_id=$(echo $response | grep -o '"id":[0-9]*' | grep -o '[0-9]*' | head -1)
if [ ! -z "$alert_id" ]; then
    echo "✓ Alert created with ID: $alert_id"
else
    echo "✗ Failed to create alert"
    exit 1
fi

# Test 4: Get all alerts
echo "Test 4: Retrieving all alerts..."
response=$(curl -s $API_URL/api/alerts)
if echo $response | grep -q "alert_type"; then
    echo "✓ Retrieved alerts successfully"
else
    echo "✗ Failed to retrieve alerts"
    exit 1
fi

# Test 5: Get all UAVs
echo "Test 5: Retrieving all UAVs..."
response=$(curl -s $API_URL/api/uavs)
if echo $response | grep -q "name"; then
    echo "✓ Retrieved UAVs successfully"
else
    echo "✗ Failed to retrieve UAVs"
    exit 1
fi

# Test 6: Create a detection
echo "Test 6: Creating a detection..."
response=$(curl -s -X POST $API_URL/api/detections \
    -H "Content-Type: application/json" \
    -d "{\"uav_id\": $uav_id, \"alert_id\": $alert_id, \"object_class\": \"fire\", \"confidence\": 0.95, \"latitude\": 37.7849, \"longitude\": -122.4294}")
detection_id=$(echo $response | grep -o '"id":[0-9]*' | grep -o '[0-9]*' | head -1)
if [ ! -z "$detection_id" ]; then
    echo "✓ Detection created with ID: $detection_id"
else
    echo "✗ Failed to create detection"
    exit 1
fi

# Test 7: Check dashboard availability
echo "Test 7: Checking dashboard availability..."
response=$(curl -s -o /dev/null -w "%{http_code}" $DASHBOARD_URL)
if [ $response -eq 200 ]; then
    echo "✓ Dashboard is accessible"
else
    echo "⚠ Dashboard returned HTTP $response (may still be starting)"
fi

echo ""
echo "All integration tests passed! ✓"
