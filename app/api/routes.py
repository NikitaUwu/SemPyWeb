# app/api/routes.py
import os, uuid
import json
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from ..services.classifier import classify
from ..services.limiter import guest_can_upload
from ..models import Track, User
from .. import db

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".flac"}

@api_bp.route("/auth/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get("email")).first()
    if user and user.verify_password(data.get("password", "")):
        # приводим identity к строке
        token = create_access_token(identity=str(user.id))
        return jsonify(access_token=token), 200
    return jsonify(error="Bad credentials"), 401

@api_bp.route("/upload", methods=["POST"])
@jwt_required(optional=True)
def api_upload():
    user_id = get_jwt_identity()
    user = User.query.get(user_id) if user_id else None

    if user is None and not guest_can_upload():
        return jsonify(error="Guest upload limit reached"), 403

    if "file" not in request.files:
        return jsonify(error="No file part"), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify(error="No selected file"), 400

    filename_raw = secure_filename(file.filename)
    ext = os.path.splitext(filename_raw)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify(error="Unsupported file extension"), 415

    unique_name = f"{uuid.uuid4().hex}{ext}"
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    save_path = os.path.join(upload_folder, unique_name)
    file.save(save_path)

    try:
        genre = classify(save_path)
    except Exception:
        genre = "unknown"

    track = Track(
        filename=unique_name,
        original_filename=filename_raw,
        genre=genre,
        user_id=(user.id if user else None)
    )
    db.session.add(track)
    db.session.commit()

    return jsonify(id=track.id, filename=unique_name, genre=genre), 201

@api_bp.route("/tracks", methods=["GET"])
@jwt_required()
def api_tracks():
    user_id = get_jwt_identity()
    tracks = Track.query.filter_by(user_id=user_id).all()
    payload = {
        "tracks": [
            {
                "id": t.id,
                "filename": t.filename,
                "genre": t.genre,
                "uploaded_at": t.uploaded_at.isoformat()
            } for t in tracks
        ]
    }
    pretty = json.dumps(payload, ensure_ascii=False, indent=2)
    return current_app.response_class(pretty, mimetype="application/json")

@api_bp.route("/tracks/<int:track_id>", methods=["GET"])
@jwt_required()
def api_track_detail(track_id):
    user_id = get_jwt_identity()
    t = Track.query.filter_by(id=track_id, user_id=user_id).first_or_404()
    return jsonify(
        id=t.id, filename=t.filename, genre=t.genre, uploaded_at=t.uploaded_at.isoformat()
    ), 200
