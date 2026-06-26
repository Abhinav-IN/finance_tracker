const data = {
  isNotificationOpen: false,
  API_URL : "https://api-fi-track.manavkashyap.com",
};

const loginForm = document.getElementById("login-form");
const messageContainer = document.getElementById("message-container");
const demoLoginButton = document.getElementById("demo-login-button");
const loginButton = document.getElementById("login-button");

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const payload = getPayload();

  // Bug fix: was payload.error.message (error is a bool, not an object)
  if (payload.error) {
    createNotification(payload.message);
    return;
  }

  data.isNotificationOpen = false;
  createNotification("Logging in, please wait...");

  try {
    const response = await fetch(`${data.API_URL}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const responseData = await response.json().catch(() => ({}));

    if (response.ok) {
      if (responseData.access_token && responseData.type === "bearer") {
        localStorage.setItem("jwtToken", responseData.access_token);
        data.isNotificationOpen = false;
        createNotification("Welcome back!");
        setTimeout(() => {
          window.location.href = "/dashboard/";
        }, 500);
      } else {
        data.isNotificationOpen = false;
        createNotification("Unexpected response from server. Please try again.");
      }
    } else {
      data.isNotificationOpen = false;
      const detail = responseData.detail;
      // Removed: "not verified" branch — email verification no longer exists
      const message = Array.isArray(detail)
        ? detail.map((d) => d.msg || d).join(". ")
        : typeof detail === "string"
          ? detail
          : "Login failed. Please try again.";
      createNotification(message);
    }

  } catch (error) {
    console.error("Login error:", error);
    data.isNotificationOpen = false;
    createNotification("Network error. Please check your connection.");
  }
});

async function startDemoLogin() {
  if (demoLoginButton?.disabled) return;

  data.isNotificationOpen = false;
  createNotification("Loading demo account...");

  if (demoLoginButton) {
    demoLoginButton.disabled = true;
    demoLoginButton.textContent = "Loading demo account...";
  }
  if (loginButton) loginButton.disabled = true;

  try {
    const response = await fetch(`${data.API_URL}/api/v1/auth/demo`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });

    const responseData = await response.json().catch(() => ({}));

    if (response.ok && responseData.access_token && responseData.type === "bearer") {
      localStorage.setItem("jwtToken", responseData.access_token);
      data.isNotificationOpen = false;
      createNotification("Demo account loaded!");
      setTimeout(() => {
        window.location.href = "/dashboard/";
      }, 500);
      return;
    }

    data.isNotificationOpen = false;
    const detail = responseData.detail;
    const message = Array.isArray(detail)
      ? detail.map((d) => d.msg || d).join(". ")
      : typeof detail === "string"
        ? detail
        : "Could not load demo account. Please try again.";
    createNotification(message);
  } catch (error) {
    console.error("Demo login error:", error);
    data.isNotificationOpen = false;
    createNotification("Network error. Please check your connection.");
  } finally {
    if (demoLoginButton) {
      demoLoginButton.disabled = false;
      demoLoginButton.textContent = "Try Demo Account";
    }
    if (loginButton) loginButton.disabled = false;
  }
}

demoLoginButton?.addEventListener("click", startDemoLogin);

function getPayload() {
  const email    = document.getElementById("email");
  const password = document.getElementById("password");

  if (!email?.value?.trim()) {
    return { error: true, message: "Please enter your email." };
  }
  if (!password?.value?.trim()) {
    return { error: true, message: "Please enter your password." };
  }

  return {
    email:    email.value.trim().toLowerCase(),
    password: password.value.trim(),
  };
}

function createNotification(message) {
  if (data.isNotificationOpen) return;
  messageContainer.textContent = message.toString().trim();
  messageContainer.classList.remove("hidden", "-translate-y-full");
  data.isNotificationOpen = true;
  setTimeout(() => {
    messageContainer.classList.add("-translate-y-full", "hidden");
    data.isNotificationOpen = false;
  }, 5000);
}