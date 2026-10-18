import os
from flask import Flask, jsonify, send_from_directory

# Find the frontend folder (it is next to the backend folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")


def create_app():
    # static_folder tells Flask where the frontend files (HTML, CSS, JS) are
    app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

    # A secret key is needed later for login sessions
    app.config["SECRET_KEY"] = "dev-secret-change-later"

    # ---------- API ----------
    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "message": "LabBook backend is running"})

    # ---------- Frontend ----------
    # When someone opens the main address, send them index.html
    @app.get("/")
    def home():
        return send_from_directory(FRONTEND_DIR, "index.html")

    return app


# This part runs only when we start the file with: python app.py
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)