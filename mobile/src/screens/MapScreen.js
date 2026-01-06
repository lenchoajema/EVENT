import React, { useEffect, useState } from 'react';
import { View, StyleSheet, Text } from 'react-native';
import MapView, { Marker } from 'react-native-maps';
import { getUAVs, getAlerts } from '../api/client';

export default function MapScreen() {
  const [uavs, setUAVs] = useState([]);
  const [alerts, setAlerts] = useState([]);
  
  // Default to SF
  const initialRegion = {
    latitude: 37.7749,
    longitude: -122.4194,
    latitudeDelta: 0.1,
    longitudeDelta: 0.1,
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [uavResp, alertResp] = await Promise.all([getUAVs(), getAlerts()]);
        setUAVs(uavResp.data);
        setAlerts(alertResp.data);
      } catch (err) {
        console.error(err);
      }
    };
    
    fetchData();
    const interval = setInterval(fetchData, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, []);

  return (
    <View style={styles.container}>
      <MapView style={styles.map} initialRegion={initialRegion}>
        {uavs.map((uav) => (
          uav.latitude && uav.longitude ? (
            <Marker
              key={`uav-${uav.id}`}
              coordinate={{ latitude: uav.latitude, longitude: uav.longitude }}
              title={uav.name}
              description={`Battery: ${uav.battery_level}%`}
              pinColor="blue"
            />
          ) : null
        ))}
        
        {alerts.map((alert) => (
          alert.latitude && alert.longitude ? (
            <Marker
              key={`alert-${alert.id}`}
              coordinate={{ latitude: alert.latitude, longitude: alert.longitude }}
              title={alert.event_type}
              description={alert.severity}
              pinColor="red"
            />
          ) : null
        ))}
      </MapView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  map: { width: '100%', height: '100%' },
});
