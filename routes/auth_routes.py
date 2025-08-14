from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from config.database import get_db
from controllers.auth_controller import register, login

router = APIRouter()

class RegisterIn(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=6, max_length=128)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
def register_user(body: RegisterIn, db: Session = Depends(get_db)):
    return register(db, body.email, body.name, body.password)

@router.post("/login")
def login_user(body: LoginIn, db: Session = Depends(get_db)):
    return login(db, body.email, body.password)
