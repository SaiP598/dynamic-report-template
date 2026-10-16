"""Flask application factory for the report builder API."""
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from .extensions import db, migrate


def create_app(test_config=None):
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    app = Flask(__name__)
    app.config.from_mapping(
        MAX_CONTENT_LENGTH=256 * 1024,
        DATABASE_URL=os.getenv("DATABASE_URL"),
    )
    if test_config:
        app.config.update(test_config)

    app.config["SQLALCHEMY_DATABASE_URI"] = app.config["DATABASE_URL"] or (
        "postgresql+psycopg://report_builder:local_dev_only@localhost:5432/report_builder"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    engine_options = app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", {})
    engine_options.setdefault("pool_pre_ping", True)
    engine_options.setdefault("connect_args", {}).setdefault("connect_timeout", 5)
    db.init_app(app)
    from . import models  # noqa: F401 - register migration metadata
    migrate.init_app(app, db, directory=str(Path(__file__).resolve().parents[1] / "migrations"))

    from .api.health import health_bp
    app.register_blueprint(health_bp, url_prefix="/api")

    from .api.templates import templates_bp
    app.register_blueprint(templates_bp, url_prefix="/api")

    from .api.reports import reports_bp
    app.register_blueprint(reports_bp, url_prefix="/api")

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify(error={"code": error.name, "message": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unhandled API error")
        return jsonify(error={"code": "internal_error", "message": "An unexpected error occurred."}), 500

    return app
