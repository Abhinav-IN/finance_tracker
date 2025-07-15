from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.models.transaction import Transaction
from api.models.category import Category
from api.models.transaction_type import TransactionType
from api.models.payment_mode import PaymentMode
from api.schemas.transaction import IncomeRequest, IncomeResponse, TransactionQueryParam
from api.services.lookup_create_service import get_or_create_category, get_or_create_paymentMode, get_or_create_transactionType
from datetime import datetime, time
from fastapi import Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session 
from zoneinfo import ZoneInfo

def create_income_service(user_income : IncomeRequest, 
    user: dict = Depends(require_roles("user", "admin")), 
    db : Session = Depends(get_db)):

    curr_category_id = get_or_create_category(user_income.category_name, user["id"], db)
    curr_transaction_type_id = get_or_create_transactionType(user_income.income_type_name, user["id"], db)
    curr_payment_mode_id = get_or_create_paymentMode(user_income.payment_mode_name, user["id"], db)
    
    new_income = Transaction(transaction_name = user_income.income_name,
                              amount = user_income.amount,
                              description = user_income.additional_note,
                              transaction_date = user_income.recieved_date,
                              user_id = user["id"],
                              category_id = curr_category_id,
                              transaction_type_id = curr_transaction_type_id,
                              payment_mode_id = curr_payment_mode_id,
                              is_expense = False,
                              is_income = True)
    db.add(new_income)
    try:
        db.commit()
        db.refresh(new_income)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in creation of income")
    

    return IncomeResponse(
        income_id = new_income.transaction_id,
        income_name = new_income.transaction_name,
        amount = new_income.amount,
        recieved_date = new_income.transaction_date,
        additional_note = new_income.description,
        income_type_id = new_income.transaction_type_id,
        income_type_name = new_income.transaction_type.transaction_type,
        category_id = new_income.category_id,
        category_name = new_income.category.category_name,
        payment_mode_id = new_income.payment_mode_id,
        payment_mode_name = new_income.payment_mode.payment_mode
)

def get_income_service(user: dict = Depends(require_roles("user", "admin")), 
                        db : Session = Depends(get_db),
                        filter_query : TransactionQueryParam = Depends()):
    curr_query = db.query(Transaction).filter(Transaction.user_id == user["id"], Transaction.is_income == True)
    if filter_query.transaction_id:
        curr_query = curr_query.filter(Transaction.transaction_id == filter_query.transaction_id)
    if filter_query.name:
        curr_query = curr_query.filter(Transaction.transaction_name.ilike(filter_query.name.strip()))
    if filter_query.exact_amount:
        curr_query = curr_query.filter(Transaction.amount == filter_query.exact_amount)
    if filter_query.greater_amount:
        curr_query = curr_query.filter(Transaction.amount > filter_query.greater_amount)
    if filter_query.lower_amount:
        curr_query = curr_query.filter(Transaction.amount < filter_query.lower_amount)
    if filter_query.date:
        ist = ZoneInfo("Asia/Kolkata")
        start_of_day = datetime.combine(filter_query.date, time.min).replace(tzinfo=ist)
        end_of_day = datetime.combine(filter_query.date, time.max).replace(tzinfo=ist)

        curr_query = curr_query.filter(
            Transaction.transaction_date.between(start_of_day, end_of_day)
        )
    if filter_query.search:
        curr_query = curr_query\
        .join(Category)\
        .join(TransactionType)\
        .join(PaymentMode)\
        .filter(
            or_(
                Transaction.transaction_name.ilike(f"%{filter_query.search}%"),
                Transaction.description.ilike(f"%{filter_query.search.strip()}%"),
                Category.category_name.ilike(f"%{filter_query.search.strip()}%"),
                TransactionType.transaction_type.ilike(f"%{filter_query.search.strip()}%"),
                PaymentMode.payment_mode.ilike(f"%{filter_query.search.strip()}%"),
            )
        )

    curr_query = curr_query.offset(filter_query.get_offset).limit(filter_query.limit)
    incomes = curr_query.all()
    
    response = []
    for i in incomes:
        response.append(IncomeResponse(
            income_id = i.transaction_id,
            income_name = i.transaction_name,
            amount = i.amount,
            recieved_date = i.transaction_date,
            additional_note = i.description,
            income_type_id = i.transaction_type_id,
            income_type_name = i.transaction_type.transaction_type,
            category_id = i.category_id,
            category_name = i.category.category_name,
            payment_mode_id = i.payment_mode_id,
            payment_mode_name = i.payment_mode.payment_mode
        ))
    
    return response

def update_income_service(
    income_id: int,
    income_update: IncomeRequest,
    user: dict = Depends(require_roles("user", "admin")), 
    db: Session = Depends(get_db)
):
    income_query = db.query(Transaction).filter(Transaction.transaction_id == income_id, Transaction.user_id == user['id'], Transaction.is_income == True) 

    existing_income = income_query.first()
    if not existing_income:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Income not found")

    curr_category_id = get_or_create_category(income_update.category_name, user["id"], db)
    curr_transaction_type_id = get_or_create_transactionType(income_update.income_type_name, user["id"], db)
    curr_payment_mode_id = get_or_create_paymentMode(income_update.payment_mode_name, user["id"], db)

    income_query.update({
        "amount": income_update.amount,
        "description": income_update.additional_note,
        "category_id": curr_category_id,
        "transaction_type_id": curr_transaction_type_id,
        "payment_mode_id" : curr_payment_mode_id
    }, synchronize_session=False)

    db.commit()
    db.refresh(existing_income)

    return IncomeResponse(
        income_id = existing_income.transaction_id,
        income_name = existing_income.transaction_name,
        amount = existing_income.amount,
        recieved_date = existing_income.transaction_date,
        additional_note = existing_income.description,
        income_type_id = existing_income.transaction_type_id,
        income_type_name = existing_income.transaction_type.transaction_type,
        category_id = existing_income.category_id,
        category_name = existing_income.category.category_name,
        payment_mode_id = existing_income.payment_mode_id,
        payment_mode_name = existing_income.payment_mode.payment_mode
)

def delete_income_service(income_id : int,
                    user: dict = Depends(require_roles("user", "admin")), 
                    db: Session = Depends(get_db)):
    income = db.query(Transaction).filter(Transaction.transaction_id == income_id, Transaction.is_income == True).first()

    if not income:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Income not found")

    if user["role"] != "admin" and income.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own income")

    db.delete(income)
    db.commit()
    return
