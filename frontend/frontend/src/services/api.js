import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const plannerService = {
  healthCheck: async () => {
    const response = await apiClient.get('/health/');
    return response.data;
  },
  
  planTrip: async (payload) => {
    const response = await apiClient.post('/trips/plan/', payload);
    return response.data;
  },

  searchLocations: async (query) => {
    const response = await apiClient.get('/locations/search/', {
      params: { q: query }
    });
    return response.data.results;
  },
};

export default apiClient;
