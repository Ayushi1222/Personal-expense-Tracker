from pydantic import BaseModel
from datetime import date

class ExpenseBase(BaseModel):
    amount: float
    note: str | None = None
    date: date

class ExpenseCreate(ExpenseBase):
    category_id: int | None = None

class Expense(ExpenseBase):
    id: int
    user_id: int
    category_id: int | None = None

    class Config:
        orm_mode = True
