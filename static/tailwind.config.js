module.exports = {
  darkMode: "class", // Make sure this is set!
  content: [
    "./index.html", // Point to your main HTML file
    "./src/**/*.{js,ts,jsx,tsx}", // Point to all JS/TS files in src/ (adjust if you have other extensions)
    // Add other paths if you have components in other folders
    ".**/**/*.{html, js, css}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
