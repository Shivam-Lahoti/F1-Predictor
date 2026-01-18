import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import type { Race } from '../services/api';
import { raceAPI } from '../services/api';

const RaceList = () => {
  const [races, setRaces] = useState<Race[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const selectedYear = searchParams.get('year') 
    ? Number(searchParams.get('year')) 
    : 2017;

  // All available years (2015-2025)
  const years = [2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015];

  // Load races from API when year changes
  useEffect(() => {
    loadRaces();
  }, [selectedYear]);

  const loadRaces = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log(`Fetching races for year: ${selectedYear}`);
      const data = await raceAPI.getRaces(selectedYear);
      console.log(`Received ${data.length} races`, data);
      setRaces(data);
    } catch (err) {
      console.error('Error loading races:', err);
      setError('Failed to load races. Make sure backend is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };
  
  const filteredRaces = races.filter(race => 
    race.race_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (race.Circuit?.name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (race.Circuit?.location || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-b from-f1-dark via-f1-darker to-black pb-20">
      
      {/* Header Section */}
      <div className="bg-gradient-to-b from-f1-dark to-transparent border-b border-gray-800/50">
        <div className="container mx-auto px-4 py-12">
          
          <button
            onClick={() => navigate('/')}
            className="text-gray-400 hover:text-white mb-6 flex items-center gap-2 group transition-colors"
          >
            <span className="transform group-hover:-translate-x-1 transition-transform text-xl">←</span>
            <span className="font-medium">Back to Home</span>
          </button>
          
          <div className="mb-8">
            <div className="flex items-center gap-4 mb-4">
              <img 
                src="/images/f1-logo.png" 
                alt="F1" 
                className="h-16 w-auto object-contain"
              />
              <h1 className="text-6xl md:text-7xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                Race Browser
              </h1>
            </div>
            <p className="text-gray-400 text-xl">
              {loading ? 'Loading...' : `${filteredRaces.length} race${filteredRaces.length !== 1 ? 's' : ''} in ${selectedYear} season`}
            </p>
          </div>
          
          <div className="max-w-2xl">
            <div className="relative">
              <input
                type="text"
                placeholder="Search by race name, Circuit, or location..."
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
        
        {/* Year Selector */}
        <div className="mb-12">
          <div className="flex items-center gap-3 mb-6">
            <div className="h-1 w-16 bg-f1-red rounded-full"></div>
            <span className="text-sm uppercase tracking-widest text-gray-500 font-bold">
              Season Selection
            </span>
          </div>
          
          <div className="flex flex-wrap gap-3">
            {years.map((year) => (
              <button
                key={year}
                onClick={() => setSearchParams({ year: year.toString() })}
                disabled={loading}
                className={`relative group px-8 py-4 rounded-xl font-bold text-lg transition-all disabled:opacity-50 ${
                  selectedYear === year
                    ? 'bg-f1-red text-white shadow-neon-red scale-105'
                    : 'bg-f1-gray-800 text-gray-300 hover:bg-f1-gray-700 border border-gray-700 hover:border-f1-red'
                }`}
              >
                {year}
                {selectedYear === year && (
                  <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-white rounded-full animate-pulse"></div>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-900/30 border border-red-500/50 rounded-xl p-6 mb-8">
            <p className="text-red-200 text-center text-lg">{error}</p>
            <p className="text-red-300 text-center text-sm mt-2">Check that backend is running on http://localhost:8000</p>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="text-center py-20">
            <div className="inline-block animate-spin text-6xl mb-4">🏎️</div>
            <div className="text-2xl font-bold mb-2">Loading {selectedYear} races...</div>
            <div className="text-gray-400">Fetching data from database...</div>
          </div>
        )}

        {/* Race Cards Grid - REAL DATA */}
        {!loading && !error && filteredRaces.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredRaces.map((race, index) => (
              <div
                key={race.id}
                onClick={() => {
                  console.log('Race clicked:', race);
                  alert(
                    `Race Details\n\n` +
                    `${race.race_name}\n` +
                    `Round ${race.round_number}\n\n` +
                    `🏟️ Circuit: ${race.Circuit?.name || 'Circuit data unavailable'}\n` +
                    `📍 Location: ${race.Circuit?.location || 'N/A'}, ${race.Circuit?.country || 'N/A'}\n` +
                    `📅 Date: ${race.race_date ? new Date(race.race_date).toLocaleDateString() : 'N/A'}`
                  );
                }}
                className="group relative animate-slide-up cursor-pointer"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <div className="absolute -inset-0.5 bg-gradient-to-r from-f1-red to-orange-600 rounded-2xl blur opacity-0 group-hover:opacity-30 transition-opacity"></div>
                
                <div className="relative bg-gradient-to-br from-f1-gray-800 to-f1-gray-700 rounded-2xl p-6 border border-gray-700 hover:border-f1-red transition-all shadow-glow hover:shadow-2xl transform hover:scale-105">
                  
                  <div className="flex items-start justify-between mb-4">
                    <div className="bg-f1-red/20 border border-f1-red/50 text-f1-red px-4 py-2 rounded-full text-sm font-black">
                      ROUND {race.round_number}
                    </div>
                    <div className="text-4xl group-hover:animate-float">🏁</div>
                  </div>
                  
                  <h3 className="text-2xl font-bold mb-4 group-hover:text-f1-red transition-colors leading-tight">
                    {race.race_name}
                  </h3>
                  
                  <div className="space-y-3 mb-6">
                    {race.Circuit ? (
                      <>
                        <div className="flex items-start gap-3 text-gray-400">
                          <span className="text-xl flex-shrink-0">🏟️</span>
                          <span className="text-sm leading-relaxed">{race.Circuit.name}</span>
                        </div>
                        <div className="flex items-start gap-3 text-gray-400">
                          <span className="text-xl flex-shrink-0">📍</span>
                          <span className="text-sm leading-relaxed">{race.Circuit.location}, {race.Circuit.country}</span>
                        </div>
                      </>
                    ) : (
                      <div className="text-gray-500 text-sm">Circuit information loading...</div>
                    )}
                    {race.race_date && (
                      <div className="flex items-start gap-3 text-gray-400">
                        <span className="text-xl flex-shrink-0">📅</span>
                        <span className="text-sm leading-relaxed">
                          {new Date(race.race_date).toLocaleDateString('en-US', {
                            weekday: 'long',
                            month: 'long',
                            day: 'numeric',
                            year: 'numeric'
                          })}
                        </span>
                      </div>
                    )}
                  </div>
                  
                  <div className="pt-4 border-t border-gray-700 group-hover:border-f1-red transition-colors">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-500 group-hover:text-f1-red font-bold uppercase tracking-wide">
                        View Details
                      </span>
                      <span className="text-f1-red transform group-hover:translate-x-2 transition-transform text-xl">
                        →
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && filteredRaces.length === 0 && (
          <div className="text-center py-20 bg-f1-gray-800/50 rounded-3xl border border-gray-700">
            <div className="text-8xl mb-6 opacity-50">🔍</div>
            <h3 className="text-3xl font-bold mb-3">No races found</h3>
            <p className="text-gray-400 text-lg mb-6">
              {searchTerm ? 'Try a different search term' : `No races available for ${selectedYear} yet`}
            </p>
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="bg-f1-red px-6 py-3 rounded-lg font-bold hover:bg-red-700 transition-colors"
              >
                Clear Search
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default RaceList;
