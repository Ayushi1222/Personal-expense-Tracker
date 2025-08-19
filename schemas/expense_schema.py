from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional

class ExpenseBase(BaseModel):
    amount: float
    date: date
    note: Optional[str] = None
    category_id: Optional[int] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseInDB(ExpenseBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PaginatedExpenseResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: List[ExpenseInDB]

class ExpenseResponse(BaseModel):
    title: str
    data: PaginatedExpenseResponse
