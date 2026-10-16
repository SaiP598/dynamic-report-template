"""Flask application factory for the report builder API."""
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException


def create_app(test_config=None):
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    app = Flask(__name__)
    app.config.from_mapping(
        MAX_CONTENT_LENGTH=256 * 1024,
        DATABASE_URL=os.getenv("DATABASE_URL"),
    )
    if test_config:
        app.config.update(test_config)

    from .api.health import health_bp
    app.register_blueprint(health_bp, url_prefix="/api")

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify(error={"code": error.name, "message": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unhandled API error")
        return jsonify(error={"code": "internal_error", "message": "An unexpected error occurred."}), 500

    return app
