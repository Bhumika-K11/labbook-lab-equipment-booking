import os
import sqlite3
from flask import g, current_app

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_db():
    """Open a connection to the database (once per request) and return it."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row             # lets us read columns by name, e.g. row["email"]
        g.db.execute("PRAGMA foreign_keys = ON")   # make SQLite check the REFERENCES links
    return g.db


def close_db(error=None):
    """Close the database connection at the end of each request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create all tables by running schema.sql (deletes old data!)."""
    db = get_db()
    schema_path = os.path.join(BASE_DIR, "schema.sql")
    with open(schema_path, encoding="utf-8") as f:
        db.executescript(f.read())
    db.commit()


def init_app(app):
    """Tell Flask to close the database automatically after every request."""
    app.teardown_appcontext(close_db)