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

    if app.config["DB_INIT_ON_STARTUP"]:
        try:
            from infrastructure.databases import init_db
            init_db(app, seed=app.config["DB_SEED_ON_INIT"])
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
        from sqlalchemy import text
        from infrastructure.databases.session import engine

        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except Exception as e:
            app.logger.warning("Database health check failed: %s", e)
            return jsonify({"status": "error", "database": "unavailable"}), 503

        return jsonify({"status": "ok", "database": "ok"})

    return app
