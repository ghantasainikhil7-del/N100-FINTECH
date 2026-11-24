/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        ios: {
          bg: '#000000',          // Pure OLED pitch black
          card: '#1C1C1E',        // System Gray 6 elevated surface
          cardSub: '#2C2C2E',     // System Gray 5 track/sub-tile
          border: 'rgba(255, 255, 255, 0.08)', // Apple Hairline divider
          borderHover: 'rgba(255, 255, 255, 0.16)',
          text: '#FFFFFF',        // 100% Crisp white
          textSecondary: '#8E8E93', // Apple System Gray
          textMuted: '#636366',   // Apple Tertiary Gray
          green: '#30D158',       // Apple Signal Green (Outperformance)
          red: '#FF453A',         // Apple Coral Red (Contraction/Loss)
          blue: '#0A84FF',        // Apple System Blue (Spotlight/Interactive)
          orange: '#FF9F0A',      // Apple System Orange
          purple: '#BF5AF2',      // Apple System Purple
        }
      },
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          '"SF Pro Display"',
          '"SF Pro Text"',
          '"Plus Jakarta Sans"',
          'system-ui',
          'sans-serif'
        ],
      },
      borderRadius: {
        'ios': '16px',
        'ios-sm': '10px',
        'ios-lg': '20px',
      }
    },
  },
  plugins: [],
}
