# SemPyWeb
Семестровая работа по web-приложениям на python

# GenreClassifier

**GenreClassifier** — веб-приложение на Flask для автоматического определения жанра аудиофайлов с помощью модели `pedromatias97/genre-recognizer-finetuned-gtzan_dset` (Hugging Face Audio Classification Pipeline).

- **Гости** могут загрузить до **5** файлов за 24-часовой период.  
- **Зарегистрированные** пользователи загружают без ограничений.  
- **Статистика** по каждому пользователю: список треков, жанр, время загрузки.  
- **Администратор** (e-mail в конфиге) может сбросить счётчик гостевых загрузок.  
- **REST-API** с JWT-аутентификацией.

---

## Технологии

- Python 3.13.2  
- Flask (+ Flask-Login, Flask-JWT-Extended, Flask-Migrate)  
- SQLAlchemy, Alembic  
- Jinja2, Bootstrap 5  
- Hugging Face Transformers (Audio Classification)  
- pytest для тестов  
- SQLite (по умолчанию)

---

## Установка и настройка

1. **Клонировать репозиторий**  
   ```bash
   git clone https://github.com/…/flask-genre-classifier.git
   cd flask-genre-classifier
   ```

2. **Виртуальное окружение**
   ```python -m venv .venv
    source .venv/bin/activate      # Linux/macOS
    .\.venv\Scripts\activate       # Windows PowerShell
   ```
   
3. **Установка зависимости**
   ```
   pip install -r requirements.txt
   ```

4. **Config**
   ```
   SECRET_KEY       = "your_secret"
   JWT_SECRET_KEY   = "your_jwt_secret"
   DATABASE_URL     = "sqlite:///instance/app.db"
   UPLOAD_FOLDER    = "instance/uploads"
   ADMIN_EMAIL      = "admin@example.com"
   ```

5. **БД и миграция**
   ```
   export FLASK_APP=manage.py
   flask db init        # только первый раз
   flask db migrate -m "Initial schema"
   flask db upgrade
   ```

## Запуск
```
export FLASK_APP=manage.py
export FLASK_ENV=development   # опционально
flask run
```
Откройте http://127.0.0.1:5000/

## REST-API
```
# Получить токен
$token = (Invoke-RestMethod `
  -Method Post `
  -Uri 'http://127.0.0.1:5000/api/v1/auth/login' `
  -ContentType 'application/json' `
  -Body '{ "email": "user@example.com", "password": "password123" }' `
).access_token

# Загрузить трек
Invoke-RestMethod `
  -Method Post `
  -Uri 'http://127.0.0.1:5000/api/v1/upload' `
  -Headers @{ Authorization = "Bearer $token" } `
  -Form @{ file = Get-Item 'C:\path\to\song.wav' }

# Список треков (читаемый вывод)
Invoke-RestMethod `
  -Method Get `
  -Uri 'http://127.0.0.1:5000/api/v1/tracks' `
  -Headers @{ Authorization = "Bearer $token" } `
| Select-Object -ExpandProperty tracks `
| Format-Table id, filename, genre, uploaded_at -AutoSize
```

## Тестирование
```
pytest -q
```

## Структура проекта
```
flask-genre-classifier/
├─ app/
│  ├─ auth/                # Регистрация/Вход
│  ├─ main/                # Веб-интерфейс
│  ├─ api/                 # REST-API
│  ├─ services/            # Классификатор + лимитер
│  ├─ templates/           # Jinja2-шаблоны
│  ├─ static/              # CSS/JS/изображения
│  ├─ models.py            # SQLAlchemy-модели
│  ├─ __init__.py          # Фабрика приложения
│  └─ config.py            # Конфиги
├─ instance/               # instance-данные (БД, uploads)
├─ migrations/             # Alembic миграции
├─ tests/                  # pytest-тесты
├─ manage.py               # Flask CLI entrypoint
├─ requirements.txt        # Зависимости
└─ README.md               # Этот файл
```

## License

This project is licensed under the **MIT License**. See the full text below or the [LICENSE](LICENSE) file for details.
