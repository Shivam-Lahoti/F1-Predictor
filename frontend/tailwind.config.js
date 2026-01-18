/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'f1': {
          'red': '#E10600',
          'dark': '#15151E',
          'darker': '#0E0E14',
          'gray': {
            '800': '#1E1E2E',
            '700': '#2A2A3C',
            '600': '#363648',
          }
        },
      },
      fontFamily: {
        'formula': ['Rajdhani', 'sans-serif'],
        'sans': ['Inter', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        'racing-gradient': 'linear-gradient(135deg, #E10600 0%, #8B0000 100%)',
        'dark-gradient': 'linear-gradient(180deg, #15151E 0%, #0E0E14 100%)',
      },
      boxShadow: {
        'neon-red': '0 0 20px rgba(225, 6, 0, 0.5)',
        'glow': '0 4px 24px rgba(0, 0, 0, 0.4)',
      },
      animation: {
        'float': 'float 3s ease-in-out infinite',
        'slide-up': 'slideUp 0.5s ease-out',
        'fade-in': 'fadeIn 0.6s ease-out',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}