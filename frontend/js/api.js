// ONE helper used by every page to talk to the backend API.
// method = "GET" or "POST", url = e.g. "/api/login", body = data to send (optional)
async function api(method, url, body) {
    const options = { method: method, headers: {}, credentials: "same-origin" };

    if (body !== undefined) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(body);       // turn JavaScript data into JSON text
    }

    const response = await fetch(url, options);    // send the request and wait for the reply

    let data = {};
    try {
        data = await response.json();              // turn the JSON reply into JavaScript data
    } catch (e) {
        // reply had no JSON - keep data empty
    }

    // 401 = not logged in -> go to the login page (FR-02)
    if (response.status === 401 && url !== "/api/login") {
        window.location.href = "index.html";
        throw new Error("Please log in first");
    }

    // Any other error (400, 403, 409...) -> pass the backend's message to the page
    if (!response.ok) {
        throw new Error(data.error || "Something went wrong");
    }

    return data;
}

// Show a green (success) or red (danger) message box on the page
function showMessage(text, type) {
    const box = document.getElementById("message");
    if (!box) return;
    box.className = "alert alert-" + type;
    box.textContent = text;                         // textContent = safe, no HTML injection (NFR-09)
}