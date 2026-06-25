const data = {
  userInfo: {
    username: "",
    first_name: "",
    last_name: "",
    email: "",
    dob: "",
    gender: "",
    password: "",
    confirm_password: "",
  },
  step: {
    current: 0,
    max: 3,
    min: 0,
  },
  password: {
    length: false,
    number: false,
    uppercase: false,
    lowercase: false,
    symbol: false,
    match: false,
  },
  API_URL : "https://api.fi-track.manavkashyap.com",
  isNotificationOpen: false,
};

// ─── DOM refs ──────────────────────────────────────────────────────────────────
const messageContainer   = document.getElementById("message-container");
const registrationForm   = document.getElementById("registration-form");
const successCard        = document.getElementById("success-card");
const failureCard        = document.getElementById("failure-card");
const failureMessage     = document.getElementById("failure-message");
const resetButton        = document.getElementById("reset-button");

const passwordFields     = document.querySelectorAll(".password-field");
const passwordInput      = document.getElementById("password");
const confirmPassword    = document.getElementById("confirm-password");

const nextBtnDiv         = document.getElementById("next-step-container");
const nextBtn            = document.getElementById("next-step-button");
const prevBtn            = document.getElementById("prev-step-button");
const submitBtnDiv       = document.getElementById("submit-button-container");
const submitBtn          = document.getElementById("submit-button");

const passwordRequirements = {
  passwordLengthField: document.getElementById("password-length"),
  passwordNumber:      document.getElementById("password-number"),
  passwordLowercase:   document.getElementById("password-lowercase"),
  passwordUppercase:   document.getElementById("password-uppercase"),
  passwordSymbol:      document.getElementById("password-symbol"),
  isPasswordMatching:  document.getElementById("is-password-matching"),
};

// ─── Step navigation ───────────────────────────────────────────────────────────
function getNextStep(direction) {
  if (direction === "next") {
    data.step.current = Math.min(data.step.current + 1, data.step.max);
  } else {
    data.step.current = Math.max(data.step.current - 1, data.step.min);
  }
  return data.step.current;
}

function changeStepUi(stepToEnable) {
  // Show/hide submit vs next button
  if (stepToEnable === data.step.max) {
    nextBtnDiv.classList.add("hidden");
    submitBtnDiv.classList.remove("hidden");
    updateSubmitButton();
  } else {
    nextBtnDiv.classList.remove("hidden");
    submitBtnDiv.classList.add("hidden");
  }

  // Hide all steps, show target
  document.querySelectorAll(".steps").forEach((s) => s.classList.add("hidden"));
  document.querySelector(`.step-${stepToEnable}`)?.classList.remove("hidden");
}

nextBtn.addEventListener("click", () => changeStepUi(getNextStep("next")));
prevBtn.addEventListener("click", () => changeStepUi(getNextStep("prev")));

// ─── Password validation ───────────────────────────────────────────────────────
function validatePassword(pwd) {
  const rules = [
    { key: "length",    test: pwd.length >= 8,              el: passwordRequirements.passwordLengthField, label: "✓ At least 8 characters",    fail: "✗ At least 8 characters" },
    { key: "number",    test: /[0-9]/.test(pwd),            el: passwordRequirements.passwordNumber,      label: "✓ Contains a number",          fail: "✗ Contains a number" },
    { key: "lowercase", test: /[a-z]/.test(pwd),            el: passwordRequirements.passwordLowercase,   label: "✓ Contains a lowercase letter", fail: "✗ Contains a lowercase letter" },
    { key: "uppercase", test: /[A-Z]/.test(pwd),            el: passwordRequirements.passwordUppercase,   label: "✓ Contains an uppercase letter",fail: "✗ Contains an uppercase letter" },
    { key: "symbol",    test: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(pwd), el: passwordRequirements.passwordSymbol, label: "✓ Contains a symbol", fail: "✗ Contains a symbol" },
  ];

  rules.forEach(({ key, test, el, label, fail }) => {
    data.password[key] = test;
    el.textContent = test ? label : fail;
    el.className = `text-xs ${test ? "text-green-500 dark:text-green-400" : "text-red-500 dark:text-red-400"}`;
  });

  updateSubmitButton();
}

function checkPasswordMatch(pwd, confirm) {
  const match = pwd === confirm && pwd.length > 0;
  data.password.match = match;
  passwordRequirements.isPasswordMatching.textContent = match ? "✓ Passwords match" : "✗ Passwords match";
  passwordRequirements.isPasswordMatching.className = `text-xs ${match ? "text-green-500 dark:text-green-400" : "text-red-500 dark:text-red-400"}`;
  updateSubmitButton();
}

function updateSubmitButton() {
  const allValid = Object.values(data.password).every(Boolean);
  submitBtn.disabled = !allValid;
}

passwordInput.addEventListener("input", () => {
  validatePassword(passwordInput.value);
  checkPasswordMatch(passwordInput.value, confirmPassword.value);
});

confirmPassword.addEventListener("input", () => {
  checkPasswordMatch(passwordInput.value, confirmPassword.value);
});

// ─── Notification ──────────────────────────────────────────────────────────────
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

// ─── Reset failure state ───────────────────────────────────────────────────────
resetButton?.addEventListener("click", () => {
  failureCard.classList.add("hidden");
  registrationForm.classList.remove("hidden");
  // Reset to step 0
  data.step.current = 0;
  changeStepUi(0);
  registrationForm.reset();
});

// ─── Build payload from form ───────────────────────────────────────────────────
function createPayload() {
  const formData = new FormData(registrationForm);
  for (const [name, value] of formData) {
    data.userInfo[name] = value;
  }
  if (data.userInfo["date-of-birth"]) {
    data.userInfo.dob = data.userInfo["date-of-birth"];
  }
}

// ─── Register API call ─────────────────────────────────────────────────────────
async function register() {
  const payload = {
    user_name: (data.userInfo.username || "").toString().trim().toLowerCase(),
    first_name: (data.userInfo.first_name || "").toString().trim().toLowerCase(),
    last_name: (data.userInfo.last_name || "").toString().trim().toLowerCase() || null,
    email: (data.userInfo.email || "").toString().trim().toLowerCase(),
    gender: (data.userInfo.gender || "").toString().trim().toLowerCase(),
    dob: (data.userInfo.dob || "").toString().trim(),
    password: data.userInfo.password,
  };

  try {
    const response = await fetch(`${data.API_URL}/api/v1/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const responseData = await response.json().catch(() => ({}));

    if (response.ok) {
      // Hide form, show success, redirect to login after short delay
      registrationForm.classList.add("hidden");
      successCard.classList.remove("hidden");
      failureCard.classList.add("hidden");

      setTimeout(() => {
        window.location.href = "/";
      }, 1800);

    } else {
      const detail = responseData.detail;
      const message = Array.isArray(detail)
        ? detail.map((d) => d.msg || d).join(". ")
        : typeof detail === "string"
          ? detail
          : "Registration failed. Please try again.";

      if (failureMessage) failureMessage.textContent = message;
      registrationForm.classList.add("hidden");
      failureCard.classList.remove("hidden");
      successCard.classList.add("hidden");
    }

  } catch (error) {
    console.error("Registration error:", error);
    if (failureMessage) failureMessage.textContent = "Network error. Please check your connection.";
    registrationForm.classList.add("hidden");
    failureCard.classList.remove("hidden");
    successCard.classList.add("hidden");
  }
}

// ─── Form submit ───────────────────────────────────────────────────────────────
registrationForm.addEventListener("submit", (e) => {
  e.preventDefault();
  createPayload();
  register();
});