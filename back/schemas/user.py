from pydantic import BaseModel
from datetime import datetime
from typing import List

class AssignmentBase(BaseModel):
    assignment_id: int  # Include only the ID of the assignments

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    tg_id: str
    available_tasks: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    auth_timestamp: datetime
    assignments: List[AssignmentBase] = []  # Expect assignment IDs here

    class Config:
        orm_mode = True
