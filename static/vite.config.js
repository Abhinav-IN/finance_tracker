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
        expense: path.resolve(__dirname, "dashboard", "expense/index.html"),
        income: path.resolve(__dirname, "dashboard", "income/index.html"),
        subscription: path.resolve(
          __dirname,
          "dashboard",
          "subscriptions/index.html"  
        ),
        profile: path.resolve(__dirname, "dashboard", "profile/index.html"),
        verify: path.resolve(__dirname, "verify", "index.html"),
        reset: path.resolve(__dirname, "reset", "index.html"),
        resetPassword: path.resolve(__dirname, "reset-password", "index.html"),
      },
    },
    outDir: "../dist/",
  },
});
