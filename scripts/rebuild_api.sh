#!/bin/bash

# Rebuild and restart the API container with enhanced code
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Rebuilding Enhanced EVENT API ===${NC}"
echo ""

# Step 1: Stop current API container
echo -e "${BLUE}Step 1: Stopping current API container...${NC}"
docker-compose stop api
docker-compose rm -f api
echo -e "${GREEN}✓ API container stopped${NC}"
echo ""

# Step 2: Rebuild API image with new dependencies
echo -e "${BLUE}Step 2: Building enhanced API image...${NC}"
docker-compose build api
echo -e "${GREEN}✓ API image rebuilt${NC}"
echo ""

# Step 3: Start enhanced API
echo -e "${BLUE}Step 3: Starting enhanced API...${NC}"
docker-compose up -d api
sleep 5
echo -e "${GREEN}✓ API container started${NC}"
echo ""

# Step 4: Check API health
echo -e "${BLUE}Step 4: Checking API health...${NC}"
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ API is healthy and responding${NC}"
        break
    fi
    echo "Waiting for API to be ready... ($i/10)"
    sleep 2
done
echo ""

echo -e "${GREEN}=== API Rebuild Complete ===${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Run: ./scripts/build_enhanced.sh (to initialize database)"
echo "2. Test authentication: curl http://localhost:8000/docs"
echo "3. Check WebSocket: ws://localhost:8000/ws/telemetry/UAV001"
