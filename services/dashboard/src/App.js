import React from 'react';
import EnhancedDashboard from './EnhancedDashboard';
import Login from './Login';
import { AuthProvider, useAuth } from './AuthContext';
import './App.css';

const Main = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="App">
        <header className="App-header">
           <p>Loading session...</p>
        </header>
      </div>
    );
  }

  if (!user) {
    return <Login />;
  }

  return (
    <div className="App">
      <EnhancedDashboard />
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <Main />
    </AuthProvider>
  );
}

export default App;
