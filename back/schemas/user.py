from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class UserBase(BaseModel):
    tg_id: str = Field(..., description="Идентификатор пользователя в Telegram (tg_id)")
    username: Optional[str] = Field(None, description="Уникальное имя пользователя в системе")


class UserCreate(UserBase):
    pass


class AssignmentBase(BaseModel):
    assignment_id: int
    task_id: int
    mark: Optional[int] = None
    status: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        orm_mode = True


class User(UserBase):
    auth_timestamp: datetime = Field(..., description="Время, когда пользователь начал взаимодействовать с ботом")
    assignments: List[AssignmentBase] = Field(default=[], description="Список заданий, связанных с пользователем")

    class Config:
        orm_mode = True
