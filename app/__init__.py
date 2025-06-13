import os
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager

from .services import limiter

# Инициализация расширений
db = SQLAlchemy()
login_manager = LoginManager()
jwt = JWTManager()

def create_app(config_name=None):
    """
    Фабрика приложения Flask.
    При необходимости передать имя конфига: 'default' или 'testing'.
    """
    app = Flask(__name__, instance_relative_config=True)

    # Выбор конфига по имени или через переменную окружения
    cfg = config_name or os.getenv("FLASK_CONFIG", "default")
    app.config.from_object(f"app.config.{cfg.capitalize()}Config")
    # Можно также подгрузить instance/config.py, если нужен override
    app.config.from_pyfile("config.py", silent=True)

    # Инициализируем расширения с приложением
    db.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)

    # Настройка перенаправления неавторизованных пользователей
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    # Функция для загрузки пользователя по ID из сессии
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Регистрируем blueprints
    from .main.routes import main_bp
    from .auth.routes import auth_bp
    from .api.routes import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    # Контекстный процессор: делаем доступными в шаблонах
    # - GUEST_LIMIT  — число гостевых загрузок
    # - session      — чтобы читать текущий счётчик
    @app.context_processor
    def inject_globals():
        return {
            "GUEST_LIMIT": limiter.GUEST_LIMIT,
            "session": session,
        }

    return app
