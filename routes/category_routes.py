from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from config.database import get_db
from middleware.auth import get_current_user
from controllers.category_controller import list_categories, create_category, delete_category, update_category
from models.user import User
from schemas.category_schema import Category as CategorySchema

router = APIRouter()

class CategoryIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)

@router.get("", response_model=dict[int, CategorySchema])
async def get_categories(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await list_categories(db, current_user)

@router.post("", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def add_category(body: CategoryIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await create_category(db, current_user, body.name)

@router.put("/{category_id}", response_model=CategorySchema)
async def edit_category(category_id: int, body: CategoryIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await update_category(db, user=current_user, category_id=category_id, name=body.name)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_category(category_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await delete_category(db, current_user, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
