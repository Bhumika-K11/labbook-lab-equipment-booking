from flask import Blueprint, jsonify, request

from db import get_db
from routes.auth_api import login_required

# All APIs about equipment live in this group
equipment_bp = Blueprint("equipment", __name__)


def equipment_to_dict(row):
    """Turn one database row into simple data we can send as JSON."""
    return {
        "id": row["id"],
        "code": row["code"],
        "name": row["name"],
        "lab": row["lab"],
        "status": row["status"],
    }


@equipment_bp.get("/api/equipment")
@login_required
def list_equipment():
    """Send the list of all equipment (FR-03). Optional filter: ?lab=Electronics Lab"""
    lab = request.args.get("lab")

    if lab:
        rows = get_db().execute(
            "SELECT * FROM equipment WHERE lab = ? ORDER BY lab, code", (lab,)
        ).fetchall()
    else:
        rows = get_db().execute("SELECT * FROM equipment ORDER BY lab, code").fetchall()

    return jsonify({"equipment": [equipment_to_dict(r) for r in rows]})