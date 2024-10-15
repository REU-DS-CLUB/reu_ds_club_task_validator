from sqlalchemy.orm import Session
from .models import User, Task, Assignment

def get_user(db: Session, telegram_login: str):
    return db.query(User).filter(User.telegram_login == telegram_login).first()

def create_user(db: Session, user: User):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.task_id == task_id).first()

def create_task(db: Session, task: Task):
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def get_assignment(db: Session, assignment_id: int):
    return db.query(Assignment).filter(Assignment.assignment_id == assignment_id).first()

def create_assignment(db: Session, assignment: Assignment):
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment