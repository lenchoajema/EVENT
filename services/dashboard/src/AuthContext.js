import React, { createContext, useContext, useState, useEffect } from 'react';
import { fetchWithFallback } from './apiClient';
import { jwtDecode } from 'jwt-decode';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('event_token'));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (token) {
      try {
        const decoded = jwtDecode(token);
        if (decoded.exp * 1000 < Date.now()) {
          logout();
        } else {
          setUser(decoded);
        }
      } catch (e) {
        logout();
      }
    }
    setLoading(false);
  }, [token]);

  const login = async (username, password) => {
    try {
      setError(null);
      const response = await fetchWithFallback('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      
      const data = await response.json();
      if (response.ok) {
        setToken(data.access_token);
        localStorage.setItem('event_token', data.access_token);
        if (data.refresh_token) {
            localStorage.setItem('event_refresh_token', data.refresh_token);
        }
        const decoded = jwtDecode(data.access_token);
        setUser(decoded);
        return true;
      } else {
        setError(data.detail || 'Login failed');
        return false;
      }
    } catch (err) {
      setError(err.message || 'Network error');
      return false;
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('event_token');
    localStorage.removeItem('event_refresh_token');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading, error }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
