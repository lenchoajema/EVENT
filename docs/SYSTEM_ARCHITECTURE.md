# System Architecture Overview
## Coordinated Satellite & UAV Event-Analysis MVP

**Document Version:** 1.0  
**Date:** November 9, 2025  
**Parent Document:** [Executive Summary](./EXECUTIVE_SUMMARY.md)

---

## 1. System Architecture Overview

### 1.1 Tiered ISR Framework (Satellite → UAV → Edge → Command)

The EVENT system implements a **hierarchical Intelligence, Surveillance, and Reconnaissance (ISR)** architecture that cascades from wide-area monitoring to precision verification through four integrated tiers.

#### Tier Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│ TIER 0: SPACE LAYER (Satellite Constellation)                          │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                      │
│ │ Commercial  │  │ Government  │  │ Tasked      │                      │
│ │ Satellites  │  │ Satellites  │  │ Imaging     │                      │
│ │ (Planet,    │  │ (Sentinel,  │  │ (Maxar,     │                      │
│ │  Capella)   │  │  Landsat)   │  │  BlackSky)  │                      │
│ └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                      │
│        │                 │                 │                             │
│        └─────────────────┴─────────────────┘                             │
│                          │                                               │
│                   [Satellite Data API]                                   │
└──────────────────────────┼───────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ TIER 1: COMMAND & CONTROL LAYER (Cloud Infrastructure)                 │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  FastAPI Backend                                           │         │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │         │
│  │  │  Alert       │  │  Mission     │  │  Detection   │    │         │
│  │  │  Ingestion   │  │  Management  │  │  Aggregation │    │         │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │         │
│  │         │                  │                  │            │         │
│  │         └──────────────────┴──────────────────┘            │         │
│  │                            │                                │         │
│  └────────────────────────────┼────────────────────────────────┘         │
│                               │                                          │
│  ┌────────────────────────────┼────────────────────────────────┐         │
│  │  PostGIS Database          │                                │         │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │         │
│  │  │  Tiles   │  │  UAVs    │  │ Missions │  │Detections│   │         │
│  │  │(Geo Zones)│ │ (Fleet)  │  │ (Tasks)  │  │(Evidence)│   │         │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │         │
│  └────────────────────────────┬────────────────────────────────┘         │
│                               │                                          │
│  ┌────────────────────────────┼────────────────────────────────┐         │
│  │  Celery Task Queue (Redis)                                  │         │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │         │
│  │  │  Assignment  │  │  Monitoring  │  │   Battery    │     │         │
│  │  │   Worker     │  │   Worker     │  │    Check     │     │         │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │         │
│  └────────────────────────────┬────────────────────────────────┘         │
│                               │                                          │
│  ┌────────────────────────────┼────────────────────────────────┐         │
│  │  MQTT Broker (Mosquitto)                                    │         │
│  │  Topics: /alerts/*, /commands/*, /telemetry/*, /detections/*│         │
│  └────────────────────────────┬────────────────────────────────┘         │
│                               │                                          │
│  ┌────────────────────────────┼────────────────────────────────┐         │
│  │  MinIO Object Storage                                       │         │
│  │  Buckets: uav-evidence/ (images, videos, logs)             │         │
│  └────────────────────────────┬────────────────────────────────┘         │
│                               │                                          │
└───────────────────────────────┼──────────────────────────────────────────┘
                                │
                         [MQTT over TLS]
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ TIER 2: EDGE LAYER (UAV Swarm)                                         │
│                                                                          │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │   UAV-001    │     │   UAV-002    │ ... │   UAV-N      │            │
│  │ ┌──────────┐ │     │ ┌──────────┐ │     │ ┌──────────┐ │            │
│  │ │ Flight   │ │     │ │ Flight   │ │     │ │ Flight   │ │            │
│  │ │Controller│ │     │ │Controller│ │     │ │Controller│ │            │
│  │ └────┬─────┘ │     │ └────┬─────┘ │     │ └────┬─────┘ │            │
│  │      │       │     │      │       │     │      │       │            │
│  │ ┌────▼─────┐ │     │ ┌────▼─────┐ │     │ ┌────▼─────┐ │            │
│  │ │  MQTT    │ │     │ │  MQTT    │ │     │ │  MQTT    │ │            │
│  │ │  Client  │ │     │ │  Client  │ │     │ │  Client  │ │            │
│  │ └────┬─────┘ │     │ └────┬─────┘ │     │ └────┬─────┘ │            │
│  │      │       │     │      │       │     │      │       │            │
│  │ ┌────▼─────┐ │     │ ┌────▼─────┐ │     │ ┌────▼─────┐ │            │
│  │ │  Edge AI │ │     │ │  Edge AI │ │     │ │  Edge AI │ │            │
│  │ │ (YOLOv8) │ │     │ │ (YOLOv8) │ │     │ │ (YOLOv8) │ │            │
│  │ │ Jetson/  │ │     │ │ Jetson/  │ │     │ │ Jetson/  │ │            │
│  │ │ Intel NUC│ │     │ │ Intel NUC│ │     │ │ Intel NUC│ │            │
│  │ └────┬─────┘ │     │ └────┬─────┘ │     │ └────┬─────┘ │            │
│  │      │       │     │      │       │     │      │       │            │
│  │ ┌────▼─────┐ │     │ ┌────▼─────┐ │     │ ┌────▼─────┐ │            │
│  │ │ Cameras  │ │     │ │ Cameras  │ │     │ │ Cameras  │ │            │
│  │ │ RGB+IR+  │ │     │ │ RGB+IR+  │ │     │ │ RGB+IR+  │ │            │
│  │ │ Thermal  │ │     │ │ Thermal  │ │     │ │ Thermal  │ │            │
│  │ └──────────┘ │     │ └──────────┘ │     │ └──────────┘ │            │
│  └──────────────┘     └──────────────┘     └──────────────┘            │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ TIER 3: OPERATOR INTERFACE LAYER (Command Dashboard)                   │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  React Dashboard (Leaflet Map)                             │         │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │         │
│  │  │  Live Map    │  │  Alert Feed  │  │  UAV Status  │    │         │
│  │  │  (Detections,│  │  (Priorities,│  │  (Telemetry, │    │         │
│  │  │   UAVs,      │  │   Confidence)│  │   Battery)   │    │         │
│  │  │   Zones)     │  │              │  │              │    │         │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │         │
│  │                                                            │         │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │         │
│  │  │  Mission     │  │  Evidence    │  │  Statistics  │    │         │
│  │  │  Controls    │  │  Viewer      │  │  Dashboard   │    │         │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │         │
│  └────────────────────────────────────────────────────────────┘         │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Tier Responsibilities & Characteristics

| Tier | Component | Coverage | Resolution | Latency | Autonomous? |
|------|-----------|----------|------------|---------|-------------|
| **Tier 0** | Satellite | 1000+ km² | 0.3-5m GSD | 4-24h revisit | Semi-autonomous |
| **Tier 1** | Command Center | Global | N/A | <100ms processing | Automated |
| **Tier 2** | UAV Fleet | 10-50 km² | 5-50cm GSD | Real-time | Fully autonomous |
| **Tier 3** | Human Operators | N/A | N/A | Variable | Manual oversight |

---

### 1.2 Real-Time Tasking Flow (Detection → Verification → Intercept)

The EVENT system orchestrates a **5-stage automated workflow** from initial satellite detection to field response, with human-in-the-loop checkpoints at critical decision nodes.

#### Stage-by-Stage Workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: SATELLITE DETECTION                                           │
│ Trigger: Scheduled satellite pass over AOI                             │
│ Duration: 2-5 minutes (image capture)                                   │
└─────────────────────┬───────────────────────────────────────────────────┘
                      │
                      ▼
              [Image Processing]
                      │
                      ▼
            {Anomaly Detected?}────NO────▶ [Log & Archive]
                      │
                     YES
                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 2: ALERT INGESTION & PRIORITIZATION                              │
│ Trigger: POST /api/v1/sat/alerts                                       │
│ Duration: <500ms                                                        │
│                                                                          │
│ Process:                                                                │
│ 1. Validate alert schema (coordinates, type, confidence)               │
│ 2. Geocode to nearest tile (PostGIS spatial query)                     │
│ 3. Calculate priority score:                                           │
│    priority = base_priority + confidence_bonus + proximity_bonus       │
│ 4. Insert into sat_alerts table                                        │
│ 5. Publish to MQTT topic: /alerts/new/{alert_id}                       │
└─────────────────────┬───────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 3: UAV ASSIGNMENT (Celery Task)                                  │
│ Trigger: Alert created with status='new'                               │
│ Duration: <2 seconds                                                    │
│                                                                          │
│ Algorithm:                                                              │
│ FOR each available UAV:                                                │
│   distance = haversine(uav.position, alert.position)                   │
│   travel_time = distance / uav.speed                                   │
│   battery_factor = 1 - (uav.battery / 100)                             │
│   risk_score = alert.priority / 10                                     │
│   cost = α × travel_time + β × battery_factor + γ × risk_score        │
│                                                                          │
│ SELECT UAV with minimum cost                                           │
│                                                                          │
│ Actions:                                                                │
│ 1. Create mission record (status='pending')                            │
│ 2. Update UAV status to 'assigned'                                     │
│ 3. Publish MQTT command: /commands/{uav_id}/mission                    │
│ 4. Start mission monitoring task                                       │
└─────────────────────┬───────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 4: UAV FLIGHT & EDGE INFERENCE                                   │
│ Trigger: UAV receives mission command                                  │
│ Duration: 10-30 minutes (variable by distance)                         │
│                                                                          │
│ UAV Actions:                                                            │
│ 1. Calculate flight path (A* + Dubins curves)                          │
│ 2. Update status to 'in_mission'                                       │
│ 3. Navigate to alert coordinates                                       │
│ 4. Publish telemetry every 5 seconds: /telemetry/{uav_id}              │
│ 5. Activate cameras upon arrival                                       │
│ 6. Execute spiral search pattern (50m radius)                          │
│                                                                          │
│ Edge AI Processing (Loop):                                             │
│ WHILE (mission active):                                                │
│   frame = capture_camera_frame()                                       │
│   detections = yolov8_inference(frame)                                 │
│   FOR each detection WHERE confidence > 0.75:                          │
│     bbox, class, conf = detection                                      │
│     IF class IN target_classes:                                        │
│       save_evidence_to_minio(frame, bbox)                              │
│       POST /api/v1/detections                                          │
│       publish_mqtt(/detections/{uav_id}, detection_data)               │
└─────────────────────┬───────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 5: VERIFICATION & HUMAN DECISION                                 │
│ Trigger: Detection confidence > 85% OR mission complete                │
│ Duration: <5 minutes (operator response SLA)                           │
│                                                                          │
│ Dashboard Updates:                                                      │
│ 1. Alert marker changes color (new → investigating → verified)         │
│ 2. Detection markers appear on map with bounding boxes                 │
│ 3. Evidence thumbnails load in sidebar                                 │
│ 4. Confidence meter updates in real-time                               │
│                                                                          │
│ Operator Actions:                                                       │
│ ┌─────────────────────────────────────────────────────┐                │
│ │ IF confirmed_threat:                                │                │
│ │   - Mark detection as verified                      │                │
│ │   - Dispatch field response team                    │                │
│ │   - Generate intelligence report                    │                │
│ │   - Tag evidence for prosecution                    │                │
│ │ ELSE IF false_positive:                             │                │
│ │   - Mark alert as false_positive                    │                │
│ │   - Update ML model training queue                  │                │
│ │   - Log for pattern analysis                        │                │
│ │ ELSE IF needs_more_info:                            │                │
│ │   - Request UAV loiter/orbit                        │                │
│ │   - Switch to thermal camera                        │                │
│ │   - Request satellite re-task                       │                │
│ └─────────────────────────────────────────────────────┘                │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Workflow Timing Analysis

**Baseline Scenario:** Border intrusion detected by satellite at 10:00:00

| Stage | Start Time | End Time | Duration | Cumulative |
|-------|-----------|----------|----------|------------|
| 1. Satellite Detection | 10:00:00 | 10:02:30 | 2m 30s | 2m 30s |
| 2. Alert Ingestion | 10:02:30 | 10:02:31 | <1s | 2m 31s |
| 3. UAV Assignment | 10:02:31 | 10:02:33 | 2s | 2m 33s |
| 4. UAV Transit | 10:02:33 | 10:14:33 | 12m | 14m 33s |
| 4. On-Site Verification | 10:14:33 | 10:19:33 | 5m | 19m 33s |
| 5. Operator Decision | 10:19:33 | 10:22:33 | 3m | 22m 33s |
| **Total Detection-to-Action** | - | - | - | **22m 33s** |

**Performance Optimization Targets:**
- Alert ingestion: 500ms → **250ms** (database indexing, connection pooling)
- UAV assignment: 2s → **<1s** (pre-computed distance matrices, cached queries)
- Transit time: 12m → **8m** (faster UAVs, strategic pre-positioning)
- Verification: 5m → **3m** (improved search algorithms, multi-sensor fusion)

---

### 1.3 Data Pipeline & Processing Layers

The EVENT system implements a **multi-layer data pipeline** optimized for low-latency streaming, batch processing, and long-term analytics.

#### Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│ INGESTION LAYER                                                         │
│                                                                          │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │  Satellite   │     │     UAV      │     │   External   │            │
│  │  Data Feeds  │     │  Telemetry   │     │   API Feeds  │            │
│  │  (REST API)  │     │    (MQTT)    │     │   (Webhook)  │            │
│  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘            │
│         │                    │                    │                     │
│         └────────────────────┴────────────────────┘                     │
│                              │                                          │
│                    [API Gateway / Load Balancer]                        │
│                              │                                          │
└──────────────────────────────┼──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PROCESSING LAYER                                                        │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────┐            │
│  │ STREAM PROCESSING (Real-Time)                          │            │
│  │                                                          │            │
│  │  ┌────────────────┐         ┌────────────────┐         │            │
│  │  │   Validation   │────────▶│  Enrichment    │         │            │
│  │  │   - Schema     │         │  - Geocoding   │         │            │
│  │  │   - Auth       │         │  - Tile lookup │         │            │
│  │  │   - Rate limit │         │  - Weather API │         │            │
│  │  └────────────────┘         └────────┬───────┘         │            │
│  │                                      │                  │            │
│  │                                      ▼                  │            │
│  │                           ┌────────────────┐            │            │
│  │                           │  Routing       │            │            │
│  │                           │  - Priority Q  │            │            │
│  │                           │  - Deduplication│           │            │
│  │                           │  - Aggregation │            │            │
│  │                           └────────┬───────┘            │            │
│  │                                    │                    │            │
│  │         ┌──────────────────────────┼──────────────────┐ │            │
│  │         ▼                          ▼                  ▼ │            │
│  │  ┌────────────┐           ┌────────────┐    ┌─────────────┐        │
│  │  │   Alert    │           │  Mission   │    │  Detection  │        │
│  │  │  Handler   │           │  Handler   │    │   Handler   │        │
│  │  └────────────┘           └────────────┘    └─────────────┘        │
│  └─────────────────────────────────────────────────────────┘            │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────┐            │
│  │ BATCH PROCESSING (Scheduled Tasks - Celery Beat)       │            │
│  │                                                          │            │
│  │  Every 10s:  Battery monitoring & low-battery alerts   │            │
│  │  Every 30s:  Mission timeout checks                     │            │
│  │  Every 5m:   Fleet rebalancing recommendations          │            │
│  │  Every 1h:   Statistics aggregation                     │            │
│  │  Every 24h:  Database cleanup & archival                │            │
│  └─────────────────────────────────────────────────────────┘            │
│                                                                          │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STORAGE LAYER                                                           │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────┐           │
│  │ HOT STORAGE (PostgreSQL + PostGIS)                       │           │
│  │ - Active missions (last 7 days)                          │           │
│  │ - Recent detections (last 30 days)                       │           │
│  │ - UAV telemetry (last 24 hours, 5s granularity)         │           │
│  │ - All tiles, UAVs, alerts (always active)               │           │
│  │                                                           │           │
│  │ Retention: 30 days → auto-archive to cold storage       │           │
│  │ Performance: <10ms query latency for indexed lookups    │           │
│  └──────────────────────────────────────────────────────────┘           │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────┐           │
│  │ WARM STORAGE (MinIO Object Storage)                      │           │
│  │ - Evidence files (images, videos): Unlimited retention  │           │
│  │ - Mission logs: 1 year retention                         │           │
│  │ - Telemetry archives: 90 days                           │           │
│  │                                                           │           │
│  │ Access: S3-compatible API, CDN-cacheable                │           │
│  │ Redundancy: 3-replica minimum                            │           │
│  └──────────────────────────────────────────────────────────┘           │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────┐           │
│  │ COLD STORAGE (Future: S3 Glacier / Azure Archive)       │           │
│  │ - Historical missions (>1 year old)                      │           │
│  │ - Compliance archives (7-year legal retention)          │           │
│  │ - Training datasets for ML model improvement            │           │
│  │                                                           │           │
│  │ Retrieval: 1-12 hours                                    │           │
│  └──────────────────────────────────────────────────────────┘           │
│                                                                          │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ ANALYTICS LAYER                                                         │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────┐           │
│  │ Real-Time Analytics (PostgreSQL Views)                   │           │
│  │ - mission_stats: Success rates, avg duration            │           │
│  │ - fleet_status: UAV availability, battery levels        │           │
│  │ - detection_summary: Counts by type, confidence         │           │
│  └──────────────────────────────────────────────────────────┘           │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────┐           │
│  │ Machine Learning Pipeline (Future)                       │           │
│  │ - False positive analysis                                │           │
│  │ - Patrol route optimization                              │           │
│  │ - Predictive maintenance                                 │           │
│  │ - Threat pattern recognition                             │           │
│  └──────────────────────────────────────────────────────────┘           │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Data Schema & Relationships

```sql
-- Core Entities and Relationships

tiles (1) ──────────────< (N) sat_alerts
  │                            │
  │                            │
  │                            ▼
  │                       (1) missions (N)
  │                            │         │
  │                            │         │
  └────────────────────────────┘         │
                                         │
uavs (1) ────────────────────────────────┘
  │                                      │
  │                                      │
  ├──────────────────< (N) telemetry    │
  │                                      │
  └──────────────────< (N) detections <─┘
                           │
                           │
                           ▼
                       (N) evidence (files in MinIO)
```

---

### 1.4 Latency, Coverage, Resolution Trade-off Framework

The EVENT system balances three competing objectives across the ISR tiers. Optimizing one dimension typically requires sacrificing another, requiring strategic trade-offs based on mission priorities.

#### The ISR Triangle

```
                        RESOLUTION
                        (Detail Level)
                             ▲
                            / \
                           /   \
                          /     \
                         /       \
                        /         \
                       /  OPTIMAL  \
                      /    ZONE     \
                     /   (MVP Tier  \
                    /    Selection)  \
                   /                  \
                  /_____________________\
           COVERAGE                LATENCY
         (Area Monitored)      (Response Time)
```

#### Tier Trade-off Analysis

| Tier | Coverage | Resolution | Latency | Cost | Use Case |
|------|----------|------------|---------|------|----------|
| **Satellite (Tier 0)** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | $$ | Initial detection, wide area |
| **UAV (Tier 2)** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | $$$ | Verification, tracking |
| **Ground Assets** | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | $$$$ | Interdiction, arrest |

#### Configuration Presets by Mission Type

**Preset 1: Border Surveillance (High Coverage Priority)**
```yaml
satellite_config:
  revisit_frequency: 6h
  resolution: 3m GSD
  coverage_area: 5000 km²
  
uav_config:
  patrol_pattern: grid_sweep
  altitude: 300m (max coverage)
  camera_resolution: 1080p
  detection_threshold: 0.70 (lower = more alerts)
  
performance_targets:
  coverage_guarantee: 100%
  false_positive_tolerance: 20%
  response_time_sla: <20 minutes
```

**Preset 2: Search & Rescue (High Resolution Priority)**
```yaml
satellite_config:
  revisit_frequency: 24h
  resolution: 0.5m GSD (high-res tasked)
  coverage_area: 500 km²
  
uav_config:
  patrol_pattern: spiral_search
  altitude: 50m (max resolution)
  camera_resolution: 4K
  detection_threshold: 0.85 (fewer but confident)
  
performance_targets:
  coverage_guarantee: 100%
  false_positive_tolerance: 10%
  response_time_sla: <10 minutes
```

**Preset 3: Critical Infrastructure (High Latency Priority)**
```yaml
satellite_config:
  revisit_frequency: 2h
  resolution: 1m GSD
  coverage_area: 100 km²
  
uav_config:
  patrol_pattern: loiter_orbit (persistent)
  altitude: 100m
  camera_resolution: 2K
  detection_threshold: 0.90 (high confidence)
  
performance_targets:
  coverage_guarantee: 100% (continuous)
  false_positive_tolerance: 5%
  response_time_sla: <5 minutes
```

#### Dynamic Trade-off Optimization

The EVENT system adjusts tier parameters in real-time based on:

1. **Threat Level Escalation**
   - Low threat: Standard patrol (300m alt, 6h sat revisit)
   - Medium threat: Increased frequency (150m alt, 3h sat revisit)
   - High threat: Continuous UAV loiter + on-demand satellite tasking

2. **Environmental Conditions**
   - Clear weather: Satellite-primary, UAV-verification
   - Cloud cover >50%: UAV-primary with SAR satellite backup
   - High winds: Reduce coverage area, increase altitude

3. **Resource Constraints**
   - Low battery fleet: Reduce patrol area, prioritize high-value zones
   - Satellite blackout: Increase UAV patrol density
   - Network congestion: Buffer telemetry, prioritize alerts

#### Mathematical Optimization Framework

**Cost Function for Tier Selection:**

```
Total_Cost = α × Coverage_Cost + β × Resolution_Cost + γ × Latency_Cost

Where:
  Coverage_Cost = Area / (UAV_count × Flight_range²)
  Resolution_Cost = 1 / (Camera_GSD × Processing_power)
  Latency_Cost = Detection_delay + Transit_time + Processing_time

Constraints:
  Coverage ≥ 90% (mission requirement)
  Resolution ≥ 10cm GSD for person detection
  Latency ≤ 30 minutes for border security
  Battery_reserve ≥ 20% (safety margin)
```

---

## Key Takeaways

✅ **Tiered architecture** enables cost-effective coverage through coordinated satellite-UAV operations  
✅ **Real-time tasking flow** achieves <25-minute detection-to-action loop  
✅ **Multi-layer data pipeline** handles streaming, batch, and analytics workloads  
✅ **Trade-off framework** allows mission-specific optimization of coverage, resolution, and latency  

---

## Navigation

- **Previous:** [Executive Summary](./EXECUTIVE_SUMMARY.md)
- **Next:** [Satellite-UAV Coordination Strategy](./COORDINATION_STRATEGY.md)
- **Home:** [Documentation Index](./README.md)

---

**Document Status:** ✅ Complete  
**Last Updated:** November 9, 2025  
**Review Cycle:** Quarterly
