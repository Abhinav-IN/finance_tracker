from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.models.transaction import Transaction
from api.models.category import Category
from api.models.transaction_type import TransactionType
from api.models.payment_mode import PaymentMode
from api.models.account import Account
from api.schemas.transaction import ExpenseRequest, ExpenseResponse, TransactionQueryParam
from api.services.lookup_create_service import get_or_create_category, get_or_create_paymentMode, get_or_create_transactionType, get_account_id
from datetime import datetime, time, timedelta
from fastapi import Depends, HTTPException, status
from math import ceil
from sqlalchemy import or_, func
from sqlalchemy.orm import Session 
from zoneinfo import ZoneInfo

def create_expense_service(user_expense : ExpenseRequest, 
    user: dict = Depends(require_roles("user", "admin")), 
    db : Session = Depends(get_db)):

    curr_category_id = get_or_create_category(user_expense.category_name, user["id"], db)
    curr_transaction_type_id = get_or_create_transactionType(user_expense.expense_type_name, user["id"], db)
    curr_payment_mode_id = get_or_create_paymentMode(user_expense.payment_mode_name, user["id"], db)
    curr_account_id = get_account_id(user_expense.account_name, user["id"], db)
    
    new_expense = Transaction(transaction_name = user_expense.expense_name,
                              amount = user_expense.price,
                              description = user_expense.additional_note,
                              transaction_date = user_expense.expense_date,
                              account_linked = curr_account_id,
                              user_id = user["id"],
                              category_id = curr_category_id,
                              transaction_type_id = curr_transaction_type_id,
                              payment_mode_id = curr_payment_mode_id,
                              is_expense = True,
                              is_income = False)
    
    try:
        db.add(new_expense)
        db.commit()
    except Exception as e:
        db.rollback(new_expense)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in creation of expense")


    return ExpenseResponse(
        expense_id = new_expense.transaction_id,
        expense_name = new_expense.transaction_name,
        price = new_expense.amount,
        expense_date = new_expense.transaction_date,
        additional_note = new_expense.description,
        account_id = new_expense.account_linked,
        account_name = getattr(new_expense.account, "account_name", None),
        expense_type_id = new_expense.transaction_type_id,
        expense_type_name = new_expense.transaction_type.transaction_type,
        category_id = new_expense.category_id,
        category_name = new_expense.category.category_name,
        payment_mode_id = new_expense.payment_mode_id,
        payment_mode_name = new_expense.payment_mode.payment_mode
    )

def get_expense_service(
    user: dict = Depends(require_roles("user", "admin")), 
    db: Session = Depends(get_db),
    filter_query: TransactionQueryParam = Depends()
):
    base_query = db.query(Transaction).filter(
        Transaction.user_id == user["id"], 
        Transaction.is_expense == True
    )

    if filter_query.transaction_id:
        base_query = base_query.filter(Transaction.transaction_id == filter_query.transaction_id)
    if filter_query.exact_amount:
        base_query = base_query.filter(Transaction.amount == filter_query.exact_amount)
    if filter_query.greater_amount:
        base_query = base_query.filter(Transaction.amount > filter_query.greater_amount)
    if filter_query.lower_amount:
        base_query = base_query.filter(Transaction.amount < filter_query.lower_amount)
    if filter_query.date:
        ist = ZoneInfo("Asia/Kolkata")
        start_of_day = datetime.combine(filter_query.date, time.min).replace(tzinfo=ist)
        end_of_day = datetime.combine(filter_query.date, time.max).replace(tzinfo=ist)
        base_query = base_query.filter(Transaction.transaction_date.between(start_of_day, end_of_day))
    if filter_query.search:
        base_query = base_query\
            .join(Category)\
            .join(Account)\
            .join(TransactionType)\
            .join(PaymentMode)\
            .filter(
                or_(
                    Transaction.transaction_name.ilike(f"%{filter_query.search.strip()}%"),
                    Transaction.description.ilike(f"%{filter_query.search.strip()}%"),
                    Category.category_name.ilike(f"%{filter_query.search.strip()}%"),
                    Account.account_name.ilike(f"%{filter_query.search.strip()}%"),
                    TransactionType.transaction_type.ilike(f"%{filter_query.search.strip()}%"),
                    PaymentMode.payment_mode.ilike(f"%{filter_query.search.strip()}%"),
                )
            )

    total_records = base_query.count()

    curr_query = base_query.offset(filter_query.get_offset).limit(filter_query.limit)
    expenses = curr_query.all()

    response = [
        ExpenseResponse(
            expense_id=e.transaction_id,
            expense_name=e.transaction_name,
            price=e.amount,
            expense_date=e.transaction_date,
            account_id=e.account_linked,
            account_name=getattr(e.account, "account_name", None),
            additional_note=e.description,
            expense_type_id=e.transaction_type_id,
            expense_type_name=e.transaction_type.transaction_type,
            category_id=e.category_id,
            category_name=e.category.category_name,
            payment_mode_id=e.payment_mode_id,
            payment_mode_name=e.payment_mode.payment_mode
        )
        for e in expenses
    ]

    return {
        "total_pages": ceil(total_records / filter_query.limit) if filter_query.limit else 1,
        "current_page": filter_query.page,
        "total_expenses": total_records,
        "expenses": response
    }

def update_expense_service(
    expense_id: int,
    expense_update: ExpenseRequest,
    user: dict = Depends(require_roles("user", "admin")), 
    db: Session = Depends(get_db)
):
    expense_query = db.query(Transaction).filter(Transaction.transaction_id == expense_id, Transaction.user_id == user['id'], Transaction.is_expense == True) 

    existing_expense = expense_query.first()
    if not existing_expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

    curr_category_id = get_or_create_category(expense_update.category_name, user["id"], db)
    curr_transaction_type_id = get_or_create_transactionType(expense_update.expense_type_name, user["id"], db)
    curr_payment_mode_id = get_or_create_paymentMode(expense_update.payment_mode_name, user["id"], db)
    curr_account_id = get_account_id(expense_update.account_name, user["id"], db)

    expense_query.update({
        "amount": expense_update.price,
        "description": expense_update.additional_note,
        "account_linked": curr_account_id,
        "category_id": curr_category_id,
        "transaction_type_id": curr_transaction_type_id,
        "payment_mode_id" : curr_payment_mode_id
    }, synchronize_session=False)

    db.commit()
    db.refresh(existing_expense)

    return ExpenseResponse(
        expense_id = existing_expense.transaction_id,
        expense_name = existing_expense.transaction_name,
        price = existing_expense.amount,
        expense_date = existing_expense.transaction_date,
        account_id = existing_expense.account_linked,
        account_name = getattr(existing_expense.account, "account_name", None),
        additional_note = existing_expense.description,
        expense_type_id = existing_expense.transaction_type_id,
        expense_type_name = existing_expense.transaction_type.transaction_type,
        category_id = existing_expense.category_id,
        category_name = existing_expense.category.category_name,
        payment_mode_id = existing_expense.payment_mode_id,
        payment_mode_name = existing_expense.payment_mode.payment_mode
    )

def delete_expense_service(expense_id : int,
                    user: dict = Depends(require_roles("user", "admin")), 
                    db: Session = Depends(get_db)):
    expense = db.query(Transaction).filter(Transaction.transaction_id == expense_id, Transaction.is_expense == True).first()

    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

    if user["role"] != "admin" and expense.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own expense")

    db.delete(expense)
    db.commit()
    return

def overview_services(user: dict = Depends(require_roles("user", "admin")), db: Session = Depends(get_db)):
    thirty_days_ago = datetime.now(ZoneInfo("Asia/Kolkata")) - timedelta(days=30)
    total_expense = db.query(Transaction).filter(
        Transaction.user_id == user["id"],
        Transaction.is_expense == True,
        Transaction.transaction_date >= thirty_days_ago
    ).with_entities(func.sum(Transaction.amount)).scalar() or 0

    seven_days_ago = datetime.now(ZoneInfo("Asia/Kolkata")) - timedelta(days=7)
    total_expense_7_days = db.query(Transaction).filter(
        Transaction.user_id == user["id"],
        Transaction.is_expense == True,
        Transaction.transaction_date >= seven_days_ago
    ).with_entities(func.sum(Transaction.amount)).scalar() or 0

    current_month_start = datetime.now(ZoneInfo("Asia/Kolkata")).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    total_expense_current_month = db.query(Transaction).filter(
        Transaction.user_id == user["id"],
        Transaction.is_expense == True,
        Transaction.transaction_date >= current_month_start
    ).with_entities(func.sum(Transaction.amount)).scalar() or 0
    average_monthly_expense = total_expense_current_month / (datetime.now(ZoneInfo("Asia/Kolkata")).day or 1)

    current_week_start = datetime.now(ZoneInfo("Asia/Kolkata")) - timedelta(days=datetime.now(ZoneInfo("Asia/Kolkata")).weekday())
    total_expense_current_week = db.query(Transaction).filter(
        Transaction.user_id == user["id"],
        Transaction.is_expense == True,
        Transaction.transaction_date >= current_week_start
    ).with_entities(func.sum(Transaction.amount)).scalar() or 0
    average_weekly_expense = total_expense_current_week / (datetime.now(ZoneInfo("Asia/Kolkata")).weekday() + 1 or 1)
    
    return {
        "total_expense_last_30_days": total_expense,
        "total_expense_last_7_days": total_expense_7_days,
        "total_expense_current_month": total_expense_current_month,
        "average_monthly_expense": average_monthly_expense,
        "average_weekly_expense": average_weekly_expense
    }
