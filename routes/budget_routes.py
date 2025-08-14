from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from config.database import get_db
from middleware.auth import get_current_user
from controllers.budget_controller import create_budget, get_budget, list_budgets, update_budget, delete_budget
from models.user import User
from schemas.budget_schema import Budget as BudgetSchema

router = APIRouter()

class BudgetIn(BaseModel):
    month: str = Field(pattern=r"^\d{4}-\d{2}$")  # YYYY-MM
    amount: float = Field(gt=0)
    category_id: int

@router.post("/", response_model=BudgetSchema, status_code=status.HTTP_201_CREATED)
def add_budget(body: BudgetIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_budget(db, current_user, body.month, body.amount, body.category_id)

@router.put("/{budget_id}", response_model=BudgetSchema)
def edit_budget(budget_id: int, body: BudgetIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return update_budget(db, current_user, budget_id, body.month, body.amount, body.category_id)

@router.get("/", response_model=list[BudgetSchema])
def read_all_budgets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_budgets(db, current_user)

@router.get("/{month}", response_model=list[BudgetSchema])
def read_budget(month: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_budget(db, current_user, month)

@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_budget(budget_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    delete_budget(db, current_user, budget_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
