# EVENT System - Quick Reference Card

## 🚀 System Access

### Web Interfaces
```
API Documentation: http://localhost:8000/api/docs
Dashboard:         http://localhost:3000
MinIO Console:     http://localhost:9001
```

### Default Credentials
```
Username: admin
Password: Event@2025!
⚠️  Change immediately in production!
```

## 📡 Key API Endpoints

### Authentication
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"Event@2025!"}'

# Setup MFA
curl -X POST http://localhost:8000/api/auth/mfa/setup \
  -H 'Authorization: Bearer {token}'

# Refresh Token
curl -X POST http://localhost:8000/api/auth/refresh \
  -H 'Content-Type: application/json' \
  -d '{"refresh_token":"{refresh_token}"}'
```

### UAVs
```bash
# List all UAVs
curl -H 'Authorization: Bearer {token}' \
  http://localhost:8000/api/v1/uavs

# Get UAV telemetry
curl -H 'Authorization: Bearer {token}' \
  http://localhost:8000/api/v2/uavs/{uav_id}/telemetry

# Get UAV performance
curl -H 'Authorization: Bearer {token}' \
  http://localhost:8000/api/v2/uavs/{uav_id}/performance
```

### Missions
```bash
# List missions
curl -H 'Authorization: Bearer {token}' \
  http://localhost:8000/api/v1/missions

# Create mission
curl -X POST http://localhost:8000/api/v1/missions \
  -H 'Authorization: Bearer {token}' \
  -H 'Content-Type: application/json' \
  -d '{"uav_id":"UAV001","target_lat":37.7749,"target_lon":-122.4194}'

# Plan path
curl -X POST http://localhost:8000/api/v2/missions/{mission_id}/plan-path \
  -H 'Authorization: Bearer {token}' \
  -H 'Content-Type: application/json' \
  -d '{"algorithm":"astar","avoid_obstacles":true}'
```

### Analytics
```bash
# Performance metrics
curl -H 'Authorization: Bearer {token}' \
  http://localhost:8000/api/v2/analytics/performance

# Coverage analysis
curl -H 'Authorization: Bearer {token}' \
  http://localhost:8000/api/v2/analytics/coverage

# Response times
curl -H 'Authorization: Bearer {token}' \
  http://localhost:8000/api/v2/analytics/response-times
```

## 🔌 WebSocket Connections

### Telemetry Stream
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/telemetry/UAV001?token={jwt_token}');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Telemetry:', data);
};
```

### Detection Stream
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/detections?token={jwt_token}');
ws.onmessage = (event) => {
  const detection = JSON.parse(event.data);
  console.log('Detection:', detection);
};
```

### Alert Stream
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/alerts?token={jwt_token}');
ws.onmessage = (event) => {
  const alert = JSON.parse(event.data);
  console.log('Alert:', alert);
};
```

## 🐳 Docker Commands

### Start/Stop System
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart api

# View logs
docker-compose logs -f api
docker-compose logs -f dashboard
```

### Service Management
```bash
# Check status
docker-compose ps

# Rebuild service
docker-compose build api
docker-compose up -d api

# Scale workers (if needed)
docker-compose up -d --scale scheduler=3
```

### Database Operations
```bash
# Connect to PostgreSQL
docker exec -it event_postgres psql -U event_user -d event_db

# Database backup
docker exec event_postgres pg_dump -U event_user event_db > backup.sql

# Restore database
cat backup.sql | docker exec -i event_postgres psql -U event_user -d event_db
```

## 🛠️ Useful Scripts

### Deployment
```bash
# Complete deployment
./scripts/deploy_complete.sh

# Rebuild API only
./scripts/rebuild_api.sh

# Initialize enhanced features
./scripts/build_enhanced.sh

# System status check
./scripts/system_status.sh
```

### Python Utilities
```bash
# Run inside API container
docker exec -it event_api python3

# Test database connection
docker exec event_api python3 -c "from app.database import engine; engine.connect(); print('✓ Connected')"

# Query users
docker exec event_api python3 -c "from app.database import get_db; from app.auth_models import User; db = next(get_db()); print(db.query(User).count())"
```

## 📊 System Architecture

### Services Overview
```
Frontend:       React Dashboard (Port 3000)
API:            FastAPI Backend (Port 8000)
Database:       PostgreSQL + PostGIS (Port 5432)
Cache:          Redis (Port 6379)
Messaging:      MQTT Mosquitto (Port 1883)
Storage:        MinIO (S3) (Port 9000, Console 9001)
Scheduler:      Celery (Background tasks)
Edge:           Edge Inference Service
Simulation:     UAV Simulator + Detection Stub
```

### Data Flow
```
1. Satellite → Alert → API → Mission Assignment
2. UAV → Telemetry → MQTT → API → WebSocket → Dashboard
3. UAV → Images → Detection → API → Storage (MinIO)
4. API → Database (PostgreSQL) → Analytics
5. Scheduler (Celery) → Background Tasks → Notifications
```

## 🔐 Security Features

### JWT Token Structure
```
Access Token:  15 minutes expiry, RS256 signed
Refresh Token: 7 days expiry, rotation on use
```

### RBAC Roles
```
viewer:     Read-only access to all resources
operator:   Create missions, view detections
supervisor: Manage UAVs, users, missions
admin:      Full system access, configuration
```

### Rate Limits
```
General endpoints:  100 req/min
Auth endpoints:     10 req/min
Telemetry streams:  1000 req/min
```

## 📈 Monitoring

### Health Checks
```bash
# API health
curl http://localhost:8000/health

# Database health
docker exec event_postgres pg_isready

# Redis health
docker exec event_redis redis-cli ping

# MQTT health  
docker exec event_mosquitto mosquitto_sub -t 'test' -C 1 -W 1
```

### Metrics
```bash
# Prometheus metrics
curl http://localhost:8000/metrics

# System statistics
curl -H 'Authorization: Bearer {token}' \
  http://localhost:8000/api/v1/stats
```

## 🐛 Troubleshooting

### Common Issues

**API not responding**
```bash
docker logs event_api --tail 50
docker restart event_api
```

**Database connection errors**
```bash
docker logs event_postgres --tail 50
docker exec event_postgres pg_isready
```

**WebSocket not connecting**
- Check JWT token validity
- Verify token in query param: `?token={jwt}`
- Check CORS settings if from browser

**Authentication failing**
```bash
# Reset admin password
docker exec -it event_api python3
>>> from app.database import get_db
>>> from app.auth_models import User
>>> from app.auth import hash_password
>>> db = next(get_db())
>>> user = db.query(User).filter(User.username=="admin").first()
>>> user.password_hash = hash_password("Event@2025!")
>>> db.commit()
```

### Log Locations
```
API logs:       docker logs event_api
Scheduler logs: docker logs event_scheduler
Database logs:  docker logs event_postgres
Dashboard logs: docker logs event_dashboard
```

## 📚 Documentation

### Full Documentation
```
FULL_SYSTEM_COMPLETE.md     - Complete implementation summary
IMPLEMENTATION_COMPLETE.md  - Technical implementation details
SECTIONS_0-11.md           - System architecture & design
APPENDICES_A-D.md          - Algorithms, data, API, security specs
```

### Code Documentation
```
API Docs:       http://localhost:8000/api/docs
ReDoc:          http://localhost:8000/api/redoc
OpenAPI JSON:   http://localhost:8000/openapi.json
```

## 🎯 Quick Tasks

### Add New User
```python
docker exec -it event_api python3
>>> from app.database import get_db
>>> from app.auth_models import User, Role
>>> from app.auth import hash_password
>>> db = next(get_db())
>>> user = User(
...     username="operator1",
...     email="operator1@event.local",
...     password_hash=hash_password("SecurePass123!"),
...     full_name="Operator One",
...     is_active=True
... )
>>> db.add(user)
>>> operator_role = db.query(Role).filter(Role.name=="operator").first()
>>> user.roles.append(operator_role)
>>> db.commit()
```

### Register New UAV
```bash
curl -X POST http://localhost:8000/api/v1/uavs \
  -H 'Authorization: Bearer {token}' \
  -H 'Content-Type: application/json' \
  -d '{
    "uav_id": "UAV005",
    "model": "Quadcopter-X1",
    "capabilities": ["camera", "thermal"],
    "max_speed": 20.0,
    "max_altitude": 500.0,
    "battery_capacity": 5000
  }'
```

### Create Geofence Zone
```bash
curl -X POST http://localhost:8000/api/v2/zones \
  -H 'Authorization: Bearer {token}' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "RestrictedArea",
    "center_lat": 37.7749,
    "center_lon": -122.4194,
    "radius_m": 5000,
    "monitoring_enabled": true,
    "alert_on_entry": true
  }'
```

## 🔧 Advanced Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://event_user:event_pass@postgres:5432/event_db

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=RS256
ACCESS_TOKEN_EXPIRE_MINUTES=15

# S3/MinIO
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
S3_ENDPOINT=http://minio:9000
MODEL_BUCKET=event-models

# MQTT
MQTT_BROKER=mosquitto
MQTT_PORT=1883

# Redis
REDIS_URL=redis://redis:6379/0
```

### Performance Tuning
```yaml
# docker-compose.yml adjustments
api:
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 4G
      reservations:
        cpus: '1.0'
        memory: 2G
```

---

## 📞 Support

For issues, check:
1. System status: `./scripts/system_status.sh`
2. Service logs: `docker-compose logs -f [service]`
3. Full documentation: `FULL_SYSTEM_COMPLETE.md`

**System Version**: 2.0.0  
**Last Updated**: November 9, 2025  
**Status**: ✅ Production Ready
