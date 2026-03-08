import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts';
import api from '../services/api';

// ── Types ─────────────────────────────────────────────────────────
interface PodiumDriver  { code: string; name: string; podiums: number }
interface YearStat      { year: number; races: number; points: number; wins: number }
interface DriverTrend   { driver: string; code: string; performance_by_year: YearStat[] }
interface CircuitWin    { driver: string; wins: number }
interface Circuit       { id: number; name: string; location: string; country: string }

// ── Helpers ───────────────────────────────────────────────────────

const RED     = '#e10600';
const COLORS  = ['#e10600','#ff6b35','#ffd700','#00d2ff','#a8ff78',
                  '#f093fb','#4facfe','#43e97b','#fa709a','#fee140'];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-gray-900 border border-gray-600 rounded-xl px-4 py-3 text-sm shadow-xl">
      <p className="text-gray-400 mb-1 font-bold">{label}</p>
      {payload.map((p: any, i: number) => (
        <p key={i} style={{ color: p.color }} className="font-bold">
          {p.name}: {typeof p.value === 'number' ? p.value.toLocaleString() : p.value}
        </p>
      ))}
    </div>
  );
};

// ── Component ─────────────────────────────────────────────────────
const AnalyticsPage = () => {
  const navigate = useNavigate();

  const [podiums,    setPodiums]    = useState<PodiumDriver[]>([]);
  const [trend,      setTrend]      = useState<DriverTrend | null>(null);
  const [circuitWins,setCircuitWins]= useState<CircuitWin[]>([]);
  const [circuits,   setCircuits]   = useState<Circuit[]>([]);
  const [popularCircuits, setPopularCircuits] = useState<any[]>([]);
  const [allDrivers, setAllDrivers] = useState<{code: string; name: string}[]>([]);
  const [driverSearch, setDriverSearch] = useState('');

  const [selectedDriver,  setSelectedDriver]  = useState('HAM');
  const [selectedCircuit, setSelectedCircuit] = useState<number>(1);
  const [trendMetric,     setTrendMetric]      = useState<'points'|'wins'>('points');
  const [activeSection,   setActiveSection]    = useState<'podiums'|'trends'|'circuits'|'popular'>('podiums');
  const [loading,         setLoading]          = useState(true);

  // Initial load
  useEffect(() => {
    const init = async () => {
      try {
        const [podRes, circRes, popRes, drvRes] = await Promise.all([
          api.get('/api/analytics/podium-finishers'),
          api.get('/api/circuits'),
          api.get('/api/stats/circuits/most-races?limit=15'),
          api.get('/api/drivers'),
        ]);
        setPodiums(podRes.data);
        setCircuits(circRes.data);
        setPopularCircuits(popRes.data);
        setAllDrivers(
          drvRes.data
            .filter((d: any) => d.code && d.name)
            .sort((a: any, b: any) => a.name.localeCompare(b.name))
        );
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    init();
  }, []);

  // Load driver trend when driver changes
  useEffect(() => {
    api.get(`/api/analytics/performance-trends/${selectedDriver}`)
      .then(r => setTrend(r.data))
      .catch(console.error);
  }, [selectedDriver]);

  // Load circuit wins when circuit changes
  useEffect(() => {
    api.get(`/api/analytics/wins-by-circuit/${selectedCircuit}`)
      .then(r => setCircuitWins(r.data))
      .catch(console.error);
  }, [selectedCircuit]);

  const maxPodiums = podiums[0]?.podiums || 1;

  const sections = [
    { id: 'podiums',  label: 'Podium Leaders'     },
    { id: 'trends',   label: 'Driver Performance' },
    { id: 'circuits', label: 'Circuit Winners'    },
    { id: 'popular',  label: 'Top Circuits'       },
  ] as const;

  if (loading) return (
    <div className="min-h-screen bg-gradient-to-b from-f1-dark to-black flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin text-6xl mb-4">🏎️</div>
        <div className="text-2xl font-bold text-white">Loading Analytics...</div>
      </div>
    </div>
  );

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
            <img src="/images/f1-logo.png" alt="F1" className="h-16 w-auto" />
            <h1 className="text-6xl md:text-7xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              Analytics
            </h1>
          </div>
          <p className="text-gray-400 text-xl">Data insights from 241 races across 11 seasons</p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-10">

        {/* Section Tabs */}
        <div className="flex flex-wrap gap-3 mb-10">
          {sections.map(s => (
            <button
              key={s.id}
              onClick={() => setActiveSection(s.id)}
              className={`px-6 py-3 rounded-xl font-bold text-sm uppercase tracking-widest transition-all ${
                activeSection === s.id
                  ? 'bg-f1-red text-white shadow-lg scale-105'
                  : 'bg-gray-800 text-gray-400 hover:text-white border border-gray-700 hover:border-f1-red'
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>

        {/* ── PODIUM LEADERS ───────────────────────────── */}
        {activeSection === 'podiums' && (
          <div>
            <div className="flex items-center gap-3 mb-8">
              <div className="h-1 w-16 bg-f1-red rounded-full"></div>
              <h2 className="text-3xl font-black text-white">All-Time Podium Leaders</h2>
              <span className="text-gray-500 text-sm">(2015–2025)</span>
            </div>

            {/* Bar chart */}
            <div className="bg-gray-900/60 border border-gray-700 rounded-2xl p-6 mb-8">
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={podiums} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="code" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                  <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="podiums" name="Podiums" radius={[6, 6, 0, 0]}>
                    {podiums.map((_, i) => (
                      <Cell key={i} fill={i === 0 ? '#ffd700' : i === 1 ? '#c0c0c0' : i === 2 ? '#cd7f32' : RED} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Leaderboard */}
            <div className="space-y-3">
              {podiums.map((d, i) => (
                <div
                  key={d.code}
                  className={`flex items-center gap-4 p-4 rounded-xl border transition-all ${
                    i === 0 ? 'bg-yellow-900/20 border-yellow-500/40' :
                    i === 1 ? 'bg-gray-700/20 border-gray-500/40' :
                    i === 2 ? 'bg-amber-900/20 border-amber-600/40' :
                    'bg-gray-800/40 border-gray-700/40'
                  }`}
                >
                  <div className={`text-2xl font-black w-8 text-center ${
                    i === 0 ? 'text-yellow-400' : i === 1 ? 'text-gray-300' : i === 2 ? 'text-amber-600' : 'text-gray-500'
                  }`}>
                    {i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `${i + 1}`}
                  </div>
                  <div className="flex-1">
                    <div className="font-bold text-white">{d.name}</div>
                    <div className="text-gray-500 text-xs">{d.code}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-black text-white text-lg">{d.podiums}</div>
                    <div className="text-gray-500 text-xs">podiums</div>
                  </div>
                  <div className="w-32 bg-gray-700 rounded-full h-2">
                    <div
                      className="h-2 rounded-full bg-f1-red"
                      style={{ width: `${(d.podiums / maxPodiums) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── DRIVER PERFORMANCE TRENDS ────────────────── */}
        {activeSection === 'trends' && (
          <div>
            <div className="flex items-center gap-3 mb-8">
              <div className="h-1 w-16 bg-f1-red rounded-full"></div>
              <h2 className="text-3xl font-black text-white">Driver Performance Trends</h2>
            </div>

            {/* Controls */}
            <div className="flex flex-wrap gap-4 mb-8">
              <div className="flex-1">
                <label className="text-gray-500 text-xs uppercase tracking-widest block mb-2">Driver</label>
                <div className="flex gap-3 flex-wrap items-center">
                  <input
                    type="text"
                    placeholder="Search driver..."
                    value={driverSearch}
                    onChange={e => setDriverSearch(e.target.value)}
                    className="bg-gray-800 border border-gray-600 focus:border-f1-red text-white rounded-xl px-4 py-2 text-sm outline-none w-48 transition-colors"
                  />
                  <div className="flex flex-wrap gap-2 max-h-28 overflow-y-auto">
                    {allDrivers
                      .filter((d: any) => {
                        const q = driverSearch.toLowerCase();
                        return (
                          d.code.toLowerCase().includes(q) ||
                          d.name.toLowerCase().includes(q) ||
                          (d.first_name || '').toLowerCase().includes(q) ||
                          (d.last_name || '').toLowerCase().includes(q) ||
                          (d.full_name || '').toLowerCase().includes(q)
                        );
                      })
                      .map(d => (
                        <button
                          key={d.code}
                          onClick={() => { setSelectedDriver(d.code); setDriverSearch(''); }}
                          className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                            selectedDriver === d.code
                              ? 'bg-f1-red text-white'
                              : 'bg-gray-800 text-gray-400 hover:text-white border border-gray-700 hover:border-f1-red'
                          }`}
                          title={d.name}
                        >
                          {d.code}
                        </button>
                      ))
                    }
                  </div>
                </div>
                {trend && (
                  <p className="text-gray-500 text-xs mt-2">
                    Showing: <span className="text-white font-bold">{trend.driver}</span>
                  </p>
                )}
              </div>

              <div>
                <label className="text-gray-500 text-xs uppercase tracking-widest block mb-2">Metric</label>
                <div className="flex gap-2">
                  {(['points', 'wins'] as const).map(m => (
                    <button
                      key={m}
                      onClick={() => setTrendMetric(m)}
                      className={`px-4 py-2 rounded-lg text-sm font-bold capitalize transition-all ${
                        trendMetric === m
                          ? 'bg-f1-red text-white'
                          : 'bg-gray-800 text-gray-400 hover:text-white border border-gray-700'
                      }`}
                    >
                      {m}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {trend && (
              <>
                {/* Summary cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                  {[
                    { label: 'Seasons',     value: trend.performance_by_year.length },
                    { label: 'Total Races', value: trend.performance_by_year.reduce((s, y) => s + y.races, 0) },
                    { label: 'Total Points',value: trend.performance_by_year.reduce((s, y) => s + y.points, 0).toFixed(0) },
                    { label: 'Total Wins',  value: trend.performance_by_year.reduce((s, y) => s + y.wins, 0) },
                  ].map(({ label, value }) => (
                    <div key={label} className="bg-gray-800/60 border border-gray-700 rounded-xl p-4 text-center">
                      <div className="text-gray-500 text-xs uppercase tracking-widest mb-1">{label}</div>
                      <div className="text-2xl font-black text-white">{value}</div>
                    </div>
                  ))}
                </div>

                {/* Line chart */}
                <div className="bg-gray-900/60 border border-gray-700 rounded-2xl p-6">
                  <h3 className="text-white font-bold mb-4">
                    {trend.driver} — {trendMetric === 'points' ? 'Points per Season' : 'Wins per Season'}
                  </h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={trend.performance_by_year} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="year" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                      <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} />
                      <Tooltip content={<CustomTooltip />} />
                      <Line
                        type="monotone"
                        dataKey={trendMetric}
                        name={trendMetric === 'points' ? 'Points' : 'Wins'}
                        stroke={RED}
                        strokeWidth={3}
                        dot={{ fill: RED, r: 5 }}
                        activeDot={{ r: 8 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                {/* Year by year table */}
                <div className="mt-6 overflow-x-auto rounded-xl border border-gray-700">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-gray-800/80 text-gray-400 text-xs uppercase tracking-widest">
                        <th className="px-4 py-3 text-left">Season</th>
                        <th className="px-4 py-3 text-center">Races</th>
                        <th className="px-4 py-3 text-center">Points</th>
                        <th className="px-4 py-3 text-center">Wins</th>
                        <th className="px-4 py-3 text-center">Pts/Race</th>
                      </tr>
                    </thead>
                    <tbody>
                      {trend.performance_by_year.map((y, i) => (
                        <tr key={y.year} className={`border-b border-gray-800 ${i % 2 === 0 ? 'bg-gray-900/30' : 'bg-gray-800/20'} hover:bg-gray-700/30 transition-colors`}>
                          <td className="px-4 py-3 font-bold text-white">{y.year}</td>
                          <td className="px-4 py-3 text-center text-gray-300">{y.races}</td>
                          <td className="px-4 py-3 text-center font-bold text-yellow-400">{y.points}</td>
                          <td className="px-4 py-3 text-center text-white">{y.wins}</td>
                          <td className="px-4 py-3 text-center text-gray-400">{(y.points / y.races).toFixed(1)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </div>
        )}

        {/* ── CIRCUIT WINNERS ──────────────────────────── */}
        {activeSection === 'circuits' && (
          <div>
            <div className="flex items-center gap-3 mb-8">
              <div className="h-1 w-16 bg-f1-red rounded-full"></div>
              <h2 className="text-3xl font-black text-white">Wins by Circuit</h2>
            </div>

            {/* Circuit selector */}
            <div className="mb-8">
              <label className="text-gray-500 text-xs uppercase tracking-widest block mb-3">Select Circuit</label>
              <select
                value={selectedCircuit}
                onChange={e => setSelectedCircuit(Number(e.target.value))}
                className="bg-gray-800 border border-gray-600 text-white rounded-xl px-4 py-3 outline-none focus:border-f1-red transition-colors w-full md:w-80"
              >
                {circuits.map(c => (
                  <option key={c.id} value={c.id}>
                    {c.name} — {c.country}
                  </option>
                ))}
              </select>
            </div>

            {circuitWins.length > 0 && (
              <>
                <div className="bg-gray-900/60 border border-gray-700 rounded-2xl p-6 mb-6">
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={circuitWins} margin={{ top: 10, right: 20, left: 0, bottom: 40 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="driver" tick={{ fill: '#9ca3af', fontSize: 11, angle: -30, textAnchor: 'end' }} />
                      <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} allowDecimals={false} />
                      <Tooltip content={<CustomTooltip />} />
                      <Bar dataKey="wins" name="Wins" radius={[6, 6, 0, 0]}>
                        {circuitWins.map((_, i) => (
                          <Cell key={i} fill={COLORS[i % COLORS.length]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <div className="space-y-3">
                  {circuitWins.map((w, i) => (
                    <div key={w.driver} className="flex items-center gap-4 p-4 bg-gray-800/40 border border-gray-700 rounded-xl">
                      <div className="text-xl font-black w-8 text-center" style={{ color: COLORS[i % COLORS.length] }}>
                        {i + 1}
                      </div>
                      <div className="flex-1 font-bold text-white">{w.driver}</div>
                      <div className="flex items-center gap-2">
                        <div className="h-2 rounded-full" style={{
                          width: `${(w.wins / circuitWins[0].wins) * 120}px`,
                          backgroundColor: COLORS[i % COLORS.length]
                        }} />
                        <span className="font-black text-white w-6 text-right">{w.wins}</span>
                        <span className="text-gray-500 text-xs">win{w.wins !== 1 ? 's' : ''}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}

            {circuitWins.length === 0 && (
              <div className="text-center py-16 text-gray-500">
                No win data available for this circuit.
              </div>
            )}
          </div>
        )}

        {/* ── POPULAR CIRCUITS ─────────────────────────── */}
        {activeSection === 'popular' && (
          <div>
            <div className="flex items-center gap-3 mb-8">
              <div className="h-1 w-16 bg-f1-red rounded-full"></div>
              <h2 className="text-3xl font-black text-white">Most Visited Circuits</h2>
              <span className="text-gray-500 text-sm">(2015–2025)</span>
            </div>

            <div className="bg-gray-900/60 border border-gray-700 rounded-2xl p-6 mb-8">
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={popularCircuits} layout="vertical" margin={{ top: 5, right: 30, left: 120, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis type="number" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                  <YAxis dataKey="circuit_name" type="category" tick={{ fill: '#9ca3af', fontSize: 11 }} width={110} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="races_held" name="Races Held" radius={[0, 6, 6, 0]}>
                    {popularCircuits.map((_, i) => (
                      <Cell key={i} fill={i < 3 ? RED : '#4b5563'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {popularCircuits.map((c, i) => (
                <div key={i} className="bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-700 hover:border-f1-red rounded-2xl p-5 transition-all">
                  <div className="flex justify-between items-start mb-3">
                    <span className={`text-2xl font-black ${i < 3 ? 'text-f1-red' : 'text-gray-600'}`}>
                      #{i + 1}
                    </span>
                    <span className="bg-f1-red/20 border border-f1-red/40 text-f1-red text-xs font-bold px-3 py-1 rounded-full">
                      {c.races_held} races
                    </span>
                  </div>
                  <h3 className="font-bold text-white text-lg mb-1">{c.circuit_name}</h3>
                  <p className="text-gray-400 text-sm">📍 {c.location}, {c.country}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalyticsPage;