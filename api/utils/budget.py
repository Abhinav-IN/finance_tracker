from api.models.budget import Budget
from api.models.transaction import Transaction
from api.utils.time import ist_now
from api.ml.data_prep import prepare_training_data
from api.ml.feature_builder import build_features
from api.ml.model import linear_regression_model
from sqlalchemy import func
from sqlalchemy.orm import Session


def get_budget_status(user_id: int, budget_id: int, db: Session):
    budget = db.query(Budget).filter(
        Budget.budget_id == budget_id,
        Budget.user_id == user_id
    ).first()

    if not budget:
        return {"message" : "Budget Not found"}  
    
    X_raw, current_spent = prepare_training_data(db, user_id, budget.category_id, budget.start_date, budget.end_date)

    if not X_raw:
        total_spent = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.category_id == budget.category_id,
            Transaction.direction == "EXPENSE",
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
    
    X_features = build_features(X_raw, budget.start_date, budget.end_date)
    y = [current_spent]*len(X_features)
    model = linear_regression_model(X_features[-1], y)
    latest_features = X_features[-1]
    predicted_total = predict_month_end_spend(model, latest_features)

    remaining = budget.amount - predicted_total
    status = "over" if remaining < 0 else "under"

    return {
        "type": "ml_based",
        "current_spent": current_spent,
        "predicted_month_end_spend": predicted_total,
        "budget": float(budget.amount),
        "remaining": float(remaining),
        "status": status,
        "message": (
            "You are likely to exceed your budget"
            if status == "over"
            else "You are within budget"
        )
    }