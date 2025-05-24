from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
import os
from pathlib import Path
import shutil
from docker import DockerClient
from datetime import datetime
from back.utils.database import get_db
from back.utils.models import Assignment as AssignmentModel, Task as TaskModel, TaskType
from back.schemas.assignment import AssignmentCreate, Assignment as AssignmentSchema
import logging
from os import getenv
from typing import List
import pandas as pd

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_LOG_SIZE = 500  # Maximum number of characters for logs

def truncate_logs(logs: str, max_size: int = MAX_LOG_SIZE) -> str:
    """Truncate logs to max_size characters, preserving the start and end of the logs."""
    if len(logs) <= max_size:
        return logs
    
    # Calculate sizes for start and end portions
    portion_size = (max_size - 50) // 2  # 50 characters reserved for truncation message
    truncation_message = "\n...[LOGS TRUNCATED]...\n"
    
    start = logs[:portion_size]
    end = logs[-portion_size:]
    
    return f"{start}{truncation_message}{end}"


@router.get("/", response_model=list[AssignmentSchema])
async def read_assignments(db: Session = Depends(get_db)):

    try:
        assignments = db.query(AssignmentModel).all()
        return assignments

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving assignments: {str(e)}")


@router.post("/submit_assignment", response_model=dict)
async def submit_assignment(assignment: AssignmentCreate, db: Session = Depends(get_db)):

    try:
        new_assignment = AssignmentModel(**assignment.dict())
        db.add(new_assignment)
        db.commit()
        db.refresh(new_assignment)
        return {"is_ok": True, "err_message": ""}

    except Exception as e:
        return {"is_ok": False, "err_message": str(e)}


@router.get("/{assignment_id}", response_model=AssignmentSchema)
async def read_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(AssignmentModel).filter(AssignmentModel.assignment_id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


@router.get("/results/{tg_id}", response_model=list[AssignmentSchema])
async def get_best_results(tg_id: str, db: Session = Depends(get_db)):
    try:
        subquery = (
            db.query(
                AssignmentModel.task_id,
                func.max(AssignmentModel.mark).label("max_mark"),
                func.max(AssignmentModel.timestamp).label("latest_timestamp")
            )
            .filter(AssignmentModel.tg_id == tg_id)
            .group_by(AssignmentModel.task_id)
            .subquery()
        )

        results = (
            db.query(AssignmentModel)
            .join(
                subquery,
                (AssignmentModel.task_id == subquery.c.task_id) &
                (AssignmentModel.mark == subquery.c.max_mark) &
                (AssignmentModel.timestamp == subquery.c.latest_timestamp)
            )
            .filter(AssignmentModel.tg_id == tg_id)
            .all()
        )

        return [
            {
                "assignment_id": result.assignment_id,
                "task_id": result.task_id,
                "tg_id": result.tg_id,
                "mark": result.mark,
                "status": result.status,
                "error_message": result.error_message,
                "assignment_file": result.assignment_file,
                "timestamp": result.timestamp
            }
            for result in results
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving best results: {str(e)}")


@router.get("/assignments/{task_id}/{tg_id}", response_model=list[AssignmentSchema])
async def get_user_assignments_by_task(task_id: int, tg_id: str, db: Session = Depends(get_db)):
    try:
        assignments = (
            db.query(AssignmentModel)
            .filter(AssignmentModel.task_id == task_id, AssignmentModel.tg_id == tg_id)
            .all()
        )
        if not assignments:
            raise HTTPException(
                status_code=404,
                detail=f"No assignments found for task_id={task_id} and tg_id={tg_id}"
            )

        return [
            {
                "assignment_id": assignment.assignment_id,
                "task_id": assignment.task_id,
                "tg_id": assignment.tg_id,
                "mark": assignment.mark,
                "status": assignment.status,
                "error_message": assignment.error_message,
                "assignment_file": assignment.assignment_file,
                "timestamp": assignment.timestamp,
            }
            for assignment in assignments
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving assignments: {str(e)}")


@router.post("/score_assignment", response_model=AssignmentSchema)
async def score_assignment(
    task_id: int,
    tg_id: str,
    submit_time: str,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Get task type from database
        task = db.query(TaskModel).filter(TaskModel.task_id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with id {str(task_id)} not found")

        # Validate files based on task type
        if len(files) != 1:
            raise HTTPException(status_code=422, detail="Exactly one file must be submitted")

        file = files[0]
        extension = file.filename.split('.')[-1].lower()
        logger.info(f"score_assignment: Processing task_id={str(task_id)} for user {tg_id} with file extension {extension}")

        # Validate file extension based on task type
        if task.task_type == TaskType.CSV and extension != 'csv':
            raise HTTPException(status_code=422, detail="CSV task requires a .csv file")
        elif task.task_type == TaskType.EXECUTABLE and extension != 'py':
            raise HTTPException(status_code=422, detail="Executable task requires a .py file")

        # Create user's directory in the host filesystem
        base_dir = getenv("CONTAINER_HOME")
        user_dir = Path(f"{base_dir}/users/{tg_id}")
        user_dir.mkdir(parents=True, exist_ok=True)

        # Save submitted file with submit_time in filename
        new_filename = f"task_{str(task_id)}_{submit_time}.{extension}"
        file_path = user_dir / new_filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"score_assignment: Saved file {new_filename} for task_id={str(task_id)}, user={tg_id}")

        # Create a temporary directory for Docker build
        temp_dir = f"temp_task_{str(task_id)}_user_{tg_id}"
        os.makedirs(temp_dir, exist_ok=True)

        try:
            # Copy file from host storage to temp directory for Docker build
            dst_path = Path(temp_dir) / new_filename
            shutil.copy2(file_path, dst_path)

            # Create a Dockerfile that uses the task image as base
            dockerfile_content = f"""
FROM img_task_{str(task_id)}
COPY . /
WORKDIR /
"""
            with open(os.path.join(temp_dir, "Dockerfile"), "w") as f:
                f.write(dockerfile_content)

            # Initialize Docker client
            client = DockerClient(base_url='unix://var/run/docker.sock')

            # Build the Docker image
            submission_image_name = f"submission_task_{str(task_id)}_user_{tg_id}"
            container_name = f"task_{str(task_id)}_user_{tg_id}"

            try:
                # Build new image using the task image as base
                client.images.build(
                    path=temp_dir,
                    tag=submission_image_name,
                    rm=True
                )

                # Run the container
                container = client.containers.run(
                    submission_image_name,
                    command="python3 check_submission.py",
                    name=container_name,
                    detach=True,
                    mem_limit="512m",  # Limit memory to 512MB
                    memswap_limit="512m",  # Disable swap
                    cpu_period=100000,  # Default CPU CFS period
                    cpu_quota=25000,  # Limit to 25% of CPU
                    pids_limit=10,  # Limit number of processes
                    network_disabled=True  # Disable network access for security
                )

                # Wait for container to finish and get the result
                result = container.wait(timeout=600)  # 10 minute timeout
                logs = container.logs().decode('utf-8')

                try:
                    # Looking for result line with marker "RESULT:"
                    result_line = None
                    for line in logs.strip().split('\n'):
                        if line.startswith("RESULT:"):
                            result_line = line[7:].strip()  # Remove "RESULT:" prefix
                            break

                    if result_line and result['StatusCode'] == 0:
                        # Parse result line in format: mark,status,error_message
                        output_parts = result_line.split(',')
                        if len(output_parts) >= 2:
                            mark = int(output_parts[0])
                            status = output_parts[1]
                            error_message = truncate_logs(output_parts[2])
                        else:
                            raise ValueError(f"Invalid result format: {result_line}")
                    else:
                        # Container failed to run properly or no result line found
                        mark = -1
                        status = "error"
                        error_message = f"Container execution failed or no result found. Logs: {truncate_logs(logs)}"

                    # Create new assignment record
                    new_assignment = AssignmentModel(
                        task_id=task_id,
                        tg_id=tg_id,
                        mark=mark,
                        status=status,
                        error_message=error_message,
                        assignment_file=new_filename,
                        timestamp=datetime.utcnow()
                    )

                except Exception as parse_error:
                    logger.error(f"score_assignment: Error parsing check_submission.py output: {str(parse_error)}")
                    new_assignment = AssignmentModel(
                        task_id=task_id,
                        tg_id=tg_id,
                        mark=-1,
                        status="error",
                        error_message=f"Failed to parse submission result: {str(parse_error)}. Full logs: {truncate_logs(logs)}",
                        assignment_file=new_filename,
                        timestamp=datetime.utcnow()
                    )

                # Save to database
                db.add(new_assignment)
                db.commit()
                db.refresh(new_assignment)

                # Cleanup
                container.remove()
                client.images.remove(submission_image_name, force=True)
                logger.info(f"score_assignment: Cleaned up container and image for task_id={str(task_id)}, user={tg_id}")

                return new_assignment

            except Exception as e:
                # Handle Docker errors
                new_assignment = AssignmentModel(
                    task_id=task_id,
                    tg_id=tg_id,
                    mark=-1,
                    status="error",
                    error_message=str(e),
                    assignment_file=new_filename,
                    timestamp=datetime.utcnow()
                )
                db.add(new_assignment)
                db.commit()

                # Cleanup in case of error
                try:
                    client.images.remove(submission_image_name, force=True)
                    logger.info(f"score_assignment: Cleaned up image after error for task_id={str(task_id)}, user={tg_id}")
                except Exception as cleanup_error:
                    logger.error(f"score_assignment: Error cleaning up image: {str(cleanup_error)}")

                return new_assignment

        finally:
            # Ensure cleanup of temporary directory
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            except Exception as cleanup_error:
                logger.error(f"score_assignment: Error cleaning up temp directory: {str(cleanup_error)}")
    except Exception as e:
        logger.error(f"score_assignment: Unhandled error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing assignment: {str(e)}")

