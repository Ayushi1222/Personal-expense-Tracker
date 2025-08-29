import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import text, func, select
from models.category import Category
from models.expense import Expense
from models.budget import Budget
from models.user import User
from fastapi import HTTPException
from config.settings import settings
from datetime import datetime, timezone

async def list_categories(db: Session, user: User):
    def _list():
        current_month = datetime.now().strftime("%Y-%m")

        budget_subquery = select(
            Budget.category_id,
            Budget.amount.label("monthly_budget")
        ).filter(
            Budget.user_id == user.id,
            Budget.month == current_month
        ).subquery()

        results = db.execute(select(
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
         .order_by(Category.name))

        formatted_categories = {}
        for category in results.all():
            formatted_categories[category.id] = {
                "id": category.id,
                "name": category.name,
                "user_id": category.user_id,
                "total_expenses": f"{settings.CURRENCY_SYMBOL}{category.total_expenses:.2f}",
                "current_month_budget": f"{settings.CURRENCY_SYMBOL}{category.monthly_budget:.2f}" if category.monthly_budget is not None else "Not Set"
            }
            
        return formatted_categories
    return await asyncio.to_thread(_list)

async def create_category(db: Session, user: User, name: str):
    def _create():
        exists = db.execute(select(Category).filter(Category.user_id == user.id, Category.name == name)).scalars().first()
        if exists:
            raise HTTPException(status_code=400, detail="Category already exists")
        
        try:
            max_id_result = db.execute(text("SELECT COALESCE(MAX(id), 0) FROM categories")).scalar_one()
            next_id = max_id_result + 1

            now = datetime.now(timezone.utc)
            db.execute(
                text("INSERT INTO categories (id, name, user_id, created_at, updated_at) VALUES (:id, :name, :user_id, :created_at, :updated_at)"),
                {'id': next_id, 'name': name, 'user_id': user.id, 'created_at': now, 'updated_at': now}
            )
            db.commit()
            
            new_cat = db.execute(select(Category).filter(Category.id == next_id)).scalars().first()
            return new_cat
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to create category: {e}") from e
    return await asyncio.to_thread(_create)

async def update_category(db: Session, user: User, category_id: int, name: str):
    def _update():
        category = db.execute(select(Category).filter(Category.id == category_id, Category.user_id == user.id)).scalars().first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found or access denied")

        existing_category = db.execute(select(Category).filter(
            Category.user_id == user.id,
            Category.name == name,
            Category.id != category_id
        )).scalars().first()
        if existing_category:
            raise HTTPException(status_code=409, detail=f"Category name '{name}' already exists.")

        category.name = name
        db.commit()
        db.refresh(category)
        return category
    return await asyncio.to_thread(_update)

async def delete_category(db: Session, user: User, category_id: int):
    def _delete():
        cat = db.execute(select(Category).filter(Category.id == category_id, Category.user_id == user.id)).scalars().first()
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")
        
        db.delete(cat)
        db.commit()
        return {"message": "Category deleted successfully"}
    return await asyncio.to_thread(_delete)
