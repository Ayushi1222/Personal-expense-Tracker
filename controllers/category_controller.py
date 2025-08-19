from sqlalchemy.orm import Session
from sqlalchemy import text, func
from models.category import Category
from models.expense import Expense
from models.budget import Budget
from models.user import User
from fastapi import HTTPException
from config.settings import settings
from datetime import datetime, timezone

def list_categories(db: Session, user: User):
    current_month = datetime.now().strftime("%Y-%m")

    budget_subquery = db.query(
        Budget.category_id,
        Budget.amount.label("monthly_budget")
    ).filter(
        Budget.user_id == user.id,
        Budget.month == current_month
    ).subquery()

    results = db.query(
        Category.id,
        Category.name,
        Category.user_id,
        func.coalesce(func.sum(Expense.amount), 0.0).label("total_expenses"),
        budget_subquery.c.monthly_budget
    ).outerjoin(Expense, Category.id == Expense.category_id)\
     .outerjoin(budget_subquery, Category.id == budget_subquery.c.category_id)\
     .filter(Category.user_id == user.id)\
     .group_by(
         Category.id, 
         Category.name, 
         Category.user_id, 
         budget_subquery.c.monthly_budget
     )\
     .order_by(Category.name)\
     .all()

    formatted_categories = {}
    for category in results:
        formatted_categories[category.id] = {
            "id": category.id,
            "name": category.name,
            "user_id": category.user_id,
            "total_expenses": f"{settings.CURRENCY_SYMBOL}{category.total_expenses:.2f}",
            "current_month_budget": f"{settings.CURRENCY_SYMBOL}{category.monthly_budget:.2f}" if category.monthly_budget is not None else "Not Set"
        }
        
    return formatted_categories

def create_category(db: Session, user: User, name: str):
    exists = db.query(Category).filter(Category.user_id == user.id, Category.name == name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    try:
        # Manual ID generation
        max_id_result = db.execute(text("SELECT COALESCE(MAX(id), 0) FROM categories")).scalar_one()
        next_id = max_id_result + 1

        now = datetime.now(timezone.utc)
        db.execute(
            text("INSERT INTO categories (id, name, user_id, created_at, updated_at) VALUES (:id, :name, :user_id, :created_at, :updated_at)"),
            {'id': next_id, 'name': name, 'user_id': user.id, 'created_at': now, 'updated_at': now}
        )
        db.commit()
        
        new_cat = db.query(Category).filter(Category.id == next_id).first()
        return new_cat
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create category: {e}")


def update_category(db: Session, user: User, category_id: int, name: str):
    category = db.query(Category).filter(Category.id == category_id, Category.user_id == user.id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found or access denied")

    existing_category = db.query(Category).filter(
        Category.user_id == user.id,
        Category.name == name,
        Category.id != category_id
    ).first()
    if existing_category:
        raise HTTPException(status_code=409, detail=f"Category name '{name}' already exists.")

    category.name = name
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, user: User, category_id: int):
    cat = db.query(Category).filter(Category.id == category_id, Category.user_id == user.id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(cat)
    db.commit()
    return {"message": "Category deleted successfully"}
