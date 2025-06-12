# app/services/limiter.py

from flask import session
from datetime import datetime, timedelta

GUEST_LIMIT = 5
SESSION_KEY = "guest_upload"
RESET_INTERVAL = timedelta(hours=24)

def guest_can_upload() -> bool:
    now = datetime.utcnow()
    data = session.get(SESSION_KEY)
    if data:
        start = datetime.fromisoformat(data["start"])
        count = data["count"]
        if now - start >= RESET_INTERVAL:
            count, start = 0, now
    else:
        count, start = 0, now

    if count >= GUEST_LIMIT:
        session[SESSION_KEY] = {"count": count, "start": start.isoformat()}
        return False

    session[SESSION_KEY] = {"count": count + 1, "start": start.isoformat()}
    return True

def reset_guest_limit():
    """
    Сбрасывает счётчик гостевых загрузок
    (удаляет ключ из сессии).
    """
    session.pop(SESSION_KEY, None)
