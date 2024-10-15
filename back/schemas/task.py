from pydantic import BaseModel
from typing import Optional

class TaskBase(BaseModel):
    task_name: str
    task_description: str
    task_type: str
    task_data: str
    task_sample_submission: str

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    task_id: int

    class Config:
        orm_mode = True
