import { data } from "../main.js";
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const passwordRequirements = {
  isPasswordMatching: document.getElementById("is-password-matching"),
  passwordLengthField: document.getElementById("password-length"),
  passwordNumber: document.getElementById("password-number"),
  passwordLowercase: document.getElementById("password-lowercase"),
  passwordUppercase: document.getElementById("password-uppercase"),
  passwordSymbol: document.getElementById("password-symbol"),
};

const userProfileEditPanel = document.getElementById("user-profile-edit-panel");
const openUserProfileEdit = document.getElementById(
  "open-user-profile-edit-button"
);
const closeUserProfileEdit = document.getElementById(
  "close-user-profile-edit-button"
);

openUserProfileEdit.addEventListener("click", (e) => {
  userProfileEditPanel.classList.remove("hidden");
});
closeUserProfileEdit.addEventListener("click", (e) => {
  userProfileEditPanel.classList.add("hidden");
});

const passwordFields = document.querySelectorAll(".passwordFields");
const userChangeOptions = document.getElementById("user-change-options");
const optionToEditBtn = document.querySelectorAll(".option-to-edit");
const optionsPanel = document.querySelectorAll(".options-panel");
const backButtons = document.querySelectorAll(".go-back");

backButtons.forEach((button) => {
  button.addEventListener("click", (e) => {
    changeOptionsPanel({ panelToEnable: userChangeOptions });
  });
});

optionToEditBtn.forEach((button) => {
  button.addEventListener("click", (e) => {
    const value = e.target.getAttribute("data-value");

    changeOptionsPanel({
      panelToEnable: document.getElementById(value),
    });
  });
});

function changeOptionsPanel({ panelToEnable = null } = {}) {
  if (!panelToEnable || panelToEnable === "" || panelToEnable === undefined) {
    alert("Panel To Enable Is Invalid");
  }
  optionsPanel.forEach((panel) => {
    panel.classList.add("hidden");
  });
  userChangeOptions.classList.add("hidden");
  panelToEnable.classList.remove("hidden");
}

const password = document.getElementById("new-password");
const confirmPassword = document.getElementById("confirm-password");

passwordFields.forEach((field, index) => {
  field.addEventListener("input", (e) => {
    if (
      matchPassword({
        password: password.value,
        passwordToMatch: confirmPassword.value,
      })
    ) {
      passwordRequirements.isPasswordMatching.classList.add("text-green-600");
      passwordRequirements.isPasswordMatching.classList.remove("text-red-600");
      passwordRequirements.isPasswordMatching.textContent = "Password Match";
      return;
    }
    passwordRequirements.isPasswordMatching.textContent =
      "Password Does Not Match";
    passwordRequirements.isPasswordMatching.classList.remove("text-green-600");
    passwordRequirements.isPasswordMatching.classList.add("text-red-600");
  });
});

password.addEventListener("input", (e) => {
  validatePassword(e.target.value);
});

function matchPassword({ password = "", passwordToMatch = "" } = {}) {
  console.log(password, passwordToMatch);
  if (password)
    if (password === passwordToMatch) {
      console.log(true);
      data.password.match = true;
      return true;
    }

  data.password.match = false;

  return false;
}

function validatePassword(password) {
  const minLength = 8;
  const hasNumber = /[0-9]/;
  const hasLowercase = /[a-z]/;
  const hasUppercase = /[A-Z]/;
  const hasSymbol = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/;

  if (password.toString().length > minLength) {
    toggleFieldColour(passwordRequirements.passwordLengthField, true);
    data.password.length = true;
  } else {
    toggleFieldColour(passwordRequirements.passwordLengthField, false);
    data.password.length = false;
  }

  if (hasNumber.test(password)) {
    toggleFieldColour(passwordRequirements.passwordNumber, true);
    data.password.number = true;
  } else {
    toggleFieldColour(passwordRequirements.passwordNumber, false);
    data.password.number = false;
  }

  if (hasLowercase.test(password)) {
    toggleFieldColour(passwordRequirements.passwordLowercase, true);
    data.password.lowercase = true;
  } else {
    toggleFieldColour(passwordRequirements.passwordLowercase, false);
    data.password.lowercase = false;
  }
  if (hasUppercase.test(password)) {
    toggleFieldColour(passwordRequirements.passwordUppercase, true);
    data.password.uppercase = true;
  } else {
    toggleFieldColour(passwordRequirements.passwordUppercase, false);
    data.password.uppercase = false;
  }

  if (hasSymbol.test(password)) {
    toggleFieldColour(passwordRequirements.passwordSymbol, true);
    data.password.symbol = true;
  } else {
    toggleFieldColour(passwordRequirements.passwordSymbol, false);
    data.password.symbol = false;
  }

  toggleButton(document.getElementById("password-change-button"));
}

function toggleFieldColour(field, state) {
  if (!state) {
    field.classList.add("text-red-600");
    field.classList.remove("text-green-600");
    return;
  }
  field.classList.remove("text-red-600");
  field.classList.add("text-green-600");
  return;
}

function toggleButton(buttonToHide) {
  if (
    !data.password.length ||
    !data.password.number ||
    !data.password.uppercase ||
    !data.password.lowercase ||
    !data.password.symbol ||
    !data.password.match
  ) {
    buttonToHide.disabled = true;
    return;
  }
  buttonToHide.disabled = false;
  return;
}

const updateDateOfBirthBtn = document.getElementById(
  "date-of-birth-change-button"
);
const updatePasswordBtn = document.getElementById("password-change-button");
const updateUsernameBtn = document.getElementById("username-change-button");
const updateEmailBtn = document.getElementById("email-change-button");
const updateNameBtn = document.getElementById("name-change-button");

updateNameBtn.addEventListener("click", (e) => {
  updateTheName();
});

updateEmailBtn.addEventListener("click", (e) => {
  updateTheEmail();
});

updateUsernameBtn.addEventListener("click", (e) => {
  updateTheUsername();
});
updatePasswordBtn.addEventListener("click", (e) => {
  updateThePassword();
});
updateDateOfBirthBtn.addEventListener("click", (e) => {
  updateDateOfBirth();
});

async function updateTheName() {
  const newFirstName = document.getElementById("first_name").value;
  const newLastName = document.getElementById("last_name").value;

  try {
    if (!newFirstName || newFirstName === "" || newFirstName === null) {
      console.log("new firstname not provided");
      return alert("new firstname not provided");
    }
    if (!newLastName || newLastName === "" || newLastName === null) {
      console.log("new firstname not provided");
      return alert("new firstname not provided");
    }

    const response = await fetch(
      `${API_URL}/api/v1/user/update_username?update_fullname?newFirstName=${newFirstName}&newLastName=${newLastName}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token()}`,
        },
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      console.error(
        `HTTP error! status: ${response.status}, message: ${errorText}`
      );
      throw new Error(
        `Failed to fetch income: ${response.status} ${response.statusText}`
      );
    }

    const resolved = await response.json();
    console.log(resolved);
  } catch (error) {
    console.log(error);
    alert("oops something went wrong, please again later.");
  }
}

async function updateTheEmail() {
  const newEmail = document.getElementById("email").value;

  try {
    if (!newEmail || newEmail === "" || newEmail === null) {
      console.log("Email Not Provided");
      return alert("Email Not Provided");
    }

    const response = await fetch(
      `${API_URL}/api/v1/user/update_email?newEmail=${newEmail}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token()}`,
        },
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      console.error(
        `HTTP error! status: ${response.status}, message: ${errorText}`
      );
      throw new Error(
        `Failed to fetch income: ${response.status} ${response.statusText}`
      );
    }

    const resolved = await response.json();
    console.log(resolved);
  } catch (error) {
    console.log(error);
    alert("oops something went wrong, please again later.");
  }
}

async function updateDateOfBirth() {
  const newDob = document.getElementById("date-of-birth").value;

  try {
    if (!newDob || newDob === "" || newDob === null) {
      console.log("Email Not Provided");
      return alert("Email Not Provided");
    }

    const response = await fetch(
      `${API_URL}/api/v1/user/update_dob?new_dob=${newDob}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token()}`,
        },
      }
    );
    if (!response.ok) {
      const errorText = await response.text();
      console.error(
        `HTTP error! status: ${response.status}, message: ${errorText}`
      );
      throw new Error(
        `Failed to fetch income: ${response.status} ${response.statusText}`
      );
    }

    const resolved = await response.json();
    console.log(resolved);
  } catch (error) {
    console.log(error);
    alert("oops something went wrong, please again later.");
  }
}

async function updateThePassword() {
  const newDob = document.getElementById("date-of-birth").value;

  try {
    if (!newDob || newDob === "" || newDob === null) {
      console.log("Email Not Provided");
      return alert("Email Not Provided");
    }

    const response = await fetch(
      `${API_URL}/api/v1/user/update_dob?new_dob=${newDob}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token()}`,
        },
      }
    );

    const resolved = await response.json();
    console.log(resolved);
  } catch (error) {
    console.log(error);
    alert("oops something went wrong, please again later.");
  }
}

async function updateTheUsername() {
  const newUsername = document.getElementById("username").value;

  try {
    if (!newUsername || newUsername === "" || newUsername === null) {
      console.log("username not provided");
      return alert("username not provided");
    }

    const response = await fetch(
      `${API_URL}/api/v1/user/update_username?newUserName=${newUsername}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token()}`,
        },
      }
    );
    if (!response.ok) {
      const errorText = await response.text();
      console.error(
        `HTTP error! status: ${response.status}, message: ${errorText}`
      );
      throw new Error(
        `Failed to fetch income: ${response.status} ${response.statusText}`
      );
    }
    if (response.status === 200) {
      const resolved = await response.json();
      console.log(resolved);
      alert("username updated");
    }
  } catch (error) {
    console.log(error);
    alert("oops something went wrong, please again later.");
  }
}

function token() {
  const jwtToken = localStorage.getItem("jwtToken");
  if (!jwtToken) {
    console.error("No JWT token found. User is not logged in.");
    window.location.href = "/login.html";
    return;
  }
  return jwtToken;
}
