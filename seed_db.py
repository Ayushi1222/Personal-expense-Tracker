import sys
from pathlib import Path
from sqlalchemy import text
from datetime import date

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from config.database import SessionLocal, engine
from models.base import Base
from models.user import User
from models.category import Category
from models.budget import Budget
from models.expense import Expense
from utils.security import hash_password

def seed_database():
    """
    Drops all tables, recreates them based on the current models,
    and seeds the database with a clean set of test data.
    """
    db = SessionLocal()
    try:
        # Drop all tables first to ensure a clean slate
        print("--- Dropping all tables ---")
        Base.metadata.drop_all(bind=engine)
        print("Tables dropped.")

        # Recreate all tables with the new schema
        print("\n--- Creating all tables ---")
        Base.metadata.create_all(bind=engine)
        print("Tables created.")

        # --- Seed Users ---
        print("\n--- Seeding Users ---")
        users_to_seed = [
            {'id': 1, 'email': 'john.doe@example.com', 'name': 'John Doe', 'password': 'password123'},
            {'id': 2, 'email': 'jane.doe@example.com', 'name': 'Jane Doe', 'password': 'password456'},
        ]
        for user_data in users_to_seed:
            hashed_password = hash_password(user_data['password'])
            insert_sql = text("""
                INSERT INTO users (id, email, name, password_hash) 
                VALUES (:id, :email, :name, :password_hash)
            """)
            db.execute(insert_sql, {
                'id': user_data['id'],
                'email': user_data['email'],
                'name': user_data['name'],
                'password_hash': hashed_password
            })
        print(f"Seeded {len(users_to_seed)} users.")

        # --- Seed Categories ---
        print("\n--- Seeding Categories ---")
        categories_to_seed = [
            {'user_id': 1, 'name': 'Food'},
            {'user_id': 1, 'name': 'Transport'},
            {'user_id': 1, 'name': 'Entertainment'},
            {'user_id': 2, 'name': 'Shopping'},
            {'user_id': 2, 'name': 'Utilities'},
        ]
        next_cat_id = 1
        for cat in categories_to_seed:
            insert_sql = text("INSERT INTO categories (id, name, user_id) VALUES (:id, :name, :user_id)")
            db.execute(insert_sql, {'id': next_cat_id, 'name': cat['name'], 'user_id': cat['user_id']})
            next_cat_id += 1
        print(f"Seeded {len(categories_to_seed)} categories.")
        
        db.commit()  # Commit users and categories to get IDs for budgets

        # --- Seed Budgets ---
        print("\n--- Seeding Budgets ---")
        budgets_to_seed = [
            {'user_id': 1, 'category_name': 'Food', 'amount': 500.00, 'month': '2025-08'},
            {'user_id': 1, 'category_name': 'Transport', 'amount': 150.00, 'month': '2025-08'},
            {'user_id': 2, 'category_name': 'Shopping', 'amount': 300.00, 'month': '2025-08'},
        ]
        next_budget_id = 1
        for budget in budgets_to_seed:
            category = db.query(Category).filter(Category.name == budget['category_name'], Category.user_id == budget['user_id']).first()
            if not category:
                print(f"Skipping budget, category '{budget['category_name']}' not found for user {budget['user_id']}")
                continue
            
            insert_sql = text("""
                INSERT INTO budgets (id, user_id, category_id, month, amount)
                VALUES (:id, :user_id, :category_id, :month, :amount)
            """)
            db.execute(insert_sql, {
                'id': next_budget_id,
                'user_id': budget['user_id'],
                'category_id': category.id,
                'month': budget['month'],
                'amount': budget['amount']
            })
            next_budget_id += 1
        print(f"Seeded {len(budgets_to_seed)} budgets.")
        
        # --- Seed Expenses ---
        print("\n--- Seeding Expenses ---")
        expenses_to_seed = [
            {'user_id': 1, 'category_name': 'Food', 'amount': 410.0, 'date': '2025-08-01', 'note': 'Groceries (to trigger alert)'},
            {'user_id': 1, 'category_name': 'Transport', 'amount': 80.0, 'date': '2025-08-02', 'note': 'Gas'},
            {'user_id': 2, 'category_name': 'Shopping', 'amount': 120.0, 'date': '2025-08-05', 'note': 'New shoes'},
        ]
        next_expense_id = 1
        for exp in expenses_to_seed:
            category = db.query(Category).filter(Category.name == exp['category_name'], Category.user_id == exp['user_id']).first()
            if not category:
                print(f"Skipping expense, category '{exp['category_name']}' not found for user {exp['user_id']}")
                continue

            insert_sql = text("""
                INSERT INTO expenses (id, user_id, category_id, amount, date, note)
                VALUES (:id, :user_id, :category_id, :amount, :date, :note)
            """)
            db.execute(insert_sql, {
                'id': next_expense_id,
                'user_id': exp['user_id'],
                'category_id': category.id,
                'amount': exp['amount'],
                'date': date.fromisoformat(exp['date']),
                'note': exp['note']
            })
            next_expense_id += 1
        print(f"Seeded {len(expenses_to_seed)} expenses.")

        db.commit()
        print("\nDatabase seeding complete.")
    except Exception as e:
        print(f"An error occurred during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
