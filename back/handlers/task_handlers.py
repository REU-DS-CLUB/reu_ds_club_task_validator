from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from back.database import get_db
from back.schemas.task import TaskCreate, TaskUpdate, Task as TaskSchema
from back.models import Task as TaskModel
from back.crud import create_task, get_task

router = APIRouter()

@router.get("/", response_model=list[TaskSchema])
async def read_tasks(db: Session = Depends(get_db)):
    try:
        tasks = db.query(TaskModel).all()
        return tasks
    except Exception as e:
        print(f"Error retrieving tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tasks")

# @router.post("/tasks/", response_model=TaskSchema)
# async def create_task_handler(task: TaskCreate, db: Session = Depends(get_db)):
#     return create_task(db, task)

@router.post("/", response_model=TaskSchema)  # Обратите внимание на путь "/"
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = TaskModel(
        task_name=task.task_name,
        task_status=task.task_status,
        task_description=task.task_description,
        task_type=task.task_type,
        task_data=task.task_data,
        requirements=task.requirements,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.put("/{task_id}", response_model=TaskSchema)
async def update_task_handler(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    db_task = get_task(db, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task.dict(exclude_unset=True).items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task
