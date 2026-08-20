from flask import Blueprint, request, g
from api.responses import success_response, error_response
from api.middleware import jwt_required, roles_required
from api.schemas.user_schema import UserResponseSchema, CreateUserRequestSchema
from services.user_service import UserService
from services.audit_service import AuditService
from domain.exceptions import CustomException
from domain.constants import Roles

user_bp = Blueprint("user", __name__, url_prefix="/api/users")

user_service = UserService()
audit_service = AuditService()
user_schema = UserResponseSchema()
users_schema = UserResponseSchema(many=True)


@user_bp.route("", methods=["GET"])
@jwt_required
@roles_required(Roles.ADMIN)
def list_users():
    role = request.args.get("role")
    users = user_service.list_users(role)
    return success_response(users_schema.dump(users))


@user_bp.route("", methods=["POST"])
@jwt_required
@roles_required(Roles.ADMIN)
def create_user():
    data = request.get_json(force=True, silent=True) or {}
    errors = CreateUserRequestSchema().validate(data)
    if errors:
        return error_response(errors, 422)
    try:
        user = user_service.create_user(data["full_name"], data["email"], data["password"], data["role"])
        audit_service.log(g.current_user["user_id"], "create_user", "user", user.user_id)
        return success_response(user_schema.dump(user), "User created", 201)
    except CustomException as e:
        return error_response(str(e), 400)


@user_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required
def get_user(user_id):
    # Admins can view anyone; others can only view themselves
    if g.current_user["role"] != Roles.ADMIN and g.current_user["user_id"] != user_id:
        return error_response("Forbidden", 403)
    try:
        user = user_service.get_profile(user_id)
        return success_response(user_schema.dump(user))
    except CustomException as e:
        return error_response(str(e), 404)


@user_bp.route("/<int:user_id>", methods=["PUT"])
@jwt_required
def update_user(user_id):
    if g.current_user["role"] != Roles.ADMIN and g.current_user["user_id"] != user_id:
        return error_response("Forbidden", 403)
    data = request.get_json(force=True, silent=True) or {}
    try:
        allowed_fields = {"full_name", "email"}
        if g.current_user["role"] == Roles.ADMIN:
            allowed_fields |= {"role", "password"}
        fields = {k: v for k, v in data.items() if k in allowed_fields}
        user = user_service.update_user(user_id, **fields)
        audit_service.log(g.current_user["user_id"], "update_user", "user", user_id, fields)
        return success_response(user_schema.dump(user), "User updated")
    except CustomException as e:
        return error_response(str(e), 404)


@user_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required
@roles_required(Roles.ADMIN)
def delete_user(user_id):
    try:
        user_service.delete_user(user_id)
        audit_service.log(g.current_user["user_id"], "delete_user", "user", user_id)
        return success_response(None, "User deleted")
    except CustomException as e:
        return error_response(str(e), 404)


@user_bp.route("/<int:user_id>/role", methods=["PATCH"])
@jwt_required
@roles_required(Roles.ADMIN)
def assign_role(user_id):
    data = request.get_json(force=True, silent=True) or {}
    role = data.get("role")
    if role not in Roles.ALL:
        return error_response("Invalid role", 422)
    try:
        user = user_service.assign_role(user_id, role)
        audit_service.log(g.current_user["user_id"], "assign_role", "user", user_id, {"role": role})
        return success_response(user_schema.dump(user), "Role updated")
    except CustomException as e:
        return error_response(str(e), 404)
