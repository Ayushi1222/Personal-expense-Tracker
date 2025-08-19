from pydantic import BaseModel, Field
from typing import List, Dict

class TopCategory(BaseModel):
    category: str
    total_spent: float

class MonthlyReport(BaseModel):
    month: str
    total_expenses: float
    total_transactions: int
    average_transaction_amount: float
    top_spending_categories: List[TopCategory]

class CategoryBreakdown(BaseModel):
    category_name: str
    total_amount: float
    transaction_count: int
    percentage_of_total_expenses: float

class MonthlyReportByCategory(BaseModel):
    month: str
    total_monthly_expenses: float
    breakdown_by_category: Dict[str, CategoryBreakdown]
