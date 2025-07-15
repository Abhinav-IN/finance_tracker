from api.models.budget import Budget
from api.models.transaction import Transaction
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session


def get_budget_status(user_id: int, category_id: int, expense_date: datetime, db: Session):
    budget = db.query(Budget).filter(
        Budget.user_id == user_id,
        Budget.category_id == category_id,
        Budget.start_date <= expense_date,
        Budget.end_date >= expense_date
    ).first()

    if not budget:
        return None  

    total_spent = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.category_id == category_id,
        Transaction.is_expense == True,
        Transaction.transaction_date >= budget.start_date,
        Transaction.transaction_date <= budget.end_date
    ).scalar() or 0

    remaining = budget.budget_amount - total_spent
    status = "under"
    warning = ""

    if remaining <= 0:
        status = "over"
        warning = f"Budget exceeded by ₹{abs(remaining)}!"
    elif remaining <= 0.1 * budget.budget_amount:
        warning = f"Only ₹{remaining} left in budget!"

    return {
        "status": status,
        "budget_amount": budget.budget_amount,
        "spent": total_spent,
        "remaining": remaining,
        "message": warning
    }