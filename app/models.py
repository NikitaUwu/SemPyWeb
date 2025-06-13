from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
    """
    Модель пользователя.
    Наследует UserMixin для интеграции с Flask-Login.
    """
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    # Электронная почта, уникальное значение, индекс для быстрого поиска
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    # Хеш пароля (никогда не храним plaintext)
    password_hash = db.Column(db.String(128), nullable=False)
    # Дата и время регистрации, по умолчанию — текущее UTC
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Связь "один-ко-многим" с треками пользователя
    tracks = db.relationship("Track", backref="owner", lazy="dynamic")

    @property
    def password(self):
        """
        Запрет прямого чтения пароля.
        Поднять ошибку, если кто-то попытается обратиться к атрибуту password.
        """
        raise AttributeError("Пароль нельзя прочитать напрямую")

    @password.setter
    def password(self, plaintext):
        """
        При установке password автоматически генерируется и сохраняется хеш.
        """
        self.password_hash = generate_password_hash(plaintext)

    def verify_password(self, plaintext):
        """
        Проверить корректность введённого пароля:
        сравнить хеш в базе с хешем от переданного plaintext.
        """
        return check_password_hash(self.password_hash, plaintext)


class Track(db.Model):
    """
    Модель аудиотрека, загруженного пользователем.
    """
    __tablename__ = "track"

    id = db.Column(db.Integer, primary_key=True)
    # Имя файла на диске (UUID + расширение)
    filename = db.Column(db.String(255), nullable=False)
    # Оригинальное имя файла, какое было у пользователя
    original_filename = db.Column(db.String(255), nullable=False)
    # Определённый моделью жанр
    genre = db.Column(db.String(64), nullable=False)
    # Время загрузки, по умолчанию текущее UTC
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Внешний ключ на пользователя-владельца
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    # (Опционально) имя файла обложки, если есть
    cover_filename = db.Column(db.String(255), nullable=True)
