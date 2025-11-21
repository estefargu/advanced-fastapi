from pydantic import BaseModel

class TaskBase(BaseModel):
    title: str
    description: str
    done: bool = False

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: str
    class Config:
        from_attributes = True  # CAMBIO: era orm_mode = True
