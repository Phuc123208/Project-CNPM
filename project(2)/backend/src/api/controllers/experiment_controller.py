from flask import Blueprint, request, g
from api.responses import success_response, error_response
from api.middleware import jwt_required, roles_required
from api.schemas.experiment_schema import CreateExperimentRequestSchema, ExperimentResponseSchema
from services.experiment_service import ExperimentService
from services.audit_service import AuditService
from domain.exceptions import CustomException
from domain.constants import Roles

experiment_bp = Blueprint("experiment", __name__, url_prefix="/api/experiments")

experiment_service = ExperimentService()
audit_service = AuditService()
exp_schema = ExperimentResponseSchema()
exps_schema = ExperimentResponseSchema(many=True)

CAN_MANAGE = (Roles.ADMIN, Roles.RESEARCHER, Roles.ANALYST)


@experiment_bp.route("", methods=["GET"])
@jwt_required
def list_experiments():
    mine = request.args.get("mine") == "true"
    version_id = request.args.get("version_id", type=int)
    user_id = g.current_user["user_id"] if mine else None
    exps = experiment_service.list_experiments(user_id=user_id, version_id=version_id)
    return success_response(exps_schema.dump(exps))


@experiment_bp.route("", methods=["POST"])
@jwt_required
@roles_required(*CAN_MANAGE)
def create_experiment():
    """Module 5: create a reproducible experiment configuration
    (dataset version + model type + hyperparameters)."""
    data = request.get_json(force=True, silent=True) or {}
    errors = CreateExperimentRequestSchema().validate(data)
    if errors:
        return error_response(errors, 422)
    try:
        exp = experiment_service.create_experiment(
            g.current_user["user_id"], data["version_id"], data["name"],
            data["model_type"], data.get("parameters", {}))
        audit_service.log(g.current_user["user_id"], "create_experiment", "experiment", exp.experiment_id)
        return success_response(exp_schema.dump(exp), "Experiment created", 201)
    except CustomException as e:
        return error_response(str(e), 400)


@experiment_bp.route("/<int:experiment_id>", methods=["GET"])
@jwt_required
def get_experiment(experiment_id):
    try:
        exp = experiment_service.get_experiment(experiment_id)
        return success_response(exp_schema.dump(exp))
    except CustomException as e:
        return error_response(str(e), 404)


@experiment_bp.route("/<int:experiment_id>/run", methods=["POST"])
@jwt_required
@roles_required(*CAN_MANAGE)
def run_experiment(experiment_id):
    """Module 3: run ARIMA/Prophet forecasting for the given segment,
    persist forecast_results and evaluation_metrics."""
    data = request.get_json(force=True, silent=True) or {}
    segment_id = data.get("segment_id")
    horizon = int(data.get("horizon", 4))
    test_size = int(data.get("test_size", 4))
    if not segment_id:
        return error_response("segment_id is required", 422)
    try:
        result = experiment_service.run_experiment(experiment_id, segment_id, horizon, test_size)
        audit_service.log(g.current_user["user_id"], "run_forecast", "experiment", experiment_id,
                           {"segment_id": segment_id, "metrics": result.get("metrics")})
        return success_response(result, "Forecast generated")
    except CustomException as e:
        return error_response(str(e), 400)


@experiment_bp.route("/<int:experiment_id>/results", methods=["GET"])
@jwt_required
def get_results(experiment_id):
    try:
        results = experiment_service.get_forecast_results(experiment_id)
        return success_response([{
            "result_id": r.result_id, "segment_id": r.segment_id,
            "forecast_time": str(r.forecast_time), "predicted_density": r.predicted_density,
            "lower_bound": r.lower_bound, "upper_bound": r.upper_bound,
        } for r in results])
    except CustomException as e:
        return error_response(str(e), 404)


@experiment_bp.route("/compare", methods=["GET"])
@jwt_required
def compare_experiments():
    ids = request.args.get("ids", "")
    id_list = [int(i) for i in ids.split(",") if i.strip().isdigit()]
    if not id_list:
        return error_response("Provide ?ids=1,2,3", 422)
    return success_response(experiment_service.compare_experiments(id_list))
