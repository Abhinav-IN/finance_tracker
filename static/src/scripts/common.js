const menu_panel = document.getElementById("menu_panel");
const menu_toggle = document.querySelectorAll(".menu_toggle");
const themeToggle = document.getElementById("theme-toggle");
const prefersDark = window.matchMedia("(prefers-color-scheme: dark)");
const html = document.documentElement;

menu_toggle.forEach((element) => {
  element.addEventListener("click", menuToggle);
});

function menuToggle() {
  menu_panel.classList.toggle("-translate-x-full");
}

// Apply OS theme by default if no preference is saved
if (!localStorage.getItem("theme")) {
  if (prefersDark.matches) {
    html.classList.add("dark");
  } else {
    html.classList.remove("dark");
  }
} else {
  // Use stored preference
  if (localStorage.getItem("theme") === "dark") {
    html.classList.add("dark");
  } else {
    html.classList.remove("dark");
  }
}

// Listen for system theme changes
prefersDark.addEventListener("change", (e) => {
  if (!localStorage.getItem("theme")) {
    // Only apply if user hasn't manually set a theme
    if (e.matches) {
      html.classList.add("dark");
    } else {
      html.classList.remove("dark");
    }
  }
});

// Toggle theme manually
themeToggle.addEventListener("click", () => {
  if (html.classList.contains("dark")) {
    html.classList.remove("dark");
    localStorage.setItem("theme", "light");
  } else {
    html.classList.add("dark");
    localStorage.setItem("theme", "dark");
  }
});
