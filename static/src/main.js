import "./style.css";
// Function to toggle dark mode
function toggleDarkMode() {
  const htmlElement = document.documentElement;
  console.log("Toggling dark mode..."); // Changed for clarity
  if (htmlElement.classList.contains("dark")) {
    htmlElement.classList.remove("dark");
    localStorage.setItem("theme", "light");
  } else {
    htmlElement.classList.add("dark");
    localStorage.setItem("theme", "dark");
  }
}

// Function to set initial theme based on user's preference or system settings
function setInitialTheme() {
  const htmlElement = document.documentElement;
  const storedTheme = localStorage.getItem("theme");

  if (
    storedTheme === "dark" ||
    (!storedTheme && window.matchMedia("(prefers-color-scheme: dark)").matches)
  ) {
    htmlElement.classList.add("dark");
  } else {
    htmlElement.classList.remove("dark");
  }
}

// Wait for the DOM to be fully loaded before interacting with elements
document.addEventListener("DOMContentLoaded", () => {
  setInitialTheme(); // Set the initial theme

  const darkModeButton = document.getElementById("darkModeButton");
  if (darkModeButton) {
    // Always check if the element exists
    darkModeButton.addEventListener("click", toggleDarkMode);
  } else {
    console.error("Dark mode button not found!");
  }
});
