from fastapi import APIRouter, status, Depends, HTTPException
from .. import schemas, oauth2, database, models
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List

router = APIRouter(tags=['Transaction'], prefix='/api/v1/transaction')

@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=schemas.TransactionResponse)
def create_transaction(user_transaction : schemas.TransactionRequest, 
    user: dict = Depends(oauth2.require_roles("user", "admin")), 
    db : Session = Depends(database.get_db)):
    if user["is_active"] == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is not verified")
    curr_category_id = db.query(models.Category.category_id).filter(models.Category.user_id == user['id'],
                        models.Category.category_name.ilike(user_transaction.category_name.strip().lower())).scalar()
    if not curr_category_id:
        new_category = models.Category(category_name = user_transaction.category_name, user_id = user['id'])
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        curr_category_id = new_category.category_id
    
    curr_transaction_type_id = db.query(models.TransactionType.transaction_type_id).filter(models.TransactionType.transaction_type.ilike(user_transaction.transaction_type_name.strip().lower())).scalar()
    if not curr_transaction_type_id:
        new_transaction_type = models.TransactionType(transaction_type = user_transaction.transaction_type_name)
        db.add(new_transaction_type)
        db.commit()
        db.refresh(new_transaction_type)
        curr_transaction_type_id = new_transaction_type.transaction_type_id
    
    new_transaction = models.Transaction(amount = user_transaction.amount, description = user_transaction.description, user_id = user['id'], 
    category_id = curr_category_id, transaction_type_id = curr_transaction_type_id)
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return {
        "amount" : new_transaction.amount,
        "description" : new_transaction.description,
        "timestamp" : new_transaction.timestamp,
        "transaction_type_id" : new_transaction.transaction_type_id,
        "transaction_type_name" : new_transaction.transaction_type.transaction_type,
        "category_id" : new_transaction.category_id,
        "category_name" : new_transaction.category.category_name
        }

@router.get('/', status_code=status.HTTP_200_OK, response_model=List[schemas.TransactionResponse])
def get_all_transaction(user: dict = Depends(oauth2.require_roles("user", "admin")), 
                        db : Session = Depends(database.get_db),
                        filter_query : schemas.getTransactionParam = Depends()):
    if user["is_active"] == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is not verified")
    
    curr_query = db.query(models.Transaction).filter(models.Transaction.user_id == user["id"])
    if filter_query.transaction_id :
        curr_query = curr_query.filter(models.Transaction.transaction_id == filter_query.transaction_id)
    if filter_query.exact_amount:
        curr_query = curr_query.filter(models.Transaction.amount == filter_query.exact_amount)
    if filter_query.greater_amount:
        curr_query = curr_query.filter(models.Transaction.amount > filter_query.greater_amount)
    if filter_query.lower_amount:
        curr_query = curr_query.filter(models.Transaction.amount < filter_query.lower_amount)
    if filter_query.date:
       curr_query = curr_query.filter(func.date(models.Transaction.timestamp) == filter_query.date)
    if filter_query.category_id:
        curr_query = curr_query.filter(models.Transaction.category_id == filter_query.category_id)
    if filter_query.transaction_type_id:
        curr_query = curr_query.filter(models.Transaction.transaction_type_id == filter_query.transaction_type_id)
    if filter_query.search:
        curr_query = curr_query.join(models.Category).filter(
        or_(
            models.Transaction.description.ilike(f"%{filter_query.search}%"),
            models.Category.category_name.ilike(f"%{filter_query.search}%")
        )
    )
    
    curr_query = curr_query.offset(filter_query.get_offset).limit(filter_query.limit)
    transaction = curr_query.all()
    
    response = []
    for t in transaction:
        response.append(schemas.TransactionResponse(
            amount=t.amount,
            description=t.description,
            timestamp=t.timestamp,
            transaction_type_id=t.transaction_type_id,
            transaction_type_name=t.transaction_type.transaction_type, 
            category_id=t.category_id,
            category_name=t.category.category_name  
        ))
    
    return response

@router.put('/{transaction_id}', status_code=status.HTTP_200_OK, response_model=schemas.TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_update: schemas.TransactionRequest,
    user: dict = Depends(oauth2.require_roles("user", "admin")), 
    db: Session = Depends(database.get_db)
):
    if not user['is_active']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account must be verified")

    transaction_query = db.query(models.Transaction).filter(
        models.Transaction.transaction_id == transaction_id,
        models.Transaction.user_id == user['id']  
    )

    existing_transaction = transaction_query.first()
    if not existing_transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    category_name = transaction_update.category_name.strip().lower()
    curr_category_id = db.query(models.Category.category_id).filter(
        models.Category.user_id == user['id'],
        models.Category.category_name.ilike(category_name)
    ).scalar()
    if not curr_category_id:
        new_category = models.Category(category_name=category_name, user_id=user['id'])
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        curr_category_id = new_category.category_id

    transaction_type_name = transaction_update.transaction_type_name.strip().lower()
    curr_transaction_type_id = db.query(models.TransactionType.transaction_type_id).filter(
        models.TransactionType.transaction_type.ilike(transaction_type_name)
    ).scalar()
    if not curr_transaction_type_id:
        new_type = models.TransactionType(transaction_type=transaction_type_name)
        db.add(new_type)
        db.commit()
        db.refresh(new_type)
        curr_transaction_type_id = new_type.transaction_type_id

    transaction_query.update({
        "amount": transaction_update.amount,
        "description": transaction_update.description,
        "category_id": curr_category_id,
        "transaction_type_id": curr_transaction_type_id
    }, synchronize_session=False)

    db.commit()
    db.refresh(existing_transaction)

    return {
        "amount": existing_transaction.amount,
        "description": existing_transaction.description,
        "timestamp": existing_transaction.timestamp,
        "transaction_type_id": existing_transaction.transaction_type_id,
        "transaction_type_name": existing_transaction.transaction_type.transaction_type,
        "category_id": existing_transaction.category_id,
        "category_name": existing_transaction.category.category_name
    }


@router.delete('/delete/{transaction_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id : int,
                    user: dict = Depends(oauth2.require_roles("user", "admin")), 
                    db: Session = Depends(database.get_db)):
    if user["is_active"] == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is not verified")
    transaction = db.query(models.Transaction).filter(models.Transaction.transaction_id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if user["role"] != "admin" and transaction.user_id != user["id"]:
        raise HTTPException(status_code=403, detail="You can only delete your own category")

    db.delete(transaction)
    db.commit()
    return