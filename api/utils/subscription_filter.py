from api.models.account import Account
from api.models.category import Category
from api.models.payment_mode import PaymentMode
from api.models.subscription import Subscription
from api.models.transaction_type import TransactionType
from api.utils.time import IST
from datetime import datetime, time
from sqlalchemy import or_

def ist_day_range(date):
    start = datetime.combine(date, time.min).replace(tzinfo=IST)
    end = datetime.combine(date, time.max).replace(tzinfo=IST)
    return start, end

def apply_basic_filters(query, filters):
    if filters.id is not None:
        query = query.filter(Subscription.id == filters.id)

    if filters.name:
        query = query.filter(
            Subscription.name.ilike(f"%{filters.name.strip()}%")
        )

    if filters.exact_amount is not None:
        query = query.filter(Subscription.amount == filters.exact_amount)

    if filters.greater_amount is not None:
        query = query.filter(Subscription.amount > filters.greater_amount)

    if filters.lower_amount is not None:
        query = query.filter(Subscription.amount < filters.lower_amount)

    return query

def apply_date_filters(query, filters):
    if filters.start_date:
        start, end = ist_day_range(filters.start_date)
        query = query.filter(Subscription.start_date.between(start, end))

    if filters.end_date:
        start, end = ist_day_range(filters.end_date)
        query = query.filter(Subscription.end_date.between(start, end))

    if filters.billing_date:
        start, end = ist_day_range(filters.billing_date)
        query = query.filter(Subscription.next_billing_date.between(start, end))

    return query

def apply_search_filters(query, filters):
    if not filters.search:
        return query

    keyword = f"%{filters.search.strip()}%"

    return (
        query
        .join(Category)
        .join(TransactionType)
        .join(Account, isouter=True)
        .join(PaymentMode)
        .filter(
            or_(
                Subscription.name.ilike(keyword),
                Subscription.description.ilike(keyword),
                Category.name.ilike(keyword),
                TransactionType.name.ilike(keyword),
                PaymentMode.name.ilike(keyword),
                Account.name.ilike(keyword),
            )
        )
    )

def build_subscription_query(base_query, filters):
    base_query = apply_basic_filters(base_query, filters)
    base_query = apply_date_filters(base_query, filters)
    base_query = apply_search_filters(base_query, filters)
    return base_query
