interface F1LogoProps {
  className?: string;
  size?: number;
  animated?: boolean;
}

const F1Logo = ({ className = "", size = 48, animated = false }: F1LogoProps) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 200 200"
      className={`${className} ${animated ? 'hover:scale-110 transition-transform' : ''}`}
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <linearGradient id="f1-red-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#FF0000" />
          <stop offset="100%" stopColor="#8B0000" />
        </linearGradient>
        
        <filter id="glow">
          <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      
      {/* Background circle */}
      <circle cx="100" cy="100" r="90" fill="#15151E" stroke="url(#f1-red-gradient)" strokeWidth="4"/>
      
      {/* F1 Text */}
      <text
        x="100"
        y="115"
        fontFamily="Rajdhani, Arial, sans-serif"
        fontSize="85"
        fontWeight="900"
        fill="url(#f1-red-gradient)"
        textAnchor="middle"
        filter="url(#glow)"
      >
        F1
      </text>
      
      {/* Racing stripes */}
      <line x1="30" y1="160" x2="170" y2="160" stroke="url(#f1-red-gradient)" strokeWidth="3" opacity="0.5"/>
      <line x1="40" y1="170" x2="160" y2="170" stroke="url(#f1-red-gradient)" strokeWidth="2" opacity="0.3"/>
      
      {/* Speed lines */}
      <path d="M 20 50 L 40 50" stroke="#E10600" strokeWidth="2" opacity="0.6"/>
      <path d="M 15 70 L 45 70" stroke="#E10600" strokeWidth="2" opacity="0.4"/>
      <path d="M 25 90 L 50 90" stroke="#E10600" strokeWidth="2" opacity="0.3"/>
    </svg>
  );
};

export default F1Logo;