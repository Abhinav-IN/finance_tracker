const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
import "./style.css";
import rivets from "rivets";

// import Swup from 'swup';
// const swup = new Swup();

export const data = {
  user: {},
  income: {},
  expense: {},
  investment: {},
  subscription: {},
};

const body = document.querySelector("body");
rivets.bind(body, {
  data: data,
});

body.addEventListener("click", (e) => {
  const target = e.target;

  if (target.classList.contains("user-panel-toggle")) {
    toggleUserPanel();
  }

  if (target.classList.contains("navigation-toggle")) {
    toggleNavigationPanel();
  }
  if (target.classList.contains("logout")) {
    logout();
  }

  if (target.classList.contains("screen-toggle")) {
    toggleHiddenElement(document.getElementById("addition-screen"));
  }
});

function toggleUserPanel() {
  const userpanel = document.getElementById("user-panel");
  userpanel.classList.toggle("hidden");
}

function toggleNavigationPanel(element) {
  console.log("Toggle Navigation Panel");
  const panel = document.getElementById("navigation-panel");
  panel.classList.toggle("-translate-x-full");
}

function toggleHiddenElement(element) {
  element.classList.toggle("hidden");
}

document.addEventListener("DOMContentLoaded", () => {
  const jwtToken = localStorage.getItem("jwtToken");
  if (jwtToken) {
    console.log("User appears to be logged in.");
  } else {
    console.log("User is not logged in.");
    window.location.href = "/";
  }
});

function logout() {
  const jwtToken = localStorage.getItem("jwtToken");
  if (!jwtToken) {
    console.log("User is not logged in");
    return;
  }
  localStorage.removeItem("jwtToken");
  alert("User Has Been Logged Out");
  window.location.href = "/";
}
