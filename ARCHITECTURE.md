# System Architecture

## Overview

The UAV-Satellite Event Analysis MVP is a microservices-based system designed to demonstrate autonomous drone deployment for investigating satellite-detected events.

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  React Dashboard (Port 3000)                                    │
│  - Real-time map visualization                                  │
│  - Leaflet for geospatial rendering                            │
│  - WebSocket updates (polling)                                  │
└─────────────────┬───────────────────────────────────────────────┘
                  │ HTTP REST
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI Backend (Port 8000)                                    │
│  - REST API endpoints                                           │
│  - SQLAlchemy ORM                                              │
│  - GeoAlchemy2 for spatial queries                            │
│  - MQTT publisher                                               │
└─────┬─────────────────────┬─────────────────────────────────────┘
      │                     │
      │ SQL                 │ MQTT
      ▼                     ▼
┌─────────────────┐   ┌─────────────────────────────────────┐
│  PostgreSQL     │   │  MQTT Broker (Mosquitto)            │
│  + PostGIS      │   │  - Port 1883 (MQTT)                │
│  Port 5432      │   │  - Port 9001 (WebSocket)           │
└─────────────────┘   └──────────┬──────────────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │ Scheduler    │  │ UAV Sim      │  │ Edge Infer   │
        │ (Celery)     │  │              │  │ (YOLOv8)     │
        ├──────────────┤  ├──────────────┤  ├──────────────┤
        │ - Assign UAVs│  │ - Simulates  │  │ - Object     │
        │ - Monitor    │  │   3 UAVs     │  │   detection  │
        │   battery    │  │ - MQTT sub   │  │ - MQTT sub   │
        │ - Celery Beat│  │ - Telemetry  │  │ - Stores DB  │
        └──────────────┘  └──────────────┘  └──────────────┘
              │
              │ Redis
              ▼
        ┌──────────────┐
        │  Redis       │
        │  Port 6379   │
        │  - Broker    │
        │  - Backend   │
        └──────────────┘
```

## Data Flow

### 1. Alert Creation Flow
```
User/System → API → PostgreSQL
                 ↓
                MQTT → topic: satellite/alerts
                 ↓
            Scheduler receives alert
                 ↓
         Finds nearest idle UAV
                 ↓
         Updates UAV & Alert status
                 ↓
            MQTT → topic: uav/{id}/mission
                 ↓
         UAV Sim receives mission
                 ↓
         UAV flies to target
```

### 2. Detection Flow
```
UAV reaches target
    ↓
UAV publishes detection
    ↓
MQTT → topic: detections
    ↓
Edge Infer receives
    ↓
Run YOLOv8 inference (simulated)
    ↓
Store in PostgreSQL
    ↓
Dashboard polls API
    ↓
Display on map
```

## Database Schema

### SatelliteAlert
- id (PK)
- alert_type (fire, flood, smoke, etc.)
- severity (high, medium, low)
- latitude, longitude
- location (PostGIS Point)
- status (pending, assigned, investigating, resolved)
- assigned_uav_id (FK)
- created_at

### UAV
- id (PK)
- name
- status (idle, assigned, flying, charging)
- battery_level
- current_latitude, current_longitude
- current_location (PostGIS Point)
- created_at, updated_at

### Detection
- id (PK)
- uav_id (FK)
- alert_id (FK, nullable)
- object_class
- confidence
- latitude, longitude
- location (PostGIS Point)
- image_path
- metadata
- created_at

## MQTT Topics

### Published by API
- `satellite/alerts` - New alert notifications

### Published by Scheduler
- `uav/{id}/mission` - Mission assignments
- `uav/{id}/command` - UAV commands

### Published by UAV Simulator
- `uav/{id}/status` - UAV status updates
- `uav/{id}/telemetry` - Telemetry data
- `detections` - Detection events

### Subscribed by Services
- **Scheduler**: `satellite/alerts`
- **UAV Sim**: `uav/{id}/mission`, `uav/{id}/command`
- **Edge Infer**: `detections`, `uav/+/telemetry`

## Task Scheduling

### Celery Beat Schedule
- `monitor_uav_status` - Every 30 seconds
  - Checks battery levels
  - Updates charging status
  
- `process_pending_alerts` - Every 60 seconds
  - Finds unassigned alerts
  - Assigns to nearest available UAV
  - Publishes mission commands

## Technology Stack Details

### Backend Services
- **FastAPI**: Modern async Python web framework
- **SQLAlchemy**: SQL ORM
- **GeoAlchemy2**: PostGIS spatial types
- **Pydantic**: Data validation
- **Alembic**: Database migrations (ready for use)

### Task Queue
- **Celery**: Distributed task queue
- **Redis**: Message broker and result backend
- **Celery Beat**: Periodic task scheduler

### Communication
- **MQTT (Mosquitto)**: Lightweight pub/sub messaging
- **paho-mqtt**: Python MQTT client

### ML/AI
- **Ultralytics YOLOv8**: Object detection
- **OpenCV**: Image processing

### Frontend
- **React**: UI framework
- **Leaflet**: Interactive maps
- **react-leaflet**: React bindings for Leaflet
- **Axios**: HTTP client

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **PostgreSQL + PostGIS**: Spatial database
- **GitHub Actions**: CI/CD

## Scalability Considerations

### Current MVP Limitations
- Single instance of each service
- Polling instead of WebSockets for dashboard
- Simulated UAV and camera feeds
- In-memory MQTT (no persistence)

### Production Enhancements
1. **Horizontal Scaling**
   - Multiple API instances behind load balancer
   - Celery worker pool
   - Redis cluster
   
2. **Real-time Updates**
   - WebSocket connections to dashboard
   - Server-Sent Events (SSE)
   
3. **Data Persistence**
   - MQTT message persistence
   - Time-series data for telemetry
   - Object storage for images
   
4. **Security**
   - MQTT authentication
   - API authentication/authorization
   - TLS/SSL everywhere
   - Secret management
   
5. **Monitoring**
   - Prometheus metrics
   - Grafana dashboards
   - ELK stack for logs
   - Health checks and alerts

## Network Architecture

```
External Network
    ↓
[Dashboard:3000] ← HTTP → [API:8000]
                             ↓
                    Internal Network
                      ↓      ↓      ↓
              [Postgres] [Redis] [MQTT]
                ↑       ↑      ↑      ↑
                │       │      │      │
    ┌───────────┴───────┴──────┴──────┴───────┐
    │                                          │
[Scheduler] [UAV Sim] [Edge Infer]
```

All services communicate through Docker's internal network, with only the API and Dashboard exposed externally.
