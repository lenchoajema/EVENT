#!/bin/bash
# EVENT System - Live Demo

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

clear
echo -e "${CYAN}╔═══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   EVENT System - Live Demo & Status       ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════╝${NC}"
echo ""

# Login
echo -e "${YELLOW}Testing Authentication...${NC}"
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"Event@2025!"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ ! -z "$TOKEN" ]; then
    echo -e "  ${GREEN}✓ Authentication successful${NC}"
    
    # Get user info
    ME=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/auth/me)
    USERNAME=$(echo "$ME" | python3 -c "import sys, json; print(json.load(sys.stdin).get('username', 'N/A'))" 2>/dev/null)
    
    echo -e "  ${GREEN}✓ Logged in as: $USERNAME${NC}"
    echo ""
    
    echo -e "${YELLOW}Database Statistics:${NC}"
    docker exec event_api python3 -c "
from app.database import get_db
from app.models import UAV, Mission, Detection, SatelliteAlert
from app.auth_models import User, Role
db = next(get_db())
print(f'  Users: {db.query(User).count()}, Roles: {db.query(Role).count()}')
print(f'  UAVs: {db.query(UAV).count()}, Missions: {db.query(Mission).count()}')
print(f'  Detections: {db.query(Detection).count()}, Alerts: {db.query(SatelliteAlert).count()}')
db.close()
" 2>/dev/null
    
    echo ""
    echo -e "${GREEN}✓ System Operational!${NC}"
    echo ""
    echo -e "${YELLOW}Access URLs:${NC}"
    echo "  API:       http://localhost:8000/api/docs"
    echo "  Dashboard: http://localhost:3000"
    echo ""
    echo -e "${YELLOW}Credentials:${NC}"
    echo "  Username: admin"
    echo "  Password: Event@2025!"
else
    echo -e "  ${RED}✗ Authentication failed${NC}"
fi
