# app/auth/routes.py

from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, request
)
from flask_login import login_user, logout_user, current_user
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.upload"))

    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        if User.query.filter_by(email=email).first():
            flash("Пользователь с таким email уже существует.", "warning")
            return render_template("auth/signup.html", form=form)

        user = User(email=email)
        user.password = form.password.data
        db.session.add(user)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("При создании пользователя произошла ошибка.", "danger")
            return render_template("auth/signup.html", form=form)

        login_user(user)
        flash("Регистрация прошла успешно!", "success")
        return redirect(url_for("main.upload"))

    return render_template("auth/signup.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.upload"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash("Вход выполнен успешно.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.upload"))
        flash("Неправильный email или пароль.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("Вы вышли из системы.", "info")
    return redirect(url_for("auth.login"))
