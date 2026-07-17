document.addEventListener("DOMContentLoaded", () => {
    const path = window.location.pathname;

    // --- REGISTER CONTROLLER ---
    const registerForm = document.getElementById("register-form");
    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const username = document.getElementById("username").value;
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;
            const confirmPassword = document.getElementById("confirm-password").value;
            const errorDiv = document.getElementById("error-message");

            errorDiv.classList.add("hidden");

            if (password !== confirmPassword) {
                errorDiv.textContent = "Passwords do not match.";
                errorDiv.classList.remove("hidden");
                return;
            }

            try {
                const response = await fetch("/register", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, email, password })
                });
                const data = await response.json();

                if (response.ok) {
                    window.location.href = "login.html";
                } else {
                    errorDiv.textContent = data.error || "Registration failed.";
                    errorDiv.classList.remove("hidden");
                }
            } catch (err) {
                errorDiv.textContent = "Cannot connect to backend server.";
                errorDiv.classList.remove("hidden");
            }
        });
    }

    // --- LOGIN CONTROLLER ---
    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;
            const errorDiv = document.getElementById("error-message");

            errorDiv.classList.add("hidden");

            try {
                const response = await fetch("/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, password })
                });
                const data = await response.json();

                if (response.ok) {
                    window.location.href = "dashboard.html";
                } else {
                    errorDiv.textContent = data.error || "Invalid username or password.";
                    errorDiv.classList.remove("hidden");
                }
            } catch (err) {
                errorDiv.textContent = "Cannot connect to backend server.";
                errorDiv.classList.remove("hidden");
            }
        });
    }

    // --- DASHBOARD AND PROTECTED INITIALIZATION CONTROLLER ---
    const dashboardContainer = document.getElementById("dashboard-container");
    if (dashboardContainer) {
        async function verifyAndLoadDashboard() {
            try {
                // Request initial state check
                const dashRes = await fetch("/dashboard");
                if (!dashRes.ok) {
                    window.location.href = "login.html";
                    return;
                }
                const dashData = await dashRes.json();

                // Fetch comprehensive profile details
                const profileRes = await fetch("/profile");
                if (!profileRes.ok) {
                    window.location.href = "login.html";
                    return;
                }
                const profileData = await profileRes.json();

                // Hydrate view layer components safely
                document.getElementById("welcome-message").textContent = `Welcome, ${dashData.username}!`;
                document.getElementById("user-role").textContent = profileData.role;
                document.getElementById("user-email").textContent = profileData.email;
                document.getElementById("user-date").textContent = profileData.created_at;

                // Reveal verified view state block
                dashboardContainer.classList.remove("hidden");
            } catch (err) {
                window.location.href = "login.html";
            }
        }

        // --- LOGOUT EVENT ---
        document.getElementById("logout-btn").addEventListener("click", async () => {
            try {
                await fetch("/logout");
                window.location.href = "login.html";
            } catch (err) {
                alert("An error occurred during logout.");
            }
        });

        verifyAndLoadDashboard();
    }
});