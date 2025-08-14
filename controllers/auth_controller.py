from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from utils.security import verify_password, create_access_token, hash_password
from models.user import User

def register(db: Session, email: str, name: str, password: str) -> dict:
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(password)
    
    try:
        # Attempt standard ORM insert
        user = User(email=email, name=name, password_hash=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception as e:
        print(f"ORM creation failed, falling back to manual ID generation. Error: {e}")
        db.rollback()
        
        # Fallback to manual ID generation
        try:
            result = db.execute(text("SELECT COALESCE(MAX(id), 0) + 1 FROM users"))
            next_id = result.scalar_one()
            
            insert_sql = text("""
                INSERT INTO users (id, email, name, password_hash) 
                VALUES (:id, :email, :name, :password_hash)
            """)
            
            db.execute(insert_sql, {
                'id': next_id,
                'email': email,
                'name': name,
                'password_hash': hashed_password
            })
            
            db.commit()
            
            user = db.query(User).filter(User.id == next_id).first()
        except Exception as manual_e:
            print(f"Manual ID generation also failed. Error: {manual_e}")
            raise HTTPException(status_code=500, detail="Failed to create user using fallback method.")

    if not user or user.id is None:
        raise HTTPException(status_code=500, detail="Failed to create or retrieve user after creation.")

    return {"id": user.id, "email": user.email, "name": user.name}

def login(db: Session, email: str, password: str) -> dict:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(sub=user.email)
    return {"message": "Login successful", "access_token": token, "token_type": "bearer"}
