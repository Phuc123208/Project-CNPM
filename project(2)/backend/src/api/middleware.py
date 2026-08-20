"""JWT authentication + role-based authorization decorators."""
import jwt
from functools import wraps
from flask import request, jsonify, current_app, g


def _extract_token():
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1]
    return None


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_token()
        if not token:
            return jsonify({"success": False, "message": "Missing authorization token"}), 401
        try:
            payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401
        g.current_user = payload
        return f(*args, **kwargs)
    return decorated


def roles_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = getattr(g, "current_user", None)
            if not user:
                return jsonify({"success": False, "message": "Authentication required"}), 401
            if user.get("role") not in allowed_roles:
                return jsonify({"success": False, "message": "Forbidden: insufficient role"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


def setup_middleware(app):
    @app.after_request
    def add_headers(response):
        response.headers["X-Powered-By"] = "Urban-Traffic-Analytics-Platform"
        return response
