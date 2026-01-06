# UAV-Satellite Event Analysis

[![Release](https://img.shields.io/github/v/release/lenchoajema/EVENT?style=flat-square)](https://github.com/lenchoajema/EVENT/releases)
[![CI/CD Pipeline](https://github.com/lenchoajema/EVENT/actions/workflows/ci.yml/badge.svg)](https://github.com/lenchoajema/EVENT/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/lenchoajema/EVENT?style=flat-square)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-blue?style=flat-square&logo=docker)](docker-compose.yml)
[![Python](https://img.shields.io/badge/python-3.11-blue?style=flat-square&logo=python)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18-blue?style=flat-square&logo=react)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.109-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)

## 🎯 Mission

Real-time coordination of satellite imagery and UAV missions for defense, surveillance, and search-and-rescue operations using AI-powered event detection and verification.

## 🌟 Key Capabilities

- **Satellite Alert Ingestion**: Receive and process satellite detection alerts
- **Intelligent UAV Dispatch**: Automatically assign UAVs based on proximity, battery, and risk
- **Real-time Verification**: Deploy UAVs to verify events (illegal movement, people in distress, fires)
- **AI-Powered Detection**: YOLOv8-based object detection (people, vehicles, camps)
- **Geospatial Storage**: PostGIS for spatial data + MinIO for evidence storage
- **Live Dashboard**: React-based visualization with mission tracking
- **Mobile Companion App**: Field operator interface for Android/iOS (React Native)
- **MQTT Telemetry**: Real-time UAV communication and monitoring

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────┐      ┌─────────────┐
│  Satellite Data │─────▶│   FastAPI    │◀────▶│  PostGIS DB │
│     Alerts      │      │   Backend    │      │   + MinIO   │
└─────────────────┘      └──────┬───────┘      └─────────────┘
                                │
                         ┌──────▼───────┐
                         │ Redis Queue  │
                         │  + Celery    │
                         └──────┬───────┘
                                │
                    ┌───────────▼────────────┐
                    │   Scheduler Worker     │
                    │  (UAV Assignment)      │
                    └───────────┬────────────┘
                                │
                         ┌──────▼───────┐
                         │     MQTT     │
                         │   Mosquitto  │
                         └──────┬───────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
         ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
         │ UAV Sim │      │ UAV Sim │      │ UAV Sim │
         │  + Edge │      │  + Edge │      │  + Edge │
         │ Infer   │      │ Infer   │      │ Infer   │
         └─────────┘      └─────────┘      └─────────┘
```

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend API | FastAPI + PostGIS | REST services, missions, detections |
| Scheduler | Celery + Redis | Prioritized UAV dispatch & mission allocation |
| Message Bus | MQTT (Eclipse Mosquitto) | UAV telemetry and commands |
| AI Inference | YOLOv8 → ONNX | Object detection (people, vehicles) |
| Storage | PostgreSQL + PostGIS + MinIO | Spatial & evidence data |
| Dashboard | React + Leaflet | Geospatial visualization |
| CI/CD | GitHub Actions | Lint, build, test, deploy |
| Deployment | Docker Compose | Containerized environment |

## 📋 Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum
- 20GB disk space

## 🚀 Quick Start

### Option A: Use Released Version (Recommended)

#### 1. Download Release

```bash
# Download the latest release
wget https://github.com/lenchoajema/EVENT/archive/refs/tags/v1.0.0.tar.gz
tar -xzf v1.0.0.tar.gz
cd EVENT-1.0.0
```

Or clone with specific tag:

```bash
git clone --depth 1 --branch v1.0.0 https://github.com/lenchoajema/EVENT.git
cd EVENT
```

#### 2. Configure Environment

```bash
# Create environment file
cp .env.example .env

# Optional: Edit .env for custom settings
# nano .env
```

#### 3. Pull Pre-built Images (Faster)

```bash
# Pull images from GitHub Container Registry
docker-compose pull

# Or use the convenience script
./scripts/pull_release_images.sh
```

#### 4. Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api dashboard
```

#### 5. Initialize and Run Demo

```bash
# Wait for services to be healthy (~30s)
./scripts/init.sh

# Generate sample satellite alerts
./scripts/demo_live.sh
```

### Option B: Build from Source

#### 1. Clone Repository

```bash
git clone https://github.com/lenchoajema/EVENT.git
cd EVENT
cp .env.example .env
```

#### 2. Build and Start Services

```bash
# Build all containers
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

#### 3. Initialize Database

```bash
# Wait for services to be healthy
./scripts/init.sh
```

### 4. Run Demo

```bash
# Generate sample satellite alerts and watch the system work
./scripts/demo.sh
```

### 5. Access Services

- **API Documentation**: http://localhost:8000/docs
- **Dashboard**: http://localhost:3000
- **MQTT Broker**: localhost:1883
- **MinIO Console**: http://localhost:9001 (admin/adminpassword)

## 📡 API Endpoints

### Satellite Alerts

```bash
POST /api/v1/sat/alerts
```

Receive satellite detection alerts

```json
{
  "tile_id": "TILE_001",
  "priority": "high",
  "event_type": "person_detected",
  "confidence": 0.89,
  "bbox": [12.3, 42.7, 12.4, 42.8]
}
```

### Missions

```bash
GET  /api/v1/missions
POST /api/v1/uav/sortie
GET  /api/v1/missions/{mission_id}
```

### Detections

```bash
POST /api/v1/detections
GET  /api/v1/detections?tile_id=TILE_001
```

### Tiles

```bash
GET  /api/v1/tiles
GET  /api/v1/tiles/{tile_id}
```

## 🤖 UAV Mission Workflow

1. **Satellite Alert** → System receives detection from satellite
2. **Priority Queue** → Alert added to Redis with priority score
3. **Scheduler Worker** → Celery task picks highest priority tile
4. **UAV Selection** → Finds nearest available UAV using Haversine distance
5. **Mission Assignment** → Publishes MQTT command to UAV
6. **Flight Execution** → UAV navigates to waypoints
7. **Edge Inference** → YOLOv8 processes frames on-board
8. **Detection Upload** → Results sent to API via REST
9. **Evidence Storage** → Images stored in MinIO, metadata in PostGIS

### Cost Function

The scheduler uses a weighted cost function:

$$cost = \alpha \times travel\_time + \beta \times (1 - battery) + \gamma \times risk$$

Where:
- α = travel time weight (1.0)
- β = battery weight (0.5)
- γ = risk weight (2.0)

## 🧪 Testing

```bash
# Unit tests
pytest tests/unit/

# Integration tests
./tests/integration_test.sh

# API tests
pytest tests/test_api.py -v

# Scheduler tests
pytest tests/test_scheduler.py -v
```

## 📊 MQTT Topics

| Topic | Direction | Purpose |
|-------|-----------|---------|
| `telemetry/{uav_id}` | UAV → System | Position, battery, status |
| `commands/{uav_id}` | System → UAV | Mission waypoints, RTL |
| `detections/{uav_id}` | UAV → System | AI detection events |

## 🔧 Configuration

Edit `.env` file:

```bash
# Database
POSTGRES_USER=mvp
POSTGRES_PASSWORD=mvp
POSTGRES_DB=mvp
DATABASE_URL=postgresql://mvp:mvp@postgres:5432/mvp

# Redis
REDIS_URL=redis://redis:6379/0

# MQTT
MQTT_BROKER=mosquitto
MQTT_PORT=1883

# MinIO
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=adminpassword
MINIO_ENDPOINT=minio:9000

# API
API_HOST=0.0.0.0
API_PORT=8000
```


## 🎮 Demo Scenarios

### Scenario 1: Search and Rescue

```bash
./scripts/generate_alerts.sh --scenario sar
```

Simulates person detected in remote forest area.

### Scenario 2: Border Surveillance

```bash
./scripts/generate_alerts.sh --scenario border
```

Simulates unauthorized vehicle movement.

### Scenario 3: Wildfire Detection

```bash
./scripts/generate_alerts.sh --scenario fire
```

Simulates thermal anomaly detection.

## 📦 Project Structure

```
EVENT/
├── docker-compose.yml           # Multi-service orchestration
├── .env.example                 # Environment template
├── services/
│   ├── api/                     # FastAPI backend
│   │   ├── app/
│   │   │   ├── main.py         # API routes
│   │   │   ├── models.py       # SQLAlchemy models
│   │   │   ├── schemas.py      # Pydantic schemas
│   │   │   ├── database.py     # DB connection
│   │   │   └── mqtt_client.py  # MQTT integration
│   │   └── Dockerfile
│   ├── scheduler/               # Celery worker
│   │   ├── app/
│   │   │   ├── celery_app.py   # Celery config
│   │   │   └── tasks.py        # Mission assignment
│   │   └── Dockerfile
│   ├── uav_sim/                 # UAV flight simulator
│   │   ├── main.py
│   │   └── Dockerfile
│   ├── edge_infer/              # YOLOv8 inference
│   │   ├── main.py
│   │   └── models/
│   ├── detection_stub/          # Satellite alert generator
│   │   ├── main.py
│   │   └── Dockerfile
│   └── dashboard/               # React UI
│       └── src/
├── infra/
│   ├── init_postgis.sql        # Database schema
│   ├── seed_tiles.py           # Initial data
│   └── mosquitto/
│       └── mosquitto.conf      # MQTT config
├── models/
│   ├── yolo_model.onnx         # AI model
│   └── model_registry.yaml     # Model metadata
├── scripts/
│   ├── init.sh                 # Setup script
│   ├── demo.sh                 # Demo runner
│   └── generate_alerts.sh      # Alert simulator
├── tests/
│   ├── test_api.py
│   └── test_scheduler.py
└── .github/
    └── workflows/
        └── ci.yml              # CI/CD pipeline
```

## 🌐 Deployment

### Local Development

```bash
docker-compose up -d
```

### Production (Kubernetes)

```bash
# Coming soon: Helm charts for K8s deployment
helm install uav-event-analysis ./charts/
```

## 🔐 Security Considerations

- [ ] Enable MQTT authentication (TLS/SSL)
- [ ] Add API key authentication to FastAPI
- [ ] Implement rate limiting
- [ ] Use secrets management (HashiCorp Vault)
- [ ] Enable network policies in K8s
- [ ] Implement OPA for Rules of Engagement

## 📈 Performance Metrics

- **Alert Processing**: < 500ms
- **UAV Assignment**: < 2 seconds
- **Detection Latency**: < 1 second
- **Mission Throughput**: 100+ missions/hour
- **Concurrent UAVs**: 50+

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

MIT License - See LICENSE file

## 🆘 Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues.

## 📚 Additional Documentation

- [Architecture Details](ARCHITECTURE.md)
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md)
- [Quick Start Guide](QUICKSTART.md)
- [Verification Checklist](VERIFICATION_CHECKLIST.md)

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review demo scripts for examples
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

1. **Start the system**: `docker compose up -d`
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
