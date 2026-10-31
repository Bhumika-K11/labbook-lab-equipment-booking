// Make one table cell with safe text (NFR-09)
function makeCell(text, className) {
    const td = document.createElement("td");
    td.textContent = text;
    if (className) td.className = className;
    return td;
}

// Load my bookings from the backend and draw the table
async function loadBookings() {
    const body = document.getElementById("bookings-body");

    try {
        const data = await api("GET", "/api/bookings/mine");
        body.innerHTML = "";

        if (data.bookings.length === 0) {
            const tr = document.createElement("tr");
            const td = makeCell("You have no bookings yet.", "text-center text-muted py-4");
            td.colSpan = 6;
            tr.appendChild(td);
            body.appendChild(tr);
            return;
        }

        data.bookings.forEach(function (b) {
            const tr = document.createElement("tr");
            tr.appendChild(makeCell(b.date));
            tr.appendChild(makeCell(b.slot_label));

            // Equipment name + lab (small grey text under it)
            const eqTd = makeCell(b.equipment);
            const lab = document.createElement("div");
            lab.className = "small text-muted";
            lab.textContent = b.lab;
            eqTd.appendChild(lab);
            tr.appendChild(eqTd);

            tr.appendChild(makeCell(b.purpose));

            // Status badge: green = Booked, grey = Cancelled
            const statusTd = document.createElement("td");
            const badge = document.createElement("span");
            badge.className = "badge " + (b.status === "Booked" ? "text-bg-success" : "text-bg-secondary");
            badge.textContent = b.status;
            statusTd.appendChild(badge);
            tr.appendChild(statusTd);

            // Cancel button (only for upcoming, active bookings)
            const actionTd = document.createElement("td");
            actionTd.className = "text-end";
            if (b.can_cancel) {
                const btn = document.createElement("button");
                btn.className = "btn btn-outline-danger btn-sm";
                btn.textContent = "Cancel";
                btn.addEventListener("click", function () { cancelBooking(b); });
                actionTd.appendChild(btn);
            } else {
                actionTd.appendChild(document.createTextNode("–"));
            }
            tr.appendChild(actionTd);

            body.appendChild(tr);
        });
    } catch (error) {
        showMessage(error.message, "danger");
    }
}

// Ask "Are you sure?" and then cancel
async function cancelBooking(b) {
    const sure = confirm("Cancel your booking of " + b.equipment + " on " + b.date + ", " + b.slot_label + "?");
    if (!sure) return;

    try {
        const data = await api("POST", "/api/bookings/" + b.id + "/cancel");
        showMessage(data.message, "success");
        loadBookings();          // refresh the table
    } catch (error) {
        showMessage(error.message, "danger");
    }
}

// Start
setupPage("student").then(loadBookings);