import React, { createContext, useState, useEffect } from 'react';
import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';
import { jwtDecode } from "jwt-decode"; // Correct import for v4

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStorageData();
  }, []);

  async function loadStorageData() {
    try {
      let storedToken = null;
      if (Platform.OS === 'web') {
        storedToken = localStorage.getItem('token');
      } else {
        storedToken = await SecureStore.getItemAsync('token');
      }

      if (storedToken) {
        const decoded = jwtDecode(storedToken);
        // Basic expiry check
        if (decoded.exp * 1000 > Date.now()) {
          setToken(storedToken);
          setUser({ username: decoded.sub, ...decoded });
        } else {
          logout();
        }
      }
    } catch (e) {
      console.log("Auth load error:", e);
    } finally {
      setLoading(false);
    }
  }

  const login = async (accessToken) => {
    setToken(accessToken);
    const decoded = jwtDecode(accessToken);
    setUser({ username: decoded.sub, ...decoded });
    
    if (Platform.OS === 'web') {
      localStorage.setItem('token', accessToken);
    } else {
      await SecureStore.setItemAsync('token', accessToken);
    }
  };

  const logout = async () => {
    setToken(null);
    setUser(null);
    if (Platform.OS === 'web') {
      localStorage.removeItem('token');
    } else {
      await SecureStore.deleteItemAsync('token');
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
