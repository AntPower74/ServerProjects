import { defineConfig } from 'vite';
import legacy from '@vitejs/plugin-legacy';

export default defineConfig({
  plugins: [
    legacy({
      targets: ['defaults', 'Android >= 5', 'iOS >= 9', 'Chrome >= 49']
    })
  ],
  server: {
    host: true,
    allowedHosts: true,
    port: 5173
  }
});
