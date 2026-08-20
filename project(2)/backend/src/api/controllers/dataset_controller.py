from flask import Blueprint, request, g, current_app
from api.responses import success_response, error_response
from api.middleware import jwt_required, roles_required
from api.schemas.dataset_schema import DatasetResponseSchema, DatasetVersionResponseSchema
from services.dataset_service import DatasetService
from services.audit_service import AuditService
from domain.exceptions import CustomException
from domain.constants import Roles

dataset_bp = Blueprint("dataset", __name__, url_prefix="/api/datasets")

audit_service = AuditService()
dataset_schema = DatasetResponseSchema()
datasets_schema = DatasetResponseSchema(many=True)
version_schema = DatasetVersionResponseSchema()
versions_schema = DatasetVersionResponseSchema(many=True)


def _service():
    return DatasetService(upload_folder=current_app.config["UPLOAD_FOLDER"])


# Researcher & Admin can manage datasets; Analyst & Student have read-only access
CAN_MANAGE = (Roles.ADMIN, Roles.RESEARCHER)


@dataset_bp.route("", methods=["GET"])
@jwt_required
def list_datasets():
    status = request.args.get("status")
    search = request.args.get("search")
    mine = request.args.get("mine") == "true"
    user_id = g.current_user["user_id"] if mine else None
    datasets = _service().list_datasets(user_id=user_id, status=status, search=search)
    return success_response(datasets_schema.dump(datasets))


@dataset_bp.route("", methods=["POST"])
@jwt_required
@roles_required(*CAN_MANAGE)
def upload_dataset():
    """Upload a new dataset (CSV of UAV vehicle trajectories) -> creates
    Dataset + first DatasetVersion + runs schema/data-quality validation."""
    name = request.form.get("name")
    description = request.form.get("description")
    file_storage = request.files.get("file")
    if not name:
        return error_response("Field 'name' is required", 422)
    try:
        dataset, version, report = _service().create_dataset_with_file(
            g.current_user["user_id"], name, description, file_storage)
        audit_service.log(g.current_user["user_id"], "upload_dataset", "dataset", dataset.dataset_id,
                           {"version": version.version_number, "rows": version.row_count})
        return success_response({
            "dataset": dataset_schema.dump(dataset),
            "version": version_schema.dump(version),
            "validation_report": report,
        }, "Dataset uploaded", 201)
    except CustomException as e:
        return error_response(str(e), 400)


@dataset_bp.route("/<int:dataset_id>", methods=["GET"])
@jwt_required
def get_dataset(dataset_id):
    try:
        ds = _service().get_dataset(dataset_id)
        return success_response(dataset_schema.dump(ds))
    except CustomException as e:
        return error_response(str(e), 404)


@dataset_bp.route("/<int:dataset_id>/versions", methods=["GET"])
@jwt_required
def list_versions(dataset_id):
    try:
        versions = _service().list_versions(dataset_id)
        return success_response(versions_schema.dump(versions))
    except CustomException as e:
        return error_response(str(e), 404)


@dataset_bp.route("/<int:dataset_id>/versions", methods=["POST"])
@jwt_required
@roles_required(*CAN_MANAGE)
def upload_new_version(dataset_id):
    file_storage = request.files.get("file")
    try:
        version, report = _service().upload_new_version(dataset_id, file_storage)
        audit_service.log(g.current_user["user_id"], "upload_dataset_version", "dataset", dataset_id,
                           {"version": version.version_number})
        return success_response({"version": version_schema.dump(version), "validation_report": report},
                                 "New version uploaded", 201)
    except CustomException as e:
        return error_response(str(e), 400)


@dataset_bp.route("/versions/<int:version_id>/preview", methods=["GET"])
@jwt_required
def preview_version(version_id):
    limit = int(request.args.get("limit", 50))
    try:
        data = _service().preview_version(version_id, limit=limit)
        return success_response(data)
    except CustomException as e:
        return error_response(str(e), 404)


@dataset_bp.route("/versions/<int:version_id>/validate", methods=["POST"])
@jwt_required
@roles_required(*CAN_MANAGE)
def validate_version(version_id):
    try:
        report = _service().validate_version(version_id)
        audit_service.log(g.current_user["user_id"], "validate_dataset", "dataset_version", version_id, report)
        return success_response(report, "Validation completed")
    except CustomException as e:
        return error_response(str(e), 404)


@dataset_bp.route("/<int:dataset_id>/archive", methods=["POST"])
@jwt_required
@roles_required(*CAN_MANAGE)
def archive_dataset(dataset_id):
    try:
        ds = _service().archive_dataset(dataset_id)
        audit_service.log(g.current_user["user_id"], "archive_dataset", "dataset", dataset_id)
        return success_response(dataset_schema.dump(ds), "Dataset archived")
    except CustomException as e:
        return error_response(str(e), 404)


@dataset_bp.route("/<int:dataset_id>/restore", methods=["POST"])
@jwt_required
@roles_required(*CAN_MANAGE)
def restore_dataset(dataset_id):
    try:
        ds = _service().restore_dataset(dataset_id)
        audit_service.log(g.current_user["user_id"], "restore_dataset", "dataset", dataset_id)
        return success_response(dataset_schema.dump(ds), "Dataset restored")
    except CustomException as e:
        return error_response(str(e), 404)


@dataset_bp.route("/<int:dataset_id>", methods=["DELETE"])
@jwt_required
@roles_required(*CAN_MANAGE)
def delete_dataset(dataset_id):
    hard = request.args.get("hard") == "true"
    try:
        _service().delete_dataset(dataset_id, hard=hard)
        audit_service.log(g.current_user["user_id"], "delete_dataset", "dataset", dataset_id, {"hard": hard})
        return success_response(None, "Dataset deleted")
    except CustomException as e:
        return error_response(str(e), 404)
