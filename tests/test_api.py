# tests/test_api.py

import pytest
from pathlib import Path

def login_get_token(client, email="test@example.com", password="password123"):
    """Логинимся и возвращаем access_token."""
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    assert resp.status_code == 200, "Не удалось получить токен"
    return resp.get_json()["access_token"]


def test_login_bad_credentials(client, new_user):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": new_user.email, "password": "wrongpass"}
    )
    assert resp.status_code == 401
    assert "error" in resp.get_json()


def test_login_success(client, new_user):
    token = login_get_token(client, new_user.email, "password123")
    assert isinstance(token, str) and token


def test_guest_upload_limit(client, wav_stub):
    # 5 успешных загрузок
    for _ in range(5):
        r = client.post(
            "/api/v1/upload",
            data={"file": (open(wav_stub, "rb"), wav_stub.name)},
            content_type="multipart/form-data"
        )
        assert r.status_code == 201

    # 6-я должна упасть с 403
    r6 = client.post(
        "/api/v1/upload",
        data={"file": (open(wav_stub, "rb"), wav_stub.name)},
        content_type="multipart/form-data"
    )
    assert r6.status_code == 403
    assert "limit" in r6.get_json()["error"].lower()


def test_auth_upload_unlimited(client, new_user, wav_stub):
    token = login_get_token(client, new_user.email, "password123")
    # разрешено более 5 загрузок
    for _ in range(7):
        r = client.post(
            "/api/v1/upload",
            headers={"Authorization": f"Bearer {token}"},
            data={"file": (open(wav_stub, "rb"), wav_stub.name)},
            content_type="multipart/form-data"
        )
        assert r.status_code == 201

    # проверяем количество записей в БД
    from app import db
    from app.models import Track
    with client.application.app_context():
        cnt = Track.query.filter_by(user_id=new_user.id).count()
        assert cnt == 7


def test_get_tracks_and_detail(client, new_user, wav_stub):
    token = login_get_token(client, new_user.email, "password123")

    upload = client.post(
        "/api/v1/upload",
        headers={"Authorization": f"Bearer {token}"},
        data={"file": (open(wav_stub, "rb"), wav_stub.name)},
        content_type="multipart/form-data"
    )
    assert upload.status_code == 201
    tid = upload.get_json()["id"]

    # GET /tracks
    lst = client.get(
        "/api/v1/tracks",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert lst.status_code == 200
    tracks = lst.get_json()["tracks"]
    assert any(t["id"] == tid for t in tracks)

    # GET /tracks/<id>
    detail = client.get(
        f"/api/v1/tracks/{tid}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert detail.status_code == 200
    assert detail.get_json()["id"] == tid


def test_upload_bad_extension(client, wav_stub):
    bad = Path(wav_stub).with_suffix(".txt")
    bad.write_bytes(wav_stub.read_bytes())

    r = client.post(
        "/api/v1/upload",
        data={"file": (open(bad, "rb"), bad.name)},
        content_type="multipart/form-data"
    )
    assert r.status_code == 415
    assert "extension" in r.get_json()["error"].lower()
