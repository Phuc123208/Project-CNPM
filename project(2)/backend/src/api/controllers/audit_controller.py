from flask import Blueprint, request
from api.responses import success_response
from api.middleware import jwt_required, roles_required
from services.audit_service import AuditService
from domain.constants import Roles

audit_bp = Blueprint("audit", __name__, url_prefix="/api/audit")
audit_service = AuditService()


@audit_bp.route("", methods=["GET"])
@jwt_required
@roles_required(Roles.ADMIN)
def list_logs():
    limit = int(request.args.get("limit", 200))
    logs = audit_service.list_logs(limit=limit)
    return success_response([{
        "log_id": l.log_id, "user_id": l.user_id, "action": l.action,
        "resource_type": l.resource_type, "resource_id": l.resource_id,
        "details": l.details, "created_at": str(l.created_at),
    } for l in logs])
