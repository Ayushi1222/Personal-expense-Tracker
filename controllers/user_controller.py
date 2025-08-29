import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status
from models.user import User

def me(user: User) -> User:
    return user

async def get_all_users(db: Session) -> dict:
    def _get_all():
        users = db.execute(select(User)).scalars().all()
        return {"title": "All Users", "data": users}
    return await asyncio.to_thread(_get_all)

async def get_user_by_id(db: Session, user_id: int) -> dict:
    def _get_by_id():
        user = db.execute(select(User).filter(User.id == user_id)).scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return {"title": "User Details", "data": user}
    return await asyncio.to_thread(_get_by_id)
