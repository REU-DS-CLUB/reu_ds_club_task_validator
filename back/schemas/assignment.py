from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional

class AssignmentBase(BaseModel):
    task_id: int
    tg_id: str
    mark: Optional[int] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    assignment_file: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        if v is None:
            return v
        allowed_statuses = ["ok", "error"]
        if v.lower() not in allowed_statuses:
            raise ValueError(f'Invalid status for assignment: {v}. Must be one of {allowed_statuses}')
        return v
    
    class Config:
        orm_mode = True

class AssignmentCreate(AssignmentBase):
    pass

class Assignment(AssignmentBase):
    # assignment_id: int
    timestamp: datetime

    class Config:
        orm_mode = True
