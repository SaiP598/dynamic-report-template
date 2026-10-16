"""Generate using server-side saved configuration only."""
from io import BytesIO
from flask import Blueprint, jsonify, request, send_file
from sqlalchemy.exc import SQLAlchemyError

from ..extensions import db
from ..services.templates import load_current
from ..services.reports import render_report

reports_bp = Blueprint("reports", __name__)


@reports_bp.post("/reports")
def generate_report():
    if request.get_data():
        return jsonify(error={"code": "validation_error", "message": "Report generation does not accept a request body. Save your template first."}), 400
    try:
        saved = load_current()
        pdf = render_report(saved["configuration"])
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify(error={"code": "database_unavailable", "message": "Template storage is unavailable. Please try again."}), 503
    response = send_file(BytesIO(pdf), mimetype="application/pdf", as_attachment=True,
                         download_name="dynamic-report.pdf", max_age=0)
    response.headers["X-Report-Layout"] = "format-only"
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Template-Revision"] = str(saved["revision"])
    return response
