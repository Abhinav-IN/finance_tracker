from api.models.transaction import Transaction
from api.models.investment import Investment
from api.models.budget import Budget
from api.models.subscription import Subscription
from api.schemas.dashboard import overviewResponse
from api.utils.enums import TransactionDirection
from api.utils.time import ist_now
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import func, extract, cast
from sqlalchemy.orm import Session
from sqlalchemy.sql.sqltypes import Date

def overview_of_user(user_id : int, db : Session):
    current_month = ist_now().month
    current_year = ist_now().year
    start_of_month = ist_now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = (start_of_month + relativedelta(months=1)) - relativedelta(seconds=1)


    # Calculate total income
    final_income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.direction == TransactionDirection.INCOME,
        extract("month", Transaction.date) == current_month,
        extract("year", Transaction.date) == current_year
    ).scalar() or 0.0

    # Calculate total expense
    final_expense = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.direction == TransactionDirection.EXPENSE,
        extract("month", Transaction.date) == current_month,
        extract("year", Transaction.date) == current_year
    ).scalar() or 0.0

    # Calculate total investment
    final_investments = db.query(func.sum(Investment.amount_invested)).filter(
        Investment.user_id == user_id,
        extract("month", Investment.investment_date) == current_month,
        extract("year", Investment.investment_date) == current_year
    ).scalar() or 0.0

    # Calculate total budget amount
    final_budget = db.query(func.sum(Budget.amount)).filter(
    Budget.user_id == user_id,
    Budget.start_date <= end_of_month,
    Budget.end_date >= start_of_month
    ).scalar() or 0.0

    # calculate total subscription
    final_subscription = db.query(func.sum(Subscription.amount)).filter(Subscription.user_id == user_id, Subscription.is_active == True).scalar() or 0.0

    return overviewResponse(
        total_income = final_income,
        total_expense = final_expense,
        total_investment = final_investments,
        total_budget = final_budget,
        total_subscription = final_subscription
    )

def get_past_30_day_transaction(userId : int, direction : TransactionDirection, db : Session):
    today = ist_now().date()
    start_date = today - timedelta(days=29)

    transaction_query = db.query(cast(Transaction.date, Date).label("date"), func.sum(Transaction.amount).label("total_transaction")).filter(
        Transaction.user_id == userId,
        Transaction.direction == direction,
        cast(Transaction.date, Date) >= start_date,
        cast(Transaction.date, Date) <= today).group_by(cast(Transaction.date, Date)).all()
    
    transaction_map = {curr_transaction.date : float(curr_transaction.total_transaction) for curr_transaction in transaction_query}

    transaction_record = []
    for i in range(30):
        date = start_date + timedelta(days=i)
        transaction_record.append({
            "date" : date.isoformat(),
            "total_transaction" : transaction_map.get(date, 0.0) 
        })
    
    return transaction_record

