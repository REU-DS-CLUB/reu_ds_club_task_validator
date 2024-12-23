from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from back.database import get_db
from back.schemas.user import UserCreate, User as UserSchema
from back.crud import get_users, create_user, get_user_by_tg_id
import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/get_users", response_model=list[UserSchema])
async def read_users(db: Session = Depends(get_db)):
    try:
        users = get_users(db)
        logger.info("Retrieved all users")
        return users
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving users: {str(e)}")

@router.post("/add_user", response_model=UserSchema)
async def add_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        existing_user = get_user_by_tg_id(db, user.tg_id)
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        new_user = create_user(db, user)
        logger.info(f"User {user.username} added successfully")
        return UserSchema.from_orm(new_user)

    except Exception as e:
        db.rollback()
        logger.error(f"Error adding user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/is_newbie/{tg_id}", response_model=dict)
async def is_newbie(tg_id: str, db: Session = Depends(get_db)):
    user = get_user_by_tg_id(db, tg_id)
    return {"is_newbie": user is None}
