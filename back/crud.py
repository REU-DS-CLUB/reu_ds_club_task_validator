from sqlalchemy.orm import Session
from sqlalchemy import func
from back.models import Task as TaskModel, Assignment as AssignmentModel, User as UserModel
from back.schemas.task import TaskCreate, TaskUpdate
from back.schemas.assignment import AssignmentCreate
from back.schemas.user import UserCreate
from datetime import datetime

# Task CRUD operations
def get_tasks(db: Session):
    return db.query(TaskModel).all()

def get_task(db: Session, task_id: int):
    return db.query(TaskModel).filter(TaskModel.task_id == task_id).first()

def create_task(db: Session, task: TaskCreate):
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
    return db_task

def update_task(db: Session, task_id: int, task: TaskUpdate):
    db_task = db.query(TaskModel).filter(TaskModel.task_id == task_id).first()
    if db_task:
        for key, value in task.dict(exclude_unset=True).items():
            setattr(db_task, key, value)
        db.commit()
        db.refresh(db_task)
    return db_task

# Assignment CRUD operations
def get_assignments(db: Session):
    return db.query(AssignmentModel).all()

def get_assignment(db: Session, assignment_id: int):
    return db.query(AssignmentModel).filter(AssignmentModel.assignment_id == assignment_id).first()

def create_assignment(db: Session, assignment: AssignmentCreate):
    new_assignment = AssignmentModel(**assignment.dict())
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return new_assignment

def get_best_results(db: Session, tg_id: str):
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

    return results

def get_user_assignments_by_task(db: Session, task_id: int, tg_id: str):
    return db.query(AssignmentModel).filter(AssignmentModel.task_id == task_id, AssignmentModel.tg_id == tg_id).all()

# User CRUD operations
def get_users(db: Session):
    return db.query(UserModel).all()

def create_user(db: Session, user: UserCreate):
    new_user = UserModel(
        tg_id=user.tg_id,
        username=user.username,
        auth_timestamp=datetime.utcnow(),
        is_banned=user.is_banned  # New field
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user_by_tg_id(db: Session, tg_id: str):
    return db.query(UserModel).filter(UserModel.tg_id == tg_id).first()
