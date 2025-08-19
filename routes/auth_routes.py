from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from config.database import get_db
from controllers.auth_controller import register, login, forgot_password, reset_password, update_password
from schemas.auth_schema import (
    ForgotPasswordRequest, ResetPasswordRequest, RegisterIn, LoginIn, UpdatePasswordIn
)
from middleware.auth import get_current_user
from models.user import User

router = APIRouter()

@router.post("/register")
def register_user(body: RegisterIn, db: Session = Depends(get_db)):
    return register(db, body.email, body.name, body.password)

@router.post("/login")
def login_user(body: LoginIn, db: Session = Depends(get_db)):
    return login(db, body.email, body.password)

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def request_password_reset(body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return forgot_password(db, body.email)

@router.post("/reset-password", status_code=status.HTTP_200_OK)
def handle_password_reset(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    return reset_password(db, body.token, body.new_password)

@router.put("/update-password", status_code=status.HTTP_200_OK)
def update_user_password(
    body: UpdatePasswordIn, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return update_password(db, current_user, body.current_password, body.new_password)
