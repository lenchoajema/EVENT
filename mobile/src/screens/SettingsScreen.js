import React, { useContext } from 'react';
import { Button, View, Text, StyleSheet } from 'react-native';
import { AuthContext } from '../context/AuthContext';

export default function SettingsScreen() {
  const { logout, user } = useContext(AuthContext);

  return (
    <View style={styles.container}>
      <Text style={styles.text}>Logged in as: {user?.username}</Text>
      <View style={styles.spacer} />
      <Button title="Logout" onPress={logout} color="#d9534f" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, alignItems: 'center', justifyContent: 'center' },
  text: { fontSize: 18, marginBottom: 20 },
  spacer: { height: 20 },
});
