from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField
from wtforms.validators import DataRequired

class UploadForm(FlaskForm):
    file = FileField(
        "Аудио-файл",
        validators=[
            DataRequired(message="Выберите файл"),
            FileAllowed(["wav", "mp3", "flac"], "Только аудио-файлы!")
        ]
    )
    submit = SubmitField("Определить жанр")
