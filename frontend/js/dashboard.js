// Shortcut cards for each role: [title, description, page]
const STUDENT_CARDS = [
    ["Book equipment", "See free slots and book a one-hour slot.", "equipment.html"],
    ["My bookings", "View or cancel your upcoming bookings.", "my-bookings.html"],
    ["Report a fault", "Tell the lab staff that something is broken.", "report-fault.html"],
];

const ASSISTANT_CARDS = [
    ["Fault tickets", "Review reported faults and update their status.", "admin-faults.html"],
    ["Manage equipment", "Add new items or edit existing ones.", "admin-equipment.html"],
    ["Daily schedule", "See all bookings for a chosen day.", "admin-schedule.html"],
];

// Make one Bootstrap card (built with createElement + textContent = safe)
function makeCard(title, text, page) {
    const col = document.createElement("div");
    col.className = "col-12 col-md-4";

    const card = document.createElement("a");
    card.className = "card h-100 shadow-sm text-decoration-none text-reset dash-card";
    card.href = page;

    const body = document.createElement("div");
    body.className = "card-body";

    const h = document.createElement("h2");
    h.className = "h5 card-title";
    h.textContent = title;

    const p = document.createElement("p");
    p.className = "card-text text-muted mb-0";
    p.textContent = text;

    body.appendChild(h);
    body.appendChild(p);
    card.appendChild(body);
    col.appendChild(card);
    return col;
}

// Start: check login + build navbar, then fill the page
setupPage().then(function (user) {
    document.getElementById("welcome").textContent = "Welcome, " + user.name;

    const isAssistant = user.role === "assistant";
    document.getElementById("subtitle").textContent = isAssistant
        ? "Lab Assistant dashboard – manage faults, equipment and the schedule."
        : "Student dashboard – book equipment and report faults.";

    const cards = isAssistant ? ASSISTANT_CARDS : STUDENT_CARDS;
    const container = document.getElementById("cards");
    cards.forEach(function (c) {
        container.appendChild(makeCard(c[0], c[1], c[2]));
    });
});