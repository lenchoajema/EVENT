#!/bin/bash

# End-to-End Demo Script
# This script demonstrates the complete UAV-Satellite Event Analysis workflow

set -e

API_URL="http://localhost:8000"
DASHBOARD_URL="http://localhost:3000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}UAV-Satellite Event Analysis Demo${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Step 1: Check if services are running
echo -e "${YELLOW}Step 1: Checking system health...${NC}"
if curl -s -f $API_URL/health > /dev/null; then
    echo -e "${GREEN}✓ API is healthy${NC}"
else
    echo -e "${RED}✗ API is not accessible. Please start services with 'docker compose up -d'${NC}"
    exit 1
fi

# Step 2: Initialize UAVs
echo ""
echo -e "${YELLOW}Step 2: Initializing UAV fleet...${NC}"
for i in {1..3}; do
    # Random positions around San Francisco
    lat=$(awk -v seed=$RANDOM 'BEGIN{srand(seed); print 37.7749 + (rand() - 0.5) * 0.1}')
    lon=$(awk -v seed=$RANDOM 'BEGIN{srand(seed); print -122.4194 + (rand() - 0.5) * 0.1}')
    
    result=$(curl -s -X POST $API_URL/api/uavs \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"UAV-$i\", \"current_latitude\": $lat, \"current_longitude\": $lon}")
    
    uav_id=$(echo $result | grep -o '"id":[0-9]*' | grep -o '[0-9]*' | head -1)
    echo -e "${GREEN}✓ Created UAV-$i (ID: $uav_id) at [$lat, $lon]${NC}"
    sleep 0.5
done

# Step 3: Display initial state
echo ""
echo -e "${YELLOW}Step 3: Current UAV status...${NC}"
uavs=$(curl -s $API_URL/api/uavs)
echo "$uavs" | python3 -m json.tool | grep -E '(name|status|battery)' || echo "$uavs"

# Step 4: Create satellite alerts
echo ""
echo -e "${YELLOW}Step 4: Ingesting satellite alerts...${NC}"

# Alert 1: High severity fire
echo "Creating Fire Alert..."
alert1=$(curl -s -X POST $API_URL/api/alerts \
    -H "Content-Type: application/json" \
    -d '{"alert_type": "fire", "severity": "high", "latitude": 37.7849, "longitude": -122.4294, "description": "Wildfire detected in urban area"}')
alert1_id=$(echo $alert1 | grep -o '"id":[0-9]*' | grep -o '[0-9]*' | head -1)
echo -e "${GREEN}✓ Fire alert created (ID: $alert1_id)${NC}"
sleep 1

# Alert 2: Medium severity flood
echo "Creating Flood Alert..."
alert2=$(curl -s -X POST $API_URL/api/alerts \
    -H "Content-Type: application/json" \
    -d '{"alert_type": "flood", "severity": "medium", "latitude": 37.7649, "longitude": -122.4094, "description": "Flood warning in residential zone"}')
alert2_id=$(echo $alert2 | grep -o '"id":[0-9]*' | grep -o '[0-9]*' | head -1)
echo -e "${GREEN}✓ Flood alert created (ID: $alert2_id)${NC}"
sleep 1

# Alert 3: Low severity smoke
echo "Creating Smoke Alert..."
alert3=$(curl -s -X POST $API_URL/api/alerts \
    -H "Content-Type: application/json" \
    -d '{"alert_type": "smoke", "severity": "low", "latitude": 37.7949, "longitude": -122.3994, "description": "Smoke plume detected"}')
alert3_id=$(echo $alert3 | grep -o '"id":[0-9]*' | grep -o '[0-9]*' | head -1)
echo -e "${GREEN}✓ Smoke alert created (ID: $alert3_id)${NC}"

# Step 5: Wait for scheduler to assign UAVs
echo ""
echo -e "${YELLOW}Step 5: Waiting for UAV assignment (scheduler runs every 60s)...${NC}"
echo "The Celery scheduler will automatically assign UAVs to alerts."
echo "This may take up to 60 seconds..."

for i in {1..12}; do
    sleep 5
    assigned=$(curl -s "$API_URL/api/alerts" | grep -o '"status":"assigned"' | wc -l)
    if [ $assigned -gt 0 ]; then
        echo -e "${GREEN}✓ $assigned UAV(s) assigned!${NC}"
        break
    fi
    echo "  Waiting... ($((i*5))s)"
done

# Step 6: Check assignment status
echo ""
echo -e "${YELLOW}Step 6: Current alert status...${NC}"
alerts=$(curl -s $API_URL/api/alerts)
echo "$alerts" | python3 -m json.tool | grep -E '(id|alert_type|severity|status|assigned_uav_id)' || echo "$alerts"

# Step 7: Monitor UAV status
echo ""
echo -e "${YELLOW}Step 7: Monitoring UAV operations...${NC}"
echo "UAVs are now flying to investigate alerts..."
sleep 5

uavs=$(curl -s $API_URL/api/uavs)
echo "$uavs" | python3 -m json.tool | grep -E '(name|status|battery|current)' || echo "$uavs"

# Step 8: Wait for detections
echo ""
echo -e "${YELLOW}Step 8: Waiting for object detections...${NC}"
echo "As UAVs investigate, they will publish detection events."
echo "Monitoring for detections..."

for i in {1..6}; do
    sleep 5
    detections=$(curl -s "$API_URL/api/detections")
    count=$(echo "$detections" | grep -o '"id":' | wc -l)
    if [ $count -gt 0 ]; then
        echo -e "${GREEN}✓ $count detection(s) logged!${NC}"
        break
    fi
    echo "  Waiting for detections... ($((i*5))s)"
done

# Step 9: Display detections
echo ""
echo -e "${YELLOW}Step 9: Detection results...${NC}"
detections=$(curl -s $API_URL/api/detections)
if [ "$detections" != "[]" ]; then
    echo "$detections" | python3 -m json.tool | grep -E '(id|object_class|confidence|uav_id|alert_id)' || echo "$detections"
else
    echo "No detections yet. Check the dashboard for real-time updates."
fi

# Step 10: Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Demo Summary${NC}"
echo -e "${BLUE}========================================${NC}"

echo ""
echo -e "${GREEN}System Statistics:${NC}"
total_alerts=$(curl -s "$API_URL/api/alerts" | grep -o '"id":' | wc -l)
total_uavs=$(curl -s "$API_URL/api/uavs" | grep -o '"id":' | wc -l)
total_detections=$(curl -s "$API_URL/api/detections" | grep -o '"id":' | wc -l)

echo "  Total Alerts: $total_alerts"
echo "  Total UAVs: $total_uavs"
echo "  Total Detections: $total_detections"

echo ""
echo -e "${GREEN}Access Points:${NC}"
echo "  Dashboard: $DASHBOARD_URL"
echo "  API: $API_URL"
echo "  API Docs: $API_URL/docs"

echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Open the dashboard at $DASHBOARD_URL"
echo "  2. Watch UAVs move to investigate alerts in real-time"
echo "  3. Create more alerts with: ./scripts/generate_alerts.sh"
echo "  4. View logs with: docker compose logs -f"

echo ""
echo -e "${GREEN}Demo completed successfully!${NC}"
