from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AssignmentBase(BaseModel):
    task_id: int
    telegram_login: str
    mark: Optional[int] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    assignment_file: Optional[str] = None

class AssignmentCreate(AssignmentBase):
    pass

class Assignment(AssignmentBase):
    assignment_id: int
    timestamp: datetime

    class Config:
        orm_mode = True
