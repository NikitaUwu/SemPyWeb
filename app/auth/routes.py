from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request
)
from flask_login import (
    login_user,
    logout_user,
    current_user
)
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Регистрация нового пользователя.
    - GET: показать форму.
    - POST: валидировать, создать User, сохранить в БД, залогинить.
    """
    # Если уже залогинен, отправляем на страницу загрузки
    if current_user.is_authenticated:
        return redirect(url_for("main.upload"))

    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        # Проверяем, что такого email ещё нет
        if User.query.filter_by(email=email).first():
            flash("Пользователь с таким email уже существует.", "warning")
            return render_template("auth/signup.html", form=form)

        # Создаём нового пользователя и хешируем пароль
        user = User(email=email)
        user.password = form.password.data

        db.session.add(user)
        try:
            db.session.commit()  # сохраняем в БД
        except Exception:
            db.session.rollback()  # при ошибке откатываем транзакцию
            flash("При создании пользователя произошла ошибка.", "danger")
            return render_template("auth/signup.html", form=form)

        # Автоматический логин после успешной регистрации
        login_user(user)
        flash("Регистрация прошла успешно!", "success")
        return redirect(url_for("main.upload"))

    # При GET или невалидной форме отображаем шаблон
    return render_template("auth/signup.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Вход пользователя.
    - GET: показать форму.
    - POST: проверить email/password, залогинить.
    """
    # Если уже залогинен, нет смысла показывать форму
    if current_user.is_authenticated:
        return redirect(url_for("main.upload"))

    form = LoginForm()
    if form.validate_on_submit():
        # Ищем пользователя по email
        user = User.query.filter_by(email=form.email.data.lower()).first()
        # Проверяем пароль
        if user and user.verify_password(form.password.data):
            # Помним пользователя, если стоит флаг remember_me
            login_user(user, remember=form.remember_me.data)
            flash("Вход выполнен успешно.", "success")
            # Редиректим на страницу, откуда пришли, или на /upload
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.upload"))

        # Если проверка не прошла
        flash("Неправильный email или пароль.", "danger")

    # GET-запрос или невалидная форма
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
def logout():
    """
    Выход пользователя из системы.
    - Если был залогинен, разлогинивает и показывает сообщение.
    - Перенаправляет на страницу входа.
    """
    if current_user.is_authenticated:
        logout_user()
        flash("Вы вышли из системы.", "info")
    return redirect(url_for("auth.login"))
