from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    _password = db.Column("password", db.String(255), nullable=False)
    joined_at = db.Column(db.DateTime, server_default=db.func.now())
    tracks = db.relationship("Track", back_populates="user", cascade="all,delete")

    # --- хелперы для безопасного пароля ---
    @property
    def password(self):
        raise AttributeError("Password is write-only")

    @password.setter
    def password(self, raw: str) -> None:
        self._password = generate_password_hash(raw)

    def verify_password(self, raw: str) -> bool:
        return check_password_hash(self._password, raw)


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(50))
    uploaded_at = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="tracks")
