import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { plannerService } from '../services/api';

const TripContext = createContext();

export const TripProvider = ({ children }) => {
  const [tripData, setTripData] = useState(() => {
    // Attempt to hydrate from localStorage on init
    const saved = localStorage.getItem('last_trip_plan');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const planTrip = useCallback(async (payload) => {
    setLoading(true);
    setError(null);
    try {
      const data = await plannerService.planTrip(payload);
      setTripData(data);
      localStorage.setItem('last_trip_plan', JSON.stringify(data));
      return data;
    } catch (err) {
      // Map API errors to human-readable English messages
      let message = 'An unexpected error occurred during trip planning.';
      
      if (err.response) {
        const { status, data } = err.response;
        if (status === 429) {
          message = 'Rate limit exceeded. Please wait a minute before requesting another route.';
        } else if (data && data.detail) {
          message = data.detail;
          
          // Specific mapping for routing/geocoding failures
          if (message.includes('Routing failed')) {
            message = 'Truck-specific routing is unavailable for this path. Please try more specific locations.';
          } else if (message.includes('resolve location')) {
            message = 'One or more locations could not be found. Please use the autocomplete suggestions.';
          }
        }
      } else if (err.request) {
        message = 'Connection error. The server is not responding.';
      }
      
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const resetTrip = useCallback(() => {
    setTripData(null);
    setError(null);
    localStorage.removeItem('last_trip_plan');
  }, []);

  return (
    <TripContext.Provider value={{ tripData, loading, error, planTrip, resetTrip }}>
      {children}
    </TripContext.Provider>
  );
};

export const useTrip = () => {
  const context = useContext(TripContext);
  if (!context) {
    throw new Error('useTrip must be used within a TripProvider');
  }
  return context;
};
