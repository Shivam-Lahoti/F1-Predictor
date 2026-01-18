import { useNavigate, useLocation } from 'react-router-dom';

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Home', icon: '🏠' },
    { path: '/races', label: 'Races', icon: '🏁' },
    { path: '/drivers', label: 'Drivers', icon: '👥' },
    { path: '/analytics', label: 'Analytics', icon: '📊' },
  ];

  return (
    <nav className="bg-f1-dark/95 backdrop-blur-md border-b border-gray-800/50 sticky top-0 z-50 shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-20">
          
          {/* Logo Section */}
          <div
            onClick={() => navigate('/')}
            className="flex items-center gap-3 cursor-pointer group"
          >
            <img 
              src="/images/f1-logo.png"
              alt="F1 Logo" 
              className="h-14 w-auto object-contain group-hover:scale-110 transition-transform filter drop-shadow-lg"
            />
            <div className="hidden sm:block">
              <div className="text-2xl font-bold text-white group-hover:text-f1-red transition-colors">
                RACE PREDICTOR
              </div>
              <div className="text-xs text-gray-500 uppercase tracking-wider">
                ML Powered Analytics
              </div>
            </div>
          </div>

          {/* Navigation Items */}
          <div className="hidden md:flex items-center gap-2">
            {navItems.map((item) => (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`px-6 py-3 rounded-lg font-bold transition-all ${
                  location.pathname === item.path
                    ? 'bg-f1-red text-white shadow-neon-red'
                    : 'text-gray-400 hover:text-white hover:bg-f1-gray-800'
                }`}
              >
                <span className="mr-2">{item.icon}</span>
                {item.label}
              </button>
            ))}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button className="text-gray-400 hover:text-white text-3xl">
              ☰
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;