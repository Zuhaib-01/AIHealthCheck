// 🌟 Login Page Script

document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");

  // ✅ Basic Form Validation
  form.addEventListener("submit", function (event) {
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();

    if (email === "" || password === "") {
      alert("Please fill in all fields.");
      event.preventDefault();
      return;
    }

    // Simple email format check
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      alert("Please enter a valid email address.");
      event.preventDefault();
      return;
    }

    // Password length check
    if (password.length < 6) {
      alert("Password must be at least 6 characters long.");
      event.preventDefault();
      return;
    }

    // You can add more logic here when connecting Flask later
    // e.g., sending data via fetch() or allowing normal form submit
  });

  // 👁️ Optional: Show/Hide Password Feature
  const toggleButton = document.createElement("span");
  toggleButton.textContent = "👁️";
  toggleButton.style.cursor = "pointer";
  toggleButton.style.position = "absolute";
  toggleButton.style.right = "10px";
  toggleButton.style.top = "35px";
  toggleButton.style.userSelect = "none";

  const passwordFieldWrapper = passwordInput.parentElement;
  passwordFieldWrapper.style.position = "relative";
  passwordFieldWrapper.appendChild(toggleButton);

  toggleButton.addEventListener("click", () => {
    if (passwordInput.type === "password") {
      passwordInput.type = "text";
      toggleButton.textContent = "🙈";
    } else {
      passwordInput.type = "password";
      toggleButton.textContent = "👁️";
    }
  });
});
