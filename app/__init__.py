"""
app package: инициализация расширений и factory create_app().
PEP 8: подключаем только то, что нужно, — никакой тяжёлой логики.
"""
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from pathlib import Path
import os

# Расширения (экземпляры объявляем здесь, инициализируем позже)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
jwt = JWTManager()

BASE_DIR = Path(__file__).resolve().parent.parent    # корень проекта
INSTANCE_DIR = BASE_DIR / "instance"                # <project>/instance
UPLOAD_DIR   = INSTANCE_DIR / "uploads"             # <project>/instance/uploads

def create_app(config_name: str | None = None) -> Flask:
    # 1) Загружаем .env до создания приложения
    load_dotenv(BASE_DIR / ".env", override=True)

    # 2) Создаём сам Flask-объект
    app = Flask(__name__, instance_relative_config=True)

    # 3) Подключаем конфиг-класс
    cfg = (config_name or os.getenv("FLASK_ENV", "development")).capitalize()
    app.config.from_object(f"app.config.{cfg}Config")

    # 4) ---------- ГАРАНТИЯ КАТАЛОГОВ  ----------
    #   a) <project>/instance               ->  для SQLite-файла
    #   b) <project>/instance/uploads       ->  для загружаемых аудио
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    # --------------------------------------------

    # 5) Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    login_manager.init_app(app)
    jwt.init_app(app)

    # 6) Регистрация blueprints (они уже существуют как заглушки)
    from app.api.routes import api_bp
    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    app.register_blueprint(api_bp,  url_prefix="/api/v1")
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app