from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException
from models.budget import Budget
from models.user import User

def create_budget(db: Session, user: User, month: str, amount: float, category_id: int):
    exists = db.query(Budget).filter(
        Budget.user_id == user.id, 
        Budget.month == month,
        Budget.category_id == category_id
    ).first()
    if exists:
        raise HTTPException(
            status_code=409,
            detail=f"Budget for this category in month {month} already exists. Use PUT /budgets/{exists.id} to update."
        )
    
    try:
        # Manual ID generation
        max_id_result = db.execute(text("SELECT COALESCE(MAX(id), 0) FROM budgets")).scalar_one()
        next_id = max_id_result + 1

        db.execute(
            text("INSERT INTO budgets (id, user_id, category_id, month, amount) VALUES (:id, :user_id, :category_id, :month, :amount)"),
            {'id': next_id, 'user_id': user.id, 'category_id': category_id, 'month': month, 'amount': amount}
        )
        db.commit()

        new_budget = db.query(Budget).filter(Budget.id == next_id).first()
        return new_budget
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create budget: {e}")

def update_budget(db: Session, user: User, budget_id: int, month: str, amount: float, category_id: int):
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user.id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    # Check if updating would cause a conflict with another existing budget
    conflict_exists = db.query(Budget).filter(
        Budget.user_id == user.id,
        Budget.month == month,
        Budget.category_id == category_id,
        Budget.id != budget_id
    ).first()
    if conflict_exists:
        raise HTTPException(
            status_code=409,
            detail=f"Another budget for this category in month {month} already exists."
        )

    budget.month = month
    budget.amount = amount
    budget.category_id = category_id
    db.commit()
    db.refresh(budget)
    return budget

def get_budget(db: Session, user: User, month: str):
    budgets = db.query(Budget).filter(Budget.user_id == user.id, Budget.month == month).all()
    if not budgets:
        raise HTTPException(status_code=404, detail=f"No budgets found for month {month}")
    return budgets

def list_budgets(db: Session, user: User):
    return db.query(Budget).filter(Budget.user_id == user.id).order_by(Budget.month.desc()).all()

def delete_budget(db: Session, user: User, budget_id: int):
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user.id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found or access denied")
    
    db.delete(budget)
    db.commit()
    return