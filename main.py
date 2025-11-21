from fastapi import FastAPI
from app.routers import tasks, auth
from app.database.base import Base
from app.database.engine import engine

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Advanced FastAPI Project", version="1.0.0")

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(auth.router)