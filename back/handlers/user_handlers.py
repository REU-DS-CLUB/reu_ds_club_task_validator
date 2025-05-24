from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from back.utils.database import get_db
from back.utils.models import User as UserModel
from back.schemas.user import UserCreate, User as UserSchema

router = APIRouter()


@router.get("/get_users", response_model=list[UserSchema])
async def read_users(db: Session = Depends(get_db)):
    try:
        users = db.query(UserModel).all()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving users: {str(e)}")


@router.post("/add_user", response_model=dict)
async def add_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        if db.query(UserModel).filter(UserModel.tg_id == user.tg_id).first():
            return {"is_ok": False, "err_message": "User already exists"}
        new_user = UserModel(**user.dict())
        db.add(new_user)
        db.commit()
        return {"is_ok": True, "err_message": ""}
    except Exception as e:
        return {"is_ok": False, "err_message": str(e)}


@router.get("/is_newbie/{tg_id}", response_model=dict)
async def is_newbie(tg_id: str, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.tg_id == tg_id).first()
    return {"is_newbie": user is None}
