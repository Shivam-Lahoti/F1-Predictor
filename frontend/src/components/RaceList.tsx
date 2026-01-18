import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

const RaceList = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();
  
  const selectedYear = searchParams.get('year') 
    ? Number(searchParams.get('year')) 
    : 2015;

  const years = [2015, 2016, 2017, 2018, 2024];
  
  // Mock data - will be replaced with real API data
  const raceData: { [key: number]: any[] } = {
    2015: [
      { id: 1, round: 1, name: 'Australian Grand Prix', circuit: 'Albert Park Circuit', location: 'Melbourne, Australia', date: '2015-03-15' },
      { id: 2, round: 2, name: 'Malaysian Grand Prix', circuit: 'Sepang International Circuit', location: 'Kuala Lumpur, Malaysia', date: '2015-03-29' },
      { id: 3, round: 3, name: 'Chinese Grand Prix', circuit: 'Shanghai International Circuit', location: 'Shanghai, China', date: '2015-04-12' },
      // Add more...
    ],
    2016: [
      { id: 21, round: 1, name: 'Australian Grand Prix', circuit: 'Albert Park Circuit', location: 'Melbourne, Australia', date: '2016-03-20' },
      { id: 22, round: 2, name: 'Bahrain Grand Prix', circuit: 'Bahrain International Circuit', location: 'Sakhir, Bahrain', date: '2016-04-03' },
      // Add more...
    ],
    2017: [
      { id: 41, round: 1, name: 'Australian Grand Prix', circuit: 'Albert Park Circuit', location: 'Melbourne, Australia', date: '2017-03-26' },
      { id: 42, round: 2, name: 'Chinese Grand Prix', circuit: 'Shanghai International Circuit', location: 'Shanghai, China', date: '2017-04-09' },
      { id: 43, round: 3, name: 'Bahrain Grand Prix', circuit: 'Bahrain International Circuit', location: 'Sakhir, Bahrain', date: '2017-04-16' },
      // Add more to reach 20 races
    ],
    2018: [
      { id: 61, round: 1, name: 'Australian Grand Prix', circuit: 'Albert Park Circuit', location: 'Melbourne, Australia', date: '2018-03-25' },
      // Add more...
    ],
    2024: [
      { id: 81, round: 7, name: 'Monaco Grand Prix', circuit: 'Circuit de Monaco', location: 'Monte Carlo, Monaco', date: '2024-05-26' },
    ]
  };

  const races = raceData[selectedYear] || [];
  const filteredRaces = races.filter(race => 
    race.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    race.location.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-b from-f1-dark via-f1-darker to-black pb-20">
      
      {/* Header Section */}
      <div className="bg-gradient-to-b from-f1-dark to-transparent border-b border-gray-800/50">
        <div className="container mx-auto px-4 py-12">
          
          {/* Back Button */}
          <button
            onClick={() => navigate('/')}
            className="text-gray-400 hover:text-white mb-6 flex items-center gap-2 group transition-colors"
          >
            <span className="transform group-hover:-translate-x-1 transition-transform text-xl">←</span>
            <span className="font-medium">Back to Home</span>
          </button>
          
          {/* Page Title */}
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
              {filteredRaces.length} race{filteredRaces.length !== 1 ? 's' : ''} found in {selectedYear} season
            </p>
          </div>
          
          {/* Search Bar */}
          <div className="max-w-2xl">
            <div className="relative">
              <input
                type="text"
                placeholder="Search by race name or location..."
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
                className={`relative group px-8 py-4 rounded-xl font-bold text-lg transition-all ${
                  selectedYear === year
                    ? 'bg-f1-red text-white shadow-neon-red scale-105'
                    : 'bg-f1-gray-800 text-gray-300 hover:bg-f1-gray-700 border border-gray-700 hover:border-f1-red'
                }`}
              >
                <span className="relative z-10">{year}</span>
                
                {/* Active indicator dot */}
                {selectedYear === year && (
                  <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-white rounded-full animate-pulse"></div>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Race Cards Grid */}
        {filteredRaces.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredRaces.map((race, index) => (
              <div
                key={race.id}
                onClick={() => alert('Race details coming soon!')}
                className="group relative animate-slide-up cursor-pointer"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                {/* Card hover glow */}
                <div className="absolute -inset-0.5 bg-gradient-to-r from-f1-red to-orange-600 rounded-2xl blur opacity-0 group-hover:opacity-30 transition-opacity"></div>
                
                <div className="relative bg-gradient-to-br from-f1-gray-800 to-f1-gray-700 rounded-2xl p-6 border border-gray-700 hover:border-f1-red transition-all shadow-glow hover:shadow-2xl transform hover:scale-105">
                  
                  {/* Header with round badge */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="bg-f1-red/20 border border-f1-red/50 text-f1-red px-4 py-2 rounded-full text-sm font-black">
                      ROUND {race.round}
                    </div>
                    <div className="text-4xl group-hover:animate-float">🏁</div>
                  </div>
                  
                  {/* Race Name */}
                  <h3 className="text-2xl font-bold mb-4 group-hover:text-f1-red transition-colors leading-tight">
                    {race.name}
                  </h3>
                  
                  {/* Circuit & Location Info */}
                  <div className="space-y-3 mb-6">
                    <div className="flex items-start gap-3 text-gray-400">
                      <span className="text-xl flex-shrink-0">🏟️</span>
                      <span className="text-sm leading-relaxed">{race.circuit}</span>
                    </div>
                    <div className="flex items-start gap-3 text-gray-400">
                      <span className="text-xl flex-shrink-0">📍</span>
                      <span className="text-sm leading-relaxed">{race.location}</span>
                    </div>
                    <div className="flex items-start gap-3 text-gray-400">
                      <span className="text-xl flex-shrink-0">📅</span>
                      <span className="text-sm leading-relaxed">
                        {new Date(race.date).toLocaleDateString('en-US', {
                          weekday: 'long',
                          month: 'long',
                          day: 'numeric',
                          year: 'numeric'
                        })}
                      </span>
                    </div>
                  </div>
                  
                  {/* Footer with action */}
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
        ) : (
          // Empty state
          <div className="text-center py-20 bg-f1-gray-800/50 rounded-3xl border border-gray-700">
            <div className="text-8xl mb-6 opacity-50">🔍</div>
            <h3 className="text-3xl font-bold mb-3">No races found</h3>
            <p className="text-gray-400 text-lg">
              Try a different search term or select another year
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RaceList;
