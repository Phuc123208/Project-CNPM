"""Module 4 - aggregate dashboard endpoint used by the KPI cards on the
frontend (works for all four roles, scoped by what each is allowed to see)."""
from flask import Blueprint, request, g
from api.responses import success_response
from api.middleware import jwt_required
from infrastructure.repositories.dataset_repository import DatasetRepository
from infrastructure.repositories.experiment_repository import ExperimentRepository
from services.analysis_service import AnalysisService

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/summary", methods=["GET"])
@jwt_required
def summary():
    version_id = request.args.get("version_id", type=int)
    dataset_repo = DatasetRepository()
    experiment_repo = ExperimentRepository()

    datasets = dataset_repo.list_datasets()
    experiments = experiment_repo.list(user_id=None)
    data = {
        "total_datasets": len(datasets),
        "total_experiments": len(experiments),
        "completed_experiments": len([e for e in experiments if e.status == "completed"]),
        "role": g.current_user["role"],
    }
    if version_id:
        data["kpis"] = AnalysisService(dataset_repo).get_kpis(version_id)
    return success_response(data)
