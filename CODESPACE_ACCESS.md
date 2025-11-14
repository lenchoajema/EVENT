# EVENT System - Codespace Remote Access Guide

**Status**: ✅ All services are running and accessible remotely

## 🌐 Remote Access URLs (GitHub Codespace)

### Primary Services

| Service | Local URL | Remote URL | Port | Status |
|---------|-----------|-----------|------|--------|
| **API** | http://localhost:8000 | https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev | 8000 | ✅ Running |
| **Dashboard** | http://localhost:3000 | https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-3000.app.github.dev | 3000 | ✅ Running |
| **MinIO Console** | http://localhost:9002 | https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-9002.app.github.dev | 9002 | ✅ Running |
| **MQTT** | localhost:1883 | event_mosquitto:1883 (internal) | 1883 | ✅ Running |
| **PostgreSQL** | localhost:5432 | event_postgres:5432 (internal) | 5432 | ✅ Running |
| **Redis** | localhost:6379 | event_redis:6379 (internal) | 6379 | ✅ Running |

## 🚀 Quick Access Links

### API Documentation
- **Swagger UI**: https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev/api/docs
- **ReDoc**: https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev/api/redoc
- **OpenAPI JSON**: https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev/openapi.json

### Dashboard
- **Main Dashboard**: https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-3000.app.github.dev

### Storage Console
- **MinIO Web UI**: https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-9002.app.github.dev
  - Username: `admin`
  - Password: `adminpassword`

## 📊 Running Services Summary

```
✅ event_postgres          - PostgreSQL + PostGIS (healthy)
✅ event_redis            - Redis cache (healthy)
✅ event_mosquitto        - MQTT Broker (healthy)
✅ event_minio            - MinIO S3 storage (healthy)
✅ event_api              - FastAPI backend (running)
✅ event_scheduler        - Celery worker (running)
✅ event_scheduler_beat   - Celery beat (running)
✅ event_dashboard        - React frontend (running)
✅ event_uav_sim          - UAV simulator (running)
✅ event_edge_infer       - Edge inference (running)
```

## 🔐 Default Credentials

### API Authentication
- **Username**: admin
- **Password**: Event@2025!
- ⚠️ **Change immediately in production!**

### MinIO Access
- **Username**: admin
- **Password**: adminpassword

## 📡 API Endpoints (Examples)

### Health Check
```bash
curl https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev/health
```

### Get System Stats
```bash
curl https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev/api/v1/stats
```

### List Missions
```bash
curl -H "Authorization: Bearer {TOKEN}" \
  https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev/api/v1/missions
```

## 🌐 Codespace Information

- **Codespace Name**: fluffy-fiesta-jj7rrx6x6jr5hjj5g
- **Domain**: app.github.dev
- **User**: len-astu
- **Repository**: lenchoajema/EVENT

## 🔗 WebSocket Connections

For real-time updates from the browser:

```javascript
// Example: Connect to telemetry stream
const token = 'YOUR_JWT_TOKEN';
const wsUrl = 'wss://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev/ws';

const ws = new WebSocket(wsUrl + `?token=${token}`);

ws.onopen = () => {
  console.log('Connected to EVENT system');
  ws.send(JSON.stringify({
    type: 'subscribe',
    channel: 'telemetry'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Telemetry update:', data);
};
```

## 🐳 Docker Compose Services

All services are running in Docker containers with the following network:
- **Network**: event_event_network
- **Driver**: bridge

## 📝 Testing the System

### 1. Health Check
```bash
curl https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev/health
# Expected: {"status":"healthy"}
```

### 2. API Documentation
Visit: https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev/api/docs

### 3. Dashboard
Visit: https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-3000.app.github.dev

### 4. MinIO Console
Visit: https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-9002.app.github.dev

## 🔄 Service Logs

View logs from any service:

```bash
# API logs
docker logs -f event_api

# Dashboard logs
docker logs -f event_dashboard

# Scheduler logs
docker logs -f event_scheduler

# All services
docker-compose logs -f
```

## ⚠️ Important Notes

1. **Network Isolation**: Internal services (Postgres, Redis, MQTT) are only accessible within the Docker network
2. **HTTPS**: Codespace URLs use HTTPS automatically (secure by default)
3. **Port Forwarding**: Automatically configured by GitHub Codespaces
4. **Session Persistence**: Services run in containers and persist while Codespace is active
5. **Cost**: GitHub Codespaces has usage limits; check your account for details

## 🚀 Accessing from Different Clients

### From Browser
```
https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev
```

### From Terminal/Scripts
```bash
# Export for use in scripts
export API_URL=https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev
export DASHBOARD_URL=https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-3000.app.github.dev

curl $API_URL/health
```

### From Postman
- Base URL: `https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev`
- Import Swagger from: `https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev/openapi.json`

## 📞 Troubleshooting

### Services Not Responding
```bash
# Check all services are running
docker-compose ps

# Restart a service
docker-compose restart api
```

### Connection Timeout
- Ensure Codespace is active
- Check GitHub Codespaces quota
- Verify port forwarding is enabled

### Authentication Failed
- Default credentials: admin / Event@2025!
- Check API docs to get access token
- Ensure token is included in Authorization header

## 🎯 Next Steps

1. ✅ All services running and accessible
2. Test API endpoints at https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev/api/docs
3. Access dashboard at https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-3000.app.github.dev
4. Generate sample alerts and missions
5. Monitor real-time updates via WebSocket

---

**Last Updated**: November 14, 2025  
**Status**: ✅ All Systems Operational  
**Codespace**: fluffy-fiesta-jj7rrx6x6jr5hjj5g
