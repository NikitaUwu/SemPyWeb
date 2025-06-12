from flask import Blueprint, jsonify
auth_bp = Blueprint("auth", __name__)
@auth_bp.route("/auth/ping")
def ping():
    return jsonify(auth="ok")
