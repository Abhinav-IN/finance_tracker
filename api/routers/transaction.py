from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.schemas.transaction import getTransactionParam, TransactionResponse, TransactionRequest
from api.services.transaction_service import create_transaction_service, delete_transaction_service, get_transaction_service, update_transaction_service
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(tags=['Transaction'], prefix='/api/v1/transaction')

@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=TransactionResponse)
def create_transaction(user_transaction : TransactionRequest, 
    user: dict = Depends(require_roles("user", "admin")), 
    db : Session = Depends(get_db)):
    return create_transaction_service(user_transaction, user, db)
    

@router.get('/', status_code=status.HTTP_200_OK, response_model=List[TransactionResponse])
def get_transaction(user: dict = Depends(require_roles("user", "admin")), 
                        db : Session = Depends(get_db),
                        filter_query : getTransactionParam = Depends()):
    return get_transaction_service(user, db, filter_query)
   

@router.put('/update/{transaction_id}', status_code=status.HTTP_200_OK, response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_update: TransactionRequest,
    user: dict = Depends(require_roles("user", "admin")), 
    db: Session = Depends(get_db)
):
    return update_transaction_service(transaction_id, transaction_update, user, db)


@router.delete('/delete/{transaction_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id : int,
                    user: dict = Depends(require_roles("user", "admin")), 
                    db: Session = Depends(get_db)):
    return delete_transaction_service(transaction_id, user, db)