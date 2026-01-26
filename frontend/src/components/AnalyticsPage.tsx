import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const AnalyticsPage = () => {
  const [circuits, setCircuits] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadCircuits();
  }, []);

  const loadCircuits = async () => {
    try {
      const response = await api.get('/api/stats/circuits/most-races?limit=15');
      setCircuits(response.data);
    } catch (error) {
      console.error('Error loading circuits:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-f1-dark via-f1-darker to-black pb-20">
      
      <div className="bg-gradient-to-b from-f1-dark to-transparent border-b border-gray-800/50">
        <div className="container mx-auto px-4 py-12">
          <button
            onClick={() => navigate('/')}
            className="text-gray-400 hover:text-white mb-6 flex items-center gap-2 group"
          >
            <span className="transform group-hover:-translate-x-1 transition-transform text-xl">←</span>
            Back to Home
          </button>

          <div className="flex items-center gap-4 mb-4">
            <img src="/images/f1-logo.png" alt="F1" className="h-16 w-auto" />
            <h1 className="text-6xl md:text-7xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              Analytics
            </h1>
          </div>
          <p className="text-gray-400 text-xl">
            Data insights from 241 races
          </p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-12">
        
        <h2 className="text-4xl font-bold mb-8">
          📊 Most Popular Circuits
        </h2>

        {loading ? (
          <div className="text-center py-20">
            <div className="inline-block animate-spin text-6xl mb-4">🏎️</div>
            <div className="text-2xl font-bold">Loading analytics...</div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {circuits.map((circuit, index) => (
              <div
                key={index}
                className="bg-gradient-to-br from-f1-gray-800 to-f1-gray-700 rounded-2xl p-6 border border-gray-700 hover:border-f1-red transition-all shadow-glow"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="text-5xl">🏁</div>
                  <div className="bg-f1-red/20 border border-f1-red/40 text-f1-red px-4 py-2 rounded-full text-sm font-bold">
                    {circuit.races_held} Races
                  </div>
                </div>
                
                <h3 className="text-2xl font-bold mb-2">{circuit.circuit_name}</h3>
                <p className="text-gray-400">
                  📍 {circuit.location}, {circuit.country}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalyticsPage;