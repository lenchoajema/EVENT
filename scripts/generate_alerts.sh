#!/bin/bash

# Generate sample satellite alerts for testing

API_URL="${API_URL:-http://localhost:8000}"

echo "Generating sample satellite alerts..."

# Sample alert locations around San Francisco
ALERTS=(
    '{"alert_type": "fire", "severity": "high", "latitude": 37.7849, "longitude": -122.4294, "description": "Wildfire detected in urban area"}'
    '{"alert_type": "flood", "severity": "medium", "latitude": 37.7649, "longitude": -122.4094, "description": "Flood warning in residential zone"}'
    '{"alert_type": "smoke", "severity": "low", "latitude": 37.7549, "longitude": -122.4494, "description": "Smoke plume detected"}'
    '{"alert_type": "vehicle", "severity": "medium", "latitude": 37.7949, "longitude": -122.3994, "description": "Abandoned vehicle detected"}'
    '{"alert_type": "building_damage", "severity": "high", "latitude": 37.7749, "longitude": -122.4594, "description": "Structural damage identified"}'
)

for alert in "${ALERTS[@]}"; do
    echo "Creating alert: $alert"
    curl -X POST "$API_URL/api/alerts" \
        -H "Content-Type: application/json" \
        -d "$alert"
    echo ""
    sleep 1
done

echo "Sample alerts created successfully!"
