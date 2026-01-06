import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet, RefreshControl } from 'react-native';
import { getAlerts } from '../api/client';

export default function AlertsScreen() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchAlerts = async () => {
    try {
      const resp = await getAlerts();
      setAlerts(resp.data);
    } catch (err) {
      console.error("Failed to fetch alerts", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchAlerts();
  };

  const renderItem = ({ item }) => (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.eventType}>{item.event_type?.toUpperCase()}</Text>
        <Text style={[styles.badge, styles[item.severity]]}>{item.severity}</Text>
      </View>
      <Text>Location: {item.latitude?.toFixed(4)}, {item.longitude?.toFixed(4)}</Text>
      <Text>Confidence: {(item.confidence * 100).toFixed(1)}%</Text>
      <Text style={styles.date}>{new Date(item.created_at).toLocaleString()}</Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={alerts}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderItem}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        ListEmptyComponent={<Text style={styles.empty}>No active alerts</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 10, backgroundColor: '#f0f0f0' },
  card: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    elevation: 2,
  },
  header: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 5 },
  eventType: { fontWeight: 'bold', fontSize: 16 },
  date: { color: '#666', fontSize: 12, marginTop: 5 },
  badge: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 4, overflow:'hidden', color:'#fff', fontSize:12 },
  critical: { backgroundColor: 'red' },
  high: { backgroundColor: 'orange' },
  medium: { backgroundColor: '#f4c242' },
  low: { backgroundColor: 'green' },
  empty: { textAlign: 'center', marginTop: 50, color: '#888' },
});
