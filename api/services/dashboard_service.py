from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.models.transaction import Transaction
from api.models.investment import Investment
from api.models.budget import Budget
from api.models.subscription import Subscription
from api.schemas.dashboard import overviewResponse
from datetime import datetime
from dateutil.relativedelta import relativedelta
from fastapi import Depends
from sqlalchemy import func, extract
from sqlalchemy.orm import Session
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