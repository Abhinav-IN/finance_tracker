from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.models.subscription import Subscription
from api.models.category import Category
from api.models.payment_mode import PaymentMode
from api.models.transaction_type import TransactionType
from api.schemas.subscription import SubscriptionRequest, SubscriptionQueryParam, SubscriptionResponse
from api.services.lookup_create_service import get_or_create_category, get_or_create_paymentMode, get_or_create_transactionType
from api.tasks.subscription import calculate_next_billing_date
from datetime import datetime, time
from fastapi import Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo

def create_subscription_service(
    user_subscription: SubscriptionRequest,
    user: dict = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db)
):
    curr_category_id = get_or_create_category(user_subscription.category_name, user["id"], db)
    curr_transaction_type_id = get_or_create_transactionType(user_subscription.expense_type_name, user["id"], db)
    curr_payment_mode_id = get_or_create_paymentMode(user_subscription.payment_mode_name, user["id"], db)

    #next_billing = calculate_next_billing_date(
        #start_date=user_subscription.start_date,
        #billing_cycle=user_subscription.billing_cycle.value,
        #end_date=user_subscription.end_date
    #)

    new_subscription = Subscription(
        subscription_name=user_subscription.subscription_name,
        amount=user_subscription.amount,
        description=user_subscription.description,
        currency=user_subscription.currency,
        billing_cycle=user_subscription.billing_cycle.value,
        start_date=user_subscription.start_date,
        end_date=user_subscription.end_date,
        next_billing_date="2025-07-13",
        user_id=user["id"],
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong while adding subscription to the database"
        )
    
    return SubscriptionResponse(
            subscription_id = new_subscription.subscription_id,
            subscription_name = new_subscription.subscription_name,
            amount = new_subscription.amount,
            start_date = new_subscription.start_date,
            end_date = new_subscription.end_date,
            next_billing_date = new_subscription.next_billing_date,
            last_paid_at = new_subscription.last_paid_at,
            description = new_subscription.description,
            currency = new_subscription.currency,
            billing_cycle = new_subscription.billing_cycle,
            expense_type_id = new_subscription.transaction_type_id,
            expense_type_name = new_subscription.transaction_type.transaction_type,
            category_id = new_subscription.category_id,
            category_name = new_subscription.category.category_name,
            payment_mode_id = new_subscription.payment_mode_id,
            payment_mode_name = new_subscription.payment_mode.payment_mode,
            is_active = new_subscription.is_active
    )

def get_subscription_service(filter_query : SubscriptionQueryParam,
                            user : dict = Depends(require_roles("user", "admin")),
                            db : Session = Depends(get_db)):
    curr_query = db.query(Subscription).filter(Subscription.user_id == user["id"])
    if filter_query.subscription_id:
        curr_query = curr_query.filter(Subscription.subscription_id == filter_query.subscription_id)
    if filter_query.name:
        curr_query = curr_query.filter(Subscription.subscription_name.ilike(filter_query.name.strip()))
    if filter_query.exact_amount:
        curr_query = curr_query.filter(Subscription.amount == filter_query.exact_amount)
    if filter_query.greater_amount:
        curr_query = curr_query.filter(Subscription.amount > filter_query.greater_amount)
    if filter_query.lower_amount:
        curr_query = curr_query.filter(Subscription.amount < filter_query.lower_amount)
    if filter_query.start_date:
        ist = ZoneInfo("Asia/Kolkata")
        start_of_day = datetime.combine(filter_query.start_date, time.min).replace(tzinfo=ist)
        end_of_day = datetime.combine(filter_query.start_date, time.max).replace(tzinfo=ist)

        curr_query = curr_query.filter(
            Subscription.start_date.between(start_of_day, end_of_day)
        )
    if filter_query.end_date:
        ist = ZoneInfo("Asia/Kolkata")
        start_of_day = datetime.combine(filter_query.end_date, time.min).replace(tzinfo=ist)
        end_of_day = datetime.combine(filter_query.end_date, time.max).replace(tzinfo=ist)

        curr_query = curr_query.filter(
            Subscription.end_date.between(start_of_day, end_of_day)
        )
    if filter_query.billing_date:
        ist = ZoneInfo("Asia/Kolkata")
        start_of_day = datetime.combine(filter_query.billing_date, time.min).replace(tzinfo=ist)
        end_of_day = datetime.combine(filter_query.billing_date, time.max).replace(tzinfo=ist)

        curr_query = curr_query.filter(
            Subscription.next_billing_date.between(start_of_day, end_of_day)
        )
    
    if filter_query.search:
        curr_query = curr_query\
        .join(Category)\
        .join(TransactionType)\
        .join(PaymentMode)\
        .filter(
            or_(
                Subscription.description.ilike(f"%{filter_query.search.strip()}%"),
                Category.category_name.ilike(f"%{filter_query.search.strip()}%"),
                TransactionType.transaction_type.ilike(f"%{filter_query.search.strip()}%"),
                PaymentMode.payment_mode.ilike(f"%{filter_query.search.strip()}%"),
            )
        )

    curr_query = curr_query.offset(filter_query.get_offset).limit(filter_query.limit)
    subscriptions = curr_query.all()
    
    response = []
    for s in subscriptions:
        response.append(SubscriptionResponse(
            subscription_id = s.subscription_id,
            subscription_name = s.subscription_name,
            amount = s.amount,
            start_date = s.start_date,
            end_date = s.end_date,
            next_billing_date = s.next_billing_date,
            last_paid_at = s.last_paid_at,
            description = s.description,
            currency = s.currency,
            billing_cycle = s.billing_cycle,
            expense_type_id = s.transaction_type_id,
            expense_type_name = s.transaction_type.transaction_type,
            category_id = s.category_id,
            category_name = s.category.category_name,
            payment_mode_id = s.payment_mode_id,
            payment_mode_name = s.payment_mode.payment_mode,
            is_active = s.is_active
        ))
    
    return response

def update_subscription_service(subscription_id : int,
                                user_subscription : SubscriptionRequest,
                                user : dict = Depends(require_roles("admin", "user")),
                                db : Session = Depends(get_db)):
    curr_subscription_query = db.query(Subscription).filter(Subscription.subscription_id == subscription_id, Subscription.user_id == user["id"])
    curr_subscription = curr_subscription_query.first()

    if not curr_subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription Not Found")
    
    curr_category_id = get_or_create_category(user_subscription.category_name, user["id"], db)
    curr_expense_type_id = get_or_create_transactionType(user_subscription.expense_type_name, user["id"], db)
    curr_payment_mode_id = get_or_create_paymentMode(user_subscription.payment_mode_name, user["id"], db)

    next_billing = calculate_next_billing_date(
        start_date=user_subscription.start_date,
        billing_cycle=user_subscription.billing_cycle.value,
        end_date=user_subscription.end_date
    )

    curr_subscription_query = curr_subscription_query.update({
        "subscription_name" : user_subscription.subscription_name,
        "amount" : user_subscription.amount,
        "description" : user_subscription.description,
        "currency" : user_subscription.currency,
        "billing_cycle" : user_subscription.billing_cycle,
        "start_date" : user_subscription.start_date,
        "end_date" : user_subscription.end_date,
        "next_billing_date" : next_billing,
        "category_id" : curr_category_id,
        "transaction_type_id" : curr_expense_type_id,
        "payment_mode_id" : curr_payment_mode_id,
        "is_active" : user_subscription.is_active
    }, synchronize_session=False)

    try:
        db.commit()
        db.refresh(curr_subscription)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something went wrong in updating subscription")
    
    return SubscriptionResponse(
            subscription_id = curr_subscription.subscription_id,
            subscription_name = curr_subscription.subscription_name,
            amount = curr_subscription.amount,
            start_date = curr_subscription.start_date,
            end_date = curr_subscription.end_date,
            next_billing_date = curr_subscription.next_billing_date,
            last_paid_at = curr_subscription.last_paid_at,
            description = curr_subscription.description,
            currency = curr_subscription.currency,
            billing_cycle = curr_subscription.billing_cycle,
            expense_type_id = curr_subscription.transaction_type_id,
            expense_type_name = curr_subscription.transaction_type.transaction_type,
            category_id = curr_subscription.category_id,
            category_name = curr_subscription.category.category_name,
            payment_mode_id = curr_subscription.payment_mode_id,
            payment_mode_name = curr_subscription.payment_mode.payment_mode,
            is_active = curr_subscription.is_active
    )

def delete_subscription_service(subscription_id : int,
                user: dict = Depends(require_roles("user", "admin")), 
                db : Session = Depends(get_db)):

    subscription = db.query(Subscription).filter(Subscription.subscription_id == subscription_id).first()

    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")
    
    if user["role"] != "admin" and subscription.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own subscription")
    
    db.delete(subscription)
    db.commit()
    return 
