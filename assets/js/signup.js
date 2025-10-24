// 🌟 Signup Page Script

document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  const nameInput = document.getElementById("name");
  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");
  const confirmPasswordInput = document.getElementById("confirm-password");

  // ✅ Basic Form Validation
  form.addEventListener("submit", function (event) {
    const name = nameInput.value.trim();
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();
    const confirmPassword = confirmPasswordInput.value.trim();

    // Empty fields
    if (!name || !email || !password || !confirmPassword) {
      alert("Please fill in all fields.");
      event.preventDefault();
      return;
    }

    // Email format check
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

    // Confirm password check
    if (password !== confirmPassword) {
      alert("Passwords do not match.");
      event.preventDefault();
      return;
    }

    // ✅ You can add backend submission logic here later
  });

  // 👁️ Show/Hide Password Toggle for both password fields
  function addPasswordToggle(inputField) {
    const toggleButton = document.createElement("span");
    toggleButton.textContent = "👁️";
    toggleButton.style.cursor = "pointer";
    toggleButton.style.position = "absolute";
    toggleButton.style.right = "10px";
    toggleButton.style.top = "35px";
    toggleButton.style.userSelect = "none";

    const wrapper = inputField.parentElement;
    wrapper.style.position = "relative";
    wrapper.appendChild(toggleButton);

    toggleButton.addEventListener("click", () => {
      if (inputField.type === "password") {
        inputField.type = "text";
        toggleButton.textContent = "🙈";
      } else {
        inputField.type = "password";
        toggleButton.textContent = "👁️";
      }
    });
  }

  addPasswordToggle(passwordInput);
  addPasswordToggle(confirmPasswordInput);
});
