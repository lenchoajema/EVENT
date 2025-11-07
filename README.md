# UAV-Satellite Event Analysis MVP

A comprehensive system for satellite-based event detection, autonomous UAV deployment, and edge-based object detection using YOLOv8.

## System Overview

This project demonstrates a complete event analysis pipeline:

1. **Satellite Alerts**: Ingest satellite-detected events (fires, floods, etc.)
2. **UAV Assignment**: Automatically assign UAVs to investigate alerts
3. **Edge Inference**: Run YOLOv8 object detection on UAV feeds
4. **Real-time Dashboard**: Monitor alerts, UAVs, and detections on an interactive map

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│ Satellite       │────▶│   FastAPI    │────▶│  PostgreSQL │
│ Alert Ingestion │     │   Backend    │     │   PostGIS   │
└─────────────────┘     └──────────────┘     └─────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │  MQTT Broker │
                        │  (Mosquitto) │
                        └──────────────┘
                         │      │      │
          ┌──────────────┘      │      └──────────────┐
          ▼                     ▼                     ▼
   ┌─────────────┐      ┌─────────────┐      ┌──────────────┐
   │ UAV         │      │  Celery     │      │   YOLOv8     │
   │ Simulator   │      │  Scheduler  │      │    Edge      │
   │             │      │   (Redis)   │      │  Inference   │
   └─────────────┘      └─────────────┘      └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │    React     │
                        │   Dashboard  │
                        └──────────────┘
```

## Services

### 1. API Service (FastAPI + PostGIS)
- REST API for alerts, UAVs, and detections
- PostgreSQL with PostGIS for geospatial data
- MQTT integration for real-time communication

### 2. Scheduler Service (Celery + Redis)
- Automated UAV assignment to alerts
- Battery monitoring and status management
- Periodic task execution

### 3. UAV Simulator
- Simulates multiple UAV units
- MQTT-based communication
- Autonomous navigation to alert locations
- Battery simulation

### 4. Edge Inference (YOLOv8)
- Real-time object detection
- Processes UAV camera feeds
- Publishes detection events

### 5. Dashboard (React + Leaflet)
- Interactive map visualization
- Real-time updates
- Alert, UAV, and detection tracking

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/lenchoajema/EVENT.git
cd EVENT
```

2. Initialize the system:
```bash
./scripts/init.sh
```

This will:
- Create environment configuration
- Build all Docker images
- Start all services
- Initialize sample UAVs

### Access the System

- **Dashboard**: http://localhost:3000
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Generate Sample Alerts

```bash
./scripts/generate_alerts.sh
```

This creates sample satellite alerts that trigger UAV assignments.

## Manual Setup

### Start All Services

```bash
docker-compose up -d
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f uav_sim
```

### Stop Services

```bash
docker-compose down
```

### Clean Up (Remove Data)

```bash
./scripts/cleanup.sh
```

## API Usage

### Create a Satellite Alert

```bash
curl -X POST http://localhost:8000/api/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "fire",
    "severity": "high",
    "latitude": 37.7849,
    "longitude": -122.4294,
    "description": "Wildfire detected"
  }'
```

### Create a UAV

```bash
curl -X POST http://localhost:8000/api/uavs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "UAV-1",
    "current_latitude": 37.7749,
    "current_longitude": -122.4194
  }'
```

### Get All Alerts

```bash
curl http://localhost:8000/api/alerts
```

### Get All UAVs

```bash
curl http://localhost:8000/api/uavs
```

### Get All Detections

```bash
curl http://localhost:8000/api/detections
```

## Development

### Project Structure

```
EVENT/
├── services/
│   ├── api/              # FastAPI backend
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   └── database.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── scheduler/        # Celery scheduler
│   │   ├── app/
│   │   │   ├── celery_app.py
│   │   │   └── tasks.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── uav_sim/         # UAV simulator
│   │   ├── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── edge_infer/      # YOLOv8 inference
│   │   ├── main.py
│   │   ├── models/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── dashboard/       # React frontend
│       ├── src/
│       │   ├── App.js
│       │   └── index.js
│       ├── public/
│       ├── Dockerfile
│       └── package.json
├── infra/
│   └── mosquitto/
│       └── mosquitto.conf
├── scripts/
│   ├── init.sh
│   ├── generate_alerts.sh
│   └── cleanup.sh
├── tests/
│   ├── test_api.py
│   ├── test_scheduler.py
│   └── integration_test.sh
├── .github/
│   └── workflows/
│       └── ci.yml
├── docker-compose.yml
├── .gitignore
└── README.md
```

### Running Tests

```bash
# Run integration tests
./tests/integration_test.sh

# Run Python unit tests (requires dependencies installed)
cd services/api
pytest ../tests/test_api.py
```

### Environment Variables

Create a `.env` file (see `.env.example`):

```bash
DATABASE_URL=postgresql://event_user:event_pass@postgres:5432/event_db
REDIS_URL=redis://redis:6379
MQTT_BROKER=mosquitto
MQTT_PORT=1883
NUM_UAVS=3
```

## CI/CD

GitHub Actions workflow automatically:
- Lints Python and JavaScript code
- Builds all Docker images
- Runs integration tests

## Technologies Used

- **Backend**: FastAPI, SQLAlchemy, GeoAlchemy2
- **Database**: PostgreSQL with PostGIS extension
- **Task Queue**: Celery with Redis
- **Message Broker**: Eclipse Mosquitto (MQTT)
- **ML/AI**: YOLOv8 (Ultralytics)
- **Frontend**: React, Leaflet
- **Infrastructure**: Docker, Docker Compose
- **CI/CD**: GitHub Actions

## Features

✅ Real-time satellite alert ingestion  
✅ Automated UAV assignment and routing  
✅ MQTT-based communication  
✅ Edge-based object detection with YOLOv8  
✅ Interactive map dashboard  
✅ Battery management and monitoring  
✅ PostGIS geospatial queries  
✅ RESTful API with automatic documentation  
✅ Containerized deployment  
✅ CI/CD pipeline  

## Demo Workflow

1. **Start the system**: `docker-compose up -d`
2. **Generate alerts**: `./scripts/generate_alerts.sh`
3. **Watch the magic**:
   - Scheduler assigns UAVs to alerts
   - UAVs fly to target locations
   - Edge inference detects objects
   - Dashboard updates in real-time

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open a GitHub issue.
