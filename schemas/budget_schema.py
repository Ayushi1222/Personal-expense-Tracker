from pydantic import BaseModel

class BudgetBase(BaseModel):
    month: str # "YYYY-MM"
    amount: float
    category_id: int

class BudgetCreate(BudgetBase):
    pass

class Budget(BudgetBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
