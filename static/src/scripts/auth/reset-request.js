const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const form = document.getElementById("reset-request-form");
const messageContainer = document.getElementById("message-container");

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

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("email").value.trim().toLowerCase();
  if (!email) {
    showMessage("Please enter your email.", true);
    return;
  }

  try {
    const response = await fetch(`${API_URL}/api/v1/auth/password-reset-request`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });

    const data = await response.json().catch(() => ({}));

    if (response.ok) {
      showMessage("If this email is registered, a reset link has been sent. Check your inbox and spam.");
    } else {
      const msg = typeof data.detail === "string" ? data.detail : "Something went wrong. Try again.";
      showMessage(msg, true);
    }
  } catch (err) {
    console.error(err);
    showMessage("Network error. Check your connection.", true);
  }
});
