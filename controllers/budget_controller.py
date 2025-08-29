import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import text, select
from fastapi import HTTPException
from models.budget import Budget
from models.user import User
from datetime import datetime, timezone

async def create_budget(db: Session, user: User, month: str, amount: float, category_id: int):
    def _create():
        exists = db.execute(select(Budget).filter(
            Budget.user_id == user.id, 
            Budget.month == month,
            Budget.category_id == category_id
        )).scalars().first()
        if exists:
            raise HTTPException(
                status_code=409,
                detail=f"Budget for this category in month {month} already exists. Use PUT /budgets/{exists.id} to update."
            )
        
        try:
            max_id_result = db.execute(text("SELECT COALESCE(MAX(id), 0) FROM budgets")).scalar_one()
            next_id = max_id_result + 1

            now = datetime.now(timezone.utc)
            db.execute(
                text("INSERT INTO budgets (id, user_id, category_id, month, amount, created_at, updated_at) VALUES (:id, :user_id, :category_id, :month, :amount, :created_at, :updated_at)"),
                {'id': next_id, 'user_id': user.id, 'category_id': category_id, 'month': month, 'amount': amount, 'created_at': now, 'updated_at': now}
            )
            db.commit()

            new_budget = db.execute(select(Budget).filter(Budget.id == next_id)).scalars().first()
            return new_budget
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create budget: {e}") from e
    return await asyncio.to_thread(_create)

async def update_budget(db: Session, user: User, budget_id: int, month: str, amount: float, category_id: int):
    def _update():
        budget = db.execute(select(Budget).filter(Budget.id == budget_id, Budget.user_id == user.id)).scalars().first()
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")

        conflict_exists = db.execute(select(Budget).filter(
            Budget.user_id == user.id,
            Budget.month == month,
            Budget.category_id == category_id,
            Budget.id != budget_id
        )).scalars().first()
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
    return await asyncio.to_thread(_update)

async def get_budget(db: Session, user: User, month: str):
    def _get():
        budgets = db.execute(select(Budget).filter(Budget.user_id == user.id, Budget.month == month)).scalars().all()
        if not budgets:
            raise HTTPException(status_code=404, detail=f"No budgets found for month {month}")
        
        formatted_budgets = {
            budget.category_id: {
                "id": budget.id,
                "user_id": budget.user_id,
                "category_id": budget.category_id,
                "month": budget.month,
                "amount": budget.amount,
                "created_at": budget.created_at.isoformat(),
                "updated_at": budget.updated_at.isoformat()
            } for budget in budgets
        }
        return formatted_budgets
    return await asyncio.to_thread(_get)

async def list_budgets(db: Session, user: User):
    def _list():
        budgets = db.execute(select(Budget).filter(Budget.user_id == user.id).order_by(Budget.month.desc())).scalars().all()
        
        budgets_by_month = {}
        for budget in budgets:
            if budget.month not in budgets_by_month:
                budgets_by_month[budget.month] = {}
            budgets_by_month[budget.month][budget.category_id] = budget
            
        return budgets_by_month
    return await asyncio.to_thread(_list)

async def delete_budget(db: Session, user: User, budget_id: int):
    def _delete():
        budget = db.execute(select(Budget).filter(Budget.id == budget_id, Budget.user_id == user.id)).scalars().first()
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")
        
        db.delete(budget)
        db.commit()
        return {"message": "Budget deleted successfully"}
    return await asyncio.to_thread(_delete)