from pydantic import BaseModel, field_validator
from enum import Enum
from typing import Optional


class TaskStatus(str, Enum):
    PROD = "prod"
    TEST = "test"
    DELETED = "deleted"


class TaskType(str, Enum):
    CSV = "csv"
    EXECUTABLE = "executable"


class TaskBase(BaseModel):
    task_num: int
    task_name: str
    task_status: TaskStatus
    task_description: Optional[str] = None
    task_type: TaskType
    task_data: str
    task_data_admin: Optional[str] = None

    @field_validator('task_num')
    def validate_task_num(cls, v):
        if v <= 0:
            raise ValueError('Task number must be positive')
        return v

    @field_validator('task_name')
    def validate_task_name(cls, v):
        if len(v) > 100:
            raise ValueError('Task name must be less than 100 characters')
        return v

    @field_validator('task_data')
    def validate_task_data(cls, v):
        if not v.endswith(('.csv')):
            raise ValueError('Task data must be a path to .csv file')
        return v


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    task_num: Optional[int] = None
    task_name: Optional[str] = None
    task_status: Optional[TaskStatus] = None
    task_description: Optional[str] = None
    task_type: Optional[TaskType] = None
    task_data: Optional[str] = None
    task_data_admin: Optional[str] = None

    _validate_task_name = field_validator('task_name')(TaskBase.validate_task_name)
    _validate_task_data = field_validator('task_data')(TaskBase.validate_task_data)


class Task(TaskBase):
    task_id: int

    class Config:
        from_attributes = True
