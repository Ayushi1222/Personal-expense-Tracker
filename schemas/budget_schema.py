from pydantic import BaseModel, Field, RootModel
from typing import Optional
from datetime import datetime

class BudgetBase(BaseModel):
    month: str # "YYYY-MM"
    amount: float
    category_id: int

class BudgetCreate(BudgetBase):
    pass

class Budget(BudgetBase):
    id: int
    user_id: int
    category_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BudgetListResponse(BaseModel):
    title: str
    data: list[Budget]

class BudgetDictResponse(RootModel):
    root: dict[int, Budget]

class AllBudgetsResponse(RootModel):
    root: dict[str, dict[int, Budget]]
