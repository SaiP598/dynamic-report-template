"""REST endpoints for complete saved layouts; text is treated as plain text."""
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from ..data.defaults import get_default_configuration
from ..extensions import db
from ..services.templates import load_current, save_configuration
from ..validation.template import ConfigurationError, validate_configuration

templates_bp = Blueprint("templates", __name__)


@templates_bp.errorhandler(ConfigurationError)
def invalid_configuration(error):
    return jsonify(error={"code": "validation_error", "message": str(error)}), 400


@templates_bp.errorhandler(SQLAlchemyError)
def database_error(error):
    db.session.rollback()
    # Avoid serializing database exceptions: they can contain connection details or payloads.
    return jsonify(error={"code": "database_unavailable",
                          "message": "Template storage is unavailable. Please try again."}), 503


@templates_bp.get("/templates/default")
def default_template():
    return jsonify(configuration=get_default_configuration(), revision=0,
                   updatedAt=None, isDefault=True)


@templates_bp.get("/templates/current")
def current_template():
    return jsonify(load_current())


@templates_bp.put("/templates/current")
def update_template():
    configuration = validate_configuration(request.get_json())
    return jsonify(save_configuration(configuration))


@templates_bp.post("/templates/current/restore")
def restore_template():
    if request.get_data():
        raise ConfigurationError("Restore does not accept a request body.")
    return jsonify(save_configuration(get_default_configuration()))
