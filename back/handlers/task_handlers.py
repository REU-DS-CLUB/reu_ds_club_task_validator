import logging
import aiofiles
from pathlib import Path
from os import getenv
from typing import List
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from docker import DockerClient
from back.utils.database import get_db
from back.utils.models import Task as TaskModel, TaskStatus, TaskType
from back.schemas.task import TaskUpdate, TaskBase, Task as TaskSchema
import shutil

router = APIRouter()

logging.basicConfig(level="INFO", format="%(asctime)s, %(levelname)s: %(message)s", force=True)
logger = logging.getLogger()


@router.get("/get_tasks", response_model=list[TaskSchema])
async def read_tasks(db: Session = Depends(get_db)):
    try:
        tasks = db.query(TaskModel).filter(TaskModel.task_status != TaskStatus.DELETED).all()
        return tasks
    except Exception as e:
        logger.error(f"read_tasks: Error retrieving tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving tasks: {str(e)}")


@router.get("/get_task/{task_id}", response_model=TaskSchema)
async def read_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(
        TaskModel.task_id == task_id,
        TaskModel.task_status != TaskStatus.DELETED
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id {str(task_id)} not found")
    return task


@router.post("/create_task", response_model=TaskSchema)
async def create_task(task: TaskBase = Form(...),
                     files: List[UploadFile] = File(...),
                     db: Session = Depends(get_db)):
    try:
        # Validate files based on task type
        extensions = {file.filename.split('.')[-1].lower() for file in files}
        logger.info(f"create_task: Received files for task type {task.task_type} with extensions {extensions}")

        required_files = {
            TaskType.CSV: {"py", "txt"},  # check_submission.py and requirements.txt
            TaskType.EXECUTABLE: {"py", "pkl", "txt"}  # check_submission.py, weights.pkl, and requirements.txt
        }

        if extensions != required_files[task.task_type]:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid file formats for task type {task.task_type}. Required: {required_files[task.task_type]}"
            )

        # Create task in database
        db_task = TaskModel(
            task_num=task.task_num,
            task_name=task.task_name,
            task_status=task.task_status,
            task_description=task.task_description,
            task_type=task.task_type,
            task_data=task.task_data,
            task_data_admin=task.task_data_admin
        )

        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        task_id = db_task.task_id
        logger.info(f"create_task: Created new task with id {str(task_id)}")

        # Create task directory and save files
        base_dir = getenv("CONTAINER_HOME")
        task_dir = Path(f"{base_dir}/tasks/{task_id}")
        task_dir.mkdir(parents=True, exist_ok=True)

        # Save files with proper names
        file_mapping = {
            "py": "check_submission.py",
            "txt": "requirements.txt",
            "pkl": "weights.pkl"
        }

        try:
            for file in files:
                ext = file.filename.split(".")[-1].lower()
                file_path = task_dir / file_mapping[ext]
                
                async with aiofiles.open(file_path, "wb") as disk_file:
                    content = await file.read()
                    await disk_file.write(content)
                    logger.info(f"create_task: Saved file {file_mapping[ext]} ({len(content)} bytes)")

            # Create Dockerfile
            dockerfile_lines = [
                "FROM python:3.12-slim",
                "COPY check_submission.py /check_submission.py",
                "COPY requirements.txt /requirements.txt",
            ]

            if task.task_type == TaskType.EXECUTABLE:
                dockerfile_lines.append("COPY weights.pkl /weights.pkl")

            dockerfile_lines.extend([
                "RUN apt-get update && \\",
                "    pip install --upgrade pip && \\",
                "    pip install -r /requirements.txt"
            ])

            dockerfile_content = "\n".join(dockerfile_lines)
            (task_dir / "Dockerfile").write_text(dockerfile_content)

            # Build Docker image
            client = DockerClient(base_url='unix://var/run/docker.sock')
            image, build_logs = client.images.build(
                path=str(task_dir),
                tag=f"img_task_{str(task_id)}",
                rm=True
            )
            logger.info(f"create_task: Successfully built Docker image for task_id={str(task_id)}: {image.tags}")

            return task_id

        except Exception as e:
            # Cleanup in case of error
            try:
                if task_dir.exists():
                    shutil.rmtree(task_dir)
            except Exception as cleanup_error:
                logger.error(f"create_task: Error cleaning up task directory: {str(cleanup_error)}")

            logger.error(f"create_task: Error during file processing or Docker build: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"create_task: Unhandled error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")


@router.put("/edit_task/{task_id}", response_model=TaskSchema)
async def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(TaskModel).filter(
        TaskModel.task_id == task_id,
        TaskModel.task_status != TaskStatus.DELETED
    ).first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail=f"Task with id {str(task_id)} not found")

    try:
        for key, value in task.dict(exclude_unset=True).items():
            setattr(db_task, key, value)
        
        db.commit()
        db.refresh(db_task)
        logger.info(f"update_task: Successfully updated task {str(task_id)}")
        return db_task

    except Exception as e:
        logger.error(f"update_task: Error updating task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")
