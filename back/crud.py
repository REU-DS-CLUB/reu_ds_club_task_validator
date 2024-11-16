from sqlalchemy.orm import Session
from .models import User, Task, Assignment
from .schemas.task import TaskCreate

def get_user(db: Session, tg_id: str):
    return db.query(User).filter(User.tg_id == tg_id).first()

def create_user(db: Session, user: User):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.task_id == task_id).first()

def create_task(db: Session, task: TaskCreate):
    db_task = Task(
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

def get_assignment(db: Session, assignment_id: int):
    return db.query(Assignment).filter(Assignment.assignment_id == assignment_id).first()

def create_assignment(db: Session, assignment: Assignment):
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment