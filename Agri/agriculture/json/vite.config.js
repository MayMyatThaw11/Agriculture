import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  root: 'frontend',
  plugins: [react()],
  resolve: {
    // The repository previously had node_modules folders at two levels. Force
    // every package (especially react-chartjs-2) to share one React runtime.
    dedupe: ['react', 'react-dom'],
  },
  server: {
    proxy: {
      // Browser requests remain same-origin; Vite forwards them to FastAPI.
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
