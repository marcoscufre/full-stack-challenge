import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { TripProvider } from './hooks/useTrip';
import LandingPage from './features/LandingPage';
import TripPlannerForm from './features/TripPlannerForm';
import Dashboard from './features/Dashboard';
import EldLogsPage from './features/EldLogsPage';

function App() {
  return (
    <TripProvider>
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/plan" element={<TripPlannerForm />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/logs" element={<EldLogsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </TripProvider>
  );
}

export default App;
