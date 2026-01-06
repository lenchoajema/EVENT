import axios from 'axios';
import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';

// In simulator/web, localhost maps differently.
// For Android Emulator use 10.0.2.2, for iOS/Web use localhost
const API_URL = Platform.OS === 'android' 
  ? 'http://10.0.2.2:8000/api' 
  : 'http://localhost:8000/api';

const client = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add Auth Token
client.interceptors.request.use(
  async (config) => {
    try {
      // On web we might use localStorage, native uses SecureStore
      let token = null;
      if (Platform.OS === 'web') {
        token = localStorage.getItem('token');
      } else {
        token = await SecureStore.getItemAsync('token');
      }
      
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error("Error retrieving token", error);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export const loginUser = async (username, password) => {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  // Using form data because FastAPI OAuth2PasswordRequestForm expects it, 
  // or JSON depending on your backend config. 
  // Based on tests, it seems your backend expects JSON for /api/auth/login
  return client.post('/auth/login', { username, password });
};

export const getAlerts = () => client.get('/satellite/alerts');
export const getUAVs = () => client.get('/uavs');
export const getDetections = () => client.get('/detections');

export default client;
