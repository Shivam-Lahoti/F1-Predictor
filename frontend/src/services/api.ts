import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Circuit {
  id: number;
  name: string;
  location: string;
  country: string;
}

export interface Race {
  id: number;
  year: number;
  round_number: number;
  race_name: string;
  race_date: string | null;
  Circuit?: Circuit;
}

export interface RaceResult {
  driver_name: string;
  driver_code: string;
  grid_position: number | null;
  final_position: number | null;
  points: number;
}

export const raceAPI = {
  getRaces: async (year?: number): Promise<Race[]> => {
    const response = await api.get('/api/races', { 
      params: year ? { year } : {} 
    });
    return response.data;
  },

  getRace: async (raceId: number): Promise<Race> => {
    const response = await api.get(`/api/races/${raceId}`);
    return response.data;
  },

  getRaceResults: async (raceId: number): Promise<RaceResult[]> => {
    const response = await api.get(`/api/races/${raceId}/results`);
    return response.data;
  },
};

export default api;