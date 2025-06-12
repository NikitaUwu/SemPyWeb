import os
import sys
import tempfile
import pytest
import shutil
from pathlib import Path
from types import SimpleNamespace

# Добавляем корень проекта в PYTHONPATH
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import wave, struct

from app import create_app, db as _db
from app.models import User

@pytest.fixture(scope="session")
def app():
    """Flask-приложение в режиме testing с временной SQLite БД."""
    flask_app = create_app("testing")
    db_fd, db_path = tempfile.mkstemp(prefix="test_", suffix=".db")
    flask_app.config.update(
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}",
        TESTING=True,
        WTF_CSRF_ENABLED=False,
    )
    with flask_app.app_context():
        _db.create_all()
    yield flask_app
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def stub_classifier(monkeypatch):
    """Заглушка классификатора, всегда возвращает 'testgenre'."""
    monkeypatch.setattr(
        "app.services.classifier.classify",
        lambda path: "testgenre"
    )


@pytest.fixture
def wav_stub(tmp_path: Path) -> Path:
    """Минимальный валидный WAV-файл (160 сэмплов тишины)."""
    p = tmp_path / "stub.wav"
    with wave.open(str(p), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        frames = struct.pack("<" + "h"*160, *([0]*160))
        wf.writeframes(frames)
    return p


@pytest.fixture
def new_user(app):
    """
    Гарантированно создаёт одного пользователя в БД
    и возвращает простой объект с id/email.
    Удаляет до этого всех существующих с таким email.
    """
    email = "test@example.com"
    password = "password123"
    with app.app_context():
        # Удаляем старые записи (если есть)
        User.query.filter_by(email=email).delete()
        _db.session.commit()

        user = User(email=email)
        # присваиваем пароль через свойство .password
        user.password = password
        _db.session.add(user)
        _db.session.commit()
        uid = user.id

    # Возвращаем простой объект, без привязки к Session
    return SimpleNamespace(id=uid, email=email)


@pytest.fixture(scope="session", autouse=True)
def cleanup_uploads(app):
    yield
    # после всех тестов удаляем папку с загруженными файлами
    upload_dir = app.config.get("UPLOAD_FOLDER")
    if upload_dir:
        shutil.rmtree(upload_dir, ignore_errors=True)