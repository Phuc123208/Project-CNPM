"""Entry point for the Urban Traffic Analytics Platform API."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from app import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 9999))
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", True))
