import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from './AuthContext';
import './Dashboard.css';
import { getApiCandidates, getWsCandidates, fetchWithFallback } from './apiClient';

// Client-side logging helper that also writes a small in-page buffer
function logClient(...args) {
  try {
    if (typeof window !== 'undefined') {
      window.__EVENT_DEBUG_LOG = window.__EVENT_DEBUG_LOG || [];
      const text = args.map(a => (typeof a === 'object' ? JSON.stringify(a) : String(a))).join(' ');
      window.__EVENT_DEBUG_LOG.push(`${new Date().toISOString()} ${text}`);
      // Keep buffer short
      if (window.__EVENT_DEBUG_LOG.length > 200) window.__EVENT_DEBUG_LOG.shift();
    }
  } catch (e) {}
  // Also emit to normal console so developers can see it
  // eslint-disable-next-line no-console
  console.debug(...args);
}

function warnClient(...args) {
  try { if (typeof window !== 'undefined') { window.__EVENT_DEBUG_LOG = window.__EVENT_DEBUG_LOG || []; window.__EVENT_DEBUG_LOG.push(`${new Date().toISOString()} WARN ${args.join(' ')}`); if (window.__EVENT_DEBUG_LOG.length > 200) window.__EVENT_DEBUG_LOG.shift(); } } catch(e) {}
  // eslint-disable-next-line no-console
  console.warn(...args);
}

function errorClient(...args) {
  try { if (typeof window !== 'undefined') { window.__EVENT_DEBUG_LOG = window.__EVENT_DEBUG_LOG || []; window.__EVENT_DEBUG_LOG.push(`${new Date().toISOString()} ERROR ${args.join(' ')}`); if (window.__EVENT_DEBUG_LOG.length > 200) window.__EVENT_DEBUG_LOG.shift(); } } catch(e) {}
  // eslint-disable-next-line no-console
  console.error(...args);
}

// Centralized API client functions live in `apiClient.js` to ensure consistent
// candidate selection and fallback behavior across dashboard modules.

// WebSocket connection manager
class WebSocketManager {
  constructor() {
    this.connections = {};
    this.reconnectTimers = {};
  }

  connect(channel, token, onMessage) {
    const candidates = getWsCandidates();
    let ws = null;
    let connected = false;
    logClient(`WebSocketManager: connecting channel='${channel}' tokenPresent=${!!token} candidates=`, candidates);
    const tryConnect = (index = 0) => {
      if (index >= candidates.length) {
        // All candidates failed; schedule reconnect
        this.reconnectTimers[channel] = setTimeout(() => {
          tryConnect(0);
        }, 5000);
        return;
      }

      const url = `${candidates[index]}/ws/${channel}?token=${token}`;
      logClient('WebSocketManager: attempting', url);
      try {
        ws = new WebSocket(url);
      } catch (err) {
        errorClient(`WebSocket construction failed for ${url}:`, err && err.message ? err.message : err);
        // try next candidate
        tryConnect(index + 1);
        return;
      }

      ws.onopen = () => {
        connected = true;
        console.log(`✓ Connected to ${channel} via ${url}`);
        if (this.reconnectTimers[channel]) {
          clearTimeout(this.reconnectTimers[channel]);
          delete this.reconnectTimers[channel];
        }
        this.connections[channel] = ws;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (e) {
          console.error('WebSocket message parse error:', e);
        }
      };

      ws.onerror = (error) => {
        errorClient(`WebSocket error on ${channel} (${url}):`, error && error.message ? error.message : error);
      };

      ws.onclose = (ev) => {
        // If we were not connected and closed quickly, try next candidate
        logClient(`WebSocket closed for ${url} code=${ev.code} reason=${ev.reason}`);
        if (!connected) {
          console.log(`Connection to ${url} failed, trying next candidate`);
          tryConnect(index + 1);
          return;
        }
        console.log(`Disconnected from ${channel} (was connected)`);
        // Auto-reconnect after 5 seconds
        this.reconnectTimers[channel] = setTimeout(() => {
          tryConnect(0);
        }, 5000);
      };
    };

    tryConnect(0);
    return {
      close: () => ws && ws.close(),
    };
  }

  disconnect(channel) {
    if (this.connections[channel]) {
      this.connections[channel].close();
      delete this.connections[channel];
    }
    if (this.reconnectTimers[channel]) {
      clearTimeout(this.reconnectTimers[channel]);
      delete this.reconnectTimers[channel];
    }
  }

  disconnectAll() {
    Object.keys(this.connections).forEach(channel => this.disconnect(channel));
  }
}

const wsManager = new WebSocketManager();

const EnhancedDashboard = () => {
  // Authentication
  const { user, token, logout } = useAuth();
  
  // Real-time data
  const [uavs, setUavs] = useState([]);
  const [missions, setMissions] = useState([]);
  const [detections, setDetections] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [telemetry, setTelemetry] = useState({});
  
  // Analytics
  const [metrics, setMetrics] = useState(null);
  const [coverage, setCoverage] = useState(null);
  
  // UI state
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedUav, setSelectedUav] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);



  // Initialize WebSocket connections
  const initializeWebSockets = useCallback((authToken) => {
    // Telemetry updates
    wsManager.connect('telemetry', authToken, (data) => {
      setTelemetry(prev => ({
        ...prev,
        [data.uav_id]: data
      }));
    });

    // Detection stream
    wsManager.connect('detections', authToken, (data) => {
      setDetections(prev => [data, ...prev].slice(0, 50)); // Keep last 50
    });

    // Alert stream
    wsManager.connect('alerts', authToken, (data) => {
      setAlerts(prev => [data, ...prev].slice(0, 20)); // Keep last 20
      // Play alert sound
      playAlertSound(data.priority);
    });

    // Mission updates
    wsManager.connect('missions', authToken, (data) => {
      setMissions(prev => {
        const index = prev.findIndex(m => m.mission_id === data.mission_id);
        if (index >= 0) {
          const updated = [...prev];
          updated[index] = data;
          return updated;
        }
        return [data, ...prev];
      });
    });
  }, []);

  // Load initial data
  const loadInitialData = async (authToken) => {
    const headers = {
      'Authorization': `Bearer ${authToken}`,
      'Content-Type': 'application/json'
    };

    try {
      // Load UAVs
      const uavsRes = await fetchWithFallback('/api/v1/uavs', { headers });
      const uavsData = await uavsRes.json();
      setUavs(uavsData);

      // Load missions
      const missionsRes = await fetchWithFallback('/api/v1/missions', { headers });
      const missionsData = await missionsRes.json();
      setMissions(missionsData);

      // Load analytics
      const metricsRes = await fetchWithFallback('/api/v2/analytics/performance', { headers });
      const metricsData = await metricsRes.json();
      setMetrics(metricsData);

      const coverageRes = await fetchWithFallback('/api/v2/analytics/coverage', { headers });
      const coverageData = await coverageRes.json();
      setCoverage(coverageData);
    } catch (err) {
      console.error('Error loading data:', err);
    }
  };


  // Initialize data on mount
  useEffect(() => {
    if (token) {
       initializeWebSockets(token);
       loadInitialData(token); 
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  // Play alert sound based on priority
  const playAlertSound = (priority) => {
    const audio = new Audio();
    if (priority === 'high') {
      audio.src = '/sounds/alert-high.mp3';
    } else {
      audio.src = '/sounds/alert-medium.mp3';
    }
    audio.play().catch(e => console.log('Audio play failed:', e));
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      wsManager.disconnectAll();
    };
  }, []);

  // Auto-refresh metrics every 30 seconds
  useEffect(() => {
    if (!token) return;

    const interval = setInterval(() => {
      loadInitialData(token);
    }, 30000);

    return () => clearInterval(interval);
  }, [token]);

  // Main dashboard
  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-left">
          <h1>🛰️ EVENT Dashboard</h1>
          <div className="header-status">
            <span className={`status-indicator ${alerts.length > 0 ? 'alert' : 'normal'}`}></span>
            <span>System Operational</span>
          </div>
        </div>
        
        <div className="header-right">
          <div className="user-info">
            <span>👤 {user?.username}</span>
            <button onClick={logout}>Logout</button>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="dashboard-nav">
        <button
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={activeTab === 'uavs' ? 'active' : ''}
          onClick={() => setActiveTab('uavs')}
        >
          UAVs ({uavs.length})
        </button>
        <button
          className={activeTab === 'missions' ? 'active' : ''}
          onClick={() => setActiveTab('missions')}
        >
          Missions ({missions.length})
        </button>
        <button
          className={activeTab === 'detections' ? 'active' : ''}
          onClick={() => setActiveTab('detections')}
        >
          Detections ({detections.length})
        </button>
        <button
          className={activeTab === 'alerts' ? 'active' : ''}
          onClick={() => setActiveTab('alerts')}
        >
          Alerts ({alerts.length})
        </button>
        <button
          className={activeTab === 'analytics' ? 'active' : ''}
          onClick={() => setActiveTab('analytics')}
        >
          Analytics
        </button>
      </nav>

      {/* Main Content */}
      <main className="dashboard-content">
        {activeTab === 'overview' && (
          <OverviewTab
            uavs={uavs}
            missions={missions}
            detections={detections}
            alerts={alerts}
            metrics={metrics}
            telemetry={telemetry}
          />
        )}
        
        {activeTab === 'uavs' && (
          <UAVsTab
            uavs={uavs}
            telemetry={telemetry}
            selectedUav={selectedUav}
            setSelectedUav={setSelectedUav}
          />
        )}
        
        {activeTab === 'missions' && (
          <MissionsTab missions={missions} token={token} />
        )}
        
        {activeTab === 'detections' && (
          <DetectionsTab detections={detections} />
        )}
        
        {activeTab === 'alerts' && (
          <AlertsTab alerts={alerts} />
        )}
        
        {activeTab === 'analytics' && (
          <AnalyticsTab metrics={metrics} coverage={coverage} />
        )}
      </main>
    </div>
  );
};

// Overview Tab Component
const OverviewTab = ({ uavs, missions, detections, alerts, metrics, telemetry }) => {
  const activeUavs = uavs.filter(u => u.status === 'active').length;
  const activeMissions = missions.filter(m => m.status === 'active').length;
  const recentDetections = detections.slice(0, 5);
  const recentAlerts = alerts.slice(0, 3);

  return (
    <div className="overview-tab">
      {/* Key Metrics */}
      <div className="metrics-grid">
        <div className="metric-card">
          <h3>Active UAVs</h3>
          <div className="metric-value">{activeUavs} / {uavs.length}</div>
          <div className="metric-label">operational</div>
        </div>
        
        <div className="metric-card">
          <h3>Active Missions</h3>
          <div className="metric-value">{activeMissions}</div>
          <div className="metric-label">in progress</div>
        </div>
        
        <div className="metric-card">
          <h3>Detections (24h)</h3>
          <div className="metric-value">{metrics?.total_detections || 0}</div>
          <div className="metric-label">{metrics?.detection_rate?.toFixed(1) || 0}/hr</div>
        </div>
        
        <div className="metric-card alert">
          <h3>Active Alerts</h3>
          <div className="metric-value">{alerts.length}</div>
          <div className="metric-label">requiring attention</div>
        </div>
      </div>

      {/* Live Map Placeholder */}
      <div className="map-container">
        <h3>Live Map</h3>
        <div className="map-placeholder">
          <p>🗺️ Real-time UAV positions and detection zones</p>
          <p className="map-hint">In production: Integrate with Leaflet/Mapbox for interactive map</p>
          
          {/* Show UAV positions */}
          <div className="uav-markers">
            {Object.entries(telemetry).map(([uavId, data]) => (
              <div key={uavId} className="uav-marker">
                🚁 {uavId}: ({data.latitude?.toFixed(4)}, {data.longitude?.toFixed(4)})
                - Battery: {data.battery_level}%
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="activity-grid">
        <div className="activity-panel">
          <h3>Recent Detections</h3>
          <div className="activity-list">
            {recentDetections.map((detection, idx) => (
              <div key={idx} className="activity-item">
                <span className="activity-icon">🎯</span>
                <div className="activity-details">
                  <strong>{detection.detection_type}</strong>
                  <small>Confidence: {(detection.confidence * 100).toFixed(1)}%</small>
                </div>
                <span className="activity-time">{new Date(detection.timestamp).toLocaleTimeString()}</span>
              </div>
            ))}
          </div>
        </div>
        
        <div className="activity-panel">
          <h3>Recent Alerts</h3>
          <div className="activity-list">
            {recentAlerts.map((alert, idx) => (
              <div key={idx} className={`activity-item priority-${alert.priority}`}>
                <span className="activity-icon">🚨</span>
                <div className="activity-details">
                  <strong>{alert.alert_type}</strong>
                  <small>Priority: {alert.priority}</small>
                </div>
                <span className="activity-time">{new Date(alert.timestamp).toLocaleTimeString()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// UAVs Tab Component
const UAVsTab = ({ uavs, telemetry, selectedUav, setSelectedUav }) => {
  return (
    <div className="uavs-tab">
      <div className="uavs-grid">
        {uavs.map(uav => {
          const live = telemetry[uav.uav_id];
          return (
            <div
              key={uav.uav_id}
              className={`uav-card ${uav.status} ${selectedUav === uav.uav_id ? 'selected' : ''}`}
              onClick={() => setSelectedUav(uav.uav_id)}
            >
              <div className="uav-header">
                <h3>🚁 {uav.uav_id}</h3>
                <span className={`status-badge ${uav.status}`}>{uav.status}</span>
              </div>
              
              <div className="uav-stats">
                <div className="stat">
                  <label>Battery</label>
                  <div className="battery-indicator">
                    <div
                      className="battery-fill"
                      style={{
                        width: `${uav.battery_level}%`,
                        backgroundColor: uav.battery_level > 50 ? '#4caf50' : uav.battery_level > 20 ? '#ff9800' : '#f44336'
                      }}
                    />
                    <span>{uav.battery_level}%</span>
                  </div>
                </div>
                
                {live && (
                  <>
                    <div className="stat">
                      <label>Position</label>
                      <value>
                        {live.latitude?.toFixed(4)}, {live.longitude?.toFixed(4)}
                      </value>
                    </div>
                    
                    <div className="stat">
                      <label>Altitude</label>
                      <value>{live.altitude?.toFixed(1)} m</value>
                    </div>
                    
                    <div className="stat">
                      <label>Speed</label>
                      <value>{live.speed?.toFixed(1)} m/s</value>
                    </div>
                  </>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Missions Tab Component
const MissionsTab = ({ missions, token }) => {
  return (
    <div className="missions-tab">
      <div className="missions-table">
        <table>
          <thead>
            <tr>
              <th>Mission ID</th>
              <th>UAV</th>
              <th>Status</th>
              <th>Target</th>
              <th>Progress</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {missions.map(mission => (
              <tr key={mission.mission_id}>
                <td><strong>{mission.mission_id}</strong></td>
                <td>{mission.uav_id}</td>
                <td><span className={`status-badge ${mission.status}`}>{mission.status}</span></td>
                <td>
                  {mission.target_lat?.toFixed(4)}, {mission.target_lon?.toFixed(4)}
                </td>
                <td>
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{ width: `${(mission.progress || 0) * 100}%` }}
                    />
                  </div>
                </td>
                <td>{new Date(mission.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Detections Tab Component
const DetectionsTab = ({ detections }) => {
  return (
    <div className="detections-tab">
      <div className="detections-list">
        {detections.map((detection, idx) => (
          <div key={idx} className="detection-card">
            <div className="detection-header">
              <h4>{detection.detection_type || 'Unknown'}</h4>
              <span className="detection-confidence">
                {(detection.confidence * 100).toFixed(1)}%
              </span>
            </div>
            
            <div className="detection-details">
              <div className="detail">
                <label>Location:</label>
                <span>{detection.latitude?.toFixed(4)}, {detection.longitude?.toFixed(4)}</span>
              </div>
              <div className="detail">
                <label>UAV:</label>
                <span>{detection.uav_id}</span>
              </div>
              <div className="detail">
                <label>Time:</label>
                <span>{new Date(detection.timestamp).toLocaleString()}</span>
              </div>
            </div>
            
            {detection.image_url && (
              <div className="detection-image">
                <img src={detection.image_url} alt="Detection" />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

// Alerts Tab Component
const AlertsTab = ({ alerts }) => {
  return (
    <div className="alerts-tab">
      <div className="alerts-list">
        {alerts.map((alert, idx) => (
          <div key={idx} className={`alert-card priority-${alert.priority}`}>
            <div className="alert-header">
              <span className="alert-icon">🚨</span>
              <h4>{alert.alert_type}</h4>
              <span className={`priority-badge ${alert.priority}`}>{alert.priority}</span>
            </div>
            
            <div className="alert-details">
              <p><strong>Location:</strong> {alert.latitude?.toFixed(4)}, {alert.longitude?.toFixed(4)}</p>
              <p><strong>Source:</strong> {alert.source}</p>
              <p><strong>Time:</strong> {new Date(alert.timestamp).toLocaleString()}</p>
              {alert.description && <p><strong>Description:</strong> {alert.description}</p>}
            </div>
            
            <div className="alert-actions">
              <button className="btn-primary">Assign Mission</button>
              <button className="btn-secondary">Dismiss</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Analytics Tab Component
const AnalyticsTab = ({ metrics, coverage }) => {
  return (
    <div className="analytics-tab">
      <h2>System Performance</h2>
      
      {metrics && (
        <div className="analytics-grid">
          <div className="analytics-card">
            <h3>Detection Rate</h3>
            <div className="analytics-value">{metrics.detection_rate?.toFixed(2)}</div>
            <div className="analytics-label">per hour</div>
          </div>
          
          <div className="analytics-card">
            <h3>Response Time (Avg)</h3>
            <div className="analytics-value">{metrics.response_time_avg?.toFixed(1)}s</div>
            <div className="analytics-label">P95: {metrics.response_time_p95?.toFixed(1)}s</div>
          </div>
          
          <div className="analytics-card">
            <h3>UAV Utilization</h3>
            <div className="analytics-value">{metrics.uav_utilization?.toFixed(1)}%</div>
            <div className="analytics-label">active time</div>
          </div>
          
          <div className="analytics-card">
            <h3>Mission Success Rate</h3>
            <div className="analytics-value">{metrics.mission_success_rate?.toFixed(1)}%</div>
            <div className="analytics-label">{metrics.total_missions} total</div>
          </div>
        </div>
      )}
      
      {coverage && (
        <>
          <h2>Coverage Analysis</h2>
          <div className="analytics-grid">
            <div className="analytics-card">
              <h3>Total Coverage</h3>
              <div className="analytics-value">{coverage.coverage_percentage?.toFixed(1)}%</div>
              <div className="analytics-label">{coverage.covered_area_km2?.toFixed(2)} km²</div>
            </div>
            
            <div className="analytics-card">
              <h3>Coverage Gaps</h3>
              <div className="analytics-value">{coverage.gaps?.length || 0}</div>
              <div className="analytics-label">areas needing attention</div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default EnhancedDashboard;
