# UAV-Satellite Event Analysis - Deployment Guide

## 🚀 Quick Deployment (5 Minutes)

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 8GB RAM
- 20GB disk space

### One-Command Deploy

```bash
git clone <your-repo-url>
cd EVENT
./scripts/init.sh
```

That's it! The system will:
1. Create environment configuration
2. Build all Docker images
3. Start infrastructure services
4. Initialize database with schema
5. Seed sample data (90 tiles, 10 UAVs)
6. Start all application services

### Access Services

After initialization completes (~3-5 minutes):

- **API Documentation**: http://localhost:8000/docs
- **Dashboard**: http://localhost:3000  
- **MinIO Console**: http://localhost:9001 (admin/adminpassword)

## 📋 Detailed Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/lenchoajema/EVENT.git
cd EVENT
```

### Step 2: Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env if needed (optional)
nano .env
```

Key variables:
- `POSTGRES_PASSWORD` - Database password
- `MINIO_ROOT_PASSWORD` - MinIO admin password
- `UAV_COUNT` - Number of simulated UAVs
- `MQTT_BROKER` - MQTT broker hostname

### Step 3: Download AI Model (Optional)

For production use, download actual YOLOv8 model:

```bash
# Install ultralytics
pip install ultralytics

# Export to ONNX
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt').export(format='onnx')"

# Move to models directory
mv yolov8n.onnx models/
```

For testing, the system will use mock inference.

### Step 4: Build Services

```bash
docker-compose build
```

This builds:
- API service (FastAPI)
- Scheduler worker (Celery)
- UAV simulator
- Edge inference
- Detection stub
- Dashboard (React)

### Step 5: Start Infrastructure

```bash
# Start database, cache, and messaging
docker-compose up -d postgres redis mosquitto minio

# Wait for services to be healthy (30 seconds)
docker-compose ps
```

### Step 6: Initialize Database

```bash
# Database schema is auto-loaded via init script
# Verify it worked:
docker-compose exec postgres psql -U mvp -d mvp -c "\dt"
```

You should see tables: tiles, uavs, missions, sat_alerts, detections, etc.

### Step 7: Seed Data

```bash
# Seed tiles and UAVs
docker-compose exec api python /app/seed_tiles.py
```

This creates:
- 10 areas of interest (border zones, forests, deserts)
- ~90 geographic tiles
- 10 simulated UAVs

### Step 8: Start Application Services

```bash
docker-compose up -d
```

### Step 9: Verify Deployment

```bash
# Check all services are running
docker-compose ps

# Check API health
curl http://localhost:8000/health

# Check system stats
curl http://localhost:8000/api/v1/stats | jq
```

## 🎮 Run Demo

```bash
./scripts/demo.sh
```

This will:
1. Post 3 satellite alerts (SAR scenario)
2. Trigger UAV assignments
3. Show mission status

Watch the dashboard at http://localhost:3000

## 🧪 Generate Test Alerts

```bash
# Search and rescue scenario (10 alerts)
./scripts/generate_alerts.sh sar 10

# Border surveillance (5 alerts)
./scripts/generate_alerts.sh border 5

# Wildfire detection (3 alerts)
./scripts/generate_alerts.sh fire 3

# Mixed scenarios (20 alerts)
./scripts/generate_alerts.sh mixed 20
```

## 📊 Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f scheduler
docker-compose logs -f uav_sim
docker-compose logs -f edge_infer
```

### Database Access

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U mvp -d mvp

# Example queries
SELECT COUNT(*) FROM tiles;
SELECT * FROM uavs;
SELECT * FROM missions ORDER BY created_at DESC LIMIT 10;
SELECT * FROM sat_alerts WHERE status = 'new';
```

### Redis Monitoring

```bash
# Connect to Redis CLI
docker-compose exec redis redis-cli

# Check queue status
KEYS *
LLEN celery
```

### MQTT Monitoring

```bash
# Subscribe to all topics
docker-compose exec mosquitto mosquitto_sub -t '#' -v

# Subscribe to telemetry
docker-compose exec mosquitto mosquitto_sub -t 'telemetry/#' -v

# Subscribe to commands
docker-compose exec mosquitto mosquitto_sub -t 'commands/#' -v
```

## 🔧 Configuration

### Scale UAV Count

Edit `.env`:
```bash
UAV_COUNT=20
```

Restart UAV simulator:
```bash
docker-compose restart uav_sim
```

### Adjust Scheduler Parameters

Edit `.env`:
```bash
# Cost function weights
SCHEDULER_COST_ALPHA=1.5    # Travel time weight
SCHEDULER_COST_BETA=0.8     # Battery weight
SCHEDULER_COST_GAMMA=2.5    # Risk weight

# Thresholds
MIN_BATTERY_THRESHOLD=25.0  # Minimum battery %
```

Restart scheduler:
```bash
docker-compose restart scheduler scheduler_beat
```

### Enable Debug Mode

Edit `.env`:
```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

Restart services:
```bash
docker-compose restart api scheduler
```

## 🐛 Troubleshooting

### API Not Responding

```bash
# Check API logs
docker-compose logs api

# Check database connection
docker-compose exec api python -c "from app.database import engine; print(engine.connect())"

# Restart API
docker-compose restart api
```

### No UAVs Available

```bash
# Check UAV count in database
docker-compose exec postgres psql -U mvp -d mvp -c "SELECT COUNT(*), status FROM uavs GROUP BY status;"

# Reseed UAVs
docker-compose exec api python /app/seed_tiles.py
```

### MQTT Connection Issues

```bash
# Check MQTT broker
docker-compose logs mosquitto

# Test MQTT connectivity
docker-compose exec api python -c "
import paho.mqtt.client as mqtt
c = mqtt.Client()
c.connect('mosquitto', 1883, 60)
print('Connected!')
"
```

### Database Schema Issues

```bash
# Reinitialize database
docker-compose down -v
docker-compose up -d postgres
docker-compose exec postgres psql -U mvp -d mvp -f /docker-entrypoint-initdb.d/01_init.sql
docker-compose up -d
```

## 🔄 Updates and Maintenance

### Update Codebase

```bash
git pull
docker-compose build
docker-compose up -d
```

### Backup Database

```bash
docker-compose exec postgres pg_dump -U mvp mvp > backup_$(date +%Y%m%d).sql
```

### Restore Database

```bash
docker-compose exec -T postgres psql -U mvp -d mvp < backup_20251107.sql
```

### Clean System

```bash
# Stop all services
docker-compose down

# Remove volumes (deletes data)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Full cleanup
./scripts/cleanup.sh
```

## 🌐 Production Deployment

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml uav-event

# Check status
docker stack ps uav-event

# Scale services
docker service scale uav-event_uav_sim=5
```

### Kubernetes (Helm)

```bash
# Coming soon - Helm chart included in future release
helm repo add uav-event https://...
helm install uav-event uav-event/chart
```

### Cloud Deployment

#### AWS ECS
- Use ECS task definitions
- RDS for PostgreSQL
- ElastiCache for Redis
- IoT Core for MQTT
- S3 for evidence storage

#### Azure
- Azure Container Instances
- Azure Database for PostgreSQL
- Azure Cache for Redis
- Azure IoT Hub
- Azure Blob Storage

#### GCP
- Google Cloud Run
- Cloud SQL
- Memorystore
- Cloud IoT Core
- Cloud Storage

## 📈 Performance Tuning

### Database Optimization

```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM missions WHERE status = 'active';

-- Rebuild indexes
REINDEX TABLE missions;

-- Vacuum database
VACUUM ANALYZE;
```

### Redis Tuning

Edit `docker-compose.yml`:
```yaml
redis:
  command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
```

### API Scaling

```bash
# Increase worker count
docker-compose up -d --scale api=3
```

### Scheduler Concurrency

Edit `.env`:
```bash
CELERY_WORKERS=8
```

## 🔐 Security Hardening

### 1. Enable MQTT Authentication

Edit `infra/mosquitto/mosquitto.conf`:
```conf
allow_anonymous false
password_file /mosquitto/config/passwd
```

Create password file:
```bash
docker-compose exec mosquitto mosquitto_passwd -c /mosquitto/config/passwd admin
```

### 2. Enable SSL/TLS

Generate certificates:
```bash
openssl req -new -x509 -days 365 -extensions v3_ca -keyout ca.key -out ca.crt
```

### 3. API Authentication

Add to `services/api/app/main.py`:
```python
from fastapi.security import HTTPBearer
security = HTTPBearer()
```

### 4. Network Isolation

Edit `docker-compose.yml`:
```yaml
networks:
  frontend:
  backend:
```

## 📞 Support

- **Documentation**: See README.md
- **Issues**: https://github.com/lenchoajema/EVENT/issues
- **Discussions**: https://github.com/lenchoajema/EVENT/discussions

---

**Deployment Status**: ✅ Production Ready

**Last Updated**: November 7, 2025
