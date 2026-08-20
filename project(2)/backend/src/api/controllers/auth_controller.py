from flask import Blueprint, request, jsonify, current_app, g
from api.responses import success_response, error_response
from api.middleware import jwt_required
from api.schemas.auth_schema import RegisterRequestSchema, LoginRequestSchema, ChangePasswordRequestSchema
from api.schemas.user_schema import UserResponseSchema
from services.auth_service import AuthService
from services.audit_service import AuditService
from domain.exceptions import CustomException

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

auth_service = AuthService()
audit_service = AuditService()
user_schema = UserResponseSchema()


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new platform account (Admin, Researcher, Analyst, Student)."""
    data = request.get_json(force=True, silent=True) or {}
    errors = RegisterRequestSchema().validate(data)
    if errors:
        return error_response(errors, 422)
    try:
        user = auth_service.register(data.get("full_name"), data.get("email"),
                                      data.get("password"), data.get("role", "student"))
        audit_service.log(user.user_id, "register", "user", user.user_id)
        return success_response(user_schema.dump(user), "Registration successful", 201)
    except CustomException as e:
        return error_response(str(e), 400)


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login and receive a JWT access token."""
    data = request.get_json(force=True, silent=True) or {}
    errors = LoginRequestSchema().validate(data)
    if errors:
        return error_response(errors, 422)
    try:
        user = auth_service.login(data.get("email"), data.get("password"))
        token = AuthService.generate_token(user, current_app.config["SECRET_KEY"],
                                            current_app.config["JWT_EXPIRE_HOURS"])
        audit_service.log(user.user_id, "login", "user", user.user_id)
        return success_response({"token": token, "user": user_schema.dump(user)}, "Login successful")
    except CustomException as e:
        return error_response(str(e), 401)


@auth_bp.route("/me", methods=["GET"])
@jwt_required
def me():
    """Return the currently authenticated user's profile."""
    from services.user_service import UserService
    user = UserService().get_profile(g.current_user["user_id"])
    return success_response(user_schema.dump(user))


@auth_bp.route("/change-password", methods=["POST"])
@jwt_required
def change_password():
    data = request.get_json(force=True, silent=True) or {}
    errors = ChangePasswordRequestSchema().validate(data)
    if errors:
        return error_response(errors, 422)
    try:
        auth_service.change_password(g.current_user["user_id"], data["old_password"], data["new_password"])
        audit_service.log(g.current_user["user_id"], "change_password", "user", g.current_user["user_id"])
        return success_response(None, "Password changed successfully")
    except CustomException as e:
        return error_response(str(e), 400)
