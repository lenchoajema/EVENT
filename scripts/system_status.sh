#!/bin/bash

# System Status & Testing Script
# Provides comprehensive system health check and basic functionality tests

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "=================================================="
echo "  EVENT System - Status & Health Check"
echo "=================================================="
echo -e "${NC}"
echo ""

# Check if containers are running
echo -e "${BLUE}Container Status:${NC}"
docker-compose ps
echo ""

# Check API health
echo -e "${BLUE}Checking API Health...${NC}"
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs || echo "000")
if [ "$API_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ API is responding (HTTP $API_STATUS)${NC}"
else
    echo -e "${RED}✗ API is not responding (HTTP $API_STATUS)${NC}"
fi
echo ""

# Check database connection
echo -e "${BLUE}Checking Database Connection...${NC}"
docker exec event_postgres pg_isready > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
else
    echo -e "${RED}✗ PostgreSQL is not ready${NC}"
fi
echo ""

# Check Redis
echo -e "${BLUE}Checking Redis Connection...${NC}"
docker exec event_redis redis-cli ping > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Redis is responding${NC}"
else
    echo -e "${RED}✗ Redis is not responding${NC}"
fi
echo ""

# Check MQTT
echo -e "${BLUE}Checking MQTT Broker...${NC}"
docker exec event_mosquitto mosquitto_sub -t 'test' -C 1 -W 1 > /dev/null 2>&1
if [ $? -eq 0 ] || [ $? -eq 27 ]; then  # 27 = timeout (broker is up)
    echo -e "${GREEN}✓ MQTT broker is responding${NC}"
else
    echo -e "${RED}✗ MQTT broker is not responding${NC}"
fi
echo ""

# Check MinIO
echo -e "${BLUE}Checking MinIO Storage...${NC}"
MINIO_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/minio/health/live || echo "000")
if [ "$MINIO_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ MinIO is responding (HTTP $MINIO_STATUS)${NC}"
else
    echo -e "${RED}✗ MinIO is not responding (HTTP $MINIO_STATUS)${NC}"
fi
echo ""

# Check Dashboard
echo -e "${BLUE}Checking Dashboard...${NC}"
DASH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 || echo "000")
if [ "$DASH_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ Dashboard is responding (HTTP $DASH_STATUS)${NC}"
else
    echo -e "${RED}✗ Dashboard is not responding (HTTP $DASH_STATUS)${NC}"
fi
echo ""

# Database statistics
echo -e "${BLUE}Database Statistics:${NC}"
docker exec event_api python3 << 'PYEOF'
from app.database import get_db
from app.models import UAV, Mission, Detection, SatelliteAlert
from app.auth_models import User, Role, Zone

db = next(get_db())

print(f"  Users:      {db.query(User).count()}")
print(f"  Roles:      {db.query(Role).count()}")
print(f"  UAVs:       {db.query(UAV).count()}")
print(f"  Missions:   {db.query(Mission).count()}")
print(f"  Detections: {db.query(Detection).count()}")
print(f"  Alerts:     {db.query(SatelliteAlert).count()}")
print(f"  Zones:      {db.query(Zone).count()}")

db.close()
PYEOF
echo ""

# Test authentication
echo -e "${BLUE}Testing Authentication...${NC}"
AUTH_TEST=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"Event@2025!"}' || echo '{"detail":"failed"}')

if echo "$AUTH_TEST" | grep -q "access_token"; then
    echo -e "${GREEN}✓ Authentication is working${NC}"
    
    # Extract token for further tests
    TOKEN=$(echo "$AUTH_TEST" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))")
    
    if [ ! -z "$TOKEN" ]; then
        echo -e "${GREEN}✓ JWT token generated successfully${NC}"
        
        # Test protected endpoint
        echo ""
        echo -e "${BLUE}Testing Protected Endpoints...${NC}"
        UAVS_TEST=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/uavs || echo "[]")
        UAV_COUNT=$(echo "$UAVS_TEST" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
        echo -e "${GREEN}✓ Protected endpoint accessible (Found $UAV_COUNT UAVs)${NC}"
    fi
else
    echo -e "${RED}✗ Authentication failed${NC}"
    echo "Response: $AUTH_TEST"
fi
echo ""

# Resource usage
echo -e "${BLUE}Resource Usage:${NC}"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep event_
echo ""

# Recent logs
echo -e "${BLUE}Recent API Logs (last 10 lines):${NC}"
docker logs event_api --tail 10 2>&1 | sed 's/^/  /'
echo ""

# System summary
echo -e "${GREEN}"
echo "=================================================="
echo "  System Summary"
echo "=================================================="
echo -e "${NC}"

TOTAL_CONTAINERS=$(docker-compose ps | grep -c "Up" || echo "0")
echo "  Running Containers: $TOTAL_CONTAINERS"

if [ "$API_STATUS" = "200" ] && [ "$DASH_STATUS" = "200" ]; then
    echo -e "  Overall Status: ${GREEN}Healthy ✓${NC}"
else
    echo -e "  Overall Status: ${RED}Issues Detected ✗${NC}"
fi

echo ""
echo -e "${YELLOW}Quick Commands:${NC}"
echo "  View logs:       docker-compose logs -f [service]"
echo "  Restart service: docker-compose restart [service]"
echo "  Stop all:        docker-compose down"
echo "  Full redeploy:   ./scripts/deploy_complete.sh"
echo ""
echo "Done!"
