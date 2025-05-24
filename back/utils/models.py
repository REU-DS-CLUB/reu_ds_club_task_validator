from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum, CheckConstraint, Index
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum
from .database import Base


class User(Base):
    __tablename__ = "users"

    tg_id = Column(String, primary_key=True)
    username = Column(String, unique=True)
    auth_timestamp = Column(DateTime, default=datetime.utcnow)
    assignments = relationship("Assignment", back_populates="user")


class TaskStatus(enum.Enum):
    PROD = "prod"
    TEST = "test"
    DELETED = "deleted"


class TaskType(enum.Enum):
    CSV = "csv"
    EXECUTABLE = "executable"


class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, autoincrement=True)
    task_num = Column(Integer, CheckConstraint("task_num > 0"), nullable=False)
    task_name = Column(String, nullable=False)
    task_status = Column(Enum(TaskStatus), nullable=False)
    task_description = Column(Text, nullable=True)
    task_type = Column(Enum(TaskType), nullable=False)
    task_data = Column(String, nullable=False)
    task_data_admin = Column(String, nullable=True)

    assignments = relationship("Assignment", back_populates="task")


class Assignment(Base):
    __tablename__ = "assignments"

    assignment_id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    task_id = Column(Integer, ForeignKey("tasks.task_id"), nullable=False)
    tg_id = Column(String, ForeignKey("users.tg_id"), nullable=False)
    mark = Column(Integer, CheckConstraint("mark >= -1 AND mark <= 100"), nullable=False, comment="Mark from -1 (error) to 100")
    status = Column(Enum("ok", "error", name="assignment_status_enum"), nullable=False)
    error_message = Column(Text)
    assignment_file = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="assignments")
    task = relationship("Task", back_populates="assignments")

    __table_args__ = (
        Index('idx_task_user', 'task_id', 'tg_id'),
        Index('idx_timestamp', 'timestamp'),
    )
