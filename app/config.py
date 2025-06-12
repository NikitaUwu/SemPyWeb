from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"          # корень instance
UPLOAD_DIR    = INSTANCE_DIR / "uploads"      # для аудио

class BaseConfig:
    # ...
    UPLOAD_FOLDER = UPLOAD_DIR
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    # <= ВАЖНО: абсолютный путь, а не относительный
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        f"sqlite:///{(INSTANCE_DIR / 'app.db').absolute()}",
    )
