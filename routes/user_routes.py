from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.database import get_db
from middleware.auth import get_current_user
from controllers.user_controller import me, get_all_users, get_user_by_id
from models.user import User
from schemas.user_schema import User as UserSchema, UserListResponse, UserDetailResponse

router = APIRouter()

@router.get("/", response_model=UserListResponse)
async def read_users(db: Session = Depends(get_db)):
    return await get_all_users(db)

@router.get("/me", response_model=UserSchema)
def get_me(current_user: User = Depends(get_current_user)):
    return me(current_user)

@router.get("/{user_id}", response_model=UserDetailResponse)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    # Optionally, you can use current_user for authorization or logging
    return await get_user_by_id(db, user_id)
