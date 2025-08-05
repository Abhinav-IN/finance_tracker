from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.models.transaction import Transaction
from api.models.investment import Investment
from api.models.budget import Budget
from api.models.subscription import Subscription
from api.schemas.dashboard import overviewResponse
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from fastapi import Depends
from sqlalchemy import func, extract, cast
from sqlalchemy.orm import Session
from sqlalchemy.sql.sqltypes import Date
from zoneinfo import ZoneInfo

def overview_of_user(user : dict = Depends(require_roles("user", "admin")),
                     db : Session = Depends(get_db)):
    
    ist = ZoneInfo("Asia/Kolkata")
    now = datetime.now(ist)
    current_month = now.month
    current_year = now.year
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = (start_of_month + relativedelta(months=1)) - relativedelta(seconds=1)


    # Calculate total income
    final_income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user["id"],
        Transaction.is_income == True,
        extract("month", Transaction.transaction_date) == current_month,
        extract("year", Transaction.transaction_date) == current_year
    ).scalar() or 0.0

    # Calculate total expense
    final_expense = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user["id"],
        Transaction.is_expense == True,
        extract("month", Transaction.transaction_date) == current_month,
        extract("year", Transaction.transaction_date) == current_year
    ).scalar() or 0.0

    # Calculate total investment
    final_investments = db.query(func.sum(Investment.amount_invested)).filter(
        Investment.user_id == user["id"],
        extract("month", Investment.investment_date) == current_month,
        extract("year", Investment.investment_date) == current_year
    ).scalar() or 0.0

    # Calculate total budget amount
    final_budget = db.query(func.sum(Budget.budget_amount)).filter(
    Budget.user_id == user["id"],
    Budget.start_date <= end_of_month,
    Budget.end_date >= start_of_month
    ).scalar() or 0.0

    # calculate total subscription
    final_subscription = db.query(func.sum(Subscription.amount)).filter(Subscription.user_id == user["id"], Subscription.is_active == True).scalar() or 0.0

    return overviewResponse(
        total_income = final_income,
        total_expense = final_expense,
        total_investment = final_investments,
        total_budget = final_budget,
        total_subscription = final_subscription
    )

def get_past_30_day_expense(userId : int, db : Session):
    today = datetime.now(tz=ZoneInfo("Asia/Kolkata")).date()
    start_date = today - timedelta(days=29)

    expense_query = db.query(cast(Transaction.transaction_date, Date).label("date"), func.sum(Transaction.amount).label("total_expense")).filter(
        Transaction.user_id == userId,
        Transaction.is_expense == True,
        cast(Transaction.transaction_date, Date) >= start_date,
        cast(Transaction.transaction_date, Date) <= today).group_by(cast(Transaction.transaction_date, Date)).all()
    
    expense_map = {curr_expense.date : float(curr_expense.total_expense) for curr_expense in expense_query}

    expense_record = []
    for i in range(30):
        date = start_date + timedelta(days=i)
        expense_record.append({
            "date" : date.isoformat(),
            "total_expense" : expense_map.get(date, 0.0) 
        })
    
    return expense_record

def get_past_30_day_income(userId : int, db : Session):
    today = datetime.now(tz=ZoneInfo("Asia/Kolkata")).date()
    start_date = today - timedelta(days=29)

    income_query = db.query(cast(Transaction.transaction_date, Date).label("date"), func.sum(Transaction.amount).label("total_income")).filter(
        Transaction.user_id == userId,
        Transaction.is_income == True,
        cast(Transaction.transaction_date, Date) >= start_date,
        cast(Transaction.transaction_date, Date) <= today).group_by(cast(Transaction.transaction_date, Date)).all()
    
    income_map = {curr_income.date : float(curr_income.total_income) for curr_income in income_query}

    income_record = []
    for i in range(30):
        date = start_date + timedelta(days=i)
        income_record.append({
            "date" : date.isoformat(),
            "total_income" : income_map.get(date, 0.0) 
        })
    
    return income_record