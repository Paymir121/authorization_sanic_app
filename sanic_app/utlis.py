import hashlib
from datetime import datetime, timedelta

from sanic_app.settings import SECRET_KEY


def generate_jwt(user_id, jwt=None):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
