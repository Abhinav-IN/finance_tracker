from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.schemas.transaction import TransactionQueryParam, TransactionResponse, TransactionCreate, ExpenseOverview, PaginatedTransactionResponse, IncomeOverview
from api.services.transaction_service import create_transaction_service, delete_transaction_service, get_transaction_service, update_transaction_service, income_overview_services, expense_overview_services
from api.utils.enums import UserRole
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(tags=['Transaction'], prefix='/api/v1/transaction')

@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=TransactionResponse)
def create_transaction(user_transaction : TransactionCreate, 
    user: dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)), 
    db : Session = Depends(get_db)):
    return create_transaction_service(user_transaction, user, db)
    

@router.get('/', status_code=status.HTTP_200_OK, response_model=PaginatedTransactionResponse)
def get_transaction(user: dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)), 
                        db : Session = Depends(get_db),
                        filter_query : TransactionQueryParam = Depends()):
    return get_transaction_service(user, db, filter_query)
   
@router.put('/update/{transaction_id}', status_code=status.HTTP_200_OK, response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_update: TransactionCreate,
    user: dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)), 
    db: Session = Depends(get_db)
):
    return update_transaction_service(transaction_id, transaction_update, user, db)


@router.delete('/delete/{transaction_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id : int,
                    user: dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)), 
                    db: Session = Depends(get_db)):
    return delete_transaction_service(transaction_id, user, db)

@router.get('/expense_overview', status_code=status.HTTP_200_OK, response_model=ExpenseOverview)
def overview_expense(user: dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)),  db: Session = Depends(get_db)):
    return expense_overview_services(user, db)

@router.get('/income_overview', status_code=status.HTTP_200_OK, response_model=IncomeOverview)
def overview_income(user: dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)),  db: Session = Depends(get_db)):
    return income_overview_services(user, db)