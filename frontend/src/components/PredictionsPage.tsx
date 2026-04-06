import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

interface Prediction {
  predicted_position: number;
  predicted_score: number;
  driver_code: string;
  driver_name: string;
  broadcast_name: string;
  nationality: string;
  team: string;
  qualifying_position: number | null;
}

interface RaceInfo {
  round_number: number;
  race_name: string;
  race_date: string | null;
  circuit_name: string | null;
  country: string | null;
  location: string | null;
}

interface ModelInfo {
  trained_on: string;
  races_used: number;
  generated_at: string;
}

interface PredictionData {
  race: RaceInfo;
  predictions: Prediction[];
  model_info: ModelInfo;
}

const teamColors: Record<string, string> = {
  'Mercedes':        'border-l-teal-400',
  'Red Bull Racing': 'border-l-blue-600',
  'Ferrari':         'border-l-red-600',
  'McLaren':         'border-l-orange-500',
  'Aston Martin':    'border-l-green-600',
  'Alpine':          'border-l-pink-500',
  'Williams':        'border-l-sky-400',
  'Haas F1 Team':    'border-l-gray-400',
  'Racing Bulls':    'border-l-indigo-400',
  'Audi':            'border-l-gray-200',
  'Cadillac':        'border-l-purple-500',
};

const positionStyle = (pos: number) => {
  if (pos === 1) return 'text-yellow-400 font-black text-2xl';
  if (pos === 2) return 'text-gray-300 font-black text-2xl';
  if (pos === 3) return 'text-amber-600 font-black text-2xl';
  if (pos <= 10) return 'text-white font-bold text-xl';
  return 'text-gray-500 font-bold text-xl';
};

const PredictionsPage = () => {
  const [data, setData]       = useState<PredictionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string | null>(null);
  const [view, setView]       = useState<'grid' | 'table'>('grid');
  const navigate = useNavigate();

  useEffect(() => {
    api.get('/api/predict/next')
      .then(r => setData(r.data))
      .catch(() => setError('Failed to load predictions. Make sure the backend is running.'))
      .finally(() => setLoading(false));
  }, []);

  const hasQuali = data?.predictions.some(p => p.qualifying_position != null);

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
            <div>
              <h1 className="text-6xl md:text-7xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                Predictions
              </h1>
              <p className="text-gray-400 text-lg mt-1">ML-powered race outcome predictions</p>
            </div>
          </div>

          {data && (
            <div className="flex flex-wrap gap-4 mt-6">
              {[
                { label: 'Next Race',    value: data.race.race_name },
                { label: 'Round',        value: `Round ${data.race.round_number}` },
                { label: 'Circuit',      value: data.race.circuit_name || 'TBC' },
                { label: 'Trained On',   value: `${data.model_info.races_used} races` },
              ].map(({ label, value }) => (
                <div key={label} className="bg-gray-800/60 border border-gray-700 rounded-xl px-5 py-3">
                  <div className="text-gray-500 text-xs uppercase tracking-widest">{label}</div>
                  <div className="text-white font-bold">{value}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="container mx-auto px-4 py-10">

        {loading && (
          <div className="text-center py-20">
            <div className="animate-spin text-6xl mb-4">🏎️</div>
            <div className="text-2xl font-bold">Loading predictions...</div>
          </div>
        )}

        {error && (
          <div className="bg-red-900/30 border border-red-500/50 rounded-xl p-6 text-center">
            <p className="text-red-200">{error}</p>
          </div>
        )}

        {data && (
          <>
            {/* Race info bar */}
            {data.race.race_date && (
              <div className="bg-gradient-to-r from-red-900/20 to-transparent border border-red-800/30 rounded-xl p-4 mb-8 flex flex-wrap gap-6 items-center">
                <div className="flex items-center gap-2 text-gray-300">
                  <span>📅</span>
                  <span>{new Date(data.race.race_date).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</span>
                </div>
                {data.race.location && (
                  <div className="flex items-center gap-2 text-gray-300">
                    <span>📍</span>
                    <span>{data.race.location}, {data.race.country}</span>
                  </div>
                )}
                <div className="ml-auto flex items-center gap-2">
                  <span className="text-gray-500 text-xs">Generated:</span>
                  <span className="text-gray-400 text-xs">{data.model_info.generated_at}</span>
                </div>
              </div>
            )}

            {/* Podium highlight */}
            {data.predictions.length >= 3 && (
              <div className="mb-10">
                <div className="flex items-center gap-3 mb-6">
                  <div className="h-1 w-16 bg-f1-red rounded-full"></div>
                  <h2 className="text-2xl font-black text-white">Predicted Podium</h2>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  {[data.predictions[1], data.predictions[0], data.predictions[2]].map((p, i) => (
                    <div
                      key={p.driver_code}
                      className={`rounded-2xl p-6 border text-center ${
                        i === 1
                          ? 'bg-yellow-900/30 border-yellow-500/50 scale-105 shadow-lg shadow-yellow-900/20'
                          : 'bg-gray-800/50 border-gray-700'
                      }`}
                    >
                      <div className="text-5xl mb-3">
                        {i === 1 ? '🥇' : i === 0 ? '🥈' : '🥉'}
                      </div>
                      <div className="text-2xl font-black text-white mb-1">{p.driver_code}</div>
                      <div className="text-gray-400 text-sm mb-2 truncate">{p.driver_name}</div>
                      <div className="text-gray-500 text-xs truncate">{p.team}</div>
                      {p.qualifying_position && (
                        <div className="mt-3 text-xs text-gray-500">
                          Qualified P{p.qualifying_position}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* View toggle */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="h-1 w-16 bg-f1-red rounded-full"></div>
                <h2 className="text-2xl font-black text-white">Full Predicted Grid</h2>
              </div>
              <div className="flex gap-2">
                {(['grid', 'table'] as const).map(v => (
                  <button
                    key={v}
                    onClick={() => setView(v)}
                    className={`px-4 py-2 rounded-lg text-sm font-bold capitalize transition-all ${
                      view === v
                        ? 'bg-f1-red text-white'
                        : 'bg-gray-800 text-gray-400 border border-gray-700 hover:text-white'
                    }`}
                  >
                    {v === 'grid' ? 'Cards' : 'Table'}
                  </button>
                ))}
              </div>
            </div>

            {/* Cards view */}
            {view === 'grid' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {data.predictions.map((p) => {
                  const borderColor = teamColors[p.team] || 'border-l-gray-600';
                  const delta = p.qualifying_position
                    ? p.qualifying_position - p.predicted_position
                    : null;
                  return (
                    <div
                      key={p.driver_code}
                      className={`bg-gray-800/60 border border-gray-700 border-l-4 ${borderColor} rounded-xl p-5 hover:border-gray-500 transition-all`}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <span className={positionStyle(p.predicted_position)}>
                          P{p.predicted_position}
                        </span>
                        {delta !== null && (
                          <span className={`text-sm font-bold px-2 py-1 rounded-full ${
                            delta > 0 ? 'bg-green-900/40 text-green-400' :
                            delta < 0 ? 'bg-red-900/40 text-red-400' :
                            'bg-gray-700 text-gray-400'
                          }`}>
                            {delta > 0 ? `+${delta}` : delta === 0 ? '=' : delta}
                          </span>
                        )}
                      </div>
                      <div className="font-black text-white text-lg">{p.driver_code}</div>
                      <div className="text-gray-300 text-sm">{p.driver_name}</div>
                      <div className="text-gray-500 text-xs mt-1">{p.team}</div>
                      {p.qualifying_position && (
                        <div className="text-gray-600 text-xs mt-2">
                          Grid: P{p.qualifying_position}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {/* Table view */}
            {view === 'table' && (
              <div className="overflow-x-auto rounded-xl border border-gray-700">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-gray-800/80 text-gray-400 text-xs uppercase tracking-widest">
                      <th className="px-4 py-3 text-left">Pos</th>
                      <th className="px-4 py-3 text-left">Driver</th>
                      <th className="px-4 py-3 text-left">Team</th>
                      {hasQuali && <th className="px-4 py-3 text-center">Grid</th>}
                      {hasQuali && <th className="px-4 py-3 text-center">+/-</th>}
                      <th className="px-4 py-3 text-center">Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.predictions.map((p, idx) => {
                      const delta = p.qualifying_position
                        ? p.qualifying_position - p.predicted_position
                        : null;
                      return (
                        <tr
                          key={p.driver_code}
                          className={`border-b border-gray-800 ${idx % 2 === 0 ? 'bg-gray-900/30' : 'bg-gray-800/20'} hover:bg-gray-700/30 transition-colors`}
                        >
                          <td className={`px-4 py-3 ${positionStyle(p.predicted_position)}`}>
                            P{p.predicted_position}
                          </td>
                          <td className="px-4 py-3">
                            <div className="font-bold text-white">{p.driver_name}</div>
                            <div className="text-gray-500 text-xs">{p.driver_code}</div>
                          </td>
                          <td className="px-4 py-3 text-gray-400">{p.team}</td>
                          {hasQuali && (
                            <td className="px-4 py-3 text-center text-gray-400">
                              {p.qualifying_position ? `P${p.qualifying_position}` : '-'}
                            </td>
                          )}
                          {hasQuali && (
                            <td className="px-4 py-3 text-center font-bold">
                              {delta !== null ? (
                                <span className={delta > 0 ? 'text-green-400' : delta < 0 ? 'text-red-400' : 'text-gray-500'}>
                                  {delta > 0 ? `+${delta}` : delta === 0 ? '=' : delta}
                                </span>
                              ) : '-'}
                            </td>
                          )}
                          <td className="px-4 py-3 text-center text-gray-500 font-mono text-xs">
                            {p.predicted_score.toFixed(2)}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}

            {/* Model disclaimer */}
            <div className="mt-8 bg-gray-800/30 border border-gray-700/50 rounded-xl p-4 text-center">
              <p className="text-gray-500 text-sm">
                Predictions generated by a Random Forest model trained on {data.model_info.races_used} races (2015-2026).
                Features include qualifying position, driver form, circuit history, and team performance.
                Predictions update automatically after each race weekend.
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default PredictionsPage;