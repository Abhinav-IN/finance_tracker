import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

export default defineConfig({
  plugins: [tailwindcss()],
  build: {
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, "index.html"),
        register: path.resolve(__dirname, "register", "index.html"),
        dashboard: path.resolve(__dirname, "dashboard", "index.html"),
      },
    },
    outDir: "../dist/",
  },
});
