from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional
import re
from back.schemas.assignment import AssignmentBase  # Использовать существующую схему


class UserBase(BaseModel):
    tg_id: str = Field(..., description="Идентификатор пользователя в Telegram (tg_id)")
    username: Optional[str] = Field(None, description="Уникальное имя пользователя в системе")

    @field_validator('tg_id')
    def validate_tg_id(cls, v):
        if not re.match(r'^[0-9]{6,}$', v):
            raise ValueError('Invalid Telegram ID format')
        return v

    @field_validator('username')
    def validate_username(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9_]{4,32}$', v):
            raise ValueError('Invalid username format')
        return v


class UserCreate(UserBase):
    pass


class User(UserBase):
    auth_timestamp: datetime = Field(..., description="Время, когда пользователь начал взаимодействовать с ботом")
    assignments: List[AssignmentBase] = Field(
        default=[], 
        description="Список заданий, связанных с пользователем",
        max_length=1000  # Ограничение на количество заданий
    )

    class Config:
        from_attributes = True
