from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from back.database import SessionLocal
from back.models import Task
from back.schemas.task import TaskCreate, TaskUpdate, Task

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/tasks/", response_model=Task)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    try:
        db_task = Task(
            task_name=task.task_name,
            task_status=task.task_status,
            task_description=task.task_description,
            task_type=task.task_type,
            task_data=task.task_data,
            requirements=task.requirements
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create task")

@router.put("/tasks/{task_id}", response_model=Task)
async def edit_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.task_id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        db_task.task_name = task.task_name or db_task.task_name
        db_task.task_status = task.task_status or db_task.task_status
        db_task.task_description = task.task_description or db_task.task_description
        db_task.task_type = task.task_type or db_task.task_type
        db_task.task_data = task.task_data or db_task.task_data
        db_task.requirements = task.requirements or db_task.requirements

        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update task")

@router.get("/tasks/", response_model=list[Task])
async def read_tasks(db: Session = Depends(get_db)):
    try:
        tasks = db.query(Task).all()
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve tasks")
