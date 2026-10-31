// Colours for the badges
const SEVERITY_COLOURS = { "Low": "secondary", "Medium": "warning", "High": "danger" };
const STATUS_COLOURS = { "Open": "danger", "In Progress": "warning", "Resolved": "success" };

function makeCell(text, className) {
    const td = document.createElement("td");
    td.textContent = text;
    if (className) td.className = className;
    return td;
}

function makeBadge(text, colour) {
    const span = document.createElement("span");
    span.className = "badge text-bg-" + (colour || "secondary");
    span.textContent = text;
    return span;
}

// Fill the equipment dropdown
async function loadEquipment() {
    const data = await api("GET", "/api/equipment");
    const select = document.getElementById("equipment");
    data.equipment.forEach(function (e) {
        const option = document.createElement("option");
        option.value = e.id;
        option.textContent = e.code + " – " + e.name + " (" + e.lab + ")";
        select.appendChild(option);
    });
}

// Show the faults this student has reported
async function loadMyFaults() {
    const body = document.getElementById("faults-body");
    const data = await api("GET", "/api/faults/mine");
    body.innerHTML = "";

    if (data.faults.length === 0) {
        const tr = document.createElement("tr");
        const td = makeCell("You have not reported any faults.", "text-center text-muted py-4");
        td.colSpan = 5;
        tr.appendChild(td);
        body.appendChild(tr);
        return;
    }

    data.faults.forEach(function (f) {
        const tr = document.createElement("tr");
        tr.appendChild(makeCell(f.reported_on));
        tr.appendChild(makeCell(f.equipment));

        // Problem + the assistant's note (if any) under it
        const problemTd = makeCell(f.description);
        if (f.note) {
            const note = document.createElement("div");
            note.className = "small text-success mt-1";
            note.textContent = "Lab note: " + f.note;
            problemTd.appendChild(note);
        }
        tr.appendChild(problemTd);

        const sevTd = document.createElement("td");
        sevTd.appendChild(makeBadge(f.severity, SEVERITY_COLOURS[f.severity]));
        tr.appendChild(sevTd);

        const statusTd = document.createElement("td");
        statusTd.appendChild(makeBadge(f.status, STATUS_COLOURS[f.status]));
        tr.appendChild(statusTd);

        body.appendChild(tr);
    });
}

// Submit the form
document.getElementById("fault-form").addEventListener("submit", async function (event) {
    event.preventDefault();

    const equipmentValue = document.getElementById("equipment").value;
    if (!equipmentValue) {
        showMessage("Please choose the equipment", "danger");
        return;
    }

    try {
        const data = await api("POST", "/api/faults", {
            equipment_id: Number(equipmentValue),
            severity: document.getElementById("severity").value,
            description: document.getElementById("description").value,
        });
        showMessage(data.message, "success");
        document.getElementById("fault-form").reset();      // clear the form
        loadMyFaults();
    } catch (error) {
        showMessage(error.message, "danger");
    }
});

// Start
setupPage("student").then(async function () {
    try {
        await loadEquipment();
        await loadMyFaults();
    } catch (error) {
        showMessage(error.message, "danger");
    }
});