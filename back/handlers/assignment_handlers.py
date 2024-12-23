import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func  # Добавить импорт func
from back.database import get_db
from back.models import Assignment as AssignmentModel
from back.schemas.assignment import AssignmentCreate, Assignment as AssignmentSchema

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=list[AssignmentSchema])
async def read_assignments(db: Session = Depends(get_db)):
    try:
        assignments = db.query(AssignmentModel).all()
        logger.info("Retrieved all assignments")
        return assignments
    except Exception as e:
        logger.error(f"Error retrieving assignments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving assignments: {str(e)}")

@router.post("/submit_assignment", response_model=dict)
async def submit_assignment(assignment: AssignmentCreate, db: Session = Depends(get_db)):
    try:
        new_assignment = AssignmentModel(**assignment.dict())
        db.add(new_assignment)
        db.commit()
        db.refresh(new_assignment)
        logger.info(f"Submitted new assignment with ID {new_assignment.assignment_id}")
        return {"is_ok": True, "err_message": ""}
    except Exception as e:
        logger.error(f"Error submitting assignment: {str(e)}")
        return {"is_ok": False, "err_message": str(e)}

@router.get("/get_assignment/{assignment_id}", response_model=AssignmentSchema)
async def read_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(AssignmentModel).filter(AssignmentModel.assignment_id == assignment_id).first()
    if not assignment:
        logger.warning(f"Assignment with ID {assignment_id} not found")
        raise HTTPException(status_code=404, detail="Assignment not found")
    logger.info(f"Retrieved assignment with ID {assignment_id}")
    return assignment

@router.get("/get_results/{tg_id}", response_model=list[AssignmentSchema])
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

        logger.info(f"Retrieved best results for tg_id {tg_id}")
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
        logger.error(f"Error retrieving best results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving best results: {str(e)}")

@router.get("/get_assignments/{task_id}/{tg_id}", response_model=list[AssignmentSchema])
async def get_user_assignments_by_task(task_id: int, tg_id: str, db: Session = Depends(get_db)):
    try:
        assignments = (
            db.query(AssignmentModel)
            .filter(AssignmentModel.task_id == task_id, AssignmentModel.tg_id == tg_id)
            .all()
        )
        if not assignments:
            logger.warning(f"No assignments found for task_id={task_id} and tg_id={tg_id}")
            raise HTTPException(
                status_code=404,
                detail=f"No assignments found for task_id={task_id} and tg_id={tg_id}"
            )

        logger.info(f"Retrieved assignments for task_id={task_id} and tg_id={tg_id}")
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
        logger.error(f"Error retrieving assignments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving assignments: {str(e)}")
