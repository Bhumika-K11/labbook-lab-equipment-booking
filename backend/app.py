import os
from flask import Flask, jsonify, send_from_directory

import db                                        # our database helper file (db.py)
from routes.auth_api import auth_bp              # the login APIs (routes/auth_api.py)
from routes.equipment_api import equipment_bp    # the equipment APIs (routes/equipment_api.py)

# Find the frontend folder (it is next to the backend folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")


def create_app(test_config=None):
    # static_folder tells Flask where the frontend files (HTML, CSS, JS) are
    app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

    # Settings
    app.config["SECRET_KEY"] = "dev-secret-change-later"          # used for login sessions
    app.config["DATABASE"] = os.path.join(BASE_DIR, "lab.db")     # the database file

    # Tests can replace the settings (e.g. use a temporary database)
    if test_config:
        app.config.update(test_config)

    # Connect the database helper to the app
    db.init_app(app)

    # Register the API groups
    app.register_blueprint(auth_bp)          # /api/login, /api/logout, /api/me
    app.register_blueprint(equipment_bp)     # /api/equipment

    # ---------- API ----------
    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "message": "LabBook backend is running"})

    # ---------- Frontend ----------
    @app.get("/")
    def home():
        return send_from_directory(FRONTEND_DIR, "index.html")

    return app


# This part runs only when we start the file with: python app.py
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)