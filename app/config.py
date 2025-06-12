# app/config.py

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-me-too")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DefaultConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(basedir, '..', 'instance', 'app.db')}"
    )
    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER",
        os.path.join(basedir, "..", "instance", "uploads")
    )
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@mail.com")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    JWT_SECRET_KEY = "test-jwt-secret"
    UPLOAD_FOLDER = os.path.join(basedir, "..", "tests", "tmp_uploads")
    ADMIN_EMAIL = "test@mail.com"
