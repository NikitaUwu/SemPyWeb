# app/auth/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegistrationForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=120)]
    )
    password = PasswordField(
        "Пароль",
        validators=[DataRequired(), Length(min=8)]
    )
    confirm_password = PasswordField(
        "Подтвердите пароль",
        validators=[DataRequired(), EqualTo("password", message="Пароли должны совпадать")]
    )
    submit = SubmitField("Зарегистрироваться")


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=120)]
    )
    password = PasswordField(
        "Пароль",
        validators=[DataRequired()]
    )
    remember_me = BooleanField("Запомнить меня")  # ← вот это поле
    submit = SubmitField("Войти")
