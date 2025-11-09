# Real-Time Dashboard
## Coordinated Satellite & UAV Event-Analysis MVP

**Document Version:** 1.0  
**Date:** November 9, 2025  
**Parent Document:** [Communication & Networking](./COMMUNICATION_NETWORKING.md)

---

## 8. Real-Time Dashboard

### 8.1 Mission Map Visualization

The EVENT dashboard provides a **geospatial interface** for monitoring satellite coverage, UAV positions, and active threats in real-time.

#### Map Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│ REAL-TIME MISSION MAP INTERFACE                                         │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │ HEADER: System Status Bar                                       │    │
│  │ [●] Connected | 8 UAVs Active | 3 Missions | 2 Alerts          │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    GEOSPATIAL MAP VIEW                           │   │
│  │                                                                   │   │
│  │   Legend:                                                         │   │
│  │   🛰️  Satellite Coverage Zone                                   │   │
│  │   🚁  UAV (Green=Available, Yellow=Tasked, Red=Low Battery)     │   │
│  │   📍  Alert Location (Color by Priority)                        │   │
│  │   📹  Active Surveillance Area                                   │   │
│  │   🚫  Geofence Boundaries (Red=Exclusion, Yellow=Prohibited)    │   │
│  │   ─►  UAV Flight Path (Planned)                                 │   │
│  │   ━►  UAV Flight Path (Actual)                                  │   │
│  │                                                                   │   │
│  │              [Zoom Controls] [Layer Toggles]                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────┬──────────────────────────────────────────────────┐   │
│  │ SIDE PANEL   │ DETAIL VIEW                                       │   │
│  │              │                                                    │   │
│  │ UAV List     │ Selected: UAV-003                                 │   │
│  │ ├ UAV-001 ✓  │ Status: On Mission                                │   │
│  │ ├ UAV-002 ✓  │ Battery: 67%                                      │   │
│  │ ├ UAV-003 ⚡ │ Position: 31.7645°N, -106.4850°W                 │   │
│  │ ├ UAV-004 ✓  │ Altitude: 60m AGL                                 │   │
│  │ └ UAV-005 ⚠️  │ Speed: 12.3 m/s                                   │   │
│  │              │                                                    │   │
│  │ Active Alerts│ Mission: Investigate Alert #A-1847               │   │
│  │ ├ A-1847 🔴  │ Progress: 45%                                     │   │
│  │ ├ A-1848 🟡  │ ETA: 3min 20sec                                   │   │
│  │ └ A-1849 🟢  │                                                    │   │
│  │              │ [View Video] [Retask UAV] [Recall]               │   │
│  └──────────────┴──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────┘
```

#### React Component Structure

```javascript
// src/components/MissionMap.js

import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, 
         Circle, Polygon } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const MissionMap = () => {
  // State management
  const [uavs, setUavs] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [missions, setMissions] = useState([]);
  const [geofences, setGeofences] = useState([]);
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [layerVisibility, setLayerVisibility] = useState({
    uavs: true,
    alerts: true,
    missions: true,
    geofences: true,
    coverage: true
  });

  // WebSocket connection for real-time updates
  const ws = useRef(null);

  useEffect(() => {
    // Initialize WebSocket connection
    ws.current = new WebSocket('ws://localhost:8000/ws/telemetry');
    
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleRealtimeUpdate(data);
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    // Fetch initial data
    fetchInitialData();

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  const fetchInitialData = async () => {
    try {
      // Fetch UAVs
      const uavResponse = await fetch('/api/uavs');
      const uavData = await uavResponse.json();
      setUavs(uavData);

      // Fetch alerts
      const alertResponse = await fetch('/api/alerts?status=active');
      const alertData = await alertResponse.json();
      setAlerts(alertData);

      // Fetch missions
      const missionResponse = await fetch('/api/missions?status=active');
      const missionData = await missionResponse.json();
      setMissions(missionData);

      // Fetch geofences
      const geofenceResponse = await fetch('/api/geofences');
      const geofenceData = await geofenceResponse.json();
      setGeofences(geofenceData);
    } catch (error) {
      console.error('Error fetching initial data:', error);
    }
  };

  const handleRealtimeUpdate = (data) => {
    const { type, payload } = data;

    switch (type) {
      case 'uav_telemetry':
        updateUavPosition(payload);
        break;
      case 'new_alert':
        addAlert(payload);
        break;
      case 'mission_update':
        updateMission(payload);
        break;
      case 'detection':
        handleDetection(payload);
        break;
      default:
        console.warn('Unknown message type:', type);
    }
  };

  const updateUavPosition = (telemetry) => {
    setUavs(prevUavs => 
      prevUavs.map(uav => 
        uav.uav_id === telemetry.uav_id 
          ? { ...uav, ...telemetry }
          : uav
      )
    );
  };

  const addAlert = (alert) => {
    setAlerts(prevAlerts => [alert, ...prevAlerts]);
    
    // Show notification
    showNotification('New Alert', {
      body: `${alert.detection_class} detected at ${alert.latitude}, ${alert.longitude}`,
      icon: '/alert-icon.png',
      priority: alert.priority
    });
  };

  const updateMission = (mission) => {
    setMissions(prevMissions => 
      prevMissions.map(m => 
        m.mission_id === mission.mission_id 
          ? { ...m, ...mission }
          : m
      )
    );
  };

  // Custom UAV icon based on status
  const getUavIcon = (uav) => {
    let iconUrl;
    
    if (uav.battery_percent < 30) {
      iconUrl = '/icons/uav-red.png';  // Low battery
    } else if (uav.status === 'on_mission') {
      iconUrl = '/icons/uav-yellow.png';  // Tasked
    } else {
      iconUrl = '/icons/uav-green.png';  // Available
    }

    return new L.Icon({
      iconUrl: iconUrl,
      iconSize: [32, 32],
      iconAnchor: [16, 16],
      popupAnchor: [0, -16]
    });
  };

  // Custom alert icon based on priority
  const getAlertIcon = (alert) => {
    const priorityColors = {
      'CRITICAL': 'red',
      'HIGH': 'orange',
      'MEDIUM': 'yellow',
      'LOW': 'blue'
    };

    const color = priorityColors[alert.priority] || 'gray';

    return new L.Icon({
      iconUrl: `/icons/alert-${color}.png`,
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    });
  };

  return (
    <div className="mission-map-container">
      {/* Map */}
      <MapContainer
        center={[31.7619, -106.4850]}  // El Paso, TX
        zoom={12}
        style={{ height: '100%', width: '100%' }}
      >
        {/* Base layer */}
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />

        {/* Geofences */}
        {layerVisibility.geofences && geofences.map(fence => (
          <Polygon
            key={fence.fence_id}
            positions={fence.coordinates}
            pathOptions={{
              color: fence.type === 'EXCLUSION' ? 'red' : 'orange',
              fillOpacity: 0.2
            }}
          >
            <Popup>
              <div>
                <h4>{fence.name}</h4>
                <p>Type: {fence.type}</p>
                <p>Alert Threshold: {fence.alert_threshold}</p>
              </div>
            </Popup>
          </Polygon>
        ))}

        {/* UAVs */}
        {layerVisibility.uavs && uavs.map(uav => (
          <React.Fragment key={uav.uav_id}>
            <Marker
              position={[uav.latitude, uav.longitude]}
              icon={getUavIcon(uav)}
              eventHandlers={{
                click: () => setSelectedEntity({ type: 'uav', data: uav })
              }}
            >
              <Popup>
                <UAVPopup uav={uav} />
              </Popup>
            </Marker>

            {/* UAV coverage circle */}
            {uav.status === 'on_mission' && (
              <Circle
                center={[uav.latitude, uav.longitude]}
                radius={60}  // Camera FOV radius
                pathOptions={{ color: 'blue', fillOpacity: 0.1 }}
              />
            )}
          </React.Fragment>
        ))}

        {/* Alerts */}
        {layerVisibility.alerts && alerts.map(alert => (
          <Marker
            key={alert.alert_id}
            position={[alert.latitude, alert.longitude]}
            icon={getAlertIcon(alert)}
            eventHandlers={{
              click: () => setSelectedEntity({ type: 'alert', data: alert })
            }}
          >
            <Popup>
              <AlertPopup alert={alert} />
            </Popup>
          </Marker>
        ))}

        {/* Mission flight paths */}
        {layerVisibility.missions && missions.map(mission => (
          <React.Fragment key={mission.mission_id}>
            {/* Planned route */}
            {mission.planned_route && (
              <Polyline
                positions={mission.planned_route}
                pathOptions={{ color: 'gray', dashArray: '5, 10' }}
              />
            )}

            {/* Actual route */}
            {mission.actual_route && (
              <Polyline
                positions={mission.actual_route}
                pathOptions={{ color: 'blue', weight: 3 }}
              />
            )}
          </React.Fragment>
        ))}
      </MapContainer>

      {/* Layer toggle controls */}
      <LayerControls
        visibility={layerVisibility}
        onToggle={setLayerVisibility}
      />
    </div>
  );
};

// UAV Popup Component
const UAVPopup = ({ uav }) => (
  <div className="uav-popup">
    <h3>{uav.uav_id}</h3>
    <table>
      <tbody>
        <tr>
          <td>Status:</td>
          <td><StatusBadge status={uav.status} /></td>
        </tr>
        <tr>
          <td>Battery:</td>
          <td>
            <BatteryIndicator percent={uav.battery_percent} />
          </td>
        </tr>
        <tr>
          <td>Altitude:</td>
          <td>{uav.altitude}m AGL</td>
        </tr>
        <tr>
          <td>Speed:</td>
          <td>{uav.speed?.toFixed(1)} m/s</td>
        </tr>
        <tr>
          <td>Heading:</td>
          <td>{uav.heading?.toFixed(0)}°</td>
        </tr>
      </tbody>
    </table>
    <div className="popup-actions">
      <button onClick={() => viewLiveFeed(uav.uav_id)}>
        📹 Live Feed
      </button>
      <button onClick={() => retaskUav(uav.uav_id)}>
        🎯 Retask
      </button>
      <button onClick={() => recallUav(uav.uav_id)}>
        ↩️ Recall
      </button>
    </div>
  </div>
);

// Alert Popup Component
const AlertPopup = ({ alert }) => (
  <div className="alert-popup">
    <h3>Alert {alert.alert_id}</h3>
    <table>
      <tbody>
        <tr>
          <td>Priority:</td>
          <td><PriorityBadge priority={alert.priority} /></td>
        </tr>
        <tr>
          <td>Detection:</td>
          <td>{alert.detection_class}</td>
        </tr>
        <tr>
          <td>Confidence:</td>
          <td>{(alert.confidence * 100).toFixed(1)}%</td>
        </tr>
        <tr>
          <td>Time:</td>
          <td>{new Date(alert.timestamp).toLocaleTimeString()}</td>
        </tr>
        <tr>
          <td>Threat Score:</td>
          <td>{(alert.threat_score * 100).toFixed(0)}%</td>
        </tr>
      </tbody>
    </table>
    <div className="popup-actions">
      <button onClick={() => dispatchUav(alert)}>
        🚁 Dispatch UAV
      </button>
      <button onClick={() => viewAlertDetails(alert.alert_id)}>
        📋 Details
      </button>
      <button onClick={() => dismissAlert(alert.alert_id)}>
        ✖️ Dismiss
      </button>
    </div>
  </div>
);

export default MissionMap;
```

---

### 8.2 Threat Timeline Visualization

The dashboard provides a **chronological view** of all threats and system events for situational awareness.

#### Timeline Component

```javascript
// src/components/ThreatTimeline.js

import React, { useState, useEffect } from 'react';
import { Timeline } from 'antd';
import './ThreatTimeline.css';

const ThreatTimeline = () => {
  const [events, setEvents] = useState([]);
  const [filter, setFilter] = useState('all');  // all, alerts, missions, system

  useEffect(() => {
    fetchTimelineEvents();

    // Poll for new events every 5 seconds
    const interval = setInterval(fetchTimelineEvents, 5000);
    return () => clearInterval(interval);
  }, [filter]);

  const fetchTimelineEvents = async () => {
    try {
      const response = await fetch(`/api/timeline?filter=${filter}&limit=50`);
      const data = await response.json();
      setEvents(data);
    } catch (error) {
      console.error('Error fetching timeline:', error);
    }
  };

  const getEventColor = (event) => {
    const colorMap = {
      'alert_critical': 'red',
      'alert_high': 'orange',
      'alert_medium': 'yellow',
      'alert_low': 'blue',
      'mission_start': 'green',
      'mission_complete': 'green',
      'detection': 'purple',
      'system': 'gray'
    };

    return colorMap[event.event_type] || 'blue';
  };

  const getEventIcon = (event) => {
    const iconMap = {
      'alert_critical': '🚨',
      'alert_high': '⚠️',
      'alert_medium': '⚡',
      'alert_low': 'ℹ️',
      'mission_start': '🚁',
      'mission_complete': '✅',
      'detection': '👁️',
      'geofence_violation': '🚫',
      'system': '⚙️'
    };

    return iconMap[event.event_type] || '📍';
  };

  return (
    <div className="threat-timeline">
      <div className="timeline-header">
        <h2>Threat Timeline</h2>
        <div className="timeline-filters">
          <button 
            className={filter === 'all' ? 'active' : ''}
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button 
            className={filter === 'alerts' ? 'active' : ''}
            onClick={() => setFilter('alerts')}
          >
            Alerts
          </button>
          <button 
            className={filter === 'missions' ? 'active' : ''}
            onClick={() => setFilter('missions')}
          >
            Missions
          </button>
          <button 
            className={filter === 'system' ? 'active' : ''}
            onClick={() => setFilter('system')}
          >
            System
          </button>
        </div>
      </div>

      <Timeline mode="left" className="timeline-content">
        {events.map((event, index) => (
          <Timeline.Item
            key={event.event_id}
            color={getEventColor(event)}
            label={
              <span className="timeline-timestamp">
                {new Date(event.timestamp).toLocaleTimeString()}
              </span>
            }
          >
            <div className="timeline-event">
              <div className="event-icon">{getEventIcon(event)}</div>
              <div className="event-content">
                <h4>{event.title}</h4>
                <p>{event.description}</p>
                
                {event.metadata && (
                  <div className="event-metadata">
                    {Object.entries(event.metadata).map(([key, value]) => (
                      <span key={key} className="metadata-tag">
                        {key}: {value}
                      </span>
                    ))}
                  </div>
                )}

                <div className="event-actions">
                  {event.actionable && (
                    <>
                      <button onClick={() => viewEventDetails(event.event_id)}>
                        View Details
                      </button>
                      {event.event_type.startsWith('alert') && (
                        <button onClick={() => dispatchToEvent(event)}>
                          Dispatch UAV
                        </button>
                      )}
                    </>
                  )}
                </div>
              </div>
            </div>
          </Timeline.Item>
        ))}
      </Timeline>
    </div>
  );
};

export default ThreatTimeline;
```

---

### 8.3 UAV & Satellite Telemetry Display

Real-time telemetry dashboards provide **system health monitoring** and performance metrics.

#### Telemetry Dashboard

```javascript
// src/components/TelemetryDashboard.js

import React, { useState, useEffect } from 'react';
import { Line, Gauge, Progress } from '@ant-design/charts';
import './TelemetryDashboard.css';

const TelemetryDashboard = ({ uavId }) => {
  const [telemetry, setTelemetry] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    // Subscribe to telemetry stream
    const ws = new WebSocket(`ws://localhost:8000/ws/telemetry/${uavId}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setTelemetry(data);
      
      // Add to history
      setHistory(prev => {
        const updated = [...prev, data];
        // Keep last 100 points
        return updated.slice(-100);
      });
    };

    return () => ws.close();
  }, [uavId]);

  if (!telemetry) {
    return <div>Loading telemetry...</div>;
  }

  return (
    <div className="telemetry-dashboard">
      <h2>UAV {uavId} Telemetry</h2>

      {/* Primary Metrics */}
      <div className="metrics-grid">
        {/* Battery Level */}
        <div className="metric-card">
          <h3>Battery</h3>
          <Gauge
            percent={telemetry.battery_percent / 100}
            range={{
              color: telemetry.battery_percent < 30 ? '#F4664A' : '#30BF78',
            }}
            indicator={{
              pointer: {
                style: {
                  stroke: '#D0D0D0',
                },
              },
              pin: {
                style: {
                  stroke: '#D0D0D0',
                },
              },
            }}
            statistic={{
              content: {
                style: {
                  fontSize: '24px',
                  lineHeight: '24px',
                },
                formatter: () => `${telemetry.battery_percent}%`,
              },
            }}
          />
        </div>

        {/* Altitude */}
        <div className="metric-card">
          <h3>Altitude</h3>
          <div className="metric-value">
            {telemetry.altitude.toFixed(1)} m
          </div>
          <div className="metric-label">AGL</div>
        </div>

        {/* Speed */}
        <div className="metric-card">
          <h3>Speed</h3>
          <div className="metric-value">
            {telemetry.speed.toFixed(1)} m/s
          </div>
          <div className="metric-label">
            ({(telemetry.speed * 3.6).toFixed(1)} km/h)
          </div>
        </div>

        {/* Signal Strength */}
        <div className="metric-card">
          <h3>Signal</h3>
          <Progress
            percent={telemetry.signal_strength}
            strokeColor={{
              '0%': '#108ee9',
              '100%': '#87d068',
            }}
          />
        </div>
      </div>

      {/* Time-series Charts */}
      <div className="charts-grid">
        {/* Altitude History */}
        <div className="chart-card">
          <h3>Altitude History</h3>
          <Line
            data={history.map((t, i) => ({
              time: i,
              altitude: t.altitude
            }))}
            xField="time"
            yField="altitude"
            smooth={true}
            height={200}
          />
        </div>

        {/* Speed History */}
        <div className="chart-card">
          <h3>Speed History</h3>
          <Line
            data={history.map((t, i) => ({
              time: i,
              speed: t.speed
            }))}
            xField="time"
            yField="speed"
            smooth={true}
            height={200}
          />
        </div>

        {/* Battery Drain */}
        <div className="chart-card">
          <h3>Battery Drain</h3>
          <Line
            data={history.map((t, i) => ({
              time: i,
              battery: t.battery_percent
            }))}
            xField="time"
            yField="battery"
            smooth={true}
            height={200}
            color="#FFA940"
          />
        </div>
      </div>

      {/* Detailed Status */}
      <div className="status-table">
        <h3>System Status</h3>
        <table>
          <tbody>
            <tr>
              <td>Position</td>
              <td>
                {telemetry.latitude.toFixed(6)}°N, {telemetry.longitude.toFixed(6)}°W
              </td>
            </tr>
            <tr>
              <td>Heading</td>
              <td>{telemetry.heading.toFixed(1)}°</td>
            </tr>
            <tr>
              <td>GPS Quality</td>
              <td>
                <StatusIndicator status={telemetry.gps_quality} />
              </td>
            </tr>
            <tr>
              <td>Camera</td>
              <td>
                <StatusIndicator status={telemetry.camera_status} />
              </td>
            </tr>
            <tr>
              <td>Data Link</td>
              <td>
                <StatusIndicator status={telemetry.datalink_status} />
              </td>
            </tr>
            <tr>
              <td>Flight Time</td>
              <td>{formatDuration(telemetry.flight_time)}</td>
            </tr>
            <tr>
              <td>Distance Traveled</td>
              <td>{(telemetry.distance_traveled / 1000).toFixed(2)} km</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

const StatusIndicator = ({ status }) => {
  const colors = {
    'good': '#52c41a',
    'degraded': '#faad14',
    'poor': '#f5222d',
    'offline': '#d9d9d9'
  };

  return (
    <span style={{ color: colors[status] }}>
      ● {status.toUpperCase()}
    </span>
  );
};

const formatDuration = (seconds) => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  return `${hours}h ${minutes}m ${secs}s`;
};

export default TelemetryDashboard;
```

---

### 8.4 Incident Confidence Meter

Visual indicators show **detection confidence** and threat assessment in real-time.

#### Confidence Meter Component

```javascript
// src/components/ConfidenceMeter.js

import React from 'react';
import { Progress, Tooltip } from 'antd';
import './ConfidenceMeter.css';

const ConfidenceMeter = ({ detection }) => {
  const {
    model_confidence,
    context_confidence,
    temporal_confidence,
    composite_confidence,
    threat_score
  } = detection;

  // Calculate color based on confidence
  const getConfidenceColor = (value) => {
    if (value >= 0.85) return '#52c41a';  // Green
    if (value >= 0.70) return '#faad14';  // Yellow
    if (value >= 0.50) return '#ff7a45';  // Orange
    return '#f5222d';  // Red
  };

  // Calculate threat level
  const getThreatLevel = (score) => {
    if (score >= 0.85) return { level: 'CRITICAL', color: '#f5222d' };
    if (score >= 0.70) return { level: 'HIGH', color: '#ff7a45' };
    if (score >= 0.50) return { level: 'MEDIUM', color: '#faad14' };
    return { level: 'LOW', color: '#52c41a' };
  };

  const threatLevel = getThreatLevel(threat_score);

  return (
    <div className="confidence-meter">
      <div className="meter-header">
        <h3>Detection Confidence</h3>
        <div 
          className="threat-badge"
          style={{ backgroundColor: threatLevel.color }}
        >
          {threatLevel.level}
        </div>
      </div>

      {/* Composite Confidence */}
      <div className="composite-confidence">
        <div className="confidence-label">
          <span>Overall Confidence</span>
          <span className="confidence-value">
            {(composite_confidence * 100).toFixed(1)}%
          </span>
        </div>
        <Progress
          percent={composite_confidence * 100}
          strokeColor={getConfidenceColor(composite_confidence)}
          strokeWidth={20}
          showInfo={false}
        />
      </div>

      {/* Component Confidences */}
      <div className="component-confidences">
        <Tooltip title="Confidence from AI model detection">
          <div className="confidence-component">
            <div className="component-label">
              <span>🤖 Model</span>
              <span>{(model_confidence * 100).toFixed(1)}%</span>
            </div>
            <Progress
              percent={model_confidence * 100}
              strokeColor={getConfidenceColor(model_confidence)}
              size="small"
              showInfo={false}
            />
          </div>
        </Tooltip>

        <Tooltip title="Confidence from contextual factors (location, time, etc.)">
          <div className="confidence-component">
            <div className="component-label">
              <span>📍 Context</span>
              <span>{(context_confidence * 100).toFixed(1)}%</span>
            </div>
            <Progress
              percent={context_confidence * 100}
              strokeColor={getConfidenceColor(context_confidence)}
              size="small"
              showInfo={false}
            />
          </div>
        </Tooltip>

        <Tooltip title="Confidence from temporal consistency">
          <div className="confidence-component">
            <div className="component-label">
              <span>⏱️ Temporal</span>
              <span>{(temporal_confidence * 100).toFixed(1)}%</span>
            </div>
            <Progress
              percent={temporal_confidence * 100}
              strokeColor={getConfidenceColor(temporal_confidence)}
              size="small"
              showInfo={false}
            />
          </div>
        </Tooltip>
      </div>

      {/* Threat Score */}
      <div className="threat-score-section">
        <div className="score-label">
          <span>Threat Assessment</span>
          <span className="score-value">
            {(threat_score * 100).toFixed(0)}%
          </span>
        </div>
        <div className="threat-meter">
          <div 
            className="threat-fill"
            style={{
              width: `${threat_score * 100}%`,
              backgroundColor: threatLevel.color
            }}
          />
        </div>
        <div className="threat-labels">
          <span>LOW</span>
          <span>MEDIUM</span>
          <span>HIGH</span>
          <span>CRITICAL</span>
        </div>
      </div>

      {/* Confidence Breakdown */}
      <div className="confidence-breakdown">
        <h4>Confidence Formula</h4>
        <div className="formula">
          <code>
            C = 0.50 × M + 0.30 × X + 0.20 × T
          </code>
        </div>
        <ul>
          <li>M = Model confidence ({(model_confidence * 100).toFixed(1)}%)</li>
          <li>X = Context confidence ({(context_confidence * 100).toFixed(1)}%)</li>
          <li>T = Temporal confidence ({(temporal_confidence * 100).toFixed(1)}%)</li>
        </ul>
      </div>
    </div>
  );
};

export default ConfidenceMeter;
```

---

### 8.5 Alerts & Notifications System

The dashboard provides **multi-channel alerting** for critical events requiring immediate attention.

#### Alert System

```javascript
// src/services/AlertService.js

class AlertService {
  constructor() {
    this.notificationPermission = false;
    this.audioContext = null;
    this.alertSounds = {};
    
    this.initialize();
  }

  async initialize() {
    // Request notification permission
    if ('Notification' in window) {
      this.notificationPermission = await Notification.requestPermission();
    }

    // Initialize audio for alerts
    this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    
    // Load alert sounds
    await this.loadAlertSounds();
  }

  async loadAlertSounds() {
    const sounds = {
      'critical': '/sounds/critical-alert.mp3',
      'high': '/sounds/high-alert.mp3',
      'medium': '/sounds/medium-alert.mp3',
      'low': '/sounds/low-alert.mp3'
    };

    for (const [priority, url] of Object.entries(sounds)) {
      try {
        const response = await fetch(url);
        const arrayBuffer = await response.arrayBuffer();
        this.alertSounds[priority] = await this.audioContext.decodeAudioData(arrayBuffer);
      } catch (error) {
        console.error(`Failed to load ${priority} alert sound:`, error);
      }
    }
  }

  playAlertSound(priority) {
    if (!this.alertSounds[priority]) return;

    const source = this.audioContext.createBufferSource();
    source.buffer = this.alertSounds[priority];
    source.connect(this.audioContext.destination);
    source.start(0);
  }

  showNotification(title, options = {}) {
    const {
      body,
      icon = '/logo192.png',
      priority = 'medium',
      requireInteraction = false,
      actions = []
    } = options;

    // Browser notification
    if (this.notificationPermission === 'granted') {
      const notification = new Notification(title, {
        body,
        icon,
        requireInteraction: priority === 'critical' || requireInteraction,
        tag: `alert-${Date.now()}`,
        actions
      });

      notification.onclick = () => {
        window.focus();
        notification.close();
      };
    }

    // Play sound
    this.playAlertSound(priority);

    // In-app notification
    this.showInAppAlert(title, body, priority);
  }

  showInAppAlert(title, body, priority) {
    // Create custom alert element
    const alert = document.createElement('div');
    alert.className = `in-app-alert alert-${priority}`;
    alert.innerHTML = `
      <div class="alert-icon">${this.getAlertIcon(priority)}</div>
      <div class="alert-content">
        <h4>${title}</h4>
        <p>${body}</p>
      </div>
      <button class="alert-close" onclick="this.parentElement.remove()">×</button>
    `;

    // Add to page
    const container = document.getElementById('alert-container');
    if (container) {
      container.appendChild(alert);

      // Auto-remove after delay (unless critical)
      if (priority !== 'critical') {
        setTimeout(() => {
          if (alert.parentElement) {
            alert.remove();
          }
        }, 10000);  // 10 seconds
      }
    }
  }

  getAlertIcon(priority) {
    const icons = {
      'critical': '🚨',
      'high': '⚠️',
      'medium': '⚡',
      'low': 'ℹ️'
    };
    return icons[priority] || 'ℹ️';
  }

  // Alert for specific event types
  alertNewDetection(detection) {
    this.showNotification('New Detection', {
      body: `${detection.detection_class} detected with ${(detection.confidence * 100).toFixed(1)}% confidence`,
      priority: detection.priority.toLowerCase(),
      requireInteraction: detection.priority === 'CRITICAL',
      actions: [
        { action: 'view', title: 'View Details' },
        { action: 'dispatch', title: 'Dispatch UAV' }
      ]
    });
  }

  alertGeofenceViolation(violation) {
    this.showNotification('Geofence Violation', {
      body: `Unauthorized entry detected in ${violation.fence_name}`,
      priority: 'critical',
      requireInteraction: true,
      actions: [
        { action: 'view', title: 'View Location' },
        { action: 'dispatch', title: 'Dispatch Response' }
      ]
    });
  }

  alertUAVLowBattery(uav) {
    this.showNotification('UAV Low Battery', {
      body: `${uav.uav_id} battery at ${uav.battery_percent}% - RTB recommended`,
      priority: 'high',
      actions: [
        { action: 'recall', title: 'Recall UAV' },
        { action: 'continue', title: 'Continue Mission' }
      ]
    });
  }

  alertMissionComplete(mission) {
    this.showNotification('Mission Complete', {
      body: `${mission.mission_id} completed successfully`,
      priority: 'low'
    });
  }
}

export default new AlertService();
```

---

### 8.6 Human-in-the-Loop Controls

The dashboard provides **manual override** capabilities for human operators to intervene in autonomous operations.

#### Control Panel

```javascript
// src/components/ControlPanel.js

import React, { useState } from 'react';
import { Button, Modal, Select, Input, Slider } from 'antd';
import './ControlPanel.css';

const ControlPanel = ({ selectedUav, selectedAlert }) => {
  const [modalVisible, setModalVisible] = useState(false);
  const [controlMode, setControlMode] = useState(null);

  // Manual UAV control
  const dispatchUAV = async (alertId) => {
    try {
      const response = await fetch('/api/dispatch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          alert_id: alertId,
          manual_dispatch: true
        })
      });

      if (response.ok) {
        AlertService.showNotification('UAV Dispatched', {
          body: 'UAV en route to alert location',
          priority: 'medium'
        });
      }
    } catch (error) {
      console.error('Dispatch failed:', error);
    }
  };

  const retaskUAV = async (uavId, newMission) => {
    Modal.confirm({
      title: 'Retask UAV',
      content: `Are you sure you want to abort current mission and retask ${uavId}?`,
      onOk: async () => {
        try {
          const response = await fetch(`/api/uavs/${uavId}/retask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newMission)
          });

          if (response.ok) {
            AlertService.showNotification('UAV Retasked', {
              body: `${uavId} assigned to new mission`,
              priority: 'medium'
            });
          }
        } catch (error) {
          console.error('Retask failed:', error);
        }
      }
    });
  };

  const recallUAV = async (uavId) => {
    Modal.confirm({
      title: 'Recall UAV',
      content: `Abort current mission and return ${uavId} to base?`,
      onOk: async () => {
        try {
          const response = await fetch(`/api/uavs/${uavId}/recall`, {
            method: 'POST'
          });

          if (response.ok) {
            AlertService.showNotification('UAV Recalled', {
              body: `${uavId} returning to base`,
              priority: 'medium'
            });
          }
        } catch (error) {
          console.error('Recall failed:', error);
        }
      }
    });
  };

  const emergencyStop = async (uavId) => {
    Modal.confirm({
      title: 'Emergency Stop',
      content: `EMERGENCY: Immediately halt ${uavId}? This cannot be undone.`,
      okText: 'EMERGENCY STOP',
      okType: 'danger',
      onOk: async () => {
        try {
          const response = await fetch(`/api/uavs/${uavId}/emergency-stop`, {
            method: 'POST'
          });

          if (response.ok) {
            AlertService.showNotification('Emergency Stop Activated', {
              body: `${uavId} emergency stopped`,
              priority: 'critical'
            });
          }
        } catch (error) {
          console.error('Emergency stop failed:', error);
        }
      }
    });
  };

  // Manual alert management
  const dismissAlert = async (alertId) => {
    Modal.confirm({
      title: 'Dismiss Alert',
      content: 'Mark this alert as false positive?',
      onOk: async () => {
        try {
          await fetch(`/api/alerts/${alertId}/dismiss`, {
            method: 'POST'
          });
        } catch (error) {
          console.error('Dismiss failed:', error);
        }
      }
    });
  };

  const escalateAlert = async (alertId, newPriority) => {
    try {
      await fetch(`/api/alerts/${alertId}/escalate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ priority: newPriority })
      });

      AlertService.showNotification('Alert Escalated', {
        body: `Alert priority changed to ${newPriority}`,
        priority: 'medium'
      });
    } catch (error) {
      console.error('Escalate failed:', error);
    }
  };

  // System-wide controls
  const setSystemMode = async (mode) => {
    // Modes: 'autonomous', 'supervised', 'manual'
    Modal.confirm({
      title: `Switch to ${mode.toUpperCase()} mode?`,
      content: getSystemModeDescription(mode),
      onOk: async () => {
        try {
          await fetch('/api/system/mode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode })
          });

          AlertService.showNotification('System Mode Changed', {
            body: `Now operating in ${mode} mode`,
            priority: 'high'
          });
        } catch (error) {
          console.error('Mode change failed:', error);
        }
      }
    });
  };

  const adjustConfidenceThreshold = async (threshold) => {
    try {
      await fetch('/api/system/confidence-threshold', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ threshold })
      });
    } catch (error) {
      console.error('Threshold adjustment failed:', error);
    }
  };

  return (
    <div className="control-panel">
      <h2>Mission Control</h2>

      {/* System-wide Controls */}
      <div className="control-section">
        <h3>System Mode</h3>
        <Select
          defaultValue="autonomous"
          style={{ width: '100%' }}
          onChange={setSystemMode}
        >
          <Select.Option value="autonomous">
            🤖 Autonomous
          </Select.Option>
          <Select.Option value="supervised">
            👁️ Supervised
          </Select.Option>
          <Select.Option value="manual">
            ✋ Manual
          </Select.Option>
        </Select>
      </div>

      <div className="control-section">
        <h3>Detection Threshold</h3>
        <Slider
          min={0.5}
          max={0.95}
          step={0.05}
          defaultValue={0.75}
          marks={{
            0.5: 'Sensitive',
            0.75: 'Balanced',
            0.95: 'Strict'
          }}
          onChange={adjustConfidenceThreshold}
        />
      </div>

      {/* UAV Controls */}
      {selectedUav && (
        <div className="control-section">
          <h3>UAV {selectedUav.uav_id} Controls</h3>
          <div className="control-buttons">
            <Button 
              type="primary"
              onClick={() => setModalVisible(true)}
            >
              🎯 Retask
            </Button>
            <Button 
              onClick={() => recallUAV(selectedUav.uav_id)}
            >
              ↩️ Recall
            </Button>
            <Button 
              danger
              onClick={() => emergencyStop(selectedUav.uav_id)}
            >
              🛑 Emergency Stop
            </Button>
          </div>
        </div>
      )}

      {/* Alert Controls */}
      {selectedAlert && (
        <div className="control-section">
          <h3>Alert {selectedAlert.alert_id} Actions</h3>
          <div className="control-buttons">
            <Button 
              type="primary"
              onClick={() => dispatchUAV(selectedAlert.alert_id)}
            >
              🚁 Dispatch UAV
            </Button>
            <Button 
              onClick={() => escalateAlert(selectedAlert.alert_id, 'HIGH')}
            >
              ⬆️ Escalate
            </Button>
            <Button 
              onClick={() => dismissAlert(selectedAlert.alert_id)}
            >
              ✖️ Dismiss
            </Button>
          </div>
        </div>
      )}

      {/* Retask Modal */}
      <RetaskModal
        visible={modalVisible}
        uav={selectedUav}
        onRetask={retaskUAV}
        onCancel={() => setModalVisible(false)}
      />
    </div>
  );
};

const getSystemModeDescription = (mode) => {
  const descriptions = {
    autonomous: 'System operates fully autonomously. UAVs dispatched automatically based on satellite alerts.',
    supervised: 'System generates recommendations but requires human approval before UAV dispatch.',
    manual: 'All operations require explicit human control. No automatic dispatching.'
  };
  return descriptions[mode] || '';
};

export default ControlPanel;
```

---

## Key Takeaways

✅ **Real-time map** with Leaflet showing UAVs, alerts, geofences, and mission paths  
✅ **WebSocket streaming** for <1 second latency on telemetry and detection updates  
✅ **Threat timeline** with chronological view of all system events  
✅ **Telemetry dashboards** with live charts for altitude, speed, battery, and signal  
✅ **Confidence meters** visualizing model, context, and temporal confidence components  
✅ **Multi-channel alerting**: browser notifications + audio + in-app with priority-based UI  
✅ **Human-in-the-loop controls**: manual dispatch, retask, recall, emergency stop  
✅ **3 operating modes**: Autonomous (full auto), Supervised (approval required), Manual (human controlled)  

---

## Navigation

- **Previous:** [Communication & Networking](./COMMUNICATION_NETWORKING.md)
- **Next:** [Evaluation & Metrics](./EVALUATION_METRICS.md)
- **Home:** [Documentation Index](./README.md)

---

**Document Status:** ✅ Complete  
**Last Updated:** November 9, 2025  
**Review Cycle:** Quarterly
