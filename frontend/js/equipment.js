// All equipment loaded from the backend (kept here so the filter works without reloading)
let allEquipment = [];

// Bootstrap colour for each status
const STATUS_COLOURS = {
    "Available": "success",        // green
    "Faulty": "danger",            // red
    "Under Repair": "warning",     // yellow
};

// Make one table cell with safe text (textContent = no HTML injection, NFR-09)
function makeCell(text) {
    const td = document.createElement("td");
    td.textContent = text;
    return td;
}

// Draw the table rows for the chosen lab ("" = all labs)
function showTable(lab) {
    const body = document.getElementById("equipment-body");
    body.innerHTML = "";

    const items = lab ? allEquipment.filter(e => e.lab === lab) : allEquipment;

    if (items.length === 0) {
        const tr = document.createElement("tr");
        const td = makeCell("No equipment found.");
        td.colSpan = 5;
        td.className = "text-center text-muted py-4";
        tr.appendChild(td);
        body.appendChild(tr);
        return;
    }

    items.forEach(function (item) {
        const tr = document.createElement("tr");
        tr.appendChild(makeCell(item.code));
        tr.appendChild(makeCell(item.name));
        tr.appendChild(makeCell(item.lab));

        // Status as a coloured badge
        const statusTd = document.createElement("td");
        const badge = document.createElement("span");
        badge.className = "badge text-bg-" + (STATUS_COLOURS[item.status] || "secondary");
        badge.textContent = item.status;
        statusTd.appendChild(badge);
        tr.appendChild(statusTd);

        // Book button: only for Available items (FR-04)
        const actionTd = document.createElement("td");
        actionTd.className = "text-end";
        if (item.status === "Available") {
            const btn = document.createElement("a");
            btn.className = "btn btn-primary btn-sm";
            btn.href = "book.html?id=" + item.id;      // the booking page (we build it next)
            btn.textContent = "Book";
            actionTd.appendChild(btn);
        } else {
            const btn = document.createElement("button");
            btn.className = "btn btn-outline-secondary btn-sm";
            btn.disabled = true;
            btn.textContent = "Not available";
            actionTd.appendChild(btn);
        }
        tr.appendChild(actionTd);

        body.appendChild(tr);
    });
}

// Fill the lab dropdown with each lab name (only once each)
function fillLabFilter() {
    const select = document.getElementById("lab-filter");
    const labs = [...new Set(allEquipment.map(e => e.lab))];
    labs.forEach(function (lab) {
        const option = document.createElement("option");
        option.value = lab;
        option.textContent = lab;
        select.appendChild(option);
    });

    // When the user picks a lab, redraw the table
    select.addEventListener("change", function () {
        showTable(select.value);
    });
}

// Start: check login + build navbar, then load the equipment
setupPage().then(async function () {
    try {
        const data = await api("GET", "/api/equipment");
        allEquipment = data.equipment;
        fillLabFilter();
        showTable("");
    } catch (error) {
        showMessage(error.message, "danger");
    }
});