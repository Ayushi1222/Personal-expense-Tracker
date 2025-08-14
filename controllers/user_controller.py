from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.user import User

def me(user: User) -> User:
    return user

def get_all_users(db: Session) -> list[User]:
    return db.query(User).all()

def get_user_by_id(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
