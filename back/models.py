from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    tg_id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    auth_timestamp = Column(DateTime, default=datetime.utcnow)
    assignments = relationship("Assignment", back_populates="user")

class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, autoincrement=True)
    task_name = Column(String, nullable=False)
    task_status = Column(Enum("prod", "test", "deleted", name="task_status_enum"), nullable=False)
    task_description = Column(Text)
    task_type = Column(String)
    task_data = Column(String)
    requirements = Column(Text)
    task_data_admin = Column(String)
    check_solution_file = Column(String)

    assignments = relationship("Assignment", back_populates="task")

class Assignment(Base):
    __tablename__ = "assignments"

    assignment_id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    task_id = Column(Integer, ForeignKey("tasks.task_id"), nullable=False)
    tg_id = Column(String, ForeignKey("users.tg_id"), nullable=False)
    mark = Column(Integer, CheckConstraint("mark >= 0 AND mark <= 100"), nullable=True)
    status = Column(Enum("ok", "error", name="assignment_status_enum"), nullable=False)
    error_message = Column(Text)
    assignment_file = Column(String)

    user = relationship("User", back_populates="assignments")
    task = relationship("Task", back_populates="assignments")
