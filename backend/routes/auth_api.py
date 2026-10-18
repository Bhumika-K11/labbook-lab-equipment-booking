from functools import wraps

from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash

from db import get_db

# A Blueprint is a group of related APIs (here: everything about login)
auth_bp = Blueprint("auth", __name__)


def user_to_dict(row):
    """Turn a database row into simple data we can send as JSON (never send the password hash!)."""
    return {"id": row["id"], "name": row["name"], "email": row["email"], "role": row["role"]}


# ---------- Guards (used by other APIs later) ----------
def login_required(view):
    """Stop the request with 401 if nobody is logged in (FR-02)."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Please log in first"}), 401
        return view(*args, **kwargs)
    return wrapper


def role_required(role):
    """Stop the request with 403 if the user has the wrong role (NFR-02)."""
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(*args, **kwargs):
            if session.get("role") != role:
                return jsonify({"error": "You are not allowed to do this"}), 403
            return view(*args, **kwargs)
        return wrapper
    return decorator


# ---------- APIs ----------
@auth_bp.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    # TC-03: empty fields
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Find the user by email (the ? keeps it safe from SQL injection - NFR-09)
    user = get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    # TC-02: wrong email or wrong password -> same message (so attackers can't guess emails)
    if user is None or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    # TC-01: success -> remember the user in the session (a signed cookie)
    session.clear()
    session["user_id"] = user["id"]
    session["role"] = user["role"]
    return jsonify({"user": user_to_dict(user)})


@auth_bp.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})


@auth_bp.get("/api/me")
@login_required
def me():
    """Tell the frontend who is logged in (used on every page)."""
    user = get_db().execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    if user is None:
        session.clear()
        return jsonify({"error": "Please log in first"}), 401
    return jsonify({"user": user_to_dict(user)})