from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from app.schemas.user import UserCreate, User
from app.models.user import User as UserModel
from app.database.engine import get_db
from app.core.security import create_token, hash_password, verify_password  # CAMBIO

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
