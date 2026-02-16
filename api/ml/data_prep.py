from api.models.transaction import Transaction
from collections import defaultdict
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session
from typing import List, Tuple

def prepare_training_data(db, user_id, category_id, budget_start, budget_end):
    transactions = db.query(
        Transaction.date,
        Transaction.amount
    ).filter(
        Transaction.user_id == user_id,
        Transaction.category_id == category_id,
        Transaction.direction == "EXPENSE",
        Transaction.date >= budget_start,
        Transaction.date <= budget_end
    ).order_by(Transaction.date).all()

    if len(transactions) < 5:
        return [], []

    daily_totals = defaultdict(float)

    for tx_date, amount in transactions:
        day = (tx_date.date() - budget_start).days + 1
        daily_totals[day] += float(amount)

    X, y = [], []
    cumulative = 0.0

    for day in sorted(daily_totals):
        cumulative += daily_totals[day]
        X.append([day])          # day index
        y.append(cumulative)     # cumulative spend till that day

    return X, y