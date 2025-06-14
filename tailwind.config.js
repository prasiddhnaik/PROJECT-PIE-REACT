/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        // Emerald-Purple theme colors
        primary: {
          50: '#F0FDF4',    // Light mint green text
          100: '#DCFCE7',
          200: '#BBF7D0',
          300: '#86EFAC',
          400: '#4ADE80',
          500: '#10B981',   // Emerald green accent
          600: '#059669',
          700: '#047857',
          800: '#065F46',
          900: '#064E3B',   // Deep forest green
        },
        secondary: {
          50: '#FAF5FF',
          100: '#F3E8FF',
          200: '#E9D5FF',
          300: '#D8B4FE',
          400: '#C084FC',
          500: '#A855F7',
          600: '#8B5CF6',   // Purple accent
          700: '#7C3AED',
          800: '#6D28D9',
          900: '#581C87',   // Deep purple
        },
        accent: {
          pink: '#EC4899',  // Pink accent
          emerald: '#34D399', // Emerald accent
        },
        background: {
          dark: '#1F2937',  // Dark gradient middle
          darker: '#111827', // Darker background
        }
      },
      backgroundImage: {
        'forest-gradient': 'linear-gradient(to bottom right, #064E3B, #1F2937, #581C87)',
        'header-gradient': 'linear-gradient(to right, #10B981, #8B5CF6, #EC4899)',
        'card-gradient': 'linear-gradient(to bottom right, #065F46, #374151)',
        'emerald-purple': 'linear-gradient(135deg, #10B981 0%, #8B5CF6 100%)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
} 