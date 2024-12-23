import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from back.database import get_db
from back.schemas.task import TaskCreate, TaskUpdate, Task as TaskSchema
from back.crud import get_tasks, get_task, create_task, update_task

router = APIRouter()
logger = logging.getLogger(__name__)

def raise_http_exception(status_code: int, detail: str):
    logger.error(f"HTTP Exception {status_code}: {detail}")
    raise HTTPException(status_code=status_code, detail=detail)

@router.get("/get_tasks", response_model=list[TaskSchema])
async def read_tasks(db: Session = Depends(get_db)) -> list[TaskSchema]:
    try:
        tasks = get_tasks(db)
        logger.info("Retrieved all tasks")
        return tasks
    except Exception as e:
        raise_http_exception(500, f"Error retrieving tasks: {str(e)}")

@router.get("/get_task/{task_id}", response_model=TaskSchema)
async def read_task(task_id: int, db: Session = Depends(get_db)) -> TaskSchema:
    task = get_task(db, task_id)
    if not task:
        raise_http_exception(404, "Task not found")
    logger.info(f"Retrieved task with ID {task_id}")
    return task

@router.post("/add_task", response_model=TaskSchema)
async def create_task_handler(task: TaskCreate, db: Session = Depends(get_db)) -> TaskSchema:
    try:
        db_task = create_task(db, task)
        logger.info(f"Created new task with ID {db_task.task_id}")
        return db_task
    except Exception as e:
        raise_http_exception(500, f"Error creating task: {str(e)}")

@router.put("/edit_task/{task_id}", response_model=TaskSchema)
async def update_task_handler(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)) -> TaskSchema:
    db_task = get_task(db, task_id)
    if not db_task:
        raise_http_exception(404, "Task not found")
    try:
        db_task = update_task(db, task_id, task)
        logger.info(f"Updated task with ID {task_id}")
        return db_task
    except Exception as e:
        raise_http_exception(500, f"Error updating task: {str(e)}")
