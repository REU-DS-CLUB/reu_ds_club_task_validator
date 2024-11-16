from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from back.database import get_db
from back.schemas.assignment import AssignmentCreate, Assignment as AssignmentSchema
from back.models import Assignment as AssignmentModel
from back.crud import create_assignment, get_assignment

router = APIRouter()

@router.get("/", response_model=list[AssignmentSchema])
async def read_assignments(db: Session = Depends(get_db)):
    assignments = db.query(AssignmentModel).all()
    return assignments

@router.post("/", response_model=AssignmentSchema)
async def create_assignment_handler(assignment: AssignmentCreate, db: Session = Depends(get_db)):
    return create_assignment(db, assignment)
