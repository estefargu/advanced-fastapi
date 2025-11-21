from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "secret-key-change-this"
ALGORITHM = "HS256"

def create_token(data: dict, expires_minutes: int = 30):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
