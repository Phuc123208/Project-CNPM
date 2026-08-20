from flask import jsonify


def success_response(data=None, message="Success", status_code=200):
    return jsonify({"success": True, "message": message, "data": data}), status_code


def error_response(message="An error occurred", status_code=400):
    return jsonify({"success": False, "message": message}), status_code
