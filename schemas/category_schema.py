from pydantic import BaseModel, Field
from typing import Optional

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    user_id: int
    total_expenses_formatted: Optional[str] = Field(None, alias="total_expenses")
    current_month_budget: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
