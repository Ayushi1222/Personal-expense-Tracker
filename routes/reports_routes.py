from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.database import get_db
from middleware.auth import get_current_user
from controllers.reports_controller import monthly_reports, monthly_reports_by_category
from models.user import User
from schemas.report_schema import MonthlyReport, MonthlyReportByCategory

router = APIRouter()

@router.get("/summary/{month}", response_model=MonthlyReport)
async def get_reports_summary(month: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await monthly_reports(db, current_user, month)

@router.get("/summary-by-category/{month}", response_model=MonthlyReportByCategory)
async def get_reports_summary_by_category(month: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await monthly_reports_by_category(db, current_user, month)
