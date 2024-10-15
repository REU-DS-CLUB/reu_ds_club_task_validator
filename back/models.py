from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    telegram_login = Column(String, primary_key=True)
    auth_timestamp = Column(DateTime, default=datetime.utcnow)
    available_tasks = Column(String, default="[1]")  

class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, autoincrement=True)
    task_name = Column(String)
    task_description = Column(String)
    task_type = Column(String)
    task_data = Column(String)
    task_sample_submission = Column(String)

class Assignment(Base):
    __tablename__ = "assignments"

    assignment_id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    task_id = Column(Integer, ForeignKey('tasks.task_id'))
    telegram_login = Column(String, ForeignKey('users.telegram_login'))
    mark = Column(Integer)
    status = Column(String)
    error_message = Column(String)
    assignment_file = Column(String)

    user = relationship("User", back_populates="assignments")
    task = relationship("Task", back_populates="assignments")

User.assignments = relationship("Assignment", back_populates="user")
Task.assignments = relationship("Assignment", back_populates="task")
