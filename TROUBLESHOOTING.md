# Troubleshooting Guide

## Common Issues and Solutions

### 1. Services Won't Start

#### Problem: Docker Compose fails to start services

**Solution:**
```bash
# Check Docker is running
docker ps

# View Docker Compose status
docker compose ps

# Check logs for specific service
docker compose logs api
docker compose logs postgres

# Clean restart
docker compose down -v
docker compose up -d
```

#### Problem: Port already in use

**Error:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution:**
```bash
# Find what's using the port
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill the process or change port in docker-compose.yml
```

### 2. Database Issues

#### Problem: PostgreSQL connection refused

**Solution:**
```bash
# Wait for PostgreSQL to be ready
docker compose logs postgres | grep "ready to accept connections"

# Test database connection
docker compose exec postgres psql -U event_user -d event_db -c "SELECT 1;"

# Restart PostgreSQL
docker compose restart postgres
```

#### Problem: PostGIS extension not available

**Solution:**
```bash
# Verify PostGIS is installed
docker compose exec postgres psql -U event_user -d event_db -c "SELECT PostGIS_version();"

# If missing, install (should be automatic with postgis/postgis image)
docker compose exec postgres psql -U event_user -d event_db -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

### 3. MQTT Issues

#### Problem: Services can't connect to MQTT broker

**Solution:**
```bash
# Check Mosquitto is running
docker compose logs mosquitto

# Test MQTT connection
docker compose exec mosquitto mosquitto_sub -t test -v

# In another terminal, publish a test message
docker compose exec mosquitto mosquitto_pub -t test -m "hello"

# Restart MQTT broker
docker compose restart mosquitto
```

#### Problem: MQTT messages not received

**Solution:**
- Check topic names match exactly (case-sensitive)
- Verify QoS settings
- Check Mosquitto logs for connection attempts
- Ensure clients are subscribing before messages are published

### 4. API Issues

#### Problem: API returns 500 errors

**Solution:**
```bash
# Check API logs
docker compose logs api

# Verify database connection
curl http://localhost:8000/health

# Restart API
docker compose restart api
```

#### Problem: CORS errors in dashboard

**Solution:**
- Ensure API has CORS middleware configured (already set to allow all origins in MVP)
- Check browser console for exact error
- Verify API_URL in dashboard environment

### 5. Scheduler Issues

#### Problem: UAVs not being assigned to alerts

**Solution:**
```bash
# Check scheduler is running
docker compose logs scheduler

# Check Celery beat is running
docker compose logs scheduler_beat

# Verify Redis connection
docker compose exec redis redis-cli ping

# Manually trigger task (requires Celery)
docker compose exec scheduler celery -A app.celery_app inspect active
```

#### Problem: Celery tasks failing

**Solution:**
```bash
# Check worker logs
docker compose logs scheduler

# Check Redis
docker compose logs redis

# Restart scheduler
docker compose restart scheduler scheduler_beat
```

### 6. UAV Simulator Issues

#### Problem: UAVs not moving or updating

**Solution:**
```bash
# Check UAV simulator logs
docker compose logs uav_sim

# Verify MQTT connection
docker compose logs mosquitto | grep "uav_"

# Restart UAV simulator
docker compose restart uav_sim
```

### 7. Edge Inference Issues

#### Problem: YOLOv8 model download fails

**Solution:**
```bash
# Check edge_infer logs
docker compose logs edge_infer

# Model downloads on first run - may take time
# Wait 2-3 minutes for initial download

# If download fails due to network, restart
docker compose restart edge_infer
```

#### Problem: No detections being logged

**Solution:**
- Detections are simulated with 10% probability
- Check MQTT messages are being published
- Verify database connection from edge_infer service

### 8. Dashboard Issues

#### Problem: Dashboard shows blank screen

**Solution:**
```bash
# Check dashboard logs
docker compose logs dashboard

# Verify API is accessible from dashboard container
docker compose exec dashboard curl http://api:8000/health

# Check for JavaScript errors in browser console
# Rebuild dashboard
docker compose build dashboard
docker compose restart dashboard
```

#### Problem: Map not loading

**Solution:**
- Check browser console for errors
- Verify Leaflet CSS is loaded
- Check API is returning data: `curl http://localhost:8000/api/alerts`
- Clear browser cache

#### Problem: Dashboard not updating

**Solution:**
- Dashboard polls API every 5 seconds
- Check API is responding: `curl http://localhost:8000/api/alerts`
- Check browser network tab for failed requests

### 9. Performance Issues

#### Problem: System running slowly

**Solution:**
```bash
# Check Docker resource usage
docker stats

# Increase Docker memory/CPU limits in Docker Desktop settings
# Recommended: 4GB RAM minimum

# Check individual service resources
docker compose top
```

### 10. Build Issues

#### Problem: Docker build fails

**Solution:**
```bash
# Clear Docker cache
docker compose build --no-cache

# Remove old images
docker image prune -a

# Check disk space
df -h  # Linux/Mac
```

#### Problem: npm install fails in dashboard

**Solution:**
```bash
# Build with verbose output
docker compose build --progress=plain dashboard

# Try building outside Docker first
cd services/dashboard
npm install
npm run build
```

## Debug Mode

### Enable Verbose Logging

Edit `docker-compose.yml` to add debug environment variables:

```yaml
services:
  api:
    environment:
      LOG_LEVEL: DEBUG
```

### Access Service Shells

```bash
# API service
docker compose exec api bash

# Database
docker compose exec postgres psql -U event_user -d event_db

# Redis
docker compose exec redis redis-cli

# View specific service logs with timestamps
docker compose logs -f --timestamps api
```

## Network Debugging

### Check Service Connectivity

```bash
# From API to database
docker compose exec api nc -zv postgres 5432

# From API to Redis
docker compose exec api nc -zv redis 6379

# From API to MQTT
docker compose exec api nc -zv mosquitto 1883
```

### DNS Resolution

```bash
# Check service can resolve other services
docker compose exec api nslookup postgres
docker compose exec api nslookup redis
```

## Data Issues

### Reset Database

```bash
# WARNING: This deletes all data
docker compose down -v
docker compose up -d postgres

# Wait for DB to be ready
sleep 10

# Restart API to recreate tables
docker compose restart api
```

### Backup Database

```bash
# Create backup
docker compose exec postgres pg_dump -U event_user event_db > backup.sql

# Restore backup
docker compose exec -T postgres psql -U event_user event_db < backup.sql
```

## Getting Help

If issues persist:

1. Check logs for all services: `docker compose logs`
2. Check GitHub Issues: https://github.com/lenchoajema/EVENT/issues
3. Create a new issue with:
   - Output of `docker compose ps`
   - Relevant logs from `docker compose logs [service]`
   - Steps to reproduce
   - Expected vs actual behavior

## Health Checks

Run this comprehensive health check:

```bash
#!/bin/bash
echo "Checking system health..."
echo ""

# API
curl -f http://localhost:8000/health && echo "✓ API healthy" || echo "✗ API unhealthy"

# Database
docker compose exec -T postgres pg_isready -U event_user && echo "✓ Database ready" || echo "✗ Database not ready"

# Redis
docker compose exec redis redis-cli ping | grep -q PONG && echo "✓ Redis healthy" || echo "✗ Redis unhealthy"

# MQTT
docker compose exec mosquitto mosquitto_sub -t test -C 1 -W 1 > /dev/null 2>&1 && echo "✓ MQTT healthy" || echo "✗ MQTT unhealthy"

# Dashboard
curl -f http://localhost:3000 > /dev/null 2>&1 && echo "✓ Dashboard accessible" || echo "✗ Dashboard not accessible"
```
