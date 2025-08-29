import asyncio
import csv
import io
import pandas as pd
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, text, select
from models.expense import Expense
from models.user import User
from models.category import Category

async def monthly_reports(db: Session, user: User, month: str):
    def _report():
        if db.bind.url.get_backend_name() == "sqlite":
            date_filter = func.strftime('%Y-%m', Expense.date) == month
        else:
            date_filter = func.to_char(Expense.date, 'YYYY-MM') == month

        query_result = db.execute(select(
            func.coalesce(func.sum(Expense.amount), 0),
            func.coalesce(func.count(Expense.id), 0) # pylint: disable=not-callable
        ).filter(
            Expense.user_id == user.id,
            date_filter
        )).one()

        total_amount = float(query_result[0] or 0)
        transaction_count = int(query_result[1] or 0)

        average_transaction = total_amount / transaction_count if transaction_count > 0 else 0

        top_categories_query = db.execute(select(
            Category.name,
            func.sum(Expense.amount).label('total_spent')
        ).join(Expense, Expense.category_id == Category.id).filter(
            Expense.user_id == user.id,
            date_filter
        ).group_by(Category.name).order_by(func.sum(Expense.amount).desc()).limit(5)).all()

        top_categories = [{"category": name, "total_spent": float(total)} for name, total in top_categories_query]

        return {
            "month": month,
            "total_expenses": total_amount,
            "total_transactions": transaction_count,
            "average_transaction_amount": round(average_transaction, 2),
            "top_spending_categories": top_categories
        }
    return await asyncio.to_thread(_report)

async def generate_monthly_report_csv(db: Session, user: User, month: str):
    report_data = await monthly_reports(db, user, month)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Month', report_data['month']])
    writer.writerow(['Total Expenses', report_data['total_expenses']])
    writer.writerow(['Total Transactions', report_data['total_transactions']])
    writer.writerow(['Average Transaction Amount', report_data['average_transaction_amount']])
    writer.writerow([]) # Empty line
    
    writer.writerow(['Top Spending Categories'])
    writer.writerow(['Category', 'Total Spent'])
    for category in report_data['top_spending_categories']:
        writer.writerow([category['category'], category['total_spent']])
        
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=monthly_report_{month}.csv"})

async def generate_monthly_by_category_report_csv(db: Session, user: User, month: str):
    report_data = await monthly_reports_by_category(db, user, month)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['Month', report_data['month']])
    writer.writerow(['Total Monthly Expenses', report_data['total_monthly_expenses']])
    writer.writerow([])

    writer.writerow(['Breakdown by Category'])
    writer.writerow(['Category Name', 'Total Amount', 'Transaction Count', 'Percentage of Total Expenses'])

    for item in report_data['breakdown_by_category'].values():
        writer.writerow([
            item['category_name'],
            item['total_amount'],
            item['transaction_count'],
            item['percentage_of_total_expenses']
        ])
    
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=monthly_report_by_category_{month}.csv"})

async def monthly_reports_by_category(db: Session, user: User, month: str):
    def _report_by_category():
        if db.bind.url.get_backend_name() == "sqlite":
            date_filter = func.strftime('%Y-%m', Expense.date) == month
            total_monthly_amount = db.execute(select(func.coalesce(func.sum(Expense.amount), 0)).filter(
                Expense.user_id == user.id,
                date_filter
            )).scalar()
        else:
            date_filter = func.to_char(Expense.date, 'YYYY-MM') == month
            total_monthly_amount = db.execute(
                text("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE user_id=:uid AND to_char(date, 'YYYY-MM')=:m"),
                {"uid": user.id, "m": month}
            ).scalar_one()
        
        total_monthly_amount = float(total_monthly_amount or 0)

        results = db.execute(select(
            Category.id,
            Category.name,
            func.coalesce(func.sum(Expense.amount), 0).label("total_amount"),
            func.coalesce(func.count(Expense.id), 0).label("transaction_count") # pylint: disable=not-callable
        )
        .outerjoin(Expense, (Expense.category_id == Category.id) & (Expense.user_id == user.id) & date_filter)
        .filter(Category.user_id == user.id)
        .group_by(Category.id, Category.name)
        .order_by(Category.name)
        ).all()

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
    return await asyncio.to_thread(_report_by_category)

async def generate_monthly_report_csv2(db: Session, user: User, month: str):
    report_data = await monthly_reports(db, user, month)
    main_data = [
        ['Month', report_data['month']],
        ['Total Expenses', report_data['total_expenses']],
        ['Total Transactions', report_data['total_transactions']],
        ['Average Transaction Amount', report_data['average_transaction_amount']],
    ]
    top_categories = report_data['top_spending_categories']
    categories_df = pd.DataFrame(top_categories)
    output = io.StringIO()
    pd.DataFrame(main_data).to_csv(output, header=False, index=False)
    output.write('\n')
    output.write('Top Spending Categories\n')
    if not categories_df.empty:
        categories_df.to_csv(output, index=False)
    else:
        output.write('No categories found\n')
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=monthly_report_{month}_csv2.csv"})

async def generate_monthly_by_category_report_csv2(db: Session, user: User, month: str):
    report_data = await monthly_reports_by_category(db, user, month)
    main_data = [
        ['Month', report_data['month']],
        ['Total Monthly Expenses', report_data['total_monthly_expenses']],
    ]
    breakdown = list(report_data['breakdown_by_category'].values())
    breakdown_df = pd.DataFrame(breakdown)
    output = io.StringIO()
    pd.DataFrame(main_data).to_csv(output, header=False, index=False)
    output.write('\nBreakdown by Category\n')
    if not breakdown_df.empty:
        breakdown_df.to_csv(output, index=False)
    else:
        output.write('No category breakdown found\n')
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=monthly_report_by_category_{month}_csv2.csv"})
