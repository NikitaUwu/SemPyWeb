# app/main/routes.py

import os
import uuid
from flask import (
    Blueprint, render_template, redirect, url_for,
    current_app, request, flash, abort
)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from ..models import Track
from ..services.classifier import classify
from ..services.limiter import guest_can_upload
from .. import db
from .forms import UploadForm
from app.services.limiter import reset_guest_limit


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    # Главная теперь — информация о модели
    return redirect(url_for("main.model_info"))


@main_bp.route("/upload", methods=["GET", "POST"])
def upload():
    """
    Разрешаем доступ гостям (до 5 загрузок) и авторизованным.
    После 5 гостевых загрузок — перенаправляем на вход.
    """
    form = UploadForm()
    user = current_user if current_user.is_authenticated else None

    if form.validate_on_submit():
        # Проверяем лимит для гостя
        if user is None and not guest_can_upload():
            flash(
                "Гостевой лимит загрузок исчерпан. Пожалуйста, войдите в систему.",
                "warning"
            )
            return redirect(url_for("auth.login"))

        f = form.file.data
        filename_raw = secure_filename(f.filename)
        ext = os.path.splitext(filename_raw)[1].lower()
        unique_name = f"{uuid.uuid4().hex}{ext}"

        # Сохраняем в папке пользователя или в общей
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        if user:
            dest_dir = os.path.join(upload_folder, str(user.id))
        else:
            dest_dir = os.path.join(upload_folder, "guests")
        os.makedirs(dest_dir, exist_ok=True)

        save_path = os.path.join(dest_dir, unique_name)
        f.save(save_path)

        # Классифицируем
        try:
            genre = classify(save_path)
        except Exception:
            genre = "unknown"

        # Сохраняем в БД
        track = Track(
            filename=unique_name,
            original_filename=filename_raw,
            genre=genre,
            user_id=user.id if user else None
        )
        db.session.add(track)
        db.session.commit()

        return redirect(url_for("main.result", track_id=track.id))

    return render_template("upload.html", form=form, user=user)


@main_bp.route("/result/<int:track_id>")
def result(track_id):
    """
    Доступен всем — и гостям, и залогиненным.
    """
    track = Track.query.get_or_404(track_id)
    return render_template("result.html", track=track)


@main_bp.route("/stats")
@login_required
def stats():
    sort = request.args.get("sort", "date")
    order = request.args.get("order", "desc")
    group = request.args.get("group", "0") == "1"

    col = Track.original_filename if sort == "name" else Track.uploaded_at

    if order == "asc":
        q = current_user.tracks.order_by(col.asc())
        next_order = "desc"
    else:
        q = current_user.tracks.order_by(col.desc())
        next_order = "asc"

    tracks = q.all()

    if group:
        grouped = {}
        for t in tracks:
            grouped.setdefault(t.genre, []).append(t)
        return render_template(
            "stats.html",
            grouped=grouped,
            sort=sort,
            order=order,
            next_order=next_order,
            group=True
        )

    return render_template(
        "stats.html",
        tracks=tracks,
        sort=sort,
        order=order,
        next_order=next_order,
        group=False
    )


@main_bp.route("/model_info")
def model_info():
    genres = [
        "blues", "classical", "country", "disco", "hiphop",
        "jazz", "metal", "pop", "reggae", "rock"
    ]
    info = {
        "model_name": "pedromatias97/genre-recognizer-finetuned-gtzan_dset",
        "supported_genres": genres,
        "max_duration": "до 5 минут",
        "notes": "HF Audio Classification Pipeline"
    }
    return render_template("model_info.html", info=info)


@main_bp.route("/admin/reset_guest_limit")
@login_required
def admin_reset_guest_limit():
    """Сброс гостевого лимита доступен только админу."""
    # проверяем, совпадает ли почта текущего пользователя с ADMIN_EMAIL
    if current_user.email.lower() != current_app.config["ADMIN_EMAIL"].lower():
        abort(403)

    reset_guest_limit()
    flash("Гостевой лимит загрузок успешно сброшен.", "success")
    return redirect(url_for("main.upload"))