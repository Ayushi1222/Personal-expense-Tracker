from fastapi import FastAPI
from config.database import init_db
from routes.auth_routes import router as auth_router
from routes.user_routes import router as user_router
from routes.category_routes import router as category_router
from routes.expense_routes import router as expense_router
from routes.budget_routes import router as budget_router
from routes.reports_routes import router as reports_router

app = FastAPI(title="Personal Finance Tracker (PFT)",
              version="1.0.0")

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Personal Finance Tracker API"}

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(category_router, prefix="/categories", tags=["categories"])
app.include_router(expense_router, prefix="/expenses", tags=["expenses"])
app.include_router(budget_router, prefix="/budgets", tags=["budgets"])
app.include_router(reports_router, prefix="/reports", tags=["reports"])
