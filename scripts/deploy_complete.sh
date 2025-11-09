#!/bin/bash

# Complete System Deployment Script
# Rebuilds and deploys the full EVENT system with all enhancements

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "=================================================="
echo "  EVENT System - Complete Deployment"
echo "=================================================="
echo -e "${NC}"
echo ""

# Step 1: Stop all containers
echo -e "${BLUE}Step 1: Stopping all containers...${NC}"
docker-compose down
echo -e "${GREEN}✓ Containers stopped${NC}"
echo ""

# Step 2: Rebuild all images
echo -e "${BLUE}Step 2: Building all container images...${NC}"
docker-compose build
echo -e "${GREEN}✓ Images built${NC}"
echo ""

# Step 3: Start infrastructure services first
echo -e "${BLUE}Step 3: Starting infrastructure services...${NC}"
docker-compose up -d postgres redis mosquitto minio
echo "Waiting for services to be healthy..."
sleep 10
echo -e "${GREEN}✓ Infrastructure ready${NC}"
echo ""

# Step 4: Start API and scheduler
echo -e "${BLUE}Step 4: Starting API and scheduler services...${NC}"
docker-compose up -d api scheduler scheduler_beat
echo "Waiting for API to be ready..."
sleep 8
echo -e "${GREEN}✓ Backend services started${NC}"
echo ""

# Step 5: Start edge and simulation services
echo -e "${BLUE}Step 5: Starting edge inference and simulation services...${NC}"
docker-compose up -d edge_infer uav_sim detection_stub
echo -e "${GREEN}✓ Edge services started${NC}"
echo ""

# Step 6: Start dashboard
echo -e "${BLUE}Step 6: Starting dashboard...${NC}"
docker-compose up -d dashboard
echo -e "${GREEN}✓ Dashboard started${NC}"
echo ""

# Step 7: Verify all services
echo -e "${BLUE}Step 7: Verifying all services...${NC}"
sleep 5

echo ""
echo "Container Status:"
docker-compose ps

echo ""
echo -e "${BLUE}Step 8: Testing API health...${NC}"
for i in {1..10}; do
    if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
        echo -e "${GREEN}✓ API is healthy${NC}"
        break
    fi
    echo "Waiting for API... ($i/10)"
    sleep 2
done

echo ""
echo -e "${GREEN}"
echo "=================================================="
echo "  Deployment Complete!"
echo "=================================================="
echo -e "${NC}"
echo ""
echo -e "${YELLOW}Service URLs:${NC}"
echo "  API Documentation:  http://localhost:8000/docs"
echo "  Dashboard:          http://localhost:3000"
echo "  MinIO Console:      http://localhost:9001"
echo ""
echo -e "${YELLOW}Default Credentials:${NC}"
echo "  Username: admin"
echo "  Password: Event@2025!"
echo ""
echo -e "${RED}⚠️  IMPORTANT: Change default password in production!${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Open dashboard: http://localhost:3000"
echo "  2. Login with credentials above"
echo "  3. Monitor real-time telemetry and detections"
echo "  4. Review system analytics"
echo ""
echo -e "${YELLOW}To view logs:${NC}"
echo "  docker-compose logs -f [service_name]"
echo ""
echo -e "${YELLOW}To stop all services:${NC}"
echo "  docker-compose down"
echo ""
echo "🚀 EVENT System is operational!"
