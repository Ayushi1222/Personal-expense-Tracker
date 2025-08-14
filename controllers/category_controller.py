from sqlalchemy.orm import Session
from sqlalchemy import text
from models.category import Category
from models.user import User
from fastapi import HTTPException

def list_categories(db: Session, user: User):
    return db.query(Category).filter(Category.user_id == user.id).order_by(Category.name).all()

def create_category(db: Session, user: User, name: str):
    exists = db.query(Category).filter(Category.user_id == user.id, Category.name == name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    try:
        # Manual ID generation
        max_id_result = db.execute(text("SELECT COALESCE(MAX(id), 0) FROM categories")).scalar_one()
        next_id = max_id_result + 1

        db.execute(
            text("INSERT INTO categories (id, name, user_id) VALUES (:id, :name, :user_id)"),
            {'id': next_id, 'name': name, 'user_id': user.id}
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
