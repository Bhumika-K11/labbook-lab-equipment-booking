"""
Automated API tests for LabBook.

How to run (from the backend folder, with the venv active):
    pip install pytest
    python -m pytest -v

Each test uses its own temporary database, so the real lab.db is never changed.
"""
import os
import sys
from datetime import date, timedelta

import pytest
from werkzeug.security import generate_password_hash

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app          # noqa: E402
from db import get_db, init_db      # noqa: E402


# ---------------------------------------------------------------- test setup

@pytest.fixture
def app(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    with app.app_context():
        init_db()
        db = get_db()
        users = [("Aarav Mehta", "student1@example.edu", "student123", "student"),
                 ("Diya Sharma", "student2@example.edu", "student123", "student"),
                 ("Ravi Kumar", "assistant@example.edu", "assistant123", "assistant")]
        for name, email, pw, role in users:
            db.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?,?,?,?)",
                       (name, email, generate_password_hash(pw), role))
        items = [("EL-OSC-01", "Digital Storage Oscilloscope", "Electronics Lab", "Available"),   # id 1
                 ("EL-FG-01", "Function Generator", "Electronics Lab", "Available"),             # id 2
                 ("EL-PS-01", "Dual DC Power Supply", "Electronics Lab", "Under Repair"),        # id 3
                 ("NW-SW-01", "Network Switch", "Networking Lab", "Available")]                  # id 4
        for row in items:
            db.execute("INSERT INTO equipment (code, name, lab, status) VALUES (?,?,?,?)", row)
        db.commit()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def login(client, email="student1@example.edu", password="student123"):
    return client.post("/api/login", json={"email": email, "password": password})


def tomorrow():
    return (date.today() + timedelta(days=1)).isoformat()


def book(client, equipment_id=1, day=None, slot=10, purpose="Lab experiment 3"):
    return client.post("/api/bookings", json={"equipment_id": equipment_id, "date": day or tomorrow(),
                                              "slot": slot, "purpose": purpose})


# ---------------------------------------------------------------- FR-01 login

def test_tc01_login_with_correct_details(client):
    r = login(client)
    assert r.status_code == 200
    assert r.get_json()["user"]["role"] == "student"


def test_tc02_login_with_wrong_password(client):
    r = login(client, password="wrongpass")
    assert r.status_code == 401
    assert r.get_json()["error"] == "Invalid email or password"


def test_tc03_login_with_empty_fields(client):
    r = client.post("/api/login", json={"email": "", "password": ""})
    assert r.status_code == 400


def test_tc04_login_email_is_not_case_sensitive(client):
    r = login(client, email="  STUDENT1@example.edu ")
    assert r.status_code == 200


def test_tc05_password_is_stored_hashed(app):
    with app.app_context():
        row = get_db().execute("SELECT password_hash FROM users WHERE email='student1@example.edu'").fetchone()
    assert row["password_hash"] != "student123"


# ---------------------------------------------------------------- FR-02 access control

def test_tc06_api_needs_login(client):
    assert client.get("/api/equipment").status_code == 401


def test_tc07_assistant_cannot_make_student_booking(client):
    login(client, "assistant@example.edu", "assistant123")
    assert book(client).status_code == 403


# ---------------------------------------------------------------- FR-03 equipment list

def test_tc08_equipment_list_and_lab_filter(client):
    login(client)
    all_items = client.get("/api/equipment").get_json()["equipment"]
    assert len(all_items) == 4
    net = client.get("/api/equipment?lab=Networking Lab").get_json()["equipment"]
    assert [e["code"] for e in net] == ["NW-SW-01"]


# ---------------------------------------------------------------- FR-04 / FR-05 booking

def test_tc09_book_a_free_slot(client):
    login(client)
    r = book(client)
    assert r.status_code == 201
    slots = client.get(f"/api/equipment/1/slots?date={tomorrow()}").get_json()["slots"]
    assert [s for s in slots if s["slot"] == 10][0]["state"] == "booked"


def test_tc10_double_booking_by_another_student_is_blocked(client):
    login(client)
    book(client)
    client.post("/api/logout")
    login(client, "student2@example.edu")
    assert book(client).status_code == 409


def test_tc11_same_student_two_items_same_slot_is_blocked(client):
    login(client)
    book(client, equipment_id=1)
    assert book(client, equipment_id=2).status_code == 409


def test_tc12_past_date_is_rejected(client):
    login(client)
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    assert book(client, day=yesterday).status_code == 400


def test_tc13_booking_window_boundary_14_and_15_days(client):
    login(client)
    d14 = (date.today() + timedelta(days=14)).isoformat()
    d15 = (date.today() + timedelta(days=15)).isoformat()
    assert book(client, day=d14).status_code == 201
    assert book(client, day=d15).status_code == 400


def test_tc14_slot_boundaries(client):
    login(client)
    assert book(client, slot=8).status_code == 400     # before 09:00
    assert book(client, slot=9).status_code == 201     # first slot
    assert book(client, slot=16, equipment_id=2).status_code == 201   # last slot
    assert book(client, slot=17).status_code == 400    # after 17:00


def test_tc15_purpose_too_short(client):
    login(client)
    r = book(client, purpose="abcd")                  # 4 characters, minimum is 5
    assert r.status_code == 400


def test_tc16_equipment_under_repair_cannot_be_booked(client):
    login(client)
    assert book(client, equipment_id=3).status_code == 409


def test_tc17_unknown_equipment_returns_404(client):
    login(client)
    assert book(client, equipment_id=999).status_code == 404


def test_tc18_cancel_own_booking_frees_the_slot(client):
    login(client)
    bid = book(client).get_json()["booking_id"]
    assert client.post(f"/api/bookings/{bid}/cancel").status_code == 200
    client.post("/api/logout")
    login(client, "student2@example.edu")
    assert book(client).status_code == 201             # slot is free again


def test_tc19_cannot_cancel_someone_elses_booking(client):
    login(client)
    bid = book(client).get_json()["booking_id"]
    client.post("/api/logout")
    login(client, "student2@example.edu")
    assert client.post(f"/api/bookings/{bid}/cancel").status_code == 404


def test_tc20_cannot_cancel_twice(client):
    login(client)
    bid = book(client).get_json()["booking_id"]
    client.post(f"/api/bookings/{bid}/cancel")
    assert client.post(f"/api/bookings/{bid}/cancel").status_code == 409


# ---------------------------------------------------------------- FR-06 fault reporting

def test_tc21_report_fault_marks_equipment_faulty(client):
    login(client)
    r = client.post("/api/faults", json={"equipment_id": 4, "severity": "High",
                                         "description": "Port 3 LED not lighting up"})
    assert r.status_code == 201
    items = client.get("/api/equipment").get_json()["equipment"]
    assert [e for e in items if e["id"] == 4][0]["status"] == "Faulty"
    assert book(client, equipment_id=4).status_code == 409


def test_tc22_fault_with_bad_severity_or_short_text(client):
    login(client)
    assert client.post("/api/faults", json={"equipment_id": 1, "severity": "Urgent",
                                            "description": "Screen flickers a lot"}).status_code == 400
    assert client.post("/api/faults", json={"equipment_id": 1, "severity": "Low",
                                            "description": "broken"}).status_code == 400


def test_tc23_my_faults_lists_own_reports(client):
    login(client)
    client.post("/api/faults", json={"equipment_id": 1, "severity": "Low",
                                     "description": "Channel 2 probe is loose"})
    faults = client.get("/api/faults/mine").get_json()["faults"]
    assert len(faults) == 1 and faults[0]["status"] == "Open"


# ---------------------------------------------------------------- edge cases

def test_tc24_equipment_id_true_is_not_accepted_as_a_number(client):
    """JSON true is not an equipment id. Python treats True as 1, so check it is rejected."""
    login(client)
    r = client.post("/api/bookings", json={"equipment_id": True, "date": tomorrow(),
                                           "slot": 10, "purpose": "Lab experiment 3"})
    assert r.status_code == 400


def test_tc25_very_long_purpose_is_rejected(client):
    """Purpose should have a sensible maximum length (e.g. 200 characters)."""
    login(client)
    assert book(client, purpose="x" * 5000).status_code == 400