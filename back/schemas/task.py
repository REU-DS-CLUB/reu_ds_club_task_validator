from pydantic import BaseModel, validator
from typing import Optional

class TaskBase(BaseModel):
    task_name: str
    task_status: str
    task_description: str
    task_type: str
    task_data: str
    requirements: str

    @validator('task_status')
    def validate_task_status(cls, v):
        allowed_statuses = ["prod", "test", "deleted"]
        if v not in allowed_statuses:
            raise ValueError(f"Invalid task_status: {v}. Must be one of {allowed_statuses}")
        return v

    class Config:
        orm_mode = True

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    task_name: Optional[str] = None
    task_status: Optional[str] = None
    task_description: Optional[str] = None
    task_type: Optional[str] = None
    task_data: Optional[str] = None
    requirements: Optional[str] = None

    @validator('task_status')
    def validate_task_status(cls, v):
        allowed_statuses = ["prod", "test", "deleted"]
        if v is not None and v not in allowed_statuses:
            raise ValueError(f"Invalid task_status: {v}. Must be one of {allowed_statuses}")
        return v

    class Config:
        orm_mode = True

class Task(TaskBase):
    task_id: int
