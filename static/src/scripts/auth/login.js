const data = {
  isNotificationOpen: false,
  API_URL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
};
const loginForm = document.getElementById("login-form");
const messageContainer = document.getElementById("message-container");

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = getPayload();
  console.log(payload.error);
  if (payload.error) {
    createNotification(payload.error.message);
    return;
  }
  data.isNotificationOpen = false;
  createNotification("Logging In Please Wait");

  console.log(data.API_URL);
  try {
    const response = await fetch(`${data.API_URL}/api/v1/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    const responseData = await response.json();

    if (response.ok) {
      if (responseData.access_token && responseData.type === "bearer") {
        console.log("Login successful!");

        // --- Store the JWT ---
        localStorage.setItem("jwtToken", responseData.access_token);
        localStorage.setItem("tokenType", responseData.type); // Optional: store token type

        console.log(responseData);
        data.isNotificationOpen = false;
        createNotification("Welcome Back!");
        setTimeout(() => {
          window.location.href = "/dashboard/";
        }, 500);
        // window.location.href = '/dashboard'; // Example: Redirect to dashboard
        // Or update a state variable to show protected content
      } else {
        // This case might happen if backend returns 200 but with unexpected payload
        console.error(
          "Login successful but unexpected response format:",
          responseData
        );
        data.isNotificationOpen = false;
        createNotification(
          "Login unsuccessful, but an issue occurred. Please try again."
        );
      }
    } else {
      console.log("Login failed with status:", response.status);
      console.log("Backend error response:", responseData.detail);
      data.isNotificationOpen = false;
      const detail = responseData.detail;
      const message =
        response.status === 403 && typeof detail === "string" && detail.toLowerCase().includes("not verified")
          ? "Please verify your account first. Check your email for the verification link (including spam)."
          : Array.isArray(detail)
            ? detail.map((d) => d.msg || d).join(". ")
            : typeof detail === "string"
              ? detail
              : "Login failed. Please try again.";
      createNotification(message);
    }
  } catch (error) {
    // Network errors or issues before the response is received
    console.error("Network or unexpected error during login:", error);
    data.isNotificationOpen = false;
    createNotification(
      "Something Went Wrong (Network Error). Please Check your connection."
    );
  }
});

function getPayload() {
  const email = document.getElementById("email");
  const password = document.getElementById("password");

  if (!email.value) {
    return {
      error: true,
      message: "Please Enter A email",
    };
  }

  if (!password.value) {
    return {
      error: true,
      message: "Please Your Password",
    };
  }

  return {
    email: email.value.toString().toLowerCase().trim(),
    password: password.value.trim(),
  };
}

function createNotification(message) {
  if (!data.isNotificationOpen) {
    messageContainer.textContent = message.toString().toLowerCase().trim();
    messageContainer.classList.remove("hidden");
    messageContainer.classList.remove("-translate-y-full");

    data.isNotificationOpen = true;
    setTimeout(() => {
      messageContainer.classList.add("-translate-y-full");
      messageContainer.classList.add("hidden");
    }, 5000);
    return;
  }
}
