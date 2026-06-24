from api.models.category import Category
from api.models.payment_mode import PaymentMode
from api.models.transaction import Transaction
from api.models.transaction_type import TransactionType
from api.utils.time import IST
from datetime import datetime, time
from sqlalchemy import or_

def apply_search_filter(query, search: str):
    search = search.strip()

    return (
        query
        .join(Category, isouter=True)
        .join(TransactionType, isouter=True)
        .join(PaymentMode, isouter=True)
        .filter(
            or_(
                Transaction.title.ilike(f"%{search}%"),
                Transaction.description.ilike(f"%{search}%"),
                Category.name.ilike(f"%{search}%"),
                TransactionType.name.ilike(f"%{search}%"),
                PaymentMode.name.ilike(f"%{search}%"),
            )
        )
    )

def apply_date_filter(query, date):
    start = datetime.combine(date, time.min).replace(tzinfo=IST)
    end = datetime.combine(date, time.max).replace(tzinfo=IST)
    return query.filter(Transaction.date.between(start, end))

def apply_transaction_filters(query, filters):
    if filters.direction:
        query = query.filter(Transaction.direction == filters.direction)
    
    if filters.id is not None:
        query = query.filter(Transaction.id == filters.id)

    if filters.exact_amount is not None:
        query = query.filter(Transaction.amount == filters.exact_amount)

    if filters.greater_amount is not None:
        query = query.filter(Transaction.amount > filters.greater_amount)

    if filters.lower_amount is not None:
        query = query.filter(Transaction.amount < filters.lower_amount)

    if filters.date:
        query = apply_date_filter(query, filters.date)

    if filters.search:
        query = apply_search_filter(query, filters.search)

    return query
