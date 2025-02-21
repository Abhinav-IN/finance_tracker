const loginForm = document.getElementById("login_form");

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const data = { username, password };
  const response = await fetch("/api/login", {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify(data),
  });

  const resolved = await response.json();

  if (resolved.message === "success") {
    alert("Welcome Back");
    window.location.href = "/dashboard";
    return;
  }

  alert("Invalid Credentials");
});
