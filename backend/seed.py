from werkzeug.security import generate_password_hash

from app import create_app
from db import get_db, init_db

# ---------- Fictional sample users (NOT real people) ----------
# (name, email, password, role)
USERS = [
    ("Aarav Mehta",  "student1@example.edu",  "student123",   "student"),
    ("Diya Sharma",  "student2@example.edu",  "student123",   "student"),
    ("Ravi Kumar",   "assistant@example.edu", "assistant123", "assistant"),
]

# ---------- Sample equipment (same as report Appendix B) ----------
# (code, name, lab, status)
EQUIPMENT = [
    ("EL-OSC-01", "Digital Storage Oscilloscope (100 MHz)", "Electronics Lab",      "Available"),
    ("EL-OSC-02", "Digital Storage Oscilloscope (100 MHz)", "Electronics Lab",      "Available"),
    ("EL-FG-01",  "Function Generator",                     "Electronics Lab",      "Available"),
    ("EL-PS-01",  "Dual DC Power Supply (0-30 V)",          "Electronics Lab",      "Under Repair"),
    ("ES-RPI-01", "Raspberry Pi 4 Kit",                     "Embedded Systems Lab", "Available"),
    ("ES-ARD-01", "Arduino Uno Starter Kit",                "Embedded Systems Lab", "Available"),
    ("NW-SW-01",  "24-port Managed Network Switch",         "Networking Lab",       "Available"),
    ("NW-RT-01",  "Wireless Router (test bench)",           "Networking Lab",       "Faulty"),
]


def seed():
    app = create_app()
    with app.app_context():
        init_db()          # create the tables (deletes old data)
        db = get_db()

        # Add users. The password is HASHED, never stored as plain text (NFR-01)
        for name, email, password, role in USERS:
            db.execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                (name, email, generate_password_hash(password), role),
            )

        # Add equipment
        for code, name, lab, status in EQUIPMENT:
            db.execute(
                "INSERT INTO equipment (code, name, lab, status) VALUES (?, ?, ?, ?)",
                (code, name, lab, status),
            )

        db.commit()        # save everything to the database file
        print(f"Database created: {len(USERS)} users and {len(EQUIPMENT)} equipment items added.")


if __name__ == "__main__":
    seed()