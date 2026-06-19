import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// Static SPA: reads data/latest.json + history.csv (copied into public/data by sync:data).
export default defineConfig({
  plugins: [react(), tailwindcss()],
})
