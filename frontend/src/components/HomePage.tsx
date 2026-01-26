import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const HomePage = () => {
  const navigate = useNavigate();
  
  const [stats, setStats] = useState({
    total_races: 241,
    total_drivers: 120,
    total_circuits: 35,
    years_covered: 11,
    seasons: [2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015]
  });
  const [loading, setLoading] = useState(true);

  // Fetch real stats from API
  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await api.get('/api/stats');
      setStats(response.data);
      console.log('Stats loaded:', response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
      // Keep default stats if API fails
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-f1-dark via-f1-darker to-black">
      
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Animated Background Blobs */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-10 w-96 h-96 bg-f1-red rounded-full filter blur-3xl animate-float"></div>
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-f1-red rounded-full filter blur-3xl animate-float" style={{animationDelay: '1.5s'}}></div>
        </div>

        {/* Hero Content */}
        <div className="relative container mx-auto px-4 py-20 md:py-32">
          <div className="text-center animate-fade-in">
            
            {/* F1 Logo */}
            <div className="mb-8 flex justify-center">
              <div className="relative">
                <img 
                  src="/images/f1-logo.png" 
                  alt="F1 Logo" 
                  className="h-32 w-auto object-contain animate-float filter drop-shadow-2xl"
                />
                {/* Logo glow */}
                <div className="absolute inset-0 bg-f1-red opacity-20 blur-3xl"></div>
              </div>
            </div>
            
            {/* Main Title */}
            <h1 className="text-6xl md:text-8xl font-bold mb-6 bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent leading-tight">
              RACE PREDICTOR
            </h1>
            
            {/* Animated Underline */}
            <div className="relative inline-block mb-8">
              <p className="text-2xl md:text-3xl text-gray-300 font-light tracking-wide">
                Machine Learning Powered Race Analytics
              </p>
              <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-f1-red to-transparent"></div>
            </div>
            
            {/* Description */}
            <p className="text-lg md:text-xl text-gray-400 max-w-3xl mx-auto mb-12 leading-relaxed">
              Explore 11 seasons of Formula 1 data spanning {stats.total_races} races. Analyze driver performance, 
              predict race outcomes, and unlock insights from over a decade of premier motorsport racing.
            </p>
            
            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
              <button
                onClick={() => navigate('/races')}
                className="group relative bg-f1-red hover:bg-red-700 text-white px-12 py-5 rounded-xl text-xl font-bold shadow-neon-red hover:shadow-2xl transform hover:scale-105 transition-all overflow-hidden"
              >
                <span className="relative z-10 flex items-center gap-3">
                  Explore Races
                  <span className="transform group-hover:translate-x-1 transition-transform">→</span>
                </span>
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 group-hover:opacity-20 transform -skew-x-12 transition-all"></div>
              </button>
              
              <button
                onClick={() => navigate('/analytics')}
                className="bg-transparent border-2 border-gray-600 hover:border-f1-red text-white px-12 py-5 rounded-xl text-xl font-bold hover:bg-f1-red/10 transition-all backdrop-blur-sm"
              >
                View Analytics
              </button>
            </div>

            {/* Scroll Indicator */}
            <div className="mt-16 flex justify-center">
              <div className="flex flex-col items-center gap-2 text-gray-500 animate-bounce">
                <span className="text-sm uppercase tracking-wider">Scroll to explore</span>
                <span className="text-2xl">↓</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Glass Morphism Stats Section */}
      <div className="container mx-auto px-4 -mt-24 relative z-10 mb-20">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <GlassStatCard
            icon="🏁"
            number={stats.total_races?.toString() || "241"}
            label="Historic Races"
            gradient="from-blue-600 to-blue-800"
          />
          <GlassStatCard
            icon="👥"
            number={`${stats.total_drivers || 120}+`}
            label="F1 Drivers"
            gradient="from-green-600 to-emerald-800"
          />
          <GlassStatCard
            icon="🗺️"
            number={`${stats.total_circuits || 35}+`}
            label="Global Circuits"
            gradient="from-purple-600 to-indigo-800"
          />
          <GlassStatCard
            icon="📊"
            number="120K+"
            label="Data Points"
            gradient="from-orange-600 to-red-800"
          />
        </div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-4 py-24">
        <div className="text-center mb-16 animate-slide-up">
          <div className="inline-block mb-4">
            <span className="text-f1-red text-sm font-bold uppercase tracking-widest border border-f1-red/30 px-4 py-2 rounded-full bg-f1-red/5">
              Platform Features
            </span>
          </div>
          <h2 className="text-5xl md:text-6xl font-bold mb-6">
            Powered by <span className="text-f1-red">Data & AI</span>
          </h2>
          <p className="text-gray-400 text-xl max-w-2xl mx-auto">
            Advanced analytics and machine learning models trained on {stats.years_covered} years of Formula 1 racing data
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <PremiumFeatureCard
            icon="📈"
            title="Historical Analysis"
            description="Deep dive into comprehensive race breakdowns with lap-by-lap analysis, qualifying performance, and decade-spanning trends."
            features={[`${stats.total_races} Races`, 'Lap Time Data', 'Weather Tracking', 'Pit Stop Analysis']}
            onClick={() => navigate('/races')}
          />
          
          <PremiumFeatureCard
            icon="🎯"
            title="Race Predictions"
            description="AI-powered predictions using machine learning models trained on historical data to forecast podium finishes and race outcomes."
            features={['ML Models', 'Probability Analysis', 'Strategy Simulator', 'What-If Scenarios']}
            onClick={() => navigate('/races')}
            highlight
          />
          
          <PremiumFeatureCard
            icon="⚡"
            title="Driver Insights"
            description="Comprehensive driver statistics with career performance metrics, circuit mastery analysis, and competitive comparisons."
            features={[`${stats.total_drivers}+ Drivers`, 'Performance Graphs', 'Head-to-Head', 'Form Analysis']}
            onClick={() => navigate('/drivers')}
          />
        </div>
      </div>

      {/* Data Timeline Section */}
      <div className="container mx-auto px-4 py-20 border-t border-gray-800/50">
        <div className="text-center mb-12">
          <h3 className="text-4xl font-bold mb-4">
            Data Coverage <span className="text-f1-red">2015-2025</span>
          </h3>
          <p className="text-gray-400 text-lg">
            Click any year to explore that season's races
          </p>
        </div>
        
        <div className="flex flex-wrap justify-center gap-4">
          {stats.seasons.map((year: number, index: number) => (
            <div
              key={year}
              onClick={() => navigate(`/races?year=${year}`)}
              className="group relative cursor-pointer animate-slide-up"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              {/* Hover glow */}
              <div className="absolute -inset-1 bg-gradient-to-r from-f1-red to-orange-600 rounded-2xl blur opacity-0 group-hover:opacity-40 transition-opacity"></div>
              
              <div className="relative bg-gradient-to-br from-f1-gray-800 to-f1-gray-700 hover:from-f1-red hover:to-red-800 px-10 py-8 rounded-2xl font-bold border border-gray-700 hover:border-f1-red transform hover:scale-110 transition-all shadow-glow">
                <div className="text-4xl font-black mb-2">{year}</div>
                <div className="text-xs text-gray-400 group-hover:text-white uppercase tracking-wider">
                  Click to View
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div className="container mx-auto px-4 py-20">
        <div className="relative overflow-hidden bg-gradient-to-r from-f1-red/20 via-f1-red/10 to-transparent border border-f1-red/30 rounded-3xl p-12 md:p-16">
          {/* Background pattern */}
          <div className="absolute inset-0 opacity-5">
            <div className="absolute inset-0" style={{
              backgroundImage: 'repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(255,255,255,.05) 10px, rgba(255,255,255,.05) 20px)'
            }}></div>
          </div>
          
          <div className="relative text-center">
            <h3 className="text-4xl md:text-5xl font-bold mb-4">
              Ready to Dive Into F1 Data?
            </h3>
            <p className="text-gray-400 mb-10 text-lg md:text-xl max-w-2xl mx-auto">
              Access comprehensive race statistics, driver analytics, and predictive insights from over a decade of Formula 1 racing
            </p>
            <button
              onClick={() => navigate('/races')}
              className="bg-f1-red hover:bg-red-700 text-white px-14 py-5 rounded-xl text-xl font-bold shadow-neon-red hover:shadow-2xl transform hover:scale-105 transition-all"
            >
              Start Exploring →
            </button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-800/50 bg-f1-darker py-12">
        <div className="container mx-auto px-4 text-center">
          <div className="flex justify-center mb-4">
            <img 
              src="/images/f1-logo.png" 
              alt="F1 Logo" 
              className="h-12 w-auto object-contain opacity-50"
            />
          </div>
          <p className="text-gray-500 mb-2">
            F1 Race Predictor - Built with React, FastAPI & Machine Learning
          </p>
          <p className="text-gray-600 text-sm">
            Data: 2015-2025 Formula 1 Seasons ({stats.total_races} Races) | Built by Shivam Lahoti
          </p>
        </div>
      </footer>
    </div>
  );
};

// Glass Morphism Stat Card Component
const GlassStatCard = ({ icon, number, label, gradient }: {
  icon: string;
  number: string;
  label: string;
  gradient: string;
}) => (
  <div className="group relative overflow-hidden animate-slide-up">
    {/* Gradient background */}
    <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-80 group-hover:opacity-100 transition-opacity`}></div>
    
    {/* Glass effect layer */}
    <div className="relative backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl p-8 text-center shadow-glow hover:shadow-2xl transform hover:scale-105 hover:-translate-y-2 transition-all">
      <div className="text-5xl mb-4 animate-float">{icon}</div>
      <div className="text-5xl font-black mb-2">{number}</div>
      <div className="text-sm uppercase tracking-widest opacity-90 font-bold">{label}</div>
    </div>
  </div>
);

// Premium Feature Card Component
const PremiumFeatureCard = ({ icon, title, description, features, onClick, highlight = false }: {
  icon: string;
  title: string;
  description: string;
  features: string[];
  onClick: () => void;
  highlight?: boolean;
}) => (
  <div
    onClick={onClick}
    className={`relative group cursor-pointer animate-slide-up ${
      highlight ? 'md:-mt-6' : ''
    }`}
  >
    {/* Featured badge glow */}
    {highlight && (
      <>
        <div className="absolute -inset-1 bg-gradient-to-r from-f1-red via-orange-600 to-f1-red rounded-3xl blur-lg opacity-30 group-hover:opacity-60 transition-opacity animate-pulse"></div>
        <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-f1-red text-white text-xs px-4 py-1 rounded-full font-bold uppercase tracking-wider shadow-lg">
          Featured
        </div>
      </>
    )}
    
    <div className={`relative bg-gradient-to-br from-f1-gray-800 to-f1-gray-700 rounded-3xl p-8 border ${
      highlight ? 'border-f1-red shadow-neon-red' : 'border-gray-700'
    } hover:border-f1-red transition-all shadow-glow hover:shadow-2xl transform hover:scale-105`}>
      
      {/* Icon with background */}
      <div className="relative mb-6 inline-block">
        <div className="absolute inset-0 bg-f1-red/20 blur-xl rounded-full"></div>
        <div className="relative text-7xl filter drop-shadow-lg">{icon}</div>
      </div>
      
      {/* Title */}
      <h3 className="text-3xl font-bold mb-4 group-hover:text-f1-red transition-colors">
        {title}
      </h3>
      
      {/* Description */}
      <p className="text-gray-400 mb-6 leading-relaxed text-base">
        {description}
      </p>
      
      {/* Feature Pills */}
      <div className="flex flex-wrap gap-2 mb-6">
        {features.map((feature, idx) => (
          <span
            key={idx}
            className="text-xs px-4 py-2 bg-f1-red/20 border border-f1-red/40 rounded-full text-f1-red font-bold uppercase tracking-wide"
          >
            {feature}
          </span>
        ))}
      </div>
      
      {/* Hover arrow indicator */}
      <div className="flex items-center text-f1-red font-bold opacity-0 group-hover:opacity-100 transform translate-x-0 group-hover:translate-x-2 transition-all">
        <span>Learn More</span>
        <span className="ml-2 text-xl">→</span>
      </div>
    </div>
  </div>
);

export default HomePage;