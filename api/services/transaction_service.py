from api.models.transaction import Transaction
from api.schemas.transaction import TransactionCreate, TransactionResponse, TransactionQueryParam
from api.services.lookup_create_service import get_or_create_category, get_or_create_paymentMode, get_or_create_transactionType, get_account_id
from api.utils.enums import TransactionDirection
from api.utils.transaction_filter import apply_transaction_filters
from api.utils.time import ist_now
from datetime import timedelta
from fastapi import HTTPException, status
from math import ceil
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

def create_transaction_service(user_transaction : TransactionCreate, user: dict, db : Session):

    curr_category_id = get_or_create_category(user_transaction.category_name, user["id"], db)
    curr_transaction_type_id = get_or_create_transactionType(user_transaction.transaction_type_name, db)
    curr_payment_mode_id = get_or_create_paymentMode(user_transaction.payment_mode_name, db)
    curr_account_id = get_account_id(user_transaction.account_name, user["id"], db)
    
    new_transaction = Transaction(title = user_transaction.title,
                              amount = user_transaction.amount,
                              description = user_transaction.description,
                              date = user_transaction.date,
                              account_id = curr_account_id,
                              user_id = user["id"],
                              category_id = curr_category_id,
                              transaction_type_id = curr_transaction_type_id,
                              payment_mode_id = curr_payment_mode_id,
                              direction = user_transaction.direction)
    
    try:
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in creation of trasnaction")

    return TransactionResponse.model_validate(new_transaction)

def get_transaction_service(user: dict, db: Session, filter_query: TransactionQueryParam):
    base_query = db.query(Transaction).filter(Transaction.user_id == user["id"])
    base_query = base_query.options(
        joinedload(Transaction.category),
        joinedload(Transaction.payment_mode),
    )

    query = apply_transaction_filters(base_query, filter_query)

    total_records = query.count()

    transactions = (query.offset(filter_query.get_offset).limit(filter_query.limit).all())

    result_transactions = []
    for tx in transactions:
        resp = TransactionResponse.model_validate(tx)
        resp.category_name = tx.category.name if tx.category else None
        resp.payment_mode_name = tx.payment_mode.name if tx.payment_mode else None
        result_transactions.append(resp)

    return {
        "total_pages": max(1, ceil(total_records / filter_query.limit)) if filter_query.limit else 1,
        "current_page": filter_query.page,
        "total_transactions": total_records,
        "transactions": result_transactions,
    }

def update_transaction_service(transaction_id: int, transaction_update: TransactionCreate, user: dict, db: Session):
    transaction_query = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == user['id'])
     
    existing_transaction = transaction_query.first()
    if not existing_transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    curr_category_id = get_or_create_category(transaction_update.category_name, user["id"], db)
    curr_transaction_type_id = get_or_create_transactionType(transaction_update.transaction_type_name, db)
    curr_payment_mode_id = get_or_create_paymentMode(transaction_update.payment_mode_name, db)
    curr_account_id = get_account_id(transaction_update.account_name, user["id"], db)

    transaction_query.update({
        "title": transaction_update.title,
        "date": transaction_update.date,
        "amount": transaction_update.amount,
        "description": transaction_update.description,
        "account_id": curr_account_id,
        "category_id": curr_category_id,
        "transaction_type_id": curr_transaction_type_id,
        "payment_mode_id" : curr_payment_mode_id
    }, synchronize_session=False)
    
    try:
        db.commit()
        db.refresh(existing_transaction)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transaction not updated! Bad request")

    return TransactionResponse.model_validate(existing_transaction)

def delete_transaction_service(transaction_id : int, user: dict, db: Session):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == user["id"]).first()

    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    if user["role"] != "admin" and transaction.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own transaction")

    db.delete(transaction)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something went wrong transaction not deleted")
    return

def expense_overview_services(user: dict, db: Session):
    thirty_days_ago = ist_now() - timedelta(days=30)
    total_expense = db.query(Transaction).filter(
        Transaction.user_id == user["id"],
        Transaction.direction == TransactionDirection.EXPENSE,
        Transaction.date >= thirty_days_ago
    ).with_entities(func.sum(Transaction.amount)).scalar() or 0

    seven_days_ago = ist_now() - timedelta(days=7)
    total_expense_7_days = db.query(Transaction).filter(
        Transaction.user_id == user["id"],
        Transaction.direction == TransactionDirection.EXPENSE,
        Transaction.date >= seven_days_ago
    ).with_entities(func.sum(Transaction.amount)).scalar() or 0

    current_month_start = ist_now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    total_expense_current_month = db.query(Transaction).filter(
        Transaction.user_id == user["id"],
        Transaction.direction == TransactionDirection.EXPENSE,
        Transaction.date >= current_month_start
    ).with_entities(func.sum(Transaction.amount)).scalar() or 0
    average_monthly_expense = total_expense_current_month / ((ist_now()).day or 1)

    current_week_start = ist_now() - timedelta(days=ist_now().weekday())
    total_expense_current_week = db.query(Transaction).filter(
        Transaction.user_id == user["id"],
        Transaction.direction == TransactionDirection.EXPENSE,
        Transaction.date >= current_week_start
    ).with_entities(func.sum(Transaction.amount)).scalar() or 0
    average_weekly_expense = total_expense_current_week / ((ist_now()).weekday() + 1 or 1)
    
    return {
        "total_expense_last_30_days": total_expense,
        "total_expense_last_7_days": total_expense_7_days,
        "total_expense_current_month": total_expense_current_month,
        "average_monthly_expense": average_monthly_expense,
        "average_weekly_expense": average_weekly_expense
    }

def income_overview_services(user: dict, db: Session):
    thirty_days_ago = ist_now() - timedelta(days=30)
    total_income = db.query(Transaction).filter(
        Transaction.user_id == user["id"],
        Transaction.direction == TransactionDirection.INCOME,
        Transaction.date >= thirty_days_ago
    ).with_entities(func.sum(Transaction.amount)).scalar() or 0

    seven_days_ago = ist_now() - timedelta(days=7)
    total_income_7_days = db.query(Transaction).filter(
        Transaction.user_id == user["id"],
        Transaction.direction == TransactionDirection.INCOME,
        Transaction.date >= seven_days_ago
    ).with_entities(func.sum(Transaction.amount)).scalar() or 0

    current_month_start = ist_now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    total_income_current_month = db.query(Transaction).filter(
        Transaction.user_id == user["id"],
        Transaction.direction == TransactionDirection.INCOME,
        Transaction.date >= current_month_start
    ).with_entities(func.sum(Transaction.amount)).scalar() or 0
    average_monthly_income = total_income_current_month / ((ist_now()).day or 1)

    current_week_start = ist_now() - timedelta(days=ist_now().weekday())
    total_income_current_week = db.query(Transaction).filter(
        Transaction.user_id == user["id"],
        Transaction.direction == TransactionDirection.INCOME,
        Transaction.date >= current_week_start
    ).with_entities(func.sum(Transaction.amount)).scalar() or 0
    average_weekly_income = total_income_current_week / ((ist_now()).weekday() + 1 or 1)
    
    return {
        "total_income_last_30_days": total_income,
        "total_income_last_7_days": total_income_7_days,
        "total_income_current_month": total_income_current_month,
        "average_monthly_income": average_monthly_income,
        "average_weekly_income": average_weekly_income
    }
