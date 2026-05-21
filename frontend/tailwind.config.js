/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#faf5ff',
          100: '#f3e8ff',
          200: '#e9d5ff',
          300: '#d8b4fe',
          400: '#c084fc',
          500: '#a855f7',
          600: '#9333ea',
          700: '#7c3aed',
          800: '#6b21a8',
          900: '#581c87',
          950: '#3b0764',
        },
        brand: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
          950: '#022c22',
        },
      },
      animation: {
        'skeleton': 'skeleton 1.8s ease-in-out infinite',
        'slide-in': 'slideIn 0.3s ease-out forwards',
        'fade-in': 'fadeIn 0.2s ease forwards',
        'spin-slow': 'spin-slow 4s linear infinite',
        'compass': 'compass-point 2s ease-in-out infinite',
        'plane': 'plane-fly 2.5s ease-in-out infinite',
        'map-pin': 'map-pin-pulse 2s ease-in-out infinite',
        'loading-bar': 'loading-bar 1.8s ease-in-out infinite',
        'float': 'float-up 2.5s ease-in-out infinite',
        'shimmer-line': 'shimmer-line 2s ease-in-out infinite',
      },
      keyframes: {
        skeleton: {
          '0%': { backgroundPosition: '200% 0' },
          '100%': { backgroundPosition: '-200% 0' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'spin-slow': {
          'from': { transform: 'rotate(0deg)' },
          'to': { transform: 'rotate(360deg)' },
        },
        'compass-point': {
          '0%, 100%': { transform: 'rotate(0deg)' },
          '25%': { transform: 'rotate(15deg)' },
          '75%': { transform: 'rotate(-15deg)' },
        },
        'plane-fly': {
          '0%': { transform: 'translate(0, 0) rotate(0deg)', opacity: '1' },
          '50%': { transform: 'translate(6px, -6px) rotate(-20deg)', opacity: '0.7' },
          '100%': { transform: 'translate(0, 0) rotate(0deg)', opacity: '1' },
        },
        'map-pin-pulse': {
          '0%, 100%': { transform: 'scale(1)', opacity: '0.8' },
          '50%': { transform: 'scale(1.15)', opacity: '1' },
        },
        'loading-bar': {
          '0%': { transform: 'translateX(-100%)' },
          '50%': { transform: 'translateX(0%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        'float-up': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-6px)' },
        },
        'shimmer-line': {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
      },
      backgroundImage: {
        'skeleton-gradient': 'linear-gradient(90deg, transparent 0%, rgba(148, 163, 184, 0.1) 50%, transparent 100%)',
      },
    },
  },
  plugins: [],
  darkMode: 'class',
}
