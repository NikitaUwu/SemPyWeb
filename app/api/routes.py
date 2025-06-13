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
    # Получаем JSON из запроса и ищем пользователя по email
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get("email")).first()

    # Если пользователь найден и пароль совпадает — выдаём JWT
    if user and user.verify_password(data.get("password", "")):
        token = create_access_token(identity=str(user.id))
        return jsonify(access_token=token), 200

    # В противном случае — 401 Unauthorized
    return jsonify(error="Bad credentials"), 401


@api_bp.route("/upload", methods=["POST"])
@jwt_required(optional=True)
def api_upload():
    # Определяем, залогинен ли пользователь
    user_id = get_jwt_identity()
    user = User.query.get(user_id) if user_id else None

    # Проверяем гостевой лимит, если нет токена
    if user is None and not guest_can_upload():
        return jsonify(error="Guest upload limit reached"), 403

    # Проверяем, передан ли файл
    if "file" not in request.files:
        return jsonify(error="No file part"), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify(error="No selected file"), 400

    # Очищаем имя и проверяем расширение
    filename_raw = secure_filename(file.filename)
    ext = os.path.splitext(filename_raw)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify(error="Unsupported file extension"), 415

    # Генерируем уникальное имя и сохраняем файл
    unique_name = f"{uuid.uuid4().hex}{ext}"
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    save_path = os.path.join(upload_folder, unique_name)
    file.save(save_path)

    # Пытаемся классифицировать аудио, при ошибке — 'unknown'
    try:
        genre = classify(save_path)
    except Exception:
        genre = "unknown"

    # Сохраняем информацию о треке в базе
    track = Track(
        filename=unique_name,
        original_filename=filename_raw,
        genre=genre,
        user_id=user.id if user else None
    )
    db.session.add(track)
    db.session.commit()

    # Возвращаем созданный ресурс
    return jsonify(id=track.id, filename=unique_name, genre=genre), 201


@api_bp.route("/tracks", methods=["GET"])
@jwt_required()
def api_tracks():
    # Получаем ID текущего пользователя и его треки
    user_id = get_jwt_identity()
    tracks = Track.query.filter_by(user_id=user_id).all()

    # Формируем список треков для JSON
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

    # Возвращаем красиво отформатированный JSON
    pretty = json.dumps(payload, ensure_ascii=False, indent=2)
    return current_app.response_class(pretty, mimetype="application/json")


@api_bp.route("/tracks/<int:track_id>", methods=["GET"])
@jwt_required()
def api_track_detail(track_id):
    # Ищем конкретный трек пользователя или 404
    user_id = get_jwt_identity()
    t = Track.query.filter_by(id=track_id, user_id=user_id).first_or_404()

    # Возвращаем детали трека
    return jsonify(
        id=t.id,
        filename=t.filename,
        genre=t.genre,
        uploaded_at=t.uploaded_at.isoformat()
    ), 200
