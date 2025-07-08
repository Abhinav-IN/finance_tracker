from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.models.category import Category
from api.models.payment_mode import PaymentMode
from api.services.lookup_create_service import get_or_create_category, get_or_create_transactionType, get_or_create_paymentMode
from api.models.transaction import Transaction
from api.models.transaction_type import TransactionType
from api.schemas.transaction import getTransactionParam, TransactionRequest, TransactionResponse
from api.utils.validator import user_active
from fastapi import Depends, HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def create_transaction_service(user_transaction : TransactionRequest, 
    user: dict = Depends(require_roles("user", "admin")), 
    db : Session = Depends(get_db)):
    user_active(user, db)

    curr_category_id = get_or_create_category(user_transaction.category_name, user["id"], db)
    curr_transaction_type_id = get_or_create_transactionType(user_transaction.transaction_type_name, user["id"], db)
    curr_payment_mode_id = get_or_create_paymentMode(user_transaction.payment_mode_name, user["id"], db)
    
    new_transaction = Transaction(amount = user_transaction.amount, description = user_transaction.description, user_id = user['id'], 
    category_id = curr_category_id, transaction_type_id = curr_transaction_type_id, payment_mode_id = curr_payment_mode_id)
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return TransactionResponse(
        transaction_id=new_transaction.transaction_id,
        amount=new_transaction.amount,
        description=new_transaction.description,
        timestamp=new_transaction.timestamp,
        transaction_type_id=new_transaction.transaction_type_id,
        transaction_type_name=new_transaction.transaction_type.transaction_type,
        category_id=new_transaction.category_id,
        category_name=new_transaction.category.category_name,
        payment_mode_id=new_transaction.payment_mode_id,
        payment_mode_name=new_transaction.payment_mode.payment_mode
)

def get_transaction_service(user: dict = Depends(require_roles("user", "admin")), 
                        db : Session = Depends(get_db),
                        filter_query : getTransactionParam = Depends()):
    user_active(user, db)
    curr_query = db.query(Transaction).filter(Transaction.user_id == user["id"])
    if filter_query.transaction_id :
        curr_query = curr_query.filter(Transaction.transaction_id == filter_query.transaction_id)
    if filter_query.exact_amount:
        curr_query = curr_query.filter(Transaction.amount == filter_query.exact_amount)
    if filter_query.greater_amount:
        curr_query = curr_query.filter(Transaction.amount > filter_query.greater_amount)
    if filter_query.lower_amount:
        curr_query = curr_query.filter(Transaction.amount < filter_query.lower_amount)
    if filter_query.date:
       curr_query = curr_query.filter(func.date(Transaction.timestamp) == filter_query.date)
    if filter_query.search:
        curr_query = curr_query\
        .join(Category)\
        .join(TransactionType)\
        .join(PaymentMode)\
        .filter(
            or_(
                Transaction.description.ilike(f"%{filter_query.search.strip()}%"),
                Category.category_name.ilike(f"%{filter_query.search.strip()}%"),
                TransactionType.transaction_type.ilike(f"%{filter_query.search.strip()}%"),
                PaymentMode.payment_mode.ilike(f"%{filter_query.search.strip()}%"),
            )
        )

    curr_query = curr_query.offset(filter_query.get_offset).limit(filter_query.limit)
    transaction = curr_query.all()
    
    response = []
    for t in transaction:
        response.append(TransactionResponse(
            transaction_id=t.transaction_id,
            amount=t.amount,
            description=t.description,
            timestamp=t.timestamp,
            transaction_type_id=t.transaction_type_id,
            transaction_type_name=t.transaction_type.transaction_type, 
            category_id=t.category_id,
            category_name=t.category.category_name,
            payment_mode_id = t.payment_mode_id,
            payment_mode_name = t.payment_mode.payment_mode
        ))
    
    return response

def update_transaction_service(
    transaction_id: int,
    transaction_update: TransactionRequest,
    user: dict = Depends(require_roles("user", "admin")), 
    db: Session = Depends(get_db)
):
    user_active(user, db)
    transaction_query = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id,
        Transaction.user_id == user['id']  
    )

    existing_transaction = transaction_query.first()
    if not existing_transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    curr_category_id = get_or_create_category(transaction_update.category_name, user["id"], db)
    curr_transaction_type_id = get_or_create_transactionType(transaction_update.transaction_type_name, user["id"], db)
    curr_payment_mode_id = get_or_create_paymentMode(transaction_update.payment_mode_name, user["id"], db)

    transaction_query.update({
        "amount": transaction_update.amount,
        "description": transaction_update.description,
        "category_id": curr_category_id,
        "transaction_type_id": curr_transaction_type_id,
        "payment_mode_id" : curr_payment_mode_id
    }, synchronize_session=False)

    db.commit()
    db.refresh(existing_transaction)

    return TransactionResponse(
        transaction_id=existing_transaction.transaction_id,
        amount=existing_transaction.amount,
        description=existing_transaction.description,
        timestamp=existing_transaction.timestamp,
        transaction_type_id=existing_transaction.transaction_type_id,
        transaction_type_name=existing_transaction.transaction_type.transaction_type,
        category_id=existing_transaction.category_id,
        category_name=existing_transaction.category.category_name,
        payment_mode_id=existing_transaction.payment_mode_id,
        payment_mode_name=existing_transaction.payment_mode.payment_mode
    )


def delete_transaction_service(transaction_id : int,
                    user: dict = Depends(require_roles("user", "admin")), 
                    db: Session = Depends(get_db)):
    user_active(user, db)
    transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    if user["role"] != "admin" and transaction.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own transaction")

    db.delete(transaction)
    db.commit()
    return