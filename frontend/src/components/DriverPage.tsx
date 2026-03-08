import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

interface Driver {
  id: number;
  code: string;
  name: string;
  first_name: string;
  last_name: string;
  full_name: string;
  nationality: string;
  number: number | null;
  races: number;
  total_points: number;
  wins: number;
  podiums: number;
}

interface Season {
  year: number;
  races: number;
  points: number;
  wins: number;
  podiums: number;
  avg_position: number;
}

interface DriverSeasonData {
  driver: {
    code: string;
    name: string;
    first_name: string;
    last_name: string;
    full_name: string;
    nationality: string;
    number: number | null;
  };
  seasons: Season[];
  career_totals: {
    total_races: number;
    total_points: number;
    total_wins: number;
    total_podiums: number;
  };
}

const DriversPage = () => {
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [selectedDriver, setSelectedDriver] = useState<DriverSeasonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingSeasons, setLoadingSeasons] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadDrivers();
  }, []);

  const loadDrivers = async () => {
    try {
      const response = await api.get('/api/drivers');
      setDrivers(response.data);
    } catch (error) {
      console.error('Error loading drivers:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadDriverSeasons = async (driverCode: string) => {
    setLoadingSeasons(true);
    try {
      const response = await api.get(`/api/drivers/${driverCode}/seasons`);
      setSelectedDriver(response.data);
    } catch (error) {
      console.error('Error loading driver seasons:', error);
    } finally {
      setLoadingSeasons(false);
    }
  };

  const filteredDrivers = drivers.filter(driver => {
    const q = searchTerm.toLowerCase();
    return (
      driver.name.toLowerCase().includes(q) ||
      driver.code.toLowerCase().includes(q) ||
      (driver.first_name || '').toLowerCase().includes(q) ||
      (driver.last_name || '').toLowerCase().includes(q) ||
      (driver.full_name || '').toLowerCase().includes(q) ||
      (driver.nationality || '').toLowerCase().includes(q)
    );
  });

  return (
    <div className="min-h-screen bg-gradient-to-b from-f1-dark via-f1-darker to-black pb-20">

      {/* Header */}
      <div className="bg-gradient-to-b from-f1-dark to-transparent border-b border-gray-800/50">
        <div className="container mx-auto px-4 py-12">
          <button
            onClick={() => navigate('/')}
            className="text-gray-400 hover:text-white mb-6 flex items-center gap-2 group transition-colors"
          >
            <span className="transform group-hover:-translate-x-1 transition-transform text-xl">←</span>
            <span className="font-medium">Back to Home</span>
          </button>

          <div className="flex items-center gap-4 mb-4">
            <img src="/images/f1-logo.png" alt="F1" className="h-16 w-auto object-contain" />
            <h1 className="text-6xl md:text-7xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              Drivers
            </h1>
          </div>
          <p className="text-gray-400 text-xl">
            {loading ? 'Loading...' : `${filteredDrivers.length} drivers across 11 seasons`}
          </p>

          {/* Search */}
          <div className="max-w-2xl mt-6">
            <div className="relative">
              <input
                type="text"
                placeholder="Search by name, first name, code, or nationality..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-f1-gray-800 border border-gray-700 focus:border-f1-red rounded-xl px-6 py-4 text-white placeholder-gray-500 outline-none transition-all shadow-lg focus:shadow-neon-red"
              />
              <span className="absolute right-4 top-1/2 transform -translate-y-1/2 text-2xl text-gray-500">
                🔍
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-12">

        {loading ? (
          <div className="text-center py-20">
            <div className="inline-block animate-spin text-6xl mb-4">🏎️</div>
            <div className="text-2xl font-bold">Loading drivers...</div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

            {/* Drivers List */}
            <div className="lg:col-span-2">
              <h2 className="text-3xl font-bold mb-6">All Drivers</h2>

              <div className="bg-f1-gray-800 rounded-2xl border border-gray-700 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-f1-gray-700 border-b border-gray-600">
                      <tr>
                        <th className="text-left py-4 px-6 text-gray-300 font-bold">#</th>
                        <th className="text-left py-4 px-6 text-gray-300 font-bold">Driver</th>
                        <th className="text-center py-4 px-6 text-gray-300 font-bold">Code</th>
                        <th className="text-center py-4 px-6 text-gray-300 font-bold hidden md:table-cell">Nationality</th>
                        <th className="text-right py-4 px-6 text-gray-300 font-bold">Points</th>
                        <th className="text-center py-4 px-6 text-gray-300 font-bold hidden sm:table-cell">Wins</th>
                        <th className="text-right py-4 px-6 text-gray-300 font-bold">Races</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredDrivers.map((driver, index) => (
                        <tr
                          key={driver.code}
                          onClick={() => loadDriverSeasons(driver.code)}
                          className="border-b border-gray-800 hover:bg-f1-red/10 hover:border-f1-red cursor-pointer transition-all group"
                        >
                          <td className="py-4 px-6 text-gray-400">{index + 1}</td>
                          <td className="py-4 px-6">
                            <div className="font-bold text-lg group-hover:text-f1-red transition-colors">
                              {driver.full_name || driver.name}
                            </div>
                            <div className="text-gray-500 text-xs">{driver.name}</div>
                          </td>
                          <td className="py-4 px-6 text-center">
                            <div className="inline-block bg-f1-red/20 border border-f1-red/40 text-f1-red px-3 py-1 rounded-full text-sm font-bold">
                              {driver.code}
                            </div>
                          </td>
                          <td className="py-4 px-6 text-center text-gray-400 hidden md:table-cell">
                            {driver.nationality || 'N/A'}
                          </td>
                          <td className="py-4 px-6 text-right">
                            <div className="text-lg font-bold">{driver.total_points.toFixed(1)}</div>
                          </td>
                          <td className="py-4 px-6 text-center font-bold hidden sm:table-cell">
                            {driver.wins > 0 ? (
                              <span className="text-f1-red">{driver.wins}</span>
                            ) : (
                              <span className="text-gray-600">0</span>
                            )}
                          </td>
                          <td className="py-4 px-6 text-right text-gray-400">{driver.races}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* Driver Details Sidebar */}
            <div className="lg:col-span-1">
              {selectedDriver ? (
                <div className="bg-gradient-to-br from-f1-gray-800 to-f1-gray-700 rounded-2xl p-6 border border-f1-red shadow-neon-red sticky top-24 animate-slide-up">

                  {/* Driver Header */}
                  <div className="text-center mb-6 pb-6 border-b border-gray-700">
                    <div className="text-6xl mb-3">🏎️</div>
                    <h3 className="text-3xl font-bold mb-1">
                      {selectedDriver.driver.full_name || selectedDriver.driver.name}
                    </h3>
                    <p className="text-gray-400 text-sm mb-3">{selectedDriver.driver.name}</p>
                    <div className="flex items-center justify-center gap-3">
                      <span className="bg-f1-red/20 border border-f1-red/40 text-f1-red px-4 py-1 rounded-full text-sm font-bold">
                        {selectedDriver.driver.code}
                      </span>
                      {selectedDriver.driver.number && (
                        <span className="bg-gray-700 text-white px-4 py-1 rounded-full text-sm font-bold">
                          #{selectedDriver.driver.number}
                        </span>
                      )}
                    </div>
                    <p className="text-gray-400 mt-2">{selectedDriver.driver.nationality}</p>
                  </div>

                  {loadingSeasons ? (
                    <div className="text-center py-8">
                      <div className="inline-block animate-spin text-4xl mb-2">⏳</div>
                      <div>Loading seasons...</div>
                    </div>
                  ) : (
                    <>
                      {/* Career Totals */}
                      <div className="mb-6">
                        <h4 className="text-sm uppercase tracking-wider text-gray-500 font-bold mb-4">
                          Career Totals
                        </h4>
                        <div className="grid grid-cols-2 gap-4">
                          {[
                            { label: 'Wins',    value: selectedDriver.career_totals.total_wins,               color: 'text-f1-red' },
                            { label: 'Podiums', value: selectedDriver.career_totals.total_podiums,            color: 'text-white' },
                            { label: 'Points',  value: selectedDriver.career_totals.total_points.toFixed(0),  color: 'text-white' },
                            { label: 'Races',   value: selectedDriver.career_totals.total_races,              color: 'text-white' },
                          ].map(({ label, value, color }) => (
                            <div key={label} className="bg-f1-dark/50 rounded-lg p-4 text-center">
                              <div className={`text-3xl font-bold ${color}`}>{value}</div>
                              <div className="text-xs text-gray-400 uppercase">{label}</div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Season by Season */}
                      <div>
                        <h4 className="text-sm uppercase tracking-wider text-gray-500 font-bold mb-4">
                          Season by Season
                        </h4>
                        <div className="space-y-3 max-h-96 overflow-y-auto pr-2 custom-scrollbar">
                          {selectedDriver.seasons.map((season) => (
                            <div
                              key={season.year}
                              className="bg-f1-dark/50 rounded-lg p-4 border border-gray-700 hover:border-f1-red transition-colors"
                            >
                              <div className="flex items-center justify-between mb-3">
                                <div className="text-xl font-bold">{season.year}</div>
                                <div className="text-sm text-gray-400">{season.races} races</div>
                              </div>
                              <div className="grid grid-cols-4 gap-2 text-sm">
                                <div className="text-center">
                                  <div className="font-bold text-f1-red">{season.wins}</div>
                                  <div className="text-xs text-gray-500">W</div>
                                </div>
                                <div className="text-center">
                                  <div className="font-bold">{season.podiums}</div>
                                  <div className="text-xs text-gray-500">P</div>
                                </div>
                                <div className="text-center">
                                  <div className="font-bold">{season.points.toFixed(0)}</div>
                                  <div className="text-xs text-gray-500">Pts</div>
                                </div>
                                <div className="text-center">
                                  <div className="font-bold text-gray-400">{season.avg_position.toFixed(1)}</div>
                                  <div className="text-xs text-gray-500">Avg</div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </>
                  )}
                </div>
              ) : (
                <div className="bg-f1-gray-800 rounded-2xl p-12 border border-gray-700 text-center sticky top-24">
                  <div className="text-6xl mb-4 opacity-50">👤</div>
                  <h3 className="text-2xl font-bold mb-2">Select a Driver</h3>
                  <p className="text-gray-400">
                    Click any driver from the list to view their season-by-season performance
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: #1E1E2E; border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #E10600; border-radius: 10px; }
      `}</style>
    </div>
  );
};

export default DriversPage;