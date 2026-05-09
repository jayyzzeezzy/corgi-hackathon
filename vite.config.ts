import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/pipeshift-api': {
        target: 'https://api.pipeshift.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/pipeshift-api/, ''),
      },
    },
  },
})
