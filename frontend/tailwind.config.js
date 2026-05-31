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
        dark: {
          bg: '#0f1117',
          card: '#1a1d29',
          border: '#2a2d3a',
          text: '#e1e4ea',
          muted: '#8b8fa3',
        },
        light: {
          bg: '#f5f7fa',
          card: '#ffffff',
          border: '#e2e8f0',
          text: '#1a202c',
          muted: '#718096',
        },
        profit: '#22c55e',
        loss: '#ef4444',
        hold: '#f59e0b',
      }
    },
  },
  plugins: [],
}