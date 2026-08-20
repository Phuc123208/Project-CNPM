import os
from flask import Flask, jsonify
from config import ActiveConfig
from cors import init_cors
from error_handler import register_error_handlers
from api.middleware import setup_middleware
from api.routes import register_routes


def create_app():
    app = Flask(__name__)
    app.config.from_object(ActiveConfig)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["REPORT_FOLDER"], exist_ok=True)

    init_cors(app)
    setup_middleware(app)
    register_error_handlers(app)
    register_routes(app)

    # Initialize DB (create tables in Supabase Postgres + seed demo accounts)
    try:
        from infrastructure.databases import init_db
        init_db(app)
        print("[app] Database initialized successfully.")
    except Exception as e:
        print(f"[app] WARNING: could not initialize database: {e}")

    @app.route("/")
    def index():
        return jsonify({
            "service": "Urban Traffic Analytics Platform API",
            "status": "running",
            "docs": "See README.md for the full endpoint list",
        })

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app
