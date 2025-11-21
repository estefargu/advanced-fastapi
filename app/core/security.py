from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext  # NUEVO

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Cambiar estas líneas para usar variables de entorno
try:
    from app.core.config import settings
    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = settings.ALGORITHM
except:
    SECRET_KEY = "secret-key-change-this"
    ALGORITHM = "HS256"

# NUEVO: Función para hashear password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# NUEVO: Función para verificar password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_token(data: dict, expires_minutes: int = 30):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)