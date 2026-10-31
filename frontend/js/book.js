// Which equipment? It comes from the address, e.g. book.html?id=3
const equipmentId = Number(new URLSearchParams(window.location.search).get("id"));
let chosenSlot = null;      // the slot the student clicked (e.g. 10)

// Today's date as "YYYY-MM-DD" in local time
function todayText() {
    const d = new Date();
    const month = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return d.getFullYear() + "-" + month + "-" + day;
}

// Load the slots for the chosen date and draw them as buttons
async function loadSlots() {
    const dateValue = document.getElementById("date").value;
    const box = document.getElementById("slots");
    chosenSlot = null;
    box.textContent = "Loading...";

    try {
        const data = await api("GET", "/api/equipment/" + equipmentId + "/slots?date=" + dateValue);

        document.getElementById("item-name").textContent = data.equipment.name;
        document.getElementById("item-info").textContent = data.equipment.code + " · " + data.equipment.lab;

        box.textContent = "";
        data.slots.forEach(function (s) {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.textContent = s.label;
            btn.dataset.slot = s.slot;

            if (s.state === "free") {
                btn.className = "btn btn-outline-primary slot-btn";
                btn.addEventListener("click", function () { chooseSlot(s.slot); });
            } else {
                btn.className = "btn btn-secondary slot-btn";
                btn.disabled = true;
                btn.title = s.state === "booked" ? "Already booked" : "Time has passed";
            }
            box.appendChild(btn);
        });
    } catch (error) {
        box.textContent = "";
        showMessage(error.message, "danger");
    }
}

// Highlight the clicked slot
function chooseSlot(slot) {
    chosenSlot = slot;
    document.querySelectorAll(".slot-btn").forEach(function (btn) {
        if (btn.disabled) return;
        btn.className = Number(btn.dataset.slot) === slot
            ? "btn btn-primary slot-btn"
            : "btn btn-outline-primary slot-btn";
    });
}

// Send the booking to the backend
document.getElementById("booking-form").addEventListener("submit", async function (event) {
    event.preventDefault();

    if (chosenSlot === null) {
        showMessage("Please choose a time slot", "danger");
        return;
    }

    try {
        const data = await api("POST", "/api/bookings", {
            equipment_id: equipmentId,
            date: document.getElementById("date").value,
            slot: chosenSlot,
            purpose: document.getElementById("purpose").value,
        });
        showMessage(data.message + ". You can see it in My bookings.", "success");
        document.getElementById("purpose").value = "";
        loadSlots();           // refresh: the slot now shows as booked
    } catch (error) {
        showMessage(error.message, "danger");
    }
});

// Start
setupPage("student").then(function () {
    if (!equipmentId) {
        window.location.href = "equipment.html";
        return;
    }
    const dateInput = document.getElementById("date");
    dateInput.value = todayText();
    dateInput.min = todayText();                       // the calendar won't allow past dates
    dateInput.addEventListener("change", loadSlots);
    loadSlots();
});