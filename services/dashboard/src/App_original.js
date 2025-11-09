import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import axios from 'axios';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './App.css';

// Fix for default marker icons in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [alerts, setAlerts] = useState([]);
  const [uavs, setUavs] = useState([]);
  const [detections, setDetections] = useState([]);
  const [stats, setStats] = useState({
    totalAlerts: 0,
    activeUavs: 0,
    totalDetections: 0,
  });

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [alertsRes, uavsRes, detectionsRes] = await Promise.all([
        axios.get(`${API_URL}/api/alerts`),
        axios.get(`${API_URL}/api/uavs`),
        axios.get(`${API_URL}/api/detections`),
      ]);

      setAlerts(alertsRes.data);
      setUavs(uavsRes.data);
      setDetections(detectionsRes.data);

      setStats({
        totalAlerts: alertsRes.data.length,
        activeUavs: uavsRes.data.filter(u => u.status !== 'idle').length,
        totalDetections: detectionsRes.data.length,
      });
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const createAlertIcon = (severity) => {
    const colors = {
      high: '#dc3545',
      medium: '#ffc107',
      low: '#28a745',
    };
    return L.divIcon({
      className: 'custom-icon',
      html: `<div style="background-color: ${colors[severity] || '#6c757d'}; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white;"></div>`,
    });
  };

  const createUavIcon = (status) => {
    const colors = {
      idle: '#6c757d',
      assigned: '#007bff',
      flying: '#17a2b8',
      charging: '#ffc107',
    };
    return L.divIcon({
      className: 'custom-icon',
      html: `<div style="background-color: ${colors[status] || '#6c757d'}; width: 15px; height: 15px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 5px rgba(0,0,0,0.3);"></div>`,
    });
  };

  return (
    <div className="App">
      <div className="header">
        <h1>UAV-Satellite Event Analysis Dashboard</h1>
        <div className="stats">
          <div className="stat-card">
            <h3>{stats.totalAlerts}</h3>
            <p>Total Alerts</p>
          </div>
          <div className="stat-card">
            <h3>{stats.activeUavs}</h3>
            <p>Active UAVs</p>
          </div>
          <div className="stat-card">
            <h3>{stats.totalDetections}</h3>
            <p>Detections</p>
          </div>
        </div>
      </div>

      <MapContainer center={[37.7749, -122.4194]} zoom={11} style={{ height: 'calc(100vh - 120px)' }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />

        {/* Render alerts */}
        {alerts.map((alert) => (
          <React.Fragment key={`alert-${alert.id}`}>
            <Marker
              position={[alert.latitude, alert.longitude]}
              icon={createAlertIcon(alert.severity)}
            >
              <Popup>
                <div>
                  <h4>Alert #{alert.id}</h4>
                  <p><strong>Type:</strong> {alert.alert_type}</p>
                  <p><strong>Severity:</strong> {alert.severity}</p>
                  <p><strong>Status:</strong> {alert.status}</p>
                  <p><strong>Description:</strong> {alert.description || 'N/A'}</p>
                  {alert.assigned_uav_id && (
                    <p><strong>Assigned UAV:</strong> {alert.assigned_uav_id}</p>
                  )}
                </div>
              </Popup>
            </Marker>
            <Circle
              center={[alert.latitude, alert.longitude]}
              radius={500}
              pathOptions={{ color: alert.severity === 'high' ? 'red' : alert.severity === 'medium' ? 'orange' : 'green', fillOpacity: 0.1 }}
            />
          </React.Fragment>
        ))}

        {/* Render UAVs */}
        {uavs.map((uav) => (
          uav.current_latitude && uav.current_longitude && (
            <Marker
              key={`uav-${uav.id}`}
              position={[uav.current_latitude, uav.current_longitude]}
              icon={createUavIcon(uav.status)}
            >
              <Popup>
                <div>
                  <h4>{uav.name}</h4>
                  <p><strong>Status:</strong> {uav.status}</p>
                  <p><strong>Battery:</strong> {uav.battery_level.toFixed(1)}%</p>
                  <p><strong>Position:</strong> [{uav.current_latitude.toFixed(4)}, {uav.current_longitude.toFixed(4)}]</p>
                </div>
              </Popup>
            </Marker>
          )
        ))}

        {/* Render detections */}
        {detections.map((detection) => (
          <Marker
            key={`detection-${detection.id}`}
            position={[detection.latitude, detection.longitude]}
            icon={L.divIcon({
              className: 'custom-icon',
              html: '<div style="background-color: #9c27b0; width: 10px; height: 10px; border-radius: 50%; border: 1px solid white;"></div>',
            })}
          >
            <Popup>
              <div>
                <h4>Detection #{detection.id}</h4>
                <p><strong>Object:</strong> {detection.object_class}</p>
                <p><strong>Confidence:</strong> {(detection.confidence * 100).toFixed(1)}%</p>
                <p><strong>UAV:</strong> {detection.uav_id}</p>
                {detection.alert_id && (
                  <p><strong>Alert:</strong> {detection.alert_id}</p>
                )}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}

export default App;
