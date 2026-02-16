from api.models.subscription import Subscription
from api.schemas.subscription import SubscriptionCreate, SubscriptionQueryParam, SubscriptionResponse
from api.services.lookup_create_service import get_or_create_category, get_or_create_paymentMode, get_or_create_transactionType, get_account_id
from api.tasks.subscription import calculate_next_billing_date
from api.utils.subscription_filter import build_subscription_query
from api.utils.time import ist_now
from datetime import timedelta
from fastapi import HTTPException, status
from math import ceil
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

def create_subscription_service(user_subscription: SubscriptionCreate, user_id: int, db: Session ):
    curr_category_id = get_or_create_category(user_subscription.category_name, user_id, db)
    curr_transaction_type_id = get_or_create_transactionType(user_subscription.transaction_type_name, db)
    curr_payment_mode_id = get_or_create_paymentMode(user_subscription.payment_mode_name, db)
    curr_account_id = get_account_id(user_subscription.account_name, user_id, db)


    next_billing = calculate_next_billing_date(
        start_date=user_subscription.start_date,
        billing_period=user_subscription.billing_period,
        end_date=user_subscription.end_date
    )

    new_subscription = Subscription(
        name=user_subscription.name,
        amount=user_subscription.amount,
        description=user_subscription.description,
        currency=user_subscription.currency,
        account_id=curr_account_id,
        billing_period=user_subscription.billing_period,
        start_date=user_subscription.start_date,
        end_date=user_subscription.end_date,
        next_billing_date=next_billing,
        user_id=user_id,
        category_id=curr_category_id,
        transaction_type_id=curr_transaction_type_id,
        payment_mode_id=curr_payment_mode_id,
        is_active=user_subscription.is_active,
        last_paid_at=user_subscription.last_paid_at
    )

    db.add(new_subscription)
    try:
        db.commit()
        db.refresh(new_subscription)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something went wrong while adding subscription to the database")
    
    return new_subscription

def get_subscription_service(filter_query: SubscriptionQueryParam, user_id: int, db: Session):
    base_query = db.query(Subscription).filter(Subscription.user_id == user_id)
    base_query = base_query.options(
        joinedload(Subscription.category),
        joinedload(Subscription.payment_mode),
        joinedload(Subscription.account),
    )
    query = build_subscription_query(base_query, filter_query)
    total_records = query.count()
    subscriptions = (query.offset(filter_query.get_offset).limit(filter_query.limit).all())

    response_subscriptions = []
    for sx in subscriptions:
        resp = SubscriptionResponse.model_validate(sx)
        resp.category_name = sx.category.name if sx.category else None
        resp.payment_mode_name = sx.payment_mode.name if sx.payment_mode else None
        resp.account_name = sx.account.name if sx.account else None
        response_subscriptions.append(resp)

    return {
        "total_pages": max(1, ceil(total_records / filter_query.limit)) if filter_query.limit else 1,
        "current_page": filter_query.page,
        "total_subscriptions": total_records,
        "subscriptions": response_subscriptions
    }

def update_subscription_service(subscription_id : int, user_subscription : SubscriptionCreate, user_id : int, db : Session ):
    curr_subscription_query = db.query(Subscription).filter(Subscription.id == subscription_id, Subscription.user_id == user_id)
    curr_subscription = curr_subscription_query.first()

    if not curr_subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription Not Found")
    
    curr_category_id = get_or_create_category(user_subscription.category_name, user_id, db)
    curr_transaction_type_id = get_or_create_transactionType(user_subscription.transaction_type_name, db)
    curr_payment_mode_id = get_or_create_paymentMode(user_subscription.payment_mode_name, db)
    curr_account_id = get_account_id(user_subscription.account_name, user_id, db)

    next_billing = calculate_next_billing_date(start_date=user_subscription.start_date,
        billing_period=user_subscription.billing_period,
        end_date=user_subscription.end_date
    )

    curr_subscription_query = curr_subscription_query.update({
        "name" : user_subscription.name,
        "amount" : user_subscription.amount,
        "description" : user_subscription.description,
        "currency" : user_subscription.currency,
        "billing_period" : user_subscription.billing_period,
        "start_date" : user_subscription.start_date,
        "end_date" : user_subscription.end_date,
        "next_billing_date" : next_billing,
        "account_id" : curr_account_id,
        "category_id" : curr_category_id,
        "transaction_type_id" : curr_transaction_type_id,
        "payment_mode_id" : curr_payment_mode_id,
        "is_active" : user_subscription.is_active
    }, synchronize_session=False)

    try:
        db.commit()
        db.refresh(curr_subscription)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something went wrong in updating subscription")
    
    return curr_subscription

def delete_subscription_service(subscription_id : int, user: dict, db : Session ):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()

    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
    
    if user["role"] != "admin" and subscription.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own subscription")
    
    db.delete(subscription)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in deleting the subscription")
    return 

def overview_services(user_id: int, db : Session):
    thirty_days_ago = ist_now() - timedelta(days=30)
    total_subscription = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.start_date >= thirty_days_ago
    ).with_entities(func.sum(Subscription.amount)).scalar() or 0

    seven_days_ago = ist_now() - timedelta(days=7)
    total_subscription_7_days = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.start_date >= seven_days_ago
    ).with_entities(func.sum(Subscription.amount)).scalar() or 0

    current_month_start = ist_now().replace(day=1)
    total_subscription_current_month = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.start_date >= current_month_start
    ).with_entities(func.sum(Subscription.amount)).scalar() or 0
    average_monthly_subscription = total_subscription_current_month / (ist_now().day or 1)

    current_week_start = ist_now() - timedelta(days=ist_now().weekday())
    total_subscription_current_week = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.start_date >= current_week_start
    ).with_entities(func.sum(Subscription.amount)).scalar() or 0
    average_weekly_subscription = total_subscription_current_week / (ist_now().weekday() + 1 or 1)

    return {
        "total_subscription_last_30_days": total_subscription,
        "total_subscription_last_7_days": total_subscription_7_days,
        "total_subscription_current_month": total_subscription_current_month,
        "average_monthly_subscription": average_monthly_subscription,
        "average_weekly_subscription": average_weekly_subscription
    }
