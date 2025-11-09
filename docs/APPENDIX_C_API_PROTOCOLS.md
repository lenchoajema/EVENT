# Appendix C: API & Message Protocols
## Coordinated Satellite & UAV Event-Analysis MVP

**Document Version:** 1.0  
**Date:** November 9, 2025  
**Parent Document:** [Data & Model Specs (Appendix B)](./APPENDIX_B_DATA_MODELS.md)

---

## Appendix C: API & Message Protocols

Complete API specifications, WebSocket protocols, MQTT topics, and message schemas.

---

### C.1 REST API Endpoints

#### Base URL
```
Production:  https://api.event-system.com/v1
Development: http://localhost:8000/v1
```

#### Authentication
```http
Authorization: Bearer <JWT_TOKEN>
```

#### API Endpoints

```
┌─────────────────────────────────────────────────────────────────────────┐
│ DETECTION ENDPOINTS                                                     │
├─────────────────────────────────────────────────────────────────────────┤
│ GET    /detections                  List all detections                 │
│ GET    /detections/{id}             Get detection by ID                 │
│ POST   /detections                  Create new detection                │
│ PATCH  /detections/{id}             Update detection                    │
│ DELETE /detections/{id}             Delete detection                    │
│ GET    /detections/recent           Get recent detections (last 24h)    │
│ GET    /detections/search           Search detections by criteria       │
│                                                                          │
│ ALERT ENDPOINTS                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│ GET    /alerts                      List all alerts                     │
│ GET    /alerts/{id}                 Get alert by ID                     │
│ POST   /alerts                      Create new alert                    │
│ PATCH  /alerts/{id}                 Update alert status                 │
│ POST   /alerts/{id}/acknowledge     Acknowledge alert                   │
│ POST   /alerts/{id}/dismiss         Dismiss alert                       │
│ GET    /alerts/active               Get active alerts                   │
│                                                                          │
│ MISSION ENDPOINTS                                                        │
├─────────────────────────────────────────────────────────────────────────┤
│ GET    /missions                    List all missions                   │
│ GET    /missions/{id}               Get mission by ID                   │
│ POST   /missions                    Create new mission                  │
│ PATCH  /missions/{id}               Update mission                      │
│ DELETE /missions/{id}               Cancel mission                      │
│ POST   /missions/{id}/start         Start mission                       │
│ POST   /missions/{id}/pause         Pause mission                       │
│ POST   /missions/{id}/resume        Resume mission                      │
│ POST   /missions/{id}/abort         Abort mission                       │
│ GET    /missions/{id}/status        Get mission status                  │
│                                                                          │
│ UAV ENDPOINTS                                                            │
├─────────────────────────────────────────────────────────────────────────┤
│ GET    /uavs                        List all UAVs                       │
│ GET    /uavs/{id}                   Get UAV by ID                       │
│ POST   /uavs                        Register new UAV                    │
│ PATCH  /uavs/{id}                   Update UAV configuration            │
│ DELETE /uavs/{id}                   Deregister UAV                      │
│ GET    /uavs/{id}/telemetry         Get UAV telemetry stream            │
│ GET    /uavs/{id}/status            Get UAV status                      │
│ POST   /uavs/{id}/command           Send command to UAV                 │
│ GET    /uavs/available              Get available UAVs                  │
│                                                                          │
│ ZONE ENDPOINTS                                                           │
├─────────────────────────────────────────────────────────────────────────┤
│ GET    /zones                       List all zones                      │
│ GET    /zones/{id}                  Get zone by ID                      │
│ POST   /zones                       Create new zone                     │
│ PATCH  /zones/{id}                  Update zone                         │
│ DELETE /zones/{id}                  Delete zone                         │
│ GET    /zones/geofences             Get geofence zones                  │
│                                                                          │
│ ANALYTICS ENDPOINTS                                                      │
├─────────────────────────────────────────────────────────────────────────┤
│ GET    /analytics/summary           Get system summary                  │
│ GET    /analytics/metrics           Get performance metrics             │
│ GET    /analytics/coverage          Get coverage statistics             │
│ GET    /analytics/threats           Get threat analytics                │
│ POST   /analytics/report            Generate custom report              │
│                                                                          │
│ SYSTEM ENDPOINTS                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│ GET    /health                      Health check                        │
│ GET    /status                      System status                       │
│ GET    /version                     API version info                    │
│ POST   /auth/login                  User login                          │
│ POST   /auth/logout                 User logout                         │
│ POST   /auth/refresh                Refresh token                       │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Request/Response Examples

**GET /detections**
```http
GET /v1/detections?limit=10&offset=0&class=person&confidence_min=0.8 HTTP/1.1
Host: api.event-system.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

Response 200 OK
{
  "total": 150,
  "limit": 10,
  "offset": 0,
  "data": [
    {
      "detection_id": "det_7k9m2n4p",
      "timestamp": "2025-11-09T14:32:15.234Z",
      "uav_id": "uav_001",
      "class": "person",
      "confidence": 0.92,
      "bbox": {
        "x": 1234.5,
        "y": 678.9,
        "width": 45.2,
        "height": 112.8
      },
      "location": {
        "latitude": 40.7128,
        "longitude": -74.0060
      },
      "image_path": "s3://event-images/2025-11-09/det_7k9m2n4p.jpg",
      "verified": false,
      "threat_level": "medium"
    }
  ]
}
```

**POST /missions**
```http
POST /v1/missions HTTP/1.1
Host: api.event-system.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
  "mission_type": "patrol",
  "priority": "high",
  "zone_id": "zone_abc123",
  "uav_id": "uav_002",
  "waypoints": [
    {"latitude": 40.7128, "longitude": -74.0060, "altitude": 100},
    {"latitude": 40.7150, "longitude": -74.0080, "altitude": 100},
    {"latitude": 40.7170, "longitude": -74.0100, "altitude": 100}
  ],
  "parameters": {
    "speed": 15.0,
    "pattern": "lawnmower",
    "overlap": 0.2
  }
}

Response 201 Created
{
  "mission_id": "mis_x5y8z2",
  "status": "created",
  "created_at": "2025-11-09T14:35:00.000Z",
  "estimated_duration": 1800,
  "estimated_distance": 4500.0
}
```

**PATCH /alerts/{id}**
```http
PATCH /v1/alerts/alert_abc123 HTTP/1.1
Host: api.event-system.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
  "status": "acknowledged",
  "operator_notes": "UAV dispatched to investigate"
}

Response 200 OK
{
  "alert_id": "alert_abc123",
  "status": "acknowledged",
  "acknowledged_by": "operator_john",
  "acknowledged_at": "2025-11-09T14:40:00.000Z",
  "operator_notes": "UAV dispatched to investigate"
}
```

#### Error Responses

```json
// 400 Bad Request
{
  "error": "validation_error",
  "message": "Invalid request parameters",
  "details": [
    {
      "field": "confidence",
      "error": "must be between 0 and 1"
    }
  ]
}

// 401 Unauthorized
{
  "error": "unauthorized",
  "message": "Invalid or expired token"
}

// 404 Not Found
{
  "error": "not_found",
  "message": "Resource not found",
  "resource_type": "detection",
  "resource_id": "det_invalid"
}

// 500 Internal Server Error
{
  "error": "internal_error",
  "message": "An unexpected error occurred",
  "request_id": "req_xyz789"
}
```

#### Rate Limiting

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1699545600
```

Rate limits:
- **Standard tier**: 1,000 requests/hour
- **Premium tier**: 10,000 requests/hour
- **Enterprise tier**: Unlimited

---

### C.2 WebSocket Protocol

#### Connection

```javascript
const ws = new WebSocket('wss://api.event-system.com/v1/ws');

// Authentication after connection
ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'eyJhbGciOiJIUzI1NiIs...'
  }));
};

// Subscribe to channels
ws.send(JSON.stringify({
  type: 'subscribe',
  channels: ['telemetry', 'alerts', 'detections']
}));
```

#### Message Types

```
┌─────────────────────────────────────────────────────────────────────────┐
│ WEBSOCKET MESSAGE TYPES                                                 │
├─────────────────────────────────────────────────────────────────────────┤
│ Client → Server                                                          │
│  - auth               Authenticate connection                            │
│  - subscribe          Subscribe to channels                              │
│  - unsubscribe        Unsubscribe from channels                          │
│  - ping               Heartbeat ping                                     │
│  - command            Send UAV command                                   │
│                                                                          │
│ Server → Client                                                          │
│  - auth_success       Authentication successful                          │
│  - auth_error         Authentication failed                              │
│  - subscribed         Subscription confirmed                             │
│  - pong               Heartbeat response                                 │
│  - telemetry          UAV telemetry update                               │
│  - detection          New detection                                      │
│  - alert              New alert                                          │
│  - mission_update     Mission status update                              │
│  - system_status      System status update                               │
│  - error              Error message                                      │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Message Schemas

**Telemetry Update**
```json
{
  "type": "telemetry",
  "timestamp": "2025-11-09T14:45:30.123Z",
  "uav_id": "uav_001",
  "data": {
    "position": {
      "latitude": 40.7128,
      "longitude": -74.0060,
      "altitude": 120.5,
      "heading": 45.2
    },
    "velocity": {
      "ground_speed": 15.3,
      "vertical_speed": 0.2
    },
    "battery": {
      "voltage": 51.2,
      "current": 12.4,
      "remaining_percent": 78,
      "estimated_time_remaining": 1800
    },
    "status": {
      "flight_mode": "mission",
      "armed": true,
      "gps_fix": "3d",
      "satellites": 14
    },
    "sensors": {
      "camera_status": "recording",
      "gimbal_pitch": -45.0,
      "gimbal_yaw": 0.0
    }
  }
}
```

**Detection Event**
```json
{
  "type": "detection",
  "timestamp": "2025-11-09T14:46:12.456Z",
  "detection_id": "det_9x7y5z",
  "uav_id": "uav_001",
  "data": {
    "class": "vehicle",
    "confidence": 0.89,
    "bbox": {
      "x": 850,
      "y": 420,
      "width": 120,
      "height": 85
    },
    "location": {
      "latitude": 40.7135,
      "longitude": -74.0065,
      "altitude": 0
    },
    "metadata": {
      "frame_id": 12345,
      "image_width": 1920,
      "image_height": 1080,
      "gsd_cm": 3.2
    }
  }
}
```

**Alert Event**
```json
{
  "type": "alert",
  "timestamp": "2025-11-09T14:47:00.789Z",
  "alert_id": "alert_p8q9r0",
  "priority": "high",
  "data": {
    "alert_type": "unauthorized_vehicle",
    "source": "satellite",
    "location": {
      "latitude": 40.7142,
      "longitude": -74.0072
    },
    "confidence": 0.94,
    "zone": {
      "zone_id": "zone_restricted_01",
      "zone_name": "Restricted Area Alpha",
      "tier": "prohibited"
    },
    "recommended_action": "dispatch_uav",
    "estimated_response_time": 90
  }
}
```

**Mission Update**
```json
{
  "type": "mission_update",
  "timestamp": "2025-11-09T14:48:30.000Z",
  "mission_id": "mis_a1b2c3",
  "data": {
    "status": "in_progress",
    "progress_percent": 45.5,
    "waypoint_current": 12,
    "waypoint_total": 25,
    "detections_count": 8,
    "alerts_generated": 2,
    "estimated_completion": "2025-11-09T15:30:00.000Z"
  }
}
```

#### Connection Management

```javascript
class EventWebSocket {
  constructor(url, token) {
    this.url = url;
    this.token = token;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.pingInterval = 30000;
  }
  
  connect() {
    this.ws = new WebSocket(this.url);
    
    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.authenticate();
      this.startPingInterval();
      this.reconnectAttempts = 0;
    };
    
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    this.ws.onclose = () => {
      console.log('WebSocket closed');
      this.stopPingInterval();
      this.reconnect();
    };
  }
  
  authenticate() {
    this.send({
      type: 'auth',
      token: this.token
    });
  }
  
  subscribe(channels) {
    this.send({
      type: 'subscribe',
      channels: channels
    });
  }
  
  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }
  
  handleMessage(message) {
    switch (message.type) {
      case 'auth_success':
        console.log('Authenticated successfully');
        break;
      case 'telemetry':
        this.onTelemetry(message.data);
        break;
      case 'detection':
        this.onDetection(message.data);
        break;
      case 'alert':
        this.onAlert(message.data);
        break;
      case 'pong':
        // Heartbeat received
        break;
      default:
        console.warn('Unknown message type:', message.type);
    }
  }
  
  startPingInterval() {
    this.pingTimer = setInterval(() => {
      this.send({ type: 'ping' });
    }, this.pingInterval);
  }
  
  stopPingInterval() {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
    }
  }
  
  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
      setTimeout(() => this.connect(), delay);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }
  
  disconnect() {
    this.stopPingInterval();
    if (this.ws) {
      this.ws.close();
    }
  }
}
```

---

### C.3 MQTT Topics & Messages

#### Topic Structure

```
event/{component}/{entity_id}/{message_type}
```

#### Topic Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────┐
│ MQTT TOPIC HIERARCHY                                                    │
├─────────────────────────────────────────────────────────────────────────┤
│ UAV Topics                                                               │
│  event/uav/{uav_id}/telemetry        UAV telemetry stream               │
│  event/uav/{uav_id}/status           UAV status updates                 │
│  event/uav/{uav_id}/command          Commands to UAV                    │
│  event/uav/{uav_id}/response         Command responses                  │
│  event/uav/{uav_id}/detection        Detections from UAV                │
│  event/uav/{uav_id}/mission          Mission updates                    │
│  event/uav/{uav_id}/health           Health checks                      │
│                                                                          │
│ Command & Control Topics                                                 │
│  event/command/mission/create        Create mission                     │
│  event/command/mission/update        Update mission                     │
│  event/command/mission/abort         Abort mission                      │
│  event/command/uav/dispatch          Dispatch UAV                       │
│  event/command/uav/recall            Recall UAV                         │
│  event/command/system/shutdown       System shutdown                    │
│                                                                          │
│ Alert Topics                                                             │
│  event/alert/satellite               Satellite-detected alerts          │
│  event/alert/uav                     UAV-detected alerts                │
│  event/alert/system                  System alerts                      │
│  event/alert/acknowledged            Alert acknowledgements             │
│                                                                          │
│ System Topics                                                            │
│  event/system/status                 System-wide status                 │
│  event/system/config                 Configuration updates              │
│  event/system/model_update           Model update notifications         │
│  event/system/log                    System logs                        │
│                                                                          │
│ Edge Relay Topics                                                        │
│  event/relay/{relay_id}/status       Relay status                       │
│  event/relay/{relay_id}/buffer       Buffered messages                  │
│  event/relay/{relay_id}/sync         Synchronization                    │
└──────────────────────────────────────────────────────────────────────────┘
```

#### QoS Levels

- **QoS 0** (At most once): Telemetry, non-critical status
- **QoS 1** (At least once): Commands, alerts, detections
- **QoS 2** (Exactly once): Mission-critical commands, safety commands

#### Message Formats

**UAV Telemetry (event/uav/{uav_id}/telemetry)**
```json
{
  "msg_id": "msg_1234567890",
  "timestamp": 1699545600.123,
  "uav_id": "uav_001",
  "position": {
    "lat": 40.7128,
    "lon": -74.0060,
    "alt": 120.5,
    "heading": 45.2
  },
  "velocity": {
    "vx": 12.3,
    "vy": 8.5,
    "vz": 0.2
  },
  "battery": {
    "voltage": 51.2,
    "current": 12.4,
    "percent": 78,
    "time_remaining": 1800
  },
  "status": {
    "mode": "mission",
    "armed": true,
    "gps_fix": "3d",
    "satellites": 14
  }
}
```

**UAV Command (event/uav/{uav_id}/command)**
```json
{
  "msg_id": "cmd_9876543210",
  "timestamp": 1699545700.456,
  "command_type": "goto",
  "priority": "high",
  "params": {
    "latitude": 40.7150,
    "longitude": -74.0080,
    "altitude": 100,
    "speed": 15.0,
    "heading": 90.0
  },
  "timeout": 30,
  "require_ack": true
}
```

**Detection Message (event/uav/{uav_id}/detection)**
```json
{
  "msg_id": "det_5678901234",
  "timestamp": 1699545800.789,
  "uav_id": "uav_001",
  "detection_id": "det_abc123",
  "class": "person",
  "confidence": 0.92,
  "bbox": {
    "x": 1234.5,
    "y": 678.9,
    "w": 45.2,
    "h": 112.8
  },
  "location": {
    "lat": 40.7128,
    "lon": -74.0060,
    "alt": 0
  },
  "image_ref": "frame_12345",
  "metadata": {
    "gsd_cm": 3.2,
    "altitude_m": 120.5,
    "camera": "sony_imx477"
  }
}
```

**Alert Message (event/alert/satellite)**
```json
{
  "msg_id": "alert_1357924680",
  "timestamp": 1699545900.012,
  "alert_id": "alert_xyz789",
  "source": "sentinel2",
  "alert_type": "unauthorized_activity",
  "priority": "critical",
  "confidence": 0.94,
  "location": {
    "lat": 40.7142,
    "lon": -74.0072,
    "bbox": [
      [40.7140, -74.0070],
      [40.7144, -74.0074]
    ]
  },
  "zone": {
    "zone_id": "zone_restricted_01",
    "tier": "prohibited"
  },
  "recommended_action": "dispatch_uav",
  "estimated_response_time": 90
}
```

**Model Update (event/system/model_update)**
```json
{
  "msg_id": "update_2468135790",
  "timestamp": 1699546000.345,
  "model_version": "2.1.0",
  "model_type": "yolov8n",
  "update_type": "mandatory",
  "download_url": "s3://event-models/yolov8n-v2.1.0.onnx",
  "checksum": "sha256:a1b2c3d4e5f6...",
  "size_bytes": 6291456,
  "deployment_time": 1699546300.000,
  "affected_uavs": ["uav_001", "uav_002", "uav_003"]
}
```

#### MQTT Client Example

```python
import paho.mqtt.client as mqtt
import json
import time

class EventMQTTClient:
    """
    MQTT client for EVENT system.
    """
    
    def __init__(self, broker_host, broker_port=1883, client_id=None):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client(client_id=client_id or f"event_client_{int(time.time())}")
        
        # Callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        # Subscriptions
        self.subscriptions = []
    
    def connect(self, username=None, password=None):
        """Connect to MQTT broker."""
        if username and password:
            self.client.username_pw_set(username, password)
        
        self.client.connect(self.broker_host, self.broker_port, keepalive=60)
        self.client.loop_start()
    
    def disconnect(self):
        """Disconnect from broker."""
        self.client.loop_stop()
        self.client.disconnect()
    
    def subscribe(self, topic, qos=1, callback=None):
        """Subscribe to topic."""
        self.client.subscribe(topic, qos)
        self.subscriptions.append({
            'topic': topic,
            'qos': qos,
            'callback': callback
        })
    
    def publish(self, topic, message, qos=1, retain=False):
        """Publish message to topic."""
        payload = json.dumps(message) if isinstance(message, dict) else message
        self.client.publish(topic, payload, qos=qos, retain=retain)
    
    def _on_connect(self, client, userdata, flags, rc):
        """Handle connection."""
        if rc == 0:
            print(f"Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            # Resubscribe to topics
            for sub in self.subscriptions:
                self.client.subscribe(sub['topic'], sub['qos'])
        else:
            print(f"Connection failed with code {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Handle incoming message."""
        try:
            payload = json.loads(msg.payload.decode())
            
            # Find callback for this topic
            for sub in self.subscriptions:
                if mqtt.topic_matches_sub(sub['topic'], msg.topic):
                    if sub['callback']:
                        sub['callback'](msg.topic, payload)
                    else:
                        self._default_handler(msg.topic, payload)
        except Exception as e:
            print(f"Error handling message: {e}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Handle disconnection."""
        if rc != 0:
            print(f"Unexpected disconnect (code {rc}). Reconnecting...")
    
    def _default_handler(self, topic, message):
        """Default message handler."""
        print(f"Received on {topic}: {message}")

# Usage example
if __name__ == "__main__":
    client = EventMQTTClient("mosquitto", 1883)
    
    # Connect
    client.connect(username="event_user", password="secure_password")
    
    # Subscribe to telemetry
    def telemetry_handler(topic, message):
        uav_id = message.get('uav_id')
        battery = message.get('battery', {}).get('percent', 0)
        print(f"UAV {uav_id}: Battery {battery}%")
    
    client.subscribe("event/uav/+/telemetry", qos=0, callback=telemetry_handler)
    
    # Subscribe to alerts
    def alert_handler(topic, message):
        alert_id = message.get('alert_id')
        priority = message.get('priority')
        print(f"ALERT {alert_id}: Priority {priority}")
    
    client.subscribe("event/alert/#", qos=1, callback=alert_handler)
    
    # Publish command
    command = {
        "msg_id": f"cmd_{int(time.time())}",
        "timestamp": time.time(),
        "command_type": "goto",
        "params": {
            "latitude": 40.7150,
            "longitude": -74.0080,
            "altitude": 100
        }
    }
    client.publish("event/uav/uav_001/command", command, qos=1)
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        client.disconnect()
```

---

### C.4 Message Schema Validation

#### JSON Schema Definitions

**Detection Schema**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Detection",
  "type": "object",
  "required": ["detection_id", "timestamp", "class", "confidence", "bbox", "location"],
  "properties": {
    "detection_id": {
      "type": "string",
      "pattern": "^det_[a-zA-Z0-9]+$"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "uav_id": {
      "type": "string",
      "pattern": "^uav_[0-9]+$"
    },
    "class": {
      "type": "string",
      "enum": ["person", "vehicle", "animal"]
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "bbox": {
      "type": "object",
      "required": ["x", "y", "width", "height"],
      "properties": {
        "x": {"type": "number"},
        "y": {"type": "number"},
        "width": {"type": "number", "minimum": 0},
        "height": {"type": "number", "minimum": 0}
      }
    },
    "location": {
      "type": "object",
      "required": ["latitude", "longitude"],
      "properties": {
        "latitude": {"type": "number", "minimum": -90, "maximum": 90},
        "longitude": {"type": "number", "minimum": -180, "maximum": 180},
        "altitude": {"type": "number"}
      }
    }
  }
}
```

**Telemetry Schema**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "UAV Telemetry",
  "type": "object",
  "required": ["uav_id", "timestamp", "position", "battery", "status"],
  "properties": {
    "uav_id": {
      "type": "string",
      "pattern": "^uav_[0-9]+$"
    },
    "timestamp": {
      "type": "number",
      "minimum": 0
    },
    "position": {
      "type": "object",
      "required": ["lat", "lon", "alt", "heading"],
      "properties": {
        "lat": {"type": "number", "minimum": -90, "maximum": 90},
        "lon": {"type": "number", "minimum": -180, "maximum": 180},
        "alt": {"type": "number", "minimum": 0},
        "heading": {"type": "number", "minimum": 0, "maximum": 360}
      }
    },
    "velocity": {
      "type": "object",
      "properties": {
        "vx": {"type": "number"},
        "vy": {"type": "number"},
        "vz": {"type": "number"}
      }
    },
    "battery": {
      "type": "object",
      "required": ["voltage", "percent"],
      "properties": {
        "voltage": {"type": "number", "minimum": 0},
        "current": {"type": "number"},
        "percent": {"type": "integer", "minimum": 0, "maximum": 100},
        "time_remaining": {"type": "integer", "minimum": 0}
      }
    },
    "status": {
      "type": "object",
      "required": ["mode", "armed", "gps_fix"],
      "properties": {
        "mode": {"type": "string", "enum": ["manual", "mission", "loiter", "rtl"]},
        "armed": {"type": "boolean"},
        "gps_fix": {"type": "string", "enum": ["none", "2d", "3d", "rtk"]},
        "satellites": {"type": "integer", "minimum": 0}
      }
    }
  }
}
```

#### Validation Example

```python
from jsonschema import validate, ValidationError
import json

def validate_detection(detection_data):
    """Validate detection message against schema."""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Detection",
        "type": "object",
        "required": ["detection_id", "timestamp", "class", "confidence"],
        "properties": {
            "detection_id": {"type": "string"},
            "timestamp": {"type": "string", "format": "date-time"},
            "class": {"type": "string", "enum": ["person", "vehicle", "animal"]},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1}
        }
    }
    
    try:
        validate(instance=detection_data, schema=schema)
        return True, None
    except ValidationError as e:
        return False, str(e)

# Example usage
detection = {
    "detection_id": "det_abc123",
    "timestamp": "2025-11-09T14:32:15.234Z",
    "class": "person",
    "confidence": 0.92
}

is_valid, error = validate_detection(detection)
if is_valid:
    print("Detection is valid")
else:
    print(f"Validation error: {error}")
```

---

## Key Takeaways

✅ **REST API**: 40+ endpoints for detections, alerts, missions, UAVs, zones, analytics  
✅ **WebSocket**: Real-time telemetry, detections, alerts with <1s latency  
✅ **MQTT**: Hierarchical topic structure, QoS 0/1/2, pub/sub messaging  
✅ **Authentication**: JWT Bearer tokens, OAuth 2.0 support  
✅ **Rate Limiting**: 1K-10K requests/hour based on tier  
✅ **Schema Validation**: JSON Schema for all message types  
✅ **Error Handling**: Standardized error responses with request IDs  

---

## Navigation

- **Previous:** [Data & Model Specs (Appendix B)](./APPENDIX_B_DATA_MODELS.md)
- **Next:** [Security Plan (Appendix D)](./APPENDIX_D_SECURITY.md)
- **Home:** [Documentation Index](./README.md)

---

**Document Status:** ✅ Complete  
**Last Updated:** November 9, 2025  
**Review Cycle:** Quarterly
