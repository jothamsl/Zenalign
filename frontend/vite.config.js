import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/datasets': 'http://localhost:8000',
      '/analysis': 'http://localhost:8000',
      '/health': 'http://localhost:8000'
    }
  }
})
