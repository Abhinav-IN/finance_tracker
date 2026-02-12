from api.database.session import SessionLocal
from api.models.subscription import Subscription
from api.models.transaction import Transaction
from api.tasks.email_task import reminder_subscription_email, subscription_email
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

def process_subscription_billing():
    now = ist_now()
    today = now.date()
    tomorrow = today + timedelta(days=1)

    with SessionLocal() as db:

        reminder_subs = db.query(Subscription).filter(Subscription.next_billing_date == tomorrow, Subscription.is_active.is_(True)).all()

        for sub in reminder_subs:
            reminder_subscription_email.delay(to_email=sub.user.email, subscription_name=sub.name, amount=sub.amount)

        due_subs = db.query(Subscription).filter(Subscription.next_billing_date == today, Subscription.is_active.is_(True)).all()

        for sub in due_subs:
            transaction = Transaction(
                title=sub.name,
                amount=sub.amount,
                description=f"Auto billed for subscription: {sub.name}",
                date=now,
                user_id=sub.user_id,
                account_id=sub.account_id,
                category_id=sub.category_id,
                transaction_type_id=sub.transaction_type_id,
                payment_mode_id=sub.payment_mode_id,
                direction=TransactionDirection.EXPENSE
            )

            db.add(transaction)

            subscription_email.delay(to_email=sub.user.email, subscription_name=sub.name, amount=sub.amount)

            sub.last_paid_at = now
            sub.next_billing_date = calculate_next_billing_date(start_date=sub.start_date, billing_period=sub.billing_period, end_date=sub.end_date)

        try:
            db.commit()
            db.refresh(transaction)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in processing subscription billing")

def process_subscriptions_for_today():
    db = SessionLocal()

    try:
        subscriptions = (
            db.query(Subscription)
            .filter(
                Subscription.is_active == True,
                Subscription.next_billing_date <= ist_now()
            )
            .all()
        )

        for sub in subscriptions:
            next_date = calculate_next_billing_date(
                start_date=sub.start_date,
                end_date=sub.end_date,
                billing_period=sub.billing_period
            )

            sub.next_billing_date = next_date

        db.commit()

    finally:
        db.close()