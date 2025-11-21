'''
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from app.schemas.user import UserCreate, User
from app.models.user import User as UserModel
from app.database.engine import get_db
from app.core.security import create_token, hash_password, verify_password  # CAMBIO
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=User)
def register(user: UserCreate, db: Session = Depends(get_db)):
    exists = db.query(UserModel).filter(UserModel.username == user.username).first()
    if exists:
        raise HTTPException(status_code=400, detail="User already exists")

    #CAMBIO: Hashear el password antes de guardar
    hashed_password = hash_password(user.password)
    new = UserModel(id=str(uuid4()), username=user.username, password=hashed_password)
    
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    u = db.query(UserModel).filter(UserModel.username == user.username).first()

    # CAMBIO: Verificar password hasheado en lugar de comparación directa
    if not u or not verify_password(user.password, u.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token({"sub": u.id})
    return {"access_token": token}
'''

# ============================================
# Endpoints de autenticación
# ============================================

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserLogin, User, Token
from app.database.engine import get_db
from app.services.auth_service import AuthService
from app.api.dependencies.auth import get_current_user
from app.models.user import User as UserModel

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/register",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="Crea un nuevo usuario en el sistema con username y password"
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario.
    
    - **username**: Nombre de usuario único (3-50 caracteres)
    - **password**: Contraseña segura (mínimo 6 caracteres)
    """
    return AuthService.register(user_data, db)


@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesión",
    description="Autentica un usuario y retorna un token JWT"
)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Inicia sesión con credenciales.
    
    - **username**: Nombre de usuario
    - **password**: Contraseña
    
    Retorna un token JWT válido por 30 minutos (configurable).
    """
    return AuthService.authenticate(login_data, db)


@router.get(
    "/me",
    response_model=User,
    summary="Obtener usuario actual",
    description="Retorna la información del usuario autenticado"
)
def get_me(current_user: UserModel = Depends(get_current_user)):
    """
    Obtiene información del usuario actual.
    
    Requiere token JWT válido en el header Authorization.
    """
    return current_user


@router.post(
    "/verify-token",
    summary="Verificar token",
    description="Verifica si un token JWT es válido"
)
def verify_token(token: str):
    """
    Verifica la validez de un token JWT.
    
    - **token**: Token JWT a verificar
    
    Retorna el payload del token si es válido.
    """
    payload = AuthService.verify_token(token)
    return {
        "valid": True,
        "user_id": payload.get("sub"),
        "expires": payload.get("exp")
    }