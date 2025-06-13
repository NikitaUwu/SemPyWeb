import pytest
from pathlib import Path

def login_get_token(client, email="test@example.com", password="password123"):
    """Логинимся через API и возвращаем полученный JWT access_token."""
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    # Убедимся, что логин успешен
    assert resp.status_code == 200, "Не удалось получить токен"
    # Извлекаем и возвращаем токен из ответа
    return resp.get_json()["access_token"]


def test_login_bad_credentials(client, new_user):
    """Проверяем, что при неверном пароле возвращается 401."""
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": new_user.email, "password": "wrongpass"}
    )
    assert resp.status_code == 401
    # В ответе должно быть поле error
    assert "error" in resp.get_json()


def test_login_success(client, new_user):
    """Успешный логин: получаем непустую строку токена."""
    token = login_get_token(client, new_user.email, "password123")
    assert isinstance(token, str) and token


def test_guest_upload_limit(client, wav_stub):
    """
    Гость может загрузить максимум 5 файлов.
    Шестая попытка должна вернуть 403 и сообщение про лимит.
    """
    # 5 успешных загрузок подряд
    for _ in range(5):
        r = client.post(
            "/api/v1/upload",
            data={"file": (open(wav_stub, "rb"), wav_stub.name)},
            content_type="multipart/form-data"
        )
        assert r.status_code == 201

    # 6-я загрузка должна быть запрещена
    r6 = client.post(
        "/api/v1/upload",
        data={"file": (open(wav_stub, "rb"), wav_stub.name)},
        content_type="multipart/form-data"
    )
    assert r6.status_code == 403
    assert "limit" in r6.get_json()["error"].lower()


def test_auth_upload_unlimited(client, new_user, wav_stub):
    """
    Авторизованный пользователь может загружать без ограничений.
    После 7 загрузок в базе должно быть 7 записей.
    """
    token = login_get_token(client, new_user.email, "password123")

    # Делает 7 последовательных загрузок с токеном
    for _ in range(7):
        r = client.post(
            "/api/v1/upload",
            headers={"Authorization": f"Bearer {token}"},
            data={"file": (open(wav_stub, "rb"), wav_stub.name)},
            content_type="multipart/form-data"
        )
        assert r.status_code == 201

    # Проверка в БД: сколько треков привязано к новому пользователю
    from app import db
    from app.models import Track
    with client.application.app_context():
        cnt = Track.query.filter_by(user_id=new_user.id).count()
        assert cnt == 7


def test_get_tracks_and_detail(client, new_user, wav_stub):
    """
    Проверяем получение списка треков и детальной информации по конкретному треку.
    """
    token = login_get_token(client, new_user.email, "password123")

    # Загружаем трек и получаем его ID
    upload = client.post(
        "/api/v1/upload",
        headers={"Authorization": f"Bearer {token}"},
        data={"file": (open(wav_stub, "rb"), wav_stub.name)},
        content_type="multipart/form-data"
    )
    assert upload.status_code == 201
    tid = upload.get_json()["id"]

    # GET /tracks — список всех треков пользователя
    lst = client.get(
        "/api/v1/tracks",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert lst.status_code == 200
    tracks = lst.get_json()["tracks"]
    # Убедимся, что наш трек присутствует в списке
    assert any(t["id"] == tid for t in tracks)

    # GET /tracks/<id> — детальная информация
    detail = client.get(
        f"/api/v1/tracks/{tid}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert detail.status_code == 200
    assert detail.get_json()["id"] == tid


def test_upload_bad_extension(client, wav_stub):
    """
    Проверяем, что загрузка файла с неподдерживаемым расширением
    возвращает 415 Unsupported Media Type.
    """
    # Переименовываем наш валидный WAV-заглушку в .txt
    bad = Path(wav_stub).with_suffix(".txt")
    bad.write_bytes(Path(wav_stub).read_bytes())

    r = client.post(
        "/api/v1/upload",
        data={"file": (open(bad, "rb"), bad.name)},
        content_type="multipart/form-data"
    )
    # Ожидаем 415 и сообщение об ошибке, связанной с расширением
    assert r.status_code == 415
    assert "extension" in r.get_json()["error"].lower()
