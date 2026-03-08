import { useState, useEffect } from 'react';
import api from '../services/api';

interface RaceResult {
  position: number;
  grid: number;
  driver: string;
  driver_code: string;
  team: string;
  points: number;
  status: string;
}

interface QualifyingResult {
  position: number;
  driver: string;
  driver_code: string;
  q1_time: number | null;
  q2_time: number | null;
  q3_time: number | null;
}

interface RaceDetail {
  id: number;
  name: string;
  year: number;
  round: number;
  date: string;
}

interface Props {
  raceId: number;
  raceName: string;
  onClose: () => void;
}

type Tab = 'results' | 'qualifying' | 'info';

const formatTime = (seconds: number | null): string => {
  if (seconds === null) return '--';
  const mins = Math.floor(seconds / 60);
  const secs = (seconds % 60).toFixed(3);
  return mins > 0 ? `${mins}:${secs.padStart(6, '0')}` : `${secs}s`;
};

const positionColor = (pos: number): string => {
  if (pos === 1) return 'text-yellow-400 font-black';
  if (pos === 2) return 'text-gray-300 font-black';
  if (pos === 3) return 'text-amber-600 font-black';
  return 'text-white';
};

const teamColor: Record<string, string> = {
  'Red Bull Racing': 'bg-blue-900/40 border-blue-500/40',
  'Mercedes':        'bg-teal-900/40 border-teal-500/40',
  'Ferrari':         'bg-red-900/40 border-red-500/40',
  'McLaren':         'bg-orange-900/40 border-orange-500/40',
  'Aston Martin':    'bg-green-900/40 border-green-500/40',
  'Alpine':          'bg-pink-900/40 border-pink-500/40',
  'Williams':        'bg-sky-900/40 border-sky-500/40',
  'Haas F1 Team':    'bg-gray-800/40 border-gray-500/40',
  'AlphaTauri':      'bg-indigo-900/40 border-indigo-500/40',
  'Alfa Romeo':      'bg-rose-900/40 border-rose-500/40',
};

const RaceDetailModal = ({ raceId, raceName, onClose }: Props) => {
  const [activeTab, setActiveTab] = useState<Tab>('results');
  const [results, setResults]     = useState<RaceResult[]>([]);
  const [qualifying, setQualifying] = useState<QualifyingResult[]>([]);
  const [raceInfo, setRaceInfo]   = useState<RaceDetail | null>(null);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [resData, qualiData] = await Promise.all([
          api.get(`/api/races/${raceId}/results`),
          api.get(`/api/races/${raceId}/qualifying`),
        ]);
        setResults(resData.data.results || []);
        setQualifying(qualiData.data.qualifying || []);
        setRaceInfo(resData.data.race || null);
      } catch (e) {
        setError('Failed to load race data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [raceId]);

  // Close on backdrop click
  const handleBackdrop = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) onClose();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
      onClick={handleBackdrop}
    >
      <div className="relative w-full max-w-4xl max-h-[90vh] flex flex-col bg-gradient-to-b from-gray-900 to-black border border-gray-700 rounded-2xl shadow-2xl overflow-hidden">

        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b border-gray-700 bg-gradient-to-r from-red-900/20 to-transparent">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <span className="bg-red-600/20 border border-red-500/50 text-red-400 text-xs font-black px-3 py-1 rounded-full uppercase tracking-widest">
                {raceInfo ? `Round ${raceInfo.round}` : 'Race'}
              </span>
              {raceInfo?.year && (
                <span className="text-gray-500 text-sm">{raceInfo.year}</span>
              )}
            </div>
            <h2 className="text-2xl font-black text-white">{raceName}</h2>
            {raceInfo?.date && (
              <p className="text-gray-400 text-sm mt-1">
                {new Date(raceInfo.date).toLocaleDateString('en-US', {
                  weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
                })}
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl transition-colors ml-4 mt-1"
          >
            ✕
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-700 bg-gray-900/50">
          {(['results', 'qualifying', 'info'] as Tab[]).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-3 text-sm font-bold uppercase tracking-widest transition-all ${
                activeTab === tab
                  ? 'text-white border-b-2 border-red-500'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              {tab === 'results' ? 'Race Results' : tab === 'qualifying' ? 'Qualifying' : 'Race Info'}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">

          {loading && (
            <div className="flex flex-col items-center justify-center py-20 text-gray-400">
              <div className="animate-spin text-4xl mb-4">⏳</div>
              <p>Loading race data...</p>
            </div>
          )}

          {error && (
            <div className="text-center py-20 text-red-400">{error}</div>
          )}

          {/* Race Results Tab */}
          {!loading && !error && activeTab === 'results' && (
            <div>
              {/* Podium highlight */}
              {results.length >= 3 && (
                <div className="grid grid-cols-3 gap-3 mb-6">
                  {[results[1], results[0], results[2]].map((r, i) => (
                    <div
                      key={r.driver_code}
                      className={`rounded-xl p-4 border text-center ${
                        i === 1
                          ? 'bg-yellow-900/30 border-yellow-500/50 scale-105'
                          : 'bg-gray-800/50 border-gray-600/50'
                      }`}
                    >
                      <div className="text-3xl mb-1">
                        {i === 1 ? '🥇' : i === 0 ? '🥈' : '🥉'}
                      </div>
                      <div className="font-black text-white text-sm">{r.driver_code}</div>
                      <div className="text-gray-400 text-xs truncate">{r.team}</div>
                      <div className="text-yellow-400 text-xs font-bold mt-1">{r.points} pts</div>
                    </div>
                  ))}
                </div>
              )}

              {/* Full results table */}
              <div className="overflow-x-auto rounded-xl border border-gray-700">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-gray-800/80 text-gray-400 text-xs uppercase tracking-widest">
                      <th className="px-4 py-3 text-left">Pos</th>
                      <th className="px-4 py-3 text-left">Driver</th>
                      <th className="px-4 py-3 text-left">Team</th>
                      <th className="px-4 py-3 text-center">Grid</th>
                      <th className="px-4 py-3 text-center">+/-</th>
                      <th className="px-4 py-3 text-center">Pts</th>
                      <th className="px-4 py-3 text-left">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((r, idx) => {
                      const delta = r.grid && r.position ? r.grid - r.position : null;
                      const rowColor = teamColor[r.team] || 'bg-gray-800/20 border-gray-700/20';
                      return (
                        <tr
                          key={r.driver_code}
                          className={`border-b border-gray-800 ${idx % 2 === 0 ? 'bg-gray-900/30' : 'bg-gray-800/20'} hover:bg-gray-700/30 transition-colors`}
                        >
                          <td className={`px-4 py-3 font-black text-lg ${positionColor(r.position)}`}>
                            {r.position}
                          </td>
                          <td className="px-4 py-3">
                            <div className="font-bold text-white">{r.driver}</div>
                            <div className="text-gray-500 text-xs">{r.driver_code}</div>
                          </td>
                          <td className="px-4 py-3">
                            <span className={`text-xs px-2 py-1 rounded-full border ${rowColor} text-gray-300`}>
                              {r.team}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-center text-gray-400">{r.grid ?? '--'}</td>
                          <td className="px-4 py-3 text-center font-bold">
                            {delta !== null ? (
                              <span className={delta > 0 ? 'text-green-400' : delta < 0 ? 'text-red-400' : 'text-gray-500'}>
                                {delta > 0 ? `+${delta}` : delta === 0 ? '=' : delta}
                              </span>
                            ) : '--'}
                          </td>
                          <td className="px-4 py-3 text-center font-bold text-yellow-400">
                            {r.points > 0 ? r.points : '--'}
                          </td>
                          <td className="px-4 py-3">
                            <span className={`text-xs px-2 py-1 rounded-full ${
                              r.status === 'Finished' ? 'bg-green-900/40 text-green-400' : 'bg-red-900/40 text-red-400'
                            }`}>
                              {r.status}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Qualifying Tab */}
          {!loading && !error && activeTab === 'qualifying' && (
            <div className="overflow-x-auto rounded-xl border border-gray-700">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-800/80 text-gray-400 text-xs uppercase tracking-widest">
                    <th className="px-4 py-3 text-left">Pos</th>
                    <th className="px-4 py-3 text-left">Driver</th>
                    <th className="px-4 py-3 text-center">Q1</th>
                    <th className="px-4 py-3 text-center">Q2</th>
                    <th className="px-4 py-3 text-center">Q3</th>
                  </tr>
                </thead>
                <tbody>
                  {qualifying.map((q, idx) => (
                    <tr
                      key={q.driver_code}
                      className={`border-b border-gray-800 ${idx % 2 === 0 ? 'bg-gray-900/30' : 'bg-gray-800/20'} hover:bg-gray-700/30 transition-colors`}
                    >
                      <td className={`px-4 py-3 font-black text-lg ${positionColor(q.position)}`}>
                        {q.position}
                      </td>
                      <td className="px-4 py-3">
                        <div className="font-bold text-white">{q.driver}</div>
                        <div className="text-gray-500 text-xs">{q.driver_code}</div>
                      </td>
                      <td className="px-4 py-3 text-center font-mono text-gray-300 text-xs">
                        {formatTime(q.q1_time)}
                      </td>
                      <td className="px-4 py-3 text-center font-mono text-gray-300 text-xs">
                        {q.q2_time ? formatTime(q.q2_time) : <span className="text-gray-600">--</span>}
                      </td>
                      <td className="px-4 py-3 text-center font-mono text-xs">
                        {q.q3_time
                          ? <span className="text-yellow-400 font-bold">{formatTime(q.q3_time)}</span>
                          : <span className="text-gray-600">--</span>
                        }
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Race Info Tab */}
          {!loading && !error && activeTab === 'info' && raceInfo && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                { label: 'Race Name',   value: raceInfo.name },
                { label: 'Season',      value: raceInfo.year },
                { label: 'Round',       value: raceInfo.round },
                { label: 'Date',        value: new Date(raceInfo.date).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) },
                { label: 'Total Drivers', value: results.length },
                { label: 'Finishers',   value: results.filter(r => r.status === 'Finished').length },
                { label: 'Retirements', value: results.filter(r => r.status !== 'Finished').length },
                { label: 'Points Leader', value: results[0] ? `${results[0].driver} (${results[0].points} pts)` : '--' },
              ].map(({ label, value }) => (
                <div key={label} className="bg-gray-800/50 border border-gray-700 rounded-xl p-4">
                  <div className="text-gray-500 text-xs uppercase tracking-widest mb-1">{label}</div>
                  <div className="text-white font-bold">{value}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RaceDetailModal;