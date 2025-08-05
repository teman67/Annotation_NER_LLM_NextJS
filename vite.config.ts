import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  css: {
    // Ensure CSS is processed inline for better performance
    postcss: "./postcss.config.js",
  },
  build: {
    // Inline CSS for critical styles
    cssCodeSplit: false,
    rollupOptions: {
      output: {
        // Ensure CSS is loaded before JS
        manualChunks: undefined,
      },
    },
  },
});
