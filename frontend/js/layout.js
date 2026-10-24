// Shared code for every page AFTER login:
// 1) checks the user is logged in, 2) builds the top navigation bar, 3) handles logout.
// requiredRole (optional): "assistant" for assistant-only pages.
async function setupPage(requiredRole) {
    // Ask the backend who is logged in. If nobody -> api.js sends us to the login page (FR-02)
    const data = await api("GET", "/api/me");
    const user = data.user;

    // Wrong role (e.g. a student opening an assistant page) -> back to dashboard
    if (requiredRole && user.role !== requiredRole) {
        window.location.href = "dashboard.html";
        throw new Error("Not allowed");
    }

    // Different menu links for each role
    let links;
    if (user.role === "assistant") {
        links = [
            ["Dashboard", "dashboard.html"],
            ["Fault tickets", "admin-faults.html"],
            ["Equipment", "admin-equipment.html"],
            ["Schedule", "admin-schedule.html"],
        ];
    } else {
        links = [
            ["Dashboard", "dashboard.html"],
            ["Equipment", "equipment.html"],
            ["My bookings", "my-bookings.html"],
            ["Report fault", "report-fault.html"],
        ];
    }

    // Build the Bootstrap navigation bar (fixed text only - user data is added safely below)
    const nav = document.getElementById("navbar");
    nav.className = "navbar navbar-expand-md navbar-dark bg-dark mb-4";
    nav.innerHTML = `
      <div class="container">
        <a class="navbar-brand fw-semibold" href="dashboard.html">LabBook</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#nav-links">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="nav-links">
          <ul class="navbar-nav me-auto" id="nav-list"></ul>
          <span class="navbar-text me-3" id="nav-user"></span>
          <button class="btn btn-outline-light btn-sm" id="logout-btn">Log out</button>
        </div>
      </div>`;

    // Add the menu links (highlight the page we are on)
    const currentPage = window.location.pathname.split("/").pop();
    const list = document.getElementById("nav-list");
    links.forEach(function (link) {
        const li = document.createElement("li");
        li.className = "nav-item";
        const a = document.createElement("a");
        a.className = "nav-link" + (link[1] === currentPage ? " active" : "");
        a.href = link[1];
        a.textContent = link[0];
        li.appendChild(a);
        list.appendChild(li);
    });

    // Show the user's name and role (textContent = safe, NFR-09)
    const roleName = user.role === "assistant" ? "Lab Assistant" : "Student";
    document.getElementById("nav-user").textContent = user.name + " (" + roleName + ")";

    // Log out button
    document.getElementById("logout-btn").addEventListener("click", async function () {
        await api("POST", "/api/logout");
        window.location.href = "index.html";
    });

    return user;
}