const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
import "./style.css";
import rivets from "rivets";

// import Swup from 'swup';
// const swup = new Swup();

export const data = {
  user: {},
  income: {
    list: [],
  },
  expense: {
    list: [],
  },
  investment: {},
  subscription: {},
  overview: {},
};

export const body = document.querySelector("body");
rivets.bind(body, {
  data: data,
});

rivets.formatters.date = function (value) {
  const date = new Date(value);

  return `${date.getDate()}-${date.getMonth()}-${date.getFullYear()}`;
};
rivets.formatters.time = function (value) {
  const date = new Date(value);

  return `${date.getHours()}:${date.getMinutes()}:${date.getSeconds()}`;
};

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
    console.log("Toggling Pop Up Screen");
    toggleHiddenElement(document.getElementById("overlay-screen"));
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
  getUserDetails();
  if (jwtToken) {
    console.log("user token is present");
  } else {
    console.log("user token is not present, redirecting");
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

async function getUserDetails() {
  try {
    const response = await fetch(`${API_URL}/api/v1/user/profile`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(
        `HTTP error! status: ${response.status}, message: ${errorText}`
      );

      if (response.status === 401) {
        alert("User is not authenticated");
        window.location.href = "/";
        return;
      }
    }
    const result = await response.json();
    console.log("User Info:", result);
    data.user = result;
  } catch (error) {
    console.log(error);
  }
}

export function token() {
  const jwtToken = localStorage.getItem("jwtToken");
  if (!jwtToken) {
    console.error("No JWT token found. User is not logged in.");
    window.location.href = "/login.html";
    return;
  }
  return jwtToken;
}
