# 🌐 EVENT System - Public Codespace Access

**Status:** ✅ All ports configured as PUBLIC  
**Date:** November 14, 2025  
**Codespace:** fluffy-fiesta-jj7rrx6x6jr5hjj5g

---

## 📍 Public Remote URLs

### Primary Services (Publicly Accessible)

| Service | URL | Status |
|---------|-----|--------|
| **API Documentation** | https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev/api/docs | ✅ 200 |
| **Dashboard** | https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-3000.app.github.dev | ✅ 200 |
| **MinIO Console** | https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-9002.app.github.dev | ✅ Live |
| **API Health** | https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev/health | ✅ 200 |

### Infrastructure Services

| Service | Local Port | Status |
|---------|-----------|--------|
| PostgreSQL + PostGIS | 5432 | ✅ Running |
| Redis Cache | 6379 | ✅ Running |
| MQTT Broker | 1883 | ✅ Running |
| MinIO S3 Storage | 9000 | ✅ Running |

---

## 🔐 Authentication

```
Username: admin
Password: Event@2025!
```

⚠️ **CHANGE IMMEDIATELY IN PRODUCTION!**

---

## 🚀 Quick Access Links

### 1. API Swagger Documentation
```
https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev/api/docs
```
- Interactive API testing
- Schema documentation
- Authentication testing

### 2. Alternative API Docs (ReDoc)
```
https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev/api/redoc
```

### 3. Mission Control Dashboard
```
https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-3000.app.github.dev
```
- Real-time mission tracking
- UAV status monitoring
- Interactive map

### 4. MinIO Storage Console
```
https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-9002.app.github.dev
```
- Evidence storage
- Model registry
- File management

---

## 📋 API Testing Examples

### Health Check
```bash
curl https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev/health
```

### Login
```bash
curl -X POST https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "admin",
    "password": "Event@2025!"
  }'
```

### List UAVs
```bash
curl https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev/api/v1/uavs \
  -H 'Authorization: Bearer {token}'
```

### List Missions
```bash
curl https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev/api/v1/missions \
  -H 'Authorization: Bearer {token}'
```

---

## 🔌 WebSocket Connections

### Real-Time Telemetry Stream
```javascript
const token = "your_jwt_token";
const ws = new WebSocket(
  'wss://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev/ws/telemetry/UAV001?token=' + token
);

ws.onmessage = (event) => {
  const telemetry = JSON.parse(event.data);
  console.log('UAV Position:', telemetry.latitude, telemetry.longitude);
};
```

### Detection Stream
```javascript
const ws = new WebSocket(
  'wss://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev/ws/detections?token=' + token
);

ws.onmessage = (event) => {
  const detection = JSON.parse(event.data);
  console.log('Detection:', detection.type, detection.confidence);
};
```

### Alert Stream
```javascript
const ws = new WebSocket(
  'wss://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev/ws/alerts?token=' + token
);

ws.onmessage = (event) => {
  const alert = JSON.parse(event.data);
  console.log('Alert:', alert.severity, alert.message);
};
```

---

## 📊 Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Codespaces                        │
│              (fluffy-fiesta-jj7rrx6x6jr5hjj5g)             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  React App      │  │  FastAPI     │  │  MinIO       │  │
│  │  Port 3000      │  │  Port 8000   │  │  Port 9002   │  │
│  │  PUBLIC ✅      │  │  PUBLIC ✅   │  │  PUBLIC ✅   │  │
│  └─────────────────┘  └──────────────┘  └──────────────┘  │
│                              ↕                              │
│  ┌────────────────────────────────────────────────────┐   │
│  │           PostgreSQL + PostGIS (5432)              │   │
│  │           Redis (6379)                            │   │
│  │           MQTT Broker (1883)                      │   │
│  └────────────────────────────────────────────────────┘   │
│                              ↕                              │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Celery Workers | UAV Sim | Edge Inference        │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         ↓↑ All services accessible via GitHub URLs ↓↑
```

---

## 🛠️ Local Development

For local testing within the container:

```bash
# API
http://localhost:8000
http://localhost:8000/api/docs

# Dashboard
http://localhost:3000

# MinIO Console
http://localhost:9002

# Database
localhost:5432

# Redis
localhost:6379

# MQTT
localhost:1883
```

---

## 📡 Port Forwarding Summary

| Port | Service | Visibility | Status |
|------|---------|-----------|--------|
| 3000 | React Dashboard | 🌐 PUBLIC | ✅ Accessible |
| 8000 | FastAPI | 🌐 PUBLIC | ✅ Accessible |
| 9002 | MinIO Console | 🌐 PUBLIC | ✅ Accessible |
| 5432 | PostgreSQL | Private | ✅ Running |
| 6379 | Redis | Private | ✅ Running |
| 1883 | MQTT | Private | ✅ Running |
| 9000 | MinIO S3 | Private | ✅ Running |

---

## ✅ Verification Checklist

- [x] All Docker containers running
- [x] API responding to health checks
- [x] Dashboard loading successfully
- [x] Database connected and seeded
- [x] Redis cache available
- [x] MQTT broker operational
- [x] MinIO storage configured
- [x] All ports publicly accessible
- [x] CORS enabled for remote access
- [x] SSL/TLS working (auto via GitHub)

---

## 🚀 Next Steps

1. **Access the API Docs:**
   - Visit: https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-8000.app.github.dev/api/docs
   - Login with: admin / Event@2025!

2. **View the Dashboard:**
   - Visit: https://fluffy-fiesta-jj7rrx6x6jr5hjj5g-3000.app.github.dev

3. **Test WebSocket Connections:**
   - Use browser DevTools Console
   - Create JWT token via login
   - Connect to WebSocket endpoints

4. **Generate Test Alerts:**
   ```bash
   docker exec event_detection_stub python main.py
   ```

---

## 📞 Support & Troubleshooting

### Service Not Responding?
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f [service]

# Restart service
docker-compose restart [service]
```

### WebSocket Connection Issues?
- Ensure JWT token is valid
- Check token in query parameter: `?token={jwt}`
- Verify WebSocket URL uses `wss://` (secure)
- Check browser console for CORS errors

### Port Access Issues?
- All ports are configured as PUBLIC
- GitHub Codespaces automatically manages SSL
- No manual firewall configuration needed

---

## 📚 Documentation References

- [SYSTEM_LIVE_STATUS.md](./SYSTEM_LIVE_STATUS.md) - Real-time system status
- [README.md](./README.md) - Complete system documentation
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture details
- [QUICKSTART.md](./QUICKSTART.md) - Quick start guide
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Troubleshooting guide

---

**System Status:** ✅ Production Ready - All Services Public  
**Last Updated:** November 14, 2025  
**Codespace:** fluffy-fiesta-jj7rrx6x6jr5hjj5g  
**Visibility:** 🌐 PUBLIC
