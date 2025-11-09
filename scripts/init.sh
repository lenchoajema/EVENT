#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================================"
echo "UAV-Satellite Event Analysis System - Initialization"
echo "============================================================"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ .env file created${NC}"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

# Create models directory and placeholder
echo -e "\n${YELLOW}Setting up models directory...${NC}"
mkdir -p models
if [ ! -f models/yolov8n.onnx ]; then
    # Create a small placeholder file
    echo "ONNX Model Placeholder - Replace with actual YOLOv8 ONNX model" > models/yolov8n.onnx
    echo -e "${YELLOW}⚠️  Placeholder model created. Download actual model for production use.${NC}"
else
    echo -e "${GREEN}✅ Model file exists${NC}"
fi

# Build all Docker images
echo -e "\n${YELLOW}Building Docker images...${NC}"
docker-compose build

# Start infrastructure services first
echo -e "\n${YELLOW}Starting infrastructure services...${NC}"
docker-compose up -d postgres redis mosquitto minio

# Wait for infrastructure to be healthy
echo -e "\n${YELLOW}Waiting for infrastructure services to be healthy...${NC}"
sleep 10

# Check PostgreSQL
echo -e "${YELLOW}Checking PostgreSQL...${NC}"
until docker-compose exec -T postgres pg_isready -U mvp -d mvp > /dev/null 2>&1; do
    echo -e "${YELLOW}Waiting for PostgreSQL...${NC}"
    sleep 2
done
echo -e "${GREEN}✅ PostgreSQL is ready${NC}"

# Check Redis
echo -e "${YELLOW}Checking Redis...${NC}"
until docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; do
    echo -e "${YELLOW}Waiting for Redis...${NC}"
    sleep 2
done
echo -e "${GREEN}✅ Redis is ready${NC}"

# Initialize database schema
echo -e "\n${YELLOW}Initializing database schema...${NC}"
docker-compose exec -T postgres psql -U mvp -d mvp -f /docker-entrypoint-initdb.d/01_init.sql > /dev/null 2>&1 || true
echo -e "${GREEN}✅ Database schema initialized${NC}"

# Start API and other services
echo -e "\n${YELLOW}Starting application services...${NC}"
docker-compose up -d

# Wait for API to be ready
echo -e "\n${YELLOW}Waiting for API to be ready...${NC}"
MAX_RETRIES=30
RETRY_COUNT=0
until curl -sf http://localhost:8000/health > /dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT+1))
    if [ $RETRY_COUNT -gt $MAX_RETRIES ]; then
        echo -e "${RED}❌ API failed to start${NC}"
        echo -e "${YELLOW}Check logs: docker-compose logs api${NC}"
        exit 1
    fi
    echo -e "${YELLOW}Waiting for API... (${RETRY_COUNT}/${MAX_RETRIES})${NC}"
    sleep 2
done
echo -e "${GREEN}✅ API is ready${NC}"

# Seed tiles and UAVs
echo -e "\n${YELLOW}Seeding initial data (tiles and UAVs)...${NC}"
docker-compose exec -T api python /app/seed_tiles.py
echo -e "${GREEN}✅ Data seeded successfully${NC}"

# Initialize MinIO bucket
echo -e "\n${YELLOW}Setting up MinIO storage...${NC}"
docker-compose exec -T -e MC_HOST_minio=http://admin:adminpassword@minio:9000 minio \
    sh -c "mc mb minio/uav-evidence 2>/dev/null || true" || true
echo -e "${GREEN}✅ MinIO bucket created${NC}"

# Display service status
echo -e "\n============================================================"
echo -e "${GREEN}✅ System initialized successfully!${NC}"
echo "============================================================"
echo ""
echo "📡 Service URLs:"
echo "   Dashboard:    http://localhost:3000"
echo "   API:          http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   MinIO Console: http://localhost:9001 (admin/adminpassword)"
echo ""
echo "📊 View Logs:"
echo "   All services: docker-compose logs -f"
echo "   API only:     docker-compose logs -f api"
echo "   UAV Sim:      docker-compose logs -f uav_sim"
echo ""
echo "🎮 Next Steps:"
echo "   1. Run demo:    ./scripts/demo.sh"
echo "   2. Generate alerts: ./scripts/generate_alerts.sh"
echo "   3. View dashboard: open http://localhost:3000"
echo ""
echo "============================================================"

