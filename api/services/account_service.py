from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.models.account import Account
from api.models.transaction import Transaction
from api.schemas.transaction import IncomeResponse, ExpenseResponse
from api.schemas.account import accountRequest, accountResponse, AccountQueryParam
from fastapi import Depends, HTTPException, status
from math import ceil
from sqlalchemy import func
from sqlalchemy.orm import Session

def create_account_service(user_account : accountRequest, user : dict = Depends(require_roles("user", "admin")), db : Session = Depends(get_db)):
    new_account = Account(user_id=user["id"], account_name=user_account.account_name, account_type=user_account.account_type,
                          bank_name=user_account.bank_name, balance_amount=user_account.balance_amount, is_active=user_account.is_active)
    db.add(new_account)

    try:
        db.commit()
        db.refresh(new_account)
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something went wrong in creating account")
    
    return new_account

def get_account_service(user : dict = Depends(require_roles("user", "admin")), db : Session = Depends(get_db)):
    accounts = db.query(Account).filter(Account.user_id == user["id"]).all()
    return accounts

def update_account_service(account_id : int , user_account : accountRequest, user : dict = Depends(require_roles("user", "admin")), db : Session = Depends(get_db)):
    curr_account_query = db.query(Account).filter(Account.account_id == account_id)
    curr_account = curr_account_query.first()

    if not curr_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    
    curr_account_query.update({
        "account_name" : user_account.account_name,
        "account_type" : user_account.account_type,
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

def delete_account_service(account_id : int, user : dict = Depends(require_roles("user", "admin")), db : Session = Depends(get_db)):
    account = db.query(Account).filter(Account.account_id == account_id).first()

    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    if user["role"] != "admin" and account.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own account")

    db.delete(account)
    db.commit()
    return

def show_incomes(account_id : int, user : dict = Depends(require_roles("user", "admin")), db : Session = Depends(get_db), filter_query : AccountQueryParam = Depends()):
    income_query = db.query(Transaction).filter(Transaction.user_id == user["id"], Transaction.is_income == True, Transaction.account_linked == account_id)
    total_records = income_query.count()
    curr_query = income_query.offset(filter_query.get_offset).limit(filter_query.limit)
    incomes = curr_query.all()

    response = [
        IncomeResponse(
            income_id=i.transaction_id,
            income_name=i.transaction_name,
            amount=i.amount,
            recieved_date=i.transaction_date,
            account_id=i.account_linked,
            account_name=getattr(i.account, "account_name", None),
            additional_note=i.description,
            income_type_id=i.transaction_type_id,
            income_type_name=i.transaction_type.transaction_type,
            category_id=i.category_id,
            category_name=i.category.category_name,
            payment_mode_id=i.payment_mode_id,
            payment_mode_name=i.payment_mode.payment_mode
        )
        for i in incomes
    ]

    return {
        "total_pages": ceil(total_records / filter_query.limit) if filter_query.limit else 1,
        "current_page": filter_query.page,
        "total_incomes": total_records,
        "incomes": response
    }

def show_expenses(account_id : int, user : dict = Depends(require_roles("user", "admin")), db : Session = Depends(get_db), filter_query : AccountQueryParam = Depends()):
    expense_query = db.query(Transaction).filter(Transaction.user_id == user["id"], Transaction.is_expense == True, Transaction.account_linked == account_id)
    total_records = expense_query.count()

    curr_query = expense_query.offset(filter_query.get_offset).limit(filter_query.limit)
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


def overview_account_service(
    account_id: int,
    user: dict = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db)
):
    total_income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user["id"],
        Transaction.is_income == True,
        Transaction.account_linked == account_id
    ).scalar() or 0

    total_expense = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user["id"],
        Transaction.is_expense == True,
        Transaction.account_linked == account_id
    ).scalar() or 0

    curr_account = db.query(Account).filter(
        Account.account_id == account_id,
        Account.user_id == user["id"]
    ).first()

    if not curr_account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    curr_account.balance_amount = total_income - total_expense


    return accountResponse.model_validate(curr_account)