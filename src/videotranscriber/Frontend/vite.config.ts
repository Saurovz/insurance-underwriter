import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3002,
    proxy: {
      '/upload-video': 'http://localhost:8001',           // ✅ ADDED
      '/upload': 'http://localhost:8001',
      '/videos-list': 'http://localhost:8001',
      '/videos': 'http://localhost:8001',
      '/transcribe': 'http://localhost:8001',
      '/generate-prescription': 'http://localhost:8001',
      '/prescription': 'http://localhost:8001',
      '/patient-media': 'http://localhost:8001',          // ✅ ADDED
      '/doctor-advice': 'http://localhost:8001',          // ✅ ADDED
      '/session': 'http://localhost:8001',                // ✅ ADDED
      '/chatbot': 'http://localhost:8001',                // ✅ ADDED
    }
  }
})
