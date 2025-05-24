from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
import re


class AssignmentBase(BaseModel):
    task_id: int
    tg_id: str
    mark: Optional[int] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    assignment_file: Optional[str] = None

    @field_validator('status')
    def validate_status(cls, v):
        if v is None:
            return v
        allowed_statuses = ["ok", "error"]
        if v.lower() not in allowed_statuses:
            raise ValueError(f'Invalid status for assignment: {v}. Must be one of {allowed_statuses}')
        return v
    
    @field_validator('tg_id')
    def validate_tg_id(cls, v):
        if not re.match(r'^[0-9]{6,}$', v):
            raise ValueError('Invalid Telegram ID format')
        return v

    @field_validator('error_message')
    def validate_error_message(cls, v):
        if v and len(v) > 1000:
            return v[:1000]
        return v

    class Config:
        from_attributes = True


class Assignment(AssignmentBase):
    assignment_id: int
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    @field_validator('mark')
    def validate_mark(cls, v):
        if v is not None and (v < -1 or v > 100):
            raise ValueError('Mark must be between -1 and 100')
        return v

    class Config:
        from_attributes = True
