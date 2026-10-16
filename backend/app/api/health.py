from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    # Liveness only: database readiness will be added with the persistence module.
    return jsonify(status="ok", service="dynamic-report-template")
