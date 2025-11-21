from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from app.schemas.task import Task, TaskCreate
from app.models.task import Task as TaskModel
from app.database.engine import get_db

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=Task)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new = TaskModel(id=str(uuid4()), **task.dict())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

@router.get("/", response_model=list[Task])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(TaskModel).all()

@router.get("/{task_id}", response_model=Task)
def get_task(task_id: str, db: Session = Depends(get_db)):
    t = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    return t

@router.put("/{task_id}", response_model=Task)
def update_task(task_id: str, task: TaskCreate, db: Session = Depends(get_db)):
    t = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    for k, v in task.dict().items():
        setattr(t, k, v)
    db.commit()
    db.refresh(t)
    return t

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: str, db: Session = Depends(get_db)):
    t = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(t)
    db.commit()
