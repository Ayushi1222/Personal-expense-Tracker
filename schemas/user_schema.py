from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class UserUpdatePassword(BaseModel):
    current_password: str
    new_password: str

class UserListResponse(BaseModel):
    title: str
    data: list[User]

class UserDetailResponse(BaseModel):
    title: str
    data: User
