-- Delete old tables if they exist (so we can rebuild the database from scratch)
DROP TABLE IF EXISTS fault_reports;
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS equipment;
DROP TABLE IF EXISTS users;

-- 1. USERS: students and lab assistants
CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('student', 'assistant'))
);

-- 2. EQUIPMENT: items in the labs
CREATE TABLE equipment (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    code   TEXT NOT NULL UNIQUE,
    name   TEXT NOT NULL,
    lab    TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Available'
           CHECK (status IN ('Available', 'Faulty', 'Under Repair'))
);

-- 3. BOOKINGS: who booked which equipment, on which date and slot
CREATE TABLE bookings (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL REFERENCES users(id),
    equipment_id INTEGER NOT NULL REFERENCES equipment(id),
    booking_date TEXT    NOT NULL,
    slot         INTEGER NOT NULL CHECK (slot BETWEEN 9 AND 16),
    purpose      TEXT    NOT NULL,
    status       TEXT    NOT NULL DEFAULT 'Booked'
                 CHECK (status IN ('Booked', 'Cancelled'))
);

-- RULE: only ONE active booking for the same equipment, date and slot (stops double booking)
CREATE UNIQUE INDEX one_active_booking_per_slot
    ON bookings (equipment_id, booking_date, slot)
    WHERE status = 'Booked';

-- 4. FAULT_REPORTS: problems reported on equipment
CREATE TABLE fault_reports (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id    INTEGER NOT NULL REFERENCES equipment(id),
    reported_by     INTEGER NOT NULL REFERENCES users(id),
    description     TEXT    NOT NULL,
    severity        TEXT    NOT NULL CHECK (severity IN ('Low', 'Medium', 'High')),
    status          TEXT    NOT NULL DEFAULT 'Open'
                    CHECK (status IN ('Open', 'In Progress', 'Resolved')),
    resolution_note TEXT,
    created_at      TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);