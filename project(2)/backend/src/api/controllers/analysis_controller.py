from flask import Blueprint, request, g
from api.responses import success_response, error_response
from api.middleware import jwt_required, roles_required
from services.analysis_service import AnalysisService
from services.audit_service import AuditService
from domain.exceptions import CustomException
from domain.constants import Roles

analysis_bp = Blueprint("analysis", __name__, url_prefix="/api/analysis")

analysis_service = AnalysisService()
audit_service = AuditService()

CAN_MANAGE = (Roles.ADMIN, Roles.RESEARCHER, Roles.ANALYST)


@analysis_bp.route("/versions/<int:version_id>/compute", methods=["POST"])
@jwt_required
@roles_required(*CAN_MANAGE)
def compute_features(version_id):
    """Module 2: build the traffic-density time series (vehicle count, avg
    speed, density, peak-hour flag) from raw trajectories."""
    data = request.get_json(force=True, silent=True) or {}
    interval = int(data.get("interval_minutes", 15))
    try:
        result = analysis_service.compute_features(version_id, interval_minutes=interval)
        audit_service.log(g.current_user["user_id"], "compute_traffic_features",
                           "dataset_version", version_id, {"interval_minutes": interval})
        return success_response(result, "Traffic pattern analysis completed")
    except CustomException as e:
        return error_response(str(e), 400)


@analysis_bp.route("/versions/<int:version_id>/kpis", methods=["GET"])
@jwt_required
def kpis(version_id):
    return success_response(analysis_service.get_kpis(version_id))


@analysis_bp.route("/versions/<int:version_id>/trend", methods=["GET"])
@jwt_required
def trend(version_id):
    segment_id = request.args.get("segment_id")
    return success_response(analysis_service.get_trend(version_id, segment_id))


@analysis_bp.route("/versions/<int:version_id>/heatmap", methods=["GET"])
@jwt_required
def heatmap(version_id):
    return success_response(analysis_service.get_heatmap(version_id))


@analysis_bp.route("/versions/<int:version_id>/speed-distribution", methods=["GET"])
@jwt_required
def speed_distribution(version_id):
    return success_response(analysis_service.get_speed_distribution(version_id))


@analysis_bp.route("/versions/<int:version_id>/peak-hours", methods=["GET"])
@jwt_required
def peak_hours(version_id):
    return success_response(analysis_service.get_peak_hours(version_id))


@analysis_bp.route("/versions/<int:version_id>/hotspots", methods=["GET"])
@jwt_required
def hotspots(version_id):
    top_n = int(request.args.get("top_n", 5))
    return success_response(analysis_service.get_hotspots(version_id, top_n=top_n))
