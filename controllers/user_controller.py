from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.user import User
from utils.security import verify_password, get_password_hash

def me(user: User) -> User:
    return user

def get_all_users(db: Session) -> dict:
    users = db.query(User).all()
    return {"title": "All Users", "data": users}

def get_user_by_id(db: Session, user_id: int) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"title": "User Details", "data": user}
