import asyncio
from datetime import date, datetime, timezone
from typing import Optional
from sqlalchemy import func, text, select
from sqlalchemy.orm import Session
from models.expense import Expense
from models.user import User
from models.budget import Budget
from fastapi import HTTPException

async def list_expenses(
    db: Session, 
    user: User, 
    page: int = 1, 
    per_page: int = 20,
    category_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> dict:
    def _list():
        q = select(Expense).filter(Expense.user_id == user.id)

        if category_id:
            q = q.filter(Expense.category_id == category_id)
        
        if start_date:
            q = q.filter(Expense.date >= start_date)

        if end_date:
            q = q.filter(Expense.date <= end_date)

        total = db.execute(select(func.count()).select_from(q.subquery())).scalar_one() # pylint: disable=not-callable

        q = q.order_by(Expense.date.desc(), Expense.id.desc())
        
        items = db.execute(q.offset((page - 1) * per_page).limit(per_page)).scalars().all()
        
        return {
            "title": "Expense List",
            "data": {
                "total": total, 
                "page": page, 
                "per_page": per_page, 
                "items": items
            }
        }
    return await asyncio.to_thread(_list)

async def create_expense(db: Session, user: User, amount: float, date_: date, note: str | None, category_id: int | None):
    def _create():
        try:
            max_id_result = db.execute(text("SELECT COALESCE(MAX(id), 0) FROM expenses")).scalar_one()
            next_id = max_id_result + 1

            now = datetime.now(timezone.utc)
            db.execute(
                text("""
                    INSERT INTO expenses (id, user_id, category_id, amount, note, date, created_at, updated_at) 
                    VALUES (:id, :user_id, :category_id, :amount, :note, :date, :created_at, :updated_at)
                """),
                {
                    'id': next_id,
                    'user_id': user.id,
                    'category_id': category_id,
                    'amount': amount,
                    'note': note,
                    'date': date_,
                    'created_at': now,
                    'updated_at': now
                }
            )
            db.commit()

            new_expense = db.execute(select(Expense).filter(Expense.id == next_id)).scalars().first()
            
            alert_message = None
            budget_status = None

            if category_id:
                month_str = date_.strftime('%Y-%m')
                
                budget = db.execute(select(Budget).filter(
                    Budget.user_id == user.id,
                    Budget.category_id == category_id,
                    Budget.month == month_str
                )).scalars().first()

                if budget:
                    if db.bind.url.get_backend_name() == "sqlite":
                        date_filter = func.strftime('%Y-%m', Expense.date) == month_str
                    else:
                        date_filter = func.to_char(Expense.date, 'YYYY-MM') == month_str

                    total_spent_result = db.execute(select(func.sum(Expense.amount)).filter(
                        Expense.user_id == user.id,
                        Expense.category_id == category_id,
                        date_filter
                    )).first()
                    
                    total_spent = total_spent_result[0] if total_spent_result and total_spent_result[0] is not None else 0.0

                    if total_spent > budget.amount:
                        overage = total_spent - budget.amount
                        alert_message = f"Warning: You have exceeded your budget for this category by ${overage:,.2f}."
                        budget_status = "over"
                    elif total_spent / budget.amount >= 0.8:
                        alert_message = "Warning: You have used 80% or more of your budget for this category."
                        budget_status = "near"

            return {"expense": new_expense, "alert": alert_message, "budget_status": budget_status}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create expense: {e}") from e
    return await asyncio.to_thread(_create)

async def update_expense(db: Session, user: User, expense_id: int, amount: float, date_: date, note: str | None, category_id: int | None):
    def _update():
        expense = db.execute(select(Expense).filter(Expense.id == expense_id, Expense.user_id == user.id)).scalars().first()
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")

        expense.amount = amount
        expense.date = date_
        expense.note = note
        expense.category_id = category_id
        db.commit()
        db.refresh(expense)
        return expense
    return await asyncio.to_thread(_update)

async def delete_expense(db: Session, user: User, expense_id: int):
    def _delete():
        expense = db.execute(select(Expense).filter(Expense.id == expense_id, Expense.user_id == user.id)).scalars().first()
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")
        
        db.delete(expense)
        db.commit()
        return {"message": "Expense deleted successfully"}
    return await asyncio.to_thread(_delete)