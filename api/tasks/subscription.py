from api.database.session import SessionLocal
from api.models.subscription import Subscription
from api.models.transaction import Transaction
from api.tasks.email_task import reminder_subscription_email, subscription_email
import datetime
from dateutil.relativedelta import relativedelta
from zoneinfo import ZoneInfo

def calculate_next_billing_date(
    start_date: datetime.datetime,
    billing_cycle: str,
    end_date: datetime.datetime = None
) -> datetime.datetime | None:
    tz = ZoneInfo("Asia/Kolkata")
    today = datetime.datetime.now(tz)

    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=tz)

    if end_date and end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=tz)

    cycle_map = {
        "weekly": relativedelta(weeks=1),
        "quaterly": relativedelta(months=3),
        "half_yearly": relativedelta(months=6),
        "yearly": relativedelta(years=1),
        "one_time": None,
        "monthly": relativedelta(months=1)
    }

    interval = cycle_map.get(billing_cycle)
    if interval is None:
        return None

    next_date = start_date
    while next_date <= today:
        next_date += interval

    if end_date and next_date > end_date:
        return None

    return next_date


def get_next_billing_date():
    now = datetime.datetime.now(ZoneInfo("Asia/Kolkata"))
    today = now.date()
    tomorrow = today + datetime.timedelta(days=1)

    with SessionLocal() as db:
        reminder_subs = db.query(Subscription).filter(
            Subscription.next_billing_date == tomorrow,
            Subscription.is_active == True
        ).all()

        for sub in reminder_subs:
            reminder_subscription_email.delay(
                to_email=sub.user.email,
                subscription_name=sub.subscription_name,
                amount=sub.amount
            )

        due_subs = db.query(Subscription).filter(
            Subscription.next_billing_date == today,
            Subscription.is_active == True
        ).all()

        for sub in due_subs:
            new_expense = Transaction(
                transaction_name=sub.subscription_name,
                amount=sub.amount,
                description=f"Auto billed for subscription: {sub.subscription_name}",
                transaction_date=now,
                account_linked=sub.account_linked,
                user_id=sub.user_id,
                category_id=sub.category_id,
                transaction_type_id=sub.transaction_type_id,
                payment_mode_id=sub.payment_mode_id,
                is_expense=True,
                is_income=False
            )
            db.add(new_expense)

            subscription_email.delay(
                to_email=sub.user.email,
                subscription_name=sub.subscription_name,
                amount=sub.amount
            )

            sub.last_paid_at = now
            sub.next_billing_date = calculate_next_billing_date(
                start_date=sub.start_date,
                billing_cycle=sub.billing_cycle,
                end_date=sub.end_date
            )

        db.commit()
