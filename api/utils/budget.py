from datetime import date
from sqlalchemy.orm import Session
from api.models.budget import Budget
from api.models.transaction import Transaction

def get_budget_status(user_id: int, budget_id: int, db: Session):
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == user_id
    ).first()

    if not budget:
        return {"message": "Budget not found"}

    transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.category_id == budget.category_id,
        Transaction.direction == "EXPENSE",
        Transaction.date >= budget.start_date,
        Transaction.date <= budget.end_date
    ).all()

    spent = sum(float(t.amount) for t in transactions)

    total_days = (budget.end_date - budget.start_date).days + 1
    today = min(date.today(), budget.end_date)
    days_elapsed = max((today - budget.start_date).days + 1, 1)
    remaining_days = max(total_days - days_elapsed, 0)

    if not transactions:
        return {
            "spent": 0.0,
            "budget": float(budget.amount),
            "remaining": float(budget.amount),
            "status": "under",
        }

    if len(transactions) < 10 or days_elapsed < 7:
        remaining = budget.amount - spent
        return {
            "spent": round(spent, 2),
            "budget": float(budget.amount),
            "remaining": round(remaining, 2),
            "status": "over" if remaining < 0 else "under"
        }