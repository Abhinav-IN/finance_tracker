from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.schemas.transaction import TransactionQueryParam, IncomeResponse, IncomeRequest, IncomeOverview, PaginatedIncomeResponse
from api.services.income_service import create_income_service, delete_income_service, get_income_service, update_income_service, overview_services
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(tags=['Income'], prefix='/api/v1/transaction/income')

@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=IncomeResponse)
def create_income(user_income : IncomeRequest, 
    user: dict = Depends(require_roles("user", "admin")), 
    db : Session = Depends(get_db)):
    return create_income_service(user_income, user, db)
    

@router.get('/', status_code=status.HTTP_200_OK, response_model=PaginatedIncomeResponse)
def get_income(user: dict = Depends(require_roles("user", "admin")), 
                        db : Session = Depends(get_db),
                        filter_query : TransactionQueryParam = Depends()):
    return get_income_service(user, db, filter_query)
   

@router.put('/update/{income_id}', status_code=status.HTTP_200_OK, response_model=IncomeResponse)
def update_income(
    income_id: int,
    income_update: IncomeRequest,
    user: dict = Depends(require_roles("user", "admin")), 
    db: Session = Depends(get_db)
):
    return update_income_service(income_id, income_update, user, db)


@router.delete('/delete/{income_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_income(income_id : int,
                    user: dict = Depends(require_roles("user", "admin")), 
                    db: Session = Depends(get_db)):
    return delete_income_service(income_id, user, db)

@router.get('/overview', status_code=status.HTTP_200_OK, response_model=IncomeOverview)
def overview_income(user: dict = Depends(require_roles("user", "admin")),  db: Session = Depends(get_db)):
    return overview_services(user, db)