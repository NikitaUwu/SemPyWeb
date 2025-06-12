# manage.py
from app import create_app

app = create_app()  # по умолчанию используется DefaultConfig

if __name__ == "__main__":
    app.run(debug=True)
