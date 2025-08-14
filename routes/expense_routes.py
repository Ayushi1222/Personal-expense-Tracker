from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from config.database import get_db
from middleware.auth import get_current_user
from controllers.expense_controller import list_expenses, create_expense, delete_expense, monthly_summary, monthly_summary_by_category
from models.user import User

router = APIRouter()

class ExpenseIn(BaseModel):
    amount: float = Field(gt=0)
    date: date
    note: str | None = Field(default=None, max_length=255)
    category_id: int | None = None

@router.get("")
def get_expenses(
    page: int = Query(1, ge=1), 
    per_page: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    start_date: Optional[date] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    return list_expenses(db, current_user, page, per_page, category_id, start_date, end_date)

@router.post("")
def add_expense(body: ExpenseIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_expense(db, current_user, body.amount, body.date, body.note, body.category_id)

@router.delete("/{expense_id}")
def remove_expense(expense_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return delete_expense(db, current_user, expense_id)

@router.get("/summary/{month}")
def get_monthly_summary(month: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return monthly_summary(db, current_user, month)

@router.get("/summary-by-category/{month}")
def get_monthly_summary_by_category(month: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return monthly_summary_by_category(db, current_user, month)