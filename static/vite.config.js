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
        budget: path.resolve(__dirname, "dashboard", "budget/index.html"),
        income: path.resolve(__dirname, "dashboard", "income/index.html"),
        investment: path.resolve(__dirname, "dashboard", "investment/index.html"),
        subscription: path.resolve(
          __dirname,
          "dashboard",
          "subscriptions/index.html"  
        ),
        profile: path.resolve(__dirname, "dashboard", "profile/index.html"),
      },
    },
  },
});
