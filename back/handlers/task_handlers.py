from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from back.database import get_db
from back.models import Task as TaskModel
from back.schemas.task import TaskCreate, TaskUpdate, Task as TaskSchema

router = APIRouter()

@router.get("/get_tasks", response_model=list[TaskSchema])
async def read_tasks(db: Session = Depends(get_db)):
    try:
        tasks = db.query(TaskModel).all()
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tasks: {str(e)}")

@router.get("/get_task/{task_id}", response_model=TaskSchema)
async def read_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/add_task", response_model=TaskSchema)
async def create_task_handler(task: TaskCreate, db: Session = Depends(get_db)):
    try:
        print(task)
        db_task = TaskModel(
        task_name=task.task_name,
        task_status=task.task_status,
        task_description=task.task_description,
        task_type=task.task_type,
        task_data=task.task_data,
        requirements = task.requirements,
        task_data_admin=task.task_data_admin,
        check_solution_file=task.check_solution_file,
    )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")

@router.put("/edit_task/{task_id}", response_model=TaskSchema)
async def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(TaskModel).filter(TaskModel.task_id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    try:
        for key, value in task.dict(exclude_unset=True).items():
            setattr(db_task, key, value)
        db.commit()
        db.refresh(db_task)
        return db_task
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")
