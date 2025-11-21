# ============================================
# Lógica de negocio de autenticación (MEJORADO)
# ============================================

from typing import Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from uuid import uuid4
from passlib.context import CryptContext
from jose import jwt
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class AuthService:
    """Servicio para manejar toda la lógica de autenticación."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Genera un hash seguro de la contraseña.
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            str: Hash de la contraseña
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifica si la contraseña coincide con el hash.
        
        Args:
            plain_password: Contraseña en texto plano
            hashed_password: Hash almacenado
            
        Returns:
            bool: True si coinciden, False en caso contrario
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
        """
        Crea un token JWT para el usuario.
        
        Args:
            user_id: ID del usuario
            expires_delta: Tiempo de expiración personalizado (opcional)
            
        Returns:
            str: Token JWT
        """
        to_encode = {"sub": user_id}
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def register(user_data: UserCreate, db: Session) -> User:
        """
        Registra un nuevo usuario.
        
        Args:
            user_data: Datos del usuario a registrar
            db: Sesión de base de datos
            
        Returns:
            User: Usuario creado
            
        Raises:
            HTTPException: Si el usuario ya existe o hay error de validación
        """
        # Verificar si el usuario ya existe
        existing_user = db.query(User).filter(
            User.username == user_data.username
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está registrado"
            )
        
        # Validar longitud de contraseña
        if len(user_data.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña debe tener al menos 6 caracteres"
            )
        
        # Crear usuario con contraseña hasheada
        hashed_password = AuthService.hash_password(user_data.password)
        new_user = User(
            id=str(uuid4()),
            username=user_data.username,
            password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    @staticmethod
    def authenticate(login_data: UserLogin, db: Session) -> dict:
        """
        Autentica un usuario y retorna el token de acceso.
        
        Args:
            login_data: Credenciales de login
            db: Sesión de base de datos
            
        Returns:
            dict: Diccionario con access_token y token_type
            
        Raises:
            HTTPException: Si las credenciales son inválidas
        """
        # Buscar usuario
        user = db.query(User).filter(
            User.username == login_data.username
        ).first()
        
        # Verificar usuario y contraseña
        if not user or not AuthService.verify_password(
            login_data.password,
            user.password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Crear token de acceso
        access_token = AuthService.create_access_token(user.id)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username
        }
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """
        Verifica y decodifica un token JWT.
        
        Args:
            token: Token JWT a verificar
            
        Returns:
            dict: Payload del token
            
        Raises:
            HTTPException: Si el token es inválido o expirado
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="El token ha expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )