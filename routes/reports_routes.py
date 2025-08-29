from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from config.database import get_db
from middleware.auth import get_current_user
from controllers.reports_controller import monthly_reports, monthly_reports_by_category, generate_monthly_report_csv, generate_monthly_by_category_report_csv
from models.user import User
from schemas.report_schema import MonthlyReport, MonthlyReportByCategory

router = APIRouter()

@router.get("/summary/{month}", response_model=MonthlyReport)
async def get_reports_summary(month: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await monthly_reports(db, current_user, month)

@router.get("/summary/{month}/csv", response_class=StreamingResponse)
async def get_reports_summary_csv(month: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await generate_monthly_report_csv(db, current_user, month)

@router.get("/summary/{month}/csv2", response_class=StreamingResponse)
async def get_reports_summary_csv2(month: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from controllers.reports_controller import generate_monthly_report_csv2
    return await generate_monthly_report_csv2(db, current_user, month)

@router.get("/summary-by-category/{month}", response_model=MonthlyReportByCategory)
async def get_reports_summary_by_category(month: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await monthly_reports_by_category(db, current_user, month)

@router.get("/summary-by-category/{month}/csv", response_class=StreamingResponse)
async def get_reports_summary_by_category_csv(month: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await generate_monthly_by_category_report_csv(db, current_user, month)

@router.get("/summary-by-category/{month}/csv2", response_class=StreamingResponse)
async def get_reports_summary_by_category_csv2(month: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from controllers.reports_controller import generate_monthly_by_category_report_csv2
    return await generate_monthly_by_category_report_csv2(db, current_user, month)
