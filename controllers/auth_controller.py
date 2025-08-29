import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import text, select
import sqlalchemy.exc
from fastapi import HTTPException, status
from datetime import datetime, timezone
from utils.security import (
    verify_password, create_access_token, get_password_hash, 
    create_password_reset_token, verify_password_reset_token
)
from models.user import User

async def register(db: Session, email: str, name: str, password: str) -> dict:
    def _register():
        if db.execute(select(User).filter(User.email == email)).scalars().first():
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = get_password_hash(password)
        
        try:
            user = User(email=email, name=name, password_hash=hashed_password)
            db.add(user)
            db.commit()
            db.refresh(user)
        except sqlalchemy.exc.SQLAlchemyError as e:
            db.rollback()
            print(f"ORM creation failed, falling back to manual ID generation. Error: {e}")
            
            try:
                result = db.execute(text("SELECT COALESCE(MAX(id), 0) + 1 FROM users"))
                next_id = result.scalar_one()
                
                insert_sql = text("""
                    INSERT INTO users (id, email, name, password_hash, created_at, updated_at) 
                    VALUES (:id, :email, :name, :password_hash, :created_at, :updated_at)
                """)
                
                now = datetime.now(timezone.utc)
                db.execute(insert_sql, {
                    'id': next_id,
                    'email': email,
                    'name': name,
                    'password_hash': hashed_password,
                    'created_at': now,
                    'updated_at': now
                })
                db.commit()
                
                user = db.execute(select(User).filter(User.id == next_id)).scalars().first()
            except sqlalchemy.exc.SQLAlchemyError as manual_e:
                print(f"Manual ID generation also failed. Error: {manual_e}")
                raise HTTPException(status_code=500, detail="Failed to create user using fallback method.") from manual_e

        if not user or user.id is None:
            raise HTTPException(status_code=500, detail="Failed to create or retrieve user after creation.")
        
        return {"id": user.id, "email": user.email, "name": user.name}

    return await asyncio.to_thread(_register)

async def login(db: Session, email: str, password: str) -> dict:
    def _login():
        user = db.execute(select(User).filter(User.email == email)).scalars().first()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        token = create_access_token(data={"sub": user.email})
        return {"message": "Login successful", "access_token": token, "token_type": "bearer"}
    return await asyncio.to_thread(_login)

async def forgot_password(db: Session, email: str) -> dict:
    def _forgot_password():
        user = db.execute(select(User).filter(User.email == email)).scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        reset_token = create_password_reset_token(email=user.email)
        return {"message": "Password reset token generated", "reset_token": reset_token}
    return await asyncio.to_thread(_forgot_password)

async def reset_password(db: Session, token: str, new_password: str) -> dict:
    def _reset_password():
        email = verify_password_reset_token(token)
        if not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

        user = db.execute(select(User).filter(User.email == email)).scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        user.password_hash = get_password_hash(new_password)
        db.commit()

        return {"message": "Password has been reset successfully"}
    return await asyncio.to_thread(_reset_password)

async def update_password(db: Session, user: User, current_password: str, new_password: str):
    def _update_password():
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect current password")

        user.password_hash = get_password_hash(new_password)
        db.commit()
        return {"message": "Password updated successfully"}
    return await asyncio.to_thread(_update_password)
