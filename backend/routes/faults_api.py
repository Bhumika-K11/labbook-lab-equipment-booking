from flask import Blueprint, jsonify, request, session

from db import get_db
from routes.auth_api import role_required

faults_bp = Blueprint("faults", __name__)

SEVERITIES = ("Low", "Medium", "High")


# ---------- 1. Report a fault (students) ----------
@faults_bp.post("/api/faults")
@role_required("student")
def report_fault():
    data = request.get_json(silent=True) or {}
    equipment_id = data.get("equipment_id")
    severity = data.get("severity")
    description = (data.get("description") or "").strip()

    # Check every field first
    if not isinstance(equipment_id, int) or isinstance(equipment_id, bool):   # Issue #1
        return jsonify({"error": "Please choose the equipment"}), 400
    if severity not in SEVERITIES:
        return jsonify({"error": "Please choose a severity (Low, Medium or High)"}), 400
    if len(description) < 10:
        return jsonify({"error": "Please describe the problem (at least 10 characters)"}), 400
    if len(description) > 500:                       # Issue #2
        return jsonify({"error": "Description is too long (maximum 500 characters)"}), 400

    db = get_db()
    item = db.execute("SELECT * FROM equipment WHERE id = ?", (equipment_id,)).fetchone()
    if item is None:
        return jsonify({"error": "Equipment not found"}), 404

    # Save the report
    cur = db.execute(
        "INSERT INTO fault_reports (equipment_id, reported_by, description, severity) VALUES (?, ?, ?, ?)",
        (equipment_id, session["user_id"], description, severity),
    )

    # Mark the equipment as Faulty so nobody can book it until it is checked
    if item["status"] == "Available":
        db.execute("UPDATE equipment SET status = 'Faulty' WHERE id = ?", (equipment_id,))

    db.commit()
    return jsonify({
        "message": f"Fault reported for {item['name']}. The lab assistant will check it.",
        "fault_id": cur.lastrowid,
    }), 201


# ---------- 2. See the faults I reported (students) ----------
@faults_bp.get("/api/faults/mine")
@role_required("student")
def my_faults():
    rows = get_db().execute(
        """SELECT f.id, f.description, f.severity, f.status, f.resolution_note, f.created_at,
                  e.code, e.name
           FROM fault_reports f
           JOIN equipment e ON e.id = f.equipment_id
           WHERE f.reported_by = ?
           ORDER BY f.id DESC""",
        (session["user_id"],),
    ).fetchall()

    return jsonify({"faults": [
        {
            "id": r["id"],
            "equipment": f"{r['name']} ({r['code']})",
            "description": r["description"],
            "severity": r["severity"],
            "status": r["status"],
            "note": r["resolution_note"] or "",
            "reported_on": r["created_at"][:10],      # just the date part
        }
        for r in rows
    ]})