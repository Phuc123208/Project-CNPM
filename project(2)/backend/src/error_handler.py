from flask import jsonify
from domain.exceptions import (
    CustomException, NotFoundException, ValidationException,
    UnauthorizedException, ConflictException, ForbiddenException,
)


def register_error_handlers(app):
    @app.errorhandler(NotFoundException)
    def handle_not_found(e):
        return jsonify({"success": False, "message": str(e)}), 404

    @app.errorhandler(ValidationException)
    def handle_validation(e):
        return jsonify({"success": False, "message": str(e)}), 422

    @app.errorhandler(UnauthorizedException)
    def handle_unauthorized(e):
        return jsonify({"success": False, "message": str(e)}), 401

    @app.errorhandler(ForbiddenException)
    def handle_forbidden(e):
        return jsonify({"success": False, "message": str(e)}), 403

    @app.errorhandler(ConflictException)
    def handle_conflict(e):
        return jsonify({"success": False, "message": str(e)}), 409

    @app.errorhandler(CustomException)
    def handle_custom(e):
        return jsonify({"success": False, "message": str(e)}), 400

    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({"success": False, "message": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def handle_500(e):
        return jsonify({"success": False, "message": "Internal server error"}), 500
