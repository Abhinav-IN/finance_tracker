import { data, token, syncRivets, onPageReady } from "../main.js";

const API_URL = import.meta.env.PROD ? "" : (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000");

const passwordRequirements = {
  isPasswordMatching: document.getElementById("is-password-matching"),
  passwordLengthField: document.getElementById("password-length"),
  passwordNumber: document.getElementById("password-number"),
  passwordLowercase: document.getElementById("password-lowercase"),
  passwordUppercase: document.getElementById("password-uppercase"),
  passwordSymbol: document.getElementById("password-symbol"),
};

const userProfileEditPanel = document.getElementById("user-profile-edit-panel");
const openUserProfileEdit = document.getElementById("open-user-profile-edit-button");
const closeUserProfileEdit = document.getElementById("close-user-profile-edit-button");
const userChangeOptions = document.getElementById("user-change-options");
const optionToEditBtn = document.querySelectorAll(".option-to-edit");
const optionsPanel = document.querySelectorAll(".options-panel");
const backButtons = document.querySelectorAll(".go-back");

const password = document.getElementById("new-password");
const confirmPassword = document.getElementById("confirm-password");

const updateDateOfBirthBtn = document.getElementById("date-of-birth-change-button");
const updatePasswordBtn = document.getElementById("password-change-button");
const updateUsernameBtn = document.getElementById("username-change-button");
const updateEmailBtn = document.getElementById("email-change-button");
const updateNameBtn = document.getElementById("name-change-button");
const loadDemoAccountBtn = document.getElementById("load-demo-account-button");
const demoAccountStatus = document.getElementById("demo-account-status");

function formatApiError(result, fallback) {
  if (!result) return fallback;
  if (typeof result.detail === "string") return result.detail;
  if (Array.isArray(result.detail)) {
    return result.detail.map((d) => d.msg || JSON.stringify(d)).join(". ");
  }
  return fallback;
}

async function refreshProfile() {
  try {
    const response = await fetch(`${API_URL}/api/v1/user/profile`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });
    if (!response.ok) {
      throw new Error(`Failed to load profile (${response.status})`);
    }
    const result = await response.json();
    Object.assign(data.user, result);
    syncRivets();
    return result;
  } catch (error) {
    console.error("Profile load failed:", error);
    throw error;
  }
}

function prefillEditForms() {
  const user = data.user || {};
  const setVal = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.value = val ?? "";
  };
  setVal("first_name", user.first_name);
  setVal("last_name", user.last_name);
  setVal("email", user.email);
  setVal("username", user.user_name);
  if (user.dob) {
    const d = new Date(user.dob);
    if (!Number.isNaN(d.getTime())) {
      setVal("date-of-birth", d.toISOString().slice(0, 10));
    }
  }
}

function resetEditPanels() {
  optionsPanel.forEach((panel) => panel.classList.add("hidden"));
  userChangeOptions?.classList.remove("hidden");
}

function closeEditPanel() {
  userProfileEditPanel?.classList.add("hidden");
  resetEditPanels();
}

function changeOptionsPanel({ panelToEnable = null } = {}) {
  if (!panelToEnable) {
    alert("Panel to enable is invalid.");
    return;
  }
  optionsPanel.forEach((panel) => panel.classList.add("hidden"));
  userChangeOptions?.classList.add("hidden");
  panelToEnable.classList.remove("hidden");
}

function toggleFieldColour(field, state) {
  if (!field) return;
  field.classList.toggle("text-red-600", !state);
  field.classList.toggle("text-green-600", state);
}

function toggleButton(buttonToHide) {
  if (!buttonToHide) return;
  const ready =
    data.password.length &&
    data.password.number &&
    data.password.uppercase &&
    data.password.lowercase &&
    data.password.symbol &&
    data.password.match;
  buttonToHide.disabled = !ready;
}

function refreshPasswordFormState() {
  const pw = password?.value ?? "";
  const confirm = confirmPassword?.value ?? "";
  const minLength = 8;
  const hasSymbol = /[!@#$%^&*(),.?":{}|<>]/;

  data.password.length = pw.length >= minLength;
  data.password.number = /[0-9]/.test(pw);
  data.password.lowercase = /[a-z]/.test(pw);
  data.password.uppercase = /[A-Z]/.test(pw);
  data.password.symbol = hasSymbol.test(pw);
  data.password.match = Boolean(pw) && pw === confirm;

  toggleFieldColour(passwordRequirements.passwordLengthField, data.password.length);
  toggleFieldColour(passwordRequirements.passwordNumber, data.password.number);
  toggleFieldColour(passwordRequirements.passwordLowercase, data.password.lowercase);
  toggleFieldColour(passwordRequirements.passwordUppercase, data.password.uppercase);
  toggleFieldColour(passwordRequirements.passwordSymbol, data.password.symbol);

  if (passwordRequirements.isPasswordMatching) {
    passwordRequirements.isPasswordMatching.textContent = data.password.match
      ? "Password Match"
      : "Password Does Not Match";
    toggleFieldColour(passwordRequirements.isPasswordMatching, data.password.match);
  }

  toggleButton(updatePasswordBtn);
}

async function updateTheName() {
  const newFirstName = document.getElementById("first_name")?.value?.trim();
  const newLastName = document.getElementById("last_name")?.value?.trim();

  if (!newFirstName) return alert("Please enter a first name.");
  if (!newLastName) return alert("Please enter a last name.");

  try {
    const params = new URLSearchParams({ newFirstName, newLastName });
    const response = await fetch(`${API_URL}/api/v1/user/update_fullname?${params}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(formatApiError(result, "Failed to update name."));
    }
    await refreshProfile();
    alert("Name updated successfully.");
    closeEditPanel();
  } catch (error) {
    console.error(error);
    alert(error.message || "Something went wrong. Please try again.");
  }
}

async function updateTheEmail() {
  const newEmail = document.getElementById("email")?.value?.trim();
  if (!newEmail) return alert("Please enter an email.");

  try {
    const params = new URLSearchParams({ newEmail });
    const response = await fetch(`${API_URL}/api/v1/user/update_email?${params}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(formatApiError(result, "Failed to update email."));
    }
    await refreshProfile();
    alert("Email updated successfully.");
    closeEditPanel();
  } catch (error) {
    console.error(error);
    alert(error.message || "Something went wrong. Please try again.");
  }
}

async function updateTheUsername() {
  const newUsername = document.getElementById("username")?.value?.trim();
  if (!newUsername) return alert("Please enter a username.");

  try {
    const params = new URLSearchParams({ newUserName: newUsername });
    const response = await fetch(`${API_URL}/api/v1/user/update_username?${params}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(formatApiError(result, "Failed to update username."));
    }
    await refreshProfile();
    alert("Username updated successfully.");
    closeEditPanel();
  } catch (error) {
    console.error(error);
    alert(error.message || "Something went wrong. Please try again.");
  }
}

async function updateDateOfBirth() {
  const newDob = document.getElementById("date-of-birth")?.value;
  if (!newDob) return alert("Please select a date of birth.");

  try {
    const params = new URLSearchParams({ new_dob: newDob });
    const response = await fetch(`${API_URL}/api/v1/user/update_dob?${params}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(formatApiError(result, "Failed to update date of birth."));
    }
    await refreshProfile();
    alert("Date of birth updated successfully.");
    closeEditPanel();
  } catch (error) {
    console.error(error);
    alert(error.message || "Something went wrong. Please try again.");
  }
}

async function updateThePassword() {
  const oldPassword = document.getElementById("old-password")?.value ?? "";
  const newPassword = document.getElementById("new-password")?.value ?? "";
  const confirm = document.getElementById("confirm-password")?.value ?? "";

  if (!oldPassword) return alert("Please enter your current password.");
  if (!newPassword) return alert("Please enter a new password.");
  if (newPassword !== confirm) return alert("New passwords do not match.");
  if (updatePasswordBtn?.disabled) return alert("Please meet all password requirements.");

  try {
    const response = await fetch(`${API_URL}/api/v1/user/change-password`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token()}`,
      },
      body: JSON.stringify({
        old_password: oldPassword,
        new_password: newPassword,
      }),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(formatApiError(result, "Failed to update password."));
    }
    document.getElementById("old-password").value = "";
    document.getElementById("new-password").value = "";
    document.getElementById("confirm-password").value = "";
    refreshPasswordFormState();
    alert(result.message || "Password updated successfully.");
    closeEditPanel();
  } catch (error) {
    console.error(error);
    alert(error.message || "Something went wrong. Please try again.");
  }
}

if (openUserProfileEdit) {
  openUserProfileEdit.addEventListener("click", () => {
    prefillEditForms();
    resetEditPanels();
    userProfileEditPanel?.classList.remove("hidden");
  });
}

if (closeUserProfileEdit) {
  closeUserProfileEdit.addEventListener("click", closeEditPanel);
}

backButtons.forEach((button) => {
  button.addEventListener("click", () => {
    changeOptionsPanel({ panelToEnable: userChangeOptions });
  });
});

optionToEditBtn.forEach((button) => {
  button.addEventListener("click", (e) => {
    const btn = e.currentTarget?.closest?.("[data-value]") || e.currentTarget;
    const value = btn?.getAttribute?.("data-value");
    const panel = value ? document.getElementById(value) : null;
    if (panel) {
      changeOptionsPanel({ panelToEnable: panel });
      if (value === "password-change") {
        document.getElementById("old-password").value = "";
        document.getElementById("new-password").value = "";
        document.getElementById("confirm-password").value = "";
        refreshPasswordFormState();
      }
    }
  });
});

document.getElementById("old-password")?.addEventListener("input", refreshPasswordFormState);
password?.addEventListener("input", refreshPasswordFormState);
confirmPassword?.addEventListener("input", refreshPasswordFormState);

updateNameBtn?.addEventListener("click", updateTheName);
updateEmailBtn?.addEventListener("click", updateTheEmail);
updateUsernameBtn?.addEventListener("click", updateTheUsername);
updatePasswordBtn?.addEventListener("click", updateThePassword);
updateDateOfBirthBtn?.addEventListener("click", updateDateOfBirth);

async function loadDemoAccount() {
  if (!loadDemoAccountBtn || loadDemoAccountBtn.disabled) return;

  loadDemoAccountBtn.disabled = true;
  demoAccountStatus?.classList.remove("hidden");

  try {
    const response = await fetch(`${API_URL}/api/v1/auth/demo`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    const result = await response.json().catch(() => ({}));

    if (!response.ok || !result.access_token) {
      throw new Error(formatApiError(result, "Could not load demo account."));
    }

    localStorage.setItem("jwtToken", result.access_token);
    await refreshProfile();
    window.location.href = "/dashboard/";
  } catch (error) {
    console.error("Demo account load failed:", error);
    alert(error.message || "Could not load demo account. Please try again.");
  } finally {
    if (loadDemoAccountBtn) loadDemoAccountBtn.disabled = false;
    demoAccountStatus?.classList.add("hidden");
  }
}

loadDemoAccountBtn?.addEventListener("click", loadDemoAccount);

onPageReady(async () => {
  await refreshProfile();
});
