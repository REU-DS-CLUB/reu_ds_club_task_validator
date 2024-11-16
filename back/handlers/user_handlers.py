from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from back.database import get_db
from back.schemas.user import UserCreate, User as UserSchema
from back.models import User as UserModel
from back.crud import create_user, get_user

router = APIRouter()

@router.get("/", response_model=list[UserSchema])
async def read_users(db: Session = Depends(get_db)):
    users = db.query(UserModel).all()
    return users

@router.post("/", response_model=UserSchema)
async def create_user_handler(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, user.tg_id)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return create_user(db, user)
