import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Forwards API calls to your Python server
      '/analyze': 'http://127.0.0.1:8000',
      '/topic-model': 'http://127.0.0.1:8000',
      '/sentiment': 'http://127.0.0.1:8000',
      '/summarize': 'http://127.0.0.1:8000'
    }
  }
})
