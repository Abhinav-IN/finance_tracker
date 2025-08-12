from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.schemas.transaction import TransactionQueryParam, ExpenseResponse, ExpenseRequest, ExpenseOverview, PaginatedExpenseResponse
from api.services.expense_service import create_expense_service, delete_expense_service, get_expense_service, update_expense_service, overview_services
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(tags=['Expense'], prefix='/api/v1/transaction/expense')

@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=ExpenseResponse)
def create_expense(user_expense : ExpenseRequest, 
    user: dict = Depends(require_roles("user", "admin")), 
    db : Session = Depends(get_db)):
    return create_expense_service(user_expense, user, db)
    

@router.get('/', status_code=status.HTTP_200_OK, response_model=PaginatedExpenseResponse)
def get_expense(user: dict = Depends(require_roles("user", "admin")), 
                        db : Session = Depends(get_db),
                        filter_query : TransactionQueryParam = Depends()):
    return get_expense_service(user, db, filter_query)
   

@router.put('/update/{expense_id}', status_code=status.HTTP_200_OK, response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    expense_update: ExpenseRequest,
    user: dict = Depends(require_roles("user", "admin")), 
    db: Session = Depends(get_db)
):
    return update_expense_service(expense_id, expense_update, user, db)


@router.delete('/delete/{expense_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id : int,
                    user: dict = Depends(require_roles("user", "admin")), 
                    db: Session = Depends(get_db)):
    return delete_expense_service(expense_id, user, db)

@router.get('/overview', status_code=status.HTTP_200_OK, response_model=ExpenseOverview)
def overview_income(user: dict = Depends(require_roles("user", "admin")),  db: Session = Depends(get_db)):
    return overview_services(user, db)