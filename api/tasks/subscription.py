from api.database.session import SessionLocal
from api.models.subscription import Subscription
from api.models.transaction import Transaction
from api.utils.enums import BillingPeriod, TransactionDirection
from api.utils.time import IST, ist_now
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from fastapi import HTTPException, status


def calculate_next_billing_date(start_date: datetime, billing_period: BillingPeriod, end_date: datetime = None) -> datetime | None:
    now = ist_now()

    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=IST)

    if end_date and end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=IST)

    interval_map = {
        BillingPeriod.WEEKLY: relativedelta(weeks=1),
        BillingPeriod.MONTHLY: relativedelta(months=1),
        BillingPeriod.QUATERLY: relativedelta(months=3),
        BillingPeriod.HALF_YEARLY: relativedelta(months=6),
        BillingPeriod.YEARLY: relativedelta(years=1),
        BillingPeriod.ONE_TIME: None,
    }

    interval = interval_map[billing_period]

    if interval is None:
        return None

    next_date = start_date
    while next_date <= now:
        next_date += interval

    if end_date and next_date > end_date:
        return None

    return next_date