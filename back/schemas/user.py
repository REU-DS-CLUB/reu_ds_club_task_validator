from pydantic import BaseModel
from datetime import datetime
from typing import List

class UserBase(BaseModel):
    telegram_login: str
    available_tasks: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    auth_timestamp: datetime
    assignments: List[int] = []

    class Config:
        orm_mode = True
