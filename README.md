# LabBook – Laboratory Equipment Booking and Fault Reporting System

ELC3143 Software Engineering project by **Bhumika Khambait (2429010022)**, Manipal University Jaipur.

LabBook lets students book lab equipment (oscilloscopes, kits, switches…) in 1-hour slots and report faulty equipment. A faulty item is blocked from booking until it is checked. All users and data in this project are fictional sample data.

## Features (working)
| # | Workflow | Who |
|---|----------|-----|
| 1 | Log in / log out with role-based navigation | Student, Lab assistant |
| 2 | Browse equipment list, filter by lab | All logged-in users |
| 3 | See free / booked slots and book equipment (09:00–17:00, up to 14 days ahead) | Student |
| 4 | View my bookings and cancel an upcoming booking | Student |
| 5 | Report a fault (Low / Medium / High) – item becomes *Faulty* and cannot be booked | Student |

## Technology and dependencies
- **Backend:** Python 3 + Flask (REST API), Werkzeug password hashing
- **Database:** SQLite (file `backend/lab.db`)
- **Frontend:** HTML, CSS (Bootstrap 5), JavaScript (fetch API)
- **Testing:** pytest
- Exact Python packages are listed in `backend/requirements.txt`.

## Setup and run (Windows)
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python seed.py        # creates lab.db with sample users and equipment
python app.py         # starts the server
```
Open **http://127.0.0.1:5000** in the browser.

### Demo logins (fictional)
| Role | Email | Password |
|------|-------|----------|
| Student | student1@example.edu | student123 |
| Student | student2@example.edu | student123 |
| Lab assistant | assistant@example.edu | assistant123 |

## Running the tests
```bash
cd backend
venv\Scripts\activate
pip install pytest
python -m pytest -v
```
25 automated API tests in `backend/tests/test_api.py` cover login, access control, equipment list, booking rules (double booking, past dates, 14-day limit, slot boundaries), cancelling and fault reporting. Each test uses a temporary database, so `lab.db` is never changed.

- Test cycle 1: 23 passed, 2 failed → logged as Issues #1 and #2
- Fix applied → Test cycle 2: 25 passed (Issues #1 and #2 closed)

## Architecture overview
```
Browser (HTML + JS pages in /frontend)
      │  fetch() calls, JSON
      ▼
Flask app (backend/app.py)
      ├── routes/auth_api.py       /api/login, /api/logout, /api/me
      ├── routes/equipment_api.py  /api/equipment
      ├── routes/bookings_api.py   /api/equipment/<id>/slots, /api/bookings, cancel
      └── routes/faults_api.py     /api/faults, /api/faults/mine
      │
      ▼
SQLite database (schema.sql): users, equipment, bookings, fault_reports
```
- Login uses a signed session cookie; passwords are stored only as hashes.
- A unique index in the database prevents two active bookings for the same item, date and slot.
- All SQL uses `?` parameters (protects against SQL injection).

## Known limitations
- No lab-assistant page yet to resolve fault reports, so a reported item stays *Faulty* (Issue #3, planned for the next increment).
- The lab assistant cannot yet add or edit equipment from the website (done through `seed.py`).
- `SECRET_KEY` is a fixed development value in `app.py`; it must be changed before real deployment.
- Runs on Flask's development server only; not set up for production hosting.

## Version control and issue tracking
- Development history: see the commit list on GitHub.
- Bug/issue log: see the **Issues** tab (including closed issues).

## Declaration
Third-party libraries used: Flask, Werkzeug, Bootstrap 5, pytest.
AI assistance: an AI assistant (Claude) was used for step-by-step guidance and code suggestions during development and testing. All code was run, tested and checked by me, and I can explain how it works.