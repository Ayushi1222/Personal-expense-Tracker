from datetime import date, datetime, timezone
from typing import Optional
from sqlalchemy import func, text
from sqlalchemy.orm import Session
from models.expense import Expense
from models.user import User
from models.budget import Budget
from fastapi import HTTPException

def list_expenses(
    db: Session, 
    user: User, 
    page: int = 1, 
    per_page: int = 20,
    category_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> dict:
    q = db.query(Expense).filter(Expense.user_id == user.id)

    if category_id:
        q = q.filter(Expense.category_id == category_id)
    
    if start_date:
        q = q.filter(Expense.date >= start_date)

    if end_date:
        q = q.filter(Expense.date <= end_date)

    q = q.order_by(Expense.date.desc(), Expense.id.desc())
    
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        "title": "Expense List",
        "data": {
            "total": total, 
            "page": page, 
            "per_page": per_page, 
            "items": items
        }
    }

def create_expense(db: Session, user: User, amount: float, date_: date, note: str | None, category_id: int | None):
    try:
        # Manual ID generation
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

        new_expense = db.query(Expense).filter(Expense.id == next_id).first()
        
        alert_message = None
        budget_status = None

        if category_id:
            month_str = date_.strftime('%Y-%m')
            
            budget = db.query(Budget).filter(
                Budget.user_id == user.id,
                Budget.category_id == category_id,
                Budget.month == month_str
            ).first()

            if budget:
                if db.bind.url.get_backend_name() == "sqlite":
                    date_filter = func.strftime('%Y-%m', Expense.date) == month_str
                else:  # Snowflake/Postgres
                    date_filter = func.to_char(Expense.date, 'YYYY-MM') == month_str

                total_spent_result = db.query(func.sum(Expense.amount)).filter(
                    Expense.user_id == user.id,
                    Expense.category_id == category_id,
                    date_filter
                ).first()
                
                total_spent = total_spent_result[0] if total_spent_result and total_spent_result[0] is not None else 0.0

                percentage_spent = (total_spent / budget.amount) * 100 if budget.amount > 0 else 0

                thresholds = [100, 90, 80]
                for t in thresholds:
                    if percentage_spent >= t:
                        alert_message = f"Warning: You have spent {percentage_spent:.2f}% of your budget for this category."
                        break
                
                budget_status = {
                    "budget_amount": budget.amount,
                    "total_spent": total_spent,
                    "percentage_spent": percentage_spent,
                    "month": month_str,
                    "alert": alert_message
                }

        return {"expense": new_expense, "budget_status": budget_status}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create expense: {e}")

def delete_expense(db: Session, user: User, expense_id: int):
    exists = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == user.id).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(exists)
    db.commit()
    return {"message": "Expense deleted successfully"}