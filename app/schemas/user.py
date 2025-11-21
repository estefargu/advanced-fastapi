from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: str
    username: str
    class Config:
        from_attributes = True  # CAMBIO: era orm_mode = True
