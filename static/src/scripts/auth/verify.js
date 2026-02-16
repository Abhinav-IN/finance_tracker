const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const verifyingEl = document.getElementById("verifying-state");
const successEl = document.getElementById("success-state");
const errorEl = document.getElementById("error-state");
const goToLoginEl = document.getElementById("go-to-login");

function getTokenFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return params.get("token");
}

function showSuccess() {
  if (verifyingEl) verifyingEl.classList.add("hidden");
  if (errorEl) errorEl.classList.add("hidden");
  if (successEl) successEl.classList.remove("hidden");
}

function showError() {
  if (verifyingEl) verifyingEl.classList.add("hidden");
  if (successEl) successEl.classList.add("hidden");
  if (errorEl) errorEl.classList.remove("hidden");
}

async function verifyAccount() {
  const token = getTokenFromUrl();

  if (!token || !token.trim()) {
    showError();
    return;
  }

  try {
    const response = await fetch(
      `${API_URL}/api/v1/auth/verify-account?token=${encodeURIComponent(token)}`,
      { method: "GET", headers: { "Content-Type": "application/json" } }
    );

    const data = await response.json().catch(() => ({}));

    if (response.ok) {
      showSuccess();
      setTimeout(() => {
        window.location.href = "/";
      }, 2500);
    } else {
      showError();
    }
  } catch (err) {
    console.error("Verify error:", err);
    showError();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  verifyAccount();
});

if (goToLoginEl) {
  goToLoginEl.addEventListener("click", (e) => {
    e.preventDefault();
    window.location.href = "/";
  });
}
