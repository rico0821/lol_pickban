import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// Determine backend port: 5001 for integration, 5000 for dev
const backendPort = process.env.LOL_PICKBAN_PORT === '5001' ? '5001' : '5000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3001,
    proxy: {
      '/api': {
        target: `http://localhost:${backendPort}`,
        changeOrigin: true,
        secure: false,
        // Uncomment for proxy debug:
        // configure: (proxy, options) => {
        //   proxy.on('proxyReq', (proxyReq, req, res) => {
        //     console.log('[vite proxy] Sending Request:', req.method, req.url);
        //   });
        //   proxy.on('proxyRes', (proxyRes, req, res) => {
        //     console.log('[vite proxy] Response:', proxyRes.statusCode, req.url);
        //   });
        // },
      },
    },
  },
})
