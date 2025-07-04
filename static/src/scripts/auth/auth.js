const data = {
  userInfo: {
    username: "Unique Username",
    first_name: "Your First Name",
    last_name: "Your Last Name",
    email: "youremail@example.com",
    dob: "2025-06-30",
    gender: "Your Gender",
    password: "XXX-XXX-XXX-XXX",
    confirm_password: "XXX-XXX-XXX-XXX",
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
  API_URL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
  isNotificationOpen: false,
};

const body = document.querySelector("body");
const messageContainer = document.getElementById("message-container");

const registrationForm = document.getElementById("registration-form");
const passwordFields = document.querySelectorAll(".password-field");
const password = document.getElementById("password");
const confirmPassword = document.getElementById("confirm-password");

const passwordRequirements = {
  passwordLengthField: document.getElementById("password-length"),
  passwordNumber: document.getElementById("password-number"),
  passwordLowercase: document.getElementById("password-lowercase"),
  passwordUppercase: document.getElementById("password-uppercase"),
  passwordSymbol: document.getElementById("password-symbol"),
  isPasswordMatching: document.getElementById("is-password-matching"),
};

const nextBtnDiv = document.getElementById("next-step-container");
const nextBtn = document.getElementById("next-step-button");
const prevBtn = document.getElementById("prev-step-button");
const submitBtnDiv = document.getElementById("submit-button-container");
const submitBtn = document.getElementById("submit-button");

function getNextStep(direction) {
  const normalisedDirection = direction.toLowerCase();

  if (normalisedDirection === "next") {
    data.step.current =
      data.step.current + 1 > data.step.max
        ? data.step.max
        : data.step.current + 1;

    return Number(data.step.current);
  }
  if (normalisedDirection === "prev") {
    data.step.current =
      data.step.current - 1 < data.step.min
        ? data.step.min
        : data.step.current - 1;

    return Number(data.step.current);
  }
}

function changeStepUi(stepToEnable) {
  if (stepToEnable === 3) {
    toggleButton(submitBtn);

    nextBtnDiv.classList.add("hidden");
    submitBtnDiv.classList.remove("hidden");
  } else {
    nextBtnDiv.classList.remove("hidden");
    submitBtnDiv.classList.add("hidden");
  }

  const allSteps = document.querySelectorAll(".steps");

  allSteps.forEach((step) => {
    step.classList.add("hidden");
  });

  const nextStep = document.querySelector(`.step-${stepToEnable}`);
  nextStep.classList.remove("hidden");
}

nextBtn.addEventListener("click", (e) => {
  const stepToGoTo = getNextStep("next");
  changeStepUi(stepToGoTo);
});

prevBtn.addEventListener("click", (e) => {
  const stepToGoTo = getNextStep("prev");
  changeStepUi(stepToGoTo);
});

function matchPassword(password, confirm_password) {
  const normlizedPassword = password.toString().trim();
  const normlizedConfirmPassword = confirm_password.toString().trim();

  if (normlizedPassword !== normlizedConfirmPassword) {
    data.password.match = false;
    toggleButton(submitBtn);
    return false;
  }
  data.password.match = true;
  toggleButton(submitBtn);
  return true;
}

function trimInput(string) {
  return string.toString().trim();
}

passwordFields.forEach((field, index) => {
  field.addEventListener("input", (e) => {
    if (matchPassword(password.value, confirmPassword.value)) {
      passwordRequirements.isPasswordMatching.classList.add("text-green-600");
      passwordRequirements.isPasswordMatching.classList.remove("text-red-600");
      return;
    }
    passwordRequirements.isPasswordMatching.textContent =
      "Password Does Not Match";
    passwordRequirements.isPasswordMatching.classList.remove("text-green-600");
    passwordRequirements.isPasswordMatching.classList.add("text-red-600");
  });
});

password.addEventListener("input", (e) => {
  validatePassword(password.value);
});

function validatePassword(password) {
  const minLength = 8;
  const hasNumber = /[0-9]/;
  const hasLowercase = /[a-z]/;
  const hasUppercase = /[A-Z]/;
  const hasSymbol = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/;

  if (password.length > minLength) {
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

  toggleButton(submitBtn);
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

async function register() {
  const payload = {
    username: data.userInfo.username.toString().toLowerCase().trim(),
    first_name: data.userInfo.first_name.toString().toLowerCase().trim(),
    last_name: data.userInfo.last_name.toString().toLowerCase().trim(),
    email: data.userInfo.email.toString().toLowerCase().trim(),
    gender: data.userInfo.gender.toString().toLowerCase().trim(),
    dob: data.userInfo.dob.toString().toLowerCase().trim(),
    password: data.userInfo.password,
  };

  const response = await fetch(`${data.API_URL}/api/v1/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  try {
    const responseData = await response.json();

    if (response.ok) {
      data.isNotificationOpen = false;
      createNotification("Registration Successful, Please Check Your Email");
      console.log(responseData);
    } else {
      // HTTP status is not 2xx (e.g., 401, 422, 500)
      console.log("Registration Failed with status:", response.status);
      console.log("Backend error response:", responseData.detail);
      data.isNotificationOpen = false;
      createNotification(responseData.detail);
    }
  } catch (error) {
    // Network errors or issues before the response is received
    console.error("Network or unexpected error during login:", error);
    data.isNotificationOpen = false;
    createNotification(
      "Something Went Wrong (Network Error). Please Check your connection."
    );
  }
}

registrationForm.addEventListener("submit", (e) => {
  e.preventDefault();
  createPayload();
  console.log(data.userInfo);
  register();
});

function createPayload() {
  const formData = new FormData(registrationForm);

  for (const [name, value] of formData) {
    data.userInfo[name] = value;
  }
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
