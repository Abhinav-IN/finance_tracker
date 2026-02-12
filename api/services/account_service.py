from api.models.account import Account
from api.models.transaction import Transaction
from api.schemas.transaction import TransactionResponse
from api.schemas.account import accountRequest, accountResponse, AccountQueryParam
from api.utils.enums import TransactionDirection
from fastapi import HTTPException, status
from math import ceil
from sqlalchemy import func
from sqlalchemy.orm import Session

def create_account_service(user_account : accountRequest, user_id : int, db : Session):
    new_account = Account(user_id=user_id, name=user_account.name, type=user_account.type,
                          bank_name=user_account.bank_name, balance_amount=user_account.balance_amount, is_active=user_account.is_active)
    db.add(new_account)

    try:
        db.commit()
        db.refresh(new_account)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something went wrong in creating account")
    
    return new_account

def get_account_service(user_id : int, db : Session):
    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    return accounts

def update_account_service(account_id : int , user_account : accountRequest, db : Session):
    curr_account_query = db.query(Account).filter(Account.id == account_id)
    curr_account = curr_account_query.first()

    if not curr_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    curr_account_query.update({
        "name" : user_account.name,
        "type" : user_account.type,
        "bank_name" : user_account.bank_name,
        "is_active" : user_account.is_active,
        "balance_amount" : user_account.balance_amount
    }, synchronize_session=False)

    try:
        db.commit()
        db.refresh(curr_account)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something went wrong in updating account")
    
    return curr_account

def delete_account_service(account_id : int, user : dict, db : Session):
    account = db.query(Account).filter(Account.id == account_id).first()

    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    if user["role"] != "admin" and account.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own account")

    db.delete(account)

    try:
        db.commit()
        return
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in deleting account")

def show_transactions(account_id : int, user_id : int, db : Session, filter_query : AccountQueryParam):
    base_query = db.query(Transaction).filter(Transaction.user_id == user_id, Transaction.account_id == account_id, Transaction.direction == filter_query.direction)
    total_records = base_query.count()
    curr_query = base_query.offset(filter_query.get_offset).limit(filter_query.limit)
    transactions = curr_query.all()

    response = [
        TransactionResponse(
            title=t.title,
            date=t.date,
            amount=t.amount,
            direction=t.direction,
            description=t.description,
            id=t.id,
            category_id=t.category_id,
            payment_mode_id=t.payment_mode_id,
            account_id=t.account_id
        )
        for t in transactions
    ]

    return {
        "total_pages": ceil(total_records / filter_query.limit) if filter_query.limit else 1,
        "current_page": filter_query.page,
        "total_transactions": total_records,
        "transactions": response
    }

def overview_account_service(account_id: int,user_id: int,db: Session):
    total_income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.direction == TransactionDirection.INCOME,
        Transaction.account_id == account_id
    ).scalar() or 0

    total_expense = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.direction == TransactionDirection.EXPENSE,
        Transaction.account_id == account_id
    ).scalar() or 0

    curr_account = db.query(Account).filter(Account.id == account_id, Account.user_id == user_id).first()

    if not curr_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    curr_account.balance_amount = total_income - total_expense

    return accountResponse.model_validate(curr_account)