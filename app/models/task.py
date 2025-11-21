from sqlalchemy import Column, String, Boolean
from app.database.base import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    done = Column(Boolean, default=False)
