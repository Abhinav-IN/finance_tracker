const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const form = document.getElementById("reset-confirm-form");
const messageContainer = document.getElementById("message-container");
const formState = document.getElementById("form-state");
const successState = document.getElementById("success-state");
const errorState = document.getElementById("error-state");

function getTokenFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return params.get("token");
}

function showMessage(text, isError = false) {
  if (!messageContainer) return;
  messageContainer.textContent = text;
  messageContainer.classList.remove("hidden");
  messageContainer.classList.remove("bg-red-100", "dark:bg-red-900/30", "text-red-700", "dark:text-red-300");
  messageContainer.classList.remove("bg-green-100", "dark:bg-green-900/30", "text-green-700", "dark:text-green-300");
  if (isError) {
    messageContainer.classList.add("bg-red-100", "dark:bg-red-900/30", "text-red-700", "dark:text-red-300");
  } else {
    messageContainer.classList.add("bg-green-100", "dark:bg-green-900/30", "text-green-700", "dark:text-green-300");
  }
}

function showSuccess() {
  if (formState) formState.classList.add("hidden");
  if (errorState) errorState.classList.add("hidden");
  if (successState) successState.classList.remove("hidden");
}

function showInvalidLink() {
  if (formState) formState.classList.add("hidden");
  if (successState) successState.classList.add("hidden");
  if (errorState) errorState.classList.remove("hidden");
}

document.addEventListener("DOMContentLoaded", () => {
  const token = getTokenFromUrl();
  if (!token || !token.trim()) {
    showInvalidLink();
    return;
  }
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const token = getTokenFromUrl();
  if (!token) {
    showInvalidLink();
    return;
  }

  const newPassword = document.getElementById("new_password").value;
  const confirmPassword = document.getElementById("confirm_password").value;

  if (newPassword !== confirmPassword) {
    showMessage("Passwords do not match.", true);
    return;
  }

  if (newPassword.length < 8) {
    showMessage("Password must be at least 8 characters.", true);
    return;
  }

  try {
    const response = await fetch(`${API_URL}/api/v1/auth/password-reset-confirm`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        password_token: token,
        new_password: newPassword,
      }),
    });

    const data = await response.json().catch(() => ({}));

    if (response.ok) {
      showSuccess();
    } else {
      const msg = typeof data.detail === "string" ? data.detail : "Could not reset password. The link may have expired.";
      showMessage(msg, true);
    }
  } catch (err) {
    console.error(err);
    showMessage("Network error. Check your connection.", true);
  }
});
