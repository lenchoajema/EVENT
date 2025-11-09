#!/bin/bash
# Enhanced EVENT System Build and Initialization Script

set -e

echo "=================================================="
echo "EVENT System - Full Build & Initialization"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Install enhanced API dependencies
echo -e "${BLUE}Step 1: Installing enhanced API dependencies...${NC}"
cd /workspaces/EVENT/services/api
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ API dependencies installed${NC}"
echo ""

# Step 2: Initialize database with new models via Docker container
echo -e "${BLUE}Step 2: Initializing enhanced database schema...${NC}"
docker exec event_api python3 <<EOF
from app.database import engine, Base
from app.models import *
from app.auth_models import *
print("Creating all tables...")
Base.metadata.create_all(bind=engine)
print("✓ Database schema created")
EOF
echo -e "${GREEN}✓ Database initialized${NC}"
echo ""

# Step 3: Initialize roles and admin user via Docker container
echo -e "${BLUE}Step 3: Setting up authentication system...${NC}"
docker exec event_api python3 <<EOF
from app.database import get_db
from app.auth import initialize_roles, create_default_admin

db = next(get_db())

# Initialize roles
initialize_roles(db)
print("✓ Roles initialized: viewer, operator, supervisor, admin")

# Create admin
admin = create_default_admin(
    db,
    username="admin",
    password="Event@2025!",
    email="admin@event.local"
)
print("✓ Admin user created")
print(f"   Username: admin")
print(f"   Password: Event@2025!")
print(f"   🚨 CHANGE THIS PASSWORD IMMEDIATELY IN PRODUCTION!")

db.close()
EOF
echo -e "${GREEN}✓ Authentication system ready${NC}"
echo ""

# Step 4: Create sample zones via Docker container
echo -e "${BLUE}Step 4: Creating geofence zones...${NC}"
docker exec event_api python3 <<EOF
from app.database import get_db
from app.auth_models import Zone
import secrets

db = next(get_db())

zones = [
    {
        "zone_id": f"zone_{secrets.token_hex(4)}",
        "name": "Restricted Border Zone Alpha",
        "description": "High-security border monitoring zone",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-74.01, 40.71],
                [-74.00, 40.71],
                [-74.00, 40.72],
                [-74.01, 40.72],
                [-74.01, 40.71]
            ]]
        },
        "center_lat": 40.715,
        "center_lon": -74.005,
        "area_km2": 1.2,
        "tier": "prohibited",
        "zone_type": "border",
        "priority": 10,
        "monitoring_enabled": True,
        "alert_on_entry": True
    },
    {
        "zone_id": f"zone_{secrets.token_hex(4)}",
        "name": "Infrastructure Protection Zone",
        "description": "Critical infrastructure monitoring",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-74.02, 40.70],
                [-74.01, 40.70],
                [-74.01, 40.71],
                [-74.02, 40.71],
                [-74.02, 40.70]
            ]]
        },
        "center_lat": 40.705,
        "center_lon": -74.015,
        "area_km2": 1.5,
        "tier": "restricted",
        "zone_type": "infrastructure",
        "priority": 8,
        "monitoring_enabled": True,
        "alert_on_entry": False
    },
    {
        "zone_id": f"zone_{secrets.token_hex(4)}",
        "name": "Public Surveillance Zone",
        "description": "General public area monitoring",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-74.03, 40.69],
                [-74.02, 40.69],
                [-74.02, 40.70],
                [-74.03, 40.70],
                [-74.03, 40.69]
            ]]
        },
        "center_lat": 40.695,
        "center_lon": -74.025,
        "area_km2": 2.0,
        "tier": "public",
        "zone_type": "urban",
        "priority": 5,
        "monitoring_enabled": True,
        "alert_on_entry": False
    }
]

for zone_data in zones:
    zone = Zone(**zone_data)
    db.add(zone)

db.commit()
print(f"✓ Created {len(zones)} geofence zones")

db.close()
EOF
echo -e "${GREEN}✓ Zones created${NC}"
echo ""

# Step 5: Display system information
echo -e "${BLUE}Step 5: System Information${NC}"
echo ""
echo "=================================================="
echo "EVENT System - Deployment Complete"
echo "=================================================="
echo ""
echo -e "${GREEN}✓ All components initialized successfully${NC}"
echo ""
echo "FEATURES IMPLEMENTED:"
echo "  ✓ JWT Authentication with RS256"
echo "  ✓ RBAC (4 roles: viewer, operator, supervisor, admin)"
echo "  ✓ Multi-Factor Authentication (MFA) support"
echo "  ✓ WebSocket real-time updates"
echo "  ✓ Advanced pathfinding (A*, Dubins)"
echo "  ✓ Coverage patterns (Lawnmower, Spiral, Sector)"
echo "  ✓ Kalman filter tracking"
echo "  ✓ Geofencing with tier classification"
echo "  ✓ Audit logging & security monitoring"
echo "  ✓ Encryption (AES-256)"
echo "  ✓ GDPR compliance utilities"
echo "  ✓ 40+ REST API endpoints"
echo "  ✓ MQTT message handling"
echo ""
echo "API DOCUMENTATION:"
echo "  Swagger UI:  http://localhost:8000/api/docs"
echo "  ReDoc:       http://localhost:8000/api/redoc"
echo ""
echo "DEFAULT CREDENTIALS:"
echo "  Username: admin"
echo "  Password: Event@2025!"
echo "  ${YELLOW}⚠️  CHANGE IMMEDIATELY IN PRODUCTION!${NC}"
echo ""
echo "WEBSOCKET ENDPOINT:"
echo "  ws://localhost:8000/ws"
echo ""
echo "QUICK START:"
echo "  1. Login:    curl -X POST http://localhost:8000/api/auth/login \\"
echo "               -H 'Content-Type: application/json' \\"
echo "               -d '{\"username\":\"admin\",\"password\":\"Event@2025!\"}'"
echo ""
echo "  2. Get UAVs: curl http://localhost:8000/api/v1/uavs \\"
echo "               -H 'Authorization: Bearer <token>'"
echo ""
echo "  3. View Stats: curl http://localhost:8000/api/v1/stats \\"
echo "                 -H 'Authorization: Bearer <token>'"
echo ""
echo "=================================================="
echo ""

# Done
echo -e "${GREEN}🚀 EVENT System is ready!${NC}"
echo ""
