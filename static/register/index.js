const registerForm = document.getElementById("register_form");
const username = document.getElementById("username");
const email = document.getElementById("email");
const password = document.getElementById("password");
const confirmPassword = document.getElementById("password_check");
const password_match = document.querySelectorAll(".password_match");

password.addEventListener("input", (e) => {
  if (password.value === "" && confirmPassword.value === "") {
    password_match.forEach((elem) => {
      elem.textContent = "";
    });
    return;
  }
  isSamePassword(password.value, confirmPassword.value);
});

confirmPassword.addEventListener("input", (e) => {
  if (password.value === "" && confirmPassword.value === "") {
    password_match.forEach((elem) => {
      elem.textContent = "";
    });
    return;
  }
  isSamePassword(password.value, confirmPassword.value);
});

registerForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const data = {
    username: username.value,
    email: email.value,
    password: password.value,
    confirmPassword: confirmPassword.value,
  };

  if (!isSamePassword(password.value, confirmPassword.value)) {
    return alert("Please ensure the password are the same");
  }

  const response = await fetch("/api/auth/register", {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify(data),
  });

  const resolved = await response.json();

  if (resolved.message === "success") {
    alert("Registration Successful, Please Check Email For Verification Link");
    window.location.href = "/login";
    return;
  }

  alert("Invalid Credentials");
});

function isSamePassword(password, confirm_password) {
  if (password.toString() !== confirm_password.toString()) {
    password_match.forEach((elem) => {
      elem.textContent = "Password Does Not Match";
      elem.classList.remove("text-green-500");
      elem.classList.add("text-red-500");
    });
    return false;
  }
  password_match.forEach((elem) => {
    elem.textContent = "Passwords Match";
    elem.classList.add("text-green-500");
    elem.classList.remove("text-red-500");
  });
  return true;
}

function isMatched() {}
