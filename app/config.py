import os

# Абсолютный путь до директории, где лежит этот файл (app/config.py)
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Базовый класс конфигурации.
    Общие настройки для всех сред.
    """
    # Секретный ключ для сессий Flask и CSRF
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")
    # Секретный ключ для подписи JWT-токенов
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-me-too")
    # Отключаем лишний overhead отслеживания изменений SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DefaultConfig(Config):
    """
    Конфигурация по умолчанию (production/development).
    Берёт настройки из переменных окружения или использует значения по умолчанию.
    """
    # URI подключения к базе данных (по умолчанию — SQLite в папке instance)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(basedir, '..', 'instance', 'app.db')}"
    )
    # Папка для хранения загруженных треков (по умолчанию — instance/uploads)
    UPLOAD_FOLDER = os.environ.get(
        "UPLOAD_FOLDER",
        os.path.join(basedir, "..", "instance", "uploads")
    )
    # E-mail администратора, которому доступен сброс лимита
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@mail.com")


class TestingConfig(Config):
    """
    Конфигурация для тестов (pytest).
    Использует in-memory SQLite и отключает CSRF.
    """
    TESTING = True
    # In-memory база для быстрого и чистого тестирования
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Отключаем CSRF-валидацию в тестовом режиме
    WTF_CSRF_ENABLED = False
    # Жёстко заданный JWT-ключ для тестов
    JWT_SECRET_KEY = "test-jwt-secret"
    # Папка для временных загрузок в тестах
    UPLOAD_FOLDER = os.path.join(basedir, "..", "tests", "tmp_uploads")
    # Тестовый e-mail администратора
    ADMIN_EMAIL = "test@mail.com"
