import sqlite3
from datetime import date, datetime, timedelta

from flask import Blueprint, jsonify, request, session

from db import get_db
from routes.auth_api import login_required, role_required

bookings_bp = Blueprint("bookings", __name__)

FIRST_SLOT = 9          # 09:00 - 10:00
LAST_SLOT = 16          # 16:00 - 17:00
MAX_DAYS_AHEAD = 14     # students can book up to 2 weeks ahead


def slot_label(slot):
    """9 -> '09:00 - 10:00'"""
    return f"{slot:02d}:00 - {slot + 1:02d}:00"


def parse_date(text):
    """Turn '2026-10-25' into a date. Returns None if the text is not a valid date."""
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def check_date(day):
    """Return an error message if the date cannot be booked, otherwise None."""
    if day is None:
        return "Please choose a valid date"
    if day < date.today():
        return "You cannot book a date in the past"
    if day > date.today() + timedelta(days=MAX_DAYS_AHEAD):
        return f"You can book at most {MAX_DAYS_AHEAD} days ahead"
    return None


# ---------- 1. See free and booked slots for one item on one day ----------
@bookings_bp.get("/api/equipment/<int:equipment_id>/slots")
@login_required
def equipment_slots(equipment_id):
    db = get_db()
    item = db.execute("SELECT * FROM equipment WHERE id = ?", (equipment_id,)).fetchone()
    if item is None:
        return jsonify({"error": "Equipment not found"}), 404

    day = parse_date(request.args.get("date"))
    error = check_date(day)
    if error:
        return jsonify({"error": error}), 400

    # Which slots are already taken on that day?
    rows = db.execute(
        "SELECT slot FROM bookings WHERE equipment_id = ? AND booking_date = ? AND status = 'Booked'",
        (equipment_id, day.isoformat()),
    ).fetchall()
    taken = {r["slot"] for r in rows}

    now_hour = datetime.now().hour
    slots = []
    for s in range(FIRST_SLOT, LAST_SLOT + 1):
        if s in taken:
            state = "booked"
        elif day == date.today() and s <= now_hour:
            state = "past"               # this hour has already started today
        else:
            state = "free"
        slots.append({"slot": s, "label": slot_label(s), "state": state})

    return jsonify({
        "equipment": {"id": item["id"], "code": item["code"], "name": item["name"],
                      "lab": item["lab"], "status": item["status"]},
        "date": day.isoformat(),
        "slots": slots,
    })


# ---------- 2. Make a booking (students only) ----------
@bookings_bp.post("/api/bookings")
@role_required("student")
def create_booking():
    data = request.get_json(silent=True) or {}
    equipment_id = data.get("equipment_id")
    slot = data.get("slot")
    purpose = (data.get("purpose") or "").strip()
    day = parse_date(data.get("date"))

    # Check every field before touching the database
    if not isinstance(equipment_id, int) or not isinstance(slot, int):
        return jsonify({"error": "Please choose equipment and a time slot"}), 400
    error = check_date(day)
    if error:
        return jsonify({"error": error}), 400
    if slot < FIRST_SLOT or slot > LAST_SLOT:
        return jsonify({"error": "Please choose a slot between 09:00 and 17:00"}), 400
    if day == date.today() and slot <= datetime.now().hour:
        return jsonify({"error": "This time slot has already started"}), 400
    if len(purpose) < 5:
        return jsonify({"error": "Please write the purpose (at least 5 characters)"}), 400

    db = get_db()
    item = db.execute("SELECT * FROM equipment WHERE id = ?", (equipment_id,)).fetchone()
    if item is None:
        return jsonify({"error": "Equipment not found"}), 404
    if item["status"] != "Available":
        return jsonify({"error": f"This equipment is {item['status']} and cannot be booked"}), 409

    # One person cannot be in two places at once: no second booking in the same slot
    clash = db.execute(
        "SELECT id FROM bookings WHERE user_id = ? AND booking_date = ? AND slot = ? AND status = 'Booked'",
        (session["user_id"], day.isoformat(), slot),
    ).fetchone()
    if clash:
        return jsonify({"error": "You already have another booking in this slot"}), 409

    # Save. The UNIQUE INDEX in schema.sql stops double booking even if two people click at once
    try:
        cur = db.execute(
            "INSERT INTO bookings (user_id, equipment_id, booking_date, slot, purpose) VALUES (?, ?, ?, ?, ?)",
            (session["user_id"], equipment_id, day.isoformat(), slot, purpose),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Sorry, someone has just booked this slot. Please choose another."}), 409

    return jsonify({
        "message": f"Booked {item['name']} on {day.isoformat()}, {slot_label(slot)}",
        "booking_id": cur.lastrowid,
    }), 201
    

# ---------- 3. See my own bookings (students) ----------
@bookings_bp.get("/api/bookings/mine")
@role_required("student")
def my_bookings():
    rows = get_db().execute(
        """SELECT b.id, b.booking_date, b.slot, b.purpose, b.status,
                  e.code, e.name, e.lab
           FROM bookings b
           JOIN equipment e ON e.id = b.equipment_id
           WHERE b.user_id = ?
           ORDER BY b.booking_date DESC, b.slot DESC""",
        (session["user_id"],),
    ).fetchall()

    today = date.today().isoformat()
    now_hour = datetime.now().hour
    result = []
    for r in rows:
        # A booking can be cancelled only if it is still active and has not started yet
        upcoming = r["booking_date"] > today or (r["booking_date"] == today and r["slot"] > now_hour)
        result.append({
            "id": r["id"],
            "date": r["booking_date"],
            "slot_label": slot_label(r["slot"]),
            "purpose": r["purpose"],
            "status": r["status"],
            "equipment": f"{r['name']} ({r['code']})",
            "lab": r["lab"],
            "can_cancel": r["status"] == "Booked" and upcoming,
        })
    return jsonify({"bookings": result})


# ---------- 4. Cancel one of my bookings (students) ----------
@bookings_bp.post("/api/bookings/<int:booking_id>/cancel")
@role_required("student")
def cancel_booking(booking_id):
    db = get_db()
    b = db.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()

    # Students can only cancel their OWN bookings
    if b is None or b["user_id"] != session["user_id"]:
        return jsonify({"error": "Booking not found"}), 404
    if b["status"] != "Booked":
        return jsonify({"error": "This booking is already cancelled"}), 409

    today = date.today().isoformat()
    if b["booking_date"] < today or (b["booking_date"] == today and b["slot"] <= datetime.now().hour):
        return jsonify({"error": "You cannot cancel a booking that has already started"}), 409

    db.execute("UPDATE bookings SET status = 'Cancelled' WHERE id = ?", (booking_id,))
    db.commit()
    return jsonify({"message": "Booking cancelled. The slot is free again."})