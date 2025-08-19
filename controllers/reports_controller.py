from sqlalchemy.orm import Session
from sqlalchemy import func, text
from models.expense import Expense
from models.user import User
from models.category import Category

def monthly_reports(db: Session, user: User, month: str):
    if db.bind.url.get_backend_name() == "sqlite":
        date_filter = func.strftime('%Y-%m', Expense.date) == month
    else:
        date_filter = func.to_char(Expense.date, 'YYYY-MM') == month

    query_result = db.query(
        func.coalesce(func.sum(Expense.amount), 0),
        func.coalesce(func.count(Expense.id), 0)
    ).filter(
        Expense.user_id == user.id,
        date_filter
    ).one()

    total_amount = float(query_result[0] or 0)
    transaction_count = int(query_result[1] or 0)

    average_transaction = total_amount / transaction_count if transaction_count > 0 else 0

    top_categories_query = db.query(
        Category.name,
        func.sum(Expense.amount).label('total_spent')
    ).join(Expense, Expense.category_id == Category.id).filter(
        Expense.user_id == user.id,
        date_filter
    ).group_by(Category.name).order_by(func.sum(Expense.amount).desc()).limit(5).all()

    top_categories = [{"category": name, "total_spent": float(total)} for name, total in top_categories_query]

    return {
        "month": month,
        "total_expenses": total_amount,
        "total_transactions": transaction_count,
        "average_transaction_amount": round(average_transaction, 2),
        "top_spending_categories": top_categories
    }


def monthly_reports_by_category(db: Session, user: User, month: str):
    if db.bind.url.get_backend_name() == "sqlite":
        date_filter = func.strftime('%Y-%m', Expense.date) == month
        total_monthly_amount = db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
            Expense.user_id == user.id,
            date_filter
        ).scalar()
    else:
        date_filter = func.to_char(Expense.date, 'YYYY-MM') == month
        total_monthly_amount = db.execute(
            text("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id=:uid AND to_char(date, 'YYYY-MM')=:m"),
            {"uid": user.id, "m": month}
        ).scalar_one()
    
    total_monthly_amount = float(total_monthly_amount or 0)

    results = (
        db.query(
            Category.id,
            Category.name,
            func.coalesce(func.sum(Expense.amount), 0).label("total_amount"),
            func.coalesce(func.count(Expense.id), 0).label("transaction_count")
        )
        .outerjoin(Expense, (Expense.category_id == Category.id) & (Expense.user_id == user.id) & date_filter)
        .filter(Category.user_id == user.id)
        .group_by(Category.id, Category.name)
        .order_by(Category.name)
        .all()
    )

    report_by_category = {}
    for r in results:
        category_total = float(r.total_amount)
        percentage = (category_total / total_monthly_amount * 100) if total_monthly_amount > 0 else 0
        report_by_category[r.id] = {
            "category_name": r.name,
            "total_amount": category_total,
            "transaction_count": r.transaction_count,
            "percentage_of_total_expenses": round(percentage, 2)
        }

    return {
        "month": month,
        "total_monthly_expenses": total_monthly_amount,
        "breakdown_by_category": report_by_category
    }
