from flask import Blueprint, request, g, send_from_directory, current_app
from api.responses import success_response, error_response
from api.middleware import jwt_required, roles_required
from services.report_service import ReportService
from services.audit_service import AuditService
from domain.exceptions import CustomException
from domain.constants import Roles

report_bp = Blueprint("report", __name__, url_prefix="/api/reports")

audit_service = AuditService()
CAN_MANAGE = (Roles.ADMIN, Roles.RESEARCHER, Roles.ANALYST)


def _service():
    return ReportService(report_folder=current_app.config["REPORT_FOLDER"])


@report_bp.route("/traffic/<int:version_id>", methods=["POST"])
@jwt_required
@roles_required(*CAN_MANAGE)
def generate_traffic_report(version_id):
    fmt = (request.get_json(silent=True) or {}).get("format", "pdf")
    try:
        report = _service().generate_traffic_report(g.current_user["user_id"], version_id, fmt)
        audit_service.log(g.current_user["user_id"], "generate_report", "report", report.report_id)
        return success_response({
            "report_id": report.report_id, "report_name": report.report_name,
            "format": report.format, "download_url": f"/api/reports/download/{report.report_id}",
        }, "Report generated", 201)
    except CustomException as e:
        return error_response(str(e), 400)


@report_bp.route("/forecast/<int:experiment_id>", methods=["POST"])
@jwt_required
@roles_required(*CAN_MANAGE)
def generate_forecast_report(experiment_id):
    fmt = (request.get_json(silent=True) or {}).get("format", "pdf")
    try:
        report = _service().generate_forecast_report(g.current_user["user_id"], experiment_id, fmt)
        audit_service.log(g.current_user["user_id"], "generate_report", "report", report.report_id)
        return success_response({
            "report_id": report.report_id, "report_name": report.report_name,
            "format": report.format, "download_url": f"/api/reports/download/{report.report_id}",
        }, "Report generated", 201)
    except CustomException as e:
        return error_response(str(e), 400)


@report_bp.route("", methods=["GET"])
@jwt_required
def list_reports():
    mine = request.args.get("mine") == "true"
    user_id = g.current_user["user_id"] if mine else None
    reports = _service().list_reports(user_id=user_id)
    return success_response([{
        "report_id": r.report_id, "report_name": r.report_name, "format": r.format,
        "created_at": str(r.created_at), "download_url": f"/api/reports/download/{r.report_id}",
    } for r in reports])


@report_bp.route("/download/<int:report_id>", methods=["GET"])
@jwt_required
def download_report(report_id):
    try:
        report = _service().get_report(report_id)
        return send_from_directory(current_app.config["REPORT_FOLDER"], report.file_url, as_attachment=True)
    except CustomException as e:
        return error_response(str(e), 404)
