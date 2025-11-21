from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: str
    username: str
    class Config:
        from_attributes = True  # CAMBIO: era orm_mode = True

class UserLogin(BaseModel):
    """Schema para login de usuario."""
    username: str
    password: str


class Token(BaseModel):
    """Schema para respuesta de token."""
    access_token: str
    token_type: str
    user_id: str
    username: str


class TokenData(BaseModel):
    """Schema para datos del token decodificado."""
    user_id: Optional[str] = None