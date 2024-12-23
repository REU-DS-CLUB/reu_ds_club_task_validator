import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from back.database import get_db
from back.models import Task as TaskModel
from back.schemas.task import TaskCreate, TaskUpdate, Task as TaskSchema

router = APIRouter()
logger = logging.getLogger(__name__)

def raise_http_exception(status_code: int, detail: str):
    logger.error(f"HTTP Exception {status_code}: {detail}")
    raise HTTPException(status_code=status_code, detail=detail)

@router.get("/get_tasks", response_model=list[TaskSchema])
async def read_tasks(db: Session = Depends(get_db)) -> list[TaskSchema]:
    try:
        tasks = db.query(TaskModel).all()
        logger.info("Retrieved all tasks")
        return tasks
    except Exception as e:
        raise_http_exception(500, f"Error retrieving tasks: {str(e)}")

@router.get("/get_task/{task_id}", response_model=TaskSchema)
async def read_task(task_id: int, db: Session = Depends(get_db)) -> TaskSchema:
    task = db.query(TaskModel).filter(TaskModel.task_id == task_id).first()
    if not task:
        raise_http_exception(404, "Task not found")
    logger.info(f"Retrieved task with ID {task_id}")
    return task

@router.post("/add_task", response_model=TaskSchema)
async def create_task_handler(task: TaskCreate, db: Session = Depends(get_db)) -> TaskSchema:
    try:
        db_task = TaskModel(
            task_name=task.task_name,
            task_status=task.task_status,
            task_description=task.task_description,
            task_type=task.task_type,
            task_data=task.task_data,
            requirements=task.requirements,
            task_data_admin=task.task_data_admin,
            check_solution_file=task.check_solution_file,
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        logger.info(f"Created new task with ID {db_task.task_id}")
        return db_task
    except Exception as e:
        raise_http_exception(500, f"Error creating task: {str(e)}")

@router.put("/edit_task/{task_id}", response_model=TaskSchema)
async def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)) -> TaskSchema:
    db_task = db.query(TaskModel).filter(TaskModel.task_id == task_id).first()
    if not db_task:
        raise_http_exception(404, "Task not found")
    try:
        for key, value in task.dict(exclude_unset=True).items():
            setattr(db_task, key, value)
        db.commit()
        db.refresh(db_task)
        logger.info(f"Updated task with ID {task_id}")
        return db_task
    except Exception as e:
        raise_http_exception(500, f"Error updating task: {str(e)}")
