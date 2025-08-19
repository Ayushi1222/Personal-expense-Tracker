from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from config.database import get_db
from middleware.auth import get_current_user
from controllers.user_controller import me, get_all_users, get_user_by_id
from controllers.auth_controller import update_password
from models.user import User
from schemas.user_schema import User as UserSchema, UserUpdatePassword, UserListResponse, UserDetailResponse

router = APIRouter()

@router.get("/", response_model=UserListResponse)
def read_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_all_users(db)

@router.get("/me", response_model=UserSchema)
def get_me(current_user: User = Depends(get_current_user)):
    return me(current_user)

@router.get("/{user_id}", response_model=UserDetailResponse)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_user_by_id(db, user_id)
