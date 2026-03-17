from flask import Blueprint, jsonify, request, session

from Backend.models import User, db
from Phase_2_Process_Management.code.process_manager import create_session_process, terminate_session_process
from Backend.utils.validation import require_fields

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    payload = request.get_json() or {}
    missing = require_fields(payload, ["username", "password"])
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    user = User.query.filter_by(username=payload["username"]).first()
    if not user or not user.check_password(payload["password"]):
        return jsonify({"error": "Invalid username or password"}), 401

    process_pid = create_session_process(user.id)
    session["user_id"] = user.id
    session["process_pid"] = process_pid
    return jsonify({"message": "Login successful", "user": user.to_dict(), "process_pid": process_pid})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    process_pid = session.get("process_pid")
    if process_pid:
        terminate_session_process(process_pid)
        session.pop("process_pid", None)
    session.pop("user_id", None)
    return jsonify({"message": "Logout successful"})


@auth_bp.route("/me", methods=["GET"])
def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"user": None}), 200

    user = db.session.get(User, user_id)
    return jsonify({"user": user.to_dict() if user else None, "process_pid": session.get("process_pid")})
