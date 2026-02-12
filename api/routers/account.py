from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.schemas.account import accountResponse, accountRequest, AccountQueryParam, PaginatedTransactionResponse
from api.services.account_service import create_account_service, get_account_service, update_account_service, delete_account_service, show_transactions, overview_account_service
from api.utils.enums import UserRole
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(tags=['Account'], prefix='/api/v1/account')

@router.post('/create', status_code=status.HTTP_200_OK, response_model=accountResponse)
def create_account(user_account : accountRequest, user : dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)), db : Session = Depends(get_db)):
    return create_account_service(user_account, user["id"], db)

@router.get('/', status_code=status.HTTP_200_OK, response_model=List[accountResponse])
def get_account(user : dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)), db : Session = Depends(get_db)):
    return get_account_service(user["id"], db)

@router.put('/update/{account_id}', status_code=status.HTTP_200_OK, response_model=accountResponse)
def update_account(account_id : int, user_account : accountRequest, user : dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)), db : Session = Depends(get_db)):
    return update_account_service(account_id, user_account, db)

@router.delete('/delete/{account_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id : int, user : dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)), db : Session = Depends(get_db)):
    return delete_account_service(account_id, user, db)

@router.get('/transactions/{account_id}', status_code=status.HTTP_200_OK, response_model=PaginatedTransactionResponse)
def get_transaction(account_id : int, user : dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)), db : Session = Depends(get_db), filter_query : AccountQueryParam = Depends() ):
    return show_transactions(account_id, user["id"], db, filter_query)

@router.get('/overview_account/{account_id}', status_code=status.HTTP_200_OK, response_model=accountResponse)
def overview_account(account_id : int, user : dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)), db : Session = Depends(get_db)):
    return overview_account_service(account_id, user["id"], db)