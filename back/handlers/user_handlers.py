from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from back.database import get_db
from back.models import User as UserModel
from back.schemas.user import UserCreate, User as UserSchema
import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/get_users", response_model=list[UserSchema])
async def read_users(db: Session = Depends(get_db)):
    try:
        users = db.query(UserModel).all()
        return users
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving users: {str(e)}")

@router.post("/add_user", response_model=UserSchema)
async def add_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(UserModel).filter(UserModel.tg_id == user.tg_id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        new_user = UserModel(
            tg_id=user.tg_id,
            username=user.username,
            auth_timestamp=datetime.utcnow()
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"User {user.username} added successfully")
        return UserSchema.from_orm(new_user)

    except Exception as e:
        db.rollback()
        logger.error(f"Error adding user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/is_newbie/{tg_id}", response_model=dict)
async def is_newbie(tg_id: str, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.tg_id == tg_id).first()
    return {"is_newbie": user is None}
