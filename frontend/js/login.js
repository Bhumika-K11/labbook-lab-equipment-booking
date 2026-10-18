// When the login form is submitted (button clicked or Enter pressed)
document.getElementById("login-form").addEventListener("submit", async function (event) {
    event.preventDefault();     // stop the browser from reloading the page

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        // Send email + password to the backend login API
        const data = await api("POST", "/api/login", { email: email, password: password });

        showMessage("Welcome, " + data.user.name + "! Opening your dashboard...", "success");

        // After a short pause, go to the dashboard page
        setTimeout(function () {
            window.location.href = "dashboard.html";
        }, 800);
    } catch (error) {
        // Show the backend's error message in red
        showMessage(error.message, "danger");
    }
});