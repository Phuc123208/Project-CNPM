import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // ⭐ Cấu hình proxy để dev gọi được Flask backend
  server: {
    port: 5173,          // Frontend vẫn chạy cổng 5173 như bình thường
    host: true,        // Cho phép truy cập từ bên ngoài network
    proxy: {
      // Mọi request bắt đầu bằng /api đều được chuyển sang backend
      '/api': {
        target: 'http://localhost:9999', // URL Flask backend
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
  // ⭐ Lưu ý: Khi build xong, bạn phải deploy backend và frontend cùng domain/port
  // hoặc dùng API gateway để route request cho đúng
})
