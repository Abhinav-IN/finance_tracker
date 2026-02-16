from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.models.budget import Budget
from api.models.transaction import Transaction
from api.ml.predictor import predict_daily_spend


def get_budget_status(user_id: int, budget_id: int, db: Session):
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == user_id
    ).first()

    if not budget:
        return {"message": "Budget not found"}

    # -------------------------
    # Fetch transactions
    # -------------------------
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

    # -------------------------
    # CASE 1: No transactions
    # -------------------------
    if not transactions:
        return {
            "type": "fresh_budget",
            "spent": 0.0,
            "budget": float(budget.amount),
            "remaining": float(budget.amount),
            "status": "under",
            "message": "No spending recorded yet"
        }

    # -------------------------
    # CASE 2: Low data → rule based
    # -------------------------
    if len(transactions) < 10 or days_elapsed < 7:
        remaining = budget.amount - spent
        return {
            "type": "rule_based",
            "spent": round(spent, 2),
            "budget": float(budget.amount),
            "remaining": round(remaining, 2),
            "status": "over" if remaining < 0 else "under",
            "message": "Not enough data for prediction"
        }

    # -------------------------
    # CASE 3: ML-assisted (SAFE)
    # -------------------------
    avg_daily_spend = spent / days_elapsed

    predicted_daily = predict_daily_spend([avg_daily_spend])

    predicted_total = spent + (predicted_daily * remaining_days)

    # HARD SAFETY CAPS (VERY IMPORTANT)
    predicted_total = max(predicted_total, spent)
    predicted_total = min(predicted_total, budget.amount * 1.5)

    remaining = budget.amount - predicted_total

    return {
        "type": "ml_assisted",
        "spent_so_far": round(spent, 2),
        "predicted_total_spend": round(predicted_total, 2),
        "budget": float(budget.amount),
        "remaining": round(remaining, 2),
        "status": "over" if remaining < 0 else "under",
        "message": (
            "Likely to exceed budget"
            if remaining < 0
            else "Spending looks under control"
        )
    }