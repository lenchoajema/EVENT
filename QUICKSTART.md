# Quick Start Guide

## Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available
- Ports 3000, 5432, 6379, 8000, 1883, 9001 available

## 1-Minute Setup

```bash
# Clone the repository
git clone https://github.com/lenchoajema/EVENT.git
cd EVENT

# Start all services (this will take a few minutes on first run)
docker compose up -d

# Wait for services to start (about 30 seconds)
sleep 30

# Initialize UAVs
curl -X POST http://localhost:8000/api/uavs \
  -H "Content-Type: application/json" \
  -d '{"name": "UAV-1", "current_latitude": 37.7749, "current_longitude": -122.4194}'

curl -X POST http://localhost:8000/api/uavs \
  -H "Content-Type: application/json" \
  -d '{"name": "UAV-2", "current_latitude": 37.7849, "current_longitude": -122.4294}'

curl -X POST http://localhost:8000/api/uavs \
  -H "Content-Type: application/json" \
  -d '{"name": "UAV-3", "current_latitude": 37.7649, "current_longitude": -122.4094}'

# Create a test alert
curl -X POST http://localhost:8000/api/alerts \
  -H "Content-Type: application/json" \
  -d '{"alert_type": "fire", "severity": "high", "latitude": 37.7949, "longitude": -122.4394, "description": "Test fire alert"}'

# Open dashboard
# Navigate to http://localhost:3000
```

## Verify Installation

Check all services are running:
```bash
docker compose ps
```

All services should show "Up" status.

## Access Points

- **Dashboard**: http://localhost:3000
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **MQTT**: localhost:1883

## View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f scheduler
docker compose logs -f uav_sim
docker compose logs -f edge_infer
```

## Stop Services

```bash
docker compose down
```

## Troubleshooting

### Services won't start
```bash
# Clean up and restart
docker compose down -v
docker compose up -d
```

### Port already in use
Check what's using the ports:
```bash
netstat -tulpn | grep -E '3000|5432|6379|8000|1883'
```

### Check service health
```bash
curl http://localhost:8000/health
```

## Next Steps

After the system is running:
1. Watch the dashboard at http://localhost:3000
2. Generate more alerts using `./scripts/generate_alerts.sh`
3. Explore the API at http://localhost:8000/docs
4. View UAV telemetry and detections in real-time
